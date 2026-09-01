# Milestone 3 scene cards — Act 1

Twenty-one storylets and two anchors, indexed. The full template is
[`SCENE_CARD_TEMPLATE.md`](../SCENE_CARD_TEMPLATE.md); what follows is the part
that has to exist before the prose does — purpose, who is in it, what it is
allowed to change, and where it could go wrong.

The structural reasoning is in [`ACT_1.md`](../ACT_1.md), the cell targeting in
[`CELL_MAP.md`](../CELL_MAP.md), and the bands in
[`PRIORITY_AUTHORING.md`](../PRIORITY_AUTHORING.md).

## The index

| Storylet | Title | Characters | Location | Hours | Phases | Band | Repeat | Requires | Branches |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `dorm_early_start` | Before the Bell | — | `dorm_room` | early morning | any | 20 AMBIENT | repeatable 1d | — | 0 |
| `dorm_bathroom_queue` | Third in the Queue | — | `dorm_room` | early morning | any | 20 AMBIENT | repeatable 1d | — | 0 |
| `hallway_afternoon_drift` | Between Lessons | — | `hallway_east` | afternoon | any | 20 AMBIENT | repeatable 1d | — | 0 |
| `common_room_evening` | The Sofa Nobody Sits On | — | `common_room` | evening, night | any | 20 AMBIENT | repeatable 1d | `anchor_done(the_common_room)` | 0 |
| `common_room_kettle` | The Kettle Question | — | `common_room` | early morning – afternoon | any | 20 AMBIENT | cooldown 2d | `anchor_done(the_common_room)` | 0 |
| `gate_going_out` | Signing Out | — | `school_gate` | evening | any | 40 EVENT | cooldown 3d | — | 3 |
| `mara_the_long_way` | The Long Way | mara | `town_road` | afternoon, evening | any | 40 EVENT | once | `rel mara->player.familiarity >= 6` | 3 |
| `theo_the_spreadsheet` | Column J | theo | `common_room` | evening, night | any | 40 EVENT | once | `anchor_done(the_common_room)` | 3 |
| `june_the_kitchen` | The Rota | june | `common_room` | evening | any | 40 EVENT | once | `anchor_done(the_common_room)` | 3 |
| `noah_the_sports_report` | Two Hundred Words | noah | `classroom_2b` | afternoon, evening | any | 40 EVENT | once | `seen(noah_asks_for_access)` | 3 |
| `iris_the_apology` | She Takes It Out of Your Hands | iris | `archive_room` | morning – afternoon | any | 40 EVENT | once | `seen(archive_intro)` | 3 |
| `ellery_the_sign_off` | Countersigned | ellery | `archive_room` | afternoon | any | 40 EVENT | once | `flag archive_visits >= 1`, `day >= 3` | 3 |
| `common_room_three_way` | The Rota, Continued | june, mara, theo | `common_room` | evening | any | 40 EVENT | once | `anchor_done(the_common_room)`, `seen(common_room_kettle)` | 3 |
| `annexe_two_of_them` | Not Your Story Yet | iris, noah | `hallway_east` | afternoon | any | 40 EVENT | once | `knows(noah_is_writing_about_the_archive)`, `seen(archive_intro)` | 3 |
| `courtyard_the_bench` | From Here | mara, noah | `courtyard` | midday, afternoon | any | 40 EVENT | once | `seen(mara_reads_the_room)`, `seen(noah_asks_for_access)` | 3 |
| `iris_the_second_box` | The Second Shoebox | iris | `archive_room` | afternoon, evening | any | 60 CALLBACK | once | `knows(iris_keeps_a_second_index)`, `rel iris->player.trust >= 14` | 3 |
| `theo_admits_it` | Wrong About the Crate | theo | `common_room` | evening, night | any | 60 CALLBACK | once | `flag theo_lost_something >= 1`, `rel theo->player.trust >= 8` | 3 |
| `june_needs_saturday` | Saturday, Then | june | `courtyard` | midday, afternoon | any | 40 EVENT | once | `seen(hallway_after_bell)`, `rel june->player.familiarity >= 8` | 3 |
| `the_saturday` | Saturday | june | `school_gate` | morning, midday | any | **80 URGENT** | once | `commitment(saturday_with_june) == active` | 3 |
| `june_reads_it_flat` | The Reasonable Reading | june | `common_room` | evening, night | **odd+** | 60 CALLBACK | once | `knows(attendance_sheet_anomaly)`, `anchor_done(the_common_room)` | 3 |
| `annexe_door` | The Annexe | — | `hallway_east` | afternoon, evening | **odd+** | 40 EVENT | once | `knows(bound_volumes_were_moved)` | 3 |

