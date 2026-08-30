"""Generating Ren'Py image and sprite definitions from installed assets.

Handwriting several hundred ``image`` statements would be tedious and, worse,
would bake the casting decision into the scripts: renaming which sprite plays
Iris would become a find-and-replace across the whole project.

Instead this generates one file from two inputs:

* ``data/characters/*.json`` — who exists in the story and which asset plays
  them (``asset_id``),
* ``assets/processed/characters/`` — which sprites are actually installed.

The result declares images under the **canon** name (``iris school_summer
neutral``) pointing at **asset** files (``char_kohaku_school_summer_neutral``).
Recasting is then a one-line edit to a JSON file. See ADR-0005.

Presentation constants live in one place too. A ``zoom 0.63`` copy-pasted into
ninety scripts is how a project ends up unable to change its sprite scale; here
there is exactly one transform per character, derived from measured metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from s32_engine.types import ContentLibrary
from s32tools.assets.install import expression_matrix
from s32tools.assets.naming import CANONICAL_EXPRESSIONS

#: Default sprite placement, in the project's 1920x1080 space.
#:
#: The Potat0Master sprites are 720x1080 with the figure's feet at the bottom
#: edge, so a scale of 1.0 already fills the frame vertically. Per-character
#: overrides go in ``data/characters/<id>.json`` under ``sprite``; nothing else
#: should ever carry a hard-coded zoom.
DEFAULT_SPRITE = {
    "scale": 1.0,
    "xoffset": 0,
    "yoffset": 0,
    "baseline": 1080,
}

#: Expression requested by a scene -> what to show when the asset lacks it.
#: Falling back is better than crashing, and better than silently showing
#: nothing: the dev build reports the substitution and the art gap analysis
#: picks it up.
EXPRESSION_FALLBACKS: dict[str, tuple[str, ...]] = {
    "neutral_blush": ("blush", "neutral"),
    "sad_talk": ("sad", "talk", "neutral"),
    "angry_talk": ("angry", "talk", "neutral"),
    "pout_angry": ("pout", "angry", "neutral"),
    "crying": ("sad", "neutral"),
    "smirk": ("happy", "neutral"),
    "disgusted": ("angry", "neutral"),
    "surprised": ("neutral",),
    "concerned": ("sad", "neutral"),
    "gloom": ("sad", "concerned", "neutral"),
}

VENDOR_IMAGE_DIR = "images/vendor/characters"
VENDOR_BG_DIR = "images/vendor/backgrounds"


@dataclass(slots=True)
class GenerationResult:
    """What the generator produced, and what it could not."""

    text: str
    characters_defined: list[str]
    characters_without_art: list[str]
    missing_expressions: dict[str, list[str]]
    backgrounds_defined: int


def _resolve(available: list[str], wanted: str) -> str | None:
    """Return the best available expression for a requested one."""
    if wanted in available:
        return wanted
    for fallback in EXPRESSION_FALLBACKS.get(wanted, ()):
        if fallback in available:
            return fallback
    return "neutral" if "neutral" in available else None


def generate(
    library: ContentLibrary,
    processed_root: Path,
    game_root: Path,
) -> GenerationResult:
    """Build the Ren'Py definitions file."""
    matrix = expression_matrix(processed_root)

    lines: list[str] = [
        "# GENERATED FILE - do not edit.",
        "#",
        "# Source: data/characters/*.json  +  assets/processed/characters/",
        "# Regenerate: s32 assets images",
        "#",
        "# Images are declared under the CANON name and point at ASSET files.",
        "# Recasting a character is a one-line edit to their JSON, not a rename",
        "# across the project. See docs/decisions/ADR-0005-character-art-consistency.md.",
        "#",
        "# Paths go through s32_sprite / s32_bg rather than being named directly,",
        "# so a checkout with no assets installed still lints, tests and runs —",
        "# each missing file becomes a labelled placeholder. See the helpers in",
        "# game/engine/00_s32_engine.rpy.",
        "",
        f"# Generated {datetime.now(UTC).isoformat(timespec='seconds')}",
        "",
        "init offset = -1",
        "",
    ]

    defined: list[str] = []
    without_art: list[str] = []
    missing: dict[str, list[str]] = {}

    for char_id in sorted(library.characters):
        character = library.characters[char_id]
        asset_key = (character.asset_id or "").removeprefix("pm_a01_").removeprefix("pm_a02_")
        outfits = matrix.get(asset_key, {})

        if not character.asset_id or not outfits:
            without_art.append(char_id)
            continue

        defined.append(char_id)
        lines.append(f"# {character.display_name} — played by asset `{asset_key}`")

        for outfit, available in outfits.items():
            for wanted in CANONICAL_EXPRESSIONS:
                resolved = _resolve(available, wanted)
                if resolved is None:
                    continue
                if resolved != wanted:
                    missing.setdefault(char_id, []).append(f"{outfit}/{wanted}")
                filename = f"char_{asset_key}_{outfit}_{resolved}.webp"
                lines.append(
                    f"image {char_id} {outfit} {wanted} = "
                    f's32_sprite("{VENDOR_IMAGE_DIR}/{filename}", '
                    f'"{char_id} / {outfit} / {wanted}")'
                )
            # An outfit with no expression named is the common case in a
            # scene: `show iris school_summer` means the neutral pose.
            if "neutral" in available:
                lines.append(
                    f"image {char_id} {outfit} = "
                    f's32_sprite("{VENDOR_IMAGE_DIR}/'
                    f'char_{asset_key}_{outfit}_neutral.webp", '
                    f'"{char_id} / {outfit}")'
                )
        lines.append("")

    lines += _sprite_transforms(library, defined)
    lines += _background_definitions(library, game_root)

    backgrounds = sum(1 for line in lines if line.startswith("image bg "))
    return GenerationResult(
        text="\n".join(lines) + "\n",
        characters_defined=defined,
        characters_without_art=without_art,
        missing_expressions={k: sorted(set(v)) for k, v in sorted(missing.items())},
        backgrounds_defined=backgrounds,
    )


