"""The eight Milestone 1 storylets, checked for the things they exist to prove.

Not schema validity — `test_content_and_tooling.py` covers that for everything.
These assert the *design* requirements: that the delayed callbacks are real,
that the relationship model is used for more than trust, that beliefs arrive as
beliefs, and that Noah's three readings are not quietly closed.
"""

from __future__ import annotations

import pytest

from s32_engine import commitments, effects, knowledge, relationships
from s32_engine.director import NarrativeDirector
from s32_engine.rng import Rng
from s32_engine.state import advance_time, new_state, record_storylet

MILESTONE_1 = (
    "june_the_favour",
    "june_welcome_pack",
    "mara_reads_the_room",
    "mara_older_story",
    "noah_asks_for_access",
    "noah_evening_layout",
    "dorm_message",
    "town_road_evening_walk",
)


@pytest.fixture
def game(real_library):
    """A run state with the whole cast present."""
    state = new_state(real_library, seed=4211)
    for character in state["characters"].values():
        character["present"] = True
    return state


def _director(real_library) -> NarrativeDirector:
    return NarrativeDirector(real_library)


# ---------------------------------------------------------------------------
# The set exists and is where it should be
# ---------------------------------------------------------------------------


def test_there_are_exactly_fifteen_storylets(real_library):
    """Fifteen is a validation checkpoint, not a milestone to overshoot."""
    assert len(real_library.storylets) == 15


def test_all_eight_new_storylets_exist(real_library):
    missing = [sid for sid in MILESTONE_1 if sid not in real_library.storylets]
    assert not missing


def test_the_three_silent_characters_now_have_content(real_library):
    counts = {"june": 0, "mara": 0, "noah": 0}
    for storylet in real_library.storylets.values():
        for character in storylet.characters:
            if character in counts:
                counts[character] += 1
    assert all(count >= 2 for count in counts.values()), counts


def test_the_two_empty_locations_now_have_content(real_library):
    used = {s.location for s in real_library.storylets.values() if s.location}
    assert "dorm_room" in used
    assert "town_road" in used


# ---------------------------------------------------------------------------
# Delayed branching
# ---------------------------------------------------------------------------


def test_june_welcome_pack_requires_having_met_her(game, real_library):
    """A callback is only a callback if the earlier scene actually gates it."""
    director = _director(real_library)
    storylet = real_library.storylets["june_welcome_pack"]
    game["world"]["location"] = "classroom_2b"

    assert not director.evaluate(storylet, game).eligible

    record_storylet(game, "june_the_favour")
    assert director.evaluate(storylet, game).eligible


def test_mara_older_story_requires_the_photograph_and_the_earlier_scene(game, real_library):
    director = _director(real_library)
    storylet = real_library.storylets["mara_older_story"]
    game["world"]["location"] = "town_road"
    game["world"]["time_slot"] = "afternoon"

    assert not director.evaluate(storylet, game).eligible

    record_storylet(game, "mara_reads_the_room")
    assert not director.evaluate(storylet, game).eligible, "the photograph is still missing"

    knowledge.grant(game, "old_photo_exists")
    assert director.evaluate(storylet, game).eligible


def test_noah_evening_layout_requires_knowing_what_he_writes(game, real_library):
    director = _director(real_library)
    storylet = real_library.storylets["noah_evening_layout"]
    game["world"]["location"] = "classroom_2b"
    game["world"]["time_slot"] = "evening"

    assert not director.evaluate(storylet, game).eligible

    knowledge.grant(game, "noah_is_writing_about_the_archive")
    assert director.evaluate(storylet, game).eligible


# ---------------------------------------------------------------------------
# Commitments
# ---------------------------------------------------------------------------


def test_june_the_favour_creates_a_promise_on_two_of_three_branches(real_library):
    storylet = real_library.storylets["june_the_favour"]
    creating = [
        branch for branch in storylet.outcomes if any("commit(june_favour" in e for e in branch)
    ]
    assert len(creating) == 2, "saying no must not create an obligation"


