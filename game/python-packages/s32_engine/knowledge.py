"""Who believes what, and how sure they are.

Information is a mechanic in September 32, not a set of booleans. The archive
produces documents that contradict each other, so the engine must be able to
say that the player *knows* a photograph exists, that Iris *suspects* it was
mislabelled, that Theo has *never heard of it*, and that Mara holds a
**false belief** about it that she will defend.

Five stances, one confidence number, one source string. That is deliberately
less than a real epistemic model: anything richer would be unmaintainable at
several hundred scenes, and nothing in the design needs it.

Legal stance transitions are constrained (see :data:`ALLOWED_TRANSITIONS`) so
that content cannot quietly walk a character back from ``disproven`` to
``known`` without an explicit, auditable override.
"""

from __future__ import annotations

from s32_engine.containers import new_dict
from s32_engine.types import (
    KNOWLEDGE_STANCES,
    PLAYER,
    BeliefState,
    ContentLibrary,
    GameState,
    KnowledgeStance,
)

#: Which stance changes content may perform without an explicit override.
#:
#: ``disproven`` is a terminal state on purpose: a fact the story has taken the
#: trouble to disprove should not silently become true again. Re-establishing it
#: is a dramatic event and must pass ``force=True``, which is greppable.
ALLOWED_TRANSITIONS: dict[KnowledgeStance, frozenset[KnowledgeStance]] = {
    "unknown": frozenset({"suspected", "known", "false_belief"}),
    "suspected": frozenset({"known", "false_belief", "disproven", "unknown"}),
    "known": frozenset({"disproven", "suspected"}),
    "false_belief": frozenset({"suspected", "known", "disproven"}),
    "disproven": frozenset(),
}


def _agent_map(state: GameState, agent: str) -> dict[str, BeliefState]:
    """Return the mutable belief map for one agent, creating it if needed."""
    beliefs = state["beliefs"].get(agent)
    if beliefs is None:
        beliefs = new_dict()
        state["beliefs"][agent] = beliefs
    return beliefs


def stance(state: GameState, fact_id: str, agent: str = PLAYER) -> KnowledgeStance:
    """Return an agent's stance on a fact; unheard-of facts read ``unknown``."""
    belief = state["beliefs"].get(agent, {}).get(fact_id)
    if belief is None:
        return "unknown"
    return belief["stance"]


def confidence(state: GameState, fact_id: str, agent: str = PLAYER) -> float:
    """Return how strongly an agent holds their stance, in ``[0.0, 1.0]``."""
    belief = state["beliefs"].get(agent, {}).get(fact_id)
    return 0.0 if belief is None else belief["confidence"]


def belief(state: GameState, fact_id: str, agent: str = PLAYER) -> BeliefState | None:
    """Return the full belief record, or ``None`` if the agent has no stance."""
    return state["beliefs"].get(agent, {}).get(fact_id)


def knows(state: GameState, fact_id: str, agent: str = PLAYER) -> bool:
    """Return whether the agent holds the fact as known.

    This is the predicate storylet requirements use; ``suspected`` deliberately
    does not satisfy it, because "I have a hunch" and "I have seen the file"
    should not unlock the same scene.
    """
    return stance(state, fact_id, agent) == "known"


def suspects(state: GameState, fact_id: str, agent: str = PLAYER) -> bool:
    """Return whether the agent suspects *or* knows the fact."""
    return stance(state, fact_id, agent) in {"suspected", "known"}


