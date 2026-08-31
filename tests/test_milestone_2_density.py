"""Milestone 2: the things the density work is supposed to guarantee.

Milestone 1 proved that content alone does not make a director choose. The
selection moment had one candidate 93% of the time and the top priority tier
had one candidate 100% of the time, so `weight`, repeat damping and the player
profiles were all inert -- three mechanisms that could not act on anything.

Milestone 2's answer was content discipline, not algorithm change: priority
bands so scenes can share a tier, fifteen storylets aimed at cells the
simulator said were busy, and a player model that moves for a reason. These
tests hold the parts of that which can be broken silently.

Deliberately absent: any assertion on a headline percentage. Those live in the
generated reports, where a content change is meant to move them.
"""

from __future__ import annotations

import pytest

from s32_engine.director import NarrativeDirector
from s32_engine.rng import Rng
from s32_engine.state import new_state, record_storylet
from s32_engine.types import TIME_SLOTS
from s32tools.simulation import profiles as profile_module
from s32tools.simulation.simulator import Simulator
from s32tools.validation.content import PRIORITY_BANDS

#: The fifteen scenes Milestone 2 added.
MILESTONE_2 = (
    "archive_iris_index",
    "archive_theo_returns",
    "classroom_before_bell",
    "courtyard_lunch_table",
    "courtyard_morning_queue",
    "dorm_corridor_noise",
    "dorm_late_night",
    "gate_early_arrival",
    "gate_noticeboard",
    "gate_waiting",
    "hallway_after_bell",
    "hallway_lost_property",
    "iris_outside",
    "town_road_last_bus",
    "town_road_shops",
)


@pytest.fixture
def game(real_library):
    """A run state with the whole cast present."""
    state = new_state(real_library, seed=90210)
    for character in state["characters"].values():
        character["present"] = True
    return state


# ---------------------------------------------------------------------------
# Priority bands
# ---------------------------------------------------------------------------


def test_every_storylet_sits_on_a_band(real_library):
    """The convention is only worth having if nothing drifts off it.

    `s32 validate` reports this as info rather than an error, because a
    deliberate exception is allowed. There are none today, and one appearing
    should be a decision rather than a surprise.
    """
    off_band = {
        sid: s.priority
        for sid, s in real_library.storylets.items()
        if s.priority not in PRIORITY_BANDS
    }
    assert not off_band


def test_priority_is_a_band_and_not_a_ranking(real_library):
    """Many storylets per distinct priority, which is the whole distinction.

    Milestone 1 had fifteen storylets on fifteen values, one each, and the top
    tier was consequently a singleton in 100% of selections. The failure this
    guards against is drift back toward that: a new scene given 41 because it
    should beat something at 40.

    `URGENT` legitimately holds one storylet today, so the assertion is about
    the ratio rather than about every band being shared.
    """
    counts: dict[int, int] = {}
    for storylet in real_library.storylets.values():
        counts[storylet.priority] = counts.get(storylet.priority, 0) + 1
    assert len(counts) <= len(PRIORITY_BANDS), counts
    assert len(real_library.storylets) / len(counts) >= 4.0, counts


def test_ambient_never_outranks_content(real_library):
    """The whole point of the bottom band.

    Texture that can beat a character scene is not texture. Checked as a
    property of the library rather than of one pair, since the failure mode is
    somebody raising one ambient scene to make sure it gets seen.
    """
    ambient = [s for s in real_library.storylets.values() if s.category == "ambient"]
    assert ambient
    highest_ambient = max(s.priority for s in ambient)
    non_ambient = [s for s in real_library.storylets.values() if s.category != "ambient"]
    assert all(s.priority >= highest_ambient for s in non_ambient)


# ---------------------------------------------------------------------------
# Weight, which the bands exist to let act
# ---------------------------------------------------------------------------


def test_weights_stay_in_the_authoring_range(real_library):
    """0.5 to 3.0.

    The two ways out of that range are both ways of avoiding a decision: a
    weight near zero hides a scene that should have a requirement or be
    deleted, and a huge weight guarantees a scene that should be in a higher
    band. Neither shows up in a play count until somebody goes looking.
    """
    out_of_range = {
        sid: s.weight for sid, s in real_library.storylets.items() if not 0.5 <= s.weight <= 3.0
    }
    assert not out_of_range