def test_the_dorm_can_keep_or_break_the_promise(game, real_library):
    """One file, two outcomes.

    Both are declared where the tooling can see them, which is the rule that
    keeps later content from looking dead.
    """
    storylet = real_library.storylets["dorm_message"]
    commitments.make(game, "june_favour", kind="meeting", participants=["june"], due_day=2)

    kept = [b for b in storylet.outcomes if any("fulfil(june_favour)" in e for e in b)]
    broken = [b for b in storylet.outcomes if any("break(june_favour)" in e for e in b)]
    assert kept and broken

    effects.apply_all(broken[0], game)
    assert commitments.status(game, "june_favour") == "broken"
    assert relationships.get(game, "june", "resentment") > 0


def test_breaking_the_promise_costs_something_measurable(game, real_library):
    commitments.make(
        game, "june_favour", kind="meeting", participants=["june"], due_day=2, importance=45
    )
    commitments.break_(game, "june_favour")
    assert commitments.broken_weight(game, "june") == 45


# ---------------------------------------------------------------------------
# Knowledge: fact, belief, suspicion
# ---------------------------------------------------------------------------


def test_maras_forgery_reading_arrives_as_a_suspicion_not_a_fact(game, real_library):
    """`photo_is_a_forgery` is an interpretation offered by a character.

    Granting it as `known` would make the game decide something the canon has
    explicitly left open. See docs/canon/SEPTEMBER_32.md.
    """
    storylet = real_library.storylets["mara_older_story"]
    granting = [
        effect
        for branch in storylet.outcomes
        for effect in branch
        if "photo_is_a_forgery" in effect
    ]
    assert granting, "the reading must be offered somewhere"
    assert all(e.startswith("suspect(") for e in granting), granting

    effects.apply_all(granting[:1], game)
    assert knowledge.stance(game, "photo_is_a_forgery") == "suspected"
    assert not knowledge.knows(game, "photo_is_a_forgery")


def test_the_player_can_end_up_holding_a_contradiction(game, real_library):
    """Holding both readings at once is the intended state.

    The engine has to be able to see the clash — rule R8.
    """
    knowledge.grant(game, "photo_dated_sept_32")
    knowledge.set_stance(game, "photo_is_a_forgery", "false_belief")

    clashes = knowledge.contradictions(game, real_library)
    assert ("photo_dated_sept_32", "photo_is_a_forgery") in clashes


def test_theo_checks_the_ledger_stays_npc_side(real_library):
    """Preserved from the baseline by design: the player never acquires it."""
    player_grants = [
        effect
        for storylet in real_library.storylets.values()
        for effect in storylet.effects + tuple(e for b in storylet.outcomes for e in b)
        if effect.startswith("know(theo_checks_the_ledger")
    ]
    assert not player_grants

    npc_grants = [
        effect
        for storylet in real_library.storylets.values()
        for effect in storylet.effects + tuple(e for b in storylet.outcomes for e in b)
        if "theo_checks_the_ledger" in effect
    ]
    assert npc_grants and all(e.startswith("npc_stance(") for e in npc_grants)


def test_the_two_previously_unused_facts_are_now_in_play(real_library):
    """The two dormant facts are now in play.

    Both were defined during the bootstrap and left waiting for content.
    """
    referenced = {
        fact
        for storylet in real_library.storylets.values()
        for effect in storylet.effects + tuple(e for b in storylet.outcomes for e in b)
        for fact in effects.referenced_ids(effect).get("knowledge", set())
    }
    assert "mara_knows_the_older_story" in referenced
    assert "photo_is_a_forgery" in referenced


# ---------------------------------------------------------------------------
# Relationships beyond trust
# ---------------------------------------------------------------------------


def test_the_new_content_uses_more_than_trust(real_library):
    axes: set[str] = set()
    for sid in MILESTONE_1:
        storylet = real_library.storylets[sid]
        for effect in storylet.effects + tuple(e for b in storylet.outcomes for e in b):
            for axis in effects.referenced_ids(effect).get("rel_axis", set()):
                axes.add(axis)

    assert len(axes - {"trust"}) >= 3, axes
    assert {"respect", "resentment", "suspicion"} <= axes


