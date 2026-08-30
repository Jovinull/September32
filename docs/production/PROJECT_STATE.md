# Project state

**Read this before starting work.** Last updated: 2026-08-30.

## Summary

Milestone 1 complete. Fifteen storylets, an archive document viewer, and three
characters who now have written voices. Every quality gate is green.

The milestone was a content proof, not an infrastructure one, and it answered
its question: the architecture supports varied hand-written content, and the
thing holding the game back is no longer the engine. It is that half the map has
nothing authored in it at any hour. See
[`MILESTONE_1_PACING.md`](MILESTONE_1_PACING.md).

## Engine

| | |
| --- | --- |
| Ren'Py | **8.5.3** (stable, verified on renpy.org 2026-08-30) |
| SDK location | `.tools/renpy/renpy-8.5.3-sdk` (gitignored) |
| SDK SHA-256 | `ff57648f9c04f27e381c48af6d8e3ee3cdec296bed4d3831f47f09b0a71b505e` |
| Resolution | 1920 × 1080 |
| Python (tooling) | 3.12 via uv |

## What works

**Narrative engine** — `game/python-packages/s32_engine/`, standard library only,
importable by both Ren'Py and the headless tooling.

- Storylet director: eligibility, priority tiers, weighted selection, cooldowns,
  repeat damping, and a full explanation trace.
- Eight-axis directed relationships, including NPC-to-NPC.
- Five-stance knowledge model with per-agent beliefs and contradiction detection.
- Commitments: made, kept, broken, excused, expired.
- Player traits, accumulated rather than chosen.
- World state: day, calendar day, time slots, weather (Markov chain), phase.
- Rollback-safe containers and counter-based deterministic RNG.
- Save migration and cross-run `persistent` meta scaffolding.

**Tooling** — `s32` CLI: `doctor`, `validate`, `schemas`, `simulate`,
`coverage`, `graph`, `explain`, `report`, `assets *`, `renpy *`.

**Assets** — 11 packs fetched from official sources, hashed, licence evidence
recorded, processed and installed. 968 files in the game tree.

**The slice** — arrival, first shift in the archive, director-driven storylets,
a photograph, a promise, an ending note. Marked PROTOTYPE / NON-FINAL in-game.

## Verified, with numbers

| Gate | Result |
| --- | --- |
| `uv run pytest` | **175 passed** |
| `uv run ruff check .` | **clean** |
| `uv run ruff format --check .` | **clean** |
| `uv run mypy` | **clean, 66 files, strict** |
| `s32 validate` | **0 errors, 0 warnings**, 9 info |
| `s32 renpy lint` | **clean** |
| `s32 renpy test` | **11/11 testcases passed** |
| `s32 simulate --runs 5000` | **15/15 storylets reachable, 0 dead ends** |
| `s32 doctor` | **0 failures, 0 warnings** |

## Content

| | |
| --- | --- |
| Storylets | 15 (all `prototype`) |
| Anchors | 3 |
| Characters | 6 (5 with art) |
| Locations | 8 |
| Knowledge facts | 9 |
| Documents | 3 |
| Items | 3 |

Unique scenes in an average run: **13.6**, up from 5.9. June, Mara and Noah
appear in 100%, 94% and 100% of runs respectively, having previously appeared in
none.

## Known gaps

**Content density, which is now the main constraint.** Fifteen storylets is
still not a game, but the shape of the shortfall has changed and is worth being
precise about. Of the 56 (location, time slot) cells, **half are empty** and a
quarter hold exactly one storylet. `school_gate` has nothing authored at any
hour of any day. In **92.7%** of moments the director has exactly one eligible
candidate, so it is not selecting; it is reporting. Everything downstream --
repetition, content mix, the inert player profiles -- follows from that one
number. [`MILESTONE_1_PACING.md`](MILESTONE_1_PACING.md).