def test_the_weighted_draw_actually_decides_something(real_library):
    """Contested tiers happen, and more than one scene wins them.

    This is the mechanism Milestone 1 measured as firing in 0.0% of
    selections -- not rarely, never. Asserted over real runs rather than a
    constructed state, because a constructed one proves the director can
    contest and says nothing about whether the library ever asks it to.
    """
    profile = profile_module.get("random")
    contested = 0
    winners: set[str] = set()

    class Watch(Simulator):
        def _apply_profile(self, selection, state, rng, prof):
            nonlocal contested
            top = max(e.priority for e in selection.eligible)
            tier = [e for e in selection.eligible if e.priority == top]
            chosen = super()._apply_profile(selection, state, rng, prof)
            if len(tier) >= 2:
                contested += 1
                winners.add(chosen.id)
            return chosen

    watcher = Watch(real_library)
    for seed in range(1234, 1254):
        watcher.run_once(seed, profile)

    assert contested > 0, "no selection moment offered the draw a choice"
    assert len(winners) >= 2, f"one scene won every contest: {winners}"


def test_repeat_damping_still_bites(real_library, game):
    """Seeing a scene halves its effective weight, once per viewing."""
    director = NarrativeDirector(real_library)
    storylet = real_library.storylets["courtyard_small_talk"]
    evaluation = director.evaluate(storylet, game, Rng(game))

    before = director._effective_weight(game, evaluation)
    record_storylet(game, storylet.id)
    after = director._effective_weight(game, evaluation)
    assert after == pytest.approx(before / 2.0)


# ---------------------------------------------------------------------------
# Cells
# ---------------------------------------------------------------------------


def test_no_storylet_is_available_at_every_hour(real_library):
    """An unslotted storylet is authored for four in the morning too.

    Four of them were, before Milestone 2, which is how the archive came to be
    offering scenes in a locked room at 3am. `time_slots` is not optional
    metadata; leaving it off is a claim, and it is almost always the wrong one.
    docs/narrative-design/CELL_MAP.md
    """
    unslotted = [sid for sid, s in real_library.storylets.items() if not s.time_slots]
    assert not unslotted


def test_school_gate_exists(real_library):
    """It had nothing at any hour, in a game set at a school."""
    gate = [s for s in real_library.storylets.values() if s.location == "school_gate"]
    assert len(gate) >= 2


def test_every_location_has_something(real_library):
    """A location with nothing authored anywhere in it is a set, not a place."""
    used = {s.location for s in real_library.storylets.values() if s.location}
    assert set(real_library.locations) <= used


def test_time_slots_are_real(real_library):
    """Milestone 1's pacing report invented `late_morning` and `late_afternoon`.

    Nothing in the data did, and nothing should: the loader would reject it.
    Asserted anyway, because the vocabulary being wrong in a document was hard
    to see and the same mistake in a JSON file would be worse.
    """
    for storylet in real_library.storylets.values():
        assert set(storylet.time_slots) <= set(TIME_SLOTS), storylet.id


# ---------------------------------------------------------------------------
# The player model
# ---------------------------------------------------------------------------


def test_profiles_have_somewhere_to_go_and_something_to_say(real_library):
    """Both halves of the Milestone 1 inertness fix.

    `mobility` gives a profile a reason to change location that is not
    starvation; `outcome_weights` gives it a reason to answer one way rather
    than another. Without both, two profiles that reach the same scene leave it
    in the same state and nothing downstream can diverge.
    """
    for profile in profile_module.PROFILES.values():
        assert 0.0 <= profile.mobility <= 1.0, profile.name
        if profile.name != "random":
            assert profile.outcome_weights, profile.name


