# Project state

**Read this before starting work.** Last updated: 2026-09-01 (Milestone 5).

## Summary

Milestone 5 complete. There is a playtest build, and it can be handed to a
person with one sentence of briefing.

Preparing it turned up the largest gap five milestones of green gates had
hidden. **Act 1 was not playable.** The game's `start` label ran six time slots
on the first day and stopped with a line saying it was a prototype, so three of
the five anchors — the common room, the undated column, and the date itself —
had never once fired outside the headless simulator. Fifty-eight storylets and a
seven-day structure were reachable on paper and unreachable in the game, and
every gate was green the whole time. `game/story/act1.rpy` is the loop that
fixes it, and `act1_golden` is the first regression test in this project that
executes a scene.

The rest of the milestone is the apparatus around a private wave: a build that
carries its own content and names its own commit, a local and consented playtest
report, nineteen written hypotheses, two questionnaires, and the templates for
reading what comes back.

**No content was written.** Fifty-eight storylets before, fifty-eight after.
That was the instruction and it was the right one.

The next unknown is human, and nothing in this repository can reduce it further.

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
`coverage`, `graph`, `explain`, `report`, `assets *`, `renpy *`, `build`,
`playtest summarize`.

**Assets** — 11 packs fetched from official sources, hashed, licence evidence
recorded, processed and installed. 968 files in the game tree.

**Act 1, playable end to end** — `game/story/act1.rpy`. Anchors first, then the
director, and the player chooses where to be three times a day and whenever the
room empties. It runs until `the_date` fires, which is the end of the act and
the only ending this build has. A median playthrough is 46 scenes and 12,750
spoken words: an hour to an hour and a half. `uv run python scripts/playtime.py`.

**A playtest build** — `uv run s32 build`. Mirrors the content into the game
tree, stamps itself with its version and commit, and excludes the repository it
was built from. `docs/production/PLAYTEST_BUILD.md`.

## Verified, with numbers

| Gate | Result |
| --- | --- |
| `uv run pytest` | **343 passed** |
| `uv run ruff check .` | **clean** |
| `uv run ruff format --check .` | **clean** |
| `uv run mypy` | **clean, 79 files, strict** |
| `s32 validate` | **0 errors, 0 warnings**, 9 info |
| `s32 renpy lint` | **clean** |
| `s32 renpy test` | **20/20 testcases passed**, including a full Act 1 |
| `s32 simulate --runs 5000` | **58/58 storylets reachable, 0 dead ends, 5/5 anchors in 100% of runs** |
| `s32 doctor` | **0 failures, 0 warnings** |

## Content

| | |
| --- | --- |
| Storylets | 58 (15 `prototype`, 43 `draft`, 0 `active`) — unchanged, deliberately |
| Anchors | 5 |
| Characters | 6 (5 with art) |
| Locations | 9 |
| Knowledge facts | 14 |
| Documents | 6 |
| Items | 3 |

Unique scenes in an average run: **41.0**, from 13.6 at Milestone 1 and 5.9 at
the bootstrap. The single most played scene takes **12.7%** of everything
played, down from 19.1% and from 71.7% at the start. Thirty-seven of the 63
(location, time slot) cells are live; the rest are classified in
[`CELL_MAP.md`](../narrative-design/CELL_MAP.md) rather than treated as gaps.

## Known gaps

**Content density is no longer the binding constraint.** Fifty-eight storylets;
the director is choosing between two or more in 45.2% of moments, and the top
priority tier holds two or more in **34.9%** — the Milestone 2 target of 30%,
essentially reached, without the selection algorithm changing. Milestone 2's
largest single gap, `dorm_room` in the early morning, is filled, and filling it
was worth thirteen points on its own. What remains thin is the **rooftop**: one
weather-gated scene across two hours, and the only location in the game with a
single storylet in it.

**Art.** Three characters have no casual outfit; one has no sprite; there is no
male-presenting sprite in a compatible style; the archive room is played by a
club room; the class photograph does not exist. See `ART_GAP_ANALYSIS.md`.

**Audio.** Five tracks. Nothing for investigation, romance, or the later phases.
No sound effects.

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

**UI.** Two signature interfaces now exist and share a visual language: the
archive document viewer (six documents, two of them deliberately mundane) and
the **calendar**, which stores nothing and derives every square from
`WorldState`, commitments and history when asked. No part of the calendar parses
a date, so a September with thirty-two days in it stays representable without
the UI being rewritten.

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