**Art.** Three characters have no casual outfit; one has no sprite; there is no
male-presenting sprite in a compatible style; the archive room is played by a
club room; the class photograph does not exist. See `ART_GAP_ANALYSIS.md`.

**Audio.** Five tracks. Nothing for investigation, romance, or the later phases.
No sound effects.

**UI.** Kenney scaffolding. The archive document viewer is **built** — three
documents, real text on deterministic generated paper, keyboard paging, effects
applied exactly once and unwound by rollback. The calendar is still unbuilt.

**Assets are not versioned, by design (ADR-0003).** A clone is 2.7 MB and has
none of them; the same checkout on a working machine is around 1.1 GB. The game
lints, tests and runs in the empty state, showing labelled `MISSING ASSET`
placeholders, and `s32 assets fetch && s32 assets install` reconstructs
everything from official sources against the recorded hashes.

**Canon.** Deliberately open. The nature of September 32 is undecided, and
`PHENOMENON_RULES.md` exists so that writing can proceed without it.

**The content mix did not resolve at fifteen, and the reason is now understood.**
It was re-checked rather than assumed, which was the point. `slice_of_life` is
94.3%, up from 90.4%. The single most played scene fell from 71.7% to 42.1% of
everything played, but repeats per run *rose* from 15.0 to 21.5: adding a second
ambient repeatable added capacity beside the first rather than diluting it. A
run offers 98 slots against about a dozen once-only scenes, so whatever repeats
absorbs the remainder.

**No repeat, cooldown or weight value was changed.** Suppressing
`courtyard_small_talk` would yield an empty slot rather than a different scene,
because 92.7% of the time it is the only thing eligible. The fix is authored
content in the empty cells, and it belongs to the next milestone.

**One knowledge fact is never acquired by the player**, correctly:
`theo_checks_the_ledger` is NPC-side only by design, and a test now holds it
that way. The two that were waiting for content
(`mara_knows_the_older_story`, `photo_is_a_forgery`) are both in play --
the first in 94.2% of runs, the second offered as a *suspicion* by Mara and
never as a fact, which is also asserted by a test.

**`purp` is resolved.** It maps to `gloom`. It was settled by measuring the
files locally -- it edits the same facial region as the other expressions, but
in violet (268-279 deg) rather than skin tones (7-31 deg) -- not by looking at
the artwork, which [ADR-0003](../decisions/ADR-0003-asset-licensing.md) forbids.
Evidence in [`ASSET_NAMING.md`](ASSET_NAMING.md). A human should still confirm
the word choice before a scene depends on the gloom/sad distinction:
[`HUMAN_ART_REVIEW.md`](HUMAN_ART_REVIEW.md).

**The player profiles are inert.** All six produce byte-identical runs.
`_apply_profile` only re-picks within the top priority tier, and every storylet
carries a distinct integer priority, so that tier holds one storylet in 100% of
selections and the scoring code never executes. Recorded rather than fixed:
with one eligible candidate in 92.7% of moments there is nothing for a profile
to express a preference over, so changing the tier logic now would prove
nothing. Any past claim of "swept six kinds of player" should be read as one
player, six times.

## Blocked

Nothing is blocked. Every download succeeded, including the ones that initially
looked blocked — two itch.io packs returned 404s that turned out to be rate
limiting, and one returned a corrupted URL because a percent-encoded `/` was
being decoded.

## Bugs found during the bootstrap

Recorded because they are the strongest evidence that the tooling earns its keep:

1. **Rollback silently did nothing.** Run state was built from plain dicts, which
   Ren'Py saves and loads perfectly and does not revert. Found by a testcase
   asserting on state rather than on text. Fixed with the container seam
   (ADR-0007) and now guarded by a test that walks the whole state tree.
2. **A scene gated on rain, in a world with no weather.** Found by the simulator.
   Fixed by building a weather model, and by teaching the static analyser to
   check weather requirements.
