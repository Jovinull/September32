# Art production plan

Three milestones accepted placeholders. That was correct: the engine was the
risk, and art that arrived before the writing knew what it needed would have
been art bought twice.

**It has stopped being correct.** In Milestone 3 the absence of a sprite changed
a scene — Ms. Ellery was written off-stage, as a voice and a folder, because
standing a labelled placeholder in the room for three minutes was worse. That is
the moment an art gap becomes a writing problem, and the point at which
"`ART PENDING`" stops being a note and needs to be a plan.

This file is that plan. It does not buy anything and does not estimate a budget.
It says what exists, what it blocks, and what closing each gap would take.

Companion to [`ART_GAP_ANALYSIS.md`](ART_GAP_ANALYSIS.md), which inventories;
this prioritises.

## Priority tiers

| | |
| --- | --- |
| **P0** | Blocks the story or the final presentation. Cannot ship without it. |
| **P1** | Highly visible, recurring, and currently degrading the writing. |
| **P2** | Polish. Noticeable, not blocking. |
| **P3** | Optional. Would be nice. |

## The plan

| # | Asset | Tier | Placeholder now | Free asset? | Deterministic build? | Modification? | Route | Blocks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **The class photograph** | **P0** | `image_placeholder` block reading *CLASS PHOTOGRAPH — ART PENDING*, in a plausible archival mount | **No.** Cannot be a stock photograph of real people; cannot be generated | No | — | **COMMISSION REQUIRED** | The premise. `the_date`, `old_photo_glimpse`, `photograph_card_unlisted`, and every later act |
| 2 | **Ms. Ellery** | **P1** | None — written off-sprite | **No.** The Sensei pack scored 3.4/10 against A01 and was rejected | No | — | **COMMISSION REQUIRED** | Two scenes already written around her absence; every future faculty scene |
| 3 | **A male-presenting sprite in A01's style** | **P1** | None | **No.** Kioshi & Haruo scored 3.4/10 | No | — | **COMMISSION REQUIRED** | Casting. The cast is currently all one presentation *because of asset availability*, which is not a design decision and must not be allowed to become one by default |
| 4 | **The archive room** | **P1** | `bg_school_clubroom_c` | Partially — the club room is adequate, not right | Possibly: overlay boxes/shelving on the existing plate | Yes, if so | **EDIT, THEN REVIEW** | Nothing. It is the most-seen location in the game and looks like somewhere else |
| 5 | Casual outfits: Mara, June, Noah | P2 | School uniform in every scene | No — A02's free tier covers only Iris and Theo | No | — | COMMISSION | `mara_the_long_way`, `the_saturday`, `town_road_*` — every out-of-school scene has them in uniform |
| 6 | Iris with a camera | P2 | Neutral sprite | No | No | Prop layer on existing sprite | COMMISSION | `iris_the_wrong_photograph`, `rain_after_school` — her defining object, unshowable |
| 7 | Theo with the ledger | P2 | Neutral sprite | No | No | Prop layer | COMMISSION | Same shape as 6 |
| 8 | The town exterior | P2 | `bg_house_a` | Marginal | No | Reframe/regrade | EDIT | Mara's entire character is about this place and it has no face |
| 9 | The common room | P2 | `bg_school_clubroom_b` | **Yes, adequately** | — | — | **NONE NEEDED** | — |
| 10 | Paper, card, stamp textures | P3 | Generated | — | **Yes, already done** | — | **DONE** | — |
| 11 | Key art / title | P3 | None | No | No | — | COMMISSION, LATER | Nothing yet |

## What this milestone did about it

**Nothing was downloaded.** Zero new assets, which was the intended outcome.

**One writing decision was reversed.** Milestone 3 wrote Ms. Ellery off-sprite
because there was no sprite. Milestone 4's second Ellery scene,
`ellery_and_the_form`, is written the same way — and that is now recorded as a
**known cost** rather than as a solution. See the placeholder policy below.

**Two briefs were written**, for the two P0/P1 items where a brief is the actual
blocker rather than money:

- [`CLASS_PHOTO_ART_BRIEF.md`](CLASS_PHOTO_ART_BRIEF.md)
- [`CHARACTER_ART_BRIEF.md`](CHARACTER_ART_BRIEF.md) — covers items 2 and 3

No brief was written for P2 items. Eleven briefs nobody has commissioned is
paperwork, not planning.

## Placeholder policy

Updated in this milestone, because the old one was being violated by omission.

A placeholder must:

1. **Be visibly non-final.** The document viewer's `image_placeholder` block
   says `ART PENDING` in the middle of an empty frame. That is correct and
   should be the model.
2. **Not define appearance.** If a placeholder sprite has blonde hair, the
   character does not have blonde hair. Nothing about a placeholder enters
   canon, ever. `docs/canon/` is the only place appearance can be decided and it
   has not decided any.
3. **Not change the writing.**

**Rule 3 is the one that was being broken.** If a character is in a scene, write
them in the scene. Do not move them off-stage, do not give their line to
somebody else, and do not choose a different location because a sprite is
missing. A neutral on-stage marker with the character's name is an acceptable
development presentation; rewriting the scene is not.

The two Ellery scenes are the standing exception, and they are an exception
rather than a precedent: they were written before this policy and they work, and
they are logged here so that the next faculty scene is written properly and this
one is revisited when item 2 lands.

## Standing constraints, unchanged

- **No AI-generated art.** Not for the photograph, not for a sprite, not for a
  background, not as a placeholder. `ADR-0004`.
- **No third-party artwork sent to a vision service.** The audit tooling is
  local and deterministic for exactly this reason.
- **No mixing character packs.** `ADR-0005`. The Kioshi/Haruo and Sensei audits
  scored 3.4/10 against A01 and the finding stands: a cast visibly assembled
  from two artists reads as a cast assembled from two artists.
- **No photographs of real people**, for the class photograph or anything else.
- **No committed third-party binaries.** `ADR-0003`.

## What would change the plan

- **A compatible free pack appears.** Possible and not likely. Would need to
  clear the same audit A01 did, and the audit is deterministic and local.
- **A budget appears.** Items 1, 2 and 3 in that order. Item 1 alone unblocks
  the premise.
- **The casting question is answered deliberately.** If the project decides the
  cast is all one presentation *by design* rather than by availability, item 3
  drops to P3. That decision belongs in `OPEN_QUESTIONS.md` and has not been
  made, and it must not be made by continuing not to make it.
