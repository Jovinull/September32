"""Deterministic visual-consistency audit for character art.

Mixing sprites from several artists is the fastest way to make a visual novel
look like an asset dump, and it is very hard to un-mix once the writing depends
on a cast. So compatibility is measured before a pack is adopted, not after.

**Everything here is computed locally from pixel data.** No image is sent to any
external service, for analysis or anything else -- see
``docs/legal/AI_AND_ASSETS_POLICY.md``. That constraint shapes what is measured:
these are proxies a script can compute honestly, not aesthetic judgements.

Measured per sprite:

``canvas``
    Image dimensions. Different canvas sizes between packs mean every scene
    needs per-pack placement fudging.
``content_box``
    Bounding box of non-transparent pixels, normalised. Tells whether two packs
    frame their characters the same way -- the single biggest cause of a cast
    that looks like it was pasted together.
``head_width``
    Width of the opaque region in the top 12% of the content box, as a fraction
    of the content width. A usable proxy for head-to-body proportion, which is
    what makes an anime style read as one style.
``edge_density``
    Fraction of pixels at a strong luminance gradient. A proxy for line weight:
    a heavier-lined pack scores noticeably higher.
``saturation``/``value``
    Mean HSV saturation and value over opaque pixels. Two packs that disagree
    here will not sit on the same background without grading.

A **compatibility score** compares a candidate pack against the chosen core and
is reported alongside the raw numbers, never instead of them: the numbers are
evidence, the score is a summary, and a human makes the call.
"""

from __future__ import annotations

import colorsys
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from PIL import Image

#: Sample stride for per-pixel statistics. A 720x1080 sprite has 777k pixels;
#: every 4th pixel in each axis is 48k samples, which is plenty for a mean and
#: keeps a 400-sprite audit to a few seconds.
STRIDE = 4

#: Fraction of the content box treated as "the head" for the proportion proxy.
HEAD_BAND = 0.12

#: Luminance jump that counts as an edge, on 0-255.
EDGE_THRESHOLD = 40


@dataclass(slots=True)
class SpriteMetrics:
    """Measurements for one sprite image."""

    path: str
    width: int
    height: int
    content_left: float
    content_top: float
    content_right: float
    content_bottom: float
    head_width_ratio: float
    edge_density: float
    saturation: float
    value: float
    opaque_ratio: float

    @property
    def content_height_ratio(self) -> float:
        """Vertical extent of the character as a fraction of the canvas."""
        return self.content_bottom - self.content_top

    @property
    def content_width_ratio(self) -> float:
        """Horizontal extent of the character as a fraction of the canvas."""
        return self.content_right - self.content_left


@dataclass(slots=True)
class PackMetrics:
    """Aggregated measurements for one pack."""

    asset_id: str
    sprite_count: int
    canvas_sizes: dict[str, int] = field(default_factory=dict)
    content_top: float = 0.0
    content_bottom: float = 0.0
    content_width: float = 0.0
    head_width_ratio: float = 0.0
    edge_density: float = 0.0
    saturation: float = 0.0
    value: float = 0.0
    characters: list[str] = field(default_factory=list)
    outfits: dict[str, list[str]] = field(default_factory=dict)
    expressions: list[str] = field(default_factory=list)


def measure_sprite(path: Path) -> SpriteMetrics | None:
    """Measure one sprite. Returns ``None`` for an image with no opaque pixels."""
    with Image.open(path) as raw:
        image = raw.convert("RGBA")
        width, height = image.size
        alpha = image.getchannel("A")
        box = alpha.getbbox()
        if box is None:
            return None
        left, top, right, bottom = box

        pixels = image.load()
        if pixels is None:
            return None

        saturations: list[float] = []
        values: list[float] = []
        opaque = 0
        sampled = 0
        edges = 0
        luminance: dict[tuple[int, int], float] = {}

        for y in range(top, bottom, STRIDE):
            for x in range(left, right, STRIDE):
                r, g, b, a = cast("tuple[int, int, int, int]", pixels[x, y])
                sampled += 1
                if a < 128:
                    continue
                opaque += 1
                _, lightness, saturation = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
                saturations.append(saturation)
                values.append(lightness)
                luminance[x, y] = 0.299 * r + 0.587 * g + 0.114 * b

        for (x, y), lum in luminance.items():
            right_neighbour = luminance.get((x + STRIDE, y))
            down_neighbour = luminance.get((x, y + STRIDE))
            if (right_neighbour is not None and abs(lum - right_neighbour) > EDGE_THRESHOLD) or (
                down_neighbour is not None and abs(lum - down_neighbour) > EDGE_THRESHOLD
            ):
                edges += 1

        head_bottom = top + max(1, int((bottom - top) * HEAD_BAND))
        head_box = alpha.crop((left, top, right, head_bottom)).getbbox()
        head_width = (head_box[2] - head_box[0]) if head_box else 0

    content_width = max(1, right - left)
    return SpriteMetrics(
        path=str(path),
        width=width,
        height=height,
        content_left=left / width,
        content_top=top / height,
        content_right=right / width,
        content_bottom=bottom / height,
        head_width_ratio=head_width / content_width,
        edge_density=edges / max(1, len(luminance)),
        saturation=statistics.fmean(saturations) if saturations else 0.0,
        value=statistics.fmean(values) if values else 0.0,
        opaque_ratio=opaque / max(1, sampled),
    )