**Both Milestone 2 hazards are gone, and one of them was worse than reported.**
Relationship direction is now explicit everywhere and refused when omitted; the
audit found that the implicit default had been wrong in **all 114** places the
content used it, not merely ambiguous.
[`RELATIONSHIP_DIRECTION.md`](../narrative-design/RELATIONSHIP_DIRECTION.md).
Credits generation no longer reads the wall clock, and a test rejects any clock
reintroduced into that module.

**Art is the largest risk, and it is now a plan rather than a note.**
[`ART_PRODUCTION_PLAN.md`](ART_PRODUCTION_PLAN.md) tiers eleven gaps and names
the route for each. Three are `P0`/`P1` and all three need a commission: the
class photograph (the object the premise turns on, currently an
`image_placeholder`), Ms. Ellery (written off-sprite twice now), and any
male-presenting sprite (the cast is one presentation *because of asset
availability*, which is not a design decision and must not become one by
default). Two briefs are written and are detailed enough to commission from:
[`CLASS_PHOTO_ART_BRIEF.md`](CLASS_PHOTO_ART_BRIEF.md) and
[`CHARACTER_ART_BRIEF.md`](CHARACTER_ART_BRIEF.md).

The placeholder policy gained the rule it was missing: **a missing sprite may
not change the writing.** It had been silently violated — Milestone 3 moved
Ellery off-stage because there was no sprite for her — and that is the moment an
art gap stops being a visual problem.

**Green tests are not good prose, and the distinction is now explicit.**
`uv run pytest` proves state coherence, reference integrity and reachability. It
proves nothing about dialogue, romance, humour or pacing. Nothing in the game is
marked `active`, and nothing should be until a person has read it.

**The playtest apparatus is built and unused.** A local, consented report; a
session code; nineteen written hypotheses; two questionnaires; a scene review
guide; and the templates for reading a wave. `docs/playtest/`. Nothing has been
sent to anybody and no tester has been approached — §66 of the brief says
prepare, not recruit.

**Nothing in the recorder reaches the network, and that is now checked across
the whole game tree** rather than only the engine package.
`tests/test_playtest_privacy.py`. `docs/legal/PRIVACY.md` has been rewritten to
say, in specifics, what a consenting tester's report contains — which is what
that document's own "if this ever changes" section demanded.

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

## Bugs found during Milestone 3

Classified, because the classes are starting to be informative.

17. **`AUTHORING` — every relationship in the game was on the wrong edge.**
    `rel iris.trust += 3` defaulted its source to the player and therefore
    stored *the player's* trust toward Iris. All 114 authored uses meant the
    reverse. Undetectable by construction: the only two conditions that read a
    relationship read the same wrong edge, so the game behaved exactly as
    intended, every test passed, and the debug screen showed a number going up
    beside the right name. Found by asking, scene by scene, what the number was
    supposed to mean.
18. **`TOOLING` — the credits gate failed every midnight.**
    `THIRD_PARTY_NOTICES.md` embedded `datetime.now()` and the gate compares
    file contents. Now derived from the committed manifest's newest
    `license_verified` date, which is both reproducible and the more useful
    fact.
19. **`TOOLING` — the Ren'Py testcase list was hand-written in `cli.py`.**
    A new testcase file ran in nobody's build until somebody remembered to add
    it. Found by adding one: five calendar testcases passed silently by never
    running. Discovery now walks `game/testcases/`.
20. **`DATA` — a scene walked the player backwards from `known` to
    `suspected`.** `old_photo_glimpse` suspects the date on the stamp, which is
    right the first time and wrong after the `the_date` anchor has established
    it. About one run in six ended the week having *unlearned* the fact the act
    is built on. `known -> suspected` is a legal and deliberate transition; the
    fix was a blocker on the scene, not a change to the knowledge model.
21. **`CONTINUITY` — two callbacks I wrote had nothing behind them.**
    `iris_the_second_box` opened on "not where it was and not how it was" while
    gated only on *knowing about* the second shoebox, and `june_reads_it_flat`
    closed on a callback to one variant of a scene the player may never have
    played. Both found by the written checklist rather than by a tool, which is
    the third milestone running in which that checklist has earned its place.
22. **`TOOLING` — the divergence script was reading the empty edge.**
    `scripts/profile_divergence.py` printed a table of zeros for every
    relationship axis after the direction fix, because its axis list still said
    `player->iris`. A report that shows zeros where there is data is worse than
    no report.

## Bugs found during Milestone 5

The most expensive one this project has had, and it was found by trying to give
the game to somebody rather than by any tool.

