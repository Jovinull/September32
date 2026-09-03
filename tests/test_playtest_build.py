"""What a tester receives, and what they must not.

The base directory Ren'Py scans when it builds is this repository. That is
convenient right up until it is not: Ren'Py's own default rules end with a
catch-all that sweeps everything into the distribution, so a build made without
thinking about it would hand a tester the canon, the character briefs, the
internal reports, the scene cards and every milestone post-mortem.

These tests are the reason that cannot happen quietly.
"""

from __future__ import annotations

import json
import re

import pytest

from s32_engine.definitions import load_library
from s32_engine.version import GAME_VERSION
from s32tools import build as build_module
from s32tools import paths

OPTIONS = paths.game_dir() / "options.rpy"


@pytest.fixture(scope="module")
def options() -> str:
    return OPTIONS.read_text(encoding="utf-8")


def _classified(options: str) -> dict[str, str | None]:
    """Return the classify rules from options.rpy, in the order they appear."""
    rules: dict[str, str | None] = {}
    for pattern, target in re.findall(
        r'build\.classify\(\s*"([^"]+)"\s*,\s*(None|"[^"]+")\s*\)', options
    ):
        rules.setdefault(pattern, None if target == "None" else target.strip('"'))
    return rules


# ---------------------------------------------------------------------------
# Nothing internal ships
# ---------------------------------------------------------------------------

#: Everything at the top of the repository, and what a build must do with it.
#:
#: Written out by name rather than derived, because the point is to fail when
#: something *new* appears. A rule that computed the answer would silently
#: approve next year's directory, which is exactly the case this exists for.
EXPECTED: dict[str, bool] = {
    "game": True,
    "PLAYTEST_README.md": True,
    "FEEDBACK_INSTRUCTIONS.md": True,
    "THIRD_PARTY_NOTICES.md": True,
    "LICENSE": True,
    "docs": False,
    "tools": False,
    "tests": False,
    "scripts": False,
    "data": False,
    "assets": False,
    "research": False,
    "playtests": False,
    "README.md": False,
    "AGENTS.md": False,
    "CLAUDE.md": False,
    "CREDITS.md": False,
    "pyproject.toml": False,
    "uv.lock": False,
    "errors.txt": False,
    "log.txt": False,
    "traceback.txt": False,
}


def test_every_top_level_entry_is_accounted_for():
    """A new directory in the repository must be a decision, not a default.

    Ren'Py's catch-all would ship it. This is the test that turns "somebody
    should remember to exclude that" into a red build.
    """
    present = {
        entry.name
        for entry in paths.repo_root().iterdir()
        if not entry.name.startswith(".") and entry.name not in {"dist", "__pycache__"}
    }
    unaccounted = present - set(EXPECTED)
    assert not unaccounted, (
        f"{sorted(unaccounted)} is at the top of the repository and no rule in "
        "game/options.rpy says whether a tester should receive it. Add a "
        "build.classify() line and a row to EXPECTED."
    )


def test_the_internal_directories_are_excluded(options):
    """The seven that would be worst to leak, named individually."""
    rules = _classified(options)
    for directory in ("docs/", "tools/", "tests/", "scripts/", "data/", "assets/", "research/"):
        assert directory in rules, f"{directory} has no build.classify rule"
        assert rules[directory] is None, f"{directory} is classified as {rules[directory]!r}"


def test_the_exclusions_use_the_directory_form(options):
    """`docs/` and not `docs/**`.

    Ren'Py's scanner skips a directory it has excluded and does not descend
    into it. The `**` form leaves the directory itself unmatched, so it falls
    through to the catch-all and the build ships an empty folder named after
    the thing that was supposed to be secret.
    """
    for directory in ("docs", "tools", "tests", "scripts", "data", "assets", "research"):
        assert f'build.classify("{directory}/**", None)' not in options, directory


def test_the_tester_documents_are_classified_before_the_sweep(options):
    """First match wins, so order is the whole mechanism here.

    `PLAYTEST_README.md` has to be classified above `*.md`, or the sweep that
    excludes the internal Markdown excludes the two documents the tester needs.
    """
    sweep = options.index('build.classify("*.md", None)')
    for name in ("PLAYTEST_README.md", "FEEDBACK_INSTRUCTIONS.md", "THIRD_PARTY_NOTICES.md"):
        position = options.index(f'build.classify("{name}", "all")')
        assert position < sweep, f"{name} is classified after the *.md sweep and would be dropped"


