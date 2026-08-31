# Project state

**Read this before starting work.** Last updated: 2026-08-31.

## Summary

Milestone 2 complete. Thirty storylets, priority bands, and a player model that
moves for a reason. Every quality gate is green.

Milestone 1 ended with a director that was not choosing: 92.7% of the time it
had exactly one eligible scene, and the top priority tier held one candidate in
100% of selections, so `weight`, repeat damping and the player profiles were all
mechanisms that could not act. Milestone 2 fixed that from the content side and
left the algorithm alone. The singleton rate is now **57.9%** and the top tier
holds two or more in **18.1%** of selections, up from 0.0%. All thirty storylets
are reachable and the nine profiles no longer produce identical runs.

The target for contested tiers was 30% and it was not met. That is a content
volume question -- two scenes cannot share a tier unless two are eligible, and
two are eligible in 28.5% of moments -- and it is the first thing the next
milestone should read. [`MILESTONE_2_DENSITY.md`](MILESTONE_2_DENSITY.md).

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
| `uv run pytest` | **194 passed** |
| `uv run ruff check .` | **clean** |
| `uv run ruff format --check .` | **clean** |
| `uv run mypy` | **clean, 68 files, strict** |
| `s32 validate` | **0 errors, 0 warnings**, 9 info |
| `s32 renpy lint` | **clean** |
| `s32 renpy test` | **11/11 testcases passed** |
| `s32 simulate --runs 5000` | **30/30 storylets reachable, 0 dead ends** |
| `s32 doctor` | **0 failures, 0 warnings** |

## Content

| | |
| --- | --- |
| Storylets | 30 (all `prototype`) |
| Anchors | 3 |
| Characters | 6 (5 with art) |
| Locations | 8 |
| Knowledge facts | 11 |
| Documents | 3 |
| Items | 3 |

Unique scenes in an average run: **13.6** at Milestone 1, from 5.9 at the
bootstrap. The single most played scene now takes 19.1% of everything played,
down from 42.1% and from 71.7% before that. Twenty-nine of the 56 (location,
time slot) cells are live; the rest are classified in
[`CELL_MAP.md`](../narrative-design/CELL_MAP.md) rather than treated as gaps.

## Known gaps

**Content density, still the main constraint, now for a narrower reason.**
Thirty storylets, and the director is choosing between two or more in 28.5% of
moments rather than 6.8%. But 57.9% of productive moments still offer exactly
one scene, so the intended 30% contested-tier rate was missed at 18.1%. The
remaining shortfall is arithmetic and not tuning: contests cannot exceed the
rate at which two scenes are eligible together, and the cells where that happens
are named in [`CELL_MAP.md`](../narrative-design/CELL_MAP.md). The largest
single gap is `dorm_room` in the early morning -- 34,000 visits in 5000 runs
with nothing authored, because the player wakes up there.

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

**The content mix improved without the repeat algorithm being touched.**
`courtyard_small_talk` fell from 42.1% of everything played to 13.7%, and the
new top scene, `dorm_late_night`, takes 19.1% -- a milder concentration in a
much larger library. No cooldown, weight or `repeat_policy` value was changed in
either milestone. What changed was the number of things eligible at the same
moment, which is what the damping needed in order to act.

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

**The player profiles are no longer inert.** Milestone 1 recorded that all six
produced byte-identical runs. Nine profiles now diverge on every measure: 0 of
36 profile pairs share an aggregate play count, and the axes separate in the
directions they were written to -- `romantic` reaches `iris.attraction` 6.9 per
run against `selfish`'s 1.4; `altruistic` reaches `june.trust` 18.9 against
`selfish`'s 2.1. Three things had to change together and none of them was the
director: priority bands so a tier can hold more than one scene, in-scene
choices resolved by the profile rather than uniformly at random, and a movement
model that relocates by preference rather than only when starving. Measure it
with `uv run python scripts/profile_divergence.py`.

