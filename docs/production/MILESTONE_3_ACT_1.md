# Milestone 3 — Act 1 foundation, and the calendar

**Verdict: PASS WITH CONCERNS.**

Both preflight hazards are fixed, and one of them was materially worse than
Milestone 2 reported. The first week exists, has a shape, and produces
recognisably different weeks for different players. The calendar is built and
stores nothing. Every gate is green.

The concerns are about the writing, not the machinery: this is a first draft of
a first week, and the cast is likeable without yet having cost the player
anything.

All figures: 5000 runs, seed 1234, unless stated.

---

## Preflight fixes

### Relationship direction — the default was wrong, not merely ambiguous

Milestone 2 recorded this as an ergonomics risk: `rel X.axis` defaulted its
source to the player, which "invites the mistake". The audit found the mistake
had already been made everywhere.

**Before**

```json
"rel iris.trust += 4"        after the player answers Iris kindly
"rel mara.suspicion += 3"    after the player presses Mara
"rel theo.respect -= 1"      after the player takes Iris's side
```

All three stored the *player's* stance toward the character. All three meant the
reverse. **114 of 114** authored relationship expressions meant the reverse.

**Why nothing caught it.** Exactly two conditions in the game read a
relationship, and both read the same wrong edge:

| Where | Was | Meant | Should have meant |
| --- | --- | --- | --- |
| `rain_after_school` requirement | `rel iris.trust >= 7` | the player trusts Iris | Iris trusts the player enough to confide — the scene is her asking *"Can I tell you something that makes me sound strange?"* |
| `hallway_encounter` blocker | `rel theo.resentment >= 40` | the player resents Theo | Theo resents the player enough not to stop and talk |

Because the writes and the reads were wrong *together*, the game behaved as
intended, every test passed, the simulator reported healthy relationship ranges,
and the debug screen showed a number rising beside the right character's name.
There was no observation available that could distinguish the two worlds.

`hallway_encounter`'s blocker is the sharper case: nothing in the game ever
raised `player->theo.resentment`, so it could never fire. Under the direction it
*means*, it is a hook waiting for content. Under the direction it had, it was a
dead clause pointing the wrong way.

**After**

| Layer | Before | After |
| --- | --- | --- |
| Conditions | `rel iris.trust >= 5` | `rel iris->player.trust >= 5` |
| Effects | `rel iris.trust += 3` | `rel iris->player.trust += 3` |
| Ren'Py helper | `rel("iris", "trust", 3)` | `rel("iris->player", "trust", 3)` |
| Ren'Py, NPC pair | `rel("june", "suspicion", 2, source="mara")` | `rel("mara->june", "suspicion", 2)` |
| Python API | `get(state, "iris", "trust")` | `get(state, "iris", "player", "trust")` |
| Debug screen | `player -> them` | both edges, always, including the empty one |

The grammars **refuse** the old form rather than accepting it, and the refusal
names both replacements:

```
ambiguous relationship direction in 'rel iris.trust':
write 'rel player->iris.trust' for the player's stance toward iris,
or 'rel iris->player.trust' for theirs toward the player
```

The internal representation did not change — `state["relationships"]` was
already keyed `"source->target"` — which is why this was an authoring fix rather
than an engine one, exactly as the brief required.

**Migration.** Save schema **v3**. A v2 save has the whole cast's feelings about
the player filed under `player->them`, so `migrate_state` flips those edges,
merging per axis so that a state's pre-seeded zeros cannot overwrite the values
being repaired. NPC-to-NPC edges always required the arrow and are untouched.

**Tests.** `tests/test_relationship_direction.py`, 13 cases: both grammars refuse
the bare form and name both directions; the two edges are independent; the trace
prints the direction; every authored expression names real agents in a real
direction; the Ren'Py helper and the JSON grammar use the same notation; the v2
save is repaired; a current save is left alone.

Full write-up:
[`RELATIONSHIP_DIRECTION.md`](../narrative-design/RELATIONSHIP_DIRECTION.md).

### Credits determinism

**Root cause.** `notices_markdown()` wrote
`f"Generated {datetime.now(UTC).date().isoformat()}"` into
`THIRD_PARTY_NOTICES.md`, and the freshness gate compares file *contents*. Any
build run on a later day than the last regeneration reported the notices stale
on a catalogue nobody had touched.