def test_the_tester_documents_exist():
    """A classify rule for a file that is not there ships nothing at all."""
    for name in ("PLAYTEST_README.md", "FEEDBACK_INSTRUCTIONS.md", "THIRD_PARTY_NOTICES.md"):
        path = paths.repo_root() / name
        assert path.exists(), name
        assert len(path.read_text(encoding="utf-8")) > 500, f"{name} is a stub"


def test_no_compiled_python_ships(options):
    """A `.pyc` embeds the absolute path of the file it was compiled from.

    On a developer's machine that is a home directory with a name in it, which
    is exactly the sort of thing the report's privacy check refuses to write
    and which was quietly going into the archive beside it.
    """
    rules = _classified(options)
    assert rules.get("**/__pycache__/**") is None
    assert rules.get("**.pyc") is None


def test_the_archive_names_the_build(options):
    """A tester should know which build they have from the file name alone."""
    assert 'build.directory_name = "September32-Act1-Playtest-"' in options


def test_the_testcases_do_not_ship(options):
    """`game/testcases/` holds the harness that answers menus for the golden path.

    It is only safe for that harness to exist because it cannot reach a build.
    """
    rules = _classified(options)
    assert rules.get("game/testcases/**") is None


def test_the_harness_lives_only_in_the_testcases_directory():
    """The overrides that answer menus automatically must not leak upward.

    If `s32_test_autochoice` were defined anywhere under `game/` other than
    `testcases/`, it would ship, and a build that can answer its own menus is
    a build whose playtest data means nothing.
    """
    offenders = [
        path.name
        for path in sorted(paths.game_dir().rglob("*.rpy"))
        if "testcases" not in path.parts and "s32_test_autochoice" in path.read_text("utf-8")
    ]
    assert not offenders, offenders


# ---------------------------------------------------------------------------
# The content has to come with it
# ---------------------------------------------------------------------------


def test_the_build_mirrors_every_kind_of_content_the_library_loads():
    """A distribution has no `data/` beside `game/`, so the build copies it in.

    The failure this prevents is silent: a built game with no content loads
    zero storylets, the director selects nothing, and the week is empty. It
    does not crash, so it would reach a tester.
    """
    kinds = {p.name for p in paths.data_dir().iterdir() if p.is_dir() and p.name != "schemas"}
    missing = kinds - set(build_module.MIRRORED)
    assert not missing, (
        f"{sorted(missing)} exists under data/ and s32tools.build.MIRRORED does not list it, "
        "so a built game would not have it"
    )


def test_the_mirror_carries_the_whole_library(tmp_path, monkeypatch):
    """Copy the content the way the build does, and load a library from it."""
    staged = tmp_path / "data"
    for name in build_module.MIRRORED:
        folder = paths.data_dir() / name
        if not folder.is_dir():
            continue
        (staged / name).mkdir(parents=True)
        for item in folder.glob("*.json"):
            (staged / name / item.name).write_bytes(item.read_bytes())

    mirrored = load_library(staged)
    real = load_library(paths.data_dir())
    assert len(mirrored.storylets) == len(real.storylets)
    assert len(mirrored.anchors) == len(real.anchors)
    assert len(mirrored.characters) == len(real.characters)
    assert len(mirrored.locations) == len(real.locations)


def test_an_empty_library_is_loud():
    """The silent failure, made loud.

    A built game with no content loads zero storylets, selects nothing, and
    raises nothing. The first person to notice would be a tester, halfway
    through a week that never starts.
    """
    bridge = (paths.game_dir() / "engine" / "00_s32_engine.rpy").read_text(encoding="utf-8")
    assert "if not s32_library.storylets:" in bridge
    assert "no content was loaded" in bridge


