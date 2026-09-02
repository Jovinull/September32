"""Aggregating playtest reports, and refusing to interpret them.

The line this module holds: it counts and it lists. It does not classify
sentiment, it does not summarise prose, and it does not read questionnaires.
Free text is a person's job, and a tool that offered a one-line verdict on what
five people thought would be believed.

Nothing here sends anything anywhere. See ``docs/playtest/PLAYTEST_DATA.md``.
"""

from __future__ import annotations

import collections
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from s32_engine import playtest

#: A literal newline, kept in a constant so the joins below survive being
#: edited by a tool that rewrites escape sequences. This has happened twice.
NEWLINE = chr(10)


@dataclass(slots=True)
class Aggregate:
    """What a wave of reports says, before anybody interprets it."""

    reports: int = 0
    rejected: list[tuple[str, list[str]]] = field(default_factory=list)
    runs: int = 0
    completed_runs: int = 0
    first_runs: int = 0
    seconds: list[int] = field(default_factory=list)
    days: list[int] = field(default_factory=list)
    scene_counts: list[int] = field(default_factory=list)
    scenes: collections.Counter[str] = field(default_factory=collections.Counter)
    #: Which sessions saw each scene, so "everybody" and "one person" are
    #: distinguishable -- a scene played five times by one tester is a
    #: different fact from one played once by five.
    scene_sessions: dict[str, set[str]] = field(default_factory=dict)
    choices: collections.Counter[str] = field(default_factory=collections.Counter)
    documents: collections.Counter[str] = field(default_factory=collections.Counter)
    calendar_opens: list[int] = field(default_factory=list)
    journal_opens: list[int] = field(default_factory=list)
    archive_reopens: list[int] = field(default_factory=list)
    commitments_made: int = 0
    commitments_kept: int = 0
    commitments_broken: int = 0
    sessions: list[str] = field(default_factory=list)
    builds: collections.Counter[str] = field(default_factory=collections.Counter)


def find_reports(target: Path) -> list[Path]:
    """Return the report files under ``target``, which may be a file."""
    if target.is_file():
        return [target]
    return sorted(target.rglob("playtest-report*.json"))


def load(target: Path) -> Aggregate:
    """Read every report under ``target`` and count what is in them."""
    agg = Aggregate()

    for path in find_reports(target):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            agg.rejected.append((str(path.name), [f"unreadable: {exc}"]))
            continue

        problems = playtest.validate(raw)
        if problems:
            # Refused rather than partially read. A report from a schema this
            # build does not know is a report about a different game.
            agg.rejected.append((path.name, problems))
            continue

        agg.reports += 1
        code = raw["session_code"]
        agg.sessions.append(code)
        agg.builds[raw["build"]["build_id"]] += 1

        for run in raw["runs"]:
            agg.runs += 1
            if run.get("completed"):
                agg.completed_runs += 1
            if not run.get("first_completed"):
                # Only the first completed run of each session feeds the
                # experience measures. A replay is informed by the first one
                # and answers a different question; averaging them together
                # would quietly turn "would they continue" into "did they".
                continue
            agg.first_runs += 1
            agg.seconds.append(int(run.get("active_seconds", 0)))
            agg.days.append(int(run.get("days_reached", 0)))
            scenes = list(run.get("scenes", []))
            agg.scene_counts.append(len(set(scenes)))
            agg.scenes.update(scenes)
            for scene in set(scenes):
                agg.scene_sessions.setdefault(scene, set()).add(code)
            agg.choices.update(run.get("choices", []))
            agg.documents.update(run.get("documents", []))
            agg.calendar_opens.append(int(run.get("calendar_opens", 0)))
            agg.journal_opens.append(int(run.get("journal_opens", 0)))
            agg.archive_reopens.append(int(run.get("archive_reopens", 0)))
            agg.commitments_made += len(run.get("commitments_made", []))
            agg.commitments_kept += len(run.get("commitments_kept", []))
            agg.commitments_broken += len(run.get("commitments_broken", []))

    return agg


def _median(values: list[int]) -> float:
    """Return the median, or 0 for an empty list."""
    if not values:
        return 0.0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2


