# The cell map

Eight locations by seven time slots is fifty-six cells. This file says what each
one is *for*, which is a different question from how many storylets it holds.

It exists because the obvious reading of Milestone 1's empty-cell count — half
the map is empty, therefore fill it — is wrong and would produce fifty-six
mediocre scenes. A school at four in the morning is empty. That is not a gap in
the content; it is the fiction working.

Recomputed at the end of Milestone 2 from `data/storylets/*.json`. Regenerate
the raw counts with `uv run s32 simulate` and read `density.md`.

## The four verdicts

| Verdict | Means | What to do about it |
| --- | --- | --- |
| `ACTIVE` | Authored, visited, and meant to stay that way. | Keep it dense enough to contend. |
| `INTENTIONALLY_EMPTY` | The fiction says nothing happens here at this hour. | Nothing. Do not author into it. |
| `FUTURE` | Should have content and does not yet. | A candidate for the next content milestone. |
| `INVALID` | The player should not be standing here at this hour at all. | Fix by gating movement, not by writing a scene. |

## The map

Storylets naming each cell, after Milestone 2. Ceilings, not what a player meets
— state gates cut these down, sometimes to nothing.

| Location | early morning | morning | midday | afternoon | evening | night | late night |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `archive_room` | 0 | 2 | 3 | 5 | 4 | 0 | 0 |
| `classroom_2b` | 2 | 2 | 2 | 2 | 1 | 1 | 0 |
| `courtyard` | 2 | 3 | 5 | 3 | 1 | 0 | 0 |
| `dorm_room` | 0 | 0 | 0 | 0 | 2 | 3 | 1 |
| `hallway_east` | 0 | 2 | 4 | 2 | 0 | 0 | 0 |
| `rooftop` | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| `school_gate` | 1 | 2 | 0 | 2 | 0 | 0 | 0 |
| `town_road` | 0 | 0 | 0 | 3 | 3 | 1 | 0 |

27 of 56 cells hold nothing, 8 hold one storylet, 21 hold two or more. Milestone
1 was 27 / 12 / 17 against the same denominator: the empty count did not move,
and that is the intended outcome. Fifteen new storylets went into cells that
already had something, or into a location that had nothing anywhere.

## Verdict by cell

### `archive_room` — the room the game is about

| Slot | Verdict | Note |
| --- | --- | --- |
| early morning | `INTENTIONALLY_EMPTY` | Iris opens it when she gets in. Nobody is in a school archive at half six. |
| morning | `ACTIVE` | Thin (2). The quiet hour. |
| midday | `ACTIVE` | |
| afternoon | `ACTIVE` | The densest cell in the game, 5. This is the room's hour. |
| evening | `ACTIVE` | 4. Iris stays late; that is characterisation, not scheduling. |
| night | `INTENTIONALLY_EMPTY` | Locked. If a later act wants the archive at night, getting in has to be the scene. |
| late night | `INTENTIONALLY_EMPTY` | As above. |

Milestone 2 closed the last two. `old_photo_glimpse` and `theo_ledger_question`
carried no `time_slots` at all, which meant the engine would offer them at three
in the morning in a locked room. That is not a cell being empty; that was a cell
being wrong.

### `classroom_2b`

| Slot | Verdict | Note |
| --- | --- | --- |
| early morning | `ACTIVE` | `classroom_before_bell` is written for exactly this. |
| morning | `ACTIVE` | |
| midday | `ACTIVE` | |
| afternoon | `ACTIVE` | |
| evening | `ACTIVE` | Thin (1). Noah's layout nights. |
| night | `ACTIVE` | Thin (1). Same, later. |
| late night | `INTENTIONALLY_EMPTY` | The block is locked. |

### `courtyard` — the busiest place in the game

| Slot | Verdict | Note |
| --- | --- | --- |
| early morning | `ACTIVE` | |
| morning | `ACTIVE` | |
| midday | `ACTIVE` | 5, and four of them are people. Lunch is where the school is. |
| afternoon | `ACTIVE` | |
| evening | `ACTIVE` | Thin (1). Acceptable: the courtyard empties out. |
| night | `INTENTIONALLY_EMPTY` | |
| late night | `INTENTIONALLY_EMPTY` | |

Milestone 1 had this location carrying 42% of everything played, from a single
ambient scene available at all seven hours. Both halves of that were wrong. It
now holds five scenes at its peak and none after dark.

### `dorm_room`

| Slot | Verdict | Note |
| --- | --- | --- |
| early morning | `FUTURE` | 34,000 visits and nothing authored — the single largest empty cell in the simulation, because the player wakes up here. Getting up is a scene nobody has written. |
| morning | `INTENTIONALLY_EMPTY` | You are supposed to be in class. |
| midday | `INTENTIONALLY_EMPTY` | As above. |
| afternoon | `INTENTIONALLY_EMPTY` | As above. |
| evening | `ACTIVE` | |
| night | `ACTIVE` | 3. |
| late night | `ACTIVE` | Thin (1), and correctly so: `dorm_late_night` is the only thing that happens at that hour anywhere. |

`dorm_room` at early morning is the clearest content recommendation this
milestone produces. It is not a density problem the director can fix.

### `hallway_east`

