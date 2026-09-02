"""Producing a build somebody outside the project can actually run.

Three things have to happen that Ren'Py's own ``distribute`` does not do on its
own, and each of them is a way the build could ship broken and silent.

**The content has to come with it.** ``data/`` sits beside ``game/`` in the
repository and the engine finds it there. A distribution has no repository, so
the build mirrors it into ``game/data/``. Without that the built game loads zero
storylets and the director selects nothing -- which is not a crash, and would
therefore reach a tester.

**The build has to be able to name itself.** A bug report that says "the one you
sent me" is worth very little. ``game/build_stamp.json`` carries the version,
a build id and the commit, and ``game/engine/03_s32_build.rpy`` reads it back at
init. It is generated rather than committed, because a file that names the
commit containing it is not a thing that can be true.

**The repository must not ship.** The base directory Ren'Py scans is a working
repository with the canon, the briefs and the internal reports in it. The
exclusions live in ``game/options.rpy`` where Ren'Py can see them, and
``tests/test_playtest_build.py`` fails if a top-level entry appears that no rule
accounts for.

Everything here is local. Nothing is uploaded, published or announced.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from s32tools import paths

#: Where Ren'Py leaves distributions.
DIST_DIRNAME = "dist"

#: Files copied into the game tree so a distribution carries its own content.
MIRRORED = ("storylets", "anchors", "characters", "locations", "knowledge", "documents", "items")


@dataclass(frozen=True, slots=True)
class Artifact:
    """One produced archive or directory."""

    path: Path
    size: int
    sha256: str

    @property
    def megabytes(self) -> float:
        """Return the size in MB, for a report a person reads."""
        return self.size / (1024 * 1024)


def commit_hash() -> str:
    """Return the current commit, or ``unknown`` outside a git checkout.

    Never raises. A build from an exported tarball is a legitimate thing to
    want, and refusing to make one because git is absent would be a tool
    deciding policy.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=paths.repo_root(),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return "unknown"
    head = result.stdout.strip()
    return head if result.returncode == 0 and head else "unknown"


def working_tree_is_clean() -> bool:
    """Return whether the checkout has uncommitted changes.

    A build from a dirty tree cannot be reproduced from its own commit hash,
    which makes the stamp a decoration. ``s32 build`` warns rather than
    refusing: refusing would make it impossible to test the build pipeline
    while working on it.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=paths.repo_root(),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0 and not result.stdout.strip()


def build_id(commit: str) -> str:
    """Return a short, stable identifier for this build.

    Derived from the commit rather than from a counter or a date. A counter
    needs somewhere to live and a date makes two builds of the same source
    look different, which is precisely the comparison a playtest wave needs to
    be able to make.
    """
    return commit[:8] if commit != "unknown" else "local"


def mirror_content() -> int:
    """Copy authored content into the game tree. Returns the number of files.

    Copied fresh every time rather than synced, because a stale storylet in
    ``game/data/`` would be loaded in preference to the real one -- the engine
    checks the game directory first -- and would be invisible to every tool in
    the project, all of which read ``data/``.
    """
    source = paths.data_dir()
    destination = paths.game_dir() / "data"
    if destination.exists():
        shutil.rmtree(destination)

    count = 0
    for name in MIRRORED:
        folder = source / name
        if not folder.is_dir():
            continue
        target = destination / name
        target.mkdir(parents=True, exist_ok=True)
        for item in sorted(folder.glob("*.json")):
            shutil.copy2(item, target / item.name)
            count += 1
    return count


def write_stamp(version: str, commit: str) -> Path:
    """Write the build stamp the game reads back at init."""
    stamp = {
        "game_version": version,
        "build_id": build_id(commit),
        "commit": commit,
    }
    path = paths.game_dir() / "build_stamp.json"
    path.write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def sha256_of(path: Path) -> str:
    """Return a file's SHA-256, read in chunks so a 500 MB archive is fine."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def describe(path: Path) -> Artifact:
    """Return size and hash for a produced file."""
    return Artifact(path=path, size=path.stat().st_size, sha256=sha256_of(path))


def artifacts(dist: Path, version: str) -> list[Artifact]:
    """Return every archive produced for this version, newest listing first."""
    if not dist.is_dir():
        return []
    found = [p for p in sorted(dist.iterdir()) if p.is_file() and version in p.name]
    return [describe(p) for p in found]