def set_stance(
    state: GameState,
    fact_id: str,
    new_stance: KnowledgeStance,
    *,
    agent: str = PLAYER,
    confidence_value: float | None = None,
    source: str = "",
    force: bool = False,
) -> KnowledgeStance:
    """Move an agent's stance on a fact, respecting the transition table.

    Args:
        state: Run state to mutate.
        fact_id: Knowledge id. Validated against the library by the content
            validator, not here, so play never pays for the lookup.
        new_stance: Target stance.
        agent: Whose belief changes. Defaults to the player.
        confidence_value: Explicit confidence. Defaults to a value implied by
            the stance.
        source: Short tag naming what caused the change (``"old_photo"``,
            ``"iris_told_me"``). Surfaced in the clue journal.
        force: Permit a transition the table forbids. Reserved for anchors and
            migrations; every use should be justified in the scene card.

    Returns:
        The stance actually held after the call, which is the previous stance if
        the transition was refused.
    """
    if new_stance not in KNOWLEDGE_STANCES:
        raise ValueError(f"unknown stance: {new_stance!r}")

    beliefs = _agent_map(state, agent)
    current = beliefs.get(fact_id)
    current_stance: KnowledgeStance = "unknown" if current is None else current["stance"]

    if current_stance == new_stance:
        if confidence_value is not None and current is not None:
            current["confidence"] = _clamp_confidence(confidence_value)
        return current_stance

    if not force and new_stance not in ALLOWED_TRANSITIONS[current_stance]:
        return current_stance

    beliefs[fact_id] = new_dict(
        {
            "stance": new_stance,
            "confidence": _clamp_confidence(
                confidence_value
                if confidence_value is not None
                else _default_confidence(new_stance)
            ),
            "source": source or (current["source"] if current else ""),
            "learned_day": state["world"]["day"],
        }
    )
    return new_stance


def grant(
    state: GameState,
    fact_id: str,
    *,
    agent: str = PLAYER,
    source: str = "",
    confidence_value: float = 1.0,
) -> KnowledgeStance:
    """Promote a fact to ``known`` for an agent.

    The common case in scene scripts. Shorthand for :func:`set_stance` with
    ``"known"``.

    Example:
        >>> from s32_engine.state import new_state
        >>> from s32_engine.types import ContentLibrary
        >>> st = new_state(ContentLibrary())
        >>> grant(st, "old_photo", source="archive_box_3")
        'known'
    """
    return set_stance(
        state,
        fact_id,
        "known",
        agent=agent,
        confidence_value=confidence_value,
        source=source,
    )


def suspect(
    state: GameState,
    fact_id: str,
    *,
    agent: str = PLAYER,
    source: str = "",
    confidence_value: float = 0.5,
) -> KnowledgeStance:
    """Move a fact to ``suspected`` for an agent."""
    return set_stance(
        state,
        fact_id,
        "suspected",
        agent=agent,
        confidence_value=confidence_value,
        source=source,
    )


def disprove(
    state: GameState, fact_id: str, *, agent: str = PLAYER, source: str = ""
) -> KnowledgeStance:
    """Move a fact to ``disproven`` for an agent."""
    return set_stance(state, fact_id, "disproven", agent=agent, confidence_value=1.0, source=source)


def known_facts(state: GameState, agent: str = PLAYER) -> list[str]:
    """Return every fact the agent holds as known, in stable order."""
    return sorted(
        fact_id
        for fact_id, entry in state["beliefs"].get(agent, {}).items()
        if entry["stance"] == "known"
    )


def contradictions(
    state: GameState, library: ContentLibrary, agent: str = PLAYER
) -> list[tuple[str, str]]:
    """Return pairs of facts the agent holds that cannot both be true.

    This is what powers the "wait, that can't be right" beats: the player can
    accumulate mutually exclusive evidence, and the engine can notice before
    the player does and offer a scene about it.
    """
    held = {
        fact_id
        for fact_id, entry in state["beliefs"].get(agent, {}).items()
        if entry["stance"] in {"known", "false_belief"}
    }
    found: set[tuple[str, str]] = set()
    for fact_id in sorted(held):
        definition = library.knowledge.get(fact_id)
        if definition is None:
            continue
        for other in definition.contradicts:
            if other in held:
                found.add((fact_id, other) if fact_id < other else (other, fact_id))
    return sorted(found)


def _default_confidence(target: KnowledgeStance) -> float:
    """Return the confidence a stance implies when none was supplied."""
    return {
        "unknown": 0.0,
        "suspected": 0.5,
        "known": 1.0,
        "false_belief": 0.8,
        "disproven": 1.0,
    }[target]


def _clamp_confidence(value: float) -> float:
    """Clamp a confidence value into ``[0.0, 1.0]``."""
    return max(0.0, min(1.0, float(value)))
