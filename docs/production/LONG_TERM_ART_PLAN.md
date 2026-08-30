# Long-term art plan

## What the current assets are for

Prototype, demo, vertical slice, early development. They are good assets, used
within their terms, and they let a game exist today that would otherwise be five
placeholder rectangles.

**They are not the finished game's art**, and the architecture is built so that
saying so costs nothing.

## Why they are not the finished art

**Coverage.** Three of five characters have no clothes but a uniform. A named
character has no sprite at all. There is no male-presenting sprite in a
compatible style. The archive room — the most-seen location — is played by a club
room.

**Identity.** These sprites appear in many other projects. That is entirely fine
for a prototype and works against a commercial release, where the visual identity
is most of what a store page communicates.

**Redistribution.** The licence permits use in a game and forbids distributing
the files. That is workable, and it means the project can never ship a mod kit,
a press pack of assets, or an art book.

## What is already decoupled

This is the part that matters, and it is done:

**Casting is one line of JSON.** `data/characters/iris.json` names an
`asset_id`; the Ren'Py image definitions are generated from it. Replacing every
sprite in the game is five edits and one command.

**Canon does not describe the placeholders.** No character bible says "pink
hair". Nothing in the writing depends on what the current sprites look like. If a
commissioned Iris looks nothing like `pm_a01_kohaku`, not a line changes.

**Presentation constants are centralised.** One transform per character,
generated. No scene contains a zoom.

**Expressions are semantic.** Scenes ask for `concerned`, not
`chinatsu_schsum_frown`. A new pack maps into the same vocabulary, and the
generator substitutes with a documented fallback where an expression is missing.

**The naming scheme records provenance.** `char_kohaku_school_summer_neutral` is
an asset name, never a canon name, and the import log resolves it back to the
artist's original filename.

## The commercial path

**Phase 1 — now.** Free assets. Build systems, write content, find out what the
game is.

**Phase 2 — vertical slice for a publisher or a crowdfund.** Commission key art
and one or two CGs. Keep the free sprites; a good title image carries a demo
further than five redrawn sprites would.

**Phase 3 — production.** Commission the cast: five to seven characters, a
consistent expression set matching `naming.CANONICAL_EXPRESSIONS`, two to three
outfits each. Specify the canvas, the baseline and the head ratio *up front*,
using the measurements in the audit — the audit is, incidentally, exactly the
document you would hand an artist.

**Phase 4 — the archive.** The documents. Photographs, ledgers, letters, the
class photograph. This is where a commission budget produces the most
distinctive result, and it is unusual for a visual novel: the documents matter
more here than the CGs.

## What must not happen

**Letting the placeholders shape the writing.** If a scene is written around what
a sprite can do, the sprite has become canon. `docs/canon/OPEN_QUESTIONS.md`
records that even the current casting is provisional and mechanical.

**Mixing commissioned and free art in the same cast.** The audit shows what that
looks like: packs by *one artist* scoring 3.2 to 5.1 against each other. A
commissioned character beside a free one would be worse.

**Generating art with a model.** Ruled out categorically —
`docs/legal/AI_AND_ASSETS_POLICY.md`.

**Shipping the free sprites in a paid release without re-reading the terms.** The
licence permits it today. Re-read it on the day, and record the date.
