#!/usr/bin/env python3
"""Read three simulated first weeks side by side, as weeks rather than as data.

The simulation report answers "is anything unreachable". It cannot answer the
question this project actually has to pass, which is whether two people who
played the same game had different weeks. That is a reading problem, and it
needs a page a person can read.

So this prints a chronological transcript per profile -- day, scene, the branch
taken, what it changed -- and then the state each one finished with. Not the
whole prose: the prose is in `game/story/`, and a transcript that reproduced it
would be longer than reading the game.

    uv run python scripts/first_week.py
    uv run python scripts/first_week.py --profiles curious romantic altruistic
    uv run python scripts/first_week.py --seed 4211 --days 7

Deterministic: same seed, same profile, same week.
"""

from __future__ import annotations

import argparse
from collections import Counter

from s32_engine.definitions import load_library
from s32_engine.types import GameState
from s32tools import paths
from s32tools.simulation import profiles as profile_module
from s32tools.simulation.simulator import Simulator

#: The three profiles the milestone brief asks to be compared. They are the
#: furthest apart on the axes the content actually moves.
DEFAULT_PROFILES = ("curious", "romantic", "altruistic")


class Transcript(Simulator):
    """A simulator that remembers what each scene actually changed.

    It does not re-implement the choice. `_resolve_outcome` is called, and the
    difference it makes to the state is read afterwards -- so this cannot drift
    out of agreement with the simulator it is reporting on, which a second copy
    of the selection logic certainly would.
    """

    def __init__(self, library) -> None:
        super().__init__(library)
        self.lines: list[tuple[int, str, str, tuple[str, ...]]] = []

    def _resolve_outcome(self, storylet, state, rng, profile):
        before = _snapshot(state)
        super()._resolve_outcome(storylet, state, rng, profile)
        self.lines.append(
            (
                state["world"]["day"],
                storylet.title,
                storylet.id,
                _changes(before, _snapshot(state)),
            )
        )

    def _fire_ready_anchor(self, state, rng):
        """Record anchors too. They are the spine of the week.

        A transcript that showed only storylets would leave the five beats every
        run shares out of the comparison, which is exactly the half a reader
        needs in order to judge whether the other half differs.
        """
        done = set(state["anchors_done"])
        before = _snapshot(state)
        super()._fire_ready_anchor(state, rng)
        for anchor_id in state["anchors_done"]:
            if anchor_id in done:
                continue
            self.lines.append(
                (
                    state["world"]["day"],
                    f"* {self.library.anchors[anchor_id].title}",
                    anchor_id,
                    _changes(before, _snapshot(state)),
                )
            )

    def week(self, seed: int, profile, max_days: int):
        """Run one week and keep the transcript."""
        self.lines.clear()
        return self.run_once(seed, profile, max_days=max_days)


def _snapshot(state: GameState) -> dict[str, int | str]:
    """Flatten the parts of the state a reader would call "what happened"."""
    flat: dict[str, int | str] = {}
    for pair, vector in state["relationships"].items():
        for axis, value in vector.items():
            if value:
                flat[f"{pair}.{axis}"] = value
    for fact, belief in state["beliefs"].get("player", {}).items():
        flat[f"knows {fact}"] = belief["stance"]
    for record in state["commitments"]:
        flat[f"promise {record['id']}"] = record["status"]
    return flat


def _changes(before: dict[str, int | str], after: dict[str, int | str]) -> tuple[str, ...]:
    """Return a short human list of what moved between two snapshots."""
    lines: list[str] = []
    for key, value in sorted(after.items()):
        old = before.get(key)
        if old == value:
            continue
        if old is None:
            lines.append(f"{key} = {value}")
        elif isinstance(value, int) and isinstance(old, int):
            lines.append(f"{key} {old} -> {value}")
        else:
            lines.append(f"{key}: {old} -> {value}")
    return tuple(lines)


def _render(name: str, transcript: Transcript, result, max_days: int) -> None:
    """Print one week."""
    print(f"\n{'=' * 72}")
    scenes = len(result.storylets_played)
    print(f"{name.upper()}  —  seed {result.seed}, {result.days} days, {scenes} scenes")
    print("=" * 72)

    by_day: dict[int, list[tuple[str, str, tuple[str, ...]]]] = {}
    for day, title, sid, effects in transcript.lines:
        if day > max_days:
            continue
        by_day.setdefault(day, []).append((title, sid, effects))

    for day in range(1, max_days + 1):
        entries = by_day.get(day, [])
        print(f"\n  DAY {day}")
        if not entries:
            print("    (nothing)")
            continue
        for title, sid, effects in entries:
            print(f"    {title}  ({sid})")
            for effect in effects:
                print(f"        {effect}")


def _render_end_state(result) -> None:
    """Print what the week left behind."""
    print("\n  ENDED THE WEEK WITH")
    print(f"    phase        {result.final_phase}")
    print(f"    knows        {', '.join(result.knowledge_gained) or 'nothing'}")

    edges = []
    for pair, vector in sorted(result.relationships.items()):
        strongest = sorted(vector.items(), key=lambda kv: -kv[1])[:2]
        strongest = [(axis, value) for axis, value in strongest if value]
        if strongest:
            edges.append(f"{pair} " + " ".join(f"{a}={v}" for a, v in strongest))
    print("    relationships")
    for edge in edges:
        print(f"        {edge}")

    traits = ", ".join(f"{k}={v}" for k, v in sorted(result.traits.items()) if v)
    print(f"    traits       {traits or 'none'}")
    print(f"    commitments  {result.commitments or 'none made'}")


def main() -> None:
    """Print one week per profile."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--profiles", nargs="*", default=list(DEFAULT_PROFILES))
    args = parser.parse_args()

    library = load_library(paths.data_dir())
    shared: list[Counter[str]] = []

    for name in args.profiles:
        profile = profile_module.get(name)
        transcript = Transcript(library)
        result = transcript.week(args.seed, profile, args.days)
        _render(name, transcript, result, args.days)
        _render_end_state(result)
        shared.append(Counter(result.storylets_played))

    print(f"\n{'=' * 72}")
    print("HOW MUCH OF THE WEEK WAS THE SAME")
    print("=" * 72)
    everyone = set.intersection(*(set(c) for c in shared)) if shared else set()
    anyone = set().union(*(set(c) for c in shared)) if shared else set()
    print(f"  scenes every profile played : {len(everyone)}")
    print(f"  scenes at least one played  : {len(anyone)}")
    if anyone:
        print(f"  shared fraction             : {len(everyone) / len(anyone):.0%}")
    only = {
        name: sorted(set(counts) - set.union(*(set(o) for o in shared if o is not counts)))
        for name, counts in zip(args.profiles, shared, strict=True)
    }
    for name, ids in only.items():
        print(f"  only {name:<14}: {', '.join(ids) or '—'}")


if __name__ == "__main__":
    main()
