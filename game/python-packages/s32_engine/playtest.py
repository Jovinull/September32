"""The private playtest report: what a tester's session did, and nothing else.

This is the only part of September 32 that writes a file describing a person's
play. It exists because five milestones of tests, simulations and static
analysis cannot answer the one question left -- whether anybody enjoys the
week -- and because a questionnaire answered from memory is worth more when it
can be read beside what actually happened.

Three rules shape everything here, and each of them is held by a test:

**Local only.** Nothing in this module opens a socket, and nothing above it
does either. The report is written next to the player's saves and stays there
until they choose to send it. ``docs/legal/PRIVACY.md``.

**Identifiers, not identity.** The report holds storylet ids, choice ids,
counts and elapsed seconds. It holds no name, no path, no hostname, no clock
reading. :func:`privacy_violations` is the executable statement of that: it
walks a finished report and reports anything that looks like a person or a
machine, and the test suite fails on a non-empty result.

**No wall clock.** Durations are accumulated elapsed seconds supplied by the
caller; no absolute time is stored. That keeps a report reproducible from a
fixture, and it also means the file cannot say when somebody was awake.

The session code is the join key. A tester writes it at the top of the
questionnaire, and it is derived from a per-installation number that has no
relationship to the machine it was generated on.
"""

from __future__ import annotations

import json
import re
from typing import Any, TypedDict

from s32_engine.version import (
    GAME_VERSION,
    PLAYTEST_REPORT_SCHEMA_VERSION,
    SAVE_SCHEMA_VERSION,
)

#: Alphabet for session codes. No vowels, so a code cannot spell anything, and
#: no 0/O or 1/I, because these get read aloud and typed into a form by hand.
_CODE_ALPHABET = "BCDFGHJKMNPQRSTVWXYZ23456789"

#: Characters in the code after the prefix. Six from a 28-character alphabet is
#: about 481 million codes -- far beyond what a private wave needs, and short
#: enough to copy without resenting it.
_CODE_LENGTH = 6

#: What every session code starts with, so a tester can recognise one in a
#: message and knows which game it came from.
_CODE_PREFIX = "S32-"


class BuildStamp(TypedDict):
    """Which build produced a report. Recorded so feedback can be attributed."""

    game_version: str
    build_id: str
    commit: str
    save_schema_version: int
    playtest_report_schema_version: int


class RunRecord(TypedDict):
    """One playthrough, from ``Start`` to wherever it stopped."""

    index: int
    seed: int
    completed: bool
    #: True for the first run in this session that reached the end of Act 1.
    #: A first reaction and a replay are different evidence and must not be
    #: averaged together.
    first_completed: bool
    days_reached: int
    active_seconds: int
    scenes: list[str]
    anchors: list[str]
    choices: list[str]
    documents: list[str]
    calendar_opens: int
    journal_opens: int
    archive_reopens: int
    commitments_made: list[str]
    commitments_kept: list[str]
    commitments_broken: list[str]
    #: Loads only. Ren'Py fires ``after_load`` however a save is restored, so
    #: this is reliable. There is no equivalent hook for saving or for
    #: rollback: every save path also carries the autosave Ren'Py forces at
    #: each choice, and rollback can be driven by the mouse wheel, a keysym or
    #: an action. A field that is silently wrong is worse than a field that is
    #: absent, so neither is recorded.
    loads: int


class PlaytestReport(TypedDict):
    """Everything one tester's installation has recorded."""

    playtest_report_schema_version: int
    build: BuildStamp
    session_code: str
    consent: bool
    runs: list[RunRecord]


# ---------------------------------------------------------------------------
# Session codes
# ---------------------------------------------------------------------------


def session_code(install_id: int) -> str:
    """Derive a stable, non-identifying session code from an installation number.

    Deterministic, so the same installation always shows the tester the same
    code however many times they open the completion screen -- a code that
    changed between two readings would be worse than no code at all.

    ``install_id`` is a number this game generated once and stored beside the
    player's saves. It is not derived from the machine, so the code cannot be
    walked back to a device.
    """
    value = abs(int(install_id))
    base = len(_CODE_ALPHABET)
    letters = []
    for _ in range(_CODE_LENGTH):
        letters.append(_CODE_ALPHABET[value % base])
        value //= base
    return _CODE_PREFIX + "".join(letters)


