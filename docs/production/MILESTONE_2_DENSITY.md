# Milestone 2: narrative density and player agency

**Verdict: PASS WITH CONCERNS.**

Every gate is green, every storylet is reachable, the profiles diverge, and one
declared target was missed and is reported as missed rather than tuned into
range.

Companion to the generated `tools/reports/m2/simulation.md` and
`tools/reports/m2/density.md`, which hold the raw numbers. All figures below:
5000 runs, seed 1234, 14 in-fiction days.

## The question

Milestone 1 ended with a `NarrativeDirector` that worked and never chose
anything. In 92.7% of moments it had exactly one eligible storylet, and the top
priority tier held exactly one candidate in **100.0%** of selections. Three
mechanisms — `weight`, repeat damping, and the nine player profiles — were
therefore inert, not because they were wrong but because nothing was ever asked
of them.

The brief was explicit that this was to be fixed from the content side first and
the algorithm side only if the data still demanded it after. It did not.
**`NarrativeDirector` is byte-identical to how Milestone 1 left it.**

## Headline numbers

| | M1 (15 storylets) | after reband | **M2 (30)** | target |
| --- | ---: | ---: | ---: | ---: |
| Nothing eligible | 64.5% | 64.6% | **32.5%** | — |
| Exactly one eligible, of productive moments | 93.2% | 93.2% | **57.9%** | ≤60% ✅ |
| Top tier held 2+ | 0.0% | 0.1% | **18.1%** | ≥30% ❌ |
| Storylets reachable | 15/15 | 15/15 | **30/30** | 100% ✅ |
| Dead ends | 0 | 0 | **0** | 0 ✅ |
| Share taken by the most played scene | 42.1% | — | **19.1%** | — |
| Profiles producing identical runs | 6 of 6 | — | **0 of 9** | 0 ✅ |

## TARGET MISSED: contested tiers at 18.1%, against 30%

Stated plainly because the brief asked for it to be stated plainly rather than
engineered away.

The top priority tier cannot hold two storylets unless two are eligible at that
moment. Two or more are eligible in **28.5%** of moments. So 30% was never
reachable with this library — the ceiling is 28.5, and 18.1 of it was achieved.

Read as a fraction of what was available, the bands are keeping **64%** of the
contests the content offers. The rest are lost to a legitimate rank: an `EVENT`
beating an `AMBIENT` at midday is the band system working, not a failure.

Three things were considered and not done:

- **Flattening the bands further**, so `AMBIENT` shares a tier with `EVENT`.
  This would raise the number and make the game worse; texture that can beat a
  character scene is not texture.
- **Weight tricks** — nudging an ambient scene down to 0.05 so it is eligible but
  never drawn. The brief forbade it and it is dishonest anyway: an eligible
  scene that never plays is a scene with a missing requirement.
- **Turning priority into a soft additive score.** Explicitly out of scope, and
  the reband result argues it was never the problem.

The honest fix is more scenes eligible at the same moment, which is content
volume, which is the next milestone's decision to make.

## What the reband proved, and why it was worth doing alone

Rebanding all fifteen Milestone 1 storylets to five values, **before** any new
content, moved contested tiers from 0.0% to **0.1%**.

That number is the most useful thing this milestone produced. It separates two
problems that had been receiving one answer. Collapsing fifteen ranks into five
bands cannot create a contest between scenes that are never eligible at the same
moment; the tier was a singleton because the *library* was, not only because the
priorities were. Had the content and the reband landed together, the reband
would have taken credit for the content's result.

The five bands, the audit that produced them, and ten real contested selections
are in [`PRIORITY_AUTHORING.md`](../narrative-design/PRIORITY_AUTHORING.md). No
requirement, blocker, effect, outcome or line of prose changed in the reband.

## The fifteen new storylets

Aimed at cells, not spread across the map. The reasoning and the cell
classification are in [`CELL_MAP.md`](../narrative-design/CELL_MAP.md); the
scene cards are in
[`scene-cards/MILESTONE_2.md`](../narrative-design/scene-cards/MILESTONE_2.md).

| Location | Added | Why |
| --- | --- | --- |
| `school_gate` | `gate_early_arrival`, `gate_noticeboard`, `gate_waiting` | It had **nothing at any hour**, in a game set at a school. |
| `courtyard` | `courtyard_morning_queue`, `courtyard_lunch_table`, `iris_outside` | The busiest place in the game, served by one ambient scene taking 42% of all plays. |
| `hallway_east` | `hallway_lost_property`, `hallway_after_bell` | 45,280 afternoon moments with nothing authored at that hour. |
| `dorm_room` | `dorm_late_night`, `dorm_corridor_noise` | Very high traffic at night; one scene. |
| `town_road` | `town_road_shops`, `town_road_last_bus` | Two scenes across two hours. |
| `classroom_2b` | `classroom_before_bell` | Early morning was empty. |
| `archive_room` | `archive_iris_index`, `archive_theo_returns` | A reason to be in the room that is not the plot. |

