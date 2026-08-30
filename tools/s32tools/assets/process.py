"""The deterministic, non-generative image pipeline.

Vendor originals are never modified. Everything the game loads is produced from
them by a recorded chain of transformations, so ``assets/processed/`` can be
deleted and rebuilt byte-identically at any time.

**Nothing here is generative.** No model, no inpainting, no upscaler, no style
transfer, no img2img -- see ``docs/legal/AI_AND_ASSETS_POLICY.md``. Every
operation is arithmetic on pixels that a human could describe in one sentence.

There is also a limit on what this pipeline is *for*. Grading can pull two
compatible packs into the same room; it cannot make two different art styles
look like one. When the audit says a pack does not fit, the answer is to use
fewer, more coherent assets -- not a heavier filter. Pushing grading far enough
to disguise a mismatch produces something that looks processed, which is worse
than the mismatch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

#: Project render target. Everything is produced at or below this.
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080


@dataclass(frozen=True, slots=True)
class Treatment:
    """A named, reproducible chain of adjustments.

    Values of ``1.0`` are identity. The defaults are all identity on purpose:
    the prototype ships assets as the artists made them, and grading is added
    deliberately, per class of asset, with a recorded reason.
    """

    name: str
    brightness: float = 1.0
    contrast: float = 1.0
    saturation: float = 1.0
    #: Blend toward this RGB, 0.0-1.0. The archival warmth applied to documents.
    tint: tuple[int, int, int] | None = None
    tint_strength: float = 0.0
    #: Convert to greyscale before any other adjustment.
    grayscale: bool = False
    #: Resize so the longest edge is at most this. ``None`` leaves size alone.
    max_edge: int | None = None
    notes: str = ""

    def describe(self) -> list[str]:
        """Return the transformation list recorded in the manifest."""
        steps: list[str] = []
        if self.grayscale:
            steps.append("grayscale")
        if self.max_edge:
            steps.append(f"resize(max_edge={self.max_edge}, lanczos)")
        for label, value in (
            ("brightness", self.brightness),
            ("contrast", self.contrast),
            ("saturation", self.saturation),
        ):
            if value != 1.0:
                steps.append(f"{label}({value})")
        if self.tint and self.tint_strength:
            steps.append(f"tint({self.tint}, {self.tint_strength})")
        return steps or ["copy (no adjustment)"]


#: Identity. Character sprites and backgrounds ship as the artist made them:
#: they already share a palette and a light direction, and touching them would
#: only introduce drift.
PASSTHROUGH = Treatment(
    name="passthrough",
    notes="No adjustment. The Potat0Master packs already agree with each other.",
)

#: Applied to the CC0 prop icons so a general-purpose item set reads as this
#: game's archive rather than as a borrowed pack. Desaturated, warmed and
#: slightly flattened, which is what a scanned catalogue card looks like.
ARCHIVAL = Treatment(
    name="archival",
    grayscale=True,
    brightness=1.04,
    contrast=0.92,
    tint=(232, 220, 196),
    tint_strength=0.35,
    max_edge=256,
    notes=(
        "Deterministic archival card treatment for inventory and clue icons. "
        "Greyscale then a warm paper tint, so 160 unrelated CC0 items read as "
        "one catalogue."
    ),
)

TREATMENTS: dict[str, Treatment] = {
    "character": PASSTHROUGH,
    "background": PASSTHROUGH,
    "ui": PASSTHROUGH,
    "prop": ARCHIVAL,
}


@dataclass(slots=True)
class ProcessResult:
    """What one processing pass produced."""

    written: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    unmapped: list[str] = field(default_factory=list)
    transformations: list[str] = field(default_factory=list)


def apply_treatment(image: Image.Image, treatment: Treatment) -> Image.Image:
    """Apply a treatment to an image, preserving alpha.

    Order is fixed and matters: greyscale, resize, then tonal adjustments, then
    tint. Reordering would change the output, so it is not a parameter.
    """
    result = image.convert("RGBA")

    if treatment.grayscale:
        alpha = result.getchannel("A")
        grey = ImageOps.grayscale(result.convert("RGB")).convert("RGB")
        result = grey.convert("RGBA")
        result.putalpha(alpha)

    if treatment.max_edge:
        longest = max(result.size)
        if longest > treatment.max_edge:
            scale = treatment.max_edge / longest
            new_size = (max(1, round(result.width * scale)), max(1, round(result.height * scale)))
            result = result.resize(new_size, Image.Resampling.LANCZOS)

    for enhancer, value in (
        (ImageEnhance.Brightness, treatment.brightness),
        (ImageEnhance.Contrast, treatment.contrast),
        (ImageEnhance.Color, treatment.saturation),
    ):
        if value != 1.0:
            alpha = result.getchannel("A")
            adjusted = enhancer(result.convert("RGB")).enhance(value).convert("RGBA")
            adjusted.putalpha(alpha)
            result = adjusted

    if treatment.tint and treatment.tint_strength > 0:
        alpha = result.getchannel("A")
        overlay = Image.new("RGB", result.size, treatment.tint)
        blended = Image.blend(result.convert("RGB"), overlay, treatment.tint_strength)
        result = blended.convert("RGBA")
        result.putalpha(alpha)

    return result


def process_file(
    source: Path,
    destination: Path,
    treatment: Treatment,
    *,
    output_format: str | None = None,
) -> None:
    """Process one image into ``destination``, creating parent directories."""
    destination.parent.mkdir(parents=True, exist_ok=True)

    if treatment is PASSTHROUGH and output_format is None:
        # A byte copy is both faster and safer than a decode/encode round trip,
        # which would silently re-compress a WebP the artist already tuned.
        destination.write_bytes(source.read_bytes())
        return

    with Image.open(source) as image:
        result = apply_treatment(image, treatment)
        fmt = output_format or ("WEBP" if destination.suffix == ".webp" else "PNG")
        if fmt == "WEBP":
            result.save(destination, "WEBP", quality=92, method=6)
        else:
            result.save(destination, fmt)
