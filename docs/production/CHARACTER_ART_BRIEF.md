# Commission brief — character sprites

Covers items 2 and 3 of [`ART_PRODUCTION_PLAN.md`](ART_PRODUCTION_PLAN.md):
**Ms. Ellery** (P1) and **a male-presenting student** (P1).

One brief because the hard requirement is identical for both: they must stand on
screen next to the five existing sprites and read as the same cast.

## The style match problem

The five students come from one free pack (internally `A01`). Two attempts to
extend the cast from other packs were audited and both scored **3.4/10** on
style compatibility, and were rejected — the finding was not "close enough",
it was that a cast visibly assembled from two artists reads as exactly that.
`ADR-0005`.

So the binding constraint on both items is not subject matter. It is that the
work sits beside A01 without the seam showing.

## Style match requirements — `REQUIRED`

An artist should be given the installed A01 sprites for reference. Concretely,
the match must hold on:

- **Line weight and whether lines are present at all** at the silhouette, at
  interior folds, and in hair.
- **Eye construction** — proportion, iris rendering, lash treatment. This is
  the single most visible mismatch in a side-by-side and the one both rejected
  packs failed on.
- **Shading model** — cel, soft, or hybrid; how many tones; where the
  terminator falls.
- **Head-to-body proportion**, measured against the existing five at the same
  display height.
- **Palette temperature.** The existing cast sits in a specific warm range.
- **Outfit rendering density** — fold count, seam detail, how much the uniform
  is drawn versus implied.

**The acceptance test is a side-by-side at game resolution (1920×1080, sprites
at their installed scale) with an existing character.** The project has
deterministic local tooling for this audit and will run it; it is not a
subjective sign-off.

---

## Item 2 — Ms. Ellery

### Function

The only adult in the game. Faculty, supervises the archive project in the sense
that she signs a sheet about it on Thursdays.

**Canon is explicit that she is not a conspiracy.** She is a person with a
filing system and a job, she is bothered by the institution's absurdities for
about ten minutes on Thursdays, and she is straightforwardly telling the truth
in every scene. Nothing about her design may suggest otherwise: no severity, no
watchfulness, no standing in doorways.

### Requirements

| | |
| --- | --- |
| Age range | `PREFERRED` forties to fifties. `OPEN` beyond that |
| Presentation | Female. Named "Ms. Ellery" in canon |
| Outfit | One. Professional, unremarkable, institutional-British. A cardigan is more right than a suit |
| Props | Carries a folder in both existing scenes. `PREFERRED` as a separable layer |
| Appearance beyond the above | **`OPEN`.** Hair, build, colouring, ethnicity are all undecided and this brief does not decide them |

### Expressions — `REQUIRED`

Fewer than a student needs. She has two scenes and will not have twenty.

`neutral`, `talk`, `pleasant`, `firm`.

**Not** angry, not surprised, not sad. If she ever needs one, that is a second
commission and the writing will have earned it.

### What she blocks

Two written scenes (`ellery_the_sign_off`, `ellery_and_the_form`) are currently
staged with her off-sprite — a voice and a folder — because standing a labelled
placeholder in a room for three minutes was worse. That works twice. It is a
cost, it is logged as one, and both scenes should be restaged when this lands.

---

## Item 3 — A male-presenting student

### The situation, stated plainly

The cast is currently five characters of one presentation. **That is not a
design decision.** It is what the free asset tier contained, and it has been
allowed to stand for three milestones because the alternative was mixing packs.

It is recorded as an open question in `docs/canon/OPEN_QUESTIONS.md`. The
project must either commission this or decide deliberately that the cast is what
it is — and continuing not to decide is itself a decision being made by
availability.

### Requirements

| | |
| --- | --- |
| Age range | Student, sixteen to eighteen |
| Presentation | Male |
| Outfits | `REQUIRED`: school uniform, summer and winter, matching A01's two. `PREFERRED`: one casual |
| Identity | **`OPEN`.** This brief does not say who this is. No existing character is male-presenting, and inventing one to justify the sprite is backwards |
| Layering | `REQUIRED`. Body/outfit/expression separable, matching A01's structure so the existing `s32_sprite` pipeline and expression fallbacks work unchanged |

### Expressions — `REQUIRED`

Match A01's set so the generated image definitions and fallback chain need no
special case: `neutral`, `talk`, `happy`, `smile`, `sad`, `concerned`, `angry`,
`surprised`, `embarrassed`, `smirk`, `gloom`, plus `_blush` variants of
`neutral` and `happy`.

`docs/production/ASSET_NAMING.md` has the canonical list and the mapping.

### What it blocks

Casting. There is no scene waiting on this sprite, because no scene has been
written for a character who does not exist. That is the harm: the writing has
been quietly shaped by who can appear.

---

## Deliverables — both items

| | |
| --- | --- |
| Resolution | Matching A01's native sprite height, at minimum |
| Format | PNG with alpha, plus layered source |
| Structure | One file per outfit × expression, or layered source the project can compose — either is fine, the pipeline handles both |
| Naming | The project renames on import. Do not match our conventions |

## Rights — `REQUIRED`

Commercial use, modification, and redistribution as part of a compiled game.
**Modification rights are not optional**: every sprite goes through a
deterministic local processing pass on import.

## What the project will not do

- Generate any of this. `ADR-0004`.
- Send existing third-party artwork to a vision service for style analysis. The
  compatibility audit is local, deterministic and offline, and always will be.
- Accept a near-match. Two have been rejected already and the standard has not
  moved.
