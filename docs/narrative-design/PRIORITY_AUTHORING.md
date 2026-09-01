# Priority authoring

**Status: CANON for the bands. The Director algorithm is unchanged.**

> Priority does not mean "this scene is better". It means "if these scenes
> compete, does one of them have to go first for structural reasons?"

If the answer is no, they belong in the same band, and the answer is usually no.

## What the director actually does

`NarrativeDirector.select` is two stages, and only the first one uses priority:

1. Take the eligible storylets. Keep **only those with the highest priority**.
   This is a hard tier, not a bonus.
2. Draw from that tier by `weight`, damped by how often the scene has been seen.

The consequence is the thing this document exists for: **a priority that is
unique to one storylet guarantees a tier of one, and a tier of one makes stage
two a formality.** Weight cannot act. Repeat damping cannot act. The draw has
one ticket in the hat.

## The audit that produced this file

The fifteen Milestone 1 storylets carried these priorities:

```
75 72 70 68 66 65 64 62 60 58 56 50 40 22 20
```

Fifteen storylets, fifteen distinct values. Instrumenting 5000 runs found the
top tier held exactly one storylet in **100.0%** of selections. Not most. All.

Asked scene by scene why each number was that number, the honest answer was
almost always "it needed to be above the one below it". The numbers encoded a
total ranking of the whole library, which is a thing nobody can maintain past
about thirty scenes and which mathematically eliminates the weighted draw.

The important finding of the audit is that **the ranking was not load-bearing.**
Narrative order is already enforced by requirements, not by priority:

| Storylet | what actually orders it |
| --- | --- |
| `old_photo_glimpse` | `seen(archive_intro)` |
| `theo_ledger_question` | `knows(old_photo_exists)` and an active commitment |
| `message_after_class` | `knows(old_photo_exists)` |
| `june_welcome_pack` | `seen(june_the_favour)` |
| `mara_older_story` | `seen(mara_reads_the_room)` and `knows(old_photo_exists)` |

Every one of those would fire in the same order with every priority set to the
same number. So the ranking could be collapsed without touching a requirement,
a blocker or a line of prose.

## The bands

Five values. Nothing between them. A storylet that seems to want 45 wants a
different requirement, not a different priority.

| Value | Band | Meaning |
| ---: | --- | --- |
| 100 | `REQUIRED` | The run is incoherent if this does not happen now. Reserved; anchors are separate objects and cover most of this today. |
| 80 | `URGENT` | A commitment falling due, or a consequence that stops making sense if deferred. |
| 60 | `CALLBACK` | Reacts to a specific earlier decision, or to a condition that will pass. Loses meaning if it waits indefinitely. |
| 40 | `EVENT` | The ordinary body of the game. Character scenes, world scenes, investigation beats. **Most content lives here.** |
| 20 | `AMBIENT` | Texture. Must never outrank anything with something to say. |

### How to choose

Ask, in order:

1. **Does something break if this waits?** No -> not `URGENT`.
2. **Does it refer back to a decision, or to a window that will close?**
   No -> not `CALLBACK`.
3. **Is it ordinary life that could happen on any suitable day?**
   Yes -> `AMBIENT` if it is texture, `EVENT` if it has content.

Most scenes stop at 3 and land on `EVENT`. That is correct and it is the point:
`EVENT` is where competition happens.

### What must not decide a band

- How good the scene is.
- How much work it was.
- How much the writer wants the player to see it. That is `weight`.
- How rare it should be. That is `weight`, or a requirement.

A scene nudged up a band to make sure it gets seen has not been prioritised; it
has been removed from competition, and every scene it now outranks has been
quietly demoted with it.

## Weight, now that it can act

Inside a band, `weight` sets relative frequency. It is a ratio, not a
percentage: two storylets at 1.0 and 2.0 are drawn roughly one to two.

Reasonable range is about **0.5 to 3.0**. Outside that, ask what is really
meant:

- `weight: 0.05` to hide a scene -> the scene wants a requirement, or deleting.
- `weight: 50` to guarantee a scene -> the scene wants a higher band, or it is
  an anchor.

Repeat damping halves a storylet's weight for each time it has been seen, so a
repeatable ambient scene at 3.0 is already at 0.375 by its fourth appearance.
Do not compensate for that by raising the base weight; that is the mechanism
working.

## What changed, and what did not

Applied to the existing fifteen:

