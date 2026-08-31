"""The condition and effect mini-languages.

Both are matched against a fixed grammar rather than evaluated with ``eval``.
That is what makes them analysable, and it means an unrecognised string must
fail loudly at validation time rather than being silently ignored — the tests
below pin that behaviour down as much as the happy paths.
"""

from __future__ import annotations

import pytest

from s32_engine import commitments, effects, knowledge, relationships
from s32_engine.conditions import ConditionContext, evaluate, evaluate_all, referenced_ids
from s32_engine.errors import ConditionError, EffectError
from s32_engine.state import record_storylet


@pytest.fixture
def ctx(state, rng):
    return ConditionContext(state, rng)


# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("condition", "expected"),
    [
        ("day >= 1", True),
        ("day > 1", False),
        ("calendar_day == 1", True),
        ("location == archive", True),
        ("location != archive", False),
        ("location in archive, rooftop", True),
        ("weather == clear", True),
        ("time_slot == morning", True),
        ("phase == normal", True),
        ("phase >= odd", False),
        ("phase <= impossible", True),
        ("month == September", True),
    ],
)
def test_world_conditions(ctx, condition, expected):
    assert evaluate(condition, ctx).passed is expected


def test_negation(ctx):
    assert evaluate("not location == rooftop", ctx).passed
    assert not evaluate("not location == archive", ctx).passed


def test_relationship_conditions(state, ctx):
    assert not evaluate("rel iris->player.trust >= 10", ctx).passed
    relationships.change(state, "iris", "player", "trust", 10)
    assert evaluate("rel iris->player.trust >= 10", ctx).passed


def test_npc_to_npc_condition(state, ctx):
    relationships.change(state, "theo", "mara", "respect", 30)
    assert evaluate("rel theo->mara.respect >= 30", ctx).passed
    assert not evaluate("rel mara->theo.respect >= 30", ctx).passed


def test_knowledge_conditions(state, ctx):
    assert not evaluate("knows(photo)", ctx).passed
    knowledge.suspect(state, "photo")
    assert not evaluate("knows(photo)", ctx).passed, "a suspicion is not knowledge"
    assert evaluate("suspects(photo)", ctx).passed
    knowledge.grant(state, "photo")
    assert evaluate("knows(photo)", ctx).passed


def test_npc_knowledge_conditions(state, ctx):
    knowledge.grant(state, "photo", agent="iris")
    assert evaluate("npc_knows(iris, photo)", ctx).passed
    assert evaluate("stance(iris, photo) == known", ctx).passed
    assert evaluate("stance(theo, photo) == unknown", ctx).passed


def test_history_conditions(state, ctx):
    assert evaluate("not_seen(intro)", ctx).passed
    record_storylet(state, "intro")
    assert evaluate("seen(intro)", ctx).passed
    assert evaluate("seen_count(intro) == 1", ctx).passed
    assert evaluate("days_since(intro) >= 0", ctx).passed


def test_days_since_treats_never_seen_as_long_ago(ctx):
    """Otherwise a cooldown-shaped requirement would gate the first occurrence."""
    result = evaluate("days_since(intro) >= 3", ctx)
    assert result.passed
    assert "never seen" in result.detail


def test_item_and_anchor_conditions(state, ctx):
    assert not evaluate("has_item(camera)", ctx).passed
    state["inventory"].append("camera")
    assert evaluate("has_item(camera)", ctx).passed

    assert not evaluate("anchor_done(start)", ctx).passed
    state["anchors_done"].append("start")
    assert evaluate("anchor_done(start)", ctx).passed


def test_commitment_conditions(state, ctx):
    assert evaluate("commitment(meet) == none", ctx).passed
    commitments.make(state, "meet", kind="meeting", participants=["theo"], due_day=3)
    assert evaluate("commitment(meet) == active", ctx).passed
    commitments.break_(state, "meet")
    assert evaluate("commitment(meet) == broken", ctx).passed
    assert evaluate("broken_weight(theo) >= 50", ctx).passed


def test_character_conditions(state, ctx):
    assert evaluate("char iris.present == true", ctx).passed
    state["characters"]["iris"]["present"] = False
    assert evaluate("char iris.present == false", ctx).passed

    state["characters"]["iris"]["mood"] = "withdrawn"
    assert evaluate("char iris.mood == withdrawn", ctx).passed
    assert evaluate("char iris.availability >= 50", ctx).passed


def test_chance_is_deterministic_for_a_given_state(state, library):
    """The same counter must always give the same answer, or rollback lies."""
    from s32_engine.rng import Rng
    from s32_engine.state import new_state

    def roll() -> list[bool]:
        probe = new_state(library, seed=7)
        probe_ctx = ConditionContext(probe, Rng(probe))
        return [evaluate("chance(0.5)", probe_ctx).passed for _ in range(10)]

    assert roll() == roll()


def test_chance_without_an_rng_is_an_error(state):
    with pytest.raises(ConditionError, match="without an RNG"):
        evaluate("chance(0.5)", ConditionContext(state, None))


def test_an_unrecognised_condition_raises(ctx):
    """Silently ignoring it would let a broken gate ship as an open door."""
    with pytest.raises(ConditionError, match="unrecognised condition"):
        evaluate("iris.vibes are good", ctx)


