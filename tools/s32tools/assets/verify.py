"""Verifying the committed asset catalogue and local asset installation.

Catalog verification is suitable for CI and clean clones: it checks the
licensing record, evidence and repository hygiene without requiring binaries.
Installed verification adds archive hashes and checks the processed files and
the copies Ren'Py loads.

Hashes are written to ``assets/catalog/acquisition.toml``. That file is
generated; ``assets.toml`` is hand-written and never touched by tooling.
"""

from __future__ import annotations

import json
import subprocess
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from s32tools.assets.fetch import sha256_of
from s32tools.assets.install import GAME_DIRS, KIND_DIRS
from s32tools.assets.manifest import ACQUISITION_FILENAME, Manifest, check, load

_ASSET_KIND_BY_TYPE = {
    "character": "character",
    "background": "background",
    "prop": "prop",
    "ui": "ui",
    "music": "audio",
    "sfx": "audio",
    "font": "font",
}
_FORBIDDEN_BINARY_PATHS = (
    "assets/.downloads",
    "assets/vendor",
    "assets/processed",
    "game/images/vendor",
    "game/audio/vendor",
    "game/gui/vendor",
)


@dataclass(slots=True)
class Acquisition:
    """What tooling discovered about one downloaded pack."""

    asset_id: str
    original_archive_name: str
    original_sha256: str
    retrieved_at: str
    status: str
    size_bytes: int = 0
    files_imported: list[str] | None = None
    processed_files: list[str] | None = None
    transformations: list[str] | None = None


def _toml_escape(value: str) -> str:
    """Escape a string for a TOML basic string."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _toml_list(values: list[str]) -> str:
    """Render a list of strings as a multi-line TOML array."""
    if not values:
        return "[]"
    inner = ",\n".join(f'  "{_toml_escape(v)}"' for v in values)
    return f"[\n{inner},\n]"


def write_acquisition(catalog_dir: Path, records: dict[str, Acquisition]) -> Path:
    """Write the generated acquisition record.

    Existing records for assets not in ``records`` are preserved, so updating a
    single asset does not erase what is known about the others.
    """
    path = catalog_dir / ACQUISITION_FILENAME
    merged: dict[str, Acquisition] = {}

    if path.exists():
        for asset_id, payload in (
            tomllib.loads(path.read_text(encoding="utf-8")).get("asset", {}).items()
        ):
            merged[asset_id] = Acquisition(
                asset_id=asset_id,
                original_archive_name=payload.get("original_archive_name", ""),
                original_sha256=payload.get("original_sha256", ""),
                retrieved_at=payload.get("retrieved_at", ""),
                status=payload.get("status", "pending"),
                size_bytes=payload.get("size_bytes", 0),
                files_imported=payload.get("files_imported"),
                processed_files=payload.get("processed_files"),
                transformations=payload.get("transformations"),
            )
    merged.update(records)

    lines = [
        "# GENERATED FILE — do not edit by hand.",
        "#",
        "# Written by `s32 assets fetch` and `s32 assets install`. Holds archive hashes,",
        "# timestamps, status, and which files were imported. The licence facts live",
        "# in assets.toml, which no tool writes.",
        "#",
        "# This file IS committed. It is how the repository records exactly which",
        "# bytes were reviewed, without containing them.",
        "",
    ]
    for asset_id, record in sorted(merged.items()):
        lines.append(f"[asset.{asset_id}]")
        lines.append(f'original_archive_name = "{_toml_escape(record.original_archive_name)}"')
        lines.append(f'original_sha256 = "{record.original_sha256}"')
        lines.append(f'retrieved_at = "{record.retrieved_at}"')
        lines.append(f'status = "{record.status}"')
        lines.append(f"size_bytes = {record.size_bytes}")
        if record.files_imported is not None:
            lines.append(f"files_imported = {_toml_list(record.files_imported)}")
        if record.processed_files is not None:
            lines.append(f"processed_files = {_toml_list(record.processed_files)}")
        if record.transformations is not None:
            lines.append(f"transformations = {_toml_list(record.transformations)}")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def record_download(
    catalog_dir: Path,
    asset_id: str,
    archive: Path,
    *,
    status: str = "downloaded",
) -> Acquisition:
    """Hash a downloaded archive and write its record."""
    record = Acquisition(
        asset_id=asset_id,
        original_archive_name=archive.name,
        original_sha256=sha256_of(archive),
        retrieved_at=datetime.now(UTC).isoformat(timespec="seconds"),
        status=status,
        size_bytes=archive.stat().st_size,
    )
    write_acquisition(catalog_dir, {asset_id: record})
    return record


def mark_installed(catalog_dir: Path, asset_ids: set[str]) -> None:
    """Record that downloaded packs have been extracted and processed."""
    path = catalog_dir / ACQUISITION_FILENAME
    if not path.is_file():
        return
    payloads = tomllib.loads(path.read_text(encoding="utf-8")).get("asset", {})
    records: dict[str, Acquisition] = {}
    for asset_id in sorted(asset_ids):
        payload = payloads.get(asset_id)
        if payload is None:
            continue
        records[asset_id] = Acquisition(
            asset_id=asset_id,
            original_archive_name=payload.get("original_archive_name", ""),
            original_sha256=payload.get("original_sha256", ""),
            retrieved_at=payload.get("retrieved_at", ""),
            status="installed",
            size_bytes=payload.get("size_bytes", 0),
            files_imported=payload.get("files_imported"),
            processed_files=payload.get("processed_files"),
            transformations=payload.get("transformations"),
        )
    if records:
        write_acquisition(catalog_dir, records)


def verify_integrity(manifest: Manifest, downloads: Path) -> list[str]:
    """Re-hash every downloaded archive and report mismatches."""
    problems: list[str] = []
    for asset_id, entry in sorted(manifest.entries.items()):
        if not entry.original_sha256 or not entry.original_archive_name:
            continue
        archive = downloads / asset_id / entry.original_archive_name
        if not archive.exists():
            problems.append(
                f"{asset_id}: manifest records {entry.original_archive_name} but it is not in "
                f"{downloads / asset_id} (re-fetch with `s32 assets fetch --asset {asset_id}`)"
            )
            continue
        actual = sha256_of(archive)
        if actual != entry.original_sha256:
            problems.append(
                f"{asset_id}: SHA-256 mismatch\n"
                f"  expected {entry.original_sha256}\n"
                f"  actual   {actual}\n"
                "  The file on disk is NOT the one that was reviewed. Do not use it."
            )
    return problems


def verify_repository_hygiene(repo_root: Path) -> list[str]:
    """Fail if third-party binaries are tracked in any forbidden directory."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", *_FORBIDDEN_BINARY_PATHS],
            cwd=repo_root,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return [f"could not inspect tracked asset files with git: {exc}"]
    tracked = [
        path.decode("utf-8", errors="replace") for path in result.stdout.split(b"\0") if path
    ]
    if not tracked:
        return []
    return ["third-party binaries are tracked in forbidden paths: " + ", ".join(tracked)]