def test_outcome_scoring_reads_the_declared_effects():
    """The profile answers from the effects, not from the prose."""
    romantic = profile_module.get("romantic")
    warm = romantic.outcome_score(("rel iris.attraction += 3", "trait gentle"))
    flat = romantic.outcome_score(("flag nothing += 1",))
    assert warm > flat

    selfish = profile_module.get("selfish")
    assert selfish.outcome_score(("break(walk_with_june)",)) > selfish.outcome_score(
        ("fulfil(walk_with_june)",)
    )


def test_a_profile_without_opinions_scores_everything_the_same():
    """`random` must stay the control group.

    It is the profile that keeps a branch from becoming unreachable because no
    profile likes it, so it has to remain exactly the old uniform behaviour.
    """
    control = profile_module.get("random")
    assert control.outcome_score(("rel iris.attraction += 3",)) == control.outcome_score(
        ("rel iris.suspicion += 3",)
    )


def test_profiles_diverge_over_a_run(real_library):
    """Two different players should not finish the same week identically.

    The Milestone 1 failure was total -- every profile produced byte-identical
    output -- so this asserts the coarsest possible difference rather than a
    magnitude. `scripts/profile_divergence.py` is where the magnitudes live.
    """
    simulator = Simulator(real_library)
    seeds = range(500, 508)

    def fingerprint(name: str) -> tuple[object, ...]:
        profile = profile_module.get(name)
        runs = [simulator.run_once(seed, profile) for seed in seeds]
        return tuple(
            (tuple(sorted(run.traits.items())), tuple(sorted(run.storylets_played))) for run in runs
        )

    assert fingerprint("romantic") != fingerprint("selfish")
    assert fingerprint("curious") != fingerprint("altruistic")


def test_relocation_is_deterministic(real_library):
    """The same seed and profile must still produce the same run.

    Movement now consumes RNG that it did not before. Determinism is what makes
    a reported dead end reproducible from the seed in the report, so it is
    worth a test of its own rather than being assumed.
    """
    simulator = Simulator(real_library)
    profile = profile_module.get("investigator")
    first = simulator.run_once(777, profile)
    second = simulator.run_once(777, profile)
    assert first.storylets_played == second.storylets_played
    assert first.relationships == second.relationships


def test_a_short_sweep_reaches_everything(real_library):
    """Every authored scene fires somewhere in a small sweep.

    `gate_waiting` and `archive_theo_returns` did not, until the player model
    stopped changing location only when it was starving: `school_gate` in the
    afternoon had zero visits in 5000 runs, so two perfectly eligible scenes
    were unreachable for a reason nothing in the content could show.
    """
    simulator = Simulator(real_library)
    result = simulator.run_many(
        180, [profile_module.get(name) for name in profile_module.PROFILES], seed=1234
    )
    assert not result.unreachable
    assert result.dead_ends == 0


# ---------------------------------------------------------------------------
# Repeatable content
# ---------------------------------------------------------------------------


def test_the_new_storylets_are_all_here(real_library):
    missing = [sid for sid in MILESTONE_2 if sid not in real_library.storylets]
    assert not missing


def test_progressive_scenes_branch_on_the_count_not_the_dice(real_library):
    """`dorm_late_night` is a progression, and progressions are ordered.

    A repeatable scene whose variants are stages -- a room stopping being
    unfamiliar -- has to read `times_seen`. Picking a stage at random is the
    Milestone 1 bug where a scene narrated the same discovery twice.
    docs/narrative-design/CONTINUITY_REVIEW.md
    """
    from s32tools import paths

    source = (paths.game_dir() / "story" / "storylets" / "residence.rpy").read_text(
        encoding="utf-8"
    )
    body = source[source.index("label s32_st_dorm_late_night:") :]
    body = body[: body.index("label s32_st_dorm_corridor_noise:")]
    assert 'times_seen("dorm_late_night")' in body
    assert "randint" not in body


def test_scenes_that_grant_knowledge_are_not_freely_repeatable(real_library):
    """Discovering the same thing twice reads as the game not paying attention.

    Anything that grants a fact must be `once`, or must have a cooldown -- in
    which case it is on the continuity review's watch list and somebody has
    read the prose.
    """
    for storylet in real_library.storylets.values():
        if storylet.grants and storylet.repeat_policy == "repeatable":
            assert storylet.cooldown, storylet.id
