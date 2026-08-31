"""Creation, access and migration of the per-run :class:`GameState`.

The state is a nested tree of dicts, lists and scalars — no custom classes. That
is a deliberate constraint, not laziness: Ren'Py's rollback can only undo
mutations to containers it controls, and a class instance created by this package
would save and load fine while silently failing to roll back. That is the worst
class of bug in a visual novel, because it only appears after the player presses
scroll-up.

Two rules follow, and both are load-bearing:

* **Containers come from** :mod:`s32_engine.containers`, never from a literal.
  Under Ren'Py those factories produce revertable types; everywhere else they are
  the builtins. A single ``{}`` written here would be a plain dict that does not
  roll back.
* **Helpers mutate in place** rather than rebinding, and never cache a reference
  to part of the state across an interaction.
"""

from __future__ import annotations

from typing import Any, cast

from s32_engine.containers import adopt, new_dict, new_list
from s32_engine.errors import StateError
from s32_engine.types import (
    AXIS_MAX,
    AXIS_MIN,
    PLAYER,
    RELATIONSHIP_AXES,
    TRAIT_AXES,
    CharacterState,
    ContentLibrary,
    GameState,
    WorldState,
)
from s32_engine.version import GAME_VERSION, SAVE_SCHEMA_VERSION

#: Starting in-fiction date. The month name is data, not a computed date, because
#: the whole point of the story is that this calendar does not behave.
START_MONTH = "September"
START_CALENDAR_DAY = 1


def new_state(library: ContentLibrary, *, seed: int = 0) -> GameState:
    """Build a fresh run state seeded from the authored content library.

    Args:
        library: Loaded content. Characters present here get a state entry, so a
            newly authored character needs no separate bootstrap step.
        seed: Deterministic seed for :mod:`s32_engine.rng`. ``0`` is a valid
            seed; the caller decides whether to randomise it.

    Returns:
        A complete, valid :class:`GameState`.
    """
    # The container factories return `Any` because the host chooses the concrete
    # type; the casts are where that deliberate looseness stops.
    world: WorldState = new_dict(
        {
            "day": 1,
            "calendar_day": START_CALENDAR_DAY,
            "month": START_MONTH,
            "time_slot": "morning",
            "weather": "clear",
            "phase": "normal",
            "location": "school_gate",
            "flags": new_dict(),
            "recent_events": new_list(),
        }
    )

    characters: dict[str, CharacterState] = new_dict()
    relationships: dict[str, dict[str, int]] = new_dict()
    for char_id in sorted(library.characters):
        characters[char_id] = _blank_character()
        # Both directions. Seeding only ``player->x`` meant a scene reading
        # ``x->player`` -- which is what almost every scene means -- hit a
        # missing key on a fresh run and after a rollback past the first change.
        relationships[_pair_key(PLAYER, char_id)] = _blank_axes()
        relationships[_pair_key(char_id, PLAYER)] = _blank_axes()

    return cast(
        "GameState",
        new_dict(
            {
                "save_schema_version": SAVE_SCHEMA_VERSION,
                "game_version": GAME_VERSION,
                "seed": seed,
                "rng_counter": 0,
                "world": world,
                "characters": characters,
                "relationships": relationships,
                "beliefs": new_dict(),
                "traits": new_dict(dict.fromkeys(TRAIT_AXES, 0)),
                "commitments": new_list(),
                "inventory": new_list(),
                "history": new_list(),
                "seen_counts": new_dict(),
                "last_seen_day": new_dict(),
                "anchors_done": new_list(),
                "documents_read": new_list(),
            }
        ),
    )


def _blank_axes() -> dict[str, int]:
    """Return a relationship vector with every axis at its neutral floor."""
    return cast("dict[str, int]", new_dict(dict.fromkeys(RELATIONSHIP_AXES, AXIS_MIN)))


def _blank_character() -> CharacterState:
    """Return the starting state for one character."""
    return cast(
        "CharacterState",
        new_dict(
            {
                "present": False,
                "availability": 50,
                "mood": "neutral",
                "location": "",
                "goal": "",
                "flags": new_dict(),
            }
        ),
    )


