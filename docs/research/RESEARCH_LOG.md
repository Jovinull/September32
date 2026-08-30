# Research log

Every non-obvious finding, with sources and a confidence marker.

| Marker | Meaning |
| --- | --- |
| `CONFIRMED` | Verified directly, at the source, on the date given. |
| `LIKELY` | Strong evidence, not directly verified. |
| `UNKNOWN` | Recorded because it matters and is not established. |

---

## 2026-08-30 — Ren'Py stable version

**Question.** Which Ren'Py release is current stable, and is 8.5.3 still it?
**Sources.** <https://www.renpy.org/latest.html>
**Finding.** 8.5.3, released 2026-05-15. SDK available as `.zip`, `.7z.exe`
(Windows), `.dmg` (macOS), `.tar.bz2` (Linux).
**Decision.** Pin 8.5.3. Use the cross-platform `.zip`: the platform-specific
packages need an external extractor, and the zip unpacks with the standard
library.
**Confidence.** `CONFIRMED`
**Recorded.** `tools/s32tools/renpy_sdk.py`, ADR-0001.

---

## 2026-08-30 — Ren'Py SDK checksum

**Question.** What does the official SDK archive hash to?
**Method.** Downloaded from `renpy.org/dl/8.5.3/`, hashed locally.
**Finding.** `ff57648f9c04f27e381c48af6d8e3ee3cdec296bed4d3831f47f09b0a71b505e`
(163,008,121 bytes).
**Decision.** Pinned. `s32 renpy install` refuses to unpack a mismatch.
**Confidence.** `CONFIRMED` — observed, not published by upstream. If upstream
ever publishes an official checksum, compare and replace this note.

---

## 2026-08-30 — Potat0Master licence terms

**Question.** What exactly do these packs permit?
**Sources.** The pack pages themselves.
**Finding, verbatim.**

> "These character sprites have a royalty free license. Meaning, you can use
> these character sprites for both personal and commercial projects, as many
> times as you want. Giving credit is not necessary but would be appreciated.
> You can edit and modify these images. However, you cannot resell or distribute
> the images in the form that it is downloaded or even when it is modified."

Background and music packs carry equivalent wording.

**Reading applied.** Use and modification in a game: permitted. Committing the
files to a public repository: distribution of those files, including modified
ones — **not** permitted.
**Decision.** No third-party binary is committed. ADR-0003.
**Confidence.** `CONFIRMED` for the text; the reading is a judgement, stated
plainly so it can be reviewed.

---

## 2026-08-30 — A02 does not contain the same free characters as A01

**Question.** The brief assumed A02 adds outfits to the same five free
characters. Does it?
**Method.** Downloaded both, parsed the filenames.
**Finding.** **No.**

| | Free characters |
| --- | --- |
| A01 | chinatsu, kanako, kohaku, tomomi, ume |
| A02 | ayumi, kohaku, mao, shiori, tomomi |

Overlap: **kohaku and tomomi only.** Ayumi, mao and shiori are paid in A01 and
free in A02; chinatsu, kanako and ume are free in A01 and absent from A02's free
tier.

**Consequence.** Only two characters can have both uniforms and casual clothes.
**Decision.** Cast kohaku and tomomi as the two most-featured characters (iris,
theo). Recorded as an art gap for the other three.
**Confidence.** `CONFIRMED` — measured from the files.

---

## 2026-08-30 — Cross-pack visual consistency

**Question.** Can secondary packs by the same artist be mixed with the core?
**Method.** Local pixel analysis; no image sent anywhere.
**Finding.** All seven secondary packs scored **3.2–5.1 / 10**. Largest
mismatches: Taishiro's head ratio 49% larger; Hiyori's line weight 156% heavier;
Kioshi & Haruo missing 8 of the core's 17 expressions.

A02 against A01: **7.4**, with deductions entirely from colour statistics
(casual clothes are more colourful than uniforms). Head ratio 0.408 vs 0.409.

**Decision.** A01 + A02 only. No secondary pack adopted.
**Confidence.** `CONFIRMED`
**Recorded.** `docs/production/CHARACTER_ASSET_AUDIT.md`, ADR-0005.

---

## 2026-08-30 — Kenney and Adobe font licences

