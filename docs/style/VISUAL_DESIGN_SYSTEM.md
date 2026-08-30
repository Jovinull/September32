# Visual design system

**Status: PROVISIONAL for the identity; CANON for the geometry.**

The numbers here are the single source of truth. A magic number in a `.rpy` file
is a bug — it is how a project ends up unable to change its sprite scale.

## Geometry

| | |
| --- | --- |
| Design resolution | **1920 × 1080** |
| Safe area | 64 px inset on all sides for anything that must not be cropped |
| Text safe area | 96 px inset |

The Ren'Py GUI template ships drawn for 1280 × 720. It was rescaled ×1.5 by
`tools/s32tools/renpy_gui_scale.py`, which also scaled every pixel constant in
`game/gui.rpy` — `gui.scale()` in the template is the identity function, so
nothing scales itself. That module documents the whole derivation and is
re-runnable if the template is ever refreshed from a newer SDK.

## Sprites

Source sprites are 720 × 1080 with the figure's feet at the bottom edge, so a
scale of 1.0 already fills the frame vertically.

| | |
| --- | --- |
| Scale | `1.0` (`DEFAULT_SPRITE` in `generate_renpy_images.py`) |
| Baseline | y = 1080, i.e. `yalign 1.0` |
| Left position | `xalign 0.18` (`s32_left`) |
| Centre | `xalign 0.5` (`s32_centre`) |
| Right | `xalign 0.82` (`s32_right`) |

There is exactly **one transform per character**, generated. A scene writes
`show iris school_summer happy at s32_centre` and never a zoom.

Per-character overrides, when a future asset needs them, belong in
`data/characters/<id>.json` — not in a scene.

## Typography

| Role | Face | Size |
| --- | --- | --- |
| Dialogue | Source Sans 3 Regular | 33 px |
| Speaker name | Source Sans 3 Semibold | 45 px |
| Interface | Source Sans 3 Regular | 33 px |
| Titles | Source Serif 4 Semibold | 75 px |
| Documents | Source Serif 4 Regular | 22–28 px |
| Notifications | Source Sans 3 Regular | 24 px |

Both faces are SIL OFL 1.1, from the upstream Adobe releases, with complete Latin
coverage including the diacritics pt-BR needs.

The sans/serif split is semantic, not decorative: **sans is the game speaking,
serif is the archive speaking.** A document rendered in the dialogue face would
read as narration, which is exactly wrong.

## Palette

`PROVISIONAL`. The direction is *school archive + analogue photography + paper +
administrative document*.

| Role | Value | Notes |
| --- | --- | --- |
| Paper | `#e8e2d4` | Off-white. Never pure white. |
| Ink | `#2a2723` | Near-black, warm. Never pure black. |
| Card | `#f5efdd` | Archive card, catalogue label. |
| Accent | `#7c5c8a` | Muted plum. Sparing. |
| Muted | `#8f887a` | Secondary text, dates, filing marks. |
| Warning | `#d08a7a` | Errors, contradictions. Desaturated on purpose. |

Nothing saturated. Nothing that reads as horror. The unease arrives through
content, not colour temperature.

## Transitions

Slow and plain, by policy.

```
enter / exit    Dissolve(0.3)
intra           Dissolve(0.2)
scene change    fade / dissolve
end of game     Dissolve(0.6)
```

A busy transition vocabulary spends attention that the story needs available.
There is no transition that means "something is wrong" — that would announce it.

## Interface hierarchy

1. **Dialogue** — the game. Everything else is subordinate.
2. **Choices** — clear, equal weight, never ranked by styling.
3. **Documents** — the archive viewer. A distinct mode, not a popup.
4. **Journal** — clues and known facts. Reference, entered deliberately.
5. **System** — save, load, preferences. Present, quiet, out of the way.

## The archive viewer

`PROVISIONAL` — scaffolded, not built.

The most important interface in the game after the dialogue box. Its job is to
make a document feel like an object: paper texture, an edge, a filing mark, a
catalogue number, and text in the serif face. The player should feel they are
looking at a thing rather than reading a UI.

Rules: never animate a document. Never distort one. Never add an effect that
signals significance — the significance is what it says.

## The Kenney question

The CC0 Kenney UI pack is installed and is **scaffolding, not a theme**. Only the
82 neutral greys from `PNG/Grey/Default` are imported, deliberately, so that
using the colourful set is not an easy accident.

The shipped interface must not read as "Kenney UI". Replacing it with the
archive/document language above is planned work, tracked in
`docs/production/ART_GAP_ANALYSIS.md`.

## The calendar

`IDEA`, and the best interface idea the project has.

A calendar widget that shows the month. Early on it is unremarkable. Much later,
it accepts:

```
30   31   32
```

No animation. No sound. No comment. It is simply there the next time the player
opens it, and it stays there.
