"""The asset catalogue is verifiable without local third-party binaries."""

from __future__ import annotations

from pathlib import Path

from s32tools import paths
from s32tools.assets.manifest import load
from s32tools.assets.verify import (
    mark_installed,
    verify_catalog,
    verify_installed_outputs,
    verify_integrity,
)


def test_catalog_verification_does_not_need_downloaded_archives() -> None:
    """Fresh assetless clones can still check licensing and repository hygiene."""
    manifest, problems = verify_catalog(
        paths.catalog_path(), paths.evidence_dir(), paths.repo_root()
    )

    assert len(manifest.entries) == 12
    assert not problems, "\n".join(problems)


def test_installed_verification_fails_when_a_recorded_archive_is_missing(
    tmp_path: Path,
) -> None:
    manifest = load(paths.catalog_path())

    problems = verify_integrity(manifest, tmp_path / "empty-download-cache")

    assert problems
    assert any("is not in" in problem for problem in problems)


def test_installed_verification_fails_when_a_recorded_archive_is_corrupt(
    tmp_path: Path,
) -> None:
    manifest = load(paths.catalog_path())
    entry = next(
        item
        for item in manifest.entries.values()
        if item.original_archive_name and item.original_sha256
    )
    archive = tmp_path / entry.id / entry.original_archive_name
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b"not the reviewed archive")

    problems = verify_integrity(manifest, tmp_path)

    assert any("SHA-256 mismatch" in problem for problem in problems)


def test_install_marks_a_fetched_pack_installed_without_changing_its_hash(
    tmp_path: Path,
) -> None:
    """A complete bootstrap should leave doctor and full verification in sync."""
    import tomllib

    catalog_dir = tmp_path / "catalog"
    catalog_dir.mkdir()
    acquisition = catalog_dir / "acquisition.toml"
    recorded_hash = "a" * 64
    acquisition.write_text(
        "[asset.example_pack]\n"
        'original_archive_name = "pack.zip"\n'
        f'original_sha256 = "{recorded_hash}"\n'
        'retrieved_at = "2026-10-23T10:00:00+00:00"\n'
        'status = "downloaded"\n'
        "size_bytes = 12\n",
        encoding="utf-8",
    )

    mark_installed(catalog_dir, {"example_pack"})

    result = tomllib.loads(acquisition.read_text(encoding="utf-8"))["asset"]["example_pack"]
    assert result["status"] == "installed"
    assert result["original_sha256"] == recorded_hash


def test_install_rebuilds_game_outputs_without_stale_unapproved_assets(tmp_path: Path) -> None:
    """A rejected pack cached locally must not leak into the game tree."""
    from s32tools.assets.install import install_all

    vendor = tmp_path / "vendor"
    fonts = vendor / "source_sans_3"
    fonts.mkdir(parents=True)
    (fonts / "SourceSans3-Regular.ttf").write_bytes(b"approved-font")

    processed = tmp_path / "processed"
    stale_processed = processed / "characters" / "char_rejected.webp"
    stale_processed.parent.mkdir(parents=True)
    stale_processed.write_bytes(b"rejected-sprite")

    game = tmp_path / "game"
    stale_game = game / "images/vendor/characters/char_rejected.webp"
    stale_game.parent.mkdir(parents=True)
    stale_game.write_bytes(b"rejected-sprite")

    report = install_all(["source_sans_3"], vendor, processed, game)

    assert report.processed["source_sans_3"].written == ["SourceSans3-Regular.ttf"]
    assert not stale_processed.exists()
    assert not stale_game.exists()
    assert (game / "gui/vendor/fonts/SourceSans3-Regular.ttf").read_bytes() == b"approved-font"


def test_installed_verification_rejects_extra_unapproved_game_assets(tmp_path: Path) -> None:
    """Full verification must catch stale files that would leak into a build."""
    import json

    manifest = load(paths.catalog_path())
    for entry in manifest.entries.values():
        entry.status = "pending"
    manifest.entries["source_sans_3"].status = "installed"

    approved_name = "SourceSans3-Regular.ttf"
    import_log = tmp_path / "assets/catalog/import_log.json"
    import_log.parent.mkdir(parents=True)
    import_log.write_text(
        json.dumps({"packs": {"source_sans_3": {"names": [approved_name]}}}),
        encoding="utf-8",
    )
    for directory in (
        tmp_path / "assets/processed/fonts",
        tmp_path / "game/gui/vendor/fonts",
        tmp_path / "game/images/vendor/characters",
    ):
        directory.mkdir(parents=True)
    (tmp_path / "assets/processed/fonts" / approved_name).write_bytes(b"approved")
    (tmp_path / "game/gui/vendor/fonts" / approved_name).write_bytes(b"approved")
    (tmp_path / "game/images/vendor/characters/char_rejected.webp").write_bytes(b"rejected")

    problems = verify_installed_outputs(manifest, tmp_path)

    assert any("unexpected game asset output" in problem for problem in problems)
