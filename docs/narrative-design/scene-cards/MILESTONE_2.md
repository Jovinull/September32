# Milestone 2 scene cards

Fifteen scenes, written before the prose. The milestone's question is not "is
there enough content" but "can two things legitimately happen at once", so
these cards are grouped by the **cell** they contend for rather than by
character.

The design constraint that shaped every card: **overlap on purpose.** Milestone
1 authored scenes so specifically that they almost never competed. Requirements
here answer one question only — *why can this scene not happen without that
condition?* Anything that could not answer it was cut.

All fifteen are `normal` phase, no `phases` field, so they remain available
later. Priority follows [`PRIORITY_AUTHORING.md`](../PRIORITY_AUTHORING.md).

---

## Contended cell: `school_gate`, early_morning / morning

Empty at every hour before this milestone, in a game about a school. Three
scenes, deliberately overlapping.

### 1. `gate_early_arrival` — AMBIENT 20, repeatable

**Where:** school_gate, early_morning + morning.
**Who:** nobody named.
**Does:** The gate is chained until the caretaker arrives. Four or five people
wait in the cold, in the particular silence of people who are not friends but
recognise each other.

Three variants on the engine RNG. Establishes the school's routine and the fact
that the day has an edge you stand outside of. Grants
`caretaker_opens_at_seven` on the variant that shows it.

**Why it exists:** the game had no scene about arriving anywhere.

### 2. `gate_noticeboard` — EVENT 40, cooldown 3

**Where:** school_gate, morning + afternoon.
**Who:** nobody named.
**Does:** The glass case by the gate. Lost property, a club that has folded, a
laminated notice about the bound volumes of the school paper being moved into
storage.

**Choice:** read the whole thing / take the lost-property notice down / walk on.
Reading it grants `bound_volumes_were_moved`, which is the *boring* explanation
for the gap Noah found. R5 requires the sceptical reading to stay available and
this is it arriving on paper, without a character to argue with.

**Why the cooldown:** a noticeboard changes weekly, not hourly.

### 3. `gate_waiting` — EVENT 40, once

**Where:** school_gate, afternoon.
**Who:** Theo.
**Does:** Theo is at the gate at the end of the day, not leaving, checking his
bag for the third time. He has lost something and does not want to say what.

**Choice:** help look / ask what it is / leave him to it. Asking directly gets a
deflection and `rel theo.respect`; helping gets `familiarity` and, on a trait
check, the detail that he is looking for a key.

**Callback out:** sets `flag theo_lost_something`, which `archive_theo_returns`
reads.

---

## Contended cell: `courtyard`, morning / midday / afternoon

The busiest cell in the simulation and the one the old library served with a
single ambient scene at 42% of all plays.

### 4. `courtyard_morning_queue` — AMBIENT 20, repeatable

**Where:** courtyard, early_morning + morning.
**Who:** nobody named.
**Does:** The queue at the hatch that sells three things. School rules that
exist for a reason nobody remembers. Two variants.

**Why it exists:** `courtyard_small_talk` was carrying every ordinary moment in
the game by itself. This is the second option in the same room, which is what
the repeat damping needed to have somewhere to send the player.

### 5. `courtyard_lunch_table` — EVENT 40, once. **Group scene.**

**Where:** courtyard, midday.
**Who:** June **and** Noah.
**Does:** June has annexed a table. Noah arrives with the paper's layout on
printouts because the laptop is booked. They know each other and do not
particularly get on: June thinks the paper is a hobby with a self-image, Noah
thinks June organises things so she does not have to be in them.

**Choice:** take June's side / take Noah's side / refuse to referee. Every
branch moves an NPC-to-NPC axis, so the disagreement exists whether or not the
player joins it.

**Why it exists:** §24. Two NPCs in a room is the only way `rel june->noah` gets
a visible cause.

### 6. `iris_outside` — EVENT 40, once

**Where:** courtyard, morning + midday.
**Who:** Iris.
**Does:** Iris out of the archive, in daylight, looking wrong in it. She is
eating lunch at ten past eleven because that is when the archive is quiet.

**Choice:** sit with her / ask why she is out here / leave her alone. Raises
`attraction` on one branch and `respect` on another; leaving her alone is not
punished.

**Why it exists:** §23. Iris had one storylet and was the most-encountered
character in the game entirely through anchors.

---

## Contended cell: `hallway_east`, midday / afternoon

45,280 selection moments in the baseline with nothing authored at all.

### 7. `hallway_lost_property` — EVENT 40, cooldown 4

**Where:** hallway_east, midday + afternoon.
**Who:** Theo.
**Does:** The lost property box outside the east stairs, which is a crate. Theo
is going through it methodically. Comic, small, and it characterises him as the
person who checks things — which is the same trait that makes him check the
ledger.

### 8. `hallway_after_bell` — EVENT 40, once. **Group scene.**