def _pair_key(source: str, target: str) -> str:
    """Return the canonical directed key for a relationship pair.

    Directed, not symmetric: Iris trusting Theo says nothing about Theo trusting
    Iris, and the story depends on that asymmetry.
    """
    return f"{source}->{target}"


def pair_key(source: str, target: str) -> str:
    """Public alias for the directed relationship key format."""
    return _pair_key(source, target)


# ---------------------------------------------------------------------------
# World helpers
# ---------------------------------------------------------------------------


def advance_time(state: GameState, slots: int = 1) -> None:
    """Advance the clock by ``slots`` time slots, rolling into the next day.

    Time slots are the natural cadence for storylet selection (see ADR-0002):
    the director runs when the clock moves, not every frame.
    """
    from s32_engine.types import TIME_SLOTS

    if slots < 0:
        raise StateError("cannot advance time by a negative number of slots")

    world = state["world"]
    index = TIME_SLOTS.index(world["time_slot"]) + slots
    days, remainder = divmod(index, len(TIME_SLOTS))
    world["time_slot"] = TIME_SLOTS[remainder]
    if days:
        world["day"] += days
        world["calendar_day"] += days
        expire_due_commitments(state)


def set_location(state: GameState, location_id: str) -> None:
    """Move the player to ``location_id``."""
    state["world"]["location"] = location_id


def flag(state: GameState, name: str, default: int = 0) -> int:
    """Read a world flag, defaulting to ``default`` when unset.

    World flags are integers rather than booleans so counters and small scales
    ("how many times has the player been caught in the archive after hours")
    do not each need their own bespoke field.
    """
    return state["world"]["flags"].get(name, default)


def set_flag(state: GameState, name: str, value: int) -> None:
    """Set a world flag to an exact value."""
    state["world"]["flags"][name] = int(value)


def bump_flag(state: GameState, name: str, delta: int = 1) -> int:
    """Add ``delta`` to a world flag and return the new value."""
    new_value = flag(state, name) + delta
    state["world"]["flags"][name] = new_value
    return new_value


def note_event(state: GameState, event: str, keep: int = 12) -> None:
    """Push a short event tag onto the rolling recent-events window.

    The window is capped so the save does not grow without bound over a long
    run; it exists for "did this just happen" checks, not as a full log.
    """
    events = state["world"]["recent_events"]
    events.append(event)
    del events[:-keep]


def expire_due_commitments(state: GameState) -> list[str]:
    """Mark active commitments whose due day has passed as expired.

    Returns:
        The ids of the commitments that just expired, so the caller can decide
        whether anybody notices.
    """
    from s32_engine.commitments import expire_overdue

    return expire_overdue(state)


# ---------------------------------------------------------------------------
# History helpers
# ---------------------------------------------------------------------------


def record_storylet(state: GameState, storylet_id: str) -> None:
    """Record that a storylet just played, updating history and counters."""
    world = state["world"]
    state["history"].append(
        new_dict({"id": storylet_id, "day": world["day"], "time_slot": world["time_slot"]})
    )
    state["seen_counts"][storylet_id] = state["seen_counts"].get(storylet_id, 0) + 1
    state["last_seen_day"][storylet_id] = world["day"]


def times_seen(state: GameState, storylet_id: str) -> int:
    """Return how many times a storylet has played this run."""
    return state["seen_counts"].get(storylet_id, 0)


def has_seen(state: GameState, storylet_id: str) -> bool:
    """Return whether a storylet has played at least once this run."""
    return storylet_id in state["seen_counts"]


def days_since_seen(state: GameState, storylet_id: str) -> int | None:
    """Return days elapsed since a storylet last played, or ``None`` if never."""
    last = state["last_seen_day"].get(storylet_id)
    if last is None:
        return None
    return state["world"]["day"] - last


# ---------------------------------------------------------------------------
# Save migration
# ---------------------------------------------------------------------------


