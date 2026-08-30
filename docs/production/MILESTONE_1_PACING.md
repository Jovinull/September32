# Pacing and content mix after Milestone 1

Companion to the generated [`MILESTONE_1_SIMULATION.md`](MILESTONE_1_SIMULATION.md),
which holds the raw before/after numbers. This file is the reading of them.

Both runs: 5000 playthroughs, seed 1234, 14 in-fiction days. The seed is fixed
so that the only variable between them is the content.

## What the milestone was asked to prove

That more hand-written content, on its own, relieves the repetition the
bootstrap simulation found — without touching the repeat algorithm.

**It half worked, and the half that failed is more useful than the half that
succeeded.**

## What clearly improved

| | 7 storylets | 15 storylets |
| --- | ---: | ---: |
| Unique scenes seen per run | 5.93 | **13.60** |
| Share taken by the single most played scene | 71.7% | **42.1%** |
| Runs in which June appears | 0% | 100% |
| Runs in which Mara appears | 0% | 94% |
| Runs in which Noah appears | 0% | 100% |
| `iris_keeps_a_second_index` learned | 2.2% | **23.7%** |

A player now sees 13.6 distinct scenes instead of 5.9, and meets three people
who previously did not exist in play at all. Every once-only storylet fires in
essentially 100% of runs — the authored content is being seen, not stranded.
`rain_after_school` is the deliberate exception at 23.7%, gated on weather and
on a relationship the player has to have actually built.

## What did not improve, and why

Repeats per run went **up**, 14.99 to 21.45. That is the opposite of the hoped
direction, and it is worth being precise about the cause rather than adjusting
the number.

Total plays across 5000 runs, 175,225. The two ambient repeatables take 63.7%:

| Storylet | plays | share | per run |
| --- | ---: | ---: | ---: |
| `courtyard_small_talk` | 73,830 | 42.1% | 14.77 |
| `town_road_evening_walk` | 37,721 | 21.5% | 7.54 |
| `hallway_encounter` | 7,834 | 4.5% | 1.57 |
| `dorm_message` | 5,292 | 3.0% | 1.06 |
| *(the eleven once-only scenes)* | 4,700-5,000 each | 2.7-2.9% each | ~1.00 |
| `rain_after_school` | 1,184 | 0.7% | 0.24 |

Adding a second repeatable did not dilute the first. It added capacity
alongside it: `courtyard_small_talk` barely moved (75,000 to 73,830) while
`town_road_evening_walk` contributed 37,721 plays on top.

### The actual cause

A run is 14 days x 7 time slots = **98 opportunities**, against roughly a dozen
once-only scenes. Something has to fill the other ~85. Whatever is repeatable
absorbs all of it. This is arithmetic, not a flaw in the damping.

Measuring the moment of choice makes it concrete. Across 100 instrumented runs:

- **92.7%** of selections had exactly **one** eligible storylet.
- 7.3% had two.
- Never more.

The director is almost never choosing. It is reporting the only thing that can
happen. Content mix, repetition and profile behaviour are all downstream of
that single fact.

### The map, by hour

Storylets eligible in each (location, time slot) cell, ignoring state gates —
so these are ceilings, not what the player actually meets:

| | early | morn | late_m | aft | late_a | eve | night |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `archive_room` | 2 | 2 | 2 | 3 | 2 | 2 | 2 |
| `classroom_2b` | 1 | 1 | 1 | 2 | 1 | 2 | 2 |
| `courtyard` | 1 | 1 | 1 | 3 | 1 | 1 | 1 |
| `dorm_room` | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| `hallway_east` | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| `rooftop` | 0 | 0 | 0 | 1 | 0 | 1 | 0 |
| `school_gate` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `town_road` | 0 | 0 | 0 | 2 | 0 | 2 | 0 |

