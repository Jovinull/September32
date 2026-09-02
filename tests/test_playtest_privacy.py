"""The promises made to a tester, as tests.

`FEEDBACK_INSTRUCTIONS.md` tells a person that nothing is uploaded, that the
report holds no identifier, and that the game refuses to write a file that does.
Those are three claims made to somebody who cannot check them, which is the kind
of claim that has to be checkable here instead.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, cast

import pytest

from s32_engine import playtest
from s32_engine.version import PLAYTEST_REPORT_SCHEMA_VERSION
from s32tools import paths

FIXTURES = Path(__file__).parent / "fixtures" / "playtests"


@pytest.fixture(scope="module")
def synthetic() -> list[dict[str, Any]]:
    """Every readable synthetic report."""
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(FIXTURES.glob("playtest-report-synthetic-[abc].json"))
    ]


# ---------------------------------------------------------------------------
# No network, anywhere
# ---------------------------------------------------------------------------

#: Modules that would make an upload possible. `socket` is the one that matters:
#: everything else is built on it, but naming them individually means a review
#: does not have to reason about what `http.client` imports.
_NETWORK = (
    "socket",
    "ssl",
    "urllib.request",
    "urllib.error",
    "http.client",
    "httplib",
    "requests",
    "ftplib",
    "smtplib",
    "telnetlib",
    "xmlrpc",
    "asyncio",
    "webbrowser",
)

_IMPORT = re.compile(r"^\s*(?:import|from)\s+([\w.]+)", re.MULTILINE)
_URL = re.compile(r"https?://")


def _game_sources() -> list[Path]:
    """Every file the built game runs: the engine package and the Ren'Py tree."""
    engine = sorted((paths.game_dir() / "python-packages" / "s32_engine").rglob("*.py"))
    scripts = sorted(paths.game_dir().rglob("*.rpy"))
    return engine + scripts


def test_the_game_imports_nothing_that_could_reach_the_internet():
    """The claim in FEEDBACK_INSTRUCTIONS.md, as a check.

    Not "networking is disabled" -- absent. A tester is told there is no network
    code in this game, and this is what makes that a fact rather than an
    intention.
    """
    offenders: list[str] = []
    for path in _game_sources():
        text = path.read_text(encoding="utf-8")
        for module in _IMPORT.findall(text):
            root = module.split(".")[0]
            if module in _NETWORK or root in {"socket", "requests", "ssl", "asyncio"}:
                offenders.append(f"{path.name}: imports {module}")
    assert not offenders, offenders


#: The one file allowed to contain a bare URL. `credits_data.rpy` is generated
#: from the asset manifest and several bundled licences *require* the
#: attribution link to be shown. It is displayed text, never fetched -- and the
#: check above is what guarantees there is nothing in the game that could fetch
#: it.
_URLS_ALLOWED_IN = {"credits_data.rpy"}

#: Ren'Py's hyperlink markup. A `{a=...}` link is a hand-off to the player's own
#: browser, on a click they make, from the About and Help screens -- it is not
#: the game reaching anywhere, and the two that exist are Ren'Py's own stock
#: text. Allowing the markup rather than the two files means a *new* bare URL is
#: still caught.
_LINK_MARKUP = re.compile(r"\{a=https?://")


def test_no_url_is_hiding_in_a_string_the_game_could_open():
    """A URL in code is either dead weight or an upload waiting to be written.

    Comments and documentation strings are allowed to reference the web -- the
    licence notices have to. Executable lines are not, with one exception that
    is named rather than pattern-matched, so adding a second one is a decision
    somebody has to make on purpose.
    """
    offenders: list[str] = []
    for path in _game_sources():
        if path.name in _URLS_ALLOWED_IN:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("##"):
                continue
            if _LINK_MARKUP.search(stripped):
                continue
            if _URL.search(stripped):
                offenders.append(f"{path.name}:{number}: {stripped[:70]}")
    assert not offenders, offenders


