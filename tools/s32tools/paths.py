"""Canonical filesystem locations, resolved once.

Every tool takes its paths from here rather than reconstructing them, so that
moving a directory is a one-line change and so that a tool run from a
subdirectory behaves the same as one run from the repository root.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

#: Marker files that identify the repository root unambiguously.
_ROOT_MARKERS = ("pyproject.toml", "game", "data")


@lru_cache(maxsize=1)
def repo_root() -> Path:
    """Return the repository root.

    Resolution order:

    1. ``S32_ROOT``, for CI and for tools invoked from odd working directories.
    2. Walking up from this file, which is correct for an editable install.
    3. Walking up from the current working directory, which covers a wheel
       installed elsewhere but run inside the checkout.

    Raises:
        RuntimeError: If no candidate looks like the repository.
    """
    override = os.environ.get("S32_ROOT")
    if override:
        candidate = Path(override).expanduser().resolve()
        if _looks_like_root(candidate):
            return candidate
        raise RuntimeError(f"S32_ROOT={candidate} does not look like the repository root")

    for start in (Path(__file__).resolve(), Path.cwd().resolve() / "_"):
        for parent in start.parents:
            if _looks_like_root(parent):
                return parent

    raise RuntimeError("could not locate the September 32 repository root")


def _looks_like_root(path: Path) -> bool:
    """Return whether a directory contains all the root markers."""
    return all((path / marker).exists() for marker in _ROOT_MARKERS)


def data_dir() -> Path:
    """Authored content (JSON): characters, storylets, knowledge, and so on."""
    return repo_root() / "data"


def schemas_dir() -> Path:
    """Generated JSON Schemas for the content in :func:`data_dir`."""
    return data_dir() / "schemas"


def game_dir() -> Path:
    """The Ren'Py project's ``game/`` directory."""
    return repo_root() / "game"


def assets_dir() -> Path:
    """Root of the asset pipeline."""
    return repo_root() / "assets"


def catalog_path() -> Path:
    """The asset manifest: the single source of truth for licensing."""
    return assets_dir() / "catalog" / "assets.toml"


def vendor_dir() -> Path:
    """Untouched third-party originals. Never committed."""
    return assets_dir() / "vendor"


def processed_dir() -> Path:
    """Game-ready derivatives produced from vendor originals. Never committed."""
    return assets_dir() / "processed"


def evidence_dir() -> Path:
    """Per-asset licence evidence captured at acquisition time. Committed."""
    return assets_dir() / "evidence"


def downloads_dir() -> Path:
    """Local download cache for fetched archives. Never committed."""
    return assets_dir() / ".downloads"


def reports_dir() -> Path:
    """Generated reports: simulation, coverage, contact sheets, graphs."""
    return repo_root() / "tools" / "reports"


def docs_dir() -> Path:
    """Project documentation."""
    return repo_root() / "docs"


def renpy_sdk_dir() -> Path:
    """Where ``s32`` installs the Ren'Py SDK. Never committed."""
    return repo_root() / ".tools" / "renpy"
