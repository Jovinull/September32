"""Contact sheets: every installed asset on one page.

A writer choosing an expression, or an artist judging whether two packs sit
together, needs to see the set at once. Opening four hundred files one at a time
is not a workflow.

Generated locally with Pillow, from files already on disk. Nothing is uploaded
anywhere — see ``docs/legal/AI_AND_ASSETS_POLICY.md``. The sheets land in
``tools/reports/contact-sheets/`` and are gitignored, because they are
derivative images of third-party art and fall under the same redistribution
restriction as the originals (ADR-0003).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

#: Thumbnail cell size. Big enough to tell two expressions apart, small enough
#: that a whole character fits on one screen.
CELL = (180, 270)

#: Room under each cell for its filename.
LABEL_HEIGHT = 26

COLUMNS = 8
MARGIN = 16
BACKGROUND = (24, 22, 20)
LABEL_COLOUR = (200, 194, 180)
HEADING_COLOUR = (232, 201, 138)


def _font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    """Return a font, falling back to Pillow's bitmap default.

    The project's own font may not be installed yet; a contact sheet with ugly
    labels is far better than one that fails to build.
    """
    for candidate in (
        Path("assets/processed/fonts/SourceSans3-Regular.ttf"),
        Path("game/gui/vendor/fonts/SourceSans3-Regular.ttf"),
    ):
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size)
            except OSError:
                pass
    return ImageFont.load_default()


def build_sheet(paths: list[Path], title: str, destination: Path) -> Path | None:
    """Render one contact sheet. Returns the path, or ``None`` if there was nothing."""
    if not paths:
        return None

    columns = min(COLUMNS, len(paths))
    rows = (len(paths) + columns - 1) // columns
    heading = 44

    width = MARGIN * 2 + columns * (CELL[0] + MARGIN)
    height = heading + MARGIN + rows * (CELL[1] + LABEL_HEIGHT + MARGIN)

    sheet = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    draw.text((MARGIN, 14), f"{title}  —  {len(paths)} files", fill=HEADING_COLOUR, font=_font(20))

    label_font = _font(12)

    for index, path in enumerate(sorted(paths)):
        column, row = index % columns, index // columns
        x = MARGIN + column * (CELL[0] + MARGIN)
        y = heading + MARGIN + row * (CELL[1] + LABEL_HEIGHT + MARGIN)

        try:
            with Image.open(path) as image:
                thumbnail = image.convert("RGBA")
                thumbnail.thumbnail(CELL, Image.Resampling.LANCZOS)
        except OSError:
            draw.text((x, y), "unreadable", fill=(200, 90, 90), font=label_font)
            continue

        # Bottom-aligned: character sprites are anchored at the feet, and a
        # sheet that centres them makes height differences invisible, which is
        # the opposite of what the sheet is for.
        offset_x = x + (CELL[0] - thumbnail.width) // 2
        offset_y = y + (CELL[1] - thumbnail.height)
        sheet.paste(thumbnail, (offset_x, offset_y), thumbnail)

        label = path.stem
        if len(label) > 30:
            label = label[:27] + "..."
        draw.text((x, y + CELL[1] + 6), label, fill=LABEL_COLOUR, font=label_font)

    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, "PNG")
    return destination


def build_all(processed_root: Path, out_dir: Path) -> list[Path]:
    """Build one sheet per character-outfit, plus sheets for the other kinds."""
    written: list[Path] = []

    characters = processed_root / "characters"
    if characters.is_dir():
        groups: dict[str, list[Path]] = {}
        for path in sorted(characters.glob("char_*")):
            parts = path.stem.split("_")
            if len(parts) < 4:
                continue
            key = f"{parts[1]}_{parts[2]}_{parts[3]}" if parts[2] in {"school", "casual"} else parts[1]
            groups.setdefault(key, []).append(path)
        for key, paths in sorted(groups.items()):
            result = build_sheet(paths, f"characters — {key}", out_dir / f"characters_{key}.png")
            if result:
                written.append(result)

    for kind, title in (("backgrounds", "backgrounds"), ("props", "props"), ("ui", "ui")):
        directory = processed_root / kind
        if not directory.is_dir():
            continue
        files = sorted(p for p in directory.iterdir() if p.suffix in {".webp", ".png"})
        # Large sets are split so no single sheet becomes unopenable.
        for chunk_index in range(0, len(files), 64):
            chunk = files[chunk_index : chunk_index + 64]
            suffix = "" if len(files) <= 64 else f"_{chunk_index // 64 + 1}"
            result = build_sheet(chunk, title, out_dir / f"{kind}{suffix}.png")
            if result:
                written.append(result)

    return written
