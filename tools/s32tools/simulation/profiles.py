"""Player profiles for the headless simulator.

A profile is a *choice strategy*, not an AI. It answers one question -- given
several eligible storylets, which does this kind of player gravitate toward? --
by scoring each candidate's tags and characters.

The profiles are deliberately crude. Their job is coverage: between them they
should push the state space into corners a single scripted playthrough would
never reach, so that unreachable content shows up as unreachable. A profile that
played *well* would be worse at that.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from s32_engine.types import GameState, StoryletDef


@dataclass(frozen=True, slots=True)
class Profile:
    """A weighted preference over storylet tags and characters."""

    name: str
    description: str
    tag_weights: dict[str, float] = field(default_factory=dict)
    character_weights: dict[str, float] = field(default_factory=dict)
    #: Multiplier applied to a storylet already seen this run. Above 1.0 means
    #: the profile happily revisits; below means it chases novelty.
    repeat_bias: float = 1.0
    #: Probability of ignoring preference entirely and picking at random. Keeps
    #: a profile from carving one deep groove and reporting the rest unreachable.
    noise: float = 0.15

    def score(self, storylet: StoryletDef, state: GameState) -> float:
        """Return this profile's appetite for a storylet. Always positive."""
        score = 1.0
        for tag in storylet.tags:
            score *= self.tag_weights.get(tag, 1.0)
        for char in storylet.characters:
            score *= self.character_weights.get(char, 1.0)
        if state["seen_counts"].get(storylet.id):
            score *= self.repeat_bias
        return max(0.01, score)


PROFILES: dict[str, Profile] = {
    "random": Profile(
        name="random",
        description="No preferences at all. The control group, and the broadest explorer.",
        noise=1.0,
    ),
    "altruistic": Profile(
        name="altruistic",
        description="Chases friendship and keeps promises; avoids poking at the archive.",
        tag_weights={"friendship": 3.0, "slice_of_life": 2.0, "investigation": 0.5, "horror": 0.4},
    ),
    "curious": Profile(
        name="curious",
        description="Follows anything unexplained, at the cost of the people around them.",
        tag_weights={"mystery": 3.5, "investigation": 3.0, "archive": 2.5, "slice_of_life": 0.6},
        repeat_bias=0.4,
    ),
    "romantic": Profile(
        name="romantic",
        description="Optimises for one relationship and lets the rest drift.",
        tag_weights={"romance": 4.0, "character": 2.0, "investigation": 0.6},
        character_weights={"iris": 2.5},
    ),
    "paranoid": Profile(
        name="paranoid",
        description="Assumes the worst. Seeks horror and evidence, trusts nobody.",
        tag_weights={"horror": 4.0, "mystery": 2.5, "meta": 2.0, "friendship": 0.4, "romance": 0.3},
    ),
    "completionist": Profile(
        name="completionist",
        description="Wants everything once. Strongly novelty-seeking.",
        repeat_bias=0.05,
        noise=0.3,
    ),
    "investigator": Profile(
        name="investigator",
        description="Methodical: archive first, people second, but keeps appointments.",
        tag_weights={"investigation": 3.0, "archive": 3.0, "mystery": 2.0, "romance": 0.5},
        repeat_bias=0.3,
    ),
    "selfish": Profile(
        name="selfish",
        description="Takes what is useful and drops commitments without hesitating.",
        tag_weights={"investigation": 2.0, "friendship": 0.3, "romance": 0.7},
        repeat_bias=1.4,
    ),
    "impulsive": Profile(
        name="impulsive",
        description="Whatever is loudest right now. Near-random with a bias to novelty.",
        tag_weights={"horror": 1.6, "romance": 1.6, "mystery": 1.4},
        noise=0.6,
    ),
}

#: Profiles used when the caller does not name any. All of them: the point of a
#: coverage sweep is breadth, and the runs are cheap.
DEFAULT_PROFILES: tuple[str, ...] = tuple(PROFILES)


def get(name: str) -> Profile:
    """Return a profile by name.

    Raises:
        KeyError: With the available names listed, since this is user input from
            the command line.
    """
    try:
        return PROFILES[name]
    except KeyError:
        raise KeyError(
            f"unknown profile {name!r}; available: {', '.join(sorted(PROFILES))}"
        ) from None
