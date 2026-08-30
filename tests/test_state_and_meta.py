"""World state, save migration, commitments, traits and cross-run meta."""

from __future__ import annotations

import pytest

from s32_engine import commitments, meta, traits
from s32_engine.errors import StateError
from s32_engine.state import (
    advance_time,
    bump_flag,
    days_since_seen,
    has_seen,
    migrate_state,
    new_state,
    note_event,
    record_storylet,
    sync_with_library,
    times_seen,
)
from s32_engine.types import CharacterDef, ContentLibrary
from s32_engine.version import META_SCHEMA_VERSION, SAVE_SCHEMA_VERSION

# ---------------------------------------------------------------------------
# Time
# ---------------------------------------------------------------------------


def test_time_advances_through_slots_and_rolls_the_day(state):
    assert state["world"]["time_slot"] == "morning"
    advance_time(state, 1)
    assert state["world"]["time_slot"] == "midday"

    advance_time(state, 7)
    assert state["world"]["day"] == 2
    assert state["world"]["time_slot"] == "midday"


def test_the_in_fiction_calendar_advances_with_the_day(state):
    advance_time(state, 7 * 3)
    assert state["world"]["day"] == 4
    assert state["world"]["calendar_day"] == 4


def test_time_cannot_run_backwards(state):
    with pytest.raises(StateError, match="negative"):
        advance_time(state, -1)


def test_the_recent_event_window_is_capped(state):
    for index in range(30):
        note_event(state, f"event_{index}", keep=5)
    events = state["world"]["recent_events"]
    assert len(events) == 5
    assert events[-1] == "event_29"


def test_flags_are_counters(state):
    assert bump_flag(state, "visits") == 1
    assert bump_flag(state, "visits", 4) == 5


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


def test_history_tracks_counts_and_recency(state):
    assert not has_seen(state, "intro")
    assert days_since_seen(state, "intro") is None

    record_storylet(state, "intro")
    advance_time(state, 7 * 2)
    record_storylet(state, "intro")

    assert times_seen(state, "intro") == 2
    assert days_since_seen(state, "intro") == 0
    assert [entry["id"] for entry in state["history"]] == ["intro", "intro"]


# ---------------------------------------------------------------------------
# Commitments
# ---------------------------------------------------------------------------


def test_a_promise_can_be_kept_broken_or_excused(state):
    commitments.make(state, "meet", kind="meeting", participants=["theo"], due_day=3)
    assert commitments.status(state, "meet") == "active"

    commitments.fulfil(state, "meet")
    assert commitments.status(state, "meet") == "fulfilled"

    # Resolving an already-resolved promise is a no-op, so a scene reachable by
    # two routes does not have to guard the call.
    commitments.break_(state, "meet")
    assert commitments.status(state, "meet") == "fulfilled"


def test_broken_and_excused_are_different(state):
    """Letting someone down and being prevented are not the same story."""
    commitments.make(state, "a", kind="meeting", participants=["theo"], due_day=1, importance=60)
    commitments.make(state, "b", kind="meeting", participants=["theo"], due_day=1, importance=60)
    commitments.break_(state, "a")
    commitments.excuse(state, "b")

    assert commitments.broken_weight(state, "theo") == 60


def test_overdue_promises_expire_on_a_day_rollover(state):
    commitments.make(state, "meet", kind="meeting", participants=["theo"], due_day=1)
    advance_time(state, 7 * 2)
    assert commitments.status(state, "meet") == "expired"


def test_remaking_a_promise_replaces_it(state):
    commitments.make(state, "meet", kind="meeting", participants=["theo"], due_day=1)
    commitments.break_(state, "meet")
    commitments.make(state, "meet", kind="meeting", participants=["theo"], due_day=5)

    assert commitments.status(state, "meet") == "active"
    assert len([c for c in state["commitments"] if c["id"] == "meet"]) == 1


def test_open_commitments_are_ordered_by_urgency(state):
    commitments.make(state, "later", kind="meeting", participants=["theo"], due_day=9)
    commitments.make(state, "sooner", kind="meeting", participants=["iris"], due_day=2)
    assert [c["id"] for c in commitments.open_commitments(state)] == ["sooner", "later"]


