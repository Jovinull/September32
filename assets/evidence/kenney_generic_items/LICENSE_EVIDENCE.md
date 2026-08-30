# Licence evidence — Generic Items

> Committed record of the terms under which this asset is used.
> Written by `s32 assets evidence`; reviewed by a human before it counts.

## Identification

| | |
| --- | --- |
| Asset id | `kenney_generic_items` |
| Name | Generic Items |
| Author | Kenney (kenney.nl) |
| Type | prop |
| Source page | <https://kenney.nl/assets/generic-items> |
| Download source | https://kenney.nl/media/pages/assets/generic-items/96b9087204-1677667000/kenney_generic-items.zip |
| Retrieved | 2026-08-30T17:56:32+00:00 |

## The file that was reviewed

| | |
| --- | --- |
| Archive | `kenney_generic-items.zip` |
| SHA-256 | `93f622e46a86f26c8c718cc133c99b545059758abdba65b335c687a581efa059` |

The hash is what makes this record specific. A later re-download that produces
different bytes is detectable by `s32 assets verify`, which is the difference
between "we checked this pack" and "we checked this file".

## Licence

| | |
| --- | --- |
| Licence | CC0 1.0 Universal (public domain dedication) |
| Licence source | <https://creativecommons.org/publicdomain/zero/1.0/> |
| Terms read on | **2026-08-30** |

### Permissions, as recorded

| Permission | |
| --- | --- |
| Commercial use | yes |
| Modification | yes |
| Redistribution of the files themselves | yes |
| Attribution required | **NO** |

`redistribution_allowed` is the field that decides whether the binaries may be
committed. See `docs/decisions/ADR-0003-asset-licensing.md`: this project's
answer is "no third-party binaries in the repository" regardless, because one
rule is easier to follow than eleven.

### Terms as written

The following was on the source page on 2026-08-30. Quoted for the
purpose of recording what the terms were.

```
The asset page states the licence as "Creative Commons CC0", linking to
creativecommons.org/publicdomain/zero/1.0/. CC0 waives copyright to the extent
possible: use, modification, redistribution and commercial use are all permitted
with no attribution requirement.
```

### AI-related terms

```
None stated on the asset page.
```

This project's own policy is stricter than most licences require: no
third-party asset is ever sent to an AI service, used for training, or modified
by a generative model. See `docs/legal/AI_AND_ASSETS_POLICY.md`.

## Attribution text

The exact credit shown in-game and in `CREDITS.md`:

```
Generic Items by Kenney (kenney.nl) — CC0
```

## Notes

160 item sprites. Used for inventory icons, clue-journal placeholders and small
UI affordances only. Every kept icon gets the same deterministic archival
treatment (see tools/s32tools/assets/process.py) so the set reads as one visual
language rather than as a borrowed pack.

CC0 permits committing these, but they are still fetched at bootstrap rather
than vendored: keeping ONE rule for all third-party binaries ("they are not in
the repo") is less error-prone than a per-pack exception. See ADR-0003.

---

*Generated 2026-08-30. If the terms on the source page have changed since
2026-08-30, this file records what they were, not what they are — re-read
them and add a new dated section rather than editing this one.*
