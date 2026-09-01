"""Tests over the project's real content, plus the tooling that guards it.

These fail when someone writes a broken storylet, lets a generated file drift,
or introduces a dependency the engine cannot have. They are expected to change
as the content grows; that is what makes them useful.
"""

from __future__ import annotations

import ast
import json
import pathlib
import sys
from pathlib import Path

import pytest

from s32_engine.definitions import load_library
from s32_engine.errors import ContentError
from s32_engine.version import GAME_VERSION
from s32tools import paths
from s32tools.validation import schemas, static_analysis
from s32tools.validation.content import schema_validate, validate_library

#: Standard-library modules the engine is allowed to import.
_STDLIB = set(sys.stdlib_module_names)


# ---------------------------------------------------------------------------
# The engine's isolation
# ---------------------------------------------------------------------------


def test_the_engine_imports_only_the_standard_library():
    """Ren'Py ships its own interpreter and cannot install wheels.

    A third-party import here would work in pytest and fail at game launch, so
    the whole package is walked rather than trusting discipline.
    """
    engine_dir = paths.repo_root() / "game" / "python-packages" / "s32_engine"
    offenders: list[str] = []

    for path in sorted(engine_dir.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]] if node.level == 0 else []
            else:
                continue
            for name in names:
                if name and name not in _STDLIB and name != "s32_engine":
                    offenders.append(f"{path.name}: {name}")

    assert not offenders, "s32_engine must import only the standard library; found: " + ", ".join(
        offenders
    )