**Relationship direction is easy to write backwards.** `rel X.axis` defaults to
`source="player"` and therefore means *the player's stance toward X*, not X's
stance toward the player. Several outcomes read naturally as the latter. Nothing
is known to be wrong today -- the Milestone 2 content was written against the
convention deliberately -- but the notation invites the mistake and there is no
check for it. Worth an explicit `player->x.trust` form, or a validator, before
the content doubles again.

**The credits gate fails every midnight.** `THIRD_PARTY_NOTICES.md` embeds its
generation date and the freshness test compares content, so the file needs
regenerating on the first run of each day. Cosmetic, recurring, and mildly
corrosive: a gate that cries wolf daily is a gate people stop reading.

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

## Bugs found during Milestone 2

12. **Two storylets were unreachable for a reason no content could show.**
    `gate_waiting` and `archive_theo_returns` never fired in 5000 runs despite
    being perfectly eligible. `school_gate` in the afternoon had **zero visits**:
    the simulated player only changed location when nothing at all was eligible
    where they stood, and the courtyard always had something ambient on offer,
    so a run never left it. Fixed in the player model, not in the director --
    profiles now relocate with probability `mobility` and choose the destination
    by appetite. Both scenes now fire in 67% and 58% of runs.
13. **Four storylets were authored for every hour of the day.**
    `courtyard_small_talk`, `june_welcome_pack`, `old_photo_glimpse` and
    `theo_ledger_question` carried no `time_slots`, which the engine reads as
    "any", so the archive was offering scenes at three in the morning in a
    locked room. Found by classifying the cell map rather than by a tool. Each
    now names its hours, and a test rejects an unslotted storylet.
14. **Every profile answered every question the same way.** `_resolve_outcome`
    picked a declared outcome uniformly at random, on the reasoning that a
    reachability sweep wants every branch taken. It does -- but it meant two
    players who reached the same scene always left it in the same state, so
    nothing downstream could diverge. Profiles now score branches from their
    declared effects, with `profile.noise` preserving the uniform behaviour
    often enough that no branch became unreachable.
15. **A callback I wrote had nothing behind it.** `hallway_after_bell` said "the
    second time this week somebody has explained Mara to you using the word
    fine"; nothing guaranteed a first time. The same class as (10), found the
    same way -- reading the prose against the requirements -- which is why it is
    now a written procedure rather than a habit:
    [`CONTINUITY_REVIEW.md`](../narrative-design/CONTINUITY_REVIEW.md).
16. **The Milestone 1 pacing report used time slots that do not exist.** Its
    location x hour matrix was built on invented `late_morning` and
    `late_afternoon` columns and omitted `midday` and `late_night`, so the cell
    counts and the "50% empty" figure derived from it were wrong. The
    conclusions drawn from it survived recomputation. Corrected in place, with
    the error recorded rather than quietly overwritten.

## Next milestone

**Not yet decided. The data is in; the decision is a person's.**

Milestone 2 was asked not to choose the next milestone before the numbers
existed. They do now, and they point three different ways:

1. **More content in the cells that are already busy.** The cheapest path, with
   a known ceiling: `dorm_room` early morning, `school_gate` evening,
   `hallway_east` afternoon, the rooftop at any hour. Would move the
   contested-tier rate directly.
2. **The calendar.** Deliberately not built this milestone. The strongest
   argument for it is that the movement model is currently the thing deciding
   where the player is, and a player who could plan a day would produce a very
   different distribution.
3. **Revisit the selection algorithm, now that there is something to test it
   against.** Milestone 2 was explicitly forbidden from turning the hard
   priority tier into a soft additive score, and the reband plus the content
   made that unnecessary rather than merely deferred. Whether it stays
   unnecessary at sixty storylets is a real question, and
   [ADR-0002](../decisions/ADR-0002-storylet-architecture.md) is where it
   belongs.

Standing, independent of that choice:

- The items in [`HUMAN_ART_REVIEW.md`](HUMAN_ART_REVIEW.md), which need a person
  and about ten minutes.
- The narrative reading list in
  [`MILESTONE_2_DENSITY.md`](MILESTONE_2_DENSITY.md), which needs a person and
  rather longer.
