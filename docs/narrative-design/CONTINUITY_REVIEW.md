# Continuity review

A storylet does not know what came before it. That is the price of the
architecture and it is worth paying, but it means one class of bug is always
available: a line of prose that assumes a history the player may not have.

This file is the checklist, the audit that ran at the end of Milestone 2, and
the policy for repeatable scenes.

It is a review, not a lint. There is no regex here that blocks a commit, and
there should not be — "again" is a perfectly good word and a rule that forbids
it would make the prose worse than the bug it prevents.

## The checklist

When a scene is written or changed, read it for these words. Each one is a
claim about the past.

| Word | The claim | What has to be true |
| --- | --- | --- |
| again | this happened before | a requirement, a `seen()`, or a `times_seen` branch |
| already | the player knows | `knows(...)` in the requirements |
| remember | a specific earlier moment | that moment fired, guaranteed |
| another | there was a first | a counted thing, not a vibe |
| second, third | an exact count | `times_seen`, not the RNG |
| still | an ongoing state | the state is actually modelled |
| as I said | this character said it | that scene played, with this character |
| like before | a comparable earlier scene | usually the hardest to guarantee |
| you know | shared knowledge | `knows(...)` or an NPC stance |
| last time | a prior instance | `times_seen` or a cooldown that guarantees one |

Three outcomes are legitimate, and the third is usually the best one:

1. **Guarantee it.** Add the requirement. The scene now needs a history, and
   `s32 explain` will say so.
2. **Guard it.** Branch on `knows(...)` or `times_seen(...)` and write both
   sides. `noah_evening_layout` does this.
3. **Rewrite it so the claim is not made.** Cheapest, and often better prose.
   A line that leans on a callback the player may not have is usually a line
   leaning on something it did not need.

## The Milestone 2 audit

Every `.rpy` under `game/story/storylets/` was read against this list. Thirty
scenes; 55 lines contain a checklist word, which is the reason this is a review
and not a lint. Almost all of them are the word doing ordinary work -- a second
bench, the third column, everybody still walks around. Twelve made a claim worth
adjudicating, and those are the ones below.

| Scene | Line | Verdict |
| --- | --- | --- |
| `noah_evening_layout` | "the second gap about a year long I've heard about this week" | **Fixed in Milestone 1.** Now guarded on `knows("school_history_skips_a_year") or knows("mara_knows_the_older_story")`; roughly a third of runs take the else branch. |
| `dorm_message` | second variant re-narrated the bench as a discovery | **Fixed in Milestone 1.** Rewritten to observe something else. |
| `hallway_after_bell` | "the second time this week somebody has explained Mara to you using the word fine" | **Fixed.** Nothing guaranteed a first time. Rewritten to "Which is the entire explanation anybody offers about Mara", which makes the same point without counting. |
| `hallway_lost_property` | "It's the second time I've done this crate." | **Kept.** Theo is counting his own actions, not the player's. No claim about the player's history. |
| `gate_waiting` | "doing it again from the start, in the same order" | **Kept.** Within-scene: the player watches him restart. |
| `dorm_late_night` | "Late again, and not for any reason." | **Kept and guaranteed.** It is the `times_seen == 1` branch; there was necessarily a first. |
| `iris_outside` | "You can sit here again, if you want." | **Kept.** Future tense — an invitation, not a claim about the past. |
| `archive_iris_index` | "a document the player may already have read" | **Kept.** In a comment, not in prose. The viewer applies effects once and re-reading is deliberately free. |
| `courtyard_lunch_table` | "They know each other well enough not to be polite" | **Kept.** About June and Noah, whose relationship exists in the character bibles independent of the player. |
| `town_road_last_bus` | "told you about the bus" | **Kept.** June said it four lines earlier, in the same scene. |
| `archive_theo_returns` | "people come in here twice a term" | **Kept.** Iris's own experience of the room, which predates the player. |
| `old_photo_glimpse` | "Look at the photograph again." | **Kept, and the model case.** The menu option is gated on `has_item("old_photo")`, so a first look is guaranteed by the requirement rather than hoped for by the prose. |

Two rules fell out of this that are worth stating:

**An NPC counting their own life is free.** Theo has done the crate twice
whether or not the player was there. That is characterisation and it needs no
state. The bug is only ever a claim about *the player's* history.

