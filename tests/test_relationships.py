"""Relationship axes: clamping, direction, and the derived readings."""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from s32_engine import relationships
from s32_engine.state import new_state
from s32_engine.types import AXIS_MAX, AXIS_MIN, RELATIONSHIP_AXES

#: The `library` fixture is immutable content, and each example builds its own
#: fresh state from it, so Hypothesis not re-running the fixture is harmless.
_IMMUTABLE_FIXTURE = settings(suppress_health_check=[HealthCheck.function_scoped_fixture])


def test_change_returns_clamped_value(state):
    assert relationships.change(state, "iris", "player", "trust", 30) == 30
    assert relationships.change(state, "iris", "player", "trust", 1000) == AXIS_MAX
    assert relationships.change(state, "iris", "player", "trust", -1000) == AXIS_MIN


def test_relationships_are_directed(state):
    relationships.change(state, "iris", "theo", "trust", 40)

    assert relationships.get(state, "iris", "theo", "trust") == 40
    # Iris trusting Theo says nothing about Theo trusting Iris. The story
    # depends on that asymmetry, so it is asserted rather than assumed.
    assert relationships.get(state, "theo", "iris", "trust") == 0
    assert relationships.get(state, "player", "theo", "trust") == 0


def test_npc_to_npc_edges_need_no_special_case(state):
    relationships.change(state, "theo", "mara", "resentment", 25)
    assert ("theo", "mara") in relationships.edges(state)
    assert relationships.get(state, "theo", "mara", "resentment") == 25


def test_apply_moves_several_axes_at_once(state):
    result = relationships.apply(state, "iris", "player", {"attraction": 20, "fear": 10})
    assert result["attraction"] == 20
    assert result["fear"] == 10


def test_apply_rejects_an_unknown_axis(state):
    with pytest.raises(KeyError, match="unknown relationship axis"):
        relationships.apply(state, "iris", "player", {"vibes": 5})


def test_love_without_trust_is_representable(state):
    """The premise the multi-axis model exists for."""
    relationships.apply(state, "iris", "player", {"attraction": 80, "trust": 5, "suspicion": 60})

    assert relationships.is_strained(state, "iris", "player")
    assert not relationships.is_close(state, "iris", "player")
    assert relationships.romantic_potential(state, "iris", "player") > 0


def test_respect_and_resentment_coexist(state):
    relationships.apply(state, "theo", "player", {"respect": 70, "resentment": 65})
    assert relationships.is_strained(state, "theo", "player")
    assert relationships.get(state, "theo", "player", "respect") == 70


def test_fear_suppresses_romantic_potential(state):
    relationships.apply(state, "iris", "player", {"attraction": 70, "trust": 60, "familiarity": 60})
    without_fear = relationships.romantic_potential(state, "iris", "player")

    relationships.change(state, "iris", "player", "fear", 60)
    with_fear = relationships.romantic_potential(state, "iris", "player")

    assert with_fear < without_fear


def test_summary_is_readable_and_empty_when_untouched(state):
    assert "no history" in relationships.summary(state, "iris", "player")
    relationships.change(state, "iris", "player", "trust", 12)
    assert "trust=12" in relationships.summary(state, "iris", "player")


@_IMMUTABLE_FIXTURE
@given(
    axis=st.sampled_from(RELATIONSHIP_AXES),
    deltas=st.lists(st.integers(min_value=-500, max_value=500), max_size=40),
)
def test_axis_never_leaves_its_range(library, axis, deltas):
    """No sequence of changes can produce an out-of-range value.

    A property test rather than examples: the clamp is the one invariant every
    scene relies on, and it is applied in several places.
    """
    game_state = new_state(library, seed=0)
    for delta in deltas:
        value = relationships.change(game_state, "iris", "player", axis, delta)
        assert AXIS_MIN <= value <= AXIS_MAX

    vector = relationships.vector(game_state, "iris", "player")
    assert all(AXIS_MIN <= v <= AXIS_MAX for v in vector.values())


@_IMMUTABLE_FIXTURE
@given(value=st.integers(min_value=-1000, max_value=1000))
def test_set_axis_clamps_too(library, value):
    game_state = new_state(library, seed=0)
    result = relationships.set_axis(game_state, "iris", "player", "trust", value)
    assert AXIS_MIN <= result <= AXIS_MAX
