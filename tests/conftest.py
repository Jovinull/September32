"""Shared fixtures.

Two kinds of test live here, and keeping them apart matters:

* Tests over a **synthetic library** (``library`` fixture) check engine
  behaviour. They must not change when a writer edits a scene.
* Tests over the **real content** (``real_library`` fixture) check that the
  project's actual data is sound. They are expected to change with the content,
  and they are what stops a broken storylet reaching a build.
"""

from __future__ import annotations

import pytest

from s32_engine import containers
from s32_engine.definitions import load_library
from s32_engine.rng import Rng
from s32_engine.state import new_state
from s32_engine.types import (
    AnchorDef,
    CharacterDef,
    ContentLibrary,
    GameState,
    ItemDef,
    KnowledgeDef,
    LocationDef,
    StoryletDef,
)
from s32tools import paths


@pytest.fixture(autouse=True)
def _builtin_containers():
    """Guarantee every test starts with the builtin container factories.

    A test that installs Ren'Py-style factories must not leak them into the
    next test, and a test that forgets to reset would otherwise fail somewhere
    unrelated.
    """
    containers.reset()
    yield
    containers.reset()


@pytest.fixture
def library() -> ContentLibrary:
    """A small synthetic library covering every feature the engine has."""
    return ContentLibrary(
        characters={
            "iris": CharacterDef("iris", "Iris", "archivist", asset_id="pm_a01_kohaku"),
            "theo": CharacterDef("theo", "Theo", "records"),
            "mara": CharacterDef("mara", "Mara", "local"),
        },
        locations={
            "archive": LocationDef("archive", "Archive", "school"),
            "rooftop": LocationDef("rooftop", "Rooftop", "school", indoor=False),
            "hall": LocationDef("hall", "Hall", "school"),
        },
        knowledge={
            "photo": KnowledgeDef("photo", "A photograph exists.", "archive"),
            "date": KnowledgeDef(
                "date", "The date is impossible.", "phenomenon", contradicts=("forgery",)
            ),
            "forgery": KnowledgeDef(
                "forgery", "The date was faked.", "phenomenon", contradicts=("date",)
            ),
        },
        items={"camera": ItemDef("camera", "Old camera", "object", grants=("photo",))},
        storylets={
            "intro": StoryletDef(
                id="intro",
                label="s32_st_intro",
                title="Intro",
                category="conversation",
                location="archive",
                characters=("iris",),
                priority=70,
                effects=("rel iris.trust += 5", "know(photo, box)"),
                tags=("archive",),
            ),
            "followup": StoryletDef(
                id="followup",
                label="s32_st_followup",
                title="Follow-up",
                category="investigation",
                location="archive",
                priority=60,
                requirements=("knows(photo)", "rel iris.trust >= 5"),
                effects=("know(date, stamp)",),
                tags=("mystery",),
            ),
            "ambient": StoryletDef(
                id="ambient",
                label="s32_st_ambient",
                title="Ambient",
                category="ambient",
                location="hall",
                priority=10,
                weight=3.0,
                repeat_policy="cooldown",
                cooldown=2,
                tags=("slice_of_life",),
            ),
            "blocked": StoryletDef(
                id="blocked",
                label="s32_st_blocked",
                title="Blocked",
                category="conversation",
                location="rooftop",
                priority=50,
                blockers=("rel iris.trust >= 5",),
            ),
        },
        anchors={
            "start": AnchorDef(
                id="start",
                label="s32_anchor_start",
                title="Start",
                order=1,
                phase="normal",
                effects=("anchor_done(start)",),
            ),
            "second": AnchorDef(
                id="second",
                label="s32_anchor_second",
                title="Second",
                order=2,
                phase="odd",
                requirements=("anchor_done(start)", "knows(photo)"),
                effects=("anchor_done(second)", "phase = odd"),
            ),
        },
    )


@pytest.fixture
def state(library: ContentLibrary) -> GameState:
    """A fresh run state with everyone present, at the archive."""
    game_state = new_state(library, seed=1234)
    for character in game_state["characters"].values():
        character["present"] = True
    game_state["world"]["location"] = "archive"
    return game_state


@pytest.fixture
def rng(state: GameState) -> Rng:
    """A deterministic RNG bound to the test state."""
    return Rng(state)


@pytest.fixture(scope="session")
def real_library() -> ContentLibrary:
    """The project's actual authored content."""
    return load_library(paths.data_dir())