| Storylet | was | now | why |
| --- | ---: | ---: | --- |
| `theo_ledger_question` | 72 | **80** | Requires an active commitment. It *is* the appointment. |
| `mara_older_story` | 68 | **60** | Callback to `mara_reads_the_room`. |
| `june_welcome_pack` | 62 | **60** | Callback to `june_the_favour`. |
| `noah_evening_layout` | 64 | **60** | Callback to learning what Noah writes. |
| `rain_after_school` | 65 | **60** | Weather-gated: the window genuinely closes. |
| `old_photo_glimpse` | 75 | **40** | Ordered by `seen(archive_intro)`, not by rank. |
| `archive_intro` | 70 | **40** | Same. |
| `june_the_favour` | 58 | **40** | An ordinary conversation. |
| `mara_reads_the_room` | 56 | **40** | An ordinary conversation. |
| `noah_asks_for_access` | 60 | **40** | An ordinary conversation. |
| `message_after_class` | 50 | **40** | Ordered by `knows(old_photo_exists)`. |
| `dorm_message` | 66 | **40** | Fires on any evening; only sometimes carries the promise. |
| `hallway_encounter` | 40 | **20** | Texture. |
| `courtyard_small_talk` | 20 | **20** | Unchanged. |
| `town_road_evening_walk` | 22 | **20** | Unchanged. |

**No requirement, blocker, effect, outcome or line of prose was changed by this
reband.** Ordering is where it always was.

### The three that moved down the most

`old_photo_glimpse` and `archive_intro` dropped 35 and 30 points, which looks
alarming and is not. They are the mystery spine, and the spine is protected by
`seen(archive_intro)` and `flag archive_visits >= 1`, which no other scene can
satisfy on their behalf. What the drop buys is that an ordinary conversation in
the archive can now compete with them on an afternoon when both fit, which is
the behaviour the room should have had all along.

## What the reband measured, and what it did not fix

Rebanding on its own, before any new content, over 5000 runs at seed 1234:

| | 15 storylets, ranked | 15 storylets, banded |
| --- | ---: | ---: |
| Top tier held 1 | 100.0% | 99.9% |
| Top tier held 2+ | 0.0% | **0.1%** |
| Exactly one eligible | 93.2% | 93.2% |

**0.1%.** The reband is necessary and it was nowhere near sufficient, and that
result is the most useful number this milestone produced, because it separates
two problems that had been getting one answer.

Collapsing fifteen ranks into five bands cannot create a contest between scenes
that are never eligible at the same moment. 93.2% of productive moments had one
candidate; five bands over one candidate is still one candidate. The tier was a
singleton because the *library* was, not only because the priorities were.

With fifteen more storylets, aimed at cells the simulator said were busy:

| | Milestone 1 | after reband | after +15 |
| --- | ---: | ---: | ---: |
| Nothing eligible | 64.5% | 64.6% | 32.5% |
| Exactly one eligible, of productive moments | 93.2% | 93.2% | **57.9%** |
| Top tier held 2+ | 0.0% | 0.1% | **18.1%** |
| Storylets reachable | 15/15 | 15/15 | 30/30 |

The ceiling on the third row is the second: the top tier cannot hold two unless
two are eligible, and two are eligible in 28.5% of moments. 18.1 out of a
possible 28.5 means the bands are keeping roughly two thirds of the available
contests intact and losing the rest to a legitimate rank — an `EVENT` beating an
`AMBIENT` is the system working, not a loss.

## Milestone 3: the bands held, and the content did the work

Twenty-one more storylets, no change to the bands, no change to the director.

| | M1 (15) | M2 (30) | **M3 (51)** |
| --- | ---: | ---: | ---: |
| Nothing eligible | 64.5% | 32.5% | **26.6%** |
| One eligible, of productive moments | 93.2% | 57.9% | **44.5%** |
| Two or more eligible | 6.8% | 30.3% | **40.7%** |
| Top tier held 2+ | 0.0% | 18.1% | **30.9%** |
| Contests kept, of contests available | — | 60% | **76%** |

The band distribution across fifty-one storylets:

| Band | Storylets |
| --- | ---: |
| `URGENT` (80) | 2 |
| `CALLBACK` (60) | 9 |
| `EVENT` (40) | 28 |
| `AMBIENT` (20) | 12 |

