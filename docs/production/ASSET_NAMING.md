# Asset naming

Third-party packs use whatever the artist preferred. The project uses one scheme.
The mapping lives in `tools/s32tools/assets/naming.py` and is applied at import.

## The scheme

```
char_<character>_<outfit>_<expression>.webp
bg_<place>_<time>[_<variant>].webp
prop_<name>.webp
ui_<name>.png
bgm_<name>.ogg
```

## The rule that makes it safe

**Names carry asset identity, never canon identity.**

The file is `char_kohaku_school_summer_neutral.webp`. The character is `iris`.
The link is one line in `data/characters/iris.json`, and the Ren'Py image
definitions are generated from it. See ADR-0005.

A file named `char_iris_...` would bake a casting decision into 425 filenames.

## Traceability

Every rename is recorded in `assets/catalog/import_log.json`, which **is**
committed even though the files are not. A project-side filename always resolves
back to the artist's original.

## Outfits

| Source | Project |
| --- | --- |
| `schsum` | `school_summer` |
| `schwin`, `schwi` | `school_winter` |
| `offtop` | `casual_offshoulder` |
| `shirttop` | `casual_shirt` |
| `whitetop` | `casual_white` |

`schwi` is a truncation in one character's files. Mapped rather than corrected,
because correcting it upstream is not ours to do.

## Expressions

Sixteen semantic names (`naming.CANONICAL_EXPRESSIONS`) that scenes may rely on.
A pack missing one gets a documented fallback (`EXPRESSION_FALLBACKS`), and the
generator reports every substitution.

| Source | Project |
| --- | --- |
| `normal` | `neutral` |
| `normalblush` | `neutral_blush` |
| `upset` | `sad` |
| `upsettalk` | `sad_talk` |
| `tears` | `crying` |
| `huh` | `surprised` |
| `frown` | `concerned` |
| `evilsmirk` | `smirk` |
| `poutangry` | `pout_angry` |
| `talk`, `happy`, `blush`, `pout`, `angry`, `angrytalk`, `disgusted` | unchanged |

### `purp`, resolved

**`purp` maps to `gloom`.** For a long time it was deliberately left unmapped:
the filename does not say what it means, and inventing a label would have put a
wrong word in front of a writer who trusts it.

It was settled by measuring the images locally rather than by looking at them.
No artwork was sent anywhere; the whole check is `PIL.ImageChops.difference`
over files already on disk.

The evidence, in the order it narrows:

1. **It is an expression, not an outfit colour.** The pack's filename grammar is
   `<character>_<outfit>_<token>`, and the token slot holds `angry`, `blush`,
   `concerned`, `crying`, `disgusted`, `happy`, `neutral`, `pout`, `sad`,
   `smirk`, `surprised`, `talk` -- and `purp`. It appears 25 times, exactly as
   often as `neutral`, across both packs and every outfit.

2. **The artist wrote it that way.** The name inside the source archive is
   already `chinatsu_schsum_purp.webp`. Our importer did not truncate anything.
   The pack abbreviates elsewhere too (`schsum`, `schwin`), and ships no
   documentation of its own -- the archives contain images and nothing else.

3. **It changes the same part of the drawing the other expressions change.**
   Comparing each variant against `neutral` and keeping only pixels differing by
   more than 90/255, the changed region is the face in every case:

   | variant | changed px | region (of 720x1080) | median hue |
   | --- | ---: | --- | ---: |
   | `happy` | 253 | x292-388, y382-512 | 8 deg |
   | `angry` | 35 | x267-400, y382-503 | 29 deg |
   | `blush` | 126 | x288-405, y382-509 | 31 deg |
   | **`purp`** | **361** | **x273-434, y366-503** | **268 deg** |

   (`char_ayumi_casual_shirt_*`; `char_kohaku_casual_shirt_*` gives 266/59/176
   px at hues 7/26/27 against `purp` at 435 px and 279 deg.)

4. **The hue is the whole point.** Every other expression edits the face in skin
   and blush tones, 7-31 degrees. `purp` edits it at 268-279 degrees -- violet --
   and reaches higher up the forehead than any of the others. That is the anime
   convention for gloom or dread: a purple shadow cast over the upper face.
   `purp` is short for purple, and it names a mood, not a colourway.

Consistent across two characters, two outfits and both packs.

The reading is strong but it has never been confirmed by human eyes, because
[ADR-0003](../decisions/ADR-0003-asset-licensing.md) forbids sending third-party
artwork to a vision service and no exception was made for convenience. A
one-line confirmation is listed in
[`HUMAN_ART_REVIEW.md`](HUMAN_ART_REVIEW.md). Until someone ticks it, treat
`gloom` as measured rather than seen, and do not write a scene that depends on
the distinction between gloom and sadness.

## Backgrounds

Pack prefixes map to place names via `naming.BG_PLACES`. The packs put their own
variant tokens after the time (`..._day_door2`, `..._night_lit`), so the image
generator files each installed file under the longest time key it matches and
takes the first candidate.

Times: `day`, `day_alt`, `evening`, `evening_alt`, `night`, `night_alt`,
`night_alt2`, `night_lit`.

## Adding a pack

1. Add the source to `sources.py`.
2. Add its prefix and place table to `naming.BG_PLACES`, or its outfit and
   expression tokens to `OUTFITS` / `EXPRESSIONS`.
3. `s32 assets install` and check the `unmapped` list — anything listed there
   needs a mapping or a deliberate decision to skip it.
4. `s32 assets images` and check the substitution report.
