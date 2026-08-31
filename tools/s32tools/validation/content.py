"""Content validation beyond what JSON Schema can express.

JSON Schema checks shape. It cannot check that ``knows(old_letter)`` refers to a
fact that exists, that some storylet actually grants it, that a ``label`` has a
matching definition in the ``.rpy`` sources, or that a cooldown on a
``repeat_policy: once`` storylet is dead configuration.

Findings are graded:

``error``
    Would break the game or is provably unreachable content. Fails CI.
``warning``
    Almost certainly a mistake, but the game still runs. Fails CI only under
    ``--strict``.
``info``
    Worth a writer's attention; never fails CI.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any, Literal

from s32_engine import conditions, effects
from s32_engine.errors import ContentError
from s32_engine.types import (
    RELATIONSHIP_AXES,
    TRAIT_AXES,
    AnchorDef,
    ContentLibrary,
    ContentSource,
    StoryletDef,
)

Severity = Literal["error", "warning", "info"]

#: The priority values a storylet is expected to use.
#:
#: A content convention, not an engine rule -- the director will happily sort
#: any integer. It exists because priority is a *hard tier*, so a value nothing
#: else shares removes that storylet from the weighted draw entirely. Five bands
#: keep scenes competing; a hundred distinct levels are a total ranking of the
#: library, which nobody can maintain and which no draw can act on.
#: docs/narrative-design/PRIORITY_AUTHORING.md
PRIORITY_BANDS: frozenset[int] = frozenset({100, 80, 60, 40, 20})

#: Matches a Ren'Py `label foo:` definition, ignoring indented (nested) labels.
_LABEL_RE = re.compile(r"^label\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(.*?\))?\s*:", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class Finding:
    """One validation result."""

    severity: Severity
    code: str
    where: str
    message: str
    hint: str = ""

    def format(self) -> str:
        """Return a one- or two-line human rendering."""
        head = f"{self.severity.upper():7} {self.code:24} {self.where}: {self.message}"
        return f"{head}\n{'':32}hint: {self.hint}" if self.hint else head


class Report:
    """A collection of findings with convenience accessors."""

    def __init__(self, findings: Iterable[Finding] = ()) -> None:
        self.findings: list[Finding] = list(findings)

    def add(self, severity: Severity, code: str, where: str, message: str, hint: str = "") -> None:
        """Append one finding."""
        self.findings.append(Finding(severity, code, where, message, hint))

    def by_severity(self, severity: Severity) -> list[Finding]:
        """Return findings of one severity."""
        return [f for f in self.findings if f.severity == severity]

    @property
    def errors(self) -> list[Finding]:
        """Findings that must be fixed."""
        return self.by_severity("error")

    @property
    def warnings(self) -> list[Finding]:
        """Findings that are probably bugs."""
        return self.by_severity("warning")

    def ok(self, *, strict: bool = False) -> bool:
        """Return whether the content passes."""
        return not self.errors and (not strict or not self.warnings)

    def format(self) -> str:
        """Return the full report text, errors first."""
        if not self.findings:
            return "content OK: no findings"
        order: dict[Severity, int] = {"error": 0, "warning": 1, "info": 2}
        ordered = sorted(self.findings, key=lambda f: (order[f.severity], f.code, f.where))
        lines = [f.format() for f in ordered]
        lines.append(
            f"\n{len(self.errors)} error(s), {len(self.warnings)} warning(s), "
            f"{len(self.by_severity('info'))} info"
        )
        return "\n".join(lines)


def validate_library(library: ContentLibrary, *, rpy_root: Path | None = None) -> Report:
    """Run every cross-reference and reachability check over a loaded library."""
    report = Report()
    _check_expressions(library, report)
    _check_references(library, report)
    _check_policies(library, report)
    _check_knowledge_graph(library, report)
    _check_anchors(library, report)
    if rpy_root is not None:
        _check_labels(library, rpy_root, report)
    return report


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def _iter_conditions(library: ContentLibrary) -> Iterator[tuple[str, str, str]]:
    """Yield ``(where, kind, expression)`` for every condition in the library."""
    for storylet in library.storylets.values():
        for expr in storylet.requirements:
            yield f"storylet {storylet.id}", "requirement", expr
        for expr in storylet.blockers:
            yield f"storylet {storylet.id}", "blocker", expr
    for anchor in library.anchors.values():
        for expr in anchor.requirements:
            yield f"anchor {anchor.id}", "requirement", expr


def _iter_effects(library: ContentLibrary) -> Iterator[tuple[str, str]]:
    """Yield ``(where, effect)`` for every effect in the library.

    Includes per-choice outcomes: those are effects like any other, and a typo
    in one would otherwise reach a player.
    """
    for storylet in library.storylets.values():
        for expr in storylet.effects:
            yield f"storylet {storylet.id}", expr
        for index, branch in enumerate(storylet.outcomes):
            for expr in branch:
                yield f"storylet {storylet.id} outcome[{index}]", expr
    for anchor in library.anchors.values():
        for expr in anchor.effects:
            yield f"anchor {anchor.id}", expr
        for index, branch in enumerate(anchor.outcomes):
            for expr in branch:
                yield f"anchor {anchor.id} outcome[{index}]", expr


def _check_expressions(library: ContentLibrary, report: Report) -> None:
    """Every condition and effect must parse against the engine's grammar."""
    from s32_engine.rng import Rng
    from s32_engine.state import new_state

    probe = new_state(library)
    ctx = conditions.ConditionContext(probe, Rng(probe))

    for where, kind, expr in _iter_conditions(library):
        try:
            conditions.evaluate(expr, ctx)
        except ContentError as exc:
            report.add("error", "bad-condition", where, f"{kind} {expr!r}: {exc}")

    for where, expr in _iter_effects(library):
        # Effects are parsed, not applied: applying them here would mutate the
        # probe state and make later checks depend on file iteration order.
        if not _effect_parses(expr):
            report.add("error", "bad-effect", where, f"effect {expr!r} does not parse")