Against the brief's counting requirements:

| | required | actual |
| --- | ---: | ---: |
| Total storylets | ~30, not over 32 | **30** |
| `school_gate` storylets | ≥2 | **3** |
| Group scenes with 2+ NPCs | ~3 | **3** |
| Delayed callbacks (`CALLBACK` band) | ≥5 | **6** |
| Storylets with a real in-scene choice | ≥6 | **22** |
| …whose outcomes change later eligibility | ≥4 | **7** |
| Commitment-vs-opportunity situations | ≥2 | **2** (see below) |

The commitment count is the one to read sceptically. `dorm_message` is a genuine
fork — keep June's favour or break it, both declared. `theo_ledger_question` is
an appointment, and it sits at `URGENT`, which means it outranks the thing it is
supposed to be competing with. It counts, but it is not the interesting shape,
and a third commitment written as a real conflict would be worth more than the
two together.

New this milestone: `gate_waiting` sets `theo_lost_something`, and
`archive_theo_returns` requires it — a consequence separated from its cause by
days and by two locations, which is the pattern the architecture exists for.

## Player agency: DIVERGENT

Milestone 1 recorded all six profiles producing byte-identical runs. Over sixty
shared seeds each, nine profiles now produce:

- **60/60 distinct run signatures** for every profile
- **0 of 36** profile pairs with identical aggregate play counts

The axes separate in the directions the profiles were written to pull:

| profile | `iris.attraction` | `june.trust` | `curious` trait | `gentle` trait |
| --- | ---: | ---: | ---: | ---: |
| `romantic` | **6.9** | 13.5 | 9.8 | **15.7** |
| `altruistic` | 3.4 | **18.9** | 7.8 | 14.1 |
| `curious` | 4.4 | 7.8 | **21.2** | 8.3 |
| `selfish` | **1.4** | **2.1** | 12.0 | **3.4** |
| `paranoid` | 1.6 | 5.0 | 9.3 | 7.9 |

Reproduce with `uv run python scripts/profile_divergence.py`.

Three things had to change together, and **none of them was the director**:

1. **Priority bands**, so the tier can hold more than one scene for the profile
   to have an opinion about.
2. **`Simulator._resolve_outcome` is profile-aware.** It used to pick a declared
   outcome uniformly at random, which is right for a reachability sweep and was
   also why two players who reached the same scene always left it in the same
   state. Profiles now score branches from the declared effect strings.
   `profile.noise` keeps the uniform behaviour often enough that no branch
   became unreachable, and `random` — the control group — scores everything 1.0
   and is exactly the old code.
3. **`Profile.mobility`.** See below; this was the big one.

No profile was given a rule of the form "if curious, choose the mystery
storylet". They choose destinations and answers; those choices change state;
state changes eligibility. That indirection is the whole design and it is what
makes the divergence evidence of anything.

## The finding: the movement model was the binding constraint

Two storylets — `gate_waiting` and `archive_theo_returns` — were unreachable
after all fifteen new scenes had landed, despite being perfectly eligible and
correctly authored.

`school_gate` in the afternoon had **zero visits in 5000 runs**.

The simulated player only changed location when *nothing at all* was eligible
where they stood. The courtyard always had something ambient on offer, so a run
that arrived there never left. Location was decided by starvation and never by
preference, which also explains the Milestone 1 profile inertness more deeply
than the tier logic did: a profile that cannot choose where to be cannot express
much.

The fix is in `tools/s32tools/simulation/` and not in `s32_engine/`:
`Profile.mobility` (0.3–0.7 by profile) gives a probability of relocating after
a scene has played, and `Simulator._relocate` picks the destination by weighted
appetite over the storylets eligible there. The candidate set is still
`locations_with_content`, the same list the game offers a real player, so the
model chooses from what a player can see rather than from the library.

Result: 28/30 reachable → **30/30**, and the two scenes now fire in 67% and 58%
of runs.

## Also fixed: four storylets authored for four in the morning

`courtyard_small_talk`, `june_welcome_pack`, `old_photo_glimpse` and
`theo_ledger_question` carried no `time_slots` at all. The engine reads that as
"any hour", so the archive was offering scenes at 3am in a locked room and the
courtyard was open all night.

Found by classifying the cell map rather than by a tool. Each now names its
hours; a test rejects an unslotted storylet; the cell map records why each empty
cell is empty.

