"""Narrative graph exporters.

The graph is a *development* artefact. The player never sees a flowchart -- that
would give away the shape of the mystery -- but a writer holding forty storylets
in their head needs to see how information flows through them.

Two edge kinds are drawn:

* **grant** — a storylet's effects give the player a fact.
* **gate** — a storylet requires a fact, an anchor, or another storylet.

Mermaid is the default because it renders in the repository's Markdown without
any tool installed. Graphviz DOT is offered for when the graph outgrows that,
but nothing in the pipeline requires ``dot`` to be present.
"""

from __future__ import annotations

from datetime import UTC, datetime
from itertools import pairwise

from s32_engine import conditions
from s32_engine.types import ContentLibrary


#: Mermaid needs identifiers without punctuation it treats as syntax.
def _node(prefix: str, name: str) -> str:
    """Return a Mermaid-safe node id."""
    return f"{prefix}_{name}".replace("-", "_")


def _collect_edges(  # noqa: PLR0912 - one branch per edge kind; flattening it hides the graph
    library: ContentLibrary,
) -> tuple[list[tuple[str, str, str]], set[str]]:
    """Return ``(edges, referenced_facts)``.

    Each edge is ``(source_node, target_node, kind)``.
    """
    edges: list[tuple[str, str, str]] = []
    facts: set[str] = set()

    for storylet in library.storylets.values():
        node = _node("S", storylet.id)
        for fact in storylet.grants:
            facts.add(fact)
            edges.append((node, _node("K", fact), "grant"))
        for expr in storylet.requirements:
            refs = conditions.referenced_ids(expr)
            for fact in refs.get("knowledge", set()):
                facts.add(fact)
                edges.append((_node("K", fact), node, "gate"))
            for other in refs.get("storylet", set()):
                if other != storylet.id and other in library.storylets:
                    edges.append((_node("S", other), node, "gate"))
            for anchor in refs.get("anchor", set()):
                edges.append((_node("A", anchor), node, "gate"))

    for anchor_def in library.anchors.values():
        node = _node("A", anchor_def.id)
        for fact in anchor_def.grants:
            facts.add(fact)
            edges.append((node, _node("K", fact), "grant"))
        for expr in anchor_def.requirements:
            refs = conditions.referenced_ids(expr)
            for fact in refs.get("knowledge", set()):
                facts.add(fact)
                edges.append((_node("K", fact), node, "gate"))
            for other in refs.get("anchor", set()):
                edges.append((_node("A", other), node, "gate"))

    for item in library.items.values():
        for fact in item.grants:
            facts.add(fact)
            edges.append((_node("I", item.id), _node("K", fact), "grant"))

    # Stable ordering: the exported file should only change when the content
    # changes, so it can be diffed and committed.
    return sorted(set(edges)), facts


def to_mermaid(library: ContentLibrary) -> str:
    """Return a Mermaid flowchart of the information graph."""
    edges, facts = _collect_edges(library)
    lines = ["flowchart LR"]

    ordered = sorted(library.anchors.values(), key=lambda a: (a.order, a.id))
    if ordered:
        lines.append("  subgraph anchors[Anchors]")
        lines.append("    direction TB")
        for anchor in ordered:
            lines.append(f'    {_node("A", anchor.id)}["{anchor.order}. {anchor.title}"]')
        for previous, current in pairwise(ordered):
            lines.append(f"    {_node('A', previous.id)} --> {_node('A', current.id)}")
        lines.append("  end")

    if facts:
        lines.append("  subgraph knowledge[Knowledge]")
        for fact in sorted(facts):
            lines.append(f'    {_node("K", fact)}(("{fact}"))')
        lines.append("  end")

    lines.append("  subgraph storylets[Storylets]")
    for storylet in sorted(library.storylets.values(), key=lambda s: s.id):
        lines.append(f'    {_node("S", storylet.id)}["{storylet.id}"]')
    lines.append("  end")

    for source, target, kind in edges:
        arrow = "-->" if kind == "grant" else "-.->"
        lines.append(f"  {source} {arrow} {target}")

    return "\n".join(lines)


def to_dot(library: ContentLibrary) -> str:
    """Return a Graphviz DOT graph of the information graph."""
    edges, facts = _collect_edges(library)
    lines = [
        "digraph september32 {",
        "  rankdir=LR;",
        '  node [fontname="Helvetica", shape=box, style=rounded];',
        '  edge [fontname="Helvetica", fontsize=9];',
    ]
    for anchor in sorted(library.anchors.values(), key=lambda a: (a.order, a.id)):
        lines.append(
            f'  {_node("A", anchor.id)} [label="{anchor.order}. {anchor.title}", '
            'shape=box, style="rounded,filled", fillcolor="#dde6f5"];'
        )
    for fact in sorted(facts):
        lines.append(
            f'  {_node("K", fact)} [label="{fact}", shape=ellipse, '
            'fillcolor="#f5efdd", style=filled];'
        )
    for storylet in sorted(library.storylets.values(), key=lambda s: s.id):
        lines.append(f'  {_node("S", storylet.id)} [label="{storylet.id}"];')
    for source, target, kind in edges:
        style = "solid" if kind == "grant" else "dashed"
        lines.append(f'  {source} -> {target} [style={style}, label="{kind}"];')
    lines.append("}")
    return "\n".join(lines)


def to_markdown(library: ContentLibrary) -> str:
    """Return a Markdown document embedding the Mermaid graph."""
    return "\n".join(
        [
            "# Narrative graph",
            "",
            "> Generated by `s32 graph`. Do not edit; re-run the command.",
            "",
            f"- Generated: `{datetime.now(UTC).isoformat(timespec='seconds')}`",
            f"- Storylets: {len(library.storylets)}, anchors: {len(library.anchors)}, "
            f"knowledge: {len(library.knowledge)}",
            "",
            "Solid arrows grant knowledge. Dashed arrows are gates: the target "
            "cannot fire until the source has happened.",
            "",
            "```mermaid",
            to_mermaid(library),
            "```",
            "",
        ]
    )
