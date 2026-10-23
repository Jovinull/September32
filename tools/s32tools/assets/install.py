"""Turning vendor originals into the files the game actually loads.

The pipeline has three stages and each one is idempotent:

``assets/vendor/<id>/``      untouched originals (from ``s32 assets import``)
``assets/processed/<kind>/`` renamed, graded, project-named files
``game/{images,audio,gui}/vendor/`` what Ren'Py loads

The last hop is a copy rather than a symlink because Ren'Py's archiver and
Windows both handle copies more predictably, and because the whole tree is
rebuildable in seconds.

Everything from ``assets/`` down is gitignored (ADR-0003), so this runs on each
developer's machine after ``s32 assets fetch``. What *is* committed is the
selection: which files were kept, under which names, with which treatment. That
lives in the import log this module writes.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from s32tools.assets import naming
from s32tools.assets.process import TREATMENTS, ProcessResult, process_file

#: Which vendor packs feed which processed directory.
KIND_DIRS: dict[str, str] = {
    "character": "characters",
    "background": "backgrounds",
    "prop": "props",
    "ui": "ui",
    "audio": "audio",
    "font": "fonts",
}

#: Where each processed kind lands inside the Ren'Py tree.
GAME_DIRS: dict[str, str] = {
    "character": "images/vendor/characters",
    "background": "images/vendor/backgrounds",
    "prop": "images/vendor/props",
    "ui": "gui/vendor",
    "audio": "audio/vendor",
    "font": "gui/vendor/fonts",
}

#: Kenney's UI pack ships the same widgets in six colourways under
#: ``PNG/<Colour>/Default``. Only the neutral grey set is taken: the shipped
#: interface must not read as "Kenney UI" (see
#: docs/style/VISUAL_DESIGN_SYSTEM.md), so this is neutral scaffolding, not a
#: theme, and importing all six colours would invite using them.
UI_KEEP_DIR = ("PNG", "Grey", "Default")

#: Only the flat-colour prop silhouettes are useful as archive icons; the
#: outlined and shaded variants fight the treatment.
PROP_KEEP_PREFIX = "genericItem_color_"

#: Fonts: only the weights the design system actually uses.
FONT_KEEP: tuple[str, ...] = (
    "SourceSans3-Regular",
    "SourceSans3-It",
    "SourceSans3-Semibold",
    "SourceSans3-Bold",
    "SourceSerif4-Regular",
    "SourceSerif4-It",
    "SourceSerif4-Semibold",
)


@dataclass(slots=True)
class InstallReport:
    """Everything one install pass did, for the log and for the CLI summary."""

    processed: dict[str, ProcessResult] = field(default_factory=dict)
    copied_to_game: int = 0
    missing_packs: list[str] = field(default_factory=list)

    def total_written(self) -> int:
        """Total files written to ``assets/processed``."""
        return sum(len(r.written) for r in self.processed.values())


def _should_keep(path: Path, kind: str) -> bool:
    """Return whether a vendor file is wanted at all."""
    if kind == "ui":
        return path.suffix.lower() == ".png" and path.parts[-4:-1] == UI_KEEP_DIR
    if kind == "prop":
        return path.stem.startswith(PROP_KEEP_PREFIX)
    if kind == "font":
        return path.suffix.lower() == ".ttf" and any(path.stem.startswith(f) for f in FONT_KEEP)
    if kind == "audio":
        return path.suffix.lower() == ".ogg"
    return path.suffix.lower() in {".webp", ".png"}


def _target_name(path: Path, kind: str) -> str | None:
    """Return the project filename for a vendor file, or ``None`` if unmappable."""
    suffix = path.suffix.lower()
    if kind == "character":
        return naming.character_filename(path.stem, suffix)
    if kind == "background":
        return naming.background_filename(path.stem, suffix)
    if kind == "prop":
        return naming.prop_filename(path.stem, ".webp")
    if kind == "ui":
        return naming.ui_filename(path.stem, suffix)
    if kind == "audio":
        return naming.audio_filename(path.stem, suffix)
    if kind == "font":
        return path.name
    return None


def install_pack(
    asset_id: str,
    vendor_root: Path,
    processed_root: Path,
) -> ProcessResult:
    """Process one vendor pack into ``assets/processed/``."""
    kind = naming.classify(vendor_root / asset_id, asset_id)
    result = ProcessResult()
    source_dir = vendor_root / asset_id
    if not source_dir.is_dir():
        return result

    treatment = TREATMENTS.get(kind)
    target_dir = processed_root / KIND_DIRS.get(kind, "other")

    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        if not _should_keep(path, kind):
            result.skipped.append(path.name)
            continue

        name = _target_name(path, kind)
        if name is None:
            result.unmapped.append(path.name)
            continue

        destination = target_dir / name
        if kind in {"audio", "font"}:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
        else:
            assert treatment is not None  # noqa: S101 - every image kind has one
            process_file(path, destination, treatment)
        result.written.append(name)

    if treatment is not None:
        result.transformations = treatment.describe()
    result.written.sort()
    return result


def copy_to_game(processed_root: Path, game_root: Path) -> int:
    """Copy processed files into the Ren'Py tree. Returns the file count."""
    count = 0
    for kind, processed_dir in KIND_DIRS.items():
        source = processed_root / processed_dir
        if not source.is_dir():
            continue
        destination = game_root / GAME_DIRS[kind]
        destination.mkdir(parents=True, exist_ok=True)
        for path in sorted(source.rglob("*")):
            if path.is_file():
                (destination / path.name).write_bytes(path.read_bytes())
                count += 1
    return count


