"""Act 1 is reachable by a player, not only by the simulator.

Milestone 5 found that it was not. The game's `start` label played six time
slots on the first day and stopped with a line saying it was a prototype, so
three of the five anchors -- the common room, the undated column, and the date
itself -- had never once fired outside the headless simulator. Fifty-eight
storylets and a seven-day structure were reachable on paper and unreachable in
the game, and every gate was green.

These tests are about the loop that fixes that. The Ren'Py side is covered by
`game/testcases/act1.rpy`, which plays a real week; what is held here is the
structure, and the §61 golden-path checklist run headlessly so that it is
checked on every commit rather than only when somebody runs the SDK.
"""

from __future__ import annotations

import re

import pytest

from s32_engine.definitions import load_library
from s32tools import paths
from s32tools.simulation import profiles as profile_module
from s32tools.simulation.simulator import Simulator

ACT1 = paths.game_dir() / "story" / "act1.rpy"


@pytest.fixture(scope="module")
def act1() -> str:
    return ACT1.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# The loop exists and is the only entry point
# ---------------------------------------------------------------------------


def test_there_is_exactly_one_start_label():
    """Two would be a Ren'Py error; zero would be a game that does not launch.

    Worth asserting because the fix for this milestone deleted one `start` and
    added another, in different files.
    """
    starts = [
        f"{path.name}:{number}"
        for path in sorted(paths.game_dir().rglob("*.rpy"))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if line.strip() == "label start:"
    ]
    assert len(starts) == 1, starts


def test_the_prototype_slice_is_gone():
    """It ended after six time slots and said so on screen.

    A tester who received that build would have finished in ten minutes,
    having met two characters and none of the mystery, and every question on
    the questionnaire would have been unanswerable.
    """
    tree = " ".join(
        path.read_text(encoding="utf-8") for path in sorted(paths.game_dir().rglob("*.rpy"))
    )
    assert "s32_prototype_loop" not in tree
    assert "end of the prototype slice" not in tree


def test_the_week_runs_until_the_last_anchor(act1):
    """The act ends on `the_date` and on nothing else.

    Not a slot count, not a day count: the loop's exit condition is the last
    anchor, so a change to the pacing cannot accidentally end the act before
    its ending.
    """
    assert 'while "the_date" not in S32State["anchors_done"]' in act1


def test_the_loop_asks_for_an_anchor_before_it_asks_the_director(act1):
    """Anchors are mandatory and ordered; a ready one outranks every storylet.

    Ordering it the other way would leave the anchor waiting behind whatever
    ambient scene happened to be eligible, and the day gates would push the
    whole act later every time it happened.
    """
    anchor = act1.index("s32_ready_anchor()")
    select = act1.index("s32_select()")
    assert anchor < select


def test_the_loop_does_not_choose_for_the_player(act1):
    """The player moves; the director selects. Neither does the other's job.

    Specifically: nothing in the loop scores, filters or re-picks a storylet.
    The selection algorithm has not changed since Milestone 1 and the loop is
    the newest place it could start to.
    """
    code = "\n".join(line for line in act1.splitlines() if not line.strip().startswith("#"))
    for forbidden in ("weighted_choice", "priority", "eligible", "profile", "s32_director"):
        assert forbidden not in code, forbidden


def test_the_loop_has_a_bound(act1):
    """A content bug must stop, not spin in front of a tester."""
    assert re.search(r"_s32_steps < \d+", act1)


def test_every_anchor_label_is_reached_through_the_library(act1):
    """The loop calls `s32_anchor_label(id)` rather than naming labels.

    A hard-coded list is how the last three anchors came to be unreachable:
    the prototype called two of them by name and nothing called the rest.
    """
    assert "s32_anchor_label(_s32_anchor)" in act1
    named = re.findall(r"call (s32_anchor_\w+)", act1)
    assert set(named) == {"s32_anchor_arrival", "s32_anchor_first_shift"}


def test_the_travel_menu_offers_only_places_with_something_in_them(act1):
    """A menu that offers nine empty corridors teaches a player not to read it."""
    assert act1.count("s32_places_with_content()") == 2


def test_the_completion_screen_shows_no_progress_figures():
    """§62. No "scenes seen", no route percentage, no character percentage.

    A completion figure turns a first playthrough into a checklist and makes
    the second one -- the one we explicitly do not want yet -- feel owed.
    """
    screen = (paths.game_dir() / "screens" / "playtest.rpy").read_text(encoding="utf-8")
    complete = screen[screen.index("screen s32_act1_complete") :]
    complete = complete[: complete.index("screen s32_feedback_instructions")]
    for forbidden in ("%", "len(", "scenes", "S32State"):
        assert forbidden not in complete, forbidden