**Where:** hallway_east, midday + afternoon.
**Who:** Mara **and** June.
**Does:** Mara and June, mid-conversation, stopping when you arrive — the
ordinary version of that, not the sinister one. June is asking Mara for
something. Mara is not saying no in a way that is clearly no.

**Requires:** `seen(mara_reads_the_room)`, because the scene is legible only if
the player has met Mara's flatness once already.

**Choice:** stay / make an excuse / ask what they were talking about. Asking
raises Mara's `suspicion` toward the player and June's `familiarity`, which is a
trade, not a mistake.

---

## Contended cell: `dorm_room`, night / late_night

58,010 baseline moments at late night with nothing authored.

### 9. `dorm_late_night` — AMBIENT 20, repeatable. **Progressive.**

**Where:** dorm_room, night + late_night.
**Who:** nobody named.
**Does:** The room at the hour when the building has gone quiet. Three variants
selected by `seen_count`, not at random: the first is the room being unfamiliar,
the second is the room being a room, the third is the small territorial act of
moving the desk. It reads as time passing rather than as a loop.

**Why written this way:** the Milestone 1 `dorm_message` bug. A repeatable scene
that narrates first-time discovery is wrong on the second visit, and the fix is
variants keyed to how often it has been seen, not a random pick.

### 10. `dorm_corridor_noise` — AMBIENT 20, cooldown 2

**Where:** dorm_room, evening + night.
**Who:** nobody named.
**Does:** Residential life through a wall: somebody's phone call, somebody's
kettle, an argument about a rota. The player is not in it. Two variants.

---

## Contended cell: `town_road`, afternoon / evening / night

### 11. `town_road_shops` — EVENT 40, cooldown 3

**Where:** town_road, afternoon + evening.
**Who:** Mara *or* nobody — she is optional, so this scene stays eligible when
she is not around.
**Does:** The parade of four shops. One sells everything. The others have
opinions about that.

**Choice:** buy something / look at the noticeboard in the window / keep walking.

### 12. `town_road_last_bus` — CALLBACK 60, once

**Where:** town_road, night.
**Who:** nobody named.
**Does:** You are further from the dorms than you meant to be and the last bus
is a real deadline. If a commitment is active, the scene knows.

**Choice:** run for the bus / walk it / call someone. Walking costs a time slot
via `time += 1`, which is the first content in the game where a choice spends
the clock rather than a relationship.

**§54:** this is one of the two scenes where a commitment competes with an
opportunity — the walk is pleasant and it may cost the promise.

---

## Contended cell: `classroom_2b`, early_morning / morning

### 13. `classroom_before_bell` — EVENT 40, cooldown 2

**Where:** classroom_2b, early_morning + morning.
**Who:** June, optional.
**Does:** The room before it is a class. Chairs still up, the radiator, somebody
else's homework left on a desk. Two variants; June appears in one.

---

## Contended cell: `archive_room`, afternoon / evening

The archive already had the most content. These two are here for **competition**
and to exercise the document viewer a second time (§42), not to add mystery.

### 14. `archive_iris_index` — CALLBACK 60, once. **Uses the document viewer.**

**Where:** archive_room, afternoon + evening.
**Who:** Iris.
**Requires:** `knows(iris_keeps_a_second_index)` — the whole scene is the
payoff of the rain conversation.
**Does:** Iris shows the player her own index, which is a card she has been
keeping because the official accession record is not usable. Opens
`accession_record_box_17` in the viewer for a second, different reason.

**Choice:** offer to help maintain it / point out it is unofficial / ask what
she thinks is missing. The last one is where a player who has been paying
attention gets the most, and it grants nothing they could not have inferred.

### 15. `archive_theo_returns` — EVENT 40, once. **Group scene.**

**Where:** archive_room, afternoon + evening.
**Who:** Iris **and** Theo.
**Requires:** `flag theo_lost_something >= 1` — the callback from `gate_waiting`.
**Does:** Theo comes to the archive to return something, or to find something,
and Iris is territorial about the room in a way she has not been with the
player. The player watches two people who both think they are being reasonable.

**Choice:** back Iris / back Theo / say nothing. All three move `rel iris->theo`
or `rel theo->iris`.

**§54:** the second commitment-competes scene — if `meet_theo_archive` is
active, this scene can satisfy it in a worse way than the scene written for it.

---

## Requirement coverage

| Milestone requirement | where |
| --- | --- |
| school_gate no longer empty (§20) | 1, 2, 3 |
| 3+ group scenes (§25) | 5, 8, 15 |
| Iris and Theo get attention (§23) | 3, 6, 7, 14, 15 |
| 5+ delayed callbacks (§31) | 3->15, 8 (needs `mara_reads_the_room`), 14 (needs rain scene), 12 (reads commitments), 2->Noah's gap |
| 2 commitment-vs-opportunity (§54) | 12, 15 |
| Document viewer reused (§42) | 14 |
| Progressive repeatable (§35–37) | 9 |
| Choice spends the clock | 12 |
| Ambient/world scenes | 1, 4, 9, 10 |
