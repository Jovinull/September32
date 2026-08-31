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
    #: How often this player reconsiders where to be when they did not have to.
    #:
    #: The old model only moved when nothing at all was eligible, which meant
    #: location was decided by starvation and never by preference. Whole cells
    #: -- the gate in the afternoon, the road before dark -- were never visited
    #: in 5000 runs, and two storylets were consequently unreachable. This is
    #: the smallest honest fix: a student who has finished one thing sometimes
    #: goes to look for another, and which one depends on the student.
    mobility: float = 0.35
    #: Appetite for what an in-scene choice *does*, keyed by the verb or axis
    #: its declared effects touch. This is how a profile answers a question
    #: rather than merely picking a scene; the simulator used to resolve every
    #: menu uniformly at random, so two profiles that reached the same scene
    #: always left it in the same state.
    outcome_weights: dict[str, float] = field(default_factory=dict)

    def outcome_score(self, effects: tuple[str, ...]) -> float:
        """Return this profile's appetite for one declared outcome branch.

        Scored from the effect strings rather than from the prose, because the
        prose is not the model. An effect contributes if the profile has an
        opinion about the axis it moves (``trust``, ``attraction``) or about
        the verb it uses (``know``, ``commit``, ``break``).
        """
        score = 1.0
        for effect in effects:
            text = effect.strip()
            for key, weight in self.outcome_weights.items():
                touched = (
                    text.startswith(f"{key}(")
                    or f".{key} " in text
                    or text.startswith(f"trait {key}")
                )
                if touched:
                    score *= weight
        return max(0.01, score)

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
        mobility=0.5,
    ),
    "altruistic": Profile(
        name="altruistic",
        description="Chases friendship and keeps promises; avoids poking at the archive.",
        tag_weights={"friendship": 3.0, "slice_of_life": 2.0, "investigation": 0.5, "horror": 0.4},
        outcome_weights={"fulfil": 3.0, "break": 0.2, "commit": 2.0, "trust": 1.8, "gentle": 2.0},
        mobility=0.3,
    ),
    "curious": Profile(
        name="curious",
        description="Follows anything unexplained, at the cost of the people around them.",
        tag_weights={"mystery": 3.5, "investigation": 3.0, "archive": 2.5, "slice_of_life": 0.6},
        outcome_weights={"know": 3.0, "suspect": 2.0, "curious": 2.5, "reserved": 0.4},
        repeat_bias=0.4,
        mobility=0.55,
    ),
    "romantic": Profile(
        name="romantic",
        description="Optimises for one relationship and lets the rest drift.",
        tag_weights={"romance": 4.0, "character": 2.0, "investigation": 0.6},
        character_weights={"iris": 2.5},
        outcome_weights={"attraction": 4.0, "trust": 2.0, "gentle": 2.5, "direct": 0.5},
        mobility=0.35,
    ),
    "paranoid": Profile(
        name="paranoid",
        description="Assumes the worst. Seeks horror and evidence, trusts nobody.",
        tag_weights={"horror": 4.0, "mystery": 2.5, "meta": 2.0, "friendship": 0.4, "romance": 0.3},
        outcome_weights={"suspicion": 3.5, "suspect": 3.0, "skeptical": 2.5, "trust": 0.4},
        mobility=0.4,
    ),
    "completionist": Profile(
        name="completionist",
        description="Wants everything once. Strongly novelty-seeking.",
        outcome_weights={"know": 1.5, "curious": 1.5},
        repeat_bias=0.05,
        noise=0.3,
        mobility=0.7,
    ),
    "investigator": Profile(
        name="investigator",
        description="Methodical: archive first, people second, but keeps appointments.",
        tag_weights={"investigation": 3.0, "archive": 3.0, "mystery": 2.0, "romance": 0.5},
        outcome_weights={
            "know": 3.0,
            "fulfil": 2.0,
            "break": 0.3,
            "curious": 2.0,
            "attraction": 0.4,
        },
        repeat_bias=0.3,
        mobility=0.5,
    ),
    "selfish": Profile(
        name="selfish",
        description="Takes what is useful and drops commitments without hesitating.",
        tag_weights={"investigation": 2.0, "friendship": 0.3, "romance": 0.7},
        outcome_weights={"break": 3.0, "fulfil": 0.3, "direct": 2.0, "know": 1.5, "gentle": 0.3},
        repeat_bias=1.4,
        mobility=0.35,
    ),
    "impulsive": Profile(
        name="impulsive",
        description="Whatever is loudest right now. Near-random with a bias to novelty.",
        tag_weights={"horror": 1.6, "romance": 1.6, "mystery": 1.4},
        outcome_weights={"direct": 2.5, "reserved": 0.3, "break": 1.8},
        noise=0.6,
        mobility=0.6,
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