def _effect_parses(expr: str) -> bool:
    """Return whether an effect string matches any known form."""
    text = expr.strip()
    return any(pattern.fullmatch(text) for pattern, _ in effects._HANDLERS)


def _check_references(library: ContentLibrary, report: Report) -> None:
    """Every id named by a condition or effect must exist."""
    known: dict[str, set[str]] = {
        "character": set(library.characters) | {"player"},
        "knowledge": set(library.knowledge),
        "item": set(library.items),
        "storylet": set(library.storylets),
        "anchor": set(library.anchors),
        "location": set(library.locations),
        "rel_axis": set(RELATIONSHIP_AXES),
        "trait_axis": set(TRAIT_AXES),
    }

    def check(where: str, refs: dict[str, set[str]], context: str) -> None:
        for kind, values in refs.items():
            universe = known.get(kind)
            if universe is None:
                continue
            for value in sorted(values - universe):
                report.add(
                    "error",
                    f"unknown-{kind}",
                    where,
                    f"{context} refers to {kind} {value!r}, which is not defined",
                    hint=f"define it under data/{kind}s/ or fix the reference",
                )

    for where, kind, expr in _iter_conditions(library):
        check(where, conditions.referenced_ids(expr), f"{kind} {expr!r}")
    for where, expr in _iter_effects(library):
        check(where, effects.referenced_ids(expr), f"effect {expr!r}")

    for storylet in library.storylets.values():
        where = f"storylet {storylet.id}"
        for char_id in storylet.characters:
            if char_id not in library.characters:
                report.add("error", "unknown-character", where, f"characters lists {char_id!r}")
        if storylet.location and storylet.location not in library.locations:
            report.add("error", "unknown-location", where, f"location {storylet.location!r}")
        if storylet.anchor and storylet.anchor not in library.anchors:
            report.add("error", "unknown-anchor", where, f"anchor {storylet.anchor!r}")

    for item in library.items.values():
        for fact in item.grants:
            if fact not in library.knowledge:
                report.add("error", "unknown-knowledge", f"item {item.id}", f"grants {fact!r}")

    for char in library.characters.values():
        if char.asset_id is None:
            report.add(
                "info",
                "art-gap",
                f"character {char.id}",
                "no asset_id: this character has no sprite yet",
                hint="tracked in docs/production/ART_GAP_ANALYSIS.md",
            )