**Fix.** The line now reads
`Generated from assets/catalog/assets.toml. Licence terms last read by a person
on 2026-08-30.` — the newest `license_verified` date in the committed manifest.
It is reproducible, and it is the more useful fact: "when a script ran" says
nothing about a legal notice, while `license_verified` is the day a human read
the terms.

**Regression test.** `test_credit_generation_does_not_depend_on_todays_date`
renders every output twice and asserts equality, then parses the generator's
source and fails on any import of `datetime`, `date`, `time` or `monotonic` —
because a *local* import inside a function would satisfy a namespace check and
reintroduce the bug. Verified by reintroducing the import: the test fails.

Both fixes landed in their own commits before any content changed.

---

## Act 1

Seven days as a dramatic model, not a schedule. Full outline:
[`ACT_1.md`](../narrative-design/ACT_1.md).

| Day | Beat | Anchor | Major variations |
| ---: | --- | --- | --- |
| 1 | `ARRIVAL` | `arrival`, `first_shift` | Which of Mara and Iris the player warms to first; whether they push at the archive or the people |
| 2 | `ROUTINE` | — | Where they spend the free hours: gate, courtyard, corridor, road, dorm |
| 3 | `CONNECTION` | `the_common_room` | Whether they speak, ask Theo about the spreadsheet, or stay quiet — three different opening relationships |
| 4 | `INCONSISTENCY` | `the_undated_column` → **phase `odd`** | Whether Theo showed them the page first, and whether they ask which day it was |
| 5 | `DOUBT` | — | `june_reads_it_flat`: agree with June, press her, or let it go. Also `annexe_door`, `courtyard_the_bench` |
| 6 | `CONSEQUENCE` | — | `the_saturday` — keep the promise or go to the annexe. `theo_admits_it`, `iris_the_second_box` |
| 7 | `CONTRADICTION` | `the_date` | Whether the player already had the photograph, and which of three readings they take |

Two structural changes:

**The phase now turns on `the_undated_column`, not `the_date`.** The phase model
defines `odd` as "one thing does not fit, singular, with an ordinary
explanation". That is the ledger column exactly — somebody forgot to write the
date, which is what everyone says and probably true. A photograph stamped with a
number September does not have is a much stronger thing and was doing the weaker
job.

**`the_date` no longer advances the phase.** Act 1 ends *inside* `odd`, holding
two records and no account that covers both. `unsettling` is the second and
third thing and belongs to Act 2. The week ends with

> "This is no longer just a clerical mistake."

and not with

> "I now understand what September 32 is."

Nothing in Act 1 explains, implies or narrows any of the four hypotheses in
`SEPTEMBER_32.md`, and four questions are marked `OPEN QUESTION` in the outline
rather than answered to finish a scene.

---

## Storylets

**Before: 30. After: 51.** (Target ~50; the fifty-first was added after
measurement — see Density.)

| Group | Count |
| --- | ---: |
| World / slice-of-life | 6 |
| Character-focused | 6 |
| Group scenes | 3 |
| Relationship callbacks | 2 |
| Commitment / consequence | 2 |
| Mystery / odd | 2 |
| **Total new** | **21** |

The full index with characters, location, phase, band, repeat policy and
requirements is in
[`scene-cards/MILESTONE_3.md`](../narrative-design/scene-cards/MILESTONE_3.md).
Summarised:

| Storylet | Characters | Location | Band | Repeat | Purpose |
| --- | --- | --- | --- | --- | --- |
| `dorm_early_start` | — | `dorm_room` | AMBIENT | repeatable | Getting up. Filled the largest empty cell in the game. |
| `dorm_bathroom_queue` | — | `dorm_room` | AMBIENT | repeatable | Its competition. See Density. |
| `hallway_afternoon_drift` | — | `hallway_east` | AMBIENT | repeatable | The four minutes after the last lesson. |
| `common_room_evening` | — | `common_room` | AMBIENT | repeatable | The room when it is quiet. |
| `common_room_kettle` | — | `common_room` | AMBIENT | cooldown 2 | The room in daylight. |
| `gate_going_out` | — | `school_gate` | EVENT | cooldown 3 | The sign-out book. |
| `mara_the_long_way` | mara | `town_road` | EVENT | once | **Mara's non-mystery scene.** Moves `player->mara`. |
| `theo_the_spreadsheet` | theo | `common_room` | EVENT | once | **Theo's.** Column J, and being pleased with something small. |
| `june_the_kitchen` | june | `common_room` | EVENT | once | **June's.** A birthday organised in four minutes. Moves `player->june`. |
| `noah_the_sports_report` | noah | `classroom_2b` | EVENT | once | **Noah's.** 200 words, done properly. |
| `iris_the_apology` | iris | `archive_room` | EVENT | once | **Iris's.** She takes a paperweight out of your hands. |
| `ellery_the_sign_off` | ellery | `archive_room` | EVENT | once | Ms. Ellery's first appearance in the project. |
| `common_room_three_way` | june, mara, theo | `common_room` | EVENT | once | Group. The rota, which is not about the rota. |
| `annexe_two_of_them` | iris, noah | `hallway_east` | EVENT | once | Group. Print it or don't. The sharpest fork. |
| `courtyard_the_bench` | mara, noah | `courtyard` | EVENT | once | Group. Who gets to write about a place. |
| `iris_the_second_box` | iris | `archive_room` | CALLBACK | once | She started the second shoebox. |
| `theo_admits_it` | theo | `common_room` | CALLBACK | once | He was wrong about something small. |
| `june_needs_saturday` | june | `courtyard` | EVENT | once | Makes the promise. |
| `the_saturday` | june | `school_gate` | **URGENT** | once | The promise falls due on the one morning the annexe is open. |
| `june_reads_it_flat` | june | `common_room` | CALLBACK | once | Rule R5, given a scene. `odd`+ |
| `annexe_door` | — | `hallway_east` | EVENT | once | A locked door with nothing behind it, and the scene says so. `odd`+ |

Against the brief's counts:

| | asked | actual |
| --- | ---: | ---: |
| Total storylets | ~50, ≤55 | **51** |
| New group scenes | ≥3 | **3** (7 in total) |
| New delayed callbacks | ~6 | **7** — `iris_the_second_box`, `theo_admits_it`, `the_saturday`, `june_reads_it_flat`, `annexe_door`, `courtyard_the_bench`, `noah_the_sports_report` |
| Commitment / consequence | — | **2**, and the second is a real fork |
| New documents | 2–4 | **3**, two entirely mundane |
| Characters with a non-mystery scene | all five | **all five, plus Ellery** |

---

## Character arcs

Every one of these is a *question*, not a route, and none of them is answered.
All five `core wound`s remain `IDEA` and no scene implies one.

### Iris — *what does she want somebody else to see?*

- **Wants this week:** for the second index to be looked at properly by someone
  who is not her.
- **Player can learn:** that she photographs before cataloguing; that the second
  index exists and does not match the accession record; that she has been alone
  with the job since March.
- **Must remain unknown:** why it matters to her. Her core wound. Whether she
  has ever filed something that mattered.
- **Relationships introduced:** `trust`, `attraction`, and — new — `resentment`,
  reachable by dismissing the paperweight, and `player->iris.trust`, reachable
  only by helping with the second box.

### Mara — *what is she not saying about the town?*

- **Wants:** for the town to be understood correctly by an outsider, and to not
  be asked to perform it.
- **Player can learn:** that the town's history skips a year, third-hand; that
  June arrived alone in February; that Mara has done Thursday for four years and
  nobody has thanked her.
- **Must remain unknown:** why she stays. What her family does not mention.
- **Relationships introduced:** the one scene in Act 1 that moves
  `player->mara` — the player's own view of her changing on a walk about a dog.

### Theo — *why does he need the crate to be complete?*

- **Wants:** Column J full, and to not be told he is overthinking it.
- **Player can learn:** that the brass key is the annexe key and it was signed
  out to him; that he has re-checked the crate three times; that checking is how
  he cares.
- **Must remain unknown:** what was filed wrongly, and who it cost.
- **Relationships introduced:** `dependency`, which only he has, and the only
  branch in Act 1 that *lowers* a trust axis — the player can refuse him the one
  thing his bible says he needs.

### June — *why does she need this place to be ordinary?*

- **Wants:** for the ledger to be nothing, urgently, and the urgency is not
  about the ledger.
- **Player can learn:** that she came alone in February; that she keeps a list
  of everybody's birthday; that her mother did payroll for nineteen years and
  that this is where her argument comes from.
