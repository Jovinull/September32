#!/usr/bin/env python3
"""Run every quality gate, in the order that fails fastest.

One command a contributor runs before saying they are done, and the same command
CI runs. Keeping them identical is the point: a gate that only exists in CI is a
gate people discover by having a pull request rejected.

Gates that need something not installed (the Ren'Py SDK, third-party assets) are
reported as SKIPPED, not failed. A new contributor should be able to run this and
see green on everything the code can check by itself.

    uv run python scripts/check.py
    uv run python scripts/check.py --fast     # skip Ren'Py and the simulator
    uv run python scripts/check.py --fix      # format and autofix first
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(slots=True)
class Gate:
    """One check."""

    name: str
    command: list[str]
    slow: bool = False
    #: Exit code meaning "the thing this checks is not installed here".
    skip_if_missing: str = ""


GATES: list[Gate] = [
    Gate("ruff format", ["uv", "run", "ruff", "format", "--check", "."]),
    Gate("ruff check", ["uv", "run", "ruff", "check", "."]),
    Gate("mypy", ["uv", "run", "mypy"]),
    Gate("pytest", ["uv", "run", "pytest", "-q"]),
    Gate("schemas up to date", ["uv", "run", "s32", "schemas", "--check"]),
    Gate("credits up to date", ["uv", "run", "s32", "assets", "credits", "--check"]),
    Gate("content validation", ["uv", "run", "s32", "validate"]),
    Gate("asset licensing", ["uv", "run", "s32", "assets", "verify", "--catalog"]),
    Gate(
        "ren'py lint",
        ["uv", "run", "s32", "renpy", "lint"],
        slow=True,
        skip_if_missing="not installed",
    ),
    Gate(
        "ren'py testcases",
        ["uv", "run", "s32", "renpy", "test"],
        slow=True,
        skip_if_missing="not installed",
    ),
    Gate(
        "simulation",
        ["uv", "run", "s32", "simulate", "--runs", "500", "--quiet"],
        slow=True,
    ),
]


def run(gate: Gate) -> tuple[str, float, str]:
    """Run one gate. Returns ``(status, seconds, output)``."""
    started = time.monotonic()
    result = subprocess.run(gate.command, cwd=ROOT, capture_output=True, text=True, check=False)
    elapsed = time.monotonic() - started
    output = result.stdout + result.stderr

    if result.returncode == 0:
        return "PASS", elapsed, output
    if gate.skip_if_missing and gate.skip_if_missing in output:
        return "SKIP", elapsed, output
    return "FAIL", elapsed, output


def main() -> int:
    """Run the gates and report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fast", action="store_true", help="skip the slow gates")
    parser.add_argument("--fix", action="store_true", help="format and autofix first")
    args = parser.parse_args()

    if args.fix:
        print("=== formatting and autofixing ===")
        subprocess.run(["uv", "run", "ruff", "format", "."], cwd=ROOT, check=False)
        subprocess.run(["uv", "run", "ruff", "check", "--fix", "."], cwd=ROOT, check=False)
        print()

    gates = [g for g in GATES if not (args.fast and g.slow)]
    results: list[tuple[Gate, str, float, str]] = []

    for gate in gates:
        print(f"... {gate.name}", end="", flush=True)
        status, elapsed, output = run(gate)
        print(f"\r{status:4}  {gate.name:24} {elapsed:6.1f}s")
        results.append((gate, status, elapsed, output))

    failures = [(g, out) for g, status, _, out in results if status == "FAIL"]
    skipped = [g.name for g, status, _, _ in results if status == "SKIP"]

    if failures:
        print("\n" + "=" * 70)
        for gate, output in failures:
            print(f"\n--- {gate.name} ---")
            print(output.strip()[-4000:])

    print("\n" + "=" * 70)
    total = sum(elapsed for _, _, elapsed, _ in results)
    passed = sum(1 for _, status, _, _ in results if status == "PASS")
    print(f"{passed}/{len(gates)} passed in {total:.1f}s")
    if skipped:
        print(f"skipped (not installed here): {', '.join(skipped)}")
    if failures:
        print(f"FAILED: {', '.join(g.name for g, _ in failures)}")
        return 1
    print("All gates green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
