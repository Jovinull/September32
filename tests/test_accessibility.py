"""The engine affordances a tester needs, and the contrast of what we drew.

§85 of the Milestone 5 brief: check the basics before the wave, and do not
build an accessibility suite to do it. Ren'Py supplies most of them — skipping,
auto-forward, dialogue history, self-voicing, keyboard navigation — and what
this file holds is that the project has not switched any of them off, plus the
one thing Ren'Py cannot check because we chose it: the colours.

Contrast is computed rather than eyeballed. Reading dark text on a dark panel
is a thing that looks fine to somebody who already knows what it says, which is
always the person who picked the colour.
"""

from __future__ import annotations

import re

import pytest

from s32tools import paths

SCREENS = paths.game_dir() / "screens"


# ---------------------------------------------------------------------------
# WCAG contrast
# ---------------------------------------------------------------------------


def _channel(value: int) -> float:
    """Linearise one sRGB channel."""
    c = value / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(colour: str) -> float:
    """Relative luminance of an opaque #rrggbb."""
    h = colour.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def composite(fg: str, bg: str) -> str:
    """Flatten an #rrggbbaa over an opaque background.

    The panels in this game are deliberately translucent, so the colour a
    reader actually sees is not the one in the source. Checking the source
    value would pass a panel that is, in practice, the page behind it.
    """
    f, b = fg.lstrip("#"), bg.lstrip("#")
    alpha = int(f[6:8], 16) / 255.0 if len(f) == 8 else 1.0
    out = [
        round(int(f[i : i + 2], 16) * alpha + int(b[i : i + 2], 16) * (1 - alpha))
        for i in (0, 2, 4)
    ]
    return "#" + "".join(f"{value:02x}" for value in out)