Cost, reported because it is a real regression: `theo_ledger_question` fell from
84% to **64%** of runs. It is a named-character scene and it is now absent from
a third of playthroughs. That is a content decision — the archive being shut at
night is right, so the scene wants another hour or another room — and it is on
the review list below rather than reverted.

## Continuity

The Milestone 1 bug where a repeatable scene narrated the same discovery twice
produced a written procedure rather than a habit:
[`CONTINUITY_REVIEW.md`](../narrative-design/CONTINUITY_REVIEW.md). It contains
the checklist, an audit of all thirty scenes, the four-way taxonomy of
repeatable content, and an audit of the twelve repeatable-or-cooldown scenes.

Deliberately **not** a lint. 55 lines in the current prose contain a checklist
word; twelve made a claim worth adjudicating; one was a real bug. A regex with
that hit rate would be ignored within a week.

One bug found and fixed: `hallway_after_bell` said "the second time this week
somebody has explained Mara to you using the word fine", and nothing guaranteed
a first time.

One item on watch: `gate_noticeboard` grants `bound_volumes_were_moved` behind a
menu choice on a three-day cooldown, so a player can read the discovery twice.
The prose is written as reading rather than as discovering, which holds, but it
is the thinnest case in the audit.

## What was deliberately not done

- **The `NarrativeDirector` algorithm.** Unchanged. Not "changed carefully" —
  unchanged.
- **`priority` as a soft additive score.** Out of scope by instruction, and the
  reband result argues it was never the problem.
- **Cooldown, weight and `repeat_policy` values.** None changed, in either
  milestone.
- **The calendar.** Out of scope by instruction.
- **New narrative subsystems.** None. The mobility work reuses
  `locations_with_content`, which already existed and which the game already
  exposes to the player.
- **Art.** No packs downloaded, no generative AI, nothing sent to a vision
  service, A01/A02 preserved. `purp` → `gloom` remains marked *human visual
  confirmation pending*; the measurement is strong evidence and it is not the
  same thing as somebody having looked.
- **Filling all 56 cells.** 29 are `ACTIVE`, 16 `INTENTIONALLY_EMPTY`, 6
  `FUTURE`, 5 `INVALID`. A school at four in the morning is empty, and that is
  the fiction working.

## HUMAN NARRATIVE REVIEW NEEDED

None of these can be settled by a tool, and several are judgement calls I should
not be making alone.

1. **The three group scenes.** `courtyard_lunch_table`, `hallway_after_bell`,
   `archive_theo_returns`. Two NPCs with opinions about each other, and the
   player not required to hold one. Do they sound like two people, or like one
   writer taking turns?
2. **The "say nothing" branches.** Most new scenes offer a reserved option. It
   is meant to be a real choice with its own reward, not an opt-out. Read
   `archive_theo_returns` and `courtyard_lunch_table` back to back and say
   whether the third branch earns its place.
3. **`theo_ledger_question` at 64% of runs**, down from 84%, because the archive
   now closes at night. Give it another hour, move it, or accept it.
4. **`dorm_late_night` stage three** — "the room is about eleven per cent yours
   now instead of nought". A number in narration. Voice, or cleverness?
5. **Relationship direction.** `rel X.axis` means the *player's* stance toward
   X. Several Milestone 1 outcomes read naturally as the reverse. Nothing is
   known to be wrong; the notation invites the error and there is no check.
   Worth deciding whether to require the explicit `player->x.trust` form.
6. **`courtyard_small_talk` at 13.7%** of all plays, down from 42.1%. Better,
   and still the second most played thing in the game. Is one ambient scene at
   one in seven acceptable, or does the courtyard want a fourth?
7. **`gate_noticeboard`'s repeatable discovery**, per the continuity watch item.
8. **`purp` → `gloom`**, carried from Milestone 1 and still pending a human
   glance. [`HUMAN_ART_REVIEW.md`](HUMAN_ART_REVIEW.md).

## Gates

| Gate | Result |
| --- | --- |
| `uv run s32 doctor` | 0 failures, 0 warnings |
| `uv run s32 validate` | 0 errors, 0 warnings, 9 info |
| `uv run ruff format --check .` | clean |
| `uv run ruff check .` | clean |
| `uv run mypy` | clean, 68 files, strict |
| `uv run pytest` | **194 passed** |
| `uv run s32 renpy lint` | clean |
| `uv run s32 renpy test` | 11/11 testcases |
| `uv run s32 simulate --runs 5000` | 30/30 reachable, 0 dead ends |
| `scripts/check.py` | **11/11** |

## The next milestone is not chosen here

By instruction, and because the data genuinely points three ways. The options,
with what each would cost and buy, are in
[`PROJECT_STATE.md`](PROJECT_STATE.md#next-milestone).
