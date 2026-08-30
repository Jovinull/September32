# ADR-0005 — One character system for the cast

**Status:** Accepted · 2026-08-30

## Context

Free visual-novel art is abundant and stylistically incompatible. Assembling a
cast from several artists is the fastest way to produce something that reads as
an asset dump, and it is very hard to undo once the writing depends on the cast.

The measurements are in `docs/production/CHARACTER_ASSET_AUDIT.md`, computed
locally by `s32 assets audit`. Against the chosen core, other packs by the *same*
artist score between 3.2 and 5.1 out of 10 — head-to-body proportions differing
by up to 49%, line weight by up to 156%, framing by up to 22%. Those are packs by
one person. Across artists it is worse.

## Decision

**The central cast comes from one character system.**

Chosen: Potat0Master's **Set A01** (school uniforms) plus **Set A02** (three
casual outfits). They share an identical canvas (720×1080), an identical
head-to-body ratio (0.408 vs 0.409 measured), and an identical 17-expression
vocabulary. A02 is not a different pack so much as a wardrobe for the same
characters — which is exactly what a character system means.

Two consequences follow, and both are load-bearing.

**Asset identity is separate from canon identity.** The file is
`char_kohaku_school_summer_neutral.webp`. The character is `iris`. The link
between them is one line in `data/characters/iris.json`, and the Ren'Py image
definitions are generated from it. Recasting a character is a one-line edit.

**Casting was decided on outfit availability, not appearance.** A01's free tier
and A02's free tier overlap on only two characters — `kohaku` and `tomomi` — so
those two, and only those two, have both uniforms and casual clothes. They were
assigned to the two most-featured characters. This tooling deliberately cannot
assess how a sprite *looks* (no artwork is sent to any vision service; see
ADR-0004 and the AI asset policy), so appearance-based casting is an open
question for a human: `docs/canon/OPEN_QUESTIONS.md`.

Secondary packs may be used for **background and incidental characters only**,
and only after `s32 assets audit` and a written justification.

CC0 utility art (Kenney) is used for icons and UI scaffolding, never for the
cast. Its licensing is simple, which is precisely why it is used where
consistency matters least.

## Alternatives

**Best-fitting sprite per character, across artists.** Rejected: this is the
Frankenstein outcome the audit exists to prevent, and the audit numbers say the
mismatch would be visible.

**A modifiable character template (MadameBerry, Wenqueque, both CC0).** A real
fallback, and the documented one if A01/A02 ever becomes unusable. It would be
adopted *as the system*, wholesale — not blended with half of A01.

**Commission art now.** The right answer for the commercial build and the wrong
one for a bootstrap. See `docs/production/LONG_TERM_ART_PLAN.md`.

## Consequences

**Good**

- The cast reads as one world.
- Five characters × two uniforms × 17 expressions, plus casual wardrobes for two
  of them: enough for a vertical slice without a single commission.
- Recasting, or replacing the whole system, does not touch the writing.

**Bad, and accepted**

- Only five free characters. `ellery` has no sprite and is tracked as an art gap;
  she still speaks, because an art gap must never stop a character being written.
- Three of the five have no casual outfit.
- The style is a particular one, and it is not this project's own. That is what
  `docs/production/LONG_TERM_ART_PLAN.md` is for.

## Revisit if

The project commissions a cast, or A01/A02 becomes unavailable. In either case
the replacement is adopted as a *system*, and the casting layer means the
writing does not change.
