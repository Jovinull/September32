"""Milestone 4: the things the editorial pass is supposed to have fixed.

Deliberately not a test of writing quality. What can be held here is that the
structural findings stay fixed: that relationships are read and not only
written, that the choice vocabulary has not collapsed back into one shape, and
that the scenes which now depend on relationship state can actually reach it.

The prose itself goes to a human. `docs/production/HUMAN_ACT1_REVIEW.md`.
"""

from __future__ import annotations

import collections
import re

import pytest

from s32tools import paths
from s32tools.simulation import profiles as profile_module
from s32tools.simulation.simulator import Simulator

#: Every `.rpy` under game/story, as one blob per label.
STORY = paths.game_dir() / "story"


def _labels() -> dict[str, str]:
    """Return every Ren'Py label body in the story tree, keyed by label name."""
    bodies: dict[str, str] = {}
    for path in sorted(STORY.rglob("*.rpy")):
        text = path.read_text(encoding="utf-8")
        for block in re.split(r"^label ", text, flags=re.M)[1:]:
            bodies[block.split(":")[0].strip()] = block
    return bodies


@pytest.fixture(scope="module")
def labels() -> dict[str, str]:
    return _labels()


# ---------------------------------------------------------------------------
# Relationships are read, not only written
# ---------------------------------------------------------------------------

#: Scenes that must behave differently depending on relationship state.
#:
#: A list rather than a threshold, because the point is that these particular
#: scenes read state -- a count would be satisfied by adding a token `if` to
#: something that did not need one.
READS_STATE = (
    "s32_st_courtyard_small_talk",
    "s32_st_iris_the_second_box",
    "s32_st_theo_admits_it",
    "s32_st_the_saturday",
    "s32_st_mara_the_long_way",
    "s32_st_june_reads_it_flat",
    "s32_st_archive_theo_returns",
    "s32_st_dorm_late_night",
    "s32_st_hallway_encounter",
)

_READING = re.compile(r"\b(stance|regards|player_regards|rel_get)\s*\(")


def test_the_named_scenes_read_relationship_state(labels):
    """Before Milestone 4 this list was empty and the count was zero.

    Fifty-one storylets wrote to eight axes and no line of prose anywhere read
    one back, which is the difference between building a relationship and
    accumulating a variable.
    """
    missing = [name for name in READS_STATE if not _READING.search(labels.get(name, ""))]
    assert not missing


def test_relationship_reads_are_not_concentrated_in_one_file(labels):
    """A reading habit, not one clever scene.

    Nine scenes across five files; if they all lived in one, the next writer
    would read it as that file's trick rather than as how this project works.
    """
    files: collections.Counter[str] = collections.Counter()
    for path in sorted(STORY.rglob("*.rpy")):
        text = path.read_text(encoding="utf-8")
        if _READING.search(text):
            files[path.name] = len(_READING.findall(text))
    assert len(files) >= 4, files


def test_no_scene_shows_the_player_a_number(labels):
    """The player should feel a relationship change and be unable to quote it.

    Catches the obvious regression: interpolating a `rel_get` straight into a
    line of narration.
    """
    for name, body in labels.items():
        for line in body.splitlines():
            if re.match(r"\s+(narrator|c_\w+) ", line) and _READING.search(line):
                raise AssertionError(f"{name}: relationship value inside a spoken line: {line!r}")


# ---------------------------------------------------------------------------
# The choice vocabulary
# ---------------------------------------------------------------------------

_TRAIT = re.compile(r'\$ trait\("([a-z_]+)"')


def _menu_trait_sets(labels: dict[str, str]) -> list[frozenset[str]]:
    """Return the set of traits each menu in the game offers."""
    sets: list[frozenset[str]] = []
    for body in labels.values():
        for menu in re.split(r"^    menu:", body, flags=re.M)[1:]:
            options = re.split(r'^        "', menu, flags=re.M)[1:]
            sets.append(frozenset((_TRAIT.findall(o) or ["-"])[0] for o in options))
    return sets


def test_the_choice_vocabulary_has_not_collapsed(labels):
    """Milestone 4's second finding, held.

    Three trait sets -- {gentle, curious, reserved}, {gentle, curious, direct},
    {gentle, direct, reserved} -- accounted for 21 of 42 menus, which is the
    same question asked half the time in different scenery. This does not
    demand variety it cannot define; it fails if any single set takes over.
    """
    sets = _menu_trait_sets(labels)
    counts = collections.Counter(sets)
    most_common, n = counts.most_common(1)[0]
    assert n / len(sets) < 0.20, f"{sorted(most_common)} is {n}/{len(sets)} of all menus"


def test_menus_are_not_all_the_same_size(labels):
    """38 of 42 menus had exactly three options.

    Three is a fine number for a menu and a suspicious number for every menu:
    it means the option count is a template rather than a decision about the
    scene.
    """
    sizes = collections.Counter(len(s) for s in _menu_trait_sets(labels))
    assert len(sizes) >= 2, sizes
    assert max(sizes.values()) / sum(sizes.values()) < 0.95, sizes


def test_choice_text_is_behaviour_rather_than_a_label(labels):
    """A choice that names its own consequence is not a choice.

    Catches the `[Be kind to Iris]` shape and the bare opt-out. "Say nothing"
    survives where it is a real move in a scene about not intervening; the
    banned forms are the ones that describe leaving rather than doing.
    """
    banned = ("Leave it.", "Leave him to it.", "Walk on.", "Keep walking.", "Be nice", "Be rude")
    for name, body in labels.items():
        for text in re.findall(r'^        "([^"]+)"', body, flags=re.M):
            for phrase in banned:
                assert phrase not in text, f"{name}: opt-out choice text {text!r}"