23. **`REACH` — Act 1 was not playable.** The game's `start` label called two
    anchors, ran six time slots, and stopped on a line saying it was a
    prototype. The other three anchors — the common room, the undated column,
    and the date the whole act is named for — had never fired outside the
    headless simulator. Fifty-eight storylets and a seven-day structure were
    reachable on paper and unreachable in the game.

    Every gate was green throughout, and each of them was answering a question
    that was not this one. `s32 validate` reads storylet metadata. `renpy lint`
    reads images and labels. The simulator plays five thousand runs of the
    *definitions* and never opens a `.rpy`. The testcases played the first two
    scenes. Nothing anywhere asked whether the game reaches its own ending.

    Fixed by `game/story/act1.rpy`, and held by `act1_golden`, which plays a
    full week in Ren'Py in about thirteen seconds.

24. **`TOOLING` — the golden path stalled at the first junction.** The travel
    menu called `renpy.display_menu` directly rather than going through the
    store's `menu`, so the harness that answers menus never saw it. The test
    did not fail: it ran for ten minutes and timed out, which is the sort of
    thing a test that never finishes does not tell you. Fixed with a seam,
    `s32_ask_where`.

25. **`DATA` — the report undercounted promises.** `s32_pt_commitment` was
    hooked to the `promise()` verb, and there are two ways to make a promise:
    a storylet's declared `commit(...)` effect goes through the effects engine
    instead. The golden path duly produced a run with a commitment in its state
    and none in its report. Now read from `S32State["commitments"]`, which is
    authoritative for every path.

26. **`DESIGN` — every installation would have played the same week.** The run
    seed was derived from the number of runs played, so every tester's first
    playthrough was seed 17. Their choices would still have diverged, but the
    random contribution to divergence would have been exactly zero across the
    whole wave — and H06 is the hypothesis that measures divergence. Now
    derived from a per-installation number generated once; the seed is recorded
    in the report, so a bug is still reproducible exactly.

27. **`DOCS` — the privacy policy had become untrue.** `PRIVACY.md` said
    "nothing observes a real session", which stopped being true the moment a
    consented report existed. Its own "if this ever changes" section prescribes
    rewriting the document first, in specifics, before any code — which is what
    was done, a little late.

## Next milestone

**None. Deliberately.**

No content milestone should be defined before real human feedback exists. The
next step is chosen from questionnaires, playtest reports, bug reports and a
person's reading of them — and choosing it now would defeat the point of
collecting them.

Candidate directions, none preferred: a character rewrite, choice and callback
revision, mystery pacing, a Day 7 rewrite, UI revision, escalating the art
priority, Act 2 planning, or a second wave asked a sharper question.

What happens next is a wave. `docs/playtest/WAVE_1_PLAN.md`: five to eight
people, two to three regular visual-novel readers, two to three casual ones, one
or two technical testers. No recruitment has happened and none should happen
automatically.

The decision rules that must not be reinvented after the results arrive:

- **`noah_takes_a_call`.** If most testers who saw it name it as their reason
  for suspecting Noah, cut it. Do not soften it — softening produces a different
  scene and destroys the comparison. Written down in
  `docs/playtest/SCENE_REVIEW_GUIDE.md` §12 before any tester saw it.
- **The class photograph.** A clear majority saying the placeholder blunted the
  ending moves `P0` to the front of the commission queue. Anything less does
  not.
- **Ms. Ellery's sprite.** Whether her absence reads as a stylistic choice or as
  a gap decides whether the character-art brief is `P1` or `P0`.

Explicitly **not** recommended:

- **Scaling to 80–100 storylets.** Five milestones have improved the numbers.
  None has confirmed that anybody enjoys reading the result.
- **Touching the selection algorithm.** Unchanged since Milestone 1, under five
  milestones of pressure. [ADR-0002](../decisions/ADR-0002-storylet-architecture.md)
  is where that decision lives if it ever does.
- **Polishing what is being tested.** `noah_takes_a_call`, the jokes, and the
  romance are all uncertain on purpose. Rewriting them before the wave would
  replace the evidence with a guess.

Standing, and still unread by a person:

- The thirteen scenes in [`HUMAN_ACT1_REVIEW.md`](HUMAN_ACT1_REVIEW.md), about
  forty minutes.
- The items in [`HUMAN_ART_REVIEW.md`](HUMAN_ART_REVIEW.md), ten minutes.
- The rooftop, still the only location in the game with one storylet in it.
