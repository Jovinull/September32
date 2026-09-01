"""The calendar: derivation, privacy, and the impossible date it must survive.

The screen is covered by ``game/testcases/calendar.rpy``, which drives it the
way a player does. What lives here is everything that can be settled without
Ren'Py: that the view is derived rather than stored, that it shows only what the
protagonist knows, and that nothing in it parses a date.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from s32_engine import calendar as cal
from s32_engine.commitments import make as make_commitment
from s32_engine.state import advance_time, new_state, record_storylet

TITLES = {"intro": "Intro", "ambient": "Ambient", "followup": "Follow-up"}


@pytest.fixture
def run(library):
    """A run state a few days in, with something in its history."""
    state = new_state(library, seed=7)
    record_storylet(state, "intro")
    advance_time(state, 7)  # one whole day
    record_storylet(state, "ambient")
    return state


# ---------------------------------------------------------------------------
# It is a view, not a second copy
# ---------------------------------------------------------------------------


def test_the_calendar_stores_nothing(library):
    """The property the whole design rests on.

    A second place to keep what day it is would eventually disagree with the
    first, and a player has no way to tell which one is lying.
    """
    state = new_state(library, seed=1)
    before = dict(state)

    cal.month_view(state, TITLES)

    assert set(state) == set(before)
    assert "calendar" not in state


def test_today_follows_world_state(run):
    assert cal.day_state(run, run["world"]["calendar_day"]) == "today"
    advance_time(run, 7)
    assert cal.day_state(run, run["world"]["calendar_day"]) == "today"


def test_days_sort_into_past_today_and_future(run):
    today = run["world"]["calendar_day"]
    assert cal.day_state(run, today - 1) == "past"
    assert cal.day_state(run, today) == "today"
    assert cal.day_state(run, today + 1) == "future"


# ---------------------------------------------------------------------------
# Dates are labels
# ---------------------------------------------------------------------------


def test_the_month_after_the_thirtieth_still_has_weekdays():
    """The premise, as a unit test.

    A date layer that raises on the thirty-second of September would fail on
    exactly the day this game is named after. Nothing here validates a day
    number against a real calendar, so day 32 has a weekday for the same reason
    day 12 does.
    """
    assert cal.weekday_of(32) in cal.WEEKDAYS
    assert cal.weekday_of(31) in cal.WEEKDAYS
    assert cal.weekday_of(365) in cal.WEEKDAYS


def test_weekdays_repeat_every_seven_days():
    assert cal.weekday_of(1) == cal.weekday_of(8) == cal.weekday_of(29)
    assert cal.weekday_of(32) == cal.weekday_of(4)


def test_day_one_is_the_day_the_arrival_scene_says_it_is():
    """The arrival scene fixes it: you are the only person arriving on a Sunday."""
    assert cal.weekday_of(1) == "Sunday"


def test_the_calendar_module_never_imports_a_date_library():
    """Checked against the source, not by hope.

    This is the one constraint that would be quietly broken by somebody being
    helpful: importing `datetime` to get a weekday is the obvious move, and it
    is the move that makes September 32 unrepresentable.
    """
    source = pathlib.Path(cal.__file__).read_text(encoding="utf-8")
    forbidden = {"datetime", "calendar", "time", "zoneinfo"}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names = {(node.module or "").split(".")[0]}
        else:
            continue
        assert not (forbidden & names), f"{names} would make an impossible date unrepresentable"


# ---------------------------------------------------------------------------
# What the protagonist knows
# ---------------------------------------------------------------------------


def test_a_played_scene_appears_on_the_day_it_played(run):
    entries = cal.month_view(run, TITLES)
    first = next(e for e in entries if e["run_day"] == 1)
    assert "Intro" in first["events"]


def test_a_future_day_carries_no_scenes(run):
    entries = cal.month_view(run, TITLES)
    for entry in entries:
        if entry["state"] == "future":
            assert entry["events"] == []


def test_an_open_promise_appears_on_its_due_day(run):
    make_commitment(
        run,
        "walk_with_june",
        kind="meeting",
        participants=["june"],
        due_day=run["world"]["day"] + 2,
    )
    due = run["world"]["calendar_day"] + 2

    entry = next(e for e in cal.month_view(run, TITLES) if e["calendar_day"] == due)

    assert "walk_with_june" in entry["commitments"]
    assert entry["state"] == "future"


def test_a_resolved_promise_leaves_the_future(run):
    """A promise you have kept is part of what happened, not what is coming."""
    from s32_engine.commitments import fulfil

    make_commitment(
        run,
        "walk_with_june",
        kind="meeting",
        participants=["june"],
        due_day=run["world"]["day"] + 2,
    )
    due = run["world"]["calendar_day"] + 2
    fulfil(run, "walk_with_june")

    entry = next(e for e in cal.month_view(run, TITLES) if e["calendar_day"] == due)

    assert entry["commitments"] == []


def test_the_view_cannot_see_content_the_player_has_not_reached(run, library):
    """The privacy rule, held structurally rather than by filtering.

    `month_view` is given a title lookup and the run state. It is never given
    the content library, so a scene scheduled for a later day is not something
    it could put on a square even by mistake.
    """
    entries = cal.month_view(run, TITLES)
    shown = {title for entry in entries for title in entry["events"]}
    played = {TITLES[record["id"]] for record in run["history"]}

    assert shown == played
    # `followup` exists in the library and has never played.
    assert "followup" in library.storylets
    assert "Follow-up" not in shown


# ---------------------------------------------------------------------------
# The grid
# ---------------------------------------------------------------------------


def test_the_month_has_one_entry_per_day(run):
    entries = cal.month_view(run, TITLES)
    assert len(entries) == cal.MONTH_LENGTH
    assert [e["calendar_day"] for e in entries] == list(range(1, cal.MONTH_LENGTH + 1))


def test_every_entry_has_a_readable_summary(run):
    """The grid marks days by tint and by a word. This is the word, as a line."""
    for entry in cal.month_view(run, TITLES):
        line = cal.summary_line(entry)
        assert str(entry["calendar_day"]) in line
        assert entry["weekday"] in line