def test_an_empty_condition_raises(ctx):
    with pytest.raises(ConditionError, match="empty condition"):
        evaluate("   ", ctx)


def test_evaluate_all_does_not_short_circuit(ctx):
    """Every reason a scene did not fire, not just the first."""
    results = evaluate_all(["day >= 99", "location == archive", "knows(photo)"], ctx)
    assert len(results) == 3
    assert [r.passed for r in results] == [False, True, False]


def test_referenced_ids_finds_content_references():
    assert referenced_ids("knows(old_photo)")["knowledge"] == {"old_photo"}
    assert referenced_ids("rel iris->player.trust >= 5")["character"] == {"iris", "player"}
    assert referenced_ids("has_item(camera)")["item"] == {"camera"}
    assert referenced_ids("not seen(intro)")["storylet"] == {"intro"}


# ---------------------------------------------------------------------------
# Effects
# ---------------------------------------------------------------------------


def test_relationship_effects(state):
    effects.apply_effect("rel iris->player.trust += 7", state)
    assert relationships.get(state, "iris", "player", "trust") == 7
    effects.apply_effect("rel iris->player.trust -= 2", state)
    assert relationships.get(state, "iris", "player", "trust") == 5
    effects.apply_effect("rel iris->player.trust = 40", state)
    assert relationships.get(state, "iris", "player", "trust") == 40


def test_trait_and_flag_effects(state):
    effects.apply_effect("trait curious += 2", state)
    assert state["traits"]["curious"] == 2
    effects.apply_effect("flag visits += 3", state)
    assert state["world"]["flags"]["visits"] == 3
    effects.apply_effect("flag visits = 1", state)
    assert state["world"]["flags"]["visits"] == 1


def test_knowledge_effects(state):
    effects.apply_effect("know(photo, box_17)", state)
    assert knowledge.knows(state, "photo")
    belief = knowledge.belief(state, "photo")
    assert belief is not None
    assert belief["source"] == "box_17"

    effects.apply_effect("npc_stance(iris, photo, suspected)", state)
    assert knowledge.stance(state, "photo", "iris") == "suspected"


def test_item_effects(state):
    effects.apply_effect("item(camera)", state)
    assert "camera" in state["inventory"]
    effects.apply_effect("item(camera)", state)
    assert state["inventory"].count("camera") == 1, "adding twice must not duplicate"
    effects.apply_effect("drop_item(camera)", state)
    assert "camera" not in state["inventory"]


def test_phase_cannot_move_backwards(state):
    """A late storylet must not be able to drag the run back to `normal`."""
    effects.apply_effect("phase = unsettling", state)
    assert state["world"]["phase"] == "unsettling"

    with pytest.raises(EffectError, match="cannot move backwards"):
        effects.apply_effect("phase = normal", state)


def test_unknown_enum_values_are_errors(state):
    with pytest.raises(EffectError, match="unknown phase"):
        effects.apply_effect("phase = apocalypse", state)
    with pytest.raises(EffectError, match="unknown weather"):
        effects.apply_effect("weather = frogs", state)


def test_time_and_location_effects(state):
    effects.apply_effect("location = rooftop", state)
    assert state["world"]["location"] == "rooftop"
    effects.apply_effect("time += 2", state)
    assert state["world"]["time_slot"] == "afternoon"


def test_commitment_effects(state):
    effects.apply_effect("commit(meet_theo, theo, 2, 70)", state)
    record = commitments.get(state, "meet_theo")
    assert record is not None
    assert record["status"] == "active"
    assert record["due_day"] == state["world"]["day"] + 2
    assert record["importance"] == 70

    effects.apply_effect("fulfil(meet_theo)", state)
    assert commitments.status(state, "meet_theo") == "fulfilled"


def test_character_effects(state):
    effects.apply_effect("char iris.mood = withdrawn", state)
    assert state["characters"]["iris"]["mood"] == "withdrawn"
    effects.apply_effect("char iris.present = false", state)
    assert state["characters"]["iris"]["present"] is False
    effects.apply_effect("char iris.availability -= 20", state)
    assert state["characters"]["iris"]["availability"] == 30


def test_effects_on_an_unknown_character_are_errors(state):
    with pytest.raises(EffectError, match="unknown character"):
        effects.apply_effect("char nobody.mood = sad", state)


def test_an_unrecognised_effect_raises(state):
    with pytest.raises(EffectError, match="unrecognised effect"):
        effects.apply_effect("make iris happy", state)


def test_effects_apply_in_order(state):
    """Order is preserved because an effect may depend on one above it."""
    effects.apply_all(["know(photo)", "phase = odd", "rel iris->player.trust += 3"], state)
    assert knowledge.knows(state, "photo")
    assert state["world"]["phase"] == "odd"
    assert relationships.get(state, "iris", "player", "trust") == 3


def test_granted_knowledge_reads_player_grants_only(state):
    granted = effects.granted_knowledge(
        ["know(photo)", "npc_stance(iris, date, known)", "suspect(forgery)"]
    )
    assert granted == {"photo"}