def measure_pack(vendor_root: Path, asset_id: str, *, sample: int = 24) -> PackMetrics:
    """Measure a pack, sampling evenly across its sprites.

    Args:
        vendor_root: ``assets/vendor``.
        asset_id: Pack directory name.
        sample: How many sprites to measure. Evenly spaced across the sorted
            file list so the sample spans every character and outfit rather than
            just the alphabetically first one.
    """
    directory = vendor_root / asset_id
    files = sorted(p for p in directory.rglob("*") if p.suffix.lower() in {".webp", ".png"})
    if not files:
        return PackMetrics(asset_id=asset_id, sprite_count=0)

    step = max(1, len(files) // sample)
    chosen = files[::step][:sample]

    measurements = [m for m in (measure_sprite(p) for p in chosen) if m is not None]
    if not measurements:
        return PackMetrics(asset_id=asset_id, sprite_count=len(files))

    sizes: dict[str, int] = {}
    for m in measurements:
        sizes[f"{m.width}x{m.height}"] = sizes.get(f"{m.width}x{m.height}", 0) + 1

    characters, outfits, expressions = _parse_names(files)

    return PackMetrics(
        asset_id=asset_id,
        sprite_count=len(files),
        canvas_sizes=dict(sorted(sizes.items())),
        content_top=statistics.fmean(m.content_top for m in measurements),
        content_bottom=statistics.fmean(m.content_bottom for m in measurements),
        content_width=statistics.fmean(m.content_width_ratio for m in measurements),
        head_width_ratio=statistics.fmean(m.head_width_ratio for m in measurements),
        edge_density=statistics.fmean(m.edge_density for m in measurements),
        saturation=statistics.fmean(m.saturation for m in measurements),
        value=statistics.fmean(m.value for m in measurements),
        characters=characters,
        outfits=outfits,
        expressions=expressions,
    )


def _parse_names(files: list[Path]) -> tuple[list[str], dict[str, list[str]], list[str]]:
    """Split ``<character>_<outfit>_<expression>`` filenames into their parts."""
    characters: set[str] = set()
    outfits: dict[str, set[str]] = {}
    expressions: set[str] = set()
    for path in files:
        parts = path.stem.split("_")
        if len(parts) < 3:
            continue
        character, outfit, expression = parts[0], parts[1], "_".join(parts[2:])
        characters.add(character)
        outfits.setdefault(character, set()).add(outfit)
        expressions.add(expression)
    return (
        sorted(characters),
        {k: sorted(v) for k, v in sorted(outfits.items())},
        sorted(expressions),
    )


def compatibility(core: PackMetrics, candidate: PackMetrics) -> tuple[float, list[str]]:
    """Score how well a candidate pack sits beside the core, on 0-10.

    Returns:
        ``(score, notes)`` where notes explain each deduction. The notes matter
        more than the number: "heads are 18% wider" is actionable, "6.2/10" is
        not.
    """
    notes: list[str] = []
    score = 10.0

    # Canvas *height* is what has to match: it sets the baseline every sprite is
    # anchored to. Width varies naturally with pose and costs nothing, so
    # penalising it would flag every pack for a non-problem.
    core_heights = {size.split("x")[1] for size in core.canvas_sizes}
    candidate_heights = {size.split("x")[1] for size in candidate.canvas_sizes}
    if core_heights != candidate_heights:
        score -= 2.5
        notes.append(
            f"canvas height differs: core {sorted(core_heights)} vs candidate "
            f"{sorted(candidate_heights)} — sprites will not share a baseline"
        )
    elif len(candidate.canvas_sizes) > 1:
        notes.append(
            f"canvas widths vary within the pack ({', '.join(candidate.canvas_sizes)}); "
            "normal for cutouts, but each sprite needs its own xalign"
        )

    for label, core_value, candidate_value, tolerance, penalty in (
        ("head/body proportion", core.head_width_ratio, candidate.head_width_ratio, 0.08, 3.0),
        ("framing (content height)", core.content_bottom - core.content_top,
         candidate.content_bottom - candidate.content_top, 0.06, 2.0),
        ("line weight (edge density)", core.edge_density, candidate.edge_density, 0.05, 2.0),
        ("saturation", core.saturation, candidate.saturation, 0.10, 1.5),
        ("brightness", core.value, candidate.value, 0.10, 1.0),
    ):
        if core_value == 0:
            continue
        drift = abs(candidate_value - core_value) / max(core_value, 1e-6)
        if drift > tolerance:
            deduction = min(penalty, penalty * drift / (tolerance * 4))
            score -= deduction
            notes.append(
                f"{label}: {candidate_value:.3f} vs core {core_value:.3f} "
                f"({drift:+.0%}) — -{deduction:.1f}"
            )

    if core.expressions and candidate.expressions:
        missing = set(core.expressions) - set(candidate.expressions)
        if missing:
            score -= min(2.0, 0.2 * len(missing))
            notes.append(
                f"missing {len(missing)} expression(s) the core has: "
                f"{', '.join(sorted(missing)[:6])}"
            )

    return max(0.0, round(score, 1)), notes
