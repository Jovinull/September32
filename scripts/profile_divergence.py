#!/usr/bin/env python3
"""Do the simulator's player profiles finish runs in different states?

Milestone 1 found that they did not. Every profile played the same scenes in the
same order, for two reasons that had to be fixed together: the director's
priority tier held exactly one candidate at every selection moment, so there was
nothing for a profile to prefer between; and the simulator resolved every
in-scene choice uniformly at random, so two players who reached the same scene
always left it in the same state and nothing downstream could diverge.

This is the measurement for that, kept out of the test suite on purpose. There
is no threshold at which divergence is "correct", and a test pinning these
numbers would fail on every content change without telling anyone anything.

    uv run python scripts/profile_divergence.py

Every profile gets the same seeds, so any difference in the output is the
profile and not the draw.
"""

from __future__ import annotations

from collections import Counter

from s32_engine.definitions import load_library
from s32tools import paths
from s32tools.simulation import profiles as profile_module
from s32tools.simulation.simulator import Simulator

#: Enough runs for the per-run means to settle, few enough to finish in a minute.
SEEDS = range(1234, 1234 + 60)

#: Axes worth printing. The full set is large and mostly moves together; these
#: are the ones the profiles were written to pull in different directions.
AXES = (
    "player->iris.attraction",
    "player->iris.trust",
    "player->theo.respect",
    "player->june.trust",
    "player->mara.suspicion",
    "player->noah.respect",
)


def main() -> None:
    """Print a divergence table for every profile."""
    library = load_library(paths.data_dir())
    simulator = Simulator(library)
    names = list(profile_module.PROFILES)
    runs = len(SEEDS)

    plays: dict[str, Counter[str]] = {}
    axes: dict[str, Counter[str]] = {}
    traits: dict[str, Counter[str]] = {}
    signatures: dict[str, set[tuple[tuple[str, int], ...]]] = {}

    for name in names:
        profile = profile_module.PROFILES[name]
        plays[name] = Counter()
        axes[name] = Counter()
        traits[name] = Counter()
        signatures[name] = set()
        for seed in SEEDS:
            run = simulator.run_once(seed, profile)
            counts = Counter(run.storylets_played)
            plays[name].update(counts)
            traits[name].update(run.traits)
            signatures[name].add(tuple(sorted(counts.items())))
            for pair, vector in run.relationships.items():
                for axis, value in vector.items():
                    axes[name][f"{pair}.{axis}"] += value

    print(f"# Profile divergence over {runs} shared seeds\n")
    print("## Distinct run signatures (which scenes, how many times)\n")
    for name in names:
        print(f"  {name:<14} {len(signatures[name]):>3}/{runs}")

    identical = [
        (a, b) for i, a in enumerate(names) for b in names[i + 1 :] if plays[a] == plays[b]
    ]
    total_pairs = len(names) * (len(names) - 1) // 2
    print(f"\n{len(identical)}/{total_pairs} profile pairs had identical aggregate play counts")
    for a, b in identical:
        print(f"  IDENTICAL: {a} vs {b}")

    trait_names = sorted({t for name in names for t in traits[name]})
    print("\n## Traits accumulated, mean per run\n")
    print(f"  {'profile':<14}" + "".join(f"{t[:9]:>10}" for t in trait_names))
    for name in names:
        print(
            f"  {name:<14}"
            + "".join(f"{traits[name].get(t, 0) / runs:>10.1f}" for t in trait_names)
        )

    print("\n## Relationship axes, mean per run\n")
    print(f"  {'profile':<14}" + "".join(f"{a.split('->')[1][:11]:>13}" for a in AXES))
    for name in names:
        print(f"  {name:<14}" + "".join(f"{axes[name].get(a, 0) / runs:>13.1f}" for a in AXES))

    print("\n## Scenes the profiles disagree about most, plays per run\n")
    spreads = []
    for sid in sorted(library.storylets):
        values = [plays[name].get(sid, 0) / runs for name in names]
        spreads.append((max(values) - min(values), sid, values))
    spreads.sort(reverse=True)
    print(f"  {'storylet':<26}" + "".join(f"{n[:7]:>8}" for n in names))
    for _, sid, values in spreads[:12]:
        print(f"  {sid:<26}" + "".join(f"{v:>8.1f}" for v in values))


if __name__ == "__main__":
    main()