# ---------------------------------------------------------------------------
# Building a report
# ---------------------------------------------------------------------------


def new_build_stamp(
    *, build_id: str = "development", commit: str = "unknown", version: str = GAME_VERSION
) -> BuildStamp:
    """Return the build identity to stamp on a report."""
    return {
        "game_version": version,
        "build_id": build_id,
        "commit": commit,
        "save_schema_version": SAVE_SCHEMA_VERSION,
        "playtest_report_schema_version": PLAYTEST_REPORT_SCHEMA_VERSION,
    }


def new_report(build: BuildStamp, code: str, *, consent: bool = False) -> PlaytestReport:
    """Return an empty report for one installation."""
    return {
        "playtest_report_schema_version": PLAYTEST_REPORT_SCHEMA_VERSION,
        "build": build,
        "session_code": code,
        "consent": consent,
        "runs": [],
    }


def new_run(report: PlaytestReport, seed: int) -> RunRecord:
    """Append and return a record for a playthrough that has just started."""
    record: RunRecord = {
        "index": len(report["runs"]) + 1,
        "seed": int(seed),
        "completed": False,
        "first_completed": False,
        "days_reached": 1,
        "active_seconds": 0,
        "scenes": [],
        "anchors": [],
        "choices": [],
        "documents": [],
        "calendar_opens": 0,
        "journal_opens": 0,
        "archive_reopens": 0,
        "commitments_made": [],
        "commitments_kept": [],
        "commitments_broken": [],
        "loads": 0,
    }
    report["runs"].append(record)
    return record


def current_run(report: PlaytestReport) -> RunRecord | None:
    """Return the run being played, or ``None`` before the first ``Start``."""
    return report["runs"][-1] if report["runs"] else None


def complete_run(report: PlaytestReport, record: RunRecord) -> None:
    """Mark a run as having reached the end of Act 1.

    Sets ``first_completed`` only on the first one, which is the record a
    reader should weight most: a replay is informed by the first playthrough
    and answers a different question.
    """
    record["completed"] = True
    record["first_completed"] = not any(
        other["completed"] and other is not record for other in report["runs"]
    )


def choice_id(storylet_id: str, index: int, caption: str) -> str:
    """Return a stable identifier for one option of one menu.

    Three parts, because each is unreliable on its own. The storylet id is
    permanent once a storylet is active and is therefore the anchor. The index
    survives a typo fix in the caption. The caption slug is what makes a report
    readable without opening the script, and it is what changes -- visibly --
    if somebody rewrites an option, which is exactly when a report from an
    older build should stop being comparable::

        iris_the_second_box.0.take-the-lid-off
    """
    slug = re.sub(r"[^a-z0-9]+", "-", caption.lower()).strip("-")
    return f"{storylet_id}.{index}.{slug[:40] or 'unnamed'}"


# ---------------------------------------------------------------------------
# Privacy
# ---------------------------------------------------------------------------

#: Patterns that must never appear anywhere in a report. Written as an
#: executable statement of ``docs/legal/PRIVACY.md`` rather than as prose: a
#: rule nothing checks is a rule that lasts until the next hurried commit.
_FORBIDDEN: tuple[tuple[str, str], ...] = (
    (r"[A-Za-z]:[\\/]", "an absolute Windows path"),
    (r"(?<![\w.])/(?:home|Users|root|var|etc|tmp)/", "an absolute POSIX path"),
    (r"[\w.+-]+@[\w-]+\.[\w.]+", "an email address"),
    (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "an IP address"),
    (r"(?i)\b(?:username|userprofile|hostname|computername|macaddr)\b", "a machine identifier"),
    (r"(?i)\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", "a wall-clock timestamp"),
)


def privacy_violations(report: PlaytestReport) -> list[str]:
    """Return every reason this report may not be sent to anybody.

    Checks the serialised form rather than the structure, because the risk is
    not a field somebody added on purpose -- it is a value that arrived inside
    one. A save path used as a document id would pass any field-by-field
    review and fail this.
    """
    blob = json.dumps(report, ensure_ascii=False)
    found: list[str] = []
    for pattern, description in _FORBIDDEN:
        match = re.search(pattern, blob)
        if match:
            found.append(f"{description}: {match.group(0)!r}")
    return found