# ---------------------------------------------------------------------------
# The golden path, headless
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def golden():
    """One deterministic week, played through the engine.

    The same checklist `act1_golden` runs in Ren'Py, run here so that it is
    checked on every commit rather than only when somebody has the SDK. What
    this cannot see is the prose: no `.rpy` is executed. That is the testcase's
    job and the two are not substitutes.
    """
    library = load_library(paths.data_dir())
    simulator = Simulator(library)
    return simulator.run_once(1234, profile_module.get("curious"), max_days=8)


def test_the_golden_path_completes_act_one(golden):
    assert "the_date" in golden.anchors_reached
    assert len(golden.anchors_reached) == 5


def test_the_golden_path_reaches_day_seven(golden):
    """§61. The week is seven days and the last anchor is gated on day six."""
    assert golden.days >= 7


def test_the_golden_path_learns_what_the_act_is_about(golden):
    assert "photo_dated_sept_32" in golden.knowledge_gained
    assert "attendance_sheet_anomaly" in golden.knowledge_gained


def test_the_golden_path_ends_inside_the_odd_phase(golden):
    """Act 1 deliberately does not escalate past `odd`.

    `unsettling` is the second and third thing and belongs to Act 2. A week
    that ended in `unsettling` would have spent Act 2's budget in Act 1.
    """
    assert golden.final_phase == "odd"


def test_the_golden_path_makes_a_promise(golden):
    """§61's checklist item, and the one most easily lost.

    A commitment that stops being made produces no error anywhere: the
    calendar simply has nothing on it and the scene that resolves it never
    fires.
    """
    assert golden.commitments


def test_the_golden_path_is_a_week_and_not_a_handful_of_scenes(golden):
    assert len(golden.storylets_played) >= 30
    assert len(set(golden.storylets_played)) >= 20


def test_the_golden_path_is_deterministic():
    """Same seed, same profile, same week.

    Which is what makes "it happened on seed 1234" a complete bug report.
    """
    library = load_library(paths.data_dir())
    first = Simulator(library).run_once(1234, profile_module.get("curious"), max_days=8)
    second = Simulator(library).run_once(1234, profile_module.get("curious"), max_days=8)
    assert first.storylets_played == second.storylets_played
    assert first.knowledge_gained == second.knowledge_gained


def test_the_act_ends_within_a_week_for_every_profile():
    """Not just the profile the golden path uses.

    A tester who plays like `selfish` or `reserved` must still reach the end of
    the act; the anchors are mandatory, so failing here would mean a day gate
    somewhere is unreachable for a way of playing.
    """
    library = load_library(paths.data_dir())
    simulator = Simulator(library)
    for name in profile_module.PROFILES:
        run = simulator.run_once(4211, profile_module.get(name), max_days=10)
        assert "the_date" in run.anchors_reached, name


# ---------------------------------------------------------------------------
# What a tester is in for
# ---------------------------------------------------------------------------


def _words_in_labels() -> dict[str, int]:
    """Return the spoken word count of every storylet and anchor label."""
    spoken = re.compile(r'^\s*(?:narrator|centered|c_\w+)\s+"(.*)"\s*$')
    counts: dict[str, int] = {}
    for path in sorted((paths.game_dir() / "story").rglob("*.rpy")):
        text = path.read_text(encoding="utf-8")
        for block in re.split(r"^label ", text, flags=re.M)[1:]:
            name = block.split(":")[0].strip()
            counts[name] = sum(
                len(match.group(1).split())
                for line in block.splitlines()
                if (match := spoken.match(line))
            )
    return counts


def test_a_playthrough_is_the_length_the_readme_says_it_is(golden):
    """§35. The estimate given to testers has to come from the content.

    Roughly 240 words a minute for prose somebody is reading rather than
    skimming, and the count is the *spoken* half only -- a run also spends time
    on menus, travel and the day cards, which is why the README gives a range
    rather than a number.
    """
    words = _words_in_labels()
    played = [f"s32_st_{sid}" for sid in golden.storylets_played]
    played += [f"s32_anchor_{aid}" for aid in golden.anchors_reached]
    total = sum(words.get(name, 0) for name in played)

    # A floor and a ceiling, both wide. This is not a target: it fails when a
    # playthrough stops being an evening's reading in either direction, which
    # is when the README's estimate stops being honest.
    assert 6000 <= total <= 20000, total

    readme = (paths.repo_root() / "PLAYTEST_README.md").read_text(encoding="utf-8")
    assert "hour" in readme
