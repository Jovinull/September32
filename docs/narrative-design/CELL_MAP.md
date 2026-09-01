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

Storylets naming each cell, after Milestone 3. Ceilings, not what a player meets
-- state gates cut these down, sometimes to nothing.

| Location | early morning | morning | midday | afternoon | evening | night | late night |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `archive_room` | 0 | 3 | 4 | 8 | 5 | 0 | 0 |
| `classroom_2b` | 2 | 2 | 2 | 3 | 2 | 1 | 0 |
| `common_room` | 1 | 2 | 2 | 2 | 6 | 4 | 0 |
| `courtyard` | 2 | 3 | 7 | 5 | 1 | 0 | 0 |
| `dorm_room` | 2 | 0 | 0 | 0 | 2 | 3 | 1 |
| `hallway_east` | 0 | 2 | 4 | 5 | 1 | 0 | 0 |
| `rooftop` | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| `school_gate` | 1 | 3 | 1 | 2 | 1 | 0 | 0 |
| `town_road` | 0 | 0 | 0 | 4 | 4 | 1 | 0 |

Nine locations now, because Milestone 3 added the common room: a residential
school with nowhere communal to sit was a gap in the fiction before it was a gap
in the map, and three of the four group scenes happen there.

Of 63 cells, 24 hold nothing, 12 hold one storylet, and 27 hold two or more.
The three milestones, against their own denominators:

| | cells | empty | one | two or more |
| --- | ---: | ---: | ---: | ---: |
| Milestone 1 (15 storylets, 8 locations) | 56 | 48% | 21% | 30% |
| Milestone 2 (30 storylets, 8 locations) | 56 | 48% | 14% | 38% |
| Milestone 3 (51 storylets, 9 locations) | 63 | 38% | 19% | 43% |

The empty share moved for the first time, and it moved because two `FUTURE`
cells got content rather than because anything was spread thin.

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

### `common_room` — new in Milestone 3

| Slot | Verdict | Note |
| --- | --- | --- |
| early morning | `ACTIVE` | Thin (1). The kettle, and somewhere to go that is not your own room. |
| morning | `ACTIVE` | |
| midday | `ACTIVE` | |
| afternoon | `ACTIVE` | |
| evening | `ACTIVE` | 6, the second densest cell in the game. This is what the location is for. |
| night | `ACTIVE` | 4. |
| late night | `INTENTIONALLY_EMPTY` | Everyone has gone up. |

Added because a residential school with nowhere communal to sit is a gap in the
fiction, and because three of the four group scenes need a room where four
people can plausibly already be when the player walks in.

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
| early morning | `ACTIVE` | Was the largest empty cell in the game: 34,000 visits and nothing authored, because the player wakes up here. Two ambient scenes now, and adding the second of them moved contested top tiers from 17% to 31% on its own. |
| morning | `INTENTIONALLY_EMPTY` | You are supposed to be in class. |
| midday | `INTENTIONALLY_EMPTY` | As above. |
| afternoon | `INTENTIONALLY_EMPTY` | As above. |
| evening | `ACTIVE` | |
| night | `ACTIVE` | 3. |
| late night | `ACTIVE` | Thin (1), and correctly so: `dorm_late_night` is the only thing that happens at that hour anywhere. |

`dorm_room` at early morning was the clearest content recommendation Milestone 2
produced, and Milestone 3 acted on it. The result is the strongest single piece
of evidence this project has that density is a content problem: one ambient
scene, written into the busiest empty cell, moved the contested-tier rate by
thirteen points without the director changing at all.

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
| evening | `ACTIVE` | Thin (1). `gate_going_out` and the sign-out book. |
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

Nine locations by seven slots is 63 cells.

| Verdict | Cells | Milestone 2 |
| --- | ---: | ---: |
| `ACTIVE` | 37 | 29 |
| `INTENTIONALLY_EMPTY` | 17 | 16 |
| `FUTURE` | 4 | 6 |
| `INVALID` | 5 | 5 |

Thirty-seven live cells against fifty-one storylets. The two `FUTURE` cells
Milestone 2 ranked first and second were both filled, and the remaining four are
all the rooftop and one thin corridor hour:

1. `rooftop` midday — the obvious scene nobody has written, and the location
   most clearly waiting for Act 2
2. `rooftop` night
3. `rooftop` early morning
4. `hallway_east` early morning — about 900 visits; low priority

The rooftop is now the only location in the game with one storylet in it. That
is the recommendation this milestone hands forward.

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

### Milestone 3

Twenty-one storylets, aimed the same way, plus a location that did not exist.

| Cell | Milestone 2 state | Added | Now |
| --- | --- | ---: | ---: |
| `dorm_room` early morning | 34,000 visits, 0 authored | +2 | 2 |
| `common_room` evening | did not exist | +6 | 6 |
| `common_room` night | did not exist | +4 | 4 |
| `hallway_east` afternoon | 22,600 visits, 2 authored | +3 | 5 |
| `archive_room` afternoon | 5 authored, mean eligible 1.0 | +3 | 8 |
| `courtyard` midday | 5 | +2 | 7 |
| `school_gate` evening | 8,300 visits, 0 authored | +1 | 1 |
| `town_road` afternoon/evening | 3 | +1 | 4 |
| `classroom_2b` afternoon | 2 | +1 | 3 |

The second entry in `dorm_room` early morning is worth singling out. It was not
in the plan; it exists because a 600-run sweep of the other twenty scenes showed
`dorm_early_start` taking 13% of everything played in the game on its own, from
a cell that had no competition. Adding one scene against it moved contested top
tiers from 17.2% to 30.7%.

## Reading a cell honestly

A cell with three storylets in this table is not a cell where the player meets
three. `density.md` reports the mean actually eligible, and for `archive_room`
afternoon that is 1.0 against 5 authored, because four of the five are gated on
state most runs do not have. The ceiling is what a writer controls; the mean is
what a player experiences. When they diverge that much, the answer is usually in
[`PRIORITY_AUTHORING.md`](PRIORITY_AUTHORING.md) and in the requirement list,
not in writing a sixth scene for the same hour.