3. **A threshold nothing could reach.** `iris.trust >= 12` when the content could
   produce at most 10, because the trust came from choices inside prose the tools
   could not see. Fixed by declared `outcomes` (ADR-0006) and by tightening the
   static analyser's relationship ceiling.
4. **81% of simulated runs dead-ended.** The model of a player wandered at
   random. Fixed by modelling what a player actually does — go where something is
   happening — which turned out to be a real design requirement, not a
   simulation artefact.
5. **An anchor's knowledge grant living only in prose.** `the_date` granted
   `photo_dated_sept_32` inside its `.rpy` label, so a 5000-run sweep reported
   the fact as never acquired. The same class of problem as (3), arriving by a
   different route. Fixed by declaring it as an effect, where both the analyser
   and the simulator can see it.
6. **A fresh clone failed `renpy lint` with 311 errors.** The claim that the
   game works without assets was true at runtime and false everywhere else:
   generated image definitions named files directly, music was played by path,
   and three screens named font files, so a checkout with no assets — which is
   what CI runs, and what every new contributor starts from — could not lint and
   lost three testcases. Found by actually cloning the repository and running
   the gates in it. Fixed with `s32_sprite` / `s32_bg` / `s32_music` / `s32_font`
   helpers that fall back to a labelled placeholder, and `s32 doctor` now
   reports how many placeholders a build would ship.

## Bugs found during Milestone 1

Same reason as above: they are the evidence the tooling earns its keep.

7. **A scene became unreachable because other scenes were added.**
   `rain_after_school` needed `iris.trust >= 12` against a reachable ceiling of
   exactly 10, and the eight new scenes gave the player model somewhere else to
   be in the evening. Baseline data showed it was already marginal at 2.18%, so
   this was an existing fault surfacing rather than a regression. Fixed by
   raising the ceiling to 14 through a declared outcome, lowering the threshold
   to 7, and widening it to the afternoon -- which the title supported anyway.
   Now reached in 23.7% of runs.
8. **Two generated paper textures were byte-identical.**
   `Image.composite` with a mask averaging 128 blends two colours evenly at
   every pixel, producing a flat fill. Caught by the determinism check hashing
   two supposedly different tiles to the same value.
9. **Documents were refused inside the scene that unlocked them.** The director
   applies a storylet's declared effects *after* its label returns, so a
   document gated on `has_item(old_photo)` could not be opened in the scene
   where the player picks the photograph up. Fixed by making the precondition
   true inline where the prose says it is true; the declared effects still run
   afterwards and the tooling's view is unchanged.
10. **Noah referred back to something the player might never have heard.**
    His scene gates only on `noah_is_writing_about_the_archive`, but a line
    called back to "the second gap about a year long" -- and about a third of
    runs arrive without having met either June's booklet or Mara's road walk.
    Found by reading the prose against the requirements rather than by a tool.
    Guarded, and now held by a test.
11. **The same discovery happened twice.** `dorm_message` is repeatable and two
    of its branches both described noticing the courtyard bench in the
    photograph for the first time. Each visit now observes something different.

## Next milestone

**Fill the empty cells, then decide about priority banding.**

The architecture question is answered and the writing works. The next milestone
is not a systems milestone either:

1. Author for the empty (location, time slot) cells rather than for the library
   as a whole. `school_gate` at any hour; `hallway_east` outside the morning;
   `courtyard` outside the afternoon.
2. Target **three or more** eligible candidates in the common cells. That is the
   threshold at which the director starts making decisions and below which no
   amount of tuning matters.
3. Then, and only then, revisit whether priority should band into tiers rather
   than be a unique integer per storylet
   ([ADR-0002](../decisions/ADR-0002-storylet-architecture.md)). That decision
   needs content dense enough to test it, and it is the thing standing between
   the player profiles and doing anything at all.
4. The calendar interface.
5. The items in [`HUMAN_ART_REVIEW.md`](HUMAN_ART_REVIEW.md), which need a
   person and about ten minutes.