def migrate_state(raw: dict[str, Any]) -> GameState:
    """Bring a state dict loaded from an old save up to the current schema.

    Ren'Py calls this from an ``after_load`` label. Migrations are written as
    small, ordered, forward-only steps; each one must leave the dict valid for
    the *next* step, and none may assume the content library is unchanged.

    Raises:
        StateError: If the save is newer than this build understands, which is
            unrecoverable and must be reported rather than guessed at.
    """
    version = int(raw.get("save_schema_version", 0))
    if version > SAVE_SCHEMA_VERSION:
        raise StateError(
            f"save schema v{version} is newer than this build (v{SAVE_SCHEMA_VERSION}); "
            "update the game to load it"
        )

    # Ordered, forward-only steps. Each must leave the dict valid for the next.
    if version < 2:
        _migrate_1_to_2(raw)
    if version < 3:
        _migrate_2_to_3(raw)

    raw["save_schema_version"] = SAVE_SCHEMA_VERSION
    # Rebuild through the configured factories. A save written by a build with a
    # different container seam — or unpickled as plain dicts — would otherwise
    # load fine and then fail to roll back.
    return cast("GameState", adopt(raw))


def _migrate_1_to_2(raw: dict[str, Any]) -> None:
    """v1 -> v2: the archive viewer needs to know what has already been read.

    A save from before the viewer existed has read nothing, so the empty list is
    the correct answer rather than a lossy default.
    """
    raw.setdefault("documents_read", [])


def _migrate_2_to_3(raw: dict[str, Any]) -> None:
    """v2 -> v3: relationships the player earned were stored on the wrong edge.

    Every authored scene wrote ``rel iris.trust += 3`` meaning *Iris* warming to
    the player, and the direction-less form stored it as the player's stance
    toward Iris. So a v2 save has the whole cast's feelings about the player
    filed under ``player->them``.

    Flipping is the correct repair rather than a heuristic: the old grammar had
    no way to express the player's own stance, so every ``player->x`` edge in a
    v2 save was written by the broken default and none was deliberate.

    Merged per axis rather than wholesale, because a state carries a zeroed
    vector for every pair from the moment it is created. Replacing the whole
    vector would let those placeholder zeros overwrite the values being
    repaired, or the reverse, depending on which key happened to be seen first.
    A value already sitting on the correct edge wins, since only content written
    after the fix could have put it there.
    """
    stored = raw.get("relationships")
    if not isinstance(stored, dict):
        return
    repaired: dict[str, Any] = {}
    flipped: dict[str, dict[str, int]] = {}
    for key, axes in stored.items():
        source, arrow, target = str(key).partition("->")
        if arrow and source == PLAYER and target != PLAYER:
            flipped[f"{target}->{PLAYER}"] = axes
        else:
            repaired[key] = axes
    for key, axes in flipped.items():
        correct = repaired.setdefault(key, {})
        for axis, value in axes.items():
            if not correct.get(axis):
                correct[axis] = value
    raw["relationships"] = repaired


def sync_with_library(state: GameState, library: ContentLibrary) -> list[str]:
    """Add state entries for characters authored since the save was written.

    Content added after a save exists is the normal case during development and
    should not invalidate saves. Removed characters are *kept* in the state
    rather than deleted, so a downgrade or a re-add does not lose history.

    Returns:
        The ids of characters that were newly added to the state.
    """
    added: list[str] = []
    for char_id in sorted(library.characters):
        if char_id not in state["characters"]:
            state["characters"][char_id] = _blank_character()
            added.append(char_id)
        for key in (_pair_key(PLAYER, char_id), _pair_key(char_id, PLAYER)):
            if key not in state["relationships"]:
                state["relationships"][key] = _blank_axes()

    for trait_axis in TRAIT_AXES:
        state["traits"].setdefault(trait_axis, 0)

    for vector in state["relationships"].values():
        for rel_axis in RELATIONSHIP_AXES:
            vector.setdefault(rel_axis, AXIS_MIN)

    return added


def clamp_axis(value: int) -> int:
    """Clamp a relationship or trait value into its legal range."""
    return max(AXIS_MIN, min(AXIS_MAX, value))