def validate(report: Any) -> list[str]:
    """Return the ways ``report`` fails to be a report this build can read.

    Used by ``s32 playtest summarize`` before it trusts a file a tester sent
    back, and by the tests over the synthetic fixtures.
    """
    problems: list[str] = []
    if not isinstance(report, dict):
        return ["not an object"]

    version = report.get("playtest_report_schema_version")
    if version != PLAYTEST_REPORT_SCHEMA_VERSION:
        problems.append(
            f"schema version {version!r}, this build reads {PLAYTEST_REPORT_SCHEMA_VERSION}"
        )

    for field in ("build", "session_code", "consent", "runs"):
        if field not in report:
            problems.append(f"missing {field!r}")

    code = report.get("session_code", "")
    if not isinstance(code, str) or not code.startswith(_CODE_PREFIX):
        problems.append(f"session code {code!r} does not look like a session code")

    runs = report.get("runs")
    if not isinstance(runs, list):
        problems.append("runs is not a list")
        return problems

    for position, run in enumerate(runs, start=1):
        if not isinstance(run, dict):
            problems.append(f"run {position} is not an object")
            continue
        for field in ("index", "seed", "completed", "scenes", "choices"):
            if field not in run:
                problems.append(f"run {position} is missing {field!r}")

    firsts = sum(1 for r in runs if isinstance(r, dict) and r.get("first_completed"))
    if firsts > 1:
        problems.append(f"{firsts} runs claim to be the first completed one")

    return problems


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def to_json(report: PlaytestReport) -> str:
    """Serialise a report, sorted and indented so two of them can be diffed."""
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _duration(seconds: int) -> str:
    """Render a duration the way a person would say it."""
    if seconds < 60:
        return f"{seconds} seconds"
    minutes, remainder = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} min {remainder:02d} s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} h {minutes:02d} min"


def summary_markdown(report: PlaytestReport) -> str:
    """Render a report as something a person can read without a tool.

    Deliberately the same facts as the JSON and no more. A summary that
    interpreted -- "the tester seemed engaged" -- would be this file inventing
    the human judgement the whole milestone exists to go and collect.
    """
    build = report["build"]
    lines = [
        "# Playtest report",
        "",
        f"Session code **{report['session_code']}**.",
        "",
        "| | |",
        "| --- | --- |",
        f"| Game version | `{build['game_version']}` |",
        f"| Build | `{build['build_id']}` |",
        f"| Commit | `{build['commit']}` |",
        f"| Report schema | {build['playtest_report_schema_version']} |",
        f"| Runs | {len(report['runs'])} |",
        "",
        "Quote the session code on the questionnaire. Nothing in this file",
        "identifies you or your computer, and nothing was sent anywhere.",
        "",
    ]

    for run in report["runs"]:
        heading = f"## Run {run['index']}"
        if run["first_completed"]:
            heading += " -- first completed run"
        elif run["completed"]:
            heading += " -- completed"
        else:
            heading += " -- not finished"
        lines += [
            heading,
            "",
            f"- reached day {run['days_reached']}",
            f"- about {_duration(run['active_seconds'])} of play",
            f"- {len(run['scenes'])} scenes, {len(set(run['scenes']))} of them different",
            f"- {len(run['choices'])} choices",
            f"- {len(run['documents'])} documents opened, {run['archive_reopens']} reopened later",
            f"- calendar opened {run['calendar_opens']} times, journal {run['journal_opens']}",
            f"- promises: {len(run['commitments_made'])} made,"
            f" {len(run['commitments_kept'])} kept,"
            f" {len(run['commitments_broken'])} broken",
            f"- {run['loads']} saves reloaded",
            "",
        ]

    lines += ["## Scenes, in the order they were played", ""]
    for run in report["runs"]:
        lines += [f"**Run {run['index']}**", ""]
        for position, scene in enumerate(run["scenes"], start=1):
            lines.append(f"{position}. `{scene}`")
        lines.append("")

    return "\n".join(lines)
