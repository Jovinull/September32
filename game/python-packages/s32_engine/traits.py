"""Player tendencies, accumulated rather than chosen.

There is no class-select screen. The protagonist has no traits at the start of a
run; they acquire them by behaving a certain way, and the traits then open
occasional contextual lines that would not otherwise exist::

    [Observant] You have seen this keyring before.

Traits gate *additional* options; they never remove ordinary ones and never
substitute for the story's own logic. A player who never accumulates a trait
should not feel that content was withheld -- only that a different player would
have noticed something they did not.
"""

from __future__ import annotations

from s32_engine.types import TRAIT_AXES, TRAIT_MAX, TRAIT_MIN, GameState, TraitAxis

#: Score at which a trait starts unlocking contextual choices. Low on purpose:
#: three or four consistent decisions should be enough to be *seen* as curious.
TRAIT_THRESHOLD = 3

#: Display names for the bracketed prompt shown on a trait-gated choice.
TRAIT_LABELS: dict[str, str] = {
    "curious": "Observant",
    "direct": "Direct",
    "gentle": "Gentle",
    "sarcastic": "Sharp",
    "impulsive": "Impulsive",
    "reserved": "Reserved",
    "skeptical": "Skeptical",
    "empathetic": "Perceptive",
}


def get(state: GameState, axis: TraitAxis) -> int:
    """Return the current score for one trait axis."""
    return state["traits"].get(axis, 0)


def change(state: GameState, axis: TraitAxis, delta: int = 1) -> int:
    """Adjust a trait score, clamped, and return the new value."""
    if axis not in TRAIT_AXES:
        raise KeyError(f"unknown trait axis: {axis!r}")
    value = max(TRAIT_MIN, min(TRAIT_MAX, get(state, axis) + delta))
    state["traits"][axis] = value
    return value


def has(state: GameState, axis: TraitAxis, threshold: int = TRAIT_THRESHOLD) -> bool:
    """Return whether a trait has reached the threshold to be noticeable."""
    return get(state, axis) >= threshold


def label(axis: TraitAxis) -> str:
    """Return the bracketed display label for a trait-gated choice."""
    return TRAIT_LABELS.get(axis, axis.title())


def dominant(state: GameState, count: int = 3) -> list[tuple[str, int]]:
    """Return the highest-scoring traits, strongest first.

    Ties break on axis name so the debug screen and the ending summary do not
    reshuffle between two otherwise identical runs.
    """
    scored: list[tuple[str, int]] = [
        (axis, get(state, axis)) for axis in TRAIT_AXES if get(state, axis) > 0
    ]
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    return scored[:count]


def profile(state: GameState) -> str:
    """Return a one-line reading of the protagonist so far, for debug output."""
    top = dominant(state)
    if not top:
        return "no established tendencies yet"
    return ", ".join(f"{TRAIT_LABELS.get(axis, axis.title())} {score}" for axis, score in top)
