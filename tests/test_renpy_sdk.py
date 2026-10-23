"""Ren'Py SDK extraction preserves executable permissions on POSIX."""

from __future__ import annotations

import os
import stat
import zipfile
from pathlib import Path

import pytest

from s32tools.renpy_sdk import _restore_executable_bits, headless_env


def test_headless_env_keeps_the_display_driver_under_xvfb(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("s32tools.renpy_sdk.platform.system", lambda: "Linux")
    monkeypatch.delenv("DISPLAY", raising=False)

    assert headless_env() == {"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}

    monkeypatch.setenv("DISPLAY", ":99")
    assert headless_env() == {}


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable bits are the regression")
def test_sdk_extraction_restores_only_archive_marked_executables(tmp_path: Path) -> None:
    archive_path = tmp_path / "sdk.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        executable = zipfile.ZipInfo("lib/py3-linux-x86_64/renpy")
        executable.create_system = 3
        executable.external_attr = (stat.S_IFREG | 0o755) << 16
        archive.writestr(executable, b"launcher")

        ordinary = zipfile.ZipInfo("lib/py3-linux-x86_64/data.txt")
        ordinary.create_system = 3
        ordinary.external_attr = (stat.S_IFREG | 0o644) << 16
        archive.writestr(ordinary, b"data")

    destination = tmp_path / "sdk"
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)
        executable_path = destination / "lib/py3-linux-x86_64/renpy"
        ordinary_path = destination / "lib/py3-linux-x86_64/data.txt"
        assert not os.access(executable_path, os.X_OK)
        assert not os.access(ordinary_path, os.X_OK)

        _restore_executable_bits(archive, destination)

    assert os.access(executable_path, os.X_OK)
    assert not os.access(ordinary_path, os.X_OK)
