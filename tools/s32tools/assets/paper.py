"""Deterministic archive-paper textures.

The document viewer needs to feel like paper without becoming a texture system.
Three small tiles, generated once at build time from a fixed seed, composited in
Ren'Py underneath real text.

Three constraints, all deliberate:

**Deterministic.** A fixed seed and no system randomness, so the same commit
always produces the same bytes. Assets that differ per run are assets that
cannot be reviewed.

**Build-time, not runtime.** Generated into ``game/images/documents/`` and
committed. These are first-party — our arithmetic, not anyone's artwork — so
unlike everything in ``assets/vendor/`` they *are* redistributable and belong in
the repository. Generating them at launch would also mean rebuilding textures
the player already has.

**Subtle.** The effect should be a suggestion of paper, not a photograph of one.
If a tile is noticeable on its own, it is too strong: the words are the content
and the paper is the surface they sit on.

Nothing here is generative in the AI sense — see
``docs/legal/AI_AND_ASSETS_POLICY.md``. Every operation is arithmetic on pixels.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

#: One seed for the whole set. Changing it changes every tile, which is why it
#: is a constant and not a parameter.
SEED = 32_0001

#: Tile size. Small enough to be cheap, large enough that the repeat is not
#: legible at the sizes the viewer draws it.
TILE = 512

#: Paper grounds, warm and low-contrast. Pure white is not a paper colour.
PAPER = (232, 226, 210)
CARD = (240, 234, 216)
INK = (42, 39, 35)


def _noise(width: int, height: int, seed: int) -> list[int]:
    """Return deterministic per-pixel noise in 0-255.

    A hash chain rather than :mod:`random`: it depends on nothing but the seed
    and the index, so it cannot be perturbed by anything else in the process.
    """
    values: list[int] = []
    block = b""
    index = 0
    needed = width * height
    while len(values) < needed:
        block = hashlib.blake2b(f"{seed}:{index}".encode(), digest_size=64).digest()
        values.extend(block)
        index += 1
    return values[:needed]


def _grained(ground: tuple[int, int, int], amplitude: int, blur: float, seed: int, size: int) -> Image.Image:
    """Return a ground colour modulated by fine deterministic grain.

    The grain is added to each channel rather than used as a compositing mask.
    A mask averaging 128 blends two colours evenly at every pixel and produces a
    flat fill — which is what the first version of this function did, and the
    determinism test caught it by hashing two supposedly different tiles to the
    same bytes.
    """
    noise = _noise(size, size, seed)
    pixels: list[tuple[int, int, int]] = []
    for value in noise:
        delta = ((value - 128) * amplitude) // 128
        pixels.append(
            (
                max(0, min(255, ground[0] + delta)),
                max(0, min(255, ground[1] + delta)),
                max(0, min(255, ground[2] + delta)),
            )
        )
    sheet = Image.new("RGB", (size, size))
    sheet.putdata(pixels)
    return sheet.filter(ImageFilter.GaussianBlur(blur))


def paper_grain(seed: int = SEED, size: int = TILE) -> Image.Image:
    """A tileable sheet of paper: warm ground plus very fine grain."""
    return _grained(PAPER, amplitude=7, blur=0.4, seed=seed, size=size)


def card_stock(seed: int = SEED + 1, size: int = TILE) -> Image.Image:
    """Heavier, lighter stock for catalogue cards: coarser, softer grain."""
    return _grained(CARD, amplitude=5, blur=0.8, seed=seed, size=size)


def ruled_lines(size: int = TILE, spacing: int = 34) -> Image.Image:
    """Faint horizontal rules, for ledger pages.

    Transparent except for the rules, so the viewer can lay it over either
    stock without a second variant of each.
    """
    sheet = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    for y in range(spacing, size, spacing):
        draw.line([(0, y), (size, y)], fill=(*INK, 26), width=1)
    return sheet


def edge_shadow(size: int = TILE) -> Image.Image:
    """A soft inner shadow, so a sheet reads as an object with a thickness."""
    shadow = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(shadow)
    for step in range(14):
        value = int(46 * (1 - step / 14))
        draw.rectangle([step, step, size - 1 - step, size - 1 - step], outline=value)
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))

    sheet = Image.new("RGBA", (size, size), (*INK, 0))
    sheet.putalpha(shadow)
    return sheet


#: Filename -> builder. The viewer names these; nothing else should.
TEXTURES: dict[str, Callable[[], Image.Image]] = {
    "doc_paper.png": paper_grain,
    "doc_card.png": card_stock,
    "doc_rules.png": ruled_lines,
    "doc_edge.png": edge_shadow,
}


def build(destination: Path) -> list[Path]:
    """Generate every texture into ``destination``. Returns the paths written."""
    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, builder in TEXTURES.items():
        path = destination / filename
        builder().save(path, "PNG", optimize=True)
        written.append(path)
    return written


def digest(destination: Path) -> dict[str, str]:
    """Return the SHA-256 of each generated texture.

    Used by the test that asserts the generator is deterministic: regenerating
    must produce identical bytes, or "build-time asset" means nothing.
    """
    return {
        filename: hashlib.sha256((destination / filename).read_bytes()).hexdigest()
        for filename in sorted(TEXTURES)
        if (destination / filename).exists()
    }