- **Must remain unknown:** what she transferred away from.
- **Relationships introduced:** `player->june.respect`, moved by agreeing with
  her — the game's only mechanical acknowledgement that the sceptic can be right.

### Noah — *what does he think printing something would fix?*

- **Wants:** to have printed something that mattered, applied this week to a
  netball result.
- **Player can learn:** that he phones the person who will tell him they were
  bad; that he attributes rather than editorialising; that he will file a piece
  about the archive whether or not Iris agrees.
- **Must remain unknown:** why it matters that it be him.
- **Relationships introduced:** `noah->iris` and `iris->noah`, which move in
  opposite directions depending on whose side the player takes.

---

## Calendar

**Data model.** `game/python-packages/s32_engine/calendar.py`, standard library
only, ~180 lines. It owns **no state**: `DayEntry` values are derived from
`state["world"]`, `state["commitments"]` and `state["history"]` at the moment
they are asked for. There is deliberately no `calendar` key in `GameState`, and
a test asserts there never is.

**Screens.** `game/screens/calendar.rpy` — a month grid beside a day panel, on
the same paper, edge frame and typography as the archive document viewer. The
day panel sits *beside* the grid rather than over it so the month never
disappears while a day is being read.

**Controls.** Arrows move the selection a day and a week at a time and clamp at
the month boundary rather than wrapping; `Home` returns to today; `Escape` and
`Close` exit. Every mouse affordance has a keyboard equivalent. Reachable from
the game menu next to Journal and Archive.

**`WorldState` integration.** `s32_calendar_today()` returns
`S32State["world"]["calendar_day"]` and `s32_calendar_month_name()` returns
`S32State["world"]["month"]`. A testcase asserts both equalities live, and
another rolls back three times and asserts the calendar still agrees — which it
does without unwinding anything, because nothing was stored.

**Commitment integration.** Open promises appear on their due square, with the
participant named from the *commitment record* rather than from the content
library. A promise already kept or broken leaves the future, because it is part
of what happened rather than part of what is coming.

**Knowledge and privacy.** The rule is structural rather than a filter:
`month_view()` is given the run state and a title lookup, and is **never given
the content library**, so a scene the game intends for Thursday is not something
it could put on Tuesday's square even by mistake. A future square carries a
weekday and anything the protagonist promised, and nothing else. A testcase
asserts a future square with a promise on it has zero events.

**Localisation.** Month and weekday names are localisable strings resolved at
the screen layer with `__()`, never baked into an image and never translated
inside the engine — `s32_engine` is imported by the headless tooling, which has
no `_()`. Structurally ready for English and pt-BR.

**Accessibility.** Keyboard-first. State is carried by a *word* as well as a
tint — "today", "promised", a count — and every square exposes a one-line
summary as a tooltip, with the selected day's summary printed under the sheet.
No information is conveyed by colour alone.

**Impossible dates.** `calendar_day` is an `int` and `month` is a `str`. Nothing
in the module or the screen calls `datetime`, and `weekday_of()` is modular
arithmetic on an offset rather than a lookup in a real calendar. A test parses
the module's imports and fails on `datetime`, `calendar`, `time` or `zoneinfo`,
because importing one to get a weekday is the obvious helpful move and it is the
move that makes September 32 unrepresentable. **Nothing about this is visible to
the player, and must not be.** The calendar looks like a school calendar.

**Tests.** 16 Python cases (`tests/test_calendar.py`) and 5 Ren'Py testcases
(`game/testcases/calendar.rpy`).

---

## Archive Viewer

No changes to the viewer beyond one presentation branch, and three new documents.

- `maintenance_docket_boiler` — a 1987 boiler service. **Completely mundane.**
  It grants nothing, implies nothing, and is not foreshadowing. It exists
  because the player had opened three documents and two of them mattered, and a
  hit rate like that teaches the wrong lesson: that opening a document is how
  you find things.
- `student_notice_rota` — the kitchen rota off the corkboard, in four
  handwritings. The only document in the game that is not from the archive, and
  it renders on card stock rather than archive paper for that reason.
- `annexe_transfer_card` — the paperwork behind the notice in the glass case. It
  says what moved and roughly when. The field for who holds the key is blank,
  and a blank field is an absence rather than a discovery.

`DocumentType` gained three values, which is a presentation decision — the type
picks a paper stock and a layout, and nothing else.