Of 56 cells: **50% are empty**, 25% hold exactly one storylet, 25% hold two or
more. `school_gate` is a location the player can stand in at any hour of any
day with nothing authored there. `hallway_east` exists only in the morning.

## The recommendation, and what was deliberately not done

The brief asked that the repeat algorithm not be changed unless the data still
showed a genuine design problem after the content landed. The data shows a
genuine problem, and it is **not** in the repeat algorithm.

Lowering the repeat weight of `courtyard_small_talk` would not produce variety.
With one eligible candidate in 92.7% of moments, suppressing it yields an empty
slot — the player would get less, not more. The damping is working correctly on
a library that gives it nothing to work with.

**No cooldown, weight or repeat-policy value was changed.** The finding is a
content-density one and belongs to the next content milestone:

1. Author for the empty cells, not for the whole library. `school_gate` at any
   hour, `hallway_east` outside morning, `courtyard` outside afternoon.
2. Aim for **three or more** eligible candidates in the common cells. That is
   the threshold at which the director begins to make decisions, and below
   which no amount of tuning matters.
3. Prefer several short ambient scenes per location over one long one. The
   courtyard's dominance is not that it is over-weighted; it is that at most
   hours it is the courtyard's only scene.

## Player profiles see the same game

Run separately over 250 seeds each, the six profiles produce **identical**
output — the same 13.7 unique scenes, the same 21.5 repeats, the same
`courtyard_small_talk` at 42%, the same tag mix.

The cause is mechanical. `Simulator._apply_profile` re-picks only within the
top priority tier, and returns the director's choice unchanged when that tier
holds one storylet. All 15 storylets carry distinct integer priorities
(20, 22, 40, 50, 56, 58, 60, 62, 64, 65, 66, 68, 70, 72, 75), so the top tier
is a singleton in **100%** of selections and the scoring code never runs.

Two things are true at once and both should be recorded:

- The profiles are currently inert. Any coverage claim resting on "we swept six
  different kinds of player" is not supported — the sweep is one player, six
  times.
- Even if the tier logic were relaxed, 92.7% of moments offer one candidate.
  Profiles cannot express taste where there is nothing to choose between.

So the profile mechanism is not worth changing yet: it would still have nothing
to bite on. Whether priority should band (say, tiers of ten) rather than be a
unique integer per storylet is a real architectural question, but it belongs to
[ADR-0002](../decisions/ADR-0002-storylet-architecture.md) and should be decided
deliberately, against content dense enough to test it. It was left alone.

## Content mix

| Tag | before | after | change |
| --- | ---: | ---: | ---: |
| `slice_of_life` | 90.4% | 94.3% | +3.9% |
| `school` | 85.6% | 63.5% | -22.0% |
| `character` | 4.9% | **23.3%** | +18.4% |
| `friendship` | 13.9% | 15.9% | +2.0% |
| `mystery` | 9.6% | 14.1% | +4.5% |
| `archive` | 14.3% | 8.6% | -5.8% |
| `investigation` | 9.6% | 8.6% | -1.0% |
| `romance` | 0.1% | 0.7% | +0.6% |

Tags are multi-label, so these do not sum to 100%. Two readings need
separating:

`slice_of_life` rising to 94.3% looks like drift toward the mundane. It is not.
Nearly everything authored for the NORMAL phase carries the tag by design, and
both ambient repeatables carry it, so the figure mostly restates the repetition
above. It is a weak signal and should not be used as a mix target.

`character` at 4.9% to 23.3% is the real one, and it is the number the milestone
was actually testing. Roughly a quarter of what a player encounters is now a
scene about a specific person rather than about the building. `school` falling
22 points is the same movement seen from the other side: the town road exists
now, so not every hour happens on campus.

`archive` and `investigation` each slipped about a point in *share* while
holding steady in absolute terms — the denominator grew. No archive content was
removed.

`romance` at 0.7% is honest and expected. Nothing in Milestone 1 was written as
romance, and the tag is present on one Iris scene.