def contrast(fg: str, bg: str) -> float:
    """WCAG 2.1 contrast ratio between two opaque colours."""
    a, b = _luminance(fg), _luminance(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


#: The page behind every full-screen panel in the game.
_PAGE = "#0d0c0a"

#: The playtest panel, flattened over the page it sits on.
_PLAYTEST_PANEL = composite("#16130fe8", _PAGE)

#: The archive viewer draws on generated paper. `PAPER` in
#: tools/s32tools/assets/paper.py is the base tone; the texture varies around
#: it by a few values, so the base is the honest thing to measure against.
_PAPER = "#e8e2d2"

#: Every colour a player can read, what it sits on, and its size in pixels.
#:
#: Written out rather than parsed. A screen's background is not derivable from
#: the line that sets a colour, and the point of the table is that somebody
#: adding a colour has to say what it sits on -- which is the question that
#: gets skipped.
READABLE: tuple[tuple[str, str, str, int], ...] = (
    ("playtest heading", "#e8e2d4", _PLAYTEST_PANEL, 44),
    ("playtest subtitle", "#a89d88", _PLAYTEST_PANEL, 24),
    ("playtest body", "#cfc8b8", _PLAYTEST_PANEL, 26),
    ("playtest note", "#9fc48a", _PLAYTEST_PANEL, 22),
    ("playtest session code", "#e8c98a", _PLAYTEST_PANEL, 48),
    ("playtest button", "#cfc8b8", _PLAYTEST_PANEL, 26),
    ("playtest button hover", "#e8c98a", _PLAYTEST_PANEL, 26),
    ("calendar heading", "#e8e2d4", composite("#1c1a1690", "#141210"), 30),
    ("calendar today", "#d8b978", composite("#1c1a1690", "#141210"), 24),
    ("calendar entry", "#ddd6c6", composite("#1c1a1690", "#141210"), 22),
    ("calendar muted", "#8f887a", composite("#1c1a1690", "#141210"), 20),
    ("journal button", "#cfc8b8", "#141210", 24),
    ("journal button hover", "#e8e2d4", "#141210", 24),
    ("document body", "#2a2723", _PAPER, 24),
    ("document label", "#6b6459", _PAPER, 20),
    ("document stamp", "#7a5c4a", _PAPER, 24),
    ("document annotation", "#4a5c6b", _PAPER, 20),
)


@pytest.mark.parametrize(("name", "fg", "bg", "size"), READABLE)
def test_every_readable_colour_meets_wcag_aa(name, fg, bg, size):
    """AA: 4.5:1 for body text, 3:1 at 24px and above.

    Not an aspiration. A tester reading eighteen thousand words of dark-on-dark
    prose will stop, and will report it as "the writing dragged".
    """
    needed = 3.0 if size >= 24 else 4.5
    ratio = contrast(fg, bg)
    assert ratio >= needed, f"{name}: {fg} on {bg} is {ratio:.2f}:1, needs {needed}:1"


def test_the_muted_colours_are_still_readable_as_body_text():
    """The two greys that carry real content, held to the stricter bar.

    `calendar muted` and `document label` are small and are the ones a designer
    reaches for when something should recede. What recedes at 20px on a screen
    somebody is reading for an hour is the content.
    """
    for name, fg, bg in (
        ("calendar muted", "#8f887a", composite("#1c1a1690", "#141210")),
        ("document label", "#6b6459", _PAPER),
    ):
        ratio = contrast(fg, bg)
        assert ratio >= 4.5, f"{name}: {ratio:.2f}:1"


def test_the_contrast_maths_is_right():
    """Two anchors from the WCAG specification itself.

    A contrast checker that is subtly wrong passes everything, which is worse
    than not having one.
    """
    assert contrast("#000000", "#ffffff") == pytest.approx(21.0, abs=0.01)
    assert contrast("#777777", "#ffffff") == pytest.approx(4.48, abs=0.02)
    # Half-transparent white over black is mid-grey, not white.
    assert composite("#ffffff80", "#000000") == "#808080"


# ---------------------------------------------------------------------------
# The affordances Ren'Py provides, and that this project has not removed
# ---------------------------------------------------------------------------


def _game_config() -> str:
    return " ".join(
        path.read_text(encoding="utf-8")
        for path in (
            paths.game_dir() / "options.rpy",
            paths.game_dir() / "gui.rpy",
            paths.game_dir() / "screens.rpy",
        )
    )


def test_skipping_is_available():
    """A reader who has seen a scene must be able to get past it.

    Act 1 has repeatable scenes by design and a tester may replay. Turning
    skipping off would make the second playthrough a punishment.
    """
    config = _game_config()
    assert "config.allow_skipping = False" not in config
    assert 'textbutton _("Skip")' in config


def test_auto_forward_is_available_and_not_instant():
    """`afm_time` of 0 is auto-forward that outruns reading."""
    options = (paths.game_dir() / "options.rpy").read_text(encoding="utf-8")
    match = re.search(r"default preferences\.afm_time = (\d+)", options)
    assert match, "auto-forward has no configured default"
    assert int(match.group(1)) >= 10


def test_dialogue_history_is_deep_enough_to_be_useful():
    """A player who missed a line has to be able to go back and find it.

    Act 1 is around nine hundred lines; a history of twenty would only ever
    hold the scene somebody is already in.
    """
    gui = (paths.game_dir() / "gui.rpy").read_text(encoding="utf-8")
    match = re.search(r"define config\.history_length = (\d+)", gui)
    assert match, "dialogue history is not configured"
    assert int(match.group(1)) >= 100

    screens = (paths.game_dir() / "screens.rpy").read_text(encoding="utf-8")
    assert "screen history():" in screens
    assert 'ShowMenu("history")' in screens


def test_the_help_and_preferences_screens_are_reachable():
    """Where a player finds the keyboard map and the text speed."""
    screens = (paths.game_dir() / "screens.rpy").read_text(encoding="utf-8")
    for name in ("screen help():", "screen preferences():"):
        assert name in screens
    assert 'ShowMenu("help")' in screens
    assert 'ShowMenu("preferences")' in screens


def test_self_voicing_is_not_disabled():
    """Ren'Py's screen reader is on the `v` key and is opt-in per player.

    Nothing in this project should switch it off, and the Help screen should
    still tell somebody it exists.
    """
    config = _game_config()
    assert "config.allow_voicing = False" not in config
    assert "self-voicing" in config


def test_every_screen_this_project_wrote_can_be_closed_without_a_mouse():
    """Each modal surface needs a keyboard way out.

    A screen that traps a keyboard user is not a minor annoyance in a game
    where the way out of every other screen is Escape.
    """
    for name in ("calendar.rpy", "archive.rpy"):
        text = (SCREENS / name).read_text(encoding="utf-8")
        assert 'key "K_ESCAPE"' in text or 'key "game_menu"' in text, name


def test_the_playtest_screens_are_answerable_from_the_keyboard():
    """Consent and the end of the act are both `call screen` with buttons.

    Ren'Py focuses buttons with the arrow keys and activates with Return, so
    what has to be true is that the choices are real buttons rather than
    click-only regions.
    """
    text = (SCREENS / "playtest.rpy").read_text(encoding="utf-8")
    assert text.count("textbutton") >= 6
    assert "imagemap" not in text
    assert "hotspot" not in text