New in-scene uses: `the_undated_column` opens `ledger_iii_page_forty` and
`the_date` opens `photograph_card_unlisted`, both with the knowledge granted
inline first, because the director does not apply an anchor's declared effects
until the label returns.

---

## Continuity

The checklist found two real faults in twenty-one new scenes, and both were
mine. Details in
[`CONTINUITY_REVIEW.md`](../narrative-design/CONTINUITY_REVIEW.md).

| Scene | Fault | Fix |
| --- | --- | --- |
| `iris_the_second_box` | "the lid off, which is not where it was and not how it was" — gated only on `knows(iris_keeps_a_second_index)`, and knowing *about* the box is not having seen it | Rewritten to claim nothing |
| `june_reads_it_flat` | "it is canals again" — a callback to one of three variants of a scene the player may never have played | Rewritten to stand alone |

46 lines in the new prose contain a checklist word; ten made a claim worth
adjudicating; eight were guaranteed or were characters counting their own lives.
Two anchors branch explicitly on `knows(...)` and `has_item(...)` because the
storylets that would otherwise guarantee their premise reach only 84% and 98% of
runs.

**The new rule this milestone produced:** *a scene's requirement is the
guarantee, not the vibe.* Both faults were the same mistake — a requirement that
sounded like it implied a memory and did not.

Beyond knowledge, the audit also covered location history, relationship
direction, commitment history, who has met whom, documents seen, and elapsed
time. Weather is referenced by exactly one scene (`rain_after_school`) and was
left alone: it is a source of variation, not a mechanic.

---

## Production status

Everything was `prototype`, which had stopped being true. `prototype` means
"written to prove the engine works"; content written or reworked to be Act 1 is
a draft of shippable writing, which is a different and more honest claim.

| Status | Storylets | Means |
| --- | ---: | --- |
| `prototype` | 15 | The bootstrap and Milestone 1 slice. Written to exercise the engine, and it shows. |
| `draft` | **36** | Act 1. Written to be read. Not finished. |
| `active` | 0 | Nothing. |
| `retired` | 0 | |

**Nothing was promoted to `active`, and nothing should have been.** 222 passing
tests say the machinery is sound. They say nothing whatsoever about the
dialogue, and a green build is not a manuscript anybody has read aloud.

The project's existing vocabulary (`prototype`/`draft`/`active`/`retired`) was
used rather than a new one. Only `retired` is excluded from selection, so the
promotion changes no behaviour — it changes what the repository claims about
itself.

---

## Density, Milestone 2 → Milestone 3

5000 runs, seed 1234, both.

| | M2 (30 storylets) | **M3 (51)** | change |
| --- | ---: | ---: | --- |
| Nothing eligible | 32.5% | **27.4%** | −5.1 |
| One eligible, of productive moments | 57.9% | **44.5%** | −13.4 |
| Two or more eligible (raw) | 30.3% | **40.5%** | +10.2 |
| Top tier held 2+ | 18.1% | **28.2%** | +10.1 |
| Contests kept, of contests available | 60% | **70%** | +10 |
| Unique scenes per run | ~19 | **38.0** | +19 |
| Scenes per run | 65.5 | **70.5** | +5.0 |
| Repeats per run | 39.0 | **32.1** | −6.9 |
| Top scene share | 19.1% | **13.1%** | −6.0 |
| Top three share | ~40% | **27.8%** | −12 |
| Reachable | 30/30 | **51/51** | — |
| Dead ends | 0 | **0** | — |

Every indicator moved the way more content should move it, and one of them —
repeats per run — moved *down* while scenes per run went up, which is the first
time in three milestones that has happened.

**Top-tier contention at 28.2% is inside the 20–30% band the brief asked for,
and no priority was flattened to get there.** The band distribution is
unchanged: 2 `URGENT`, 9 `CALLBACK`, 28 `EVENT`, 12 `AMBIENT`.

### The finding worth keeping

After the twenty planned storylets landed, contested tiers were **17.2%** —
*below* where Milestone 2 finished. The cause was one cell: the player wakes up
in the dorm every day of a fourteen-day run, exactly one scene had been written
for that hour, and it was taking 13% of everything played in the game with
nothing to compete against.

Writing a second scene for it moved contested tiers to **30.7%**.

