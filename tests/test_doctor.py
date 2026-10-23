"""Doctor must distinguish repository records from this clone's files."""

from s32tools.doctor import _check_assets


def test_asset_manifest_reports_records_without_claiming_local_installation() -> None:
    checks = _check_assets()

    manifest = next(check for check in checks if check.name == "asset manifest")
    assert "acquisition records" in manifest.detail
    assert "installed" not in manifest.detail