def _check_policies(library: ContentLibrary, report: Report) -> None:
    """Catch configurations that are legal but cannot do what they look like."""
    for s in library.storylets.values():
        where = f"storylet {s.id}"
        if s.cooldown and s.repeat_policy == "once":
            report.add(
                "warning",
                "dead-cooldown",
                where,
                f"cooldown={s.cooldown} has no effect with repeat_policy=once",
                hint="set repeat_policy to 'cooldown', or drop the cooldown",
            )
        if s.repeat_policy == "cooldown" and not s.cooldown:
            report.add(
                "warning",
                "missing-cooldown",
                where,
                "repeat_policy=cooldown with cooldown=0 repeats immediately",
            )
        if s.weight <= 0:
            report.add("error", "bad-weight", where, f"weight must be positive, got {s.weight}")
        if s.status == "active" and not s.summary:
            report.add("warning", "no-summary", where, "active storylet has no summary")
        if s.category == "anchor" and not s.anchor:
            report.add("warning", "anchor-unlinked", where, "category=anchor but no anchor id set")

        # Priority is a hard tier: a value nothing else shares guarantees a
        # tier of one, and a tier of one makes the weighted draw a formality.
        # The bands are a content convention rather than an engine rule, so
        # this is informational -- a deliberate exception is allowed, it just
        # has to be deliberate enough to notice.
        # docs/narrative-design/PRIORITY_AUTHORING.md
        if s.priority not in PRIORITY_BANDS:
            report.add(
                "info",
                "off-band-priority",
                where,
                f"priority={s.priority} is not one of {sorted(PRIORITY_BANDS)}",
                hint="see docs/narrative-design/PRIORITY_AUTHORING.md",
            )

        # A `not_seen(self)` requirement duplicates repeat_policy=once. Harmless,
        # but it hides the real policy from the coverage report, so flag it.
        if f"not_seen({s.id})" in s.requirements and s.repeat_policy == "once":
            report.add(
                "info",
                "redundant-not-seen",
                where,
                "not_seen(self) is redundant with repeat_policy=once",
            )


def _check_knowledge_graph(  # noqa: PLR0912 - one branch per way a fact can be used or missed
    library: ContentLibrary, report: Report
) -> None:
    """Find facts nothing grants, and facts nothing consumes."""
    granted: dict[str, list[str]] = {}
    sources: list[ContentSource] = [*library.storylets.values(), *library.anchors.values()]
    for source in sources:
        for fact in source.grants:
            granted.setdefault(fact, []).append(source.id)
    for item in library.items.values():
        for fact in item.grants:
            granted.setdefault(fact, []).append(f"item:{item.id}")

    required: dict[str, list[str]] = {}
    for where, _kind, expr in _iter_conditions(library):
        for fact in conditions.referenced_ids(expr).get("knowledge", set()):
            required.setdefault(fact, []).append(where)

    # Facts an effect gives to an NPC rather than the player still count as
    # used. They cannot satisfy a player-facing `knows()`, so they are not
    # `granted`, but reporting them as orphans would be wrong: a character
    # believing something is a legitimate purpose for a fact to exist.
    npc_used: set[str] = set()
    for _where, expr in _iter_effects(library):
        npc_used.update(effects.referenced_ids(expr).get("knowledge", set()))

    for fact, wheres in sorted(required.items()):
        if fact in library.knowledge and fact not in granted:
            report.add(
                "error",
                "ungranted-knowledge",
                wheres[0],
                f"requires knowledge {fact!r}, which no storylet, anchor or item grants",
                hint="add a `know(...)` effect somewhere, or remove the requirement",
            )

    for fact in sorted(library.knowledge):
        if fact not in granted and fact not in required and fact not in npc_used:
            report.add(
                "info",
                "orphan-knowledge",
                f"knowledge {fact}",
                "defined but neither granted nor required by any content",
            )

    for fact_def in library.knowledge.values():
        for other in fact_def.contradicts:
            if other not in library.knowledge:
                continue
            if fact_def.id not in library.knowledge[other].contradicts:
                report.add(
                    "warning",
                    "asymmetric-contradiction",
                    f"knowledge {fact_def.id}",
                    f"contradicts {other!r}, but {other!r} does not contradict it back",
                    hint="contradiction is mutual; list it on both facts",
                )