def test_the_playtest_module_is_standard_library_only():
    """The engine's rule, restated for the newest module in it."""
    source = (paths.game_dir() / "python-packages" / "s32_engine" / "playtest.py").read_text(
        encoding="utf-8"
    )
    imported = {m.split(".")[0] for m in _IMPORT.findall(source)}
    assert imported <= {"__future__", "json", "re", "typing", "s32_engine"}


# ---------------------------------------------------------------------------
# The privacy check itself
# ---------------------------------------------------------------------------


def test_a_clean_report_has_no_violations(synthetic):
    for report in synthetic:
        assert playtest.privacy_violations(cast("playtest.PlaytestReport", report)) == [], report[
            "session_code"
        ]


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("scenes", "C:\\Users\\someone\\saves", "an absolute Windows path"),
        ("scenes", "/home/someone/.renpy", "an absolute POSIX path"),
        ("choices", "someone@example.com", "an email address"),
        ("choices", "192.168.1.14", "an IP address"),
        ("documents", "COMPUTERNAME", "a machine identifier"),
        ("documents", "2026-09-01T14:32", "a wall-clock timestamp"),
    ],
)
def test_a_poisoned_report_is_caught(field, value, expected):
    """Each pattern, poisoned one at a time.

    Parametrised rather than written as one report with six problems in it,
    because a single combined case passes as soon as *any* pattern fires and
    would keep passing if five of the six were deleted.
    """
    report = playtest.new_report(playtest.new_build_stamp(), "S32-TESTBC", consent=True)
    run = playtest.new_run(report, 1)
    # `field` is parametrised, so the key is not a literal and the TypedDict
    # cannot check it. The cast is the honest way to say so.
    cast("dict[str, list[str]]", run)[field].append(value)

    problems = playtest.privacy_violations(report)
    assert problems, f"{value!r} was not caught"
    assert any(expected in problem for problem in problems), problems


def test_the_forbidden_patterns_do_not_fire_on_ordinary_content():
    """The check has to be usable, which means it must not cry wolf.

    Real storylet ids, real choice ids and real document ids, none of which
    should trip anything. A privacy check that fails on ordinary data gets
    switched off within a week.
    """
    report = playtest.new_report(playtest.new_build_stamp(), "S32-TESTBC", consent=True)
    run = playtest.new_run(report, 4211)
    run["scenes"] += ["iris_the_second_box", "mara_the_long_way", "the_date"]
    run["choices"] += [
        playtest.choice_id("iris_the_second_box", 0, "Take the lid off."),
        playtest.choice_id("theo_admits_it", 2, '"You said it yourself."'),
        "travel.archive_room",
    ]
    run["documents"] += ["accession_record", "attendance_sheet_1994"]
    assert playtest.privacy_violations(report) == []


# ---------------------------------------------------------------------------
# The schema
# ---------------------------------------------------------------------------


def test_every_synthetic_report_validates(synthetic):
    for report in synthetic:
        assert playtest.validate(report) == [], report["session_code"]


def test_a_report_from_a_newer_schema_is_refused():
    """Refused, not half-read.

    A report whose schema this build does not know is a report about a
    different game, and reading the fields that happen to match would produce
    a number nobody could interpret.
    """
    future = json.loads(
        (FIXTURES / "playtest-report-synthetic-future.json").read_text(encoding="utf-8")
    )
    problems = playtest.validate(future)
    assert problems
    assert any("schema version" in p for p in problems)


def test_two_first_completed_runs_is_a_validation_error():
    """`first_completed` is what separates a first reaction from a replay.

    If two runs claimed it, every wave figure derived from it would silently
    double-count one tester.
    """
    report = playtest.new_report(playtest.new_build_stamp(), "S32-TESTBC", consent=True)
    first = playtest.new_run(report, 1)
    second = playtest.new_run(report, 2)
    playtest.complete_run(report, first)
    second["completed"] = True
    second["first_completed"] = True
    assert any("first completed" in p for p in playtest.validate(report))


def test_only_the_first_completed_run_is_marked():
    report = playtest.new_report(playtest.new_build_stamp(), "S32-TESTBC", consent=True)
    first = playtest.new_run(report, 1)
    playtest.complete_run(report, first)
    second = playtest.new_run(report, 2)
    playtest.complete_run(report, second)
    assert first["first_completed"]
    assert not second["first_completed"]
    assert playtest.validate(report) == []


