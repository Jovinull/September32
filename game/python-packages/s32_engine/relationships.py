"""Multi-dimensional relationships between agents.

A single ``affection`` number cannot express the situations this story is built
on: someone can be loved and not trusted, respected and resented, depended on
and feared. Every pair therefore carries eight independent axes.

Relationships are **directed**. ``iris->theo`` is Iris's stance toward Theo and
says nothing about his toward her. NPC-to-NPC pairs use exactly the same storage
as player-to-NPC pairs, so the graph can grow without an architectural change
even though the prototype only exercises a few edges.
"""

from __future__ import annotations

from s32_engine.containers import new_dict
from s32_engine.state import clamp_axis, pair_key
from s32_engine.types import (
    AXIS_MAX,
    AXIS_MIN,
    PLAYER,
    RELATIONSHIP_AXES,
    GameState,
    RelationshipAxis,
)


def _vector(state: GameState, source: str, target: str) -> dict[str, int]:
    """Return the mutable axis vector for a pair, creating it if needed."""
    key = pair_key(source, target)
    vector = state["relationships"].get(key)
    if vector is None:
        vector = new_dict(dict.fromkeys(RELATIONSHIP_AXES, AXIS_MIN))
        state["relationships"][key] = vector
    return vector


def get(state: GameState, target: str, axis: RelationshipAxis, source: str = PLAYER) -> int:
    """Return one axis of ``source``'s relationship toward ``target``."""
    return _vector(state, source, target).get(axis, AXIS_MIN)


def vector(state: GameState, target: str, source: str = PLAYER) -> dict[str, int]:
    """Return a copy of the full axis vector from ``source`` toward ``target``."""
    return dict(_vector(state, source, target))


def change(
    state: GameState,
    target: str,
    axis: RelationshipAxis,
    delta: int,
    source: str = PLAYER,
) -> int:
    """Adjust one axis by ``delta``, clamped to ``[0, 100]``.

    Returns:
        The value after clamping, so callers can detect that a change was
        absorbed by the ceiling rather than silently assuming it landed.

    Example:
        >>> from s32_engine.state import new_state
        >>> from s32_engine.types import CharacterDef, ContentLibrary
        >>> lib = ContentLibrary(characters={"iris": CharacterDef("iris", "Iris", "archivist")})
        >>> st = new_state(lib)
        >>> change(st, "iris", "trust", 12)
        12
    """
    vec = _vector(state, source, target)
    vec[axis] = clamp_axis(vec.get(axis, AXIS_MIN) + delta)
    return vec[axis]


def set_axis(
    state: GameState,
    target: str,
    axis: RelationshipAxis,
    value: int,
    source: str = PLAYER,
) -> int:
    """Set one axis to an absolute value, clamped to ``[0, 100]``.

    Prefer :func:`change` in scene scripts. Absolute assignment is for anchors
    and migrations, where an exact post-condition matters more than the path.
    """
    vec = _vector(state, source, target)
    vec[axis] = clamp_axis(value)
    return vec[axis]


def apply(
    state: GameState,
    target: str,
    deltas: dict[str, int],
    source: str = PLAYER,
) -> dict[str, int]:
    """Apply several axis deltas at once and return the resulting vector.

    Most meaningful beats move more than one axis, and often in opposite
    directions -- a confession can raise ``attraction`` and ``fear`` together.
    """
    for axis, delta in deltas.items():
        if axis not in RELATIONSHIP_AXES:
            raise KeyError(f"unknown relationship axis: {axis!r}")
        change(state, target, axis, delta, source=source)
    return vector(state, target, source=source)


def edges(state: GameState, source: str | None = None) -> list[tuple[str, str]]:
    """Return every stored directed pair, optionally filtered by source.

    Used by the relationship inspector and by the graph exporter.
    """
    result: list[tuple[str, str]] = []
    for key in sorted(state["relationships"]):
        left, _, right = key.partition("->")
        if source is None or left == source:
            result.append((left, right))
    return result


# ---------------------------------------------------------------------------
# Derived readings
#
# These exist so scene conditions can ask a human question ("does she trust me
# enough to say this out loud?") instead of restating threshold arithmetic in
# fifty different storylet files.
# ---------------------------------------------------------------------------


def is_close(state: GameState, target: str, source: str = PLAYER) -> bool:
    """Return whether the pair reads as an actual friendship, not just contact."""
    vec = _vector(state, source, target)
    return vec["trust"] >= 55 and vec["familiarity"] >= 45


def is_strained(state: GameState, target: str, source: str = PLAYER) -> bool:
    """Return whether resentment or suspicion currently outweighs trust."""
    vec = _vector(state, source, target)
    return max(vec["resentment"], vec["suspicion"]) > vec["trust"]


def romantic_potential(state: GameState, target: str, source: str = PLAYER) -> int:
    """Score romantic viability on ``[0, 100]``.

    Attraction alone is not romance. This weights attraction by the trust and
    familiarity that make it mean anything, and subtracts fear, because a
    relationship built on fear is a different story and must not be scored as
    if it were this one.
    """
    vec = _vector(state, source, target)
    base = (vec["attraction"] * 2 + vec["trust"] + vec["familiarity"]) // 4
    return max(AXIS_MIN, min(AXIS_MAX, base - vec["fear"] // 2))


def summary(state: GameState, target: str, source: str = PLAYER) -> str:
    """Return a one-line human reading of a pair, for debug screens and logs."""
    vec = _vector(state, source, target)
    parts = [f"{axis}={vec[axis]}" for axis in RELATIONSHIP_AXES if vec[axis]]
    return f"{source}->{target}: " + (", ".join(parts) if parts else "no history")