def _check_anchors(library: ContentLibrary, report: Report) -> None:
    """Anchors must be strictly ordered and each reachable from the last."""
    ordered: list[AnchorDef] = sorted(library.anchors.values(), key=lambda a: (a.order, a.id))
    seen_orders: dict[int, str] = {}
    for anchor in ordered:
        if anchor.order in seen_orders:
            report.add(
                "error",
                "duplicate-anchor-order",
                f"anchor {anchor.id}",
                f"order {anchor.order} already used by {seen_orders[anchor.order]!r}",
            )
        seen_orders[anchor.order] = anchor.id

    for previous, current in pairwise(ordered):
        needs_previous = f"anchor_done({previous.id})" in current.requirements
        if not needs_previous:
            report.add(
                "info",
                "anchor-not-chained",
                f"anchor {current.id}",
                f"does not require anchor_done({previous.id})",
                hint="anchors are ordered; chaining them makes the order enforceable",
            )


def _check_labels(library: ContentLibrary, rpy_root: Path, report: Report) -> None:
    """Every storylet and anchor must point at a label that actually exists."""
    defined: dict[str, Path] = {}
    for path in sorted(rpy_root.rglob("*.rpy")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in _LABEL_RE.finditer(text):
            defined.setdefault(match.group(1), path)

    sources: list[StoryletDef | AnchorDef] = [
        *library.storylets.values(),
        *library.anchors.values(),
    ]
    for source in sources:
        kind = "storylet" if isinstance(source, StoryletDef) else "anchor"
        if source.label not in defined:
            report.add(
                "error",
                "missing-label",
                f"{kind} {source.id}",
                f"label {source.label!r} is not defined in any .rpy file",
                hint=f"add `label {source.label}:` under game/story/",
            )

    referenced = {s.label for s in sources}
    for label, path in sorted(defined.items()):
        if label.startswith(("s32_st_", "s32_anchor_")) and label not in referenced:
            report.add(
                "warning",
                "orphan-label",
                str(path.name),
                f"label {label!r} looks like content but no storylet or anchor points at it",
            )


def schema_validate(data_root: Path, schemas_root: Path) -> Report:
    """Validate every content file against its generated JSON Schema."""
    import json

    import jsonschema

    from s32tools.validation.schemas import DIRECTORY_SCHEMAS

    report = Report()
    for subdir, schema_name in sorted(DIRECTORY_SCHEMAS.items()):
        schema_path = schemas_root / schema_name
        if not schema_path.exists():
            report.add("error", "missing-schema", schema_name, "run `s32 schemas` to generate it")
            continue
        schema: dict[str, Any] = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)

        for path in sorted((data_root / subdir).rglob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                report.add("error", "bad-json", str(path.name), str(exc))
                continue
            for error in sorted(validator.iter_errors(payload), key=str):
                location = "/".join(str(p) for p in error.absolute_path) or "<root>"
                report.add(
                    "error", "schema", f"{subdir}/{path.name}", f"{location}: {error.message}"
                )

            if payload.get("id") != path.stem:
                report.add(
                    "warning",
                    "id-filename-mismatch",
                    f"{subdir}/{path.name}",
                    f"id {payload.get('id')!r} does not match the filename",
                    hint="one entity per file, named after its id, keeps diffs readable",
                )
    return report
