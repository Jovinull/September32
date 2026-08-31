"""Headless playthrough simulation.

Running thousands of playthroughs without launching Ren'Py is what makes a
quality-based narrative maintainable. The combinatorics that make the system
worth building also make it impossible to reason about by hand: nobody can look
at forty storylets and say which state combination is unreachable. The simulator
can, empirically, and it gets more useful as the content grows.

What it does *not* do is play the game. It never touches ``.rpy`` prose, never
renders anything, and never sees a choice menu -- the storylet metadata is the
model. Its findings are therefore about *structure*: which scenes can fire, in
what order, how often, and which never fire at all.

Determinism: given a seed, a profile and a content library, a run is exactly
reproducible, because :class:`s32_engine.rng.Rng` is counter-based rather than
stateful. Reproducing a reported dead end is therefore a matter of copying the
seed out of the report.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from s32_engine.director import NarrativeDirector, Selection
from s32_engine.effects import apply_all
from s32_engine.rng import Rng
from s32_engine.state import advance_time, new_state, set_location
from s32_engine.types import PHASES, ContentLibrary, GameState, StoryletDef
from s32_engine.world import locations_with_content, roll_weather
from s32tools.simulation.profiles import Profile

#: Hard cap on time-slot advances per run, so a content bug cannot hang the tool.
MAX_STEPS = 400

#: In-fiction days a simulated run covers.
#:
#: The prototype has no endings, and it has a repeatable ambient storylet, so a
#: run would never exhaust its content and would always hit MAX_STEPS. A horizon
#: is the honest stand-in: it says "this is how much of a term we are modelling",
#: which is a statement about the content, not about the tool. Replace it with a
#: real ending condition once endings exist.
MAX_DAYS = 14

#: Consecutive empty steps before a run stops. Six slots is most of a day, so
#: content gated to one time of day still gets its chance before the run gives
#: up. Whether stopping counts as an ending or a dead end depends on the anchors
#: (see ``_anchors_complete``).
DEAD_END_THRESHOLD = 8


@dataclass(slots=True)
class RunResult:
    """The outcome of one simulated playthrough."""

    seed: int
    profile: str
    steps: int
    days: int
    final_phase: str
    storylets_played: list[str] = field(default_factory=list)
    anchors_reached: list[str] = field(default_factory=list)
    knowledge_gained: list[str] = field(default_factory=list)
    relationships: dict[str, dict[str, int]] = field(default_factory=dict)
    traits: dict[str, int] = field(default_factory=dict)
    commitments: dict[str, int] = field(default_factory=dict)
    tag_counts: dict[str, int] = field(default_factory=dict)
    dead_end: bool = False
    dead_end_at: str = ""
    #: How many storylets were eligible at each selection moment, and how many
    #: shared the top priority tier. These are different questions: five
    #: eligible scenes with one in the top tier still leaves the weighted draw
    #: nothing to draw from. Counted here rather than derived afterwards
    #: because the eligible set does not survive the run.
    eligible_hist: Counter[int] = field(default_factory=Counter)
    tier_hist: Counter[int] = field(default_factory=Counter)
    #: "location|time_slot" -> moments spent there, and eligible candidates
    #: summed over them, so the matrix can report a mean rather than a total.
    cell_moments: Counter[str] = field(default_factory=Counter)
    cell_eligible: Counter[str] = field(default_factory=Counter)
    cell_multi: Counter[str] = field(default_factory=Counter)


@dataclass(slots=True)
class SimulationResult:
    """Aggregated findings across many runs."""

    runs: int
    seed: int
    profiles: list[str]
    library_size: int
    reachable: set[str] = field(default_factory=set)
    unreachable: set[str] = field(default_factory=set)
    play_counts: Counter[str] = field(default_factory=Counter)
    anchor_counts: Counter[str] = field(default_factory=Counter)
    knowledge_counts: Counter[str] = field(default_factory=Counter)
    character_counts: Counter[str] = field(default_factory=Counter)
    tag_counts: Counter[str] = field(default_factory=Counter)
    phase_counts: Counter[str] = field(default_factory=Counter)
    dead_ends: int = 0
    dead_end_examples: list[RunResult] = field(default_factory=list)
    average_scenes: float = 0.0
    average_days: float = 0.0
    average_repeats: float = 0.0
    relationship_ranges: dict[str, tuple[int, int]] = field(default_factory=dict)
    rare_storylets: list[tuple[str, int]] = field(default_factory=list)
    eligible_hist: Counter[int] = field(default_factory=Counter)
    tier_hist: Counter[int] = field(default_factory=Counter)
    cell_moments: Counter[str] = field(default_factory=Counter)
    cell_eligible: Counter[str] = field(default_factory=Counter)
    cell_multi: Counter[str] = field(default_factory=Counter)


class Simulator:
    """Drives many runs of the director over a content library."""

    def __init__(self, library: ContentLibrary) -> None:
        self.library = library
        self.director = NarrativeDirector(library)
        self._locations = sorted(library.locations)
        # Which storylets could ever fire in each location. Scoring a candidate
        # destination otherwise walks the whole library once per location per
        # move, which the hot loop notices. A storylet with no declared location
        # can fire anywhere, so it appears in every list.
        self._by_location: dict[str, list[StoryletDef]] = {
            loc: [s for s in library.storylets.values() if not s.location or s.location == loc]
            for loc in self._locations
        }

    def run_once(
        self,
        seed: int,
        profile: Profile,
        *,
        max_steps: int = MAX_STEPS,
        max_days: int = MAX_DAYS,
    ) -> RunResult:
        """Simulate a single playthrough."""
        state = new_state(self.library, seed=seed)
        rng = Rng(state)
        played: list[str] = []
        empty_streak = 0
        step = 0

        # Everyone is present by default. Availability is modelled by the
        # storylets themselves, not by a scheduler; adding one here would be a
        # simulation of a system the game does not have.
        for char in state["characters"].values():
            char["present"] = True

        eligible_hist: Counter[int] = Counter()
        tier_hist: Counter[int] = Counter()
        cell_moments: Counter[str] = Counter()
        cell_eligible: Counter[str] = Counter()
        cell_multi: Counter[str] = Counter()

        for step in range(1, max_steps + 1):
            self._fire_ready_anchor(state, rng)

            selection = self.director.select(state, rng, keep_trace=False)

            # Every pass through here is a moment the director was asked for a
            # scene, including the ones where it had nothing. Measured before
            # the profile gets a say, because this is about what the *director*
            # was offered.
            eligible = selection.eligible
            count = len(eligible)
            eligible_hist[count] += 1
            if eligible:
                top = max(e.priority for e in eligible)
                tier_hist[sum(1 for e in eligible if e.priority == top)] += 1
            cell = f"{state['world']['location']}|{state['world']['time_slot']}"
            cell_moments[cell] += 1
            cell_eligible[cell] += count
            if count >= 2:  # two is the definition of a choice
                cell_multi[cell] += 1

            if selection.storylet is None:
                empty_streak += 1
                if empty_streak >= DEAD_END_THRESHOLD:
                    # Nothing has been eligible anywhere for several slots. If
                    # the anchors are all done, the run has simply run out of
                    # content, which is the prototype's real ending condition.
                    # If anchors remain, the run is genuinely stuck and that is
                    # a content bug worth reporting.
                    return self._finish(
                        state,
                        seed,
                        profile,
                        step,
                        played,
                        density=(
                            eligible_hist,
                            tier_hist,
                            cell_moments,
                            cell_eligible,
                            cell_multi,
                        ),
                        dead_end=not self._anchors_complete(state),
                        dead_end_at=f"day {state['world']['day']} {state['world']['time_slot']} "
                        f"@ {state['world']['location']}",
                    )
                self._wander(state, rng, profile)
                continue

            empty_streak = 0
            chosen = self._apply_profile(selection, state, rng, profile)
            self.director.play(chosen, state)
            self._resolve_outcome(chosen, state, rng, profile)
            played.append(chosen.id)
            self._advance(state, rng)

            # Having done one thing, this player sometimes goes to look for
            # another. Without this the only reason to change location is
            # starvation, and a location that always has something ambient on
            # offer -- the courtyard -- becomes a place a run never leaves.
            if rng.random() < profile.mobility:
                self._relocate(state, rng, profile)

            if state["world"]["day"] > max_days:
                break

        return self._finish(
            state,
            seed,
            profile,
            step,
            played,
            density=(eligible_hist, tier_hist, cell_moments, cell_eligible, cell_multi),
        )

    def _apply_profile(
        self,
        selection: Selection,
        state: GameState,
        rng: Rng,
        profile: Profile,
    ) -> StoryletDef:
        """Re-pick within the top priority tier according to the profile.

        The director already applied its own hard priority rule; the profile
        only expresses taste inside that tier. Letting a profile override
        priority would test a game nobody is going to ship.
        """
        from s32_engine.director import Selection

        assert isinstance(selection, Selection)
        assert selection.storylet is not None

        eligible = selection.eligible
        top = max(e.priority for e in eligible)
        tier = [self.library.storylets[e.storylet_id] for e in eligible if e.priority == top]
        if len(tier) == 1 or rng.random() < profile.noise:
            return selection.storylet
        return rng.weighted_choice(tier, [profile.score(s, state) for s in tier])

    def _fire_ready_anchor(self, state: GameState, rng: Rng) -> None:
        """Play the next anchor if its requirements are met."""
        pending = self.director.next_anchor(state, rng)
        if pending is None:
            return
        anchor_id, ready = pending
        if not ready:
            return
        anchor = self.library.anchors[anchor_id]
        apply_all(anchor.effects, state)
        if anchor.outcomes:
            apply_all(rng.choice(anchor.outcomes), state)
        if anchor_id not in state["anchors_done"]:
            state["anchors_done"].append(anchor_id)

    def _resolve_outcome(
        self, storylet: StoryletDef, state: GameState, rng: Rng, profile: Profile
    ) -> None:
        """Apply one of a storylet's declared choice outcomes.

        Resolution used to be uniform, on the reasoning that a reachability
        sweep wants every branch taken. That was true and it was also why every
        profile finished a run in the same state: two players who reached the
        same scene always left it identically, so nothing downstream could
        diverge.

        Now the profile answers, scored from the declared effects, and
        ``profile.noise`` keeps the uniform behaviour often enough that no
        branch becomes unreachable. A profile with no ``outcome_weights`` scores
        every branch 1.0 and is therefore exactly the old behaviour.
        """
        from s32_engine.types import StoryletDef

        assert isinstance(storylet, StoryletDef)
        if not storylet.outcomes:
            return
        if len(storylet.outcomes) == 1 or rng.random() < profile.noise:
            apply_all(rng.choice(storylet.outcomes), state)
            return
        chosen = rng.weighted_choice(
            list(storylet.outcomes),
            [profile.outcome_score(branch) for branch in storylet.outcomes],
        )
        apply_all(chosen, state)

    def _advance(self, state: GameState, rng: Rng) -> None:
        """Move the clock forward one slot, rolling the weather on a new day."""
        before = state["world"]["day"]
        advance_time(state, 1)
        if state["world"]["day"] != before:
            roll_weather(state, rng)

    def _wander(self, state: GameState, rng: Rng, profile: Profile) -> None:
        """Nothing fits here: go where something is happening, and let time pass.

        Modelling this correctly matters more than it looks. A purely random
        walk makes every location-gated storylet look unreachable and floods the
        report with dead ends that no real player would experience -- a student
        in a small school can see where people are. So the model looks for a
        location with eligible content and goes there, and only falls back to a
        random move when nowhere has anything.

        The fallback is what keeps the dead-end metric honest: a genuine dead
        end is now "nowhere in the world has anything for me", which is a real
        content bug, rather than "I guessed wrong six times".
        """
        if not self._relocate(state, rng, profile) and self._locations:
            set_location(state, rng.choice(self._locations))
        self._advance(state, rng)

    def _relocate(self, state: GameState, rng: Rng, profile: Profile) -> bool:
        """Move to a location this profile wants to be in. Time does not pass.

        The candidate set is :func:`locations_with_content` -- the same list the
        game offers the player on the travel screen, so the model is choosing
        from what a player can actually see rather than from the library. What
        the profile adds is a reason to prefer one of them, which is the half
        that was missing: destinations used to be drawn uniformly, so a profile
        could not express that it would rather be in the archive than the gate.

        Returns:
            Whether the player moved. False means nowhere in the world has
            anything, which is the dead-end condition and the caller's problem.
        """
        options = locations_with_content(state, self.library, self.director, rng)
        if not options:
            return False
        set_location(
            state,
            rng.weighted_choice(
                options, [self._appetite(state, rng, profile, option) for option in options]
            ),
        )
        return True

    def _appetite(self, state: GameState, rng: Rng, profile: Profile, location: str) -> float:
        """Return how much this profile wants to be in ``location`` right now.

        Summed rather than averaged: a location with three things the player
        half-wants is a better place to be than one with a single thing they
        half-want, and the busy-place-is-attractive reading is the one a student
        would recognise.
        """
        original = state["world"]["location"]
        state["world"]["location"] = location
        try:
            return sum(
                profile.score(storylet, state)
                for storylet in self._by_location[location]
                if self.director.is_eligible(storylet, state, rng)
            )
        finally:
            state["world"]["location"] = original

    def _anchors_complete(self, state: GameState) -> bool:
        """Return whether every anchor beat has played.

        Deliberately NOT the stopping rule. Ending a run the moment the last
        anchor fires cuts it short on day two and makes late content look
        unreachable — which is exactly the false report this replaced. A run
        stops when the world has nothing left to offer; the anchors only decide
        whether that counts as an ending or as a dead end.
        """
        return len(state["anchors_done"]) >= len(self.library.anchors) > 0

    def _finish(
        self,
        state: GameState,
        seed: int,
        profile: Profile,
        steps: int,
        played: list[str],
        *,
        density: tuple[Counter[int], Counter[int], Counter[str], Counter[str], Counter[str]]
        | None = None,
        dead_end: bool = False,
        dead_end_at: str = "",
    ) -> RunResult:
        """Package the final state into a :class:`RunResult`."""
        eligible_hist, tier_hist, cell_moments, cell_eligible, cell_multi = density or (
            Counter(),
            Counter(),
            Counter(),
            Counter(),
            Counter(),
        )
        tag_counts: Counter[str] = Counter()
        for sid in played:
            tag_counts.update(self.library.storylets[sid].tags)

        return RunResult(
            seed=seed,
            profile=profile.name,
            steps=steps,
            days=state["world"]["day"],
            final_phase=state["world"]["phase"],
            storylets_played=played,
            anchors_reached=list(state["anchors_done"]),
            knowledge_gained=sorted(
                fact
                for fact, belief in state["beliefs"].get("player", {}).items()
                if belief["stance"] == "known"
            ),
            relationships={k: dict(v) for k, v in state["relationships"].items()},
            traits=dict(state["traits"]),
            commitments=dict(Counter(c["status"] for c in state["commitments"])),
            tag_counts=dict(tag_counts),
            dead_end=dead_end,
            dead_end_at=dead_end_at,
            eligible_hist=eligible_hist,
            tier_hist=tier_hist,
            cell_moments=cell_moments,
            cell_eligible=cell_eligible,
            cell_multi=cell_multi,
        )

    # -- aggregation --------------------------------------------------------

    def run_many(
        self,
        runs: int,
        profiles: list[Profile],
        *,
        seed: int = 0,
        max_steps: int = MAX_STEPS,
        max_days: int = MAX_DAYS,
        keep_dead_end_examples: int = 5,
    ) -> SimulationResult:
        """Simulate ``runs`` playthroughs, cycling through ``profiles``."""
        if not profiles:
            raise ValueError("at least one profile is required")

        result = SimulationResult(
            runs=runs,
            seed=seed,
            profiles=[p.name for p in profiles],
            library_size=len(self.library.storylets),
        )
        total_scenes = 0
        total_days = 0
        total_repeats = 0
        axis_ranges: dict[str, list[int]] = {}

        for index in range(runs):
            profile = profiles[index % len(profiles)]
            run = self.run_once(seed + index, profile, max_steps=max_steps, max_days=max_days)

            total_scenes += len(run.storylets_played)
            total_days += run.days
            counts = Counter(run.storylets_played)
            total_repeats += sum(c - 1 for c in counts.values())

            result.play_counts.update(counts)
            result.reachable.update(counts)
            result.anchor_counts.update(run.anchors_reached)
            result.knowledge_counts.update(run.knowledge_gained)
            result.tag_counts.update(run.tag_counts)
            result.phase_counts[run.final_phase] += 1
            for sid in counts:
                result.character_counts.update(self.library.storylets[sid].characters)

            for pair, vector in run.relationships.items():
                for axis, value in vector.items():
                    axis_ranges.setdefault(f"{pair}.{axis}", []).append(value)

            result.eligible_hist.update(run.eligible_hist)
            result.tier_hist.update(run.tier_hist)
            result.cell_moments.update(run.cell_moments)
            result.cell_eligible.update(run.cell_eligible)
            result.cell_multi.update(run.cell_multi)

            if run.dead_end:
                result.dead_ends += 1
                if len(result.dead_end_examples) < keep_dead_end_examples:
                    result.dead_end_examples.append(run)

        result.unreachable = set(self.library.storylets) - result.reachable
        result.average_scenes = total_scenes / runs if runs else 0.0
        result.average_days = total_days / runs if runs else 0.0
        result.average_repeats = total_repeats / runs if runs else 0.0
        result.relationship_ranges = {
            key: (min(values), max(values)) for key, values in sorted(axis_ranges.items())
        }
        result.rare_storylets = [
            (sid, count)
            for sid, count in sorted(result.play_counts.items(), key=lambda kv: (kv[1], kv[0]))
            if count <= max(1, runs // 100)
        ]
        for phase in PHASES:
            result.phase_counts.setdefault(phase, 0)
        return result
