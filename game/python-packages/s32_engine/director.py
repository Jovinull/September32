"""The narrative director: which pre-written scene fits the world right now.

This is the piece that replaces nested ``if`` trees. Instead of the script
deciding what happens next, every storylet declares the situation it belongs in,
and the director looks at the current state and asks which ones fit. Content
scales additively: a new scene is a new file, not an edit to a branching tree
that already has forty leaves.

Two properties matter more than cleverness here:

**It never generates anything.** The director picks among authored scenes. There
is no runtime text generation of any kind in this project (ADR-0004).

**It explains itself.** Every evaluation produces a full trace of which clauses
passed and failed, with the actual values. At several hundred storylets, "why
didn't that fire?" is the question a writer will ask every day, and an engine
that cannot answer it is unusable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from s32_engine.conditions import ConditionContext, ConditionResult, evaluate_all
from s32_engine.conditions import evaluate as evaluate_condition
from s32_engine.effects import apply_all
from s32_engine.rng import Rng
from s32_engine.state import days_since_seen, record_storylet, times_seen
from s32_engine.types import ContentLibrary, GameState, StoryletDef

#: Storylets in these statuses never play. ``retired`` content stays on disk so
#: old saves referencing it still resolve, but it is not offered again.
EXCLUDED_STATUSES = frozenset({"retired"})


@dataclass(frozen=True, slots=True)
class Evaluation:
    """The full reasoning for one storylet at one moment."""

    storylet_id: str
    eligible: bool
    priority: int
    weight: float
    requirement_results: tuple[ConditionResult, ...] = ()
    blocker_results: tuple[ConditionResult, ...] = ()
    rejections: tuple[str, ...] = ()

    def format(self) -> str:
        """Return the multi-line debug block for this storylet."""
        lines = [f"Storylet: {self.storylet_id}", f"ELIGIBLE: {str(self.eligible).lower()}"]
        if self.eligible:
            lines.append(f"priority={self.priority} weight={self.weight:g}")
        if self.rejections:
            lines.append("Structural:")
            lines.extend(f"  FAIL {reason}" for reason in self.rejections)
        if self.requirement_results:
            lines.append("Requirements:")
            lines.extend(f"  {r.format()}" for r in self.requirement_results)
        if self.blocker_results:
            lines.append("Blockers (any pass blocks):")
            lines.extend(f"  {r.format()}" for r in self.blocker_results)
        return "\n".join(lines)


@dataclass(slots=True)
class Selection:
    """What the director chose, and everything it considered."""

    storylet: StoryletDef | None
    evaluations: list[Evaluation] = field(default_factory=list)

    @property
    def eligible(self) -> list[Evaluation]:
        """Return only the evaluations that came out eligible."""
        return [e for e in self.evaluations if e.eligible]

    def format(self, *, include_rejected: bool = False) -> str:
        """Return a readable summary, for the debug screen and the dev log."""
        chosen = self.storylet.id if self.storylet else "<none>"
        head = f"selected {chosen}  eligible={len(self.eligible)}/{len(self.evaluations)}"
        blocks = [e.format() for e in self.evaluations if include_rejected or e.eligible]
        return "\n\n".join([head, *blocks])


class NarrativeDirector:
    """Selects the next storylet for a given state.

    The director is stateless: it holds the content library (immutable) and
    nothing else. All mutable state is passed in per call, which is what lets
    the headless simulator run thousands of parallel runs through one instance,
    and what keeps Ren'Py rollback from ever seeing engine-owned state.
    """

    __slots__ = ("library",)

    def __init__(self, library: ContentLibrary) -> None:
        self.library = library

    # -- evaluation ---------------------------------------------------------

    def evaluate(
        self, storylet: StoryletDef, state: GameState, rng: Rng | None = None
    ) -> Evaluation:
        """Evaluate one storylet against the current state.

        Structural gates (status, location, time slot, phase, repeat policy,
        cooldown) are checked before the condition language runs. They are the
        cheap, common reasons a scene does not fit, and separating them keeps
        the trace readable: "wrong location" is a different kind of answer from
        "her trust is 22, needs 30".
        """
        rejections: list[str] = []
        world = state["world"]

        if storylet.status in EXCLUDED_STATUSES:
            rejections.append(f"status == {storylet.status}")

        if storylet.location and storylet.location != world["location"]:
            rejections.append(f"location == {storylet.location} (is {world['location']})")

        if storylet.time_slots and world["time_slot"] not in storylet.time_slots:
            rejections.append(
                f"time_slot in {','.join(storylet.time_slots)} (is {world['time_slot']})"
            )

        if storylet.phases and world["phase"] not in storylet.phases:
            rejections.append(f"phase in {','.join(storylet.phases)} (is {world['phase']})")

        seen = times_seen(state, storylet.id)
        if storylet.repeat_policy == "once" and seen:
            rejections.append("repeat_policy == once (already seen)")
        elif storylet.cooldown:
            since = days_since_seen(state, storylet.id)
            if since is not None and since < storylet.cooldown:
                rejections.append(f"cooldown {storylet.cooldown}d (last seen {since}d ago)")

        for char_id in storylet.characters:
            char = state["characters"].get(char_id)
            if char is None:
                rejections.append(f"character {char_id} missing from state")
            elif not char["present"]:
                rejections.append(f"character {char_id} not present")

        # Conditions are evaluated even when a structural gate already failed:
        # a writer debugging a scene wants the whole picture, not the first
        # thing that went wrong. The cost is a handful of dict lookups.
        ctx = ConditionContext(state, rng)
        requirement_results = tuple(evaluate_all(storylet.requirements, ctx))
        blocker_results = tuple(evaluate_all(storylet.blockers, ctx))

        eligible = (
            not rejections
            and all(r.passed for r in requirement_results)
            and not any(r.passed for r in blocker_results)
        )
        return Evaluation(
            storylet_id=storylet.id,
            eligible=eligible,
            priority=storylet.priority,
            weight=storylet.weight,
            requirement_results=requirement_results,
            blocker_results=blocker_results,
            rejections=tuple(rejections),
        )

    def evaluate_all(
        self,
        state: GameState,
        rng: Rng | None = None,
        *,
        candidates: list[str] | None = None,
    ) -> list[Evaluation]:
        """Evaluate every storylet (or a named subset) in stable id order."""
        ids = candidates if candidates is not None else self.library.storylet_ids()
        return [self.evaluate(self.library.storylets[sid], state, rng) for sid in ids]

    def is_eligible(  # noqa: PLR0911 - a gate per rejection reason is clearer than one boolean
        self, storylet: StoryletDef, state: GameState, rng: Rng | None = None
    ) -> bool:
        """Return whether a storylet can fire, without building a trace.

        :meth:`evaluate` deliberately checks everything so a writer sees every
        reason a scene did not fire. That is the right behaviour for a debug
        screen and the wrong one for a hot loop: the headless simulator asks
        this question millions of times and throws the answer away. So this path
        short-circuits and allocates nothing.

        The two must agree. ``tests/test_director.py`` asserts they do for every
        storylet in the library.
        """
        world = state["world"]

        if storylet.status in EXCLUDED_STATUSES:
            return False
        if storylet.location and storylet.location != world["location"]:
            return False
        if storylet.time_slots and world["time_slot"] not in storylet.time_slots:
            return False
        if storylet.phases and world["phase"] not in storylet.phases:
            return False

        if storylet.repeat_policy == "once":
            if times_seen(state, storylet.id):
                return False
        elif storylet.cooldown:
            since = days_since_seen(state, storylet.id)
            if since is not None and since < storylet.cooldown:
                return False

        for char_id in storylet.characters:
            char = state["characters"].get(char_id)
            if char is None or not char["present"]:
                return False

        ctx = ConditionContext(state, rng)
        if not all(evaluate_condition(r, ctx).passed for r in storylet.requirements):
            return False
        return all(not evaluate_condition(b, ctx).passed for b in storylet.blockers)

    def any_eligible(self, state: GameState, rng: Rng | None = None) -> bool:
        """Return whether any storylet at all can fire right now."""
        return any(
            self.is_eligible(storylet, state, rng) for storylet in self.library.storylets.values()
        )

    # -- selection ----------------------------------------------------------

    def select(
        self,
        state: GameState,
        rng: Rng,
        *,
        category: str | None = None,
        tags: set[str] | None = None,
        keep_trace: bool = True,
    ) -> Selection:
        """Choose the next storylet.

        Selection is two-stage, and the split is deliberate:

        1. **Priority is a hard tier.** Only the eligible storylets with the
           highest priority compete. This is how an anchor beat or a scene that
           must resolve today outranks ambient content without needing a
           probability so large it might as well be certainty.
        2. **Weight decides within the tier.** A weighted draw keeps repeat
           playthroughs from feeling scripted, and re-seen storylets are damped
           so a repeatable scene does not crowd out fresh content.

        Args:
            state: Run state. Mutated only through ``rng``'s counter.
            rng: Rollback-safe randomness.
            category: Restrict to one storylet category.
            tags: Restrict to storylets carrying at least one of these tags.
            keep_trace: Keep evaluations for rejected storylets. Turn off in the
                simulator's hot loop, where the trace is thrown away anyway.

        Returns:
            A :class:`Selection`; ``storylet`` is ``None`` when nothing fits,
            which is a normal outcome the caller must handle (usually by
            advancing time).
        """
        candidate_ids = [
            sid
            for sid, s in sorted(self.library.storylets.items())
            if (category is None or s.category == category)
            and (tags is None or bool(tags & set(s.tags)))
        ]

        evaluations = self.evaluate_all(state, rng, candidates=candidate_ids)
        eligible = [e for e in evaluations if e.eligible]
        trace = evaluations if keep_trace else eligible

        if not eligible:
            return Selection(None, trace)

        top_priority = max(e.priority for e in eligible)
        tier = [e for e in eligible if e.priority == top_priority]

        chosen = rng.weighted_choice(
            [e.storylet_id for e in tier],
            [self._effective_weight(state, e) for e in tier],
        )
        return Selection(self.library.storylets[chosen], trace)

    def _effective_weight(self, state: GameState, evaluation: Evaluation) -> float:
        """Return a storylet's weight after repetition damping.

        Each previous play halves the weight. Repeatable content should be
        available, not insistent: without damping, a high-weight ambient scene
        reappears immediately and reads as a bug even though it is legal.
        """
        seen = times_seen(state, evaluation.storylet_id)
        return evaluation.weight / (2.0**seen)

    # -- application --------------------------------------------------------

    def play(self, storylet: StoryletDef, state: GameState) -> list[str]:
        """Apply a storylet's effects and record it in the history.

        Called *after* the Ren'Py label has run, not before: a scene's effects
        should land once the player has actually seen it, so that a rollback
        past the scene also rolls back its consequences.

        Returns:
            Per-effect descriptions, for the dev log.
        """
        changes = apply_all(storylet.effects, state)
        record_storylet(state, storylet.id)
        return changes

    # -- anchors ------------------------------------------------------------

    def next_anchor(self, state: GameState, rng: Rng | None = None) -> tuple[str, bool] | None:
        """Return the next anchor in order and whether it is ready to fire.

        Anchors are strictly ordered, so this returns the first one not yet
        done, together with whether its requirements are currently met. A caller
        that gets ``(id, False)`` knows what the run is working toward, which is
        what the pacing report needs.
        """
        ctx = ConditionContext(state, rng)
        for anchor in sorted(self.library.anchors.values(), key=lambda a: (a.order, a.id)):
            if anchor.id in state["anchors_done"]:
                continue
            results = evaluate_all(anchor.requirements, ctx)
            return anchor.id, all(r.passed for r in results)
        return None