def _header(agg: Aggregate, add: Callable[[str], None]) -> None:
    """The wave: how many reports, from whom, and what was refused."""
    add("=" * 72)
    add("PLAYTEST REPORTS")
    add("=" * 72)

    if agg.rejected:
        add("")
        add(f"REFUSED  {len(agg.rejected)} file(s)")
        for name, problems in agg.rejected:
            add(f"  {name}")
            for problem in problems:
                add(f"      {problem}")

    if not agg.reports:
        return

    add("")
    add(f"  reports              {agg.reports}")
    add(f"  sessions             {', '.join(agg.sessions)}")
    add(f"  builds               {', '.join(sorted(agg.builds))}")
    add(f"  runs                 {agg.runs} ({agg.completed_runs} completed)")
    add(f"  first completed runs {agg.first_runs}")


def _measures(agg: Aggregate, add: Callable[[str], None]) -> None:
    """The figures, all of them from first completed runs only."""
    add("")
    add("  ALL FIGURES BELOW ARE FIRST COMPLETED RUNS ONLY")
    add(f"  completion rate      {agg.first_runs}/{agg.reports}")
    add(f"  median playtime      {_median(agg.seconds) / 60:.0f} min")
    if agg.seconds:
        low, high = min(agg.seconds) / 60, max(agg.seconds) / 60
        add(f"  playtime range       {low:.0f} to {high:.0f} min")
    add(f"  median day reached   {_median(agg.days):.0f}")
    add(f"  distinct scenes/run  {_median(agg.scene_counts):.0f}")
    add(f"  calendar opens       median {_median(agg.calendar_opens):.0f}")
    add(f"  journal opens        median {_median(agg.journal_opens):.0f}")
    add(f"  document re-reads    median {_median(agg.archive_reopens):.0f}")
    add(
        f"  promises             {agg.commitments_made} made, "
        f"{agg.commitments_kept} kept, {agg.commitments_broken} broken"
    )


def _divergence(agg: Aggregate, add: Callable[[str], None]) -> None:
    """How much of the week two testers had in common. H06 is measured here."""
    if not (agg.scene_sessions and agg.first_runs):
        return
    everyone = [s for s, who in agg.scene_sessions.items() if len(who) == agg.first_runs]
    alone = sorted(s for s, who in agg.scene_sessions.items() if len(who) == 1)

    add("")
    add("  DIVERGENCE")
    add(f"  scenes anybody saw   {len(agg.scene_sessions)}")
    add(f"  scenes everybody saw {len(everyone)}")
    add(f"  scenes one saw       {len(alone)}")
    add(f"  shared fraction      {len(everyone) / len(agg.scene_sessions):.0%}")

    add("")
    add("  MOST PLAYED")
    for scene, count in agg.scenes.most_common(12):
        seen_by = len(agg.scene_sessions.get(scene, ()))
        plural = "tester" if seen_by == 1 else "testers"
        add(f"      {count:>4}  ({seen_by} {plural})  {scene}")

    if alone:
        add("")
        add("  SEEN BY EXACTLY ONE TESTER")
        for scene in alone:
            add(f"      {scene}")


def _surfaces(agg: Aggregate, add: Callable[[str], None]) -> None:
    """What was opened and what was chosen."""
    add("")
    add("  DOCUMENTS")
    for document, count in agg.documents.most_common():
        add(f"      {count:>4}  {document}")

    add("")
    add("  CHOICES")
    add(f"      {len(agg.choices)} distinct choice ids across the wave")
    for choice, count in agg.choices.most_common(12):
        add(f"      {count:>4}  {choice}")


def render(agg: Aggregate) -> str:
    """Render the aggregate as text, with no conclusions in it.

    Split into sections not for length but because each one answers a
    different question, and because the divergence block is the one somebody
    will want to change first.
    """
    out: list[str] = []
    add = out.append

    _header(agg, add)
    if not agg.reports:
        add("")
        add("No readable reports. Nothing to say.")
        return NEWLINE.join(out)

    _measures(agg, add)
    _divergence(agg, add)
    _surfaces(agg, add)

    add("")
    add("  Free text is not summarised here, by design. Read it.")
    add("  docs/playtest/WAVE_1_SUMMARY_TEMPLATE.md")

    return NEWLINE.join(out)
