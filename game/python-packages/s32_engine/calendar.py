"""The calendar, as a view of the run rather than a second copy of it.

This module owns no state. Every value it returns is derived from
``state["world"]``, ``state["commitments"]`` and ``state["history"]`` at the
moment it is called. There is deliberately no ``calendar`` key in
:class:`~s32_engine.types.GameState`: a second place to store what day it is
would eventually disagree with the first, and the bug that produces is invisible
until somebody reads a date out loud in a scene.

**Dates here are labels, not arithmetic.** ``calendar_day`` is an integer and
``month`` is a string, and neither goes through :mod:`datetime` at any point.
That is not laziness. A game whose premise is a September with more days than
September has cannot afford a date layer that raises ``ValueError`` on the day
it becomes interesting. Nothing in this file rejects a day number, and
:func:`weekday_of` is arithmetic on an offset rather than a lookup in a real
calendar, so day 32 has a weekday for the same reason day 12 does.

None of that is visible to the player yet, and must not be. The first-phase
calendar looks like a school calendar because it is one.

**What the player knows is not what the world knows.** :func:`month_view` reads
only what the protagonist has actually done or been told -- history and their
own promises. It never consults the content library, so a scene that is going to
happen on Thursday cannot leak into Tuesday's square. This is a structural
guarantee rather than a filter: the future information is not in scope here.
"""

from __future__ import annotations

from typing import Literal, TypedDict

from s32_engine.types import GameState

#: Weekday names, in the order the fiction uses them.
#:
#: Index 0 is the weekday of ``calendar_day`` 1, which the arrival scene fixes
#: as a Sunday: "You're the only person arriving on a Sunday." Changing the
#: start date means changing :data:`WEEKDAY_OFFSET`, not this tuple.
WEEKDAYS: tuple[str, ...] = (
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
)

#: Which entry of :data:`WEEKDAYS` ``calendar_day`` 1 falls on.
WEEKDAY_OFFSET = 0

#: How many day squares a month view holds.
#:
#: Thirty, because September has thirty. The number is a constant rather than a
#: literal so that the day this has to change, it changes in one place and the
#: grid follows. Nothing here validates it against a real calendar, and nothing
#: should.
MONTH_LENGTH = 30

DayState = Literal["past", "today", "future"]


class DayEntry(TypedDict):
    """One square. Everything on it is something the protagonist knows."""

    calendar_day: int
    weekday: str
    state: DayState
    #: Run day, or 0 for a day the run has not reached.
    run_day: int
    #: Titles of scenes that played on this day, in the order they played.
    events: list[str]
    #: Commitments falling due on this day that are still open.
    commitments: list[str]
    #: A short line for a day with nothing else on it, or "".
    annotation: str


def weekday_of(calendar_day: int) -> str:
    """Return the weekday name for a calendar day.

    Deliberately modular arithmetic on an integer. A day number this function
    would refuse is a day the story is not allowed to have, and the story has
    not decided that yet.
    """
    return WEEKDAYS[(calendar_day - 1 + WEEKDAY_OFFSET) % len(WEEKDAYS)]


def day_state(state: GameState, calendar_day: int) -> DayState:
    """Return whether a day is behind, current, or ahead of the run."""
    today = state["world"]["calendar_day"]
    if calendar_day < today:
        return "past"
    return "today" if calendar_day == today else "future"


def _run_day_for(state: GameState, calendar_day: int) -> int:
    """Map a calendar day onto the run's own day counter.

    The two move together -- ``advance_time`` increments both -- so this is a
    fixed offset rather than a search. It is a function anyway, because "the
    two always move together" is exactly the kind of thing that stops being
    true when somebody adds a scene that skips a day.
    """
    world = state["world"]
    offset = world["day"] - world["calendar_day"]
    return calendar_day + offset


def events_on(state: GameState, calendar_day: int, titles: dict[str, str]) -> list[str]:
    """Return the titles of scenes the player played on a calendar day.

    Args:
        state: Run state.
        calendar_day: The day to look up, as a label rather than a date.
        titles: Storylet id to display title. Passed in rather than looked up,
            so this module never touches the content library and therefore
            cannot accidentally reach a scene that has not happened.
    """
    run_day = _run_day_for(state, calendar_day)
    seen: list[str] = []
    for record in state["history"]:
        if record["day"] != run_day:
            continue
        title = titles.get(record["id"])
        if title and title not in seen:
            seen.append(title)
    return seen


def commitments_on(state: GameState, calendar_day: int) -> list[str]:
    """Return open promises falling due on a calendar day.

    Only ``active`` ones. A promise the player has already kept or broken is
    part of what happened, not part of what is coming, and putting it on a
    future square would be the calendar telling them something they have not
    done yet.
    """
    run_day = _run_day_for(state, calendar_day)
    return [
        record["id"]
        for record in state["commitments"]
        if record["status"] == "active" and record["due_day"] == run_day
    ]


def month_view(state: GameState, titles: dict[str, str] | None = None) -> list[DayEntry]:
    """Return one entry per day of the current month.

    The whole month, including days the run has not reached, because a calendar
    that only shows the past is a diary. Future squares carry a weekday and
    anything the protagonist has promised, and nothing else.
    """
    titles = titles or {}
    entries: list[DayEntry] = []
    for calendar_day in range(1, MONTH_LENGTH + 1):
        where = day_state(state, calendar_day)
        events = events_on(state, calendar_day, titles) if where != "future" else []
        entries.append(
            DayEntry(
                calendar_day=calendar_day,
                weekday=weekday_of(calendar_day),
                state=where,
                run_day=_run_day_for(state, calendar_day) if where != "future" else 0,
                events=events,
                commitments=commitments_on(state, calendar_day),
                annotation="",
            )
        )
    return entries


def summary_line(entry: DayEntry) -> str:
    """Return a one-line reading of a square, for a screen reader or a log.

    Exists because the grid distinguishes days by colour and by a mark, and a
    mark is not enough on its own: this is the text a caller can read out.
    """
    parts = [f"{entry['weekday']} {entry['calendar_day']}"]
    if entry["state"] == "today":
        parts.append("today")
    elif entry["state"] == "future":
        parts.append("not yet")
    if entry["commitments"]:
        parts.append(f"{len(entry['commitments'])} promised")
    if entry["events"]:
        parts.append(f"{len(entry['events'])} recorded")
    return ", ".join(parts)