# ---------------------------------------------------------------------------
# Traits
# ---------------------------------------------------------------------------


def test_traits_start_empty_and_accumulate(state):
    assert traits.profile(state) == "no established tendencies yet"
    assert not traits.has(state, "curious")

    for _ in range(3):
        traits.change(state, "curious")

    assert traits.has(state, "curious")
    assert traits.dominant(state)[0] == ("curious", 3)
    assert traits.label("curious") == "Observant"


def test_dominant_traits_break_ties_stably(state):
    traits.change(state, "curious", 5)
    traits.change(state, "direct", 5)
    assert traits.dominant(state) == traits.dominant(state)
    assert traits.dominant(state)[0][0] == "curious"


def test_an_unknown_trait_axis_is_an_error(state):
    with pytest.raises(KeyError, match="unknown trait axis"):
        traits.change(state, "brooding")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Save migration
# ---------------------------------------------------------------------------


def test_migration_stamps_the_current_schema(library):
    old = new_state(library, seed=1)
    old["save_schema_version"] = 0
    assert migrate_state(dict(old))["save_schema_version"] == SAVE_SCHEMA_VERSION


def test_a_save_from_a_newer_build_is_refused(library):
    """Guessing at a future schema is worse than saying so."""
    future = new_state(library, seed=1)
    future["save_schema_version"] = SAVE_SCHEMA_VERSION + 5

    with pytest.raises(StateError, match="newer than this build"):
        migrate_state(dict(future))


def test_characters_added_after_a_save_get_state(library):
    """Adding a character mid-development must not invalidate saves."""
    old = new_state(library, seed=1)

    extended = ContentLibrary(
        characters={**library.characters, "june": CharacterDef("june", "June", "sceptic")},
        locations=library.locations,
        knowledge=library.knowledge,
        items=library.items,
        storylets=library.storylets,
        anchors=library.anchors,
    )
    added = sync_with_library(old, extended)

    assert added == ["june"]
    assert old["characters"]["june"]["present"] is False
    assert "player->june" in old["relationships"]


def test_removed_characters_are_kept_not_deleted(library):
    """A downgrade or a re-add must not lose history."""
    old = new_state(library, seed=1)
    reduced = ContentLibrary(
        characters={"iris": library.characters["iris"]},
        locations=library.locations,
        knowledge=library.knowledge,
        items=library.items,
        storylets=library.storylets,
        anchors=library.anchors,
    )
    sync_with_library(old, reduced)
    assert "theo" in old["characters"]


# ---------------------------------------------------------------------------
# Cross-run meta
# ---------------------------------------------------------------------------


def test_new_meta_is_empty_and_versioned():
    fresh = meta.new_meta()
    assert fresh["schema_version"] == META_SCHEMA_VERSION
    assert fresh["runs_started"] == 0
    assert meta.is_first_run(fresh)


def test_meta_migration_never_raises():
    """A player must always be able to launch, whatever their persistent file."""
    assert meta.migrate_meta(None)["runs_started"] == 0
    assert meta.migrate_meta({})["runs_started"] == 0
    assert meta.migrate_meta({"runs_started": 4})["runs_started"] == 4
    assert meta.migrate_meta({"schema_version": 999})["schema_version"] == META_SCHEMA_VERSION


def test_meta_records_are_idempotent():
    state = meta.new_meta()
    assert meta.record_discovery(state, "photo") is True
    assert meta.record_discovery(state, "photo") is False
    assert state["discoveries"] == ["photo"]


def test_meta_clues_gate_the_you_remember_option():
    state = meta.new_meta()
    assert not meta.remembers(state, "the_back_of_the_photo")
    meta.unlock_meta_clue(state, "the_back_of_the_photo")
    assert meta.remembers(state, "the_back_of_the_photo")


def test_first_run_detection():
    state = meta.new_meta()
    meta.start_run(state)
    assert meta.is_first_run(state)
    meta.start_run(state)
    assert not meta.is_first_run(state)
