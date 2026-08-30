"""World simulation: weather, and finding somewhere worth being.

Two small systems that the storylet architecture turns out to need.

**Weather** is the cheapest source of variation that changes which scenes exist
without changing what they mean. A conversation on a roof in the rain is a
different conversation. Rain also has to actually *happen*, which sounds obvious
until the simulator reports that a scene gated on ``weather == rain`` is
unreachable because nothing in the content ever makes it rain -- which is exactly
what happened here.

**Location choice** matters because a quality-based narrative is only as good as
the player's ability to find the content. A player who cannot tell where anything
is happening experiences the same combinatorial richness as an empty corridor.
:func:`locations_with_content` is what lets the game, and the simulator's model
of a player, go where something is.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from s32_engine.types import WEATHERS, ContentLibrary, GameState, Weather

if TYPE_CHECKING:
    from s32_engine.director import NarrativeDirector
    from s32_engine.rng import Rng

#: Weather transition weights: current -> {next: weight}.
#:
#: A Markov chain rather than an independent daily roll, because weather that
#: has no memory reads as noise. The chain is biased toward persistence, and
#: every state can reach rain within a couple of days -- a scene gated on rain
#: must be something a patient player can wait for, not a lottery.
TRANSITIONS: dict[Weather, dict[Weather, float]] = {
    "clear": {"clear": 4.0, "overcast": 3.0, "wind": 1.5, "heat": 1.0, "rain": 0.5},
    "overcast": {"overcast": 3.0, "rain": 3.5, "clear": 2.0, "fog": 1.5, "wind": 1.0},
    "rain": {"rain": 2.5, "overcast": 3.5, "storm": 1.0, "clear": 1.5, "fog": 1.0},
    "storm": {"rain": 4.0, "overcast": 2.5, "clear": 1.0},
    "fog": {"fog": 2.0, "overcast": 3.0, "clear": 2.0, "rain": 1.5},
    "wind": {"wind": 2.0, "clear": 3.0, "overcast": 2.5, "rain": 1.5, "cold": 1.0},
    "heat": {"heat": 2.5, "clear": 3.0, "storm": 1.0, "overcast": 1.5},
    "cold": {"cold": 2.5, "clear": 2.0, "overcast": 2.5, "fog": 1.5},
}


def roll_weather(state: GameState, rng: Rng) -> Weather:
    """Advance the weather one day and return the new value.

    Called on a day rollover, not on every time slot: weather that changes
    between lunch and the afternoon is weather nobody can plan around, and
    planning around it is the point.
    """
    current: Weather = state["world"]["weather"]
    table = TRANSITIONS.get(current, TRANSITIONS["clear"])
    options = sorted(table)
    weights = [table[option] for option in options]
    new_weather = rng.weighted_choice(options, weights)
    state["world"]["weather"] = new_weather
    return new_weather


def is_valid_weather(value: str) -> bool:
    """Return whether a string names a real weather state."""
    return value in WEATHERS


def locations_with_content(
    state: GameState,
    library: ContentLibrary,
    director: NarrativeDirector,
    rng: Rng | None = None,
) -> list[str]:
    """Return locations where at least one storylet is currently eligible.

    Evaluates each location by temporarily moving the player there and asking
    the director. The temporary move is restored before returning, so the caller
    sees no side effect beyond the RNG counter that ``chance()`` conditions
    consume.

    This is not cheating on the player's behalf. It answers the question a
    student in a small school can answer by looking: is anyone in the club room
    right now?
    """
    original = state["world"]["location"]
    found: list[str] = []
    try:
        for location_id in sorted(library.locations):
            state["world"]["location"] = location_id
            if director.any_eligible(state, rng):
                found.append(location_id)
    finally:
        state["world"]["location"] = original
    return found
