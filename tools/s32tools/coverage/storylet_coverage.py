"""Coverage reporting over the authored content.

Two different questions get answered here, and keeping them apart matters:

*Authoring coverage* — how much content exists, in what state, using which parts
of the condition language. Purely static; no simulation needed.

*Exercise coverage* — which storylets a simulation actually reached. Needs a
simulation result to be passed in.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from s32_engine import conditions, effects
from s32_engine.types import CONTENT_STATUSES, ContentLibrary
from s32tools.simulation.simulator import SimulationResult


@dataclass(slots=True)
class Coverage:
    """Aggregated coverage numbers."""

    total: int = 0
    by_status: dict[str, int] = field(default_factory=dict)
    by_category: dict[str, int] = field(default_factory=dict)
    by_tag: dict[str, int] = field(default_factory=dict)
    with_requirements: int = 0
    with_blockers: int = 0
    with_effects: int = 0
    condition_forms: dict[str, int] = field(default_factory=dict)
    effect_forms: dict[str, int] = field(default_factory=dict)
    knowledge_granted: set[str] = field(default_factory=set)
    knowledge_required: set[str] = field(default_factory=set)
    characters_used: set[str] = field(default_factory=set)
    locations_used: set[str] = field(default_factory=set)
    untested: set[str] = field(default_factory=set)
    unreachable: set[str] = field(default_factory=set)


def _form_of(expression: str) -> str:
    """Reduce an expression to its grammatical form, for a histogram.

    ``rel iris.trust >= 30`` and ``rel theo.trust >= 5`` are the same form. What
    the histogram is for is spotting parts of the language nobody uses -- an
    unused form is either a design idea that never landed or a feature to delete.
    """
    text = expression.strip().removeprefix("not ").strip()
    head = text.split("(")[0].split()[0] if text else "?"
    if "(" in text and text.index("(") < len(head) + 1:
        return f"{head}()"
    return head


def analyse(library: ContentLibrary, simulation: SimulationResult | None = None) -> Coverage:
    """Compute coverage over a library, optionally folding in a simulation."""
    coverage = Coverage(total=len(library.storylets))
    status_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()
    tag_counter: Counter[str] = Counter()
    condition_counter: Counter[str] = Counter()
    effect_counter: Counter[str] = Counter()

    for storylet in library.storylets.values():
        status_counter[storylet.status] += 1
        category_counter[storylet.category] += 1
        tag_counter.update(storylet.tags)
        coverage.characters_used.update(storylet.characters)
        if storylet.location:
            coverage.locations_used.add(storylet.location)
        if storylet.requirements:
            coverage.with_requirements += 1
        if storylet.blockers:
            coverage.with_blockers += 1
        if storylet.effects:
            coverage.with_effects += 1

        for expr in (*storylet.requirements, *storylet.blockers):
            condition_counter[_form_of(expr)] += 1
            coverage.knowledge_required.update(
                conditions.referenced_ids(expr).get("knowledge", set())
            )
        for expr in storylet.effects:
            effect_counter[_form_of(expr)] += 1
        coverage.knowledge_granted.update(effects.granted_knowledge(storylet.effects))
        coverage.knowledge_granted.update(storylet.grants)

    for status in CONTENT_STATUSES:
        status_counter.setdefault(status, 0)

    coverage.by_status = dict(sorted(status_counter.items()))
    coverage.by_category = dict(sorted(category_counter.items()))
    coverage.by_tag = dict(sorted(tag_counter.items()))
    coverage.condition_forms = dict(sorted(condition_counter.items()))
    coverage.effect_forms = dict(sorted(effect_counter.items()))

    if simulation is not None:
        coverage.unreachable = set(simulation.unreachable)
        coverage.untested = set(library.storylets) - set(simulation.reachable)
    else:
        coverage.untested = set(library.storylets)

    return coverage


def to_dict(coverage: Coverage, library: ContentLibrary) -> dict[str, Any]:
    """Return the machine-readable coverage payload."""
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "totals": {
            "storylets": coverage.total,
            "anchors": len(library.anchors),
            "characters": len(library.characters),
            "locations": len(library.locations),
            "knowledge": len(library.knowledge),
            "items": len(library.items),
        },
        "by_status": coverage.by_status,
        "by_category": coverage.by_category,
        "by_tag": coverage.by_tag,
        "requirements_coverage": {
            "with_requirements": coverage.with_requirements,
            "with_blockers": coverage.with_blockers,
            "with_effects": coverage.with_effects,
            "condition_forms": coverage.condition_forms,
            "effect_forms": coverage.effect_forms,
        },
        "knowledge_coverage": {
            "defined": len(library.knowledge),
            "granted_by_content": sorted(coverage.knowledge_granted),
            "required_by_content": sorted(coverage.knowledge_required),
            "defined_but_unused": sorted(
                set(library.knowledge) - coverage.knowledge_granted - coverage.knowledge_required
            ),
        },
        "cast_coverage": {
            "characters_in_content": sorted(coverage.characters_used),
            "characters_without_content": sorted(
                set(library.characters) - coverage.characters_used
            ),
            "locations_in_content": sorted(coverage.locations_used),
            "locations_without_content": sorted(set(library.locations) - coverage.locations_used),
        },
        "exercise": {
            "unreachable": sorted(coverage.unreachable),
            "untested": sorted(coverage.untested),
        },
    }


def to_markdown(coverage: Coverage, library: ContentLibrary) -> str:
    """Return the human-readable coverage report."""
    payload = to_dict(coverage, library)
    active = coverage.by_status.get("active", 0)
    prototype = coverage.by_status.get("prototype", 0)

    lines = [
        "# Storylet coverage",
        "",
        "> Generated by `s32 coverage`. Do not edit; re-run the command.",
        "",
        f"- Generated: `{payload['generated_at']}`",
        "",
        "## Totals",
        "",
        "| | |",
        "| --- | ---: |",
        f"| TOTAL storylets | {coverage.total} |",
        f"| ACTIVE | {active} |",
        f"| PROTOTYPE | {prototype} |",
        f"| DRAFT | {coverage.by_status.get('draft', 0)} |",
        f"| RETIRED | {coverage.by_status.get('retired', 0)} |",
        f"| UNREACHABLE | {len(coverage.unreachable)} |",
        f"| UNTESTED | {len(coverage.untested)} |",
        f"| Anchors | {len(library.anchors)} |",
        f"| Characters | {len(library.characters)} |",
        f"| Locations | {len(library.locations)} |",
        f"| Knowledge facts | {len(library.knowledge)} |",
        f"| Items | {len(library.items)} |",
        "",
        "## By category",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]
    lines += [f"| {k} | {v} |" for k, v in coverage.by_category.items()]

    lines += ["", "## By tag", "", "| Tag | Storylets |", "| --- | ---: |"]
    lines += [f"| {k} | {v} |" for k, v in coverage.by_tag.items()]

    lines += [
        "",
        "## Condition and effect coverage",
        "",
        f"- Storylets with requirements: **{coverage.with_requirements}/{coverage.total}**",
        f"- Storylets with blockers: **{coverage.with_blockers}/{coverage.total}**",
        f"- Storylets with effects: **{coverage.with_effects}/{coverage.total}**",
        "",
        "| Condition form | Uses |",
        "| --- | ---: |",
    ]
    lines += [f"| `{k}` | {v} |" for k, v in coverage.condition_forms.items()]
    lines += ["", "| Effect form | Uses |", "| --- | ---: |"]
    lines += [f"| `{k}` | {v} |" for k, v in coverage.effect_forms.items()]

    unused_knowledge = payload["knowledge_coverage"]["defined_but_unused"]
    no_content = payload["cast_coverage"]["characters_without_content"]
    empty_locations = payload["cast_coverage"]["locations_without_content"]

    lines += ["", "## Gaps", ""]
    gaps = []
    if unused_knowledge:
        gaps.append(
            f"- Knowledge defined but unused: {', '.join(f'`{k}`' for k in unused_knowledge)}"
        )
    if no_content:
        gaps.append(f"- Characters with no storylet: {', '.join(f'`{c}`' for c in no_content)}")
    if empty_locations:
        gaps.append(
            f"- Locations with no storylet: {', '.join(f'`{loc}`' for loc in empty_locations)}"
        )
    if coverage.unreachable:
        gaps.append(f"- Unreachable: {', '.join(f'`{s}`' for s in sorted(coverage.unreachable))}")
    lines += gaps or ["No gaps."]
    lines.append("")

    return "\n".join(lines)


def to_json(coverage: Coverage, library: ContentLibrary) -> str:
    """Return the JSON coverage report text."""
    return json.dumps(to_dict(coverage, library), indent=2, ensure_ascii=False) + "\n"
