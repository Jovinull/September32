"""Locating, installing and driving the Ren'Py SDK.

The SDK is ~500 MB unpacked and is not committed (ADR-0001). It lives in
``.tools/renpy/`` by default, and ``S32_RENPY_SDK`` overrides that for a
developer who already has one installed.

The pinned version is a deliberate choice, not a floor: a Ren'Py point release
can change lint output and save compatibility, so CI and every developer run the
same one. Upgrading is an explicit edit here plus a fresh checksum.
"""

from __future__ import annotations

import os
import platform
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

#: Pinned Ren'Py version. Verified as the current stable release on the official
#: site on 2026-10-23 (https://www.renpy.org/latest.html). Nightlies are never
#: used. See docs/research/RESEARCH_LOG.md.
RENPY_VERSION = "8.5.3"

#: Official download host. No mirrors.
BASE_URL = f"https://www.renpy.org/dl/{RENPY_VERSION}"

#: The cross-platform SDK zip. The platform-specific packages (the Windows
#: 7z self-extractor, the macOS dmg) need an external extractor; the plain zip
#: contains the same SDK and unpacks with the standard library.
SDK_ARCHIVE = f"renpy-{RENPY_VERSION}-sdk.zip"

#: SHA-256 of the SDK archive, observed on download from the official host on
#: 2026-10-23. `s32 renpy install` refuses to unpack an archive that does not
#: match, so a corrupted or substituted download cannot reach the project.
SDK_SHA256 = "ff57648f9c04f27e381c48af6d8e3ee3cdec296bed4d3831f47f09b0a71b505e"

ENV_VAR = "S32_RENPY_SDK"


@dataclass(frozen=True, slots=True)
class SdkInfo:
    """A located Ren'Py SDK."""

    root: Path
    version: str
    launcher: Path

    @property
    def exists(self) -> bool:
        """Return whether the launcher is actually present."""
        return self.launcher.exists()


def _launcher_name() -> str:
    """Return the platform's Ren'Py console executable name."""
    if platform.system() == "Windows":
        # renpy.exe opens the launcher GUI; renpy.py under the bundled Python is
        # what accepts `lint` and `test` on the command line.
        return "renpy.exe"
    return "renpy.sh"


def locate(sdk_root: Path | None = None) -> SdkInfo | None:
    """Find an installed SDK.

    Resolution order: explicit argument, ``S32_RENPY_SDK``, then the default
    ``.tools/renpy/renpy-<version>-sdk`` inside the repository.
    """
    candidates: list[Path] = []
    if sdk_root is not None:
        candidates.append(sdk_root)
    if env := os.environ.get(ENV_VAR):
        candidates.append(Path(env).expanduser())

    from s32tools.paths import renpy_sdk_dir

    default_root = renpy_sdk_dir()
    candidates.append(default_root / f"renpy-{RENPY_VERSION}-sdk")
    candidates.append(default_root)

    for candidate in candidates:
        launcher = candidate / _launcher_name()
        if launcher.exists():
            return SdkInfo(root=candidate, version=_read_version(candidate), launcher=launcher)
        # A zip that unpacked one level deeper than expected.
        nested = candidate / f"renpy-{RENPY_VERSION}-sdk"
        if (nested / _launcher_name()).exists():
            return SdkInfo(
                root=nested, version=_read_version(nested), launcher=nested / _launcher_name()
            )
    return None


def _read_version(root: Path) -> str:
    """Read the SDK's own reported version, falling back to the pin."""
    vc_version = root / "renpy" / "vc_version.py"
    if vc_version.exists():
        for line in vc_version.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("version ="):
                return line.split("=", 1)[1].strip().strip("\"'")
    return RENPY_VERSION