The lesson is not "add ambient scenes". It is that **a cell with one storylet
and high traffic is worth more attention than a cell with none** — the empty
cell costs a moment, the single-occupancy cell costs a *choice*, and only the
second is invisible in a play-count table.

`dorm_late_night` now sits where `dorm_early_start` was, at 13.1% and about nine
plays per run of a three-stage progression. It is inside policy and it is the
largest single block of repeated text in the game; the residence's late nights
are the first place a Milestone 4 ambient scene should go.

---

## Profiles

Nine profiles, sixty shared seeds each. `scripts/profile_divergence.py`.

- **60/60 distinct run signatures** for every profile
- **0 of 36** profile pairs with identical aggregate play counts

Relationship axes, mean per run — and note these are `x->player` edges, which is
the direction the content actually moves:

| profile | `iris.attraction` | `iris.trust` | `theo.respect` | `june.trust` | `mara.suspicion` | `noah.respect` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `romantic` | **8.7** | **23.1** | 4.6 | 19.5 | **1.9** | 2.4 |
| `altruistic` | 2.6 | 9.6 | 6.0 | **23.4** | 3.1 | **2.2** |
| `curious` | 3.2 | 20.6 | 10.7 | 8.2 | 2.8 | 6.3 |
| `completionist` | 5.0 | 21.0 | **10.8** | 11.1 | 3.6 | 7.0 |
| `paranoid` | 2.0 | 12.0 | 8.7 | 6.1 | **4.3** | 7.0 |
| `selfish` | **1.9** | **10.6** | 9.1 | **4.9** | 2.9 | **8.4** |

Four- to five-fold separation on the axes the content is built to move.

**Knowledge divergence** (5000 runs): `attendance_sheet_anomaly`, `old_photo_exists`
and `photo_dated_sept_32` at 100% — they are the act's spine and the anchors
guarantee them. Everything else spreads: `mara_knows_the_older_story` 87%,
`noah_is_writing_about_the_archive` 86%, `school_history_skips_a_year` 77%,
`annexe_is_locked` 73%, `bound_volumes_were_moved` 67%, `caretaker_opens_at_seven`
50%, `theo_lost_the_annexe_key` 48%, `iris_keeps_a_second_index` 46%,
`june_arrived_alone` 43%.

Two facts are still never held by the player as `known`, both by design:
`theo_checks_the_ledger` is an NPC-side belief, and `photo_is_a_forgery` is only
ever offered as a *suspicion* by Mara. Both are asserted by tests. The
simulation report calls them "never acquired", which is technically true and
reads as a fault; that report line is worth rewording in Milestone 4.

---

## Representative first weeks

`uv run python scripts/first_week.py` prints three chronological weeks with the
state each scene changed. Seed 1234, seven days, `curious` / `romantic` /
`altruistic`.

| | shared |
| --- | ---: |
| Scenes every profile played | 13 |
| Scenes at least one played | 35 |
| **Shared fraction** | **37%** |

Scenes only one of them reached:

- **curious only** — `annexe_door`, `archive_intro`, `iris_outside`,
  `iris_the_apology`, `noah_asks_for_access`, `old_photo_glimpse`,
  `theo_ledger_question`
- **romantic only** — `courtyard_lunch_table`
- **altruistic only** — `hallway_after_bell`, `hallway_encounter`,
  `june_needs_saturday`, `mara_older_story`, `mara_reads_the_room`,
  `mara_the_long_way`

### Do they feel like different versions of the same story?

**Yes, and the shape is the right one.** All three arrive, take the first shift,
sit in the common room, find the column and read the stamp — the five anchors —
and all three end the week in `odd` holding two records. What differs is
everything between: `curious` spends the week in the archive and ends knowing
seven facts with `iris->player.trust` at 20; `altruistic` spends it with people,
ends with `june->player.trust` at 23 and `player->mara.trust` at 6 from a walk
about a dog, and reaches the annexe door not at all.

They are not different games. `curious` has not been given a different plot;
they have been given the same week and have spent it somewhere else. That is the
intended outcome.

**The honest caveat:** this is measured on scene identity and end state, which
is what a tool can see. Whether three people would *feel* they had different
weeks is a reading question, and it is on the list below.

---

## Pacing

### Did we preserve enough normal life?