`EVENT` holds more than half the library, which is the shape the convention was
written for: it is the band where competition happens, and everything that does
not have a structural reason to go first belongs in it.

**The single most instructive result of the milestone** is that the biggest move
in the contested-tier rate came from one ambient scene. After twenty new
storylets the rate was 17.2% -- *below* where Milestone 2 left it. The cause was
`dorm_room` at early morning: the player wakes up there every day of a
fourteen-day run, one scene had been written for it, and that scene was taking
13% of everything played in the game with nothing to compete against.

Writing a second one moved contested tiers to 30.7%.

The lesson is not "add ambient scenes". It is that a cell with one storylet and
high traffic is worth more attention than a cell with none, because the empty
cell costs a moment and the single-occupancy cell costs a *choice* -- and only
the second one is invisible in a play-count table.

## Ten real contested selections

Collected from live runs, not constructed. Each is a moment where the top band
held more than one storylet and the weighted draw actually decided something.
`w` is the effective weight after repeat damping.

- **random**, day 2 early morning, `courtyard` — band 20
  - tier: `courtyard_morning_queue` (w 2.5), `courtyard_small_talk` (w 3.0)
  - played `courtyard_morning_queue`, against the odds, which is the point
- **random**, day 3 midday, `courtyard` — band 40
  - tier: `courtyard_lunch_table` (w 1.3), `june_the_favour` (w 1.5), `noah_asks_for_access` (w 1.2)
  - outranked: `courtyard_small_talk`
  - played `june_the_favour`
- **random**, day 3 night, `dorm_room` — band 20
  - tier: `dorm_corridor_noise` (w 2.0), `dorm_late_night` (w 1.25)
  - played `dorm_corridor_noise`; `dorm_late_night` is damped, having been seen
- **random**, day 4 midday, `courtyard` — band 40
  - tier: `courtyard_lunch_table` (w 1.3), `noah_asks_for_access` (w 1.2)
  - played `courtyard_lunch_table`
- **random**, day 5 midday, `hallway_east` — band 40
  - tier: `hallway_lost_property` (w 0.6), `mara_reads_the_room` (w 1.5)
  - outranked: `hallway_encounter`
  - played `mara_reads_the_room`
- **random**, day 5 afternoon, `hallway_east` — band 40
  - tier: `hallway_after_bell` (w 1.2), `hallway_lost_property` (w 0.6)
  - played `hallway_lost_property`, at 1:2 against
- **altruistic**, day 2 midday, `hallway_east` — band 40
  - tier: `hallway_after_bell` (w 1.2), `hallway_lost_property` (w 1.2)
  - outranked: `hallway_encounter`
  - played `hallway_after_bell`
- **altruistic**, day 4 morning, `courtyard` — band 20
  - tier: `courtyard_morning_queue` (w 2.5), `courtyard_small_talk` (w 3.0)
  - played `courtyard_morning_queue`
- **curious**, day 1 night, `dorm_room` — band 20
  - tier: `dorm_corridor_noise` (w 2.0), `dorm_late_night` (w 2.5)
  - played `dorm_late_night`
- **curious**, day 2 midday, `courtyard` — band 40
  - tier: `courtyard_lunch_table` (w 1.3), `june_the_favour` (w 1.5)
  - outranked: `courtyard_small_talk`
  - played `courtyard_lunch_table`

The `outranked` lines are the bands doing the job they were introduced for.
`courtyard_small_talk` is texture; at midday it loses to whatever has something
to say, without needing a number chosen to be larger than its number.

Reproduce with the same shape of instrumentation used for the density report:
subclass `Simulator`, record `selection.eligible` grouped by priority.

## Anti-pattern: priority as a substitute for a requirement

```json
"priority": 71,
"requirements": []
```

This says "beat everything at 70". It will keep working until someone writes a
scene at 72, and it tells a future reader nothing. If the scene must precede
another, say so:

```json
"priority": 40,
"requirements": ["not_seen(the_thing_that_must_come_after)"]
```

or put the dependency on the later scene, which is usually the better place.

## Checking it

`s32 validate` reports an `off-band-priority` info finding for any storylet
outside the five values. It is informational, not an error: a deliberate
exception is allowed, but it has to be deliberate enough to notice.

`s32 simulate` reports the top-tier size distribution under
**Top priority tier size**. If that table says 100% at size 1 again, the bands
have drifted back into a ranking.
