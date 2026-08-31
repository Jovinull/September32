"""The container seam that makes Ren'Py rollback work.

This is the highest-value test file in the project. The bug it guards against
cost real debugging time during the bootstrap: the run state was built from plain
dicts, Ren'Py saved and loaded it perfectly, and rollback silently did nothing —
the text rewound and the world did not. Nothing raised, nothing logged.

The rule is that **every container reachable from GameState must come from
``s32_engine.containers``**. A single literal ``{}`` three levels down is enough
to bring the bug back, so the tests below walk the whole tree rather than
checking the places we happen to remember.
"""

from __future__ import annotations

from typing import Any

import pytest

from s32_engine import commitments, containers, knowledge, relationships
from s32_engine.director import NarrativeDirector
from s32_engine.rng import Rng
from s32_engine.state import migrate_state, new_state, note_event, set_flag


class TrackedDict(dict[Any, Any]):
    """Stands in for Ren'Py's RevertableDict."""


class TrackedList(list[Any]):
    """Stands in for Ren'Py's RevertableList."""


@pytest.fixture
def tracked():
    """Install the tracking factories for one test."""
    containers.configure(TrackedDict, TrackedList)
    yield
    containers.reset()


def walk(value: Any, path: str = "state") -> list[tuple[str, Any]]:
    """Yield every container in a state tree with the path that reaches it."""
    found: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        found.append((path, value))
        for key, item in value.items():
            found.extend(walk(item, f"{path}[{key!r}]"))
    elif isinstance(value, list):
        found.append((path, value))
        for index, item in enumerate(value):
            found.extend(walk(item, f"{path}[{index}]"))
    return found


def assert_all_tracked(state: Any) -> None:
    """Fail with the exact path of any container that bypassed the seam."""
    for path, container in walk(state):
        expected = TrackedDict if isinstance(container, dict) else TrackedList
        assert isinstance(container, expected), (
            f"{path} is a plain {type(container).__name__}; it will not roll back. "
            "Build it through s32_engine.containers."
        )


def test_a_fresh_state_is_entirely_tracked(tracked, library):
    assert_all_tracked(new_state(library, seed=1))


def test_relationship_vectors_created_on_demand_are_tracked(tracked, library):
    state = new_state(library, seed=1)
    relationships.change(state, "iris", "theo", "trust", 5)
    assert_all_tracked(state)


def test_belief_maps_created_on_demand_are_tracked(tracked, library):
    state = new_state(library, seed=1)
    knowledge.grant(state, "photo", agent="mara")
    assert_all_tracked(state)


def test_commitments_are_tracked(tracked, library):
    state = new_state(library, seed=1)
    commitments.make(state, "meet", kind="meeting", participants=["theo"], due_day=3)
    assert_all_tracked(state)


def test_history_entries_are_tracked(tracked, library):
    state = new_state(library, seed=1)
    NarrativeDirector(library).play(library.storylets["intro"], state)
    assert_all_tracked(state)


def test_a_full_play_session_stays_tracked(tracked, library):
    """The integration case: exercise everything, then check the whole tree."""
    state = new_state(library, seed=99)
    for character in state["characters"].values():
        character["present"] = True
    state["world"]["location"] = "archive"

    director = NarrativeDirector(library)
    rng = Rng(state)
    for _ in range(12):
        selection = director.select(state, rng)
        if selection.storylet is not None:
            director.play(selection.storylet, state)
        set_flag(state, "steps", state["world"]["flags"].get("steps", 0) + 1)
        note_event(state, "tick")
        from s32_engine.state import advance_time

        advance_time(state, 1)

    assert_all_tracked(state)


def test_migrating_a_plain_save_rebuilds_it_through_the_seam(tracked, library):
    """A save loaded as plain dicts must be adopted, not used as-is.

    Without this, loading an old save would produce a session where rollback
    quietly stops working — the same invisible bug, arriving by a different
    route.
    """
    containers.reset()
    plain = new_state(library, seed=1)
    assert isinstance(plain, dict) and not isinstance(plain, TrackedDict)

    containers.configure(TrackedDict, TrackedList)
    assert_all_tracked(migrate_state(dict(plain)))


def test_adopt_converts_tuples_to_lists(tracked):
    """A tuple in game state is a trap: a scene that mutates it fails."""
    adopted = containers.adopt({"a": (1, 2, {"b": (3,)})})
    assert isinstance(adopted["a"], TrackedList)
    assert isinstance(adopted["a"][2]["b"], TrackedList)


def test_adopt_leaves_scalars_alone(tracked):
    assert containers.adopt("text") == "text"
    assert containers.adopt(7) == 7
    assert containers.adopt(None) is None


def test_the_default_factories_are_the_builtins(library):
    """Headless tooling and tests must see ordinary dicts and lists."""
    dict_factory, list_factory = containers.factories()
    assert dict_factory is dict
    assert list_factory is list
    assert type(new_state(library, seed=1)) is dict