Yes, and the mix says so: `slice_of_life` 91.9%, `school` 61.7%, `character`
35.4%, `friendship` 20.4% against `mystery` 8.1%, `investigation` 9.1% and
`archive` 8.2%. The pacing budget asks for 65/25/10 in `normal` and roughly
50/30/20 in `odd`; the game is *more* slice-of-life than the budget requires,
not less. `character` at 35.4% is up from 28.7% and is the number the milestone
was actually testing.

### Did the mystery escalate too quickly?

No, and the structure was changed to make sure. The phase now turns on the
weakest available thing — a column with no date, explained inside the same scene
by a character who is probably right — and the photograph, which is far stronger
evidence, no longer advances anything. Days 1 through 3 contain no mystery
content that is not optional. `annexe_door` and `june_reads_it_flat` are gated
to `odd` and cannot appear before day 4.

### Is the Day 7 contradiction earned?

**Qualified yes.** By day 7 the player has been in the archive at least twice,
has read the ledger page in the viewer, has had at least one character offer an
ordinary explanation, and holds `attendance_sheet_anomaly` in 100% of runs. The
photograph then contradicts nothing on its own — the scene is careful that the
stamp *alone* is a franking machine set wrong, and the contradiction is between
two documents rather than inside one.

What is not yet earned is the *weight*. The strongest version of that scene is a
player who has spent the week with Iris finding it in a room they now care
about, and about half of runs do not have that relationship. That is a depth
problem, and it is the argument for Milestone 4 being about character.

### Do the choices alter the experience without destroying coherence?

Yes on both halves. 37% shared across three profiles; five anchors at 100%; zero
dead ends across 5000 runs; every intended scene reachable.

---

## Tests

| Gate | Result |
| --- | --- |
| `uv run s32 doctor` | 0 failures, 0 warnings |
| `uv run s32 validate` | 0 errors, 0 warnings, 9 info |
| `uv run ruff format --check .` | clean |
| `uv run ruff check .` | clean |
| `uv run mypy` | clean, 71 files, strict |
| `uv run pytest` | **222 passed** |
| `uv run s32 schemas --check` | clean |
| `uv run s32 assets credits --check` | clean |
| `uv run s32 assets verify` | clean |
| `uv run s32 renpy lint` | clean |
| `uv run s32 renpy test` | **16/16 testcases** |
| `uv run s32 simulate --runs 5000` | 51/51 reachable, 0 dead ends |
| `scripts/check.py` | **11/11** |

194 → 222 Python tests (+28) and 11 → 16 Ren'Py testcases (+5). New coverage:
relationship direction and its save migration (13), the calendar (16, plus 5
testcases), credits determinism (1). No test was added to raise a count.

One caveat worth recording: the commit that added the two anchors left
`test_every_location_has_something` red, because `common_room` existed as a
location before any storylet was written for it. It was green again one commit
later. The gate was not run between them, and it should have been.

---

## Architecture

**`NarrativeDirector` selection algorithm unchanged.** Byte-identical to how
Milestone 1 left it. Three milestones of density pressure and it has not needed
changing.

What did change:

| Change | Why it is not the director |
| --- | --- |
| `s32_engine/relationships.py` — `parse_pair`, source-first signatures, no defaults | Authoring ergonomics. The directed graph and its storage are untouched. |
| `s32_engine/conditions.py`, `effects.py` — arrow required, old form refused by name | Grammar, not selection. |
| `s32_engine/state.py` — save migration v3, both edges seeded | Data repair. |
| `s32_engine/calendar.py` — **new**, ~180 lines, derives everything | A view. Owns no state. |
| `s32_engine/documents.py` — three new `DocumentType` values | Presentation. |
| `s32tools/validation/` — arrow required, `PRIORITY_BANDS` | Validation. |
| `s32tools/cli.py` — testcase discovery | Tooling. A hand-written list had silently excluded five tests. |
| `game/screens/calendar.rpy` — **new** | UI. |
| `game/screens/debug.rpy` — both relationship edges | UI. |
| `scripts/first_week.py` — **new** | A reading tool. Subclasses the simulator and diffs state rather than re-implementing any decision. |

No new narrative subsystem. The calendar reuses `WorldState`, `commitments` and
`history`; the movement model still reuses `locations_with_content`.

---

## Git

Eight commits this milestone, on `main`, local only.