# ---------------------------------------------------------------------------
# The state those scenes read has to be reachable
# ---------------------------------------------------------------------------


def test_every_relationship_state_a_scene_branches_on_is_reachable(real_library):
    """A `wary` branch nobody can reach is a branch nobody will read.

    Runs a short sweep and asserts that each of the four stances the writing
    distinguishes actually occurs for at least one character in at least one
    run. `distant` is trivially reachable; `wary` and `close` are the ones
    worth checking, and `wary` is the one the eight axes exist for.
    """
    simulator = Simulator(real_library)
    names = list(profile_module.PROFILES)
    seen: set[str] = set()

    for index in range(90):
        run = simulator.run_once(1234 + index, profile_module.PROFILES[names[index % len(names)]])
        for who in ("iris", "june", "mara", "theo", "noah"):
            vector = run.relationships.get(f"{who}->player", {})
            trust = vector.get("trust", 0)
            familiarity = vector.get("familiarity", 0)
            against = max(vector.get("suspicion", 0), vector.get("resentment", 0))
            if against >= 4 and against * 2 >= trust:
                seen.add("wary")
            elif trust >= 18 and familiarity >= 12:
                seen.add("close")
            elif familiarity >= 8 or trust >= 8:
                seen.add("comfortable")
            else:
                seen.add("distant")

    assert {"wary", "close", "comfortable"} <= seen, seen


# ---------------------------------------------------------------------------
# The cut, and the commitment that moved with it
# ---------------------------------------------------------------------------


def test_the_cut_scene_is_gone_everywhere(real_library):
    """The cut, held.

    `june_needs_saturday` asked for a Saturday that `hallway_after_bell` had
    already spent three pages arranging.
    """
    assert "june_needs_saturday" not in real_library.storylets
    for path in sorted(STORY.rglob("*.rpy")):
        text = path.read_text(encoding="utf-8")
        assert "label s32_st_june_needs_saturday" not in text


def test_the_saturday_promise_is_still_makeable(real_library, labels):
    """The commitment moved into the group scene rather than being deleted."""
    made_in = [
        sid
        for sid, s in real_library.storylets.items()
        for branch in (s.outcomes or ())
        for effect in branch
        if effect.startswith("commit(saturday_with_june")
    ]
    assert "hallway_after_bell" in made_in
    assert 'promise("saturday_with_june"' in labels["s32_st_hallway_after_bell"]


def test_the_promise_is_still_resolvable(real_library):
    """Both halves, so a commitment cannot become a thing that only accrues."""
    resolutions = {
        effect.split("(")[0]
        for branch in real_library.storylets["the_saturday"].outcomes
        for effect in branch
        if effect.startswith(("fulfil(", "break("))
    }
    assert resolutions == {"fulfil", "break"}


# ---------------------------------------------------------------------------
# Declared outcomes still match the menus that produce them
# ---------------------------------------------------------------------------


def test_declared_outcomes_match_the_number_of_menu_options(real_library, labels):
    """Trimming an option means trimming its declared branch.

    Milestone 4 cut a third option from two scenes. A declared outcome with no
    menu option behind it is a state change the simulator believes in and no
    player can produce.
    """
    mismatches = []
    for sid, storylet in real_library.storylets.items():
        body = labels.get(storylet.label, "")
        menus = re.split(r"^    menu:", body, flags=re.M)[1:]
        if len(menus) != 1 or not storylet.outcomes:
            continue
        options = len(re.split(r'^        "', menus[0], flags=re.M)[1:])
        if options != len(storylet.outcomes):
            mismatches.append(f"{sid}: {options} options, {len(storylet.outcomes)} outcomes")
    assert not mismatches


# ---------------------------------------------------------------------------
# The documentation this milestone is accountable to
# ---------------------------------------------------------------------------


def test_the_act_one_documents_exist_and_are_not_stubs():
    """The documents this milestone is accountable to.

    Cheap, and it catches the thing that actually happens: a document
    referenced from three other documents that was never written.
    """
    required = {
        "docs/narrative-design/ACT_1_EDITORIAL_AUDIT.md": 3000,
        "docs/narrative-design/ACT_1_CHARACTER_ARCS.md": 3000,
        "docs/narrative-design/ACT_1_MYSTERY_LEDGER.md": 3000,
        "docs/narrative-design/RELATIONSHIP_SEMANTICS.md": 3000,
        "docs/narrative-design/CHARACTER_NETWORK_ACT1.md": 2000,
        "docs/characters/PROTAGONIST.md": 2000,
        "docs/production/ART_PRODUCTION_PLAN.md": 2000,
        "docs/production/CLASS_PHOTO_ART_BRIEF.md": 2000,
        "docs/production/CHARACTER_ART_BRIEF.md": 2000,
    }
    for name, floor in required.items():
        path = paths.repo_root() / name
        assert path.exists(), name
        assert len(path.read_text(encoding="utf-8")) >= floor, f"{name} is a stub"


def test_every_new_scene_names_the_gap_it_fills(real_library):
    """The audit's rule: new scenes fill functions, not cells.

    Held by requiring a real summary. A storylet whose summary is one sentence
    is one nobody justified.
    """
    thin = [
        sid
        for sid, s in real_library.storylets.items()
        if s.status == "draft" and len(s.summary) < 120
    ]
    assert not thin


def test_the_storylet_count_moved_deliberately(real_library):
    counts = collections.Counter(s.status for s in real_library.storylets.values())
    assert counts["draft"] >= 40
    assert sum(counts.values()) == len(real_library.storylets)
