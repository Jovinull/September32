# Licence evidence — Ren'Py Visual Novel Engine 8.5.3

> Committed record of the terms under which this asset is used.
> Written by `s32 assets evidence`; reviewed by a human before it counts.

## Identification

| | |
| --- | --- |
| Asset id | `renpy` |
| Name | Ren'Py Visual Novel Engine 8.5.3 |
| Author | Tom Rothamel and the Ren'Py contributors |
| Type | software |
| Source page | <https://www.renpy.org/latest.html> |
| Download source | https://www.renpy.org/dl/8.5.3/renpy-8.5.3-sdk.zip |
| Retrieved | not yet downloaded |

## The file that was reviewed

| | |
| --- | --- |
| Archive | `not yet downloaded` |
| SHA-256 | `not yet downloaded` |

The hash is what makes this record specific. A later re-download that produces
different bytes is detectable by `s32 assets verify`, which is the difference
between "we checked this pack" and "we checked this file".

## Licence

| | |
| --- | --- |
| Licence | MIT (engine); see Ren'Py's own LICENSE.txt for bundled components |
| Licence source | <https://www.renpy.org/doc/html/license.html> |
| Terms read on | **2026-08-30** |

### Permissions, as recorded

| Permission | |
| --- | --- |
| Commercial use | yes |
| Modification | yes |
| Redistribution of the files themselves | yes |
| Attribution required | yes |

`redistribution_allowed` is the field that decides whether the binaries may be
committed. See `docs/decisions/ADR-0003-asset-licensing.md`: this project's
answer is "no third-party binaries in the repository" regardless, because one
rule is easier to follow than eleven.

### Terms as written

The following was on the source page on 2026-08-30. Quoted for the
purpose of recording what the terms were.

```
Ren'Py itself is MIT-licensed. It bundles components under other free licences
(among them Python, SDL2, FFmpeg subsets and freetype), each with its own terms.
A game built with Ren'Py must reproduce the notices the engine generates; the
`renpy` distribute step does this automatically into the built package.

Note the three distinct licences this project must not conflate:
  1. Ren'Py's own licence (MIT, plus bundled component licences)
  2. this project's licence (see /LICENSE — provisional, all rights reserved)
  3. each third-party asset's licence (this file)
```

### AI-related terms

```
None.
```

This project's own policy is stricter than most licences require: no
third-party asset is ever sent to an AI service, used for training, or modified
by a generative model. See `docs/legal/AI_AND_ASSETS_POLICY.md`.

## Attribution text

The exact credit shown in-game and in `CREDITS.md`:

```
Made with Ren'Py — https://www.renpy.org/
```

## Notes

The SDK is installed to `.tools/renpy/` and is never committed. See
docs/decisions/ADR-0001-renpy.md.

One exception to the "no third-party binaries" rule applies here and is
deliberate: `game/gui/` contains Ren'Py's own GUI template images, copied from
the SDK and rescaled to 1080p by tools/s32tools/renpy_gui_scale.py. Ren'Py ships
that template expressly so projects copy it, and a built game needs the images
present because the SDK's regeneration step only runs in development. They are
therefore committed, under Ren'Py's own licence, and will be replaced by the
project's own interface (docs/style/VISUAL_DESIGN_SYSTEM.md).

---

*Generated 2026-08-30. If the terms on the source page have changed since
2026-08-30, this file records what they were, not what they are — re-read
them and add a new dated section rather than editing this one.*
