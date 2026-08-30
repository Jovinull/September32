# Licence evidence — Free Characters for Visual Novels (Set A01) - School Ver.

> Committed record of the terms under which this asset is used.
> Written by `s32 assets evidence`; reviewed by a human before it counts.

## Identification

| | |
| --- | --- |
| Asset id | `pm_char_a01` |
| Name | Free Characters for Visual Novels (Set A01) - School Ver. |
| Author | Potat0Master |
| Type | character |
| Source page | <https://potat0master.itch.io/free-characters-for-visual-novels-set-a01> |
| Download source | itch.io public free-download flow (no account, no purchase) |
| Retrieved | 2026-08-30T17:57:31+00:00 |

## The file that was reviewed

| | |
| --- | --- |
| Archive | `BasicCharacterSetA01_1080p_WEBP_Free.zip` |
| SHA-256 | `b4c6998c8f45e0dcbe4c011b102c4c25a49b7c832b3e090ab60061a52f21fe63` |

The hash is what makes this record specific. A later re-download that produces
different bytes is detectable by `s32 assets verify`, which is the difference
between "we checked this pack" and "we checked this file".

## Licence

| | |
| --- | --- |
| Licence | Custom royalty-free licence (creator's own terms; see license_summary) |
| Licence source | <https://potat0master.itch.io/free-characters-for-visual-novels-set-a01> |
| Terms read on | **2026-08-30** |

### Permissions, as recorded

| Permission | |
| --- | --- |
| Commercial use | yes |
| Modification | yes |
| Redistribution of the files themselves | **NO** |
| Attribution required | **NO** |

`redistribution_allowed` is the field that decides whether the binaries may be
committed. See `docs/decisions/ADR-0003-asset-licensing.md`: this project's
answer is "no third-party binaries in the repository" regardless, because one
rule is easier to follow than eleven.

### Terms as written

The following was on the source page on 2026-08-30. Quoted for the
purpose of recording what the terms were.

```
Verbatim from the pack page on 2026-08-30:

  "These character sprites have a royalty free license. Meaning, you can use
   these character sprites for both personal and commercial projects, as many
   times as you want. Giving credit is not necessary but would be appreciated.
   You can edit and modify these images. However, you cannot resell or
   distribute the images in the form that it is downloaded or even when it is
   modified."

Reading applied by this project: use and modification in the game are permitted;
committing the files (original or processed) to a public repository would be
distribution of the images as files and is therefore NOT permitted. Hence
`assets/vendor/` and `assets/processed/` are gitignored.
```

### AI-related terms

```
The page states "No generative AI was used" as a statement about how the assets
were made. No restriction on the buyer's own use of AI is stated. This project
still applies docs/legal/AI_AND_ASSETS_POLICY.md: these files are never uploaded
to an AI service, never used for training, img2img or style transfer.
```

This project's own policy is stricter than most licences require: no
third-party asset is ever sent to an AI service, used for training, or modified
by a generative model. See `docs/legal/AI_AND_ASSETS_POLICY.md`.

## Attribution text

The exact credit shown in-game and in `CREDITS.md`:

```
Character sprites by Potat0Master (potat0master.itch.io)
```

## Notes

Free tier: Chinatsu, Kanako, Kohaku, Tomomi, Ume — 17 expressions each, summer
and winter school uniforms. Three further characters (Ayumi, Mao, Shiori) are
behind a $2 tier and are NOT used.

Asset identity is kept separate from canon identity: `pm_a01_chinatsu` is a
sprite, `iris` is a character. See data/characters/*.json.

---

*Generated 2026-08-30. If the terms on the source page have changed since
2026-08-30, this file records what they were, not what they are — re-read
them and add a new dated section rather than editing this one.*
