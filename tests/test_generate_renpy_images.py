"""Generated Ren'Py images keep shared stage transforms and stable output."""

from __future__ import annotations

from pathlib import Path

from s32tools.assets.generate_renpy_images import generate


def test_image_generation_keeps_group_stage_positions(library, tmp_path: Path) -> None:
    result = generate(library, tmp_path / "processed", tmp_path / "game")

    for position in "abcd":
        assert f"transform s32_quad_{position}:" in result.text


def test_image_generation_has_no_wall_clock_output(library, tmp_path: Path) -> None:
    first = generate(library, tmp_path / "processed", tmp_path / "game")
    second = generate(library, tmp_path / "processed", tmp_path / "game")

    assert first.text == second.text