Two anchors, in
[`data/anchors/`](../../../data/anchors) and written in
[`anchors.rpy`](../../../game/story/anchors/anchors.rpy):

| Anchor | Order | Earliest | Phase after | Requires |
| --- | ---: | --- | --- | --- |
| `the_common_room` | 3 | day 3 | `normal` | `anchor_done(first_shift)` |
| `the_undated_column` | 4 | day 4 | **`odd`** | `anchor_done(the_common_room)`, `flag archive_visits >= 1` |

## Purposes, in one line each

**World**

- `dorm_early_start` / `dorm_bathroom_queue` — what getting up here is like.
  Two of them because one was taking 13% of every scene played in the game.
- `hallway_afternoon_drift` — the four minutes after the last lesson, and the
  problem of not having a plan.
- `common_room_evening` / `common_room_kettle` — the room in two lights.
- `gate_going_out` — the sign-out book, which is the only bureaucracy the player
  ever has to touch and is funnier than that sounds.

**Character** — one each, and none of them about the archive

- `mara_the_long_way` — she walks you back the long way and does not say why.
  A dog, a gate, and how long it takes to stop being new somewhere.
- `theo_the_spreadsheet` — Column J is `seen`, not `logged`. He is pleased with
  it. Checking is how he cares, and here it is charming rather than anxious.
- `june_the_kitchen` — a birthday nobody organised, organised in four minutes.
  Her charm at full strength doing something good with itself.
- `noah_the_sports_report` — 200 words on a fixture he did not watch, and he
  phones somebody rather than writing "a spirited second half".
- `iris_the_apology` — she takes a paperweight out of your hands and apologises,
  and means the apology and not the taking. Nothing is discovered.
- `ellery_the_sign_off` — she countersigns a week of boxes. Canon says she is
  not a conspiracy; her first scene is her doing the job.

**Group**

- `common_room_three_way` — the kitchen rota, which is not about the kitchen
  rota. Moves `mara->june`, `june->mara` and `theo->june` depending.
- `annexe_two_of_them` — Noah wants to print it, Iris will not have it, and
  both are right about something. The sharpest fork of the milestone.
- `courtyard_the_bench` — Mara and Noah on whether being from somewhere
  qualifies you to write about it. Neither has seen the photograph.

**Callback and consequence**

- `iris_the_second_box` — she has started the second shoebox. Four cards in,
  two hundred and six boxes to go. She does not say why it matters.
- `theo_admits_it` — he was wrong about something small, and the player can
  give him the one thing his bible says he needs, or refuse to.
- `june_needs_saturday` → `the_saturday` — a promise about nothing important,
  falling due on the one morning the annexe is open.

**Odd**

- `june_reads_it_flat` — the ordinary explanation, argued well. Rule R5 given a
  scene.
- `annexe_door` — a locked door with nothing behind it yet, and the scene says
  so.

## Continuity risks, recorded before they became bugs

Two of these did become bugs and were caught in the audit
([`CONTINUITY_REVIEW.md`](../CONTINUITY_REVIEW.md)):

- **`iris_the_second_box`** — gated on `knows(iris_keeps_a_second_index)`, which
  is not the same as having *seen* the box. The opening claimed the player had.
  Fixed.
- **`june_reads_it_flat`** — closed on a callback to one variant of
  `common_room_evening`, which the player may never have played. Fixed.
- **`annexe_two_of_them`** — "he does not usually leave first" needs at least one
  prior Noah scene, which `knows(noah_is_writing_about_the_archive)` guarantees.
  Kept, and it is the thinnest thing kept.
- **`theo_admits_it`** — the harsh branch damages `theo->player.trust`, which is
  the only branch in Act 1 that lowers a trust axis. Deliberate: a scene where
  every option is kind is not a scene with a choice in it.
- **`the_saturday`** — the break branch grants `annexe_is_locked`, so a player
  who breaks the promise gets something for it. If that ever reads as the game
  rewarding the unkind option, the fix is to make keeping it grant something
  too, not to take this away.

## What none of these may do

- Explain September 32, or imply any of the four hypotheses in
  [`SEPTEMBER_32.md`](../../canon/SEPTEMBER_32.md).
- Settle any character's `core wound`. All five are still `IDEA`.
- Advance the phase. Only anchors do that.
- Read a date. `calendar_day` is a label.
