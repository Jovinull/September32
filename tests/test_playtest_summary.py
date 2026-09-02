"""The summarizer counts. It does not interpret.

That is the whole design constraint, and it is easier to break than it looks:
a tool that offered a one-line verdict on what five people thought would be
believed, and would quietly become the wave's conclusion.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from s32tools.playtest_summary import Aggregate, load, render

FIXTURES = Path(__file__).parent / "fixtures" / "playtests"


@pytest.fixture(scope="module")
def aggregate() -> Aggregate:
    return load(FIXTURES)


def test_it_reads_the_readable_reports(aggregate):
    """Three synthetic testers, and the fourth file refused."""
    assert aggregate.reports == 3
    assert sorted(aggregate.sessions) == ["S32-SYNTHA", "S32-SYNTHB", "S32-SYNTHC"]


def test_it_refuses_a_report_from_a_schema_it_does_not_know(aggregate):
    """Refused and named, not skipped silently.

    A wave that quietly ignored two of its five reports would produce numbers
    nobody could interpret and no sign that anything was missing.
    """
    assert len(aggregate.rejected) == 1
    name, problems = aggregate.rejected[0]
    assert "future" in name
    assert any("schema version" in p for p in problems)


def test_only_first_completed_runs_feed_the_experience_measures(aggregate):
    """Fixture A has two completed runs; only the first should count.

    A replay is informed by the first playthrough and answers a different
    question. Averaging them together turns "would they continue" into "did
    they", which is not the same measurement at all.
    """
    assert aggregate.runs == 4
    assert aggregate.completed_runs == 3
    assert aggregate.first_runs == 2
    assert len(aggregate.seconds) == 2
    assert sorted(aggregate.seconds) == [4620, 5880]


def test_the_unfinished_run_still_counts_as_a_report(aggregate):
    """Somebody who stopped on day four is a finding, not a missing data point."""
    assert "S32-SYNTHC" in aggregate.sessions
    assert aggregate.completed_runs < aggregate.runs


def test_scene_coverage_distinguishes_everybody_from_one_person(aggregate):
    """A scene played five times by one tester is not a scene five testers saw.

    H06 is measured from this distinction, so collapsing it would be measuring
    nothing.
    """
    assert aggregate.scene_sessions["arrival"] == {"S32-SYNTHA", "S32-SYNTHB"}
    assert aggregate.scene_sessions["theo_the_quiz"] == {"S32-SYNTHA"}
    assert aggregate.scenes["courtyard_small_talk"] == 3


def test_commitments_are_counted_in_all_three_states(aggregate):
    assert aggregate.commitments_made == 2
    assert aggregate.commitments_kept == 1
    assert aggregate.commitments_broken == 1


def test_the_rendered_report_says_what_it_will_not_do(aggregate):
    """The line that keeps the tool honest has to be in its output.

    A note in a document nobody rereads is not a constraint; a line printed
    every time somebody runs the command is.
    """
    text = render(aggregate)
    assert "Free text is not summarised here, by design" in text


def test_the_rendered_report_contains_no_verdict(aggregate):
    """No adjectives about the testers or the game.

    The summarizer's whole job is to hand a person numbers they then have to
    read. If it started saying "engagement was strong", that reading would stop
    happening.
    """
    text = render(aggregate).lower()
    for word in ("engag", "positive", "negative", "sentiment", "liked", "enjoyed", "success"):
        assert word not in text, word


def test_an_empty_directory_says_so_rather_than_reporting_zeroes(tmp_path):
    """A table of zeros is worse than no table.

    Milestone 3 shipped a divergence script that printed one, and a report that
    shows zeros where there is no data gets quoted as though there were.
    """
    text = render(load(tmp_path))
    assert "Nothing to say" in text


def test_a_single_file_can_be_summarised_directly():
    """`s32 playtest summarize <one report>` is the common case during a wave."""
    one = load(FIXTURES / "playtest-report-synthetic-a.json")
    assert one.reports == 1
    assert one.first_runs == 1


def test_the_summarizer_sends_nothing_anywhere():
    """§52. No tooling in this repository uploads a tester's words.

    Asserted against the module rather than promised in a document, because
    this is the file where an "upload the results" convenience would land.
    """
    source = (Path(__file__).parents[1] / "tools" / "s32tools" / "playtest_summary.py").read_text(
        encoding="utf-8"
    )
    for forbidden in ("socket", "urllib", "requests", "http", "openai", "anthropic", "api_key"):
        assert forbidden not in source, forbidden


def test_the_fixtures_are_not_mistaken_for_people(aggregate):
    """Every session in the aggregate is visibly synthetic."""
    assert all("SYNTH" in code for code in aggregate.sessions)
    for path in sorted(FIXTURES.glob("*.json")):
        assert "SYNTHETIC" in json.loads(path.read_text(encoding="utf-8"))["note"]
