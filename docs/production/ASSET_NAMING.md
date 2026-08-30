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

### The unmapped one

**`purp` is deliberately not mapped.** Its meaning cannot be determined from the
filename, and inventing one would put a wrong label in front of a writer who
trusts it. It passes through unchanged.

Resolving it requires a human looking at the contact sheets. It is a two-minute
job that has not been done, and leaving it visibly unmapped is more honest than
guessing.

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
