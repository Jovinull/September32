"""Verifying downloaded assets and recording what was actually acquired.

Three separate questions, answered together because they fail together:

1. **Integrity** — do the bytes on disk still hash to what the manifest records?
2. **Completeness** — does every manifest entry have evidence, and does every
   installed entry have a hash and a date?
3. **Licence hygiene** — is anything recorded in a way that would let a future
   reader draw the wrong conclusion (a payment model in the licence field, an
   attribution requirement with no credit text)?

Hashes are written to ``assets/catalog/acquisition.toml``. That file is
generated; ``assets.toml`` is hand-written and never touched by tooling.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from s32tools.assets.fetch import sha256_of
from s32tools.assets.manifest import ACQUISITION_FILENAME, Manifest, check, load


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

    Existing records for assets not in ``records`` are preserved, so verifying a
    single asset does not erase what is known about the others.
    """
    path = catalog_dir / ACQUISITION_FILENAME
    merged: dict[str, Acquisition] = {}

    if path.exists():
        import tomllib

        for asset_id, payload in tomllib.loads(path.read_text(encoding="utf-8")).get("asset", {}).items():
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
        "# Written by `s32 assets verify` and `s32 assets import`. Holds only what",
        "# tooling discovers: archive hashes, acquisition timestamps, and which files",
        "# were imported. The licence facts live in assets.toml, which no tool writes.",
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


def verify_all(catalog_path: Path, evidence_root: Path, downloads: Path) -> tuple[Manifest, list[str]]:
    """Run every verification and return the manifest plus the problems found."""
    manifest = load(catalog_path)
    problems = check(manifest, evidence_root)
    problems.extend(verify_integrity(manifest, downloads))
    return manifest, problems
