# Commission brief — the class photograph

**Priority: P0.** This asset blocks the premise. Everything else in the art plan
can wait for it.

Written so that an artist can produce it without being told the plot. If you are
reading this as a commissioned artist: you do not need to know what September 32
is, and the sections marked `OPEN` are open because the project has not decided
them, not because they are being withheld.

## What it is

A class photograph from a small English residential school, of no stated year,
which has been in a cardboard box in a store cupboard for a long time.

It is not a prop in a horror game. It is a photograph that would be completely
unremarkable if it were not for one thing, and that one thing is a rubber stamp
in the corner, which is a separate layer and is not your problem unless you want
it to be.

**The single most important note in this brief:** it must look like a real
photograph of a real institution that nobody thought was interesting. Every
instinct toward atmosphere, mood, ominousness or significance is wrong. If it
looks like a clue, it has failed.

## Narrative purpose

The player finds it loose in the bottom of a box, under a bundle of sports-day
programmes. They turn it over looking for names and a year, the way you do, and
there are none, and there is a stamp.

The photograph is the thing they carry around for the rest of the game. It goes
in a drawer, comes out under a desk lamp, gets looked at again. It has to
survive being looked at repeatedly and reward it slightly.

## Composition — `REQUIRED`

- **Three rows.** Back row **standing on a bench**. This is referenced in prose
  and matters: a later scene notices that the bench is the same bench that is
  still in the courtyard.
- **Approximately forty people.** "Forty-odd" is what the prose says; the exact
  count is `OPEN` and should not be countable at a glance. If it is trivially
  countable, the number becomes a fact, and the project has deliberately avoided
  making it one.
- **Everybody squinting.** Sun behind the photographer.
- **Outdoors**, against a school building or a wall. Not a hall, not a studio.
- **Nobody looking at the camera in quite the same way** — which is true of
  every group photograph ever taken and should read as ordinary rather than as
  eerie.

## The object — `REQUIRED`

- **Gelatin silver print, mounted on card.** The catalogue card says so.
- **The mount is trimmed along one edge, by hand, not squarely.** Somebody cut
  it to fit something. This is referenced in prose twice and is the photograph's
  most distinctive physical feature.
- **A rubber stamp in one corner**, ink gone brown. Rolled cleanly by somebody
  who does it four hundred times a week — **not** smudged, not doubled, not
  ambiguous. Its legibility is the whole point.
- **No names, no year, nothing written on the reverse.**

## The stamp text — `OPEN`, and deliberately

The stamp reads a month and a number. **Do not render the number.**

Supply the stamp as a **separate layer** with the numerals omitted or on their
own sub-layer, so the project can set them without a re-commission. The prose
currently says only "the month you are currently standing in, and the number
after the month is not a number that month has", and no character reads it
aloud.

If a placeholder is needed for composition, use `SEP ██`.

## Period — `PREFERRED`, not `REQUIRED`

Mid-century, loosely. Uniforms and haircuts should be *hard to date within about
twenty years*, which is both period-appropriate for a school that changed very
little and useful to a project that has not fixed a date.

**Avoid** anything that pins a decade: no visible technology, no distinctive
silhouettes, no signage with a legible date.

The project's era, region and country are all `OPEN` in
`docs/canon/OPEN_QUESTIONS.md`. Please do not resolve them.

## What must NOT be visible — `REQUIRED`

- **Any real person.** No photographic reference of identifiable individuals, no
  stock photography, no AI generation. This is an absolute constraint and the
  reason this brief exists rather than a search.
- **Any of the five main characters.** They are alive now; this is decades old.
- **A legible date, anywhere except the stamp.**
- **Anything that reads as a clue** — no odd figure at the back, no blur, no
  person who is not quite there, no gap in the row. The photograph's strangeness
  is entirely in the stamp. Adding a second strangeness would destroy the scene.
- **Damage that implies intent.** Foxing, fading and a trimmed edge, yes.
  A torn-out face, no.

## Degradation — `REQUIRED`

Handled, filed, and not cared for. Corner wear, a fingerprint or two on the
mount, mild silvering. The image itself should be **in good condition** — this
is a well-made print that has been in a dry box, not a ruin.

The project applies its own archival treatment in software
(`tools/s32tools/assets/process.py`, deterministic, no model), so **supply it
clean**. Do not bake in ageing.

## Deliverables — `REQUIRED`

| | |
| --- | --- |
| Resolution | 3000px on the long edge minimum. It is examined in a document viewer that can zoom. |
| Format | Lossless master (PNG or TIFF), plus layered source |
| Layers | (a) photograph, (b) mount/card, (c) stamp, with numerals separable |
| Colour | Monochrome print on warm card. Not sepia-filtered colour |
| Alpha | The mount's cut edge must be a real edge, not a rectangle |

## Variants — `PREFERRED`

The reverse of the mount: blank card, mount adhesive, the same trimmed edge. The
player turns it over in two separate scenes and there is currently nothing
there.

## Rights — `REQUIRED`

Commercial use, modification, and inclusion in a distributed game. The project
cannot use anything it may not modify: the software treatment pass is not
optional.

## What the project will not ask for later

So this can be quoted once, honestly: there is no plan to commission variants of
this photograph showing different people, different years, or anything altered.
If the story ever needs a second version of this image, it will be a second
commission with its own brief.