def test_the_engine_makes_no_network_calls():
    """ADR-0004: the shipped game has no network access at all."""
    engine_dir = paths.repo_root() / "game" / "python-packages" / "s32_engine"
    forbidden = {"socket", "urllib", "http", "ftplib", "smtplib", "asyncio", "ssl"}
    offenders: list[str] = []

    for path in sorted(engine_dir.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [(node.module or "").split(".")[0]]
            else:
                continue
            offenders.extend(f"{path.name}: {n}" for n in names if n in forbidden)

    assert not offenders, "no networking in the shipped engine: " + ", ".join(offenders)


# ---------------------------------------------------------------------------
# The real content
# ---------------------------------------------------------------------------


def test_the_real_content_loads(real_library):
    assert real_library.storylets
    assert real_library.anchors
    assert real_library.characters


def test_the_real_content_validates(real_library):
    report = validate_library(real_library, rpy_root=paths.game_dir())
    assert not report.errors, "\n" + report.format()


def test_the_real_content_matches_its_schemas():
    report = schema_validate(paths.data_dir(), paths.schemas_dir())
    assert not report.errors, "\n" + report.format()


def test_the_real_content_has_no_unreachable_storylets(real_library):
    report = static_analysis.analyse(real_library)
    assert not report.errors, "\n" + report.format()


def test_every_storylet_points_at_a_label_that_exists(real_library):
    """Caught here in a second; caught in-game as a crash mid-scene."""
    labels: set[str] = set()
    for path in (paths.game_dir()).rglob("*.rpy"):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("label "):
                labels.add(line[6:].split(":")[0].strip())

    missing = [s.id for s in real_library.storylets.values() if s.label not in labels]
    missing += [a.id for a in real_library.anchors.values() if a.label not in labels]
    assert not missing, f"no Ren'Py label for: {', '.join(missing)}"


def test_ids_match_their_filenames(real_library):
    """One entity per file, named after its id, keeps diffs readable."""
    for subdir in ("characters", "locations", "knowledge", "items", "storylets", "anchors"):
        for path in sorted((paths.data_dir() / subdir).glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            assert payload["id"] == path.stem, f"{path} declares id {payload['id']!r}"


def test_duplicate_ids_are_rejected(tmp_path: Path):
    (tmp_path / "characters").mkdir()
    for name in ("a.json", "b.json"):
        (tmp_path / "characters" / name).write_text(
            json.dumps({"id": "iris", "display_name": "Iris", "role": "x"}), encoding="utf-8"
        )

    with pytest.raises(ContentError, match="duplicate id"):
        load_library(tmp_path)


def test_malformed_json_names_the_file(tmp_path: Path):
    (tmp_path / "characters").mkdir()
    (tmp_path / "characters" / "broken.json").write_text("{not json", encoding="utf-8")

    with pytest.raises(ContentError, match="invalid JSON"):
        load_library(tmp_path)


def test_a_missing_required_field_names_the_file(tmp_path: Path):
    (tmp_path / "storylets").mkdir()
    (tmp_path / "storylets" / "x.json").write_text(json.dumps({"id": "x"}), encoding="utf-8")

    with pytest.raises(ContentError, match="missing required field 'label'"):
        load_library(tmp_path)


# ---------------------------------------------------------------------------
# Generated files must not drift
# ---------------------------------------------------------------------------


def test_json_schemas_are_up_to_date():
    """Generated schemas must match the engine.

    They are generated from the engine's enums, so drift means the validator
    would accept content the engine itself rejects.
    """
    stale = schemas.check_all(paths.schemas_dir())
    assert not stale, "run `s32 schemas`: " + ", ".join(stale)


def test_credit_files_are_up_to_date():
    from s32tools.assets.generate_credits import check_all
    from s32tools.assets.manifest import load

    manifest = load(paths.catalog_path())
    stale = check_all(paths.repo_root(), manifest)
    assert not stale, "run `s32 assets credits`: " + ", ".join(stale)


def test_credit_generation_does_not_depend_on_todays_date():
    """The freshness gate used to fail every midnight.

    ``THIRD_PARTY_NOTICES.md`` embedded ``datetime.now()``, and the gate
    compares file contents, so a build run the day after the last regeneration
    reported the notices stale on content nobody had touched. Rendering twice
    under two different wall clocks is the direct check for that: same
    catalogue, same bytes.
    """
    from s32tools.assets import generate_credits
    from s32tools.assets.generate_credits import OUTPUTS, render
    from s32tools.assets.manifest import load

    manifest = load(paths.catalog_path())
    first = {name: render(name, manifest) for name in OUTPUTS}

    second = {name: render(name, manifest) for name in OUTPUTS}
    assert first == second

    # Rendering twice in one second proves little on its own, so the invariant
    # is stated directly: there is no clock in the generator to read. Parsed
    # rather than grepped, because a local import inside a function would
    # satisfy the namespace check and reintroduce the bug -- and because the
    # docstring explaining all this necessarily mentions `datetime.now`.
    assert not hasattr(generate_credits, "datetime")
    tree = ast.parse(pathlib.Path(generate_credits.__file__).read_text(encoding="utf-8"))
    clocks = {"datetime", "date", "time", "monotonic", "now", "today"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import | ast.ImportFrom):
            names = [alias.name.split(".")[0] for alias in node.names]
            names.append((getattr(node, "module", None) or "").split(".")[0])
            assert not clocks & set(names), f"{names} would put a clock in the generator"

    # And the date it does print comes from the committed catalogue, so it
    # moves only when a person records reading the terms again.
    verified = sorted(e.license_verified for e in manifest.entries.values() if e.license_verified)
    assert verified[-1] in first["THIRD_PARTY_NOTICES.md"]


def test_the_game_version_matches_options_rpy():
    """`define` runs before any import, so options.rpy holds a literal.

    This is the check that keeps the literal honest.
    """
    text = (paths.game_dir() / "options.rpy").read_text(encoding="utf-8")
    assert f'define config.version = "{GAME_VERSION}"' in text, (
        f"game/options.rpy must declare config.version = {GAME_VERSION!r} "
        "to match s32_engine.version.GAME_VERSION"
    )


# ---------------------------------------------------------------------------
# The asset manifest
# ---------------------------------------------------------------------------


def test_every_manifest_entry_has_licence_evidence():
    from s32tools.assets.manifest import check, load

    manifest = load(paths.catalog_path())
    problems = check(manifest, paths.evidence_dir())
    assert not problems, "\n" + "\n".join(problems)


def test_no_third_party_binaries_are_committed():
    """ADR-0003. The .gitignore enforces it; this proves the .gitignore works."""
    import subprocess

    result = subprocess.run(
        ["git", "ls-files", "assets/vendor", "assets/processed", "game/images/vendor"],
        cwd=paths.repo_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    assert not tracked, "third-party binaries must not be committed: " + ", ".join(tracked[:10])


def test_every_cast_member_with_an_asset_id_has_one_that_looks_real(real_library):
    for character in real_library.characters.values():
        if character.asset_id is not None:
            assert character.asset_id.startswith("pm_a0"), (
                f"{character.id} names asset {character.asset_id!r}, which is not from the "
                "chosen character system (ADR-0005)"
            )
