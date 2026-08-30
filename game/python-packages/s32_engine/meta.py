"""Cross-run meta state (Ren'Py ``persistent``).

The design rule this module enforces: **the protagonist does not remember. The
player does.** Nothing here feeds back into the protagonist's knowledge
automatically. What it does is record what the *player* has seen across runs, so
that a later run can occasionally offer a choice the player -- not the character
-- has earned::

    [You remember.] Turn the photograph over.

Used sparingly. See ``docs/narrative-design/META.md`` for the budget, and
``docs/decisions/ADR-0004`` for why none of this involves reaching outside the
game.

Only genuinely cross-run facts belong here. Per-run state in ``persistent`` is
the classic way to produce a save file that contradicts itself.
"""

from __future__ import annotations

from typing import Any, TypedDict

from s32_engine.version import META_SCHEMA_VERSION


class MetaState(TypedDict):
    """Everything that survives between playthroughs."""

    schema_version: int
    runs_started: int
    runs_completed: int
    endings_seen: list[str]
    discoveries: list[str]
    anchors_seen: list[str]
    gallery_unlocked: list[str]
    meta_clues: list[str]


def new_meta() -> MetaState:
    """Return a fresh meta-state for a player who has never played before."""
    return {
        "schema_version": META_SCHEMA_VERSION,
        "runs_started": 0,
        "runs_completed": 0,
        "endings_seen": [],
        "discoveries": [],
        "anchors_seen": [],
        "gallery_unlocked": [],
        "meta_clues": [],
    }


def migrate_meta(raw: dict[str, Any] | None) -> MetaState:
    """Bring a persistent blob up to the current meta schema.

    Unlike save migration, this must never raise: a player whose ``persistent``
    file is from a newer build should still be able to launch. Unknown keys are
    preserved as-is so that downgrading and re-upgrading does not lose unlocks.
    """
    if not raw:
        return new_meta()

    meta = new_meta()
    for key in meta:
        if key in raw:
            meta[key] = raw[key]  # type: ignore[literal-required]
    meta["schema_version"] = META_SCHEMA_VERSION
    return meta


def _add(meta: MetaState, key: str, value: str) -> bool:
    """Append to a set-like list field, preserving insertion order."""
    bucket: list[str] = meta[key]  # type: ignore[literal-required]
    if value in bucket:
        return False
    bucket.append(value)
    return True


def record_discovery(meta: MetaState, discovery_id: str) -> bool:
    """Record something the player has now seen at least once. Returns novelty."""
    return _add(meta, "discoveries", discovery_id)


def record_ending(meta: MetaState, ending_id: str) -> bool:
    """Record an ending reached; also counts the run as completed."""
    meta["runs_completed"] += 1
    return _add(meta, "endings_seen", ending_id)


def record_anchor(meta: MetaState, anchor_id: str) -> bool:
    """Record that an anchor beat has been witnessed in some run."""
    return _add(meta, "anchors_seen", anchor_id)


def unlock_meta_clue(meta: MetaState, clue_id: str) -> bool:
    """Unlock a cross-run clue, the thing ``[You remember.]`` options key off."""
    return _add(meta, "meta_clues", clue_id)


def remembers(meta: MetaState, clue_id: str) -> bool:
    """Return whether the *player* has earned a given meta clue."""
    return clue_id in meta["meta_clues"]


def start_run(meta: MetaState) -> int:
    """Increment and return the run counter."""
    meta["runs_started"] += 1
    return meta["runs_started"]


def is_first_run(meta: MetaState) -> bool:
    """Return whether this is the player's very first run.

    First-run pacing differs: nothing meta may surface, and the ordinary school
    days must be allowed to be ordinary.
    """
    return meta["runs_started"] <= 1