def test_a_session_code_is_stable_and_shaped_like_one():
    """It is shown on screen and typed into a form by hand.

    Stability is the requirement that is easy to lose: a code derived from
    anything that changes would show the tester one value at the end of the act
    and a different one in the summary file.
    """
    assert playtest.session_code(918273) == playtest.session_code(918273)
    code = playtest.session_code(918273)
    assert code.startswith("S32-")
    assert len(code) == 10
    assert not set(code[4:]) & set("AEIOU01")


def test_different_installations_get_different_codes():
    codes = {playtest.session_code(n) for n in range(1, 4000)}
    assert len(codes) == 3999


# ---------------------------------------------------------------------------
# Choice ids
# ---------------------------------------------------------------------------


def test_a_choice_id_survives_a_typo_fix_in_the_caption():
    """Only the readable half moves.

    The storylet and the index are the stable part; the slug is the readable
    part. A caption edit changes the id visibly, which is the intent: reports
    from two builds should stop being comparable exactly when the option does.
    """
    before = playtest.choice_id("iris_the_second_box", 0, "Take the lid of.")
    after = playtest.choice_id("iris_the_second_box", 0, "Take the lid off.")
    assert before != after
    assert before.startswith("iris_the_second_box.0.")
    assert after.startswith("iris_the_second_box.0.")


def test_a_choice_id_is_never_empty():
    """An unnamed option still needs an identifier a report can group by."""
    assert playtest.choice_id("some_scene", 1, "...").endswith(".unnamed")
    assert playtest.choice_id("some_scene", 1, "").endswith(".unnamed")


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def test_the_report_serialises_deterministically(synthetic):
    """Two dumps of the same report are byte-identical.

    Milestone 3's credits gate failed every midnight because a generated file
    embedded the wall clock. Nothing in a report may vary between two readings
    of the same data.
    """
    for report in synthetic:
        typed = cast("playtest.PlaytestReport", report)
        assert playtest.to_json(typed) == playtest.to_json(typed)


def test_the_summary_says_what_the_json_says(synthetic):
    """A tester is asked to read the summary before sending the JSON.

    That only means anything if the two describe the same session.
    """
    for report in synthetic:
        text = playtest.summary_markdown(cast("playtest.PlaytestReport", report))
        assert report["session_code"] in text
        assert report["build"]["game_version"] in text
        for run in report["runs"]:
            if run["first_completed"]:
                assert "first completed run" in text
        for scene in report["runs"][0]["scenes"]:
            assert scene in text


def test_the_summary_contains_no_wall_clock(synthetic):
    for report in synthetic:
        text = playtest.summary_markdown(cast("playtest.PlaytestReport", report))
        assert not re.search(r"\d{4}-\d{2}-\d{2}", text)


def test_the_schema_version_matches_the_engine(synthetic):
    for report in synthetic:
        assert report["playtest_report_schema_version"] == PLAYTEST_REPORT_SCHEMA_VERSION


# ---------------------------------------------------------------------------
# Fixtures are never mistaken for people
# ---------------------------------------------------------------------------


def test_every_fixture_says_it_is_synthetic():
    """A fixture that could be read as a tester is a fixture that will be.

    Two independent marks -- the session code and a note -- because one of them
    will eventually be copied off in a summary without the other.
    """
    for path in sorted(FIXTURES.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert "SYNTH" in raw["session_code"], path.name
        assert "SYNTHETIC" in raw["note"], path.name


def test_real_feedback_is_not_in_version_control():
    """Real feedback stays out of version control.

    `playtests/raw/` is where people's words go, and it is gitignored.
    """
    ignore = (paths.repo_root() / ".gitignore").read_text(encoding="utf-8")
    assert "playtests/raw/" in ignore
    tracked = (
        list((paths.repo_root() / "playtests" / "raw").glob("*"))
        if (paths.repo_root() / "playtests" / "raw").exists()
        else []
    )
    assert all(p.name.startswith(".") for p in tracked), tracked