```
7e5c82d  docs: record milestone three, and what the first week measured
3fca495  tools: read a simulated first week, and fix a report of zeros
016d491  content: pass the new prose for tics, and stop one scene unteaching a fact
9138307  feat: add the calendar, as a view of the run rather than a copy of it
d43077f  content: write the first week, and give the cast lives outside the archive
461e314  docs: define the first week, and give it the anchors it needs
88fd956  fix: make generated credits reproducible
7e26fe1  fix: make relationship direction explicit, and correct 114 backwards edges
```

The two preflight fixes are the two oldest, each on its own, before any content
moved. Tests ship with the feature they cover rather than in a commit of their
own, which is why there is no `test:` commit.

Working tree clean. **Nothing pushed. No co-authors. No history rewritten.**

---

## HUMAN NARRATIVE REVIEW NEEDED

Nothing on this list can be settled by a tool.

1. **Read the three first weeks aloud.** `scripts/first_week.py` proves they
   differ mechanically. The question it cannot answer is whether they differ as
   *experiences*, and that is the milestone's actual claim.
2. **The four group scenes** — `the_common_room`, `common_room_three_way`,
   `annexe_two_of_them`, `courtyard_the_bench`. Four people in a room is the
   hardest thing in this project to write and the easiest to fake. Do they sound
   like four people, or like one writer taking turns?
3. **`theo_admits_it`'s third branch** is the only place in Act 1 where the
   player can be actively unkind and it costs them trust. Does it read as a real
   option or as a trap?
4. **`the_saturday`'s break branch** grants `annexe_is_locked` — the player who
   breaks the promise gets something for it. If that reads as the game rewarding
   the unkind choice, the fix is to make keeping it grant something too, not to
   take this away.
5. **Ms. Ellery, played off-sprite.** She works as a voice and a folder. Is that
   a solution or a stopgap that will read as one the moment anybody else in the
   scene has a face?
6. **`june_reads_it_flat`.** Rule R5 says the player must never feel stupid for
   agreeing with June. Read it and say whether agreeing feels like the
   intelligent option or like the one the game is waiting for you to abandon.
7. **`dorm_late_night` at nine plays per run**, of which about seven are the
   same third stage. Inside policy, and a lot of the same paragraph.
8. **`purp` → `gloom`**, carried from Milestone 1, still pending a human glance.
   [`HUMAN_ART_REVIEW.md`](HUMAN_ART_REVIEW.md).

---

## Remaining risks

**Art is the largest, and it has not moved in three milestones.**

- **The class photograph does not exist.** The premise turns on an object the
  game cannot show. It is an `image_placeholder` reading *CLASS PHOTOGRAPH — ART
  PENDING* inside a plausible archival mount, which is the honest presentation
  and is not a solution. It cannot be generated, cannot be a downloaded
  photograph of real people, and cannot be borrowed. It needs a commission.
- **There is no compatible male-presenting sprite.** Not attempted, per
  ADR-0005: mixing packs produces a cast that visibly comes from two places.
- **Ms. Ellery has no sprite**, and Milestone 3 has now written a scene *around*
  that rather than for it. That worked once. It will not scale, and every scene
  written to avoid her being on stage is a scene that will need rewriting when
  she has a face.

Three milestones of placeholders working is not evidence the problem is handled.
It is evidence that the problem has been deferred three times.

**Others.**

- **The first week is a draft.** Marked `ACT1_DRAFT`, not `CANON`. 222 passing
  tests say the machinery is sound; they say nothing about the dialogue.
- **The cast is likeable and has not cost the player anything.** `theo_admits_it`
  is the only scene where being unkind is a real option with a real price.
- **`rain_after_school` at 0.16 plays per run.** Weather-gated, relationship-gated,
  rooftop-gated. Flagged in Milestone 1, still the rarest scene in the game.
- **`iris_keeps_a_second_index` at 46%** gates `iris_the_second_box`, which is
  Iris's best scene. More than half of players will not see it.

---

## Next milestone

Not started. Recommended in
[`PROJECT_STATE.md`](PROJECT_STATE.md#next-milestone): **Act 1 depth, not Act 1
breadth** — a second and third beat per character, the rooftop, and somewhere
for `unsettling` to happen. Explicitly *not* a scale to 80–100 storylets: the
density measurements do not support it, and the first week is a draft nobody has
read aloud.