def install_all(
    asset_ids: list[str],
    vendor_root: Path,
    processed_root: Path,
    game_root: Path,
    *,
    to_game: bool = True,
) -> InstallReport:
    """Rebuild generated asset outputs from the named packs only.

    ``processed_root`` and the game vendor folders are generated caches. Clear
    them before processing so assets from a previously evaluated or rejected
    pack cannot survive a later approved install and enter a build.
    """
    for folder in set(KIND_DIRS.values()):
        target = processed_root / folder
        if target.is_dir():
            shutil.rmtree(target)
    if to_game:
        # Clear deepest first because font assets live under gui/vendor/fonts.
        for folder in sorted(
            set(GAME_DIRS.values()), key=lambda item: item.count("/"), reverse=True
        ):
            target = game_root / folder
            if target.is_dir():
                shutil.rmtree(target)

    report = InstallReport()
    for asset_id in asset_ids:
        if not (vendor_root / asset_id).is_dir():
            report.missing_packs.append(asset_id)
            continue
        report.processed[asset_id] = install_pack(asset_id, vendor_root, processed_root)
    if to_game:
        report.copied_to_game = copy_to_game(processed_root, game_root)
    return report


def write_log(report: InstallReport, path: Path) -> Path:
    """Write the import log.

    This file IS committed even though the assets are not: it is the record of
    which third-party files were selected, what they were renamed to, and what
    was done to them. Without it, a project-side filename would be untraceable
    back to the artist's original.
    """
    payload = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "packs": {
            asset_id: {
                "files_written": len(result.written),
                "files_skipped": len(result.skipped),
                "unmapped": result.unmapped,
                "transformations": result.transformations,
                "names": result.written,
            }
            for asset_id, result in sorted(report.processed.items())
        },
        "missing_packs": report.missing_packs,
        "copied_to_game": report.copied_to_game,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def expression_matrix(processed_root: Path) -> dict[str, dict[str, list[str]]]:
    """Return ``{character: {outfit: [expressions]}}`` from processed sprites.

    Feeds the Ren'Py image definition generator and the art gap analysis: a
    character missing ``crying`` should be a documented gap, not a crash the
    first time a scene asks for it.
    """
    matrix: dict[str, dict[str, set[str]]] = {}
    directory = processed_root / "characters"
    if not directory.is_dir():
        return {}

    for path in sorted(directory.glob("char_*")):
        parts = path.stem.split("_")
        if len(parts) < 4:
            continue
        character = parts[1]
        # Outfit names contain underscores (`school_summer`), and so do some
        # expression names (`pout_angry`). The outfit is always the known token
        # from naming.OUTFITS, so match the longest known prefix.
        remainder = "_".join(parts[2:])
        outfit, expression = _split_outfit(remainder)
        matrix.setdefault(character, {}).setdefault(outfit, set()).add(expression)

    return {
        character: {outfit: sorted(expressions) for outfit, expressions in sorted(outfits.items())}
        for character, outfits in sorted(matrix.items())
    }


def _split_outfit(remainder: str) -> tuple[str, str]:
    """Split ``school_summer_pout_angry`` into ``(school_summer, pout_angry)``."""
    known = sorted(set(naming.OUTFITS.values()), key=len, reverse=True)
    for outfit in known:
        if remainder.startswith(outfit + "_"):
            return outfit, remainder[len(outfit) + 1 :]
    head, _, tail = remainder.partition("_")
    return head, tail or "neutral"


def counts_by_kind(processed_root: Path) -> dict[str, int]:
    """Return how many processed files exist per kind, for ``s32 doctor``."""
    counts: Counter[str] = Counter()
    for kind, directory in KIND_DIRS.items():
        path = processed_root / directory
        if path.is_dir():
            counts[kind] = sum(1 for p in path.rglob("*") if p.is_file())
    return dict(sorted(counts.items()))
