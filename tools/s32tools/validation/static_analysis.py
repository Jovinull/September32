"""Static reachability analysis over the content graph.

The simulator answers "did any of a thousand runs reach this?". This module
answers the stronger, cheaper question: "could *any* run reach this, ever?" It
does so without simulating, by propagating a monotone over-approximation of what
a run can accumulate.

The approximation is deliberate. Full satisfiability over the condition language
is unnecessary here and would be a maintenance liability: what actually breaks in
practice is a typo in a fact name, a threshold nothing can raise a value to, and
a storylet whose location gate contradicts its own requirements. Those are all
catchable by a fixed-point pass, and the results are exact for the "unreachable"
verdict in the direction that matters -- if this pass says a storylet is
unreachable, it truly is, because every over-approximation is generous.

Reported findings are therefore sound, not complete: nothing here will falsely
accuse content of being unreachable, but genuinely unreachable content can still
slip past and be caught later by the simulator.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from s32_engine import conditions, effects
from s32_engine.types import PHASES, ContentLibrary, ContentSource, Weather
from s32_engine.world import TRANSITIONS, is_valid_weather
from s32tools.validation.content import Report


def _reachable_weather() -> set[Weather]:
    """Return every weather state the transition chain can actually reach."""
    reachable: set[Weather] = {"clear"}
    changed = True
    while changed:
        changed = False
        for source in list(reachable):
            for target, weight in (TRANSITIONS.get(source) or {}).items():
                if weight > 0 and target not in reachable:
                    reachable.add(target)
                    changed = True
    return reachable


_REL_REQ = re.compile(
    r"rel\s+(?:(?P<source>[a-z_][a-z0-9_]*)->)?(?P<target>[a-z_][a-z0-9_]*)"
    r"\.(?P<axis>[a-z_]+)\s*(?P<op>>=|>)\s*(?P<value>-?\d+)"
)
_REL_EFF = re.compile(
    r"rel\s+(?:(?P<source>[a-z_][a-z0-9_]*)->)?(?P<target>[a-z_][a-z0-9_]*)"
    r"\.(?P<axis>[a-z_]+)\s*(?P<op>\+=|=)\s*(?P<value>-?\d+)"
)
_TRAIT_REQ = re.compile(r"trait\s+(?P<axis>[a-z_]+)\s*(?:>=|>)\s*(?P<value>-?\d+)")
_TRAIT_EFF = re.compile(r"trait\s+(?P<axis>[a-z_]+)\s*(?:\+=|=)\s*(?P<value>-?\d+)")
_FLAG_REQ = re.compile(r"flag\s+(?P<name>[a-z_]+)\s*(?:>=|>)\s*(?P<value>-?\d+)")
_FLAG_EFF = re.compile(r"flag\s+(?P<name>[a-z_]+)\s*(?:\+=|=)\s*(?P<value>-?\d+)")
_PHASE_REQ = re.compile(r"phase\s*(?:>=|>|==)\s*(?P<value>[a-z_]+)")
_PHASE_EFF = re.compile(r"phase\s*=\s*(?P<value>[a-z_]+)")
_COMMITMENT_REQ = re.compile(r"commitment\(\s*(?P<cid>[a-z_]+)\s*\)\s*==\s*(?P<value>[a-z_]+)")
_COMMIT_EFF = re.compile(r"commit\(\s*(?P<cid>[a-z_]+)\s*,")
_WEATHER_REQ = re.compile(r"weather\s*==\s*(?P<value>[a-z_]+)")


@dataclass
class Ceiling:
    """The highest values any run could possibly reach.

    Every field grows monotonically as the fixed point is computed, so a value
    here is an upper bound: if a requirement asks for more than the ceiling, no
    run can satisfy it.
    """

    knowledge: set[str] = field(default_factory=set)
    items: set[str] = field(default_factory=set)
    anchors: set[str] = field(default_factory=set)
    storylets: set[str] = field(default_factory=set)
    commitments: set[str] = field(default_factory=set)
    relationships: dict[str, int] = field(default_factory=dict)
    traits: dict[str, int] = field(default_factory=dict)
    flags: dict[str, int] = field(default_factory=dict)
    phase_index: int = 0


def analyse(library: ContentLibrary) -> Report:
    """Run every static check and return the findings."""
    report = Report()
    ceiling = _compute_ceiling(library)
    _check_unsatisfiable(library, ceiling, report)
    _check_orphans(library, report)
    _check_self_contradiction(library, report)
    return report


def _compute_ceiling(library: ContentLibrary) -> Ceiling:
    """Compute the fixed point of everything the content can grant.

    Iterates until nothing new is added. Each pass admits any storylet whose
    *knowledge, item, anchor, storylet and commitment* prerequisites are already
    in the ceiling, then folds in everything it grants. Numeric requirements are
    intentionally ignored when admitting, because a threshold that is currently
    out of reach may become reachable once another storylet is admitted; being
    generous here is what keeps the analysis sound.
    """
    ceiling = Ceiling()
    for item in library.items.values():
        ceiling.items.add(item.id)
        ceiling.knowledge.update(item.grants)

    sources: list[ContentSource] = [*library.storylets.values(), *library.anchors.values()]
    changed = True
    while changed:
        changed = False
        for source in sources:
            if source.id in ceiling.storylets or source.id in ceiling.anchors:
                continue
            if not _prerequisites_met(source.requirements, ceiling):
                continue

            if source.id in library.anchors:
                ceiling.anchors.add(source.id)
            else:
                ceiling.storylets.add(source.id)
            changed = True
            _absorb(source.effects, ceiling)
            # Every choice a scene offers is a path a player can take, so the
            # ceiling includes all of them.
            for branch in getattr(source, "outcomes", ()):
                _absorb(branch, ceiling)
            ceiling.knowledge.update(source.grants)

    _tighten_relationship_ceiling(library, ceiling)
    return ceiling


def _tighten_relationship_ceiling(library: ContentLibrary, ceiling: Ceiling) -> None:
    """Replace the generous per-axis ceiling with the best achievable total.

    ``_absorb`` assumes a positive ``+=`` can reach the axis maximum, which is
    true for repeatable content and badly wrong for content that plays once. A
    play-once storylet contributes at most its own delta, and a scene's mutually
    exclusive choices contribute at most the best of them.

    Getting this right is what turns "the simulator noticed nothing reached
    trust 12" into "no possible run can exceed trust 10", which is a far more
    useful thing to tell a writer, and is available without simulating.
    """
    totals: dict[str, int] = {}
    repeatable: set[str] = set()

    sources: list[ContentSource] = [*library.storylets.values(), *library.anchors.values()]
    for source in sources:
        once = getattr(source, "repeat_policy", "once") == "once"

        # Unconditional effects always apply; choice outcomes are exclusive, so
        # only the most generous branch counts toward the ceiling.
        base = _axis_deltas(source.effects)
        best_branch: dict[str, int] = {}
        for branch in getattr(source, "outcomes", ()):
            for key, value in _axis_deltas(branch).items():
                best_branch[key] = max(best_branch.get(key, 0), value)

        for key in set(base) | set(best_branch):
            gain = base.get(key, 0) + best_branch.get(key, 0)
            if gain <= 0:
                continue
            if once:
                totals[key] = totals.get(key, 0) + gain
            else:
                repeatable.add(key)

    for key in ceiling.relationships:
        if key in repeatable:
            ceiling.relationships[key] = 100
        else:
            ceiling.relationships[key] = min(100, totals.get(key, 0))


def _axis_deltas(effect_list: tuple[str, ...]) -> dict[str, int]:
    """Return the positive relationship movement one effect list produces."""
    deltas: dict[str, int] = {}
    for effect in effect_list:
        match = _REL_EFF.fullmatch(effect.strip())
        if match is None:
            continue
        key = f"{match.group('source') or 'player'}->{match.group('target')}.{match.group('axis')}"
        value = int(match.group("value"))
        if match.group("op") == "=":
            deltas[key] = max(deltas.get(key, 0), value)
        elif value > 0:
            deltas[key] = deltas.get(key, 0) + value
    return deltas


def _prerequisites_met(requirements: tuple[str, ...], ceiling: Ceiling) -> bool:
    """Return whether the symbolic (non-numeric) prerequisites are reachable."""
    for req in requirements:
        text = req.strip()
        if text.startswith("not "):
            # A negated requirement can always be satisfied at some point in a
            # run (before the thing happens), so it never blocks admission.
            continue
        refs = conditions.referenced_ids(text)
        if not refs.get("knowledge", set()) <= ceiling.knowledge:
            return False
        if not refs.get("item", set()) <= ceiling.items:
            return False
        if not refs.get("anchor", set()) <= ceiling.anchors:
            return False
        if text.startswith("seen(") and not refs.get("storylet", set()) <= ceiling.storylets:
            return False
        match = _COMMITMENT_REQ.fullmatch(text)
        if match and match.group("cid") not in ceiling.commitments:
            return False
    return True


def _absorb(effect_list: tuple[str, ...], ceiling: Ceiling) -> None:
    """Fold a set of effects into the ceiling."""
    ceiling.knowledge.update(effects.granted_knowledge(effect_list))
    for effect in effect_list:
        text = effect.strip()

        refs = effects.referenced_ids(text)
        ceiling.items.update(refs.get("item", set()))
        ceiling.anchors.update(refs.get("anchor", set()))

        if match := _REL_EFF.fullmatch(text):
            actor = match.group("source") or "player"
            key = f"{actor}->{match.group('target')}.{match.group('axis')}"
            value = int(match.group("value"))
            if match.group("op") == "+=":
                # Repeatable content could apply this many times, so a positive
                # delta implies the axis maximum is reachable.
                ceiling.relationships[key] = 100 if value > 0 else ceiling.relationships.get(key, 0)
            else:
                ceiling.relationships[key] = max(ceiling.relationships.get(key, 0), value)
        if match := _TRAIT_EFF.fullmatch(text):
            ceiling.traits[match.group("axis")] = 100
        if match := _FLAG_EFF.fullmatch(text):
            ceiling.flags[match.group("name")] = 10**6
        if match := _PHASE_EFF.fullmatch(text):
            phase_name = match.group("value")
            if phase_name in PHASES:
                ceiling.phase_index = max(ceiling.phase_index, PHASES.index(phase_name))
        if match := _COMMIT_EFF.match(text):
            ceiling.commitments.add(match.group("cid"))


def _check_unsatisfiable(  # noqa: PLR0912 - one branch per requirement form, which is the check
    library: ContentLibrary, ceiling: Ceiling, report: Report
) -> None:
    """Report requirements no run could ever meet."""
    sources: list[ContentSource] = [*library.storylets.values(), *library.anchors.values()]
    for source in sources:
        kind = "storylet" if source.id in library.storylets else "anchor"
        where = f"{kind} {source.id}"
        admitted = source.id in ceiling.storylets or source.id in ceiling.anchors

        for req in source.requirements:
            text = req.strip()
            if text.startswith("not "):
                continue

            if match := _REL_REQ.fullmatch(text):
                key = (
                    f"{match.group('source') or 'player'}->{match.group('target')}"
                    f".{match.group('axis')}"
                )
                needed = int(match.group("value"))
                if ceiling.relationships.get(key, 0) < needed:
                    report.add(
                        "error",
                        "unsatisfiable-relationship",
                        where,
                        f"requires {text!r}, but no content raises {key} above "
                        f"{ceiling.relationships.get(key, 0)}",
                        hint="add an effect that moves this axis, or lower the threshold",
                    )

            if match := _TRAIT_REQ.fullmatch(text):
                axis = match.group("axis")
                if ceiling.traits.get(axis, 0) < int(match.group("value")):
                    report.add(
                        "error",
                        "unsatisfiable-trait",
                        where,
                        f"requires {text!r}, but no content increases trait {axis!r}",
                    )

            if match := _FLAG_REQ.fullmatch(text):
                name = match.group("name")
                if ceiling.flags.get(name, 0) < int(match.group("value")):
                    report.add(
                        "error",
                        "unsatisfiable-flag",
                        where,
                        f"requires {text!r}, but no content sets flag {name!r}",
                    )

            if match := _PHASE_REQ.fullmatch(text):
                phase_name = match.group("value")
                if phase_name in PHASES and PHASES.index(phase_name) > ceiling.phase_index:
                    report.add(
                        "error",
                        "unsatisfiable-phase",
                        where,
                        f"requires phase {phase_name!r}, but nothing advances past "
                        f"{PHASES[ceiling.phase_index]!r}",
                    )

            if match := _COMMITMENT_REQ.fullmatch(text):
                cid = match.group("cid")
                if cid not in ceiling.commitments:
                    report.add(
                        "error",
                        "unsatisfiable-commitment",
                        where,
                        f"requires commitment {cid!r}, which no content creates",
                    )

            # Weather is not authored by content -- it comes from the world
            # model -- so the check is that the value exists at all and that the
            # model can actually produce it. A scene gated on weather the chain
            # never reaches is unreachable in exactly the same way as one gated
            # on a fact nobody grants.
            if match := _WEATHER_REQ.fullmatch(text):
                value = match.group("value")
                if not is_valid_weather(value):
                    report.add(
                        "error",
                        "unknown-weather",
                        where,
                        f"requires weather {value!r}, which is not a weather state",
                    )
                elif value not in _reachable_weather():
                    report.add(
                        "error",
                        "unreachable-weather",
                        where,
                        f"requires weather {value!r}, which the weather model never produces",
                        hint="add it to s32_engine.world.TRANSITIONS",
                    )

        if not admitted:
            report.add(
                "error",
                "statically-unreachable",
                where,
                "prerequisites can never all be satisfied",
                hint="check the requirement chain; the simulator will confirm",
            )


def _check_orphans(library: ContentLibrary, report: Report) -> None:
    """Report content nothing points at and that gates nothing."""
    referenced: set[str] = set()
    for storylet in library.storylets.values():
        for expr in (*storylet.requirements, *storylet.blockers):
            referenced.update(conditions.referenced_ids(expr).get("storylet", set()))
    for anchor in library.anchors.values():
        for expr in anchor.requirements:
            referenced.update(conditions.referenced_ids(expr).get("storylet", set()))

    for storylet in library.storylets.values():
        if storylet.status != "active":
            continue
        gates_nothing = storylet.id not in referenced
        grants_nothing = not storylet.grants and not storylet.effects
        if gates_nothing and grants_nothing:
            report.add(
                "warning",
                "inert-storylet",
                f"storylet {storylet.id}",
                "has no effects and is not required by anything",
                hint="pure flavour is fine; confirm that is the intent",
            )


def _check_self_contradiction(library: ContentLibrary, report: Report) -> None:
    """Report storylets whose own clauses cannot hold simultaneously."""
    for storylet in library.storylets.values():
        where = f"storylet {storylet.id}"
        overlap = set(storylet.requirements) & set(storylet.blockers)
        if overlap:
            report.add(
                "error",
                "requirement-blocker-clash",
                where,
                f"the same condition is both required and blocking: {', '.join(sorted(overlap))}",
            )

        if storylet.location:
            for req in storylet.requirements:
                match = re.fullmatch(r"location\s*==\s*([a-z_]+)", req.strip())
                if match and match.group(1) != storylet.location:
                    report.add(
                        "error",
                        "location-clash",
                        where,
                        f"location field says {storylet.location!r} but a requirement "
                        f"demands {match.group(1)!r}",
                    )

        if storylet.time_slots:
            for req in storylet.requirements:
                match = re.fullmatch(r"time_slot\s*==\s*([a-z_]+)", req.strip())
                if match and match.group(1) not in storylet.time_slots:
                    report.add(
                        "error",
                        "time-slot-clash",
                        where,
                        f"time_slots {storylet.time_slots} exclude required {match.group(1)!r}",
                    )