def test_the_built_game_can_read_content_out_of_an_archive():
    """`Path.is_dir` is False for a directory inside a Ren'Py archive.

    That is how the first playtest build reached a fresh install and failed on
    its own content, with a stack trace, before the main menu. The seam that
    fixes it keeps the engine dependency-free, which is the property that lets
    the same loader run in the headless simulator.
    """
    from s32_engine.definitions import load_library_from
    from s32_engine.documents import load_documents_from

    files = {
        f"{path.parent.name}/{path.name}": path.read_text(encoding="utf-8")
        for path in sorted(paths.data_dir().rglob("*.json"))
    }
    assert len(load_library_from(files).storylets) == len(load_library(paths.data_dir()).storylets)
    assert load_documents_from(files).documents

    bridge = (paths.game_dir() / "engine" / "00_s32_engine.rpy").read_text(encoding="utf-8")
    assert "renpy.list_files()" in bridge


def test_no_shipped_script_imports_a_launcher_only_module():
    """`gui7` lives in the SDK and is not part of a distribution.

    An unguarded import crashed the second playtest build before the main
    menu. The guard is why a build gets unpacked somewhere else and run there.
    """
    for path in sorted(paths.game_dir().rglob("*.rpy")):
        if "testcases" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "gui7" not in text:
            continue
        assert 'os.path.isdir(os.path.join(_launcher, "gui7"))' in text, path.name


def test_the_engine_looks_in_the_game_directory_first():
    """The order of the two candidate directories, which decides two things.

    It is what makes the mirror work in a build, and it is why a stale mirror
    is dangerous in development. Both facts come from the same three lines.
    """
    bridge = (paths.game_dir() / "engine" / "00_s32_engine.rpy").read_text(encoding="utf-8")
    gamedir = bridge.index('os.path.join(config.gamedir, "data")')
    basedir = bridge.index('os.path.join(config.basedir, "data")')
    assert gamedir < basedir


def test_the_mirror_and_the_stamp_are_not_committed():
    """Both are generated, so neither belongs in version control.

    A committed mirror would be loaded in preference to the real content and
    would be invisible to every tool in the project, all of which read `data/`.
    """
    ignore = (paths.repo_root() / ".gitignore").read_text(encoding="utf-8")
    assert "game/data/" in ignore
    assert "game/build_stamp.json" in ignore


# ---------------------------------------------------------------------------
# The build can name itself
# ---------------------------------------------------------------------------


def test_the_stamp_round_trips(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "game_dir", lambda: tmp_path)
    path = build_module.write_stamp("0.2.0-playtest.1", "a" * 40)
    stamp = json.loads(path.read_text(encoding="utf-8"))
    assert stamp["game_version"] == "0.2.0-playtest.1"
    assert stamp["build_id"] == "aaaaaaaa"
    assert stamp["commit"] == "a" * 40


def test_the_build_id_is_derived_from_the_commit_and_not_the_clock():
    """Two builds of the same source must look the same.

    A date-derived id would make them look different, which is precisely the
    comparison a playtest wave needs to be able to make -- and it would be the
    third time a wall clock got into a generated artefact in this project.
    """
    assert build_module.build_id("a" * 40) == build_module.build_id("a" * 40)
    assert build_module.build_id("unknown") == "local"
    source = (paths.repo_root() / "tools" / "s32tools" / "build.py").read_text("utf-8")
    assert "datetime" not in source
    assert "time.time" not in source


def test_the_game_reads_the_stamp_back():
    """The stamp is only worth writing if something reads it."""
    bridge = (paths.game_dir() / "engine" / "03_s32_build.rpy").read_text(encoding="utf-8")
    assert 'renpy.loadable("build_stamp.json")' in bridge
    assert "def s32_build_line" in bridge

    screens = (paths.game_dir() / "screens.rpy").read_text(encoding="utf-8")
    assert "s32_build_line()" in screens


def test_the_version_is_a_playtest_version():
    """The build a tester receives must say what it is.

    Both halves matter: `playtest` so nobody mistakes it for a release, and a
    version that sorts *after* the prototype it succeeds.
    """
    assert "playtest" in GAME_VERSION
    assert GAME_VERSION > "0.1.0-prototype"


def test_the_build_says_it_is_a_private_playtest(options):
    """§5: visible, discreet, and not a debug build."""
    assert "private playtest" in options.lower()
    screens = (paths.game_dir() / "screens.rpy").read_text(encoding="utf-8")
    assert "private playtest" in screens.lower()


# ---------------------------------------------------------------------------
# Nothing internal is on screen
# ---------------------------------------------------------------------------