| Slot | Verdict | Note |
| --- | --- | --- |
| early morning | `FUTURE` | Thin traffic (about 900 visits). Low priority. |
| morning | `ACTIVE` | |
| midday | `ACTIVE` | 4. Between-lessons is what a corridor is. |
| afternoon | `ACTIVE` | 22,600 visits against 2 authored — the highest visit-to-content ratio still standing. |
| evening | `INTENTIONALLY_EMPTY` | 6,800 visits. See the note below. |
| night | `INVALID` | 8 visits in 5000 runs. Nobody should be in the east corridor at night. |
| late night | `INVALID` | Never visited. |

### `rooftop`

| Slot | Verdict | Note |
| --- | --- | --- |
| early morning | `FUTURE` | |
| morning | `INTENTIONALLY_EMPTY` | |
| midday | `FUTURE` | A roof at lunchtime is an obvious scene and there isn't one. |
| afternoon | `ACTIVE` | Thin (1), weather-gated. |
| evening | `ACTIVE` | Thin (1), same scene. |
| night | `FUTURE` | |
| late night | `INTENTIONALLY_EMPTY` | |

The rooftop is the location most obviously waiting for Act 1. One weather-gated
scene at two hours is not a place; it is a set with a single use.

### `school_gate`

| Slot | Verdict | Note |
| --- | --- | --- |
| early morning | `ACTIVE` | Thin (1). |
| morning | `ACTIVE` | |
| midday | `INTENTIONALLY_EMPTY` | 11,600 visits, nothing authored. Arguably `FUTURE`: nobody is at the gate at lunch, but the player keeps going there. |
| afternoon | `ACTIVE` | |
| evening | `FUTURE` | 8,300 visits. Going out, or coming back. |
| night | `INVALID` | Chained. 9 visits total. |
| late night | `INVALID` | |

This location had zero storylets at zero hours before Milestone 2, in a game set
at a school. It now has three.

### `town_road`

| Slot | Verdict | Note |
| --- | --- | --- |
| early morning | `INTENTIONALLY_EMPTY` | |
| morning | `INTENTIONALLY_EMPTY` | Lessons. |
| midday | `INTENTIONALLY_EMPTY` | Lessons. |
| afternoon | `ACTIVE` | 3. |
| evening | `ACTIVE` | 3. |
| night | `ACTIVE` | Thin (1) and deliberately so: `town_road_last_bus` is a scene about being out too late, which only works if there is nothing else out there. |
| late night | `INVALID` | 2,773 visits. The player should not be able to be on the road at three in the morning; the movement model lets them, and no scene rewards it. |

## The tally

| Verdict | Cells |
| --- | ---: |
| `ACTIVE` | 29 |
| `INTENTIONALLY_EMPTY` | 16 |
| `FUTURE` | 6 |
| `INVALID` | 5 |

Twenty-nine live cells against thirty storylets is the honest shape of the game
right now. The six `FUTURE` cells, ranked by how much traffic they already carry
with nothing in them:

1. `dorm_room` early morning — 34,000 visits, 0 authored
2. `school_gate` evening — 8,300 visits, 0 authored
3. `rooftop` midday — the obvious scene nobody has written
4. `rooftop` night
5. `rooftop` early morning
6. `hallway_east` early morning — about 900 visits; low priority

`hallway_east` afternoon is `ACTIVE` rather than `FUTURE`, but it is the
thinnest active cell by a distance: 22,600 visits against two storylets. It is
the first place a sixteenth scene should go.

## The hot cells, and why those

Milestone 2's fifteen storylets were aimed at eight cells rather than spread
across the map. The selection rule was: **traffic the simulator already measured,
crossed with a location that had a reason to exist.** Not "which cell is empty" —
`town_road` at 4am is empty and always should be.

| Cell | Milestone 1 visits | Authored then | Added | Now |
| --- | ---: | ---: | ---: | ---: |
| `courtyard` midday | high | 3 | +2 | 5 |
| `hallway_east` midday | 45,280 at afternoon, high at midday | 2 | +2 | 4 |
| `school_gate` morning | substantial, 0 authored | 0 | +2 | 2 |
| `school_gate` afternoon | substantial, 0 authored | 0 | +2 | 2 |
| `dorm_room` night | high | 2 | +1 | 3 |
| `dorm_room` late night | very high | 0 | +1 | 1 |
| `town_road` afternoon/evening | high | 2 | +1 | 3 |
| `archive_room` afternoon/evening | high | 3 | +2 | 5 |
| `classroom_2b` early morning | high | 1 | +1 | 2 |
| `courtyard` early morning/morning | very high | 1 | +2 | 3 |

Two of the fifteen did not go to a hot cell. `town_road_last_bus` and
`archive_iris_index` are there for the shape of the week rather than for
density, and both are flagged as such on their scene cards.

## Reading a cell honestly

A cell with three storylets in this table is not a cell where the player meets
three. `density.md` reports the mean actually eligible, and for `archive_room`
afternoon that is 1.0 against 5 authored, because four of the five are gated on
state most runs do not have. The ceiling is what a writer controls; the mean is
what a player experiences. When they diverge that much, the answer is usually in
[`PRIORITY_AUTHORING.md`](PRIORITY_AUTHORING.md) and in the requirement list,
not in writing a sixth scene for the same hour.