def verify_catalog(
    catalog_path: Path, evidence_root: Path, repo_root: Path
) -> tuple[Manifest, list[str]]:
    """Check catalogue facts, evidence, recorded hashes and repository hygiene."""
    manifest = load(catalog_path)
    problems = check(manifest, evidence_root)
    problems.extend(verify_repository_hygiene(repo_root))
    return manifest, problems


def verify_installed(
    catalog_path: Path,
    evidence_root: Path,
    downloads: Path,
    repo_root: Path,
) -> tuple[Manifest, list[str]]:
    """Check the catalogue plus downloaded archives and installed game files."""
    manifest, problems = verify_catalog(catalog_path, evidence_root, repo_root)
    problems.extend(verify_integrity(manifest, downloads))
    problems.extend(verify_installed_outputs(manifest, repo_root))
    return manifest, problems


def verify_installed_outputs(manifest: Manifest, repo_root: Path) -> list[str]:
    """Check that import-log outputs exist and game copies match processed files."""
    import_log = repo_root / "assets" / "catalog" / "import_log.json"
    if not import_log.is_file():
        return [f"installed asset import log is missing: {import_log}"]
    try:
        payload = json.loads(import_log.read_text(encoding="utf-8"))
        packs = payload["packs"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return [f"installed asset import log is invalid: {exc}"]

    problems: list[str] = []
    expected_by_kind: dict[str, set[str]] = {
        kind: set() for kind in set(_ASSET_KIND_BY_TYPE.values())
    }
    for asset_id, entry in sorted(manifest.entries.items()):
        if not entry.installed or entry.type not in _ASSET_KIND_BY_TYPE:
            continue
        names = packs.get(asset_id, {}).get("names", [])
        if not isinstance(names, list) or not names:
            problems.append(f"{asset_id}: installed asset has no output names in import_log.json")
            continue
        kind = _ASSET_KIND_BY_TYPE[entry.type]
        processed_dir = repo_root / "assets" / "processed" / KIND_DIRS[kind]
        game_dir = repo_root / "game" / GAME_DIRS[kind]
        for name in names:
            if not isinstance(name, str) or Path(name).name != name:
                problems.append(f"{asset_id}: invalid installed output name {name!r}")
                continue
            expected_by_kind[kind].add(name)
            processed = processed_dir / name
            shipped = game_dir / name
            if not processed.is_file():
                problems.append(f"{asset_id}: processed output is missing: {processed}")
            if not shipped.is_file():
                problems.append(f"{asset_id}: game copy is missing: {shipped}")
            elif processed.is_file() and processed.read_bytes() != shipped.read_bytes():
                problems.append(f"{asset_id}: game copy differs from processed output: {name}")

    for kind, names in expected_by_kind.items():
        processed_dir = repo_root / "assets" / "processed" / KIND_DIRS[kind]
        game_dir = repo_root / "game" / GAME_DIRS[kind]
        for label, directory in (("processed", processed_dir), ("game", game_dir)):
            if not directory.is_dir():
                continue
            actual = {path.name for path in directory.glob("*") if path.is_file()}
            for name in sorted(actual - names):
                problems.append(
                    f"unexpected {label} asset output for {kind}: {directory / name}; "
                    "rebuild with `s32 assets install` from configured sources"
                )
    return problems
