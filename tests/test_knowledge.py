"""Belief stances, the transition table, and contradictions."""

from __future__ import annotations

import pytest

from s32_engine import knowledge


def test_unknown_facts_read_as_unknown(state):
    assert knowledge.stance(state, "never_heard_of_it") == "unknown"
    assert knowledge.confidence(state, "never_heard_of_it") == 0.0
    assert not knowledge.knows(state, "never_heard_of_it")


def test_grant_makes_a_fact_known(state):
    assert knowledge.grant(state, "photo", source="box_17") == "known"
    assert knowledge.knows(state, "photo")
    belief = knowledge.belief(state, "photo")
    assert belief is not None
    assert belief["source"] == "box_17"


def test_suspecting_is_not_knowing(state):
    """The distinction the whole mystery rests on."""
    knowledge.suspect(state, "date")

    assert knowledge.suspects(state, "date")
    assert not knowledge.knows(state, "date")


def test_each_agent_holds_their_own_stance(state):
    knowledge.grant(state, "photo", agent="player")
    knowledge.suspect(state, "photo", agent="iris")
    knowledge.set_stance(state, "photo", "false_belief", agent="mara")

    assert knowledge.stance(state, "photo", "player") == "known"
    assert knowledge.stance(state, "photo", "iris") == "suspected"
    assert knowledge.stance(state, "photo", "mara") == "false_belief"
    assert knowledge.stance(state, "photo", "theo") == "unknown"


def test_disproven_is_terminal_without_force(state):
    knowledge.grant(state, "date")
    knowledge.disprove(state, "date")

    # A fact the story took the trouble to disprove must not quietly become
    # true again; re-establishing it has to be a deliberate, greppable act.
    assert knowledge.set_stance(state, "date", "known") == "disproven"
    assert knowledge.set_stance(state, "date", "known", force=True) == "known"


def test_illegal_transitions_are_refused_not_raised(state):
    """Content bugs here must not crash a player's session."""
    knowledge.grant(state, "photo")
    assert knowledge.set_stance(state, "photo", "false_belief") == "known"


def test_an_unknown_stance_name_is_an_error(state):
    with pytest.raises(ValueError, match="unknown stance"):
        knowledge.set_stance(state, "photo", "vibes")  # type: ignore[arg-type]


def test_restating_the_same_stance_can_update_confidence(state):
    knowledge.grant(state, "photo", confidence_value=1.0)
    knowledge.set_stance(state, "photo", "known", confidence_value=0.4)
    assert knowledge.confidence(state, "photo") == 0.4


def test_confidence_is_clamped(state):
    knowledge.grant(state, "photo", confidence_value=9.0)
    assert knowledge.confidence(state, "photo") == 1.0
    knowledge.set_stance(state, "photo", "known", confidence_value=-3.0)
    assert knowledge.confidence(state, "photo") == 0.0


def test_learned_day_is_recorded(state):
    state["world"]["day"] = 7
    knowledge.grant(state, "photo")
    belief = knowledge.belief(state, "photo")
    assert belief is not None
    assert belief["learned_day"] == 7


def test_known_facts_is_sorted_and_excludes_suspicions(state):
    knowledge.grant(state, "photo")
    knowledge.grant(state, "date")
    knowledge.suspect(state, "forgery")

    assert knowledge.known_facts(state) == ["date", "photo"]


def test_contradictions_are_detected(state, library):
    knowledge.grant(state, "date")
    knowledge.set_stance(state, "forgery", "false_belief")

    assert knowledge.contradictions(state, library) == [("date", "forgery")]


def test_a_suspicion_is_not_a_contradiction(state, library):
    """Holding a hunch alongside a fact is not yet a problem."""
    knowledge.grant(state, "date")
    knowledge.suspect(state, "forgery")

    assert knowledge.contradictions(state, library) == []


def test_contradictions_are_per_agent(state, library):
    knowledge.grant(state, "date", agent="mara")
    knowledge.set_stance(state, "forgery", "false_belief", agent="mara")

    assert knowledge.contradictions(state, library, agent="mara")
    assert not knowledge.contradictions(state, library, agent="player")
