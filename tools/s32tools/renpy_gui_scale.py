"""Rescaling Ren'Py's GUI template from 720p to the project's 1080p target.

Ren'Py ships its default GUI drawn for 1280x720 and the launcher regenerates it
when you pick a different resolution. This project is bootstrapped from the
command line, so the same job is done here: multiply every pixel constant in
``gui.rpy`` and every bitmap in ``game/gui/`` by 1.5.

The two halves of the job are not symmetrical, and the difference matters:

*The constants must be scaled here.* The template wraps them in ``gui.scale()``,
but that function is the identity (see ``game/guisupport.rpy``) -- it is a hook
for the launcher, not a runtime scaler. A 22px dialogue font stays 22px on a
1080p screen unless something changes the literal.

*The bitmaps are scaled here as a safety net.* When the project runs from the
SDK, ``guisupport.rpy`` regenerates the GUI images through Ren'Py's own ``gui7``
generator at ``config.screen_width``, overwriting these. That does not happen in
a built game, so the committed images have to already be the right size.

This is a **one-time bootstrap step**, run once with its result committed. It
lives here rather than in a scratch script because it documents exactly how the
1080p GUI was derived, and because the operation must stay repeatable if the
template is ever refreshed from a newer SDK.

The project's own interface (see ``docs/style/VISUAL_DESIGN_SYSTEM.md``)
replaces this as it lands. This is scaffolding that lets the game run and be
tested today, not the intended look.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

#: Template design size and the project's target.
SOURCE_SIZE = (1280, 720)
TARGET_SIZE = (1920, 1080)
SCALE = TARGET_SIZE[0] / SOURCE_SIZE[0]

#: ``gui.<name>`` constants that are pixel measurements and must scale.
#: Everything not listed is a ratio, a colour, a boolean or a string, and
#: scaling it would corrupt the GUI. An allowlist is the only safe direction:
#: a missed constant looks slightly wrong, a wrongly-scaled ratio breaks layout.
_SCALABLE_SUFFIXES = (
    "_size",
    "_width",
    "_height",
    "_xpos",
    "_ypos",
    "_xsize",
    "_ysize",
    "_spacing",
    "_padding",
    "_borders",
    "_thickness",
    "_xalign_offset",
    "_offset",
    "_leading",
    "_margin",
    "_indent",
)

#: Constants matching a scalable suffix that are nevertheless NOT pixels.
_EXCLUDE = frozenset(
    {
        "gui.slot_spacing",  # scaled, but listed here for the reader: see below
    }
) - {"gui.slot_spacing"}

_DEFINE_RE = re.compile(
    r"^(?P<head>\s*define\s+(?P<name>gui\.[A-Za-z_][A-Za-z0-9_]*)\s*=\s*)(?P<value>.+?)"
    r"(?P<tail>\s*(?:#.*)?)$"
)
_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


@dataclass(slots=True)
class ScaleReport:
    """What a rescale pass changed."""

    constants_scaled: list[str] = field(default_factory=list)
    constants_skipped: list[str] = field(default_factory=list)
    images_scaled: list[str] = field(default_factory=list)
    init_updated: bool = False


def _is_scalable(name: str) -> bool:
    """Return whether a ``gui.*`` constant is a pixel measurement."""
    if name in _EXCLUDE:
        return False
    return name.endswith(_SCALABLE_SUFFIXES)


def _scale_number(match: re.Match[str]) -> str:
    """Scale one numeric literal, keeping integers integral."""
    raw = match.group(0)
    scaled = float(raw) * SCALE
    if "." not in raw:
        return str(round(scaled))
    return f"{scaled:g}"


def scale_gui_rpy(path: Path) -> ScaleReport:
    """Rewrite ``gui.rpy`` for the target resolution."""
    report = ScaleReport()
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []

    for line in lines:
        stripped = line.rstrip("\r\n")
        ending = line[len(stripped) :]

        if f"gui.init({SOURCE_SIZE[0]}, {SOURCE_SIZE[1]})" in stripped:
            out.append(
                stripped.replace(
                    f"gui.init({SOURCE_SIZE[0]}, {SOURCE_SIZE[1]})",
                    f"gui.init({TARGET_SIZE[0]}, {TARGET_SIZE[1]})",
                )
                + ending
            )
            report.init_updated = True
            continue

        match = _DEFINE_RE.match(stripped)
        if match is None:
            out.append(line)
            continue

        name = match.group("name")
        value = match.group("value")
        if not _is_scalable(name) or not _NUMBER_RE.search(value):
            if _NUMBER_RE.fullmatch(value.strip()):
                report.constants_skipped.append(name)
            out.append(line)
            continue

        new_value = _NUMBER_RE.sub(_scale_number, value)
        out.append(f"{match.group('head')}{new_value}{match.group('tail')}{ending}")
        report.constants_scaled.append(name)

    path.write_text("".join(out), encoding="utf-8")
    return report


def scale_gui_images(directory: Path, report: ScaleReport) -> ScaleReport:
    """Rescale every GUI bitmap in place with Lanczos resampling."""
    for path in sorted(directory.rglob("*.png")):
        with Image.open(path) as image:
            converted = image.convert("RGBA")
            new_size = (
                max(1, round(converted.width * SCALE)),
                max(1, round(converted.height * SCALE)),
            )
            resized = converted.resize(new_size, Image.Resampling.LANCZOS)
        resized.save(path, "PNG")
        report.images_scaled.append(path.name)
    return report


def rescale_project(game_dir: Path) -> ScaleReport:
    """Rescale a Ren'Py project's GUI from the template size to the target."""
    report = scale_gui_rpy(game_dir / "gui.rpy")
    return scale_gui_images(game_dir / "gui", report)