**Question.** Are these redistributable, and under what terms?
**Sources.** kenney.nl asset pages; the Adobe font repositories' LICENSE files.
**Finding.** Kenney Generic Items and UI Pack are CC0 1.0. Source Sans 3
(3.052R) and Source Serif 4 (4.005R) are SIL OFL 1.1.
**Decision.** Both usable. The OFL requires the licence text to travel with the
font, so it is copied alongside the `.ttf` files and reproduced in
`THIRD_PARTY_NOTICES.md`. Both are still fetched rather than committed, to keep
one rule for all third-party binaries.
**Confidence.** `CONFIRMED`

---

## 2026-08-30 — itch.io public download flow

**Question.** Can free itch.io assets be fetched without an account?
**Method.** Traced what a browser does when a visitor clicks "Download Now" then
"No thanks, just take me to the downloads".
**Finding.** Three public requests: `GET /purchase` for a CSRF token,
`POST /download_url`, `POST /file/<upload_id>`. No login, no CAPTCHA, no paid
file.
**Two failures worth recording.**

1. The download token is returned percent-encoded and **must stay that way**.
   Some tokens contain an encoded `/`; decoding turns it into an extra path
   segment and a 404. This looked like a broken page for two packs.
2. Rapid requests get 429, and sometimes an unhelpful 404. Fixed with a fixed
   delay plus exponential backoff.

**Decision.** Use the public flow, identify the tool honestly rather than
impersonating a browser, and back off politely. Anything requiring a login or a
purchase emits `MANUAL DOWNLOAD REQUIRED` and the pipeline continues.
**Confidence.** `CONFIRMED`

---

## 2026-08-30 — Ren'Py rollback and non-revertable containers

**Question.** Does state built in an imported Python package roll back?
**Method.** Wrote a testcase asserting on engine state after a rollback. It
failed.
**Finding.** **No.** Ren'Py substitutes `RevertableDict`/`RevertableList` inside
its own Python blocks. A `{}` in an imported module is a plain `dict`: it saves,
it loads, and it does not roll back. Nothing raises and nothing logs.
**Decision.** A container seam (`s32_engine.containers`) that the Ren'Py bridge
repoints at the revertable types at init. ADR-0007.
**Confidence.** `CONFIRMED` — observed as a real failure, then observed fixed.
**Note.** This is the most important finding in the log. It would have shipped.

---

## 2026-08-30 — Ren'Py test statement syntax

**Question.** How are assertions written in a `testcase`?
**Method.** Read `renpy/test/testparser.py` in the SDK.
**Finding.** Conditions take an `eval <simple_expression>` form, and
`simple_expression` stops at a comparison operator. `assert x >= 1` is a parse
error; `assert eval (x >= 1)` is correct. `until` clauses accept `timeout`.
**Confidence.** `CONFIRMED` — read from the parser source.

---

## 2026-08-30 — The Ren'Py GUI template does not scale itself

**Question.** How does the 1280×720 template become 1920×1080?
**Method.** Read `game/guisupport.rpy` and `renpy/common/00gui.rpy`.
**Finding.** `gui.scale()` in the template is the **identity function** — a hook
for the launcher, not a runtime scaler. `gui.init(w, h)` only sets the screen
size. Separately, `guisupport.rpy` regenerates the GUI *images* via `gui7` when
run from the SDK, but not in a built game.
**Decision.** Scale the constants and the bitmaps once, scripted and documented,
in `tools/s32tools/renpy_gui_scale.py`.
**Confidence.** `CONFIRMED`

---

## 2026-08-30 — Public-domain status of the literature references

**Question.** Are all seven works public domain?
**Finding.** All published 1890–1927 (US public domain: pre-1930). All authors
died 1914–1951 (life+70: all expired by 2022).
**Decision.** Public domain in both. Texts **not** downloaded anyway — the
project needs analysis, not a corpus.
**Confidence.** `CONFIRMED` for the dates; the legal conclusion is a
record of a check, not advice. `docs/references/literature/PUBLIC_DOMAIN.md`.

---

## Open

**`purp`.** One Potat0Master expression token whose meaning cannot be determined
from the filename. Deliberately unmapped rather than guessed.
`UNKNOWN`. Two minutes and a human looking at a contact sheet.

**Whether AI use in development should be disclosed on a store page.**
`UNKNOWN`. The honest default is to say so.
`docs/canon/OPEN_QUESTIONS.md`.