def test_there_are_npc_to_npc_effects(real_library):
    """The world should do something when the player is not the subject."""
    npc_pairs: set[str] = set()
    for storylet in real_library.storylets.values():
        for effect in storylet.effects + tuple(e for b in storylet.outcomes for e in b):
            text = effect.strip()
            if text.startswith("rel ") and "->" in text.split(".")[0]:
                npc_pairs.add(text.split()[1].split(".")[0])

    assert len(npc_pairs) >= 2, npc_pairs


def test_telling_noah_costs_iris(game, real_library):
    """A trade-off, not a good/bad choice: you gain Noah and lose Iris."""
    storylet = real_library.storylets["noah_asks_for_access"]
    branch = next(b for b in storylet.outcomes if any("iris->noah" in e for e in b))

    effects.apply_all(branch, game)

    assert relationships.get(game, "noah", "trust") > 0
    assert (
        relationships.get(game, "iris", "trust") < 0
        or relationships.get(game, "iris", "trust") == 0
    )
    assert relationships.get(game, "noah", "suspicion", source="iris") == 3


def test_mara_turns_on_june_without_the_player_being_told(game, real_library):
    storylet = real_library.storylets["mara_reads_the_room"]
    branch = storylet.outcomes[0]
    effects.apply_all(branch, game)
    assert relationships.get(game, "june", "suspicion", source="mara") == 2


# ---------------------------------------------------------------------------
# Ambient content and the repetition problem
# ---------------------------------------------------------------------------


def test_the_road_is_a_second_ambient_option(game, real_library):
    """One repeatable scene accounted for 72% of everything played at baseline."""
    ambient = [
        s
        for s in real_library.storylets.values()
        if s.repeat_policy == "repeatable" and s.category == "ambient"
    ]
    assert len(ambient) >= 2
    assert len({s.location for s in ambient}) >= 2, "both must not be in the same place"


def test_the_road_scene_never_ends_ominously(real_library):
    """The road must stay ordinary.

    Its ordinariness is an asset the story spends later, so no variant may
    foreshadow anything. Checked against the prose, not the metadata.
    """
    from s32tools import paths

    text = (paths.game_dir() / "story" / "storylets" / "places.rpy").read_text(encoding="utf-8")
    start = text.index("label s32_st_town_road_evening_walk")
    body = text[start:]

    for banned in ("wrong", "chill", "somehow", "for some reason", "shiver", "watching"):
        assert banned not in body.lower(), f"the road scene reaches for {banned!r}"


# ---------------------------------------------------------------------------
# Trait gating
# ---------------------------------------------------------------------------


def test_trait_gated_choices_exist_in_the_prose(real_library):
    """A trait should change what the player notices, never how well they do."""
    from s32tools import paths

    gated = 0
    for path in (paths.game_dir() / "story").rglob("*.rpy"):
        text = path.read_text(encoding="utf-8")
        gated += text.count("if has_trait(")
    assert gated >= 2, gated


# ---------------------------------------------------------------------------
# Everything still fits together
# ---------------------------------------------------------------------------


def test_a_long_run_never_selects_an_ineligible_storylet(real_library):
    """The invariant the whole director rests on, over the enlarged library."""
    director = _director(real_library)

    for seed in range(30):
        state = new_state(real_library, seed=seed)
        for character in state["characters"].values():
            character["present"] = True
        rng = Rng(state)

        for step in range(40):
            state["world"]["location"] = sorted(real_library.locations)[step % 8]
            selection = director.select(state, rng)
            if selection.storylet is None:
                advance_time(state, 1)
                continue
            assert director.evaluate(selection.storylet, state, rng).eligible
            director.play(selection.storylet, state)
            advance_time(state, 1)


def test_noahs_callback_line_is_guarded():
    """Noah's scene does not require the facts his dialogue refers back to.

    `noah_evening_layout` only gates on `noah_is_writing_about_the_archive`, so
    about a third of runs reach it having heard of no other year-long gap. The
    line that calls back to one has to check first.
    """
    from s32tools import paths

    text = (paths.game_dir() / "story" / "storylets" / "noah.rpy").read_text(encoding="utf-8")
    line = "That's the second gap about a year long"
    assert line in text

    guard = text.rindex('if knows("school_history_skips_a_year")', 0, text.index(line))
    between = text[guard : text.index(line)]
    assert "else:" not in between, "the callback must sit in the positive branch"