**A callback the player might not have is not a small problem.** It reads as the
game not paying attention, which is precisely the impression a quality-based
narrative cannot afford, because the whole promise is that it is paying
attention.

## Repeatable is not the same as resettable

A `repeat_policy` of `repeatable` says the engine may fire the scene again. It
says nothing about whether the *prose* can be read again. Milestone 1 shipped a
scene that discovered the same thing twice, which is how this section exists.

Four kinds, and the policy for each:

### `REPEATABLE AMBIENT`

No discovery, no state change, no reference to a previous time. Texture. Can
run twenty times and only gets slightly dull.

`courtyard_small_talk`. Everything about it is a fact about the school, not an
event in the player's week.

### `WITH VARIANTS`

Several interchangeable bodies, picked by `s32_rng().randint(...)`. Any variant
can be first, so no variant may reference another. Use when the variants are
*alternatives* — different things that could be happening in the same place.

`gate_early_arrival` (3), `courtyard_morning_queue` (2),
`dorm_corridor_noise` (2), `classroom_before_bell` (2).

The rule that makes this safe: **a variant may not know how many times the scene
has run.** If it needs to, it is the next kind.

### `PROGRESSIVE`

Variants keyed to `times_seen(<id>)`, in a fixed order, because the order is the
content. Use when the scene is about a state that changes — a room stopping
being unfamiliar, a habit forming.

`dorm_late_night`. Three stages: the room is strange, the room is a room, the
room is yours. Picking that at random is the bug this category exists to
prevent, and `times_seen` is exposed on the Ren'Py side specifically for it.

The rule: **the last stage must be stable.** `dorm_late_night`'s third branch
runs for every visit from the third onward, so there is no cliff at four.

### `ONCE ONLY`

`repeat_policy: once`. Anything that discovers something, changes a
relationship materially, or could not honestly happen twice.

Eighteen of the thirty. The test is not "would the engine allow it" but "would
a person do this twice" — Theo does not lose the same key twice.

### Cooldowns are a fifth thing, and they are not a policy

`gate_noticeboard` has a three-day cooldown. That is a pacing device, not a
continuity guarantee, and a cooldown does **not** license a callback: three days
later is still possibly the first time, because the first eligible day may not
have been visited. Scenes with cooldowns are audited as `WITH VARIANTS`.

## Audit of the existing repeatables

Twelve repeatable or cooldown scenes at the end of Milestone 2 -- five
`repeatable`, seven on a cooldown. Each was read for "discovering it again":

| Scene | Kind | Discovers something | Verdict |
| --- | --- | --- | --- |
| `courtyard_small_talk` | ambient | no | clean |
| `town_road_evening_walk` | ambient | no | clean |
| `hallway_encounter` | ambient | no | clean |
| `dorm_message` | variants | fixed in Milestone 1 | clean |
| `gate_early_arrival` | variants | `learn(caretaker_opens_at_seven)` in variant 1 only | clean — `learn` is idempotent and the prose does not say "so that is when it opens" a second time |
| `gate_noticeboard` | cooldown 3 | `learn(bound_volumes_were_moved)` behind a menu choice | **watch**: a player who picks "read the laminated one" twice reads the discovery twice. The prose is written as reading, not as discovering, which holds, but it is the thinnest case in the list |
| `courtyard_morning_queue` | variants | no | clean |
| `dorm_corridor_noise` | variants | no | clean |
| `hallway_lost_property` | cooldown 4 | no | clean |
| `dorm_late_night` | progressive | no | clean — and the reason `times_seen` exists |
| `town_road_shops` | cooldown 3 | `learn(caretaker_opens_at_seven)` behind a menu choice | clean — the line is about a rota being unsecret, not about learning a time |
| `classroom_before_bell` | variants | no | clean |

One `watch`, no failures. `gate_noticeboard` is the item to look at first if
this section is ever revisited.

## What this file does not do

It does not run. There is no `s32 continuity` command and there should not be
one until the failure mode is mechanical rather than editorial. Every entry
above required reading the scene and knowing what the player could be carrying;
a checker that could do that would be checking meaning, and it would be wrong
often enough to be ignored, which is worse than not existing.

Related: [`PRIORITY_AUTHORING.md`](PRIORITY_AUTHORING.md) for bands,
[`CELL_MAP.md`](CELL_MAP.md) for where scenes go.
