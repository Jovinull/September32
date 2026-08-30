"""``s32 doctor`` — one command that says whether the project is workable.

The value of this is a new contributor (or a returning one after two months)
running one command and learning exactly which of the many moving parts is not
set up, instead of discovering it one failure at a time.

Nothing here mutates anything. Every check reports ``ok``, ``warn`` or ``fail``,
and the exit code reflects only ``fail``: a missing asset pack is a ``warn``,
because the code, tests and simulator all work without it.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass
from typing import Literal

Status = Literal["ok", "warn", "fail"]

MARKS: dict[Status, str] = {"ok": "  ok  ", "warn": " warn ", "fail": " FAIL "}


@dataclass(frozen=True, slots=True)
class Check:
    """One diagnostic line."""

    name: str
    status: Status
    detail: str
    hint: str = ""

    def format(self) -> str:
        """Return the rendered line, with a hint on a second line if present."""
        line = f"[{MARKS[self.status]}] {self.name:<26} {self.detail}"
        return f"{line}\n{'':>10}-> {self.hint}" if self.hint else line


def run_checks() -> list[Check]:
    """Run every diagnostic and return the results in report order."""
    from s32tools import paths

    checks: list[Check] = [
        Check("python", "ok", f"{sys.version.split()[0]} on {platform.system()}"),
    ]

    root = paths.repo_root()
    checks.append(Check("repository", "ok", str(root)))

    checks.append(_check_renpy())
    checks.extend(_check_content())
    checks.extend(_check_assets())
    checks.append(_check_credits())
    checks.append(_check_schemas())
    checks.append(_check_placeholders())
    return checks


def _check_renpy() -> Check:
    """Is the pinned Ren'Py SDK available?"""
    from s32tools import renpy_sdk

    info = renpy_sdk.locate()
    if info is None:
        return Check(
            "ren'py sdk",
            "warn",
            f"not installed (pinned {renpy_sdk.RENPY_VERSION})",
            "s32 renpy install   — needed only to run or lint the game itself",
        )
    if not info.version.startswith(renpy_sdk.RENPY_VERSION):
        return Check(
            "ren'py sdk",
            "warn",
            f"{info.version} at {info.root}, but this project pins {renpy_sdk.RENPY_VERSION}",
            "lint and save behaviour can differ between point releases",
        )
    return Check("ren'py sdk", "ok", f"{info.version} at {info.root}")


def _check_content() -> list[Check]:
    """Does the authored content load and cross-reference cleanly?"""
    from s32_engine.definitions import load_library
    from s32_engine.errors import ContentError
    from s32tools import paths
    from s32tools.validation.content import validate_library

    try:
        library = load_library(paths.data_dir())
    except ContentError as exc:
        return [Check("content", "fail", str(exc), "s32 validate")]

    summary = (
        f"{len(library.storylets)} storylets, {len(library.anchors)} anchors, "
        f"{len(library.characters)} characters, {len(library.knowledge)} facts, "
        f"{len(library.locations)} locations, {len(library.items)} items"
    )
    checks = [Check("content", "ok", summary)]

    report = validate_library(library, rpy_root=paths.game_dir())
    if report.errors:
        checks.append(
            Check("content validation", "fail", f"{len(report.errors)} error(s)", "s32 validate")
        )
    elif report.warnings:
        checks.append(
            Check(
                "content validation", "warn", f"{len(report.warnings)} warning(s)", "s32 validate"
            )
        )
    else:
        checks.append(Check("content validation", "ok", "no findings"))
    return checks


def _check_assets() -> list[Check]:
    """Are third-party assets recorded, downloaded and installed?"""
    from s32tools import paths
    from s32tools.assets.install import counts_by_kind
    from s32tools.assets.manifest import check, load

    checks: list[Check] = []
    try:
        manifest = load(paths.catalog_path())
    except ValueError as exc:
        return [Check("asset manifest", "fail", str(exc))]

    installed = sum(1 for e in manifest.entries.values() if e.installed)
    checks.append(
        Check("asset manifest", "ok", f"{len(manifest.entries)} entries, {installed} installed")
    )

    problems = check(manifest, paths.evidence_dir())
    if problems:
        checks.append(
            Check(
                "asset licensing",
                "fail",
                f"{len(problems)} problem(s): {problems[0]}",
                "s32 assets verify",
            )
        )
    else:
        checks.append(Check("asset licensing", "ok", "evidence and terms recorded for every entry"))

    counts = counts_by_kind(paths.processed_dir())
    if not counts:
        checks.append(
            Check(
                "installed assets",
                "warn",
                "none processed",
                "s32 assets fetch && s32 assets install — the game runs with "
                "placeholders without them",
            )
        )
    else:
        checks.append(
            Check(
                "installed assets",
                "ok",
                ", ".join(f"{kind}: {count}" for kind, count in counts.items()),
            )
        )
    return checks


def _check_placeholders() -> Check:
    """How many image definitions would fall back to a placeholder.

    A development checkout with placeholders is fine and expected. A release
    build with even one is not, so this is reported rather than left to be
    discovered in a screenshot.
    """
    import re

    from s32tools import paths

    generated = paths.game_dir() / "engine" / "01_s32_images.rpy"
    if not generated.exists():
        return Check("game images", "warn", "not generated", "s32 assets images")

    referenced = re.findall(r's32_(?:sprite|bg)\("([^"]+)"', generated.read_text(encoding="utf-8"))
    missing = [p for p in referenced if not (paths.game_dir() / p).exists()]

    if not missing:
        return Check("game images", "ok", f"all {len(referenced)} resolve to real files")
    return Check(
        "game images",
        "warn",
        f"{len(missing)}/{len(referenced)} would show a MISSING ASSET placeholder",
        "s32 assets fetch && s32 assets install — fine in development, not in a release",
    )


def _check_credits() -> Check:
    """Are the generated credit files current?"""
    from s32tools import paths
    from s32tools.assets.generate_credits import check_all
    from s32tools.assets.manifest import load

    try:
        manifest = load(paths.catalog_path())
    except ValueError:
        return Check("credits", "fail", "manifest does not parse")

    stale = check_all(paths.repo_root(), manifest)
    if stale:
        return Check("credits", "fail", ", ".join(stale), "s32 assets credits")
    return Check("credits", "ok", "CREDITS, NOTICES, game credits all current")


def _check_schemas() -> Check:
    """Are the generated JSON Schemas current?"""
    from s32tools import paths
    from s32tools.validation.schemas import check_all

    stale = check_all(paths.schemas_dir())
    if stale:
        return Check("json schemas", "fail", ", ".join(stale), "s32 schemas")
    return Check("json schemas", "ok", "generated schemas match the engine's enums")


def report(checks: list[Check]) -> str:
    """Render the full report."""
    lines = ["September 32 — doctor", "=" * 60, ""]
    lines += [check.format() for check in checks]

    failures = sum(1 for c in checks if c.status == "fail")
    warnings = sum(1 for c in checks if c.status == "warn")
    lines += ["", f"{failures} failure(s), {warnings} warning(s)"]
    if not failures:
        lines.append(
            "The project is workable." if not warnings else "Workable, with caveats above."
        )
    return "\n".join(lines)


def exit_code(checks: list[Check]) -> int:
    """Return 1 if anything failed, else 0. Warnings never fail the command."""
    return 1 if any(c.status == "fail" for c in checks) else 0