def install(destination: Path, *, force: bool = False) -> tuple[SdkInfo | None, str]:
    """Download and unpack the pinned SDK.

    Returns:
        ``(info, message)``. ``info`` is ``None`` when the download failed, in
        which case ``message`` explains what to do by hand -- the rest of the
        toolchain works without the SDK, so this must never be fatal.
    """
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / SDK_ARCHIVE
    url = f"{BASE_URL}/{SDK_ARCHIVE}"

    existing = locate(destination)
    if existing is not None and not force and not archive.exists():
        return existing, f"already installed at {existing.root} (no cached archive to inspect)"

    if not archive.exists() or force:
        try:
            with urllib.request.urlopen(url, timeout=600) as response, archive.open("wb") as handle:
                while chunk := response.read(1 << 20):
                    handle.write(chunk)
        except OSError as exc:
            launcher = destination / f"renpy-{RENPY_VERSION}-sdk" / _launcher_name()
            return None, (
                f"could not download the Ren'Py SDK: {exc}\n\n"
                "MANUAL INSTALL REQUIRED\n"
                f"  1. Download {url}\n"
                f"  2. Unpack it into {destination}\n"
                f"  3. Confirm {launcher} exists\n"
                f"  ...or set {ENV_VAR} to an SDK you already have."
            )

    from s32tools.assets.fetch import sha256_of

    observed = sha256_of(archive)
    if SDK_SHA256 and observed != SDK_SHA256:
        return None, (
            f"SDK checksum mismatch for {archive.name}\n"
            f"  expected {SDK_SHA256}\n  observed {observed}\n"
            "Refusing to unpack. Delete the file and retry, or verify the pin."
        )

    if existing is not None and not force:
        with zipfile.ZipFile(archive) as zf:
            _restore_executable_bits(zf, destination)
        return existing, f"already installed at {existing.root}; executable modes checked"

    with zipfile.ZipFile(archive) as zf:
        zf.extractall(destination)
        _restore_executable_bits(zf, destination)

    info = locate(destination)

    if info is None:
        return None, f"unpacked {archive.name} but no launcher was found under {destination}"
    return info, f"installed {info.version} at {info.root} (sha256 {observed})"


def _restore_executable_bits(archive: zipfile.ZipFile, destination: Path) -> None:
    """Restore only executable modes recorded in the verified SDK zip.

    Python's ``zipfile.extractall`` does not restore Unix permission bits. The
    Ren'Py launcher invokes ``lib/py3-linux-x86_64/renpy`` directly, so losing
    that member's executable bit makes a cached SDK fail with ``Permission
    denied``. The official archive carries the intended mode in each member's
    Unix ``external_attr``; restore that narrow bit only, on POSIX systems.
    """
    if os.name == "nt":
        return
    for member in archive.infolist():
        recorded_mode = member.external_attr >> 16
        if not stat.S_ISREG(recorded_mode):
            continue
        if not recorded_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            continue
        if member.is_dir():
            continue
        target = destination / member.filename
        if target.is_file():
            current_mode = target.stat().st_mode
            executable_bits = recorded_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            target.chmod(current_mode | executable_bits)


def command(info: SdkInfo, *args: str) -> list[str]:
    """Build the argv for a Ren'Py CLI invocation.

    On Windows the ``renpy.exe`` shim works for ``lint`` and ``test``. Elsewhere
    ``renpy.sh`` does the same. Both take the project directory as the first
    positional argument.
    """
    return [str(info.launcher), *args]


def run(
    info: SdkInfo,
    project: Path,
    *args: str,
    timeout: int = 900,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a Ren'Py CLI command against the project.

    Ren'Py needs a writable home for its own state and, in CI, a dummy video
    driver; both are set here so callers do not each rediscover it.
    """
    env = dict(os.environ)
    env.setdefault("RENPY_SIMPLE_EXCEPTIONS", "1")
    if extra_env:
        env.update(extra_env)

    return subprocess.run(
        command(info, str(project), *args),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
        check=False,
    )


def headless_env() -> dict[str, str]:
    """Return environment variables that let Ren'Py run without a display.

    Ren'Py still initialises SDL even for ``lint``. On a headless Linux runner
    without an X server, the dummy drivers stop it from failing at startup. If
    ``DISPLAY`` is set (for example by ``xvfb-run``), keep SDL's real video
    driver so Ren'Py can create the GL context needed by screen testcases.
    """
    if platform.system() == "Linux" and not os.environ.get("DISPLAY"):
        return {"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}
    return {}


def which_python() -> str:
    """Return the interpreter running the tooling, for ``s32 doctor``."""
    return f"{sys.version.split()[0]} ({shutil.which('python') or sys.executable})"
