"""Extracting downloaded archives and organising them into the vendor tree.

Two directories, one rule each:

``assets/vendor/<asset_id>/``
    Untouched originals, exactly as they came out of the archive. Nothing ever
    writes here twice, and nothing edits in place. If a processing step turns
    out to be wrong, this is what it is redone from.

``assets/processed/<kind>/``
    Game-ready derivatives, produced deterministically from vendor originals by
    a recorded transformation. Deleting this directory is always safe: `s32
    assets import` rebuilds it.

Both are gitignored (ADR-0003), so this step runs on each developer's machine.

Renaming follows ``docs/production/ASSET_NAMING.md``. The original filename is
kept in the import log so traceability survives the rename -- a game-side name
like ``char_iris_school_summer_smile`` must always be resolvable back to the
file the artist shipped.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

#: Members that are never extracted: archive metadata and OS cruft.
_SKIP = re.compile(r"(^|/)(__MACOSX/|\._|\.DS_Store$|Thumbs\.db$)")

#: Extensions we accept out of an archive. Anything else (executables, scripts)
#: is refused rather than trusted, because an asset pack has no business
#: shipping them.
ALLOWED_SUFFIXES = frozenset(
    {".png", ".webp", ".jpg", ".jpeg", ".ogg", ".mp3", ".wav", ".ttf", ".otf", ".txt", ".md", ".pdf"}
)


@dataclass(slots=True)
class ImportResult:
    """What one archive extraction produced."""

    asset_id: str
    extracted: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    refused: list[str] = field(default_factory=list)
    target: Path | None = None

    @property
    def count(self) -> int:
        """Number of files extracted."""
        return len(self.extracted)


def _safe_member(name: str, root: Path) -> Path | None:
    """Resolve an archive member to a path inside ``root``, or ``None``.

    Guards against path traversal (``../``) and absolute paths in the archive.
    These packs are from reputable creators, but an extraction routine that
    trusts archive member names is a bug regardless of the source.
    """
    if name.endswith("/"):
        return None
    candidate = (root / name).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def extract(archive: Path, asset_id: str, vendor_root: Path) -> ImportResult:
    """Extract one archive into ``assets/vendor/<asset_id>/``."""
    vendor_root = vendor_root.resolve()
    target = vendor_root / asset_id
    result = ImportResult(asset_id=asset_id, target=target)

    if not archive.exists():
        raise FileNotFoundError(f"archive not found: {archive}")

    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        for name in zf.namelist():
            if _SKIP.search(name) or name.endswith("/"):
                result.skipped.append(name)
                continue

            suffix = Path(name).suffix.lower()
            if suffix not in ALLOWED_SUFFIXES:
                result.refused.append(name)
                continue

            destination = _safe_member(name, target)
            if destination is None:
                result.refused.append(f"{name} (unsafe path)")
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(name) as source, destination.open("wb") as handle:
                while chunk := source.read(1 << 20):
                    handle.write(chunk)
            result.extracted.append(str(destination.relative_to(vendor_root)).replace("\\", "/"))

    result.extracted.sort()
    return result


def inventory(vendor_root: Path, asset_id: str) -> dict[str, int]:
    """Return a count of files by extension for an extracted pack."""
    directory = vendor_root / asset_id
    counts: dict[str, int] = {}
    if not directory.is_dir():
        return counts
    for path in directory.rglob("*"):
        if path.is_file():
            counts[path.suffix.lower()] = counts.get(path.suffix.lower(), 0) + 1
    return dict(sorted(counts.items()))


def describe_tree(vendor_root: Path, asset_id: str, *, max_depth: int = 2) -> list[str]:
    """Return a shallow listing of an extracted pack, for the import report."""
    directory = vendor_root / asset_id
    if not directory.is_dir():
        return []
    lines: list[str] = []
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        if len(relative.parts) > max_depth:
            continue
        marker = "/" if path.is_dir() else ""
        lines.append(f"{'  ' * (len(relative.parts) - 1)}{relative.name}{marker}")
    return lines


def extract_downloads(downloads_root: Path, vendor_root: Path) -> dict[str, ImportResult]:
    """Extract every downloaded archive into ``assets/vendor/``.

    The step between ``fetch`` and processing. It exists as a function rather
    than as part of ``fetch`` because extraction is idempotent and cheap, while
    downloading is neither: re-running the pipeline after a naming change should
    not re-download 90 MB.

    Nested archives are handled. Two of the character packs ship a zip
    containing one zip per character, and a caller that did not expect that
    would silently extract nothing.
    """
    results: dict[str, ImportResult] = {}
    if not downloads_root.is_dir():
        return results

    nested_dir = downloads_root / "_nested"

    for pack_dir in sorted(p for p in downloads_root.iterdir() if p.is_dir()):
        if pack_dir.name.startswith("_"):
            continue
        archives = sorted(p for p in pack_dir.iterdir() if p.suffix.lower() == ".zip")
        if not archives:
            continue

        merged = ImportResult(asset_id=pack_dir.name, target=vendor_root / pack_dir.name)
        for archive in archives:
            result = extract(archive, pack_dir.name, vendor_root)
            merged.extracted.extend(result.extracted)
            merged.skipped.extend(result.skipped)
            merged.refused.extend(result.refused)

            # An archive whose only contents were more archives.
            inner = [name for name in result.refused if name.lower().endswith(".zip")]
            if inner:
                merged.refused = [name for name in merged.refused if name not in inner]
                merged.extracted.extend(
                    _extract_nested(archive, inner, pack_dir.name, vendor_root, nested_dir)
                )

        merged.extracted.sort()
        results[pack_dir.name] = merged
    return results


def _extract_nested(
    archive: Path,
    members: list[str],
    asset_id: str,
    vendor_root: Path,
    scratch: Path,
) -> list[str]:
    """Extract archives that were themselves inside an archive."""
    scratch.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []

    with zipfile.ZipFile(archive) as outer:
        for name in members:
            inner_path = scratch / Path(name).name
            inner_path.write_bytes(outer.read(name))
            extracted.extend(extract(inner_path, asset_id, vendor_root).extracted)
    return extracted
