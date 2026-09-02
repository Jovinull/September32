#!/usr/bin/env python3
"""How long Act 1 takes, measured rather than guessed.

The number a tester is given in `PLAYTEST_README.md` has to come from the
content. "About ninety minutes" is the kind of figure that gets written down
once, becomes true by repetition, and is wrong by the third milestone.

So this plays every profile at forty seeds, keeps the runs that actually reached
the end of the act, and counts the words in the scenes each of them played. The
count is the *spoken* half only: menus, travel, the day cards and the time
somebody spends deciding are all extra, which is why the README gives a range
and not a number.

    uv run python scripts/playtime.py

Reading speeds are given at three rates because they are not interchangeable.
240 words a minute is ordinary prose read for pleasure; 300 is somebody who
reads a lot of fiction; 200 is somebody stopping to look at things.
"""

from __future__ import annotations

import re
import statistics

from s32_engine.definitions import load_library
from s32tools import paths
from s32tools.simulation import profiles as profile_module
from s32tools.simulation.simulator import Simulator

#: A line somebody reads: narration, a centred card, or a character speaking.
SPOKEN = re.compile(r'^\s*(?:narrator|centered|c_\w+)\s+"(.*)"\s*$')

#: Seeds per profile. Forty is enough for a stable median and quick enough to
#: run while somebody is waiting for it.
SEEDS = 40

#: Words a minute. See the module docstring for why there are three.
RATES = (200, 240, 300)


def words_by_label() -> dict[str, int]:
    """Return the spoken word count of every label in the story tree."""
    counts: dict[str, int] = {}
    for path in sorted((paths.game_dir() / "story").rglob("*.rpy")):
        text = path.read_text(encoding="utf-8")
        for block in re.split(r"^label ", text, flags=re.M)[1:]:
            name = block.split(":")[0].strip()
            counts[name] = sum(
                len(match.group(1).split())
                for line in block.splitlines()
                if (match := SPOKEN.match(line))
            )
    return counts


def main() -> None:
    """Measure and print."""
    words = words_by_label()
    library = load_library(paths.data_dir())
    simulator = Simulator(library)

    totals: list[int] = []
    scenes: list[int] = []
    unfinished = 0

    for seed in range(1234, 1234 + SEEDS):
        for name in profile_module.PROFILES:
            run = simulator.run_once(seed, profile_module.get(name), max_days=8)
            if "the_date" not in run.anchors_reached:
                # A run that did not reach the end of the act says nothing
                # about how long the act takes. Counted, because a large number
                # here would be a content bug rather than a rounding detail.
                unfinished += 1
                continue
            played = [f"s32_st_{sid}" for sid in run.storylets_played]
            played += [f"s32_anchor_{aid}" for aid in run.anchors_reached]
            totals.append(sum(words.get(label, 0) for label in played))
            scenes.append(len(run.storylets_played) + len(run.anchors_reached))

    if not totals:
        print("No run reached the end of Act 1. That is the finding.")
        return

    print(f"{'=' * 60}")
    print("HOW LONG ACT 1 TAKES")
    print("=" * 60)
    print(f"  runs measured    {len(totals)} ({unfinished} did not finish the act)")
    print(
        f"  scenes per run   median {statistics.median(scenes):.0f}, "
        f"range {min(scenes)}-{max(scenes)}"
    )
    print(
        f"  words per run    median {statistics.median(totals):.0f}, "
        f"range {min(totals)}-{max(totals)}"
    )
    print("")
    for rate in RATES:
        median = statistics.median(totals) / rate
        print(
            f"  at {rate} wpm     median {median:.0f} min, "
            f"range {min(totals) / rate:.0f}-{max(totals) / rate:.0f} min"
        )
    print("")
    print(f"  all prose        {sum(words.values())} words across {len(words)} labels")
    print("")
    print("  Menus, travel, the day cards and thinking time are on top of this.")


if __name__ == "__main__":
    main()