def _sprite_transforms(library: ContentLibrary, defined: list[str]) -> list[str]:
    """Emit one placement transform per character.

    Centralised so that changing how sprites sit on screen is one edit. A scene
    writes ``show iris school_summer happy at centre``; it never writes a zoom.
    """
    lines = [
        "",
        "# Sprite placement. One transform per character, so that adjusting how",
        "# a sprite sits on screen never means touching a scene script.",
        "",
    ]
    for char_id in defined:
        character = library.characters[char_id]
        sprite = DEFAULT_SPRITE
        scale = sprite["scale"]
        yoffset = sprite["yoffset"]
        lines += [
            f"transform {char_id}_base:",
            f"    zoom {scale}",
            f"    yoffset {yoffset}",
            "    subpixel True",
            "",
        ]
        _ = character  # per-character overrides land here when the data carries them

    lines += [
        "# Stage positions, in the 1920x1080 design space.",
        "transform s32_left:",
        "    xalign 0.18",
        "    yalign 1.0",
        "",
        "transform s32_centre:",
        "    xalign 0.5",
        "    yalign 1.0",
        "",
        "transform s32_right:",
        "    xalign 0.82",
        "    yalign 1.0",
        "",
    ]
    return lines


#: Time-of-day keys a scene may use, longest first.
#:
#: Order matters: ``bg_hall_day_alt_door1`` starts with ``bg_hall_day``, so a
#: shortest-first scan would file every alternate under the plain daytime key.
_TIME_KEYS: tuple[str, ...] = (
    "night_alt2",
    "night_alt",
    "night_lit",
    "evening_alt",
    "day_alt",
    "evening",
    "night",
    "day",
)


def _background_definitions(library: ContentLibrary, game_root: Path) -> list[str]:
    """Emit ``image bg <location> <time>`` for every installed background.

    Locations name a background *stem* in their JSON. The packs append their own
    variant tokens after the time (``..._day_door2``, ``..._night_lit``), so
    each installed file is filed under the longest time key it matches and the
    first candidate wins. A scene then writes ``scene bg archive_room evening``
    and gets a real image or a lint error, never a silent black frame.
    """
    lines = [
        "",
        "# Backgrounds, keyed by location id so a scene names a place, not a file.",
        "",
    ]
    directory = game_root / VENDOR_BG_DIR
    if not directory.is_dir():
        lines.append("# (no backgrounds installed; run `s32 assets install`)")
        return lines

    installed = {p.stem: p.suffix for p in directory.iterdir() if p.suffix in {".webp", ".png"}}

    for location_id in sorted(library.locations):
        location = library.locations[location_id]
        if not location.background:
            continue

        by_time: dict[str, list[str]] = {}
        prefix = location.background + "_"
        for name in sorted(installed):
            if not name.startswith(prefix):
                continue
            rest = name[len(prefix) :]
            for key in _TIME_KEYS:
                if rest == key or rest.startswith(key + "_"):
                    by_time.setdefault(key, []).append(name)
                    break

        for time in ("day", "day_alt", "evening", "night", "night_lit"):
            candidates = by_time.get(time)
            if candidates:
                chosen = candidates[0]
                lines.append(
                    f"image bg {location_id} {time} = "
                    f's32_bg("{VENDOR_BG_DIR}/{chosen}{installed[chosen]}", '
                    f'"bg {location_id} {time}")'
                )

        # The bare `bg <location>` form every scene uses when the time of day
        # does not matter to the shot.
        default = by_time.get("day") or by_time.get("evening") or by_time.get("night")
        if default:
            lines.append(
                f"image bg {location_id} = "
                f's32_bg("{VENDOR_BG_DIR}/{default[0]}{installed[default[0]]}", '
                f'"bg {location_id}")'
            )
    lines.append("")
    return lines