def test_the_inspectors_are_behind_the_developer_flag():
    """Absent from a build rather than hidden in it.

    A tester who found the storylet inspector would be able to read every scene
    they had not reached, every eligibility clause, and every relationship
    number -- which would end the playtest and spoil the act in one keypress.
    """
    debug = (paths.game_dir() / "screens" / "debug.rpy").read_text(encoding="utf-8")
    bindings = debug.index("config.keymap.setdefault")
    guard = debug.rindex("if config.developer:", 0, bindings)
    assert guard < bindings
    assert "s32_force_storylet" in debug


def test_no_player_facing_screen_shows_a_storylet_id_or_a_number():
    """The screens a tester can actually open.

    `debug.rpy` is excluded because it is developer-only and is the one place
    these are supposed to appear.
    """
    # Call shapes rather than bare words. `stance` is also the name of a
    # knowledge stance -- "known", "suspected" -- and `s32_journal_facts` takes
    # one as a parameter, which a `\bstance\b` pattern flagged and should not
    # have. The relationship helper always takes a character id as a literal.
    reading = re.compile(
        r'rel_get\(|regards\(|stance\("|s32_debug_|S32State\["relationships"\]|\.priority'
    )
    offenders: list[str] = []
    for path in sorted((paths.game_dir() / "screens").glob("*.rpy")):
        if path.name == "debug.rpy":
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip().startswith("#"):
                continue
            if reading.search(line):
                offenders.append(f"{path.name}:{number}")
    assert not offenders, offenders


#: Words that mean "unfinished" to a developer and "broken" to a tester.
#:
#: `PLACEHOLDER` is deliberately absent: labelled placeholder art is the
#: policy, not a leak, and `MISSING ASSET` is meant to be visible.
_INTERNAL_MARKERS = ("TODO", "FIXME", "XXX", "HACK", "WIP")


def test_no_internal_marker_reaches_a_line_a_player_can_read():
    """§87. Comments may say TODO. Dialogue and buttons may not."""
    offenders: list[str] = []
    said = re.compile(r'^\s*(?:narrator|centered|c_\w+|text|textbutton|label)\b.*"([^"]*)"')
    for path in sorted(paths.game_dir().rglob("*.rpy")):
        if "testcases" in path.parts:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip().startswith("#"):
                continue
            match = said.match(line)
            if match and any(marker in match.group(1) for marker in _INTERNAL_MARKERS):
                offenders.append(f"{path.name}:{number}: {match.group(1)[:60]}")
    assert not offenders, offenders


def test_the_readme_warns_that_some_art_is_temporary():
    """§7. Said once, to the tester, outside the fiction.

    Repeating it inside a scene would make the game apologise for itself, which
    changes how the scene reads and therefore what the playtest measures.
    """
    readme = (paths.repo_root() / "PLAYTEST_README.md").read_text(encoding="utf-8")
    assert "temporary" in readme.lower()

    # The About screen is allowed to say it -- that is a tester-facing surface
    # outside the fiction. What must not carry it is a line anybody reads while
    # playing, so comments are excluded: the story files discuss the art gap at
    # length and should, in the places a writer looks.
    offenders: list[str] = []
    for path in sorted((paths.game_dir() / "story").rglob("*.rpy")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip().startswith("#"):
                continue
            if "placeholder" in line.lower() or "final art" in line.lower():
                offenders.append(f"{path.name}:{number}: {line.strip()[:60]}")
    assert not offenders, offenders


# ---------------------------------------------------------------------------
# One language
# ---------------------------------------------------------------------------


def test_the_shipped_build_is_in_one_language():
    """§84. English is the source language and the only one in this build.

    Not a translation check -- a check that the *development* language has not
    leaked into a line a tester reads. The briefs for this project are written
    in Portuguese and this is the surface where that would show up.
    """
    portuguese = re.compile(
        r"\b(não|você|então|também|porque|jogador|cena|personagem|arquivo)\b",
        re.IGNORECASE,
    )
    offenders: list[str] = []
    for path in sorted(paths.game_dir().rglob("*.rpy")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if portuguese.search(line):
                offenders.append(f"{path.name}:{number}: {line.strip()[:60]}")
    assert not offenders, offenders
