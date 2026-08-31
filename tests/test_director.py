"""Eligibility, priority tiers, weighting, cooldowns, and the debug trace."""

from __future__ import annotations

from s32_engine import knowledge, relationships
from s32_engine.director import NarrativeDirector
from s32_engine.rng import Rng
from s32_engine.state import advance_time, new_state, record_storylet


def test_location_gates_a_storylet(state, library):
    director = NarrativeDirector(library)

    state["world"]["location"] = "hall"
    assert not director.evaluate(library.storylets["intro"], state).eligible

    state["world"]["location"] = "archive"
    assert director.evaluate(library.storylets["intro"], state).eligible


def test_absent_characters_gate_a_storylet(state, library):
    director = NarrativeDirector(library)
    state["characters"]["iris"]["present"] = False

    evaluation = director.evaluate(library.storylets["intro"], state)

    assert not evaluation.eligible
    assert any("iris not present" in reason for reason in evaluation.rejections)


def test_requirements_gate_a_storylet(state, library):
    director = NarrativeDirector(library)
    assert not director.evaluate(library.storylets["followup"], state).eligible

    knowledge.grant(state, "photo")
    relationships.change(state, "iris", "player", "trust", 5)

    assert director.evaluate(library.storylets["followup"], state).eligible


def test_a_passing_blocker_blocks(state, library):
    director = NarrativeDirector(library)
    state["world"]["location"] = "rooftop"
    assert director.evaluate(library.storylets["blocked"], state).eligible

    relationships.change(state, "iris", "player", "trust", 10)
    assert not director.evaluate(library.storylets["blocked"], state).eligible


def test_repeat_policy_once(state, library):
    director = NarrativeDirector(library)
    record_storylet(state, "intro")

    evaluation = director.evaluate(library.storylets["intro"], state)
    assert not evaluation.eligible
    assert any("repeat_policy" in reason for reason in evaluation.rejections)


def test_cooldown_blocks_then_expires(state, library):
    director = NarrativeDirector(library)
    state["world"]["location"] = "hall"
    record_storylet(state, "ambient")

    assert not director.evaluate(library.storylets["ambient"], state).eligible

    advance_time(state, 7 * 2)  # two whole days
    assert director.evaluate(library.storylets["ambient"], state).eligible


def test_the_trace_names_the_failing_clause(state, library):
    """The feature that makes the system usable at scale."""
    director = NarrativeDirector(library)
    knowledge.grant(state, "photo")

    evaluation = director.evaluate(library.storylets["followup"], state)
    text = evaluation.format()

    assert "ELIGIBLE: false" in text
    assert "PASS knows(photo)" in text
    assert "FAIL rel iris->player.trust >= 5" in text
    # The actual value, not just the clause: "needs 5" is useless without
    # "currently 0".
    assert "iris->player.trust=0" in text


def test_the_trace_reports_every_failure_not_just_the_first(state, library):
    director = NarrativeDirector(library)
    state["world"]["location"] = "hall"

    evaluation = director.evaluate(library.storylets["followup"], state)

    assert len(evaluation.requirement_results) == 2
    assert evaluation.rejections


def test_priority_is_a_hard_tier(state, library, rng):
    """A high-priority scene beats a heavier low-priority one every time."""
    director = NarrativeDirector(library)
    state["world"]["location"] = "archive"

    for _ in range(20):
        probe = new_state(library, seed=state["seed"])
        for character in probe["characters"].values():
            character["present"] = True
        probe["world"]["location"] = "archive"
        selection = director.select(probe, Rng(probe))
        assert selection.storylet is not None
        assert selection.storylet.id == "intro"


def test_select_returns_none_when_nothing_fits(state, library, rng):
    director = NarrativeDirector(library)
    state["world"]["location"] = "nowhere"

    selection = director.select(state, rng)

    assert selection.storylet is None
    assert selection.eligible == []


def test_select_never_returns_an_ineligible_storylet(library):
    """The invariant the whole system depends on."""
    director = NarrativeDirector(library)

    for seed in range(60):
        probe = new_state(library, seed=seed)
        for character in probe["characters"].values():
            character["present"] = True
        probe["world"]["location"] = ["archive", "hall", "rooftop"][seed % 3]
        rng = Rng(probe)

        selection = director.select(probe, rng)
        if selection.storylet is None:
            continue
        assert director.evaluate(selection.storylet, probe, rng).eligible


def test_play_applies_effects_and_records_history(state, library):
    director = NarrativeDirector(library)
    changes = director.play(library.storylets["intro"], state)

    assert relationships.get(state, "iris", "player", "trust") == 5
    assert knowledge.knows(state, "photo")
    assert state["history"][-1]["id"] == "intro"
    assert state["seen_counts"]["intro"] == 1
    assert any("trust" in change for change in changes)


def test_repeats_are_damped(state, library):
    director = NarrativeDirector(library)
    evaluation = director.evaluate(library.storylets["ambient"], state)

    first = director._effective_weight(state, evaluation)
    record_storylet(state, "ambient")
    second = director._effective_weight(state, evaluation)

    assert second < first


def test_next_anchor_is_ordered_and_reports_readiness(state, library, rng):
    director = NarrativeDirector(library)

    assert director.next_anchor(state, rng) == ("start", True)

    state["anchors_done"].append("start")
    assert director.next_anchor(state, rng) == ("second", False)

    knowledge.grant(state, "photo")
    assert director.next_anchor(state, rng) == ("second", True)

    state["anchors_done"].append("second")
    assert director.next_anchor(state, rng) is None


def test_fast_and_full_eligibility_agree(library):
    """`is_eligible` short-circuits; it must not disagree with `evaluate`.

    They exist separately because the trace is what makes the director
    debuggable and what makes a million-iteration sweep slow. Two code paths
    for one question is a real risk, so it is pinned here.
    """
    director = NarrativeDirector(library)

    for seed in range(40):
        probe = new_state(library, seed=seed)
        for index, character in enumerate(probe["characters"].values()):
            character["present"] = seed % 3 != index % 3
        probe["world"]["location"] = ["archive", "hall", "rooftop", "nowhere"][seed % 4]
        probe["world"]["phase"] = "odd" if seed % 5 == 0 else "normal"
        if seed % 2:
            knowledge.grant(probe, "photo")
            relationships.change(probe, "iris", "player", "trust", seed % 12)
        if seed % 7 == 0:
            record_storylet(probe, "intro")

        for storylet in library.storylets.values():
            fast = director.is_eligible(storylet, probe, Rng(probe))
            full = director.evaluate(storylet, probe, Rng(probe)).eligible
            assert fast == full, f"disagreement on {storylet.id} at seed {seed}"
