#!/usr/bin/env python3
"""Take a fresh checkout to a running game.

    uv run python scripts/bootstrap.py

Every step is idempotent and every step is skippable. A step that cannot complete
— no network, an asset behind a login — reports what is needed and the script
carries on, because a project that stops entirely because one download failed is
a project nobody can start work on.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def step(title: str, command: list[str], *, optional: bool = False) -> bool:
    """Run one bootstrap step. Returns whether it succeeded."""
    print(f"\n=== {title} ===")
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode == 0:
        return True
    if optional:
        print(f"\n[!] {title} did not complete. Continuing.")
        return False
    print(f"\n[X] {title} failed. This one is required.")
    return False


def main() -> int:
    """Run the bootstrap."""
    print("September 32 — bootstrap")
    print("=" * 70)

    if not step("Python toolchain", ["uv", "sync"]):
        return 1

    renpy_ok = step(
        "Ren'Py SDK (~163 MB)",
        ["uv", "run", "s32", "renpy", "install"],
        optional=True,
    )

    assets_ok = step(
        "Third-party assets (~90 MB, official sources)",
        ["uv", "run", "s32", "assets", "fetch"],
        optional=True,
    )

    if assets_ok:
        step("Processing assets", ["uv", "run", "s32", "assets", "install"], optional=True)
        step("Ren'Py image definitions", ["uv", "run", "s32", "assets", "images"], optional=True)

    step("Generated files", ["uv", "run", "s32", "schemas"], optional=True)
    step("Credits", ["uv", "run", "s32", "assets", "credits"], optional=True)

    print("\n" + "=" * 70)
    subprocess.run(["uv", "run", "s32", "doctor"], cwd=ROOT, check=False)

    print("\n" + "=" * 70)
    print("Next:")
    print("  uv run python scripts/check.py     run every quality gate")
    if renpy_ok:
        print("  uv run s32 renpy run               play the vertical slice")
    else:
        print("  uv run s32 renpy install           (retry the SDK download)")
    if not assets_ok:
        print("  uv run s32 assets fetch            (retry the assets)")
        print("  The game runs without them; it just has no art.")
    print("\nRead docs/production/PROJECT_STATE.md before starting work.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
