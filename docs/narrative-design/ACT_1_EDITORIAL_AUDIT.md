# Act 1 editorial audit

Every storylet in the game, read as prose rather than as metadata, and
classified. Milestone 4.

The audit is the milestone. What follows the table is more important than the
table: two findings came out of reading all fifty-one that no individual scene
would have shown.

## The two findings

### 1. Relationships were write-only

**Not one line of prose in the game read a relationship value.**

Fifty-one storylets wrote to eight axes across dozens of directed edges. Two
requirement clauses read one. The prose read none. `rel_get` existed and had
zero callers; `is_close`, `is_strained` and `romantic_potential` had zero
callers outside their own tests.

That is the precise shape of "are we building relationships, or merely
accumulating relationship variables". The honest answer before this milestone
was the second one. A player could raise Iris's trust from 0 to 41 across six
scenes and no sentence anywhere in the game would be different.

Fixed: eight scenes now read state, via a small `stance()` reading in the Ren'Py
bridge that answers the human question rather than the numeric one. See
[`RELATIONSHIP_SEMANTICS.md`](RELATIONSHIP_SEMANTICS.md).

### 2. The choices were the same three choices, forty-two times

Every menu in the game, by the traits it offered:

| Trait set | Menus | Scenes |
| --- | ---: | --- |
| `{gentle, curious, reserved}` | 7 | the_common_room, mara_the_long_way, june_the_kitchen, iris_the_second_box, courtyard_lunch_table, iris_outside, town_road_shops |
| `{gentle, curious, direct}` | 7 | theo_the_spreadsheet, iris_the_apology, ellery_the_sign_off, courtyard_the_bench, the_saturday, gate_noticeboard, mara_older_story |
| `{gentle, direct, reserved}` | 7 | common_room_three_way, annexe_two_of_them, june_needs_saturday, gate_waiting, hallway_after_bell, town_road_last_bus, archive_theo_returns |
| everything else | 21 | |

**Three sets accounted for half of all forty-two menus.** 38 of 42 menus had
exactly three options. 21 of 42 offered "say nothing" or its equivalent.

Stated plainly: the game asked the player the same question forty-two times —
*be warm, be nosy, or be quiet* — and dressed it in different scenery. That is
a personality slider, not agency.

The structural shape was even narrower than the trait sets suggest. Thirty-three
of fifty-one storylets were **exactly**: setup, one three-option menu, three
declared outcomes, character leaves. The remaining eighteen were: pick one of
two or three random paragraphs, no choice, no state.

Two scene shapes. Fifty-one scenes.

## What changed

- Choices that decide **information** rather than posture: `message_after_class`
  now decides whether you bring Theo the photograph, and the scene a day later
  reads it.
- Choices that decide **tact** rather than attendance: `iris_outside`'s third
  option was declining the scene; it is now sitting down and deliberately not
  raising the thing she just told you.
- **Two-option menus where the third was filler**: `gate_noticeboard`,
  `town_road_shops`. Both third options were one line, no state, no
  characterisation.
- **Choice text is behaviour, not a label**: "Leave him to it" became "Say
  something ordinary and go through the gate"; "Leave it" became "Go back to the
  boxes you do have keys for".

What was *not* done: adding a fourth option everywhere. The problem was never
the count.

## The table

`KEEP` means read in full and left alone. It is not a shrug.

| Storylet | Verdict | Why |
| --- | --- | --- |
| `archive_intro` | KEEP | Six lines, no menu, and correct: it is the job being explained, and the document does the work. |
| `archive_iris_index` | KEEP | The second index, and the viewer's second use. Strong. |
| `archive_theo_returns` | REVISE_LIGHT | Now reads `iris->theo` and `theo->iris` — the one place an NPC-to-NPC edge is visible. |
| `annexe_door` | REVISE_LIGHT | "Leave it." renamed to the behaviour. |
| `annexe_two_of_them` | KEEP | The sharpest fork in the game. Both are right about something. |
| `classroom_before_bell` | KEEP | |
| `common_room_evening` | KEEP | |
| `common_room_kettle` | KEEP | The laminated sign is recurring-detail material. |
| `common_room_three_way` | REVISE_MAJOR | Was round-robin: A speaks, B speaks, C speaks. Now people collide, talk past each other, and Theo logs a defect at a rota. |
| `courtyard_lunch_table` | KEEP | |
| `courtyard_morning_queue` | KEEP | |
| `courtyard_small_talk` | **REVISE_MAJOR** | The thinnest scene in the game and the second most played: three interchangeable jokes about a card game, a vending machine and two crows, five times a run, saying nothing about anybody. It now reads which people the player has got close to and hands their week back to them. |
| `courtyard_the_bench` | KEEP | |
| `dorm_bathroom_queue` | KEEP | |
| `dorm_corridor_noise` | REVISE_LIGHT | Its rota variant now collides with two better rota scenes. |
| `dorm_early_start` | KEEP | |
| `dorm_late_night` | REVISE_LIGHT | Nine plays a run, the largest block of repeated text in the game. Given a coda that is the week rather than the room, keyed to open promises and to who the player is close to. |
| `dorm_message` | KEEP | Still the best-guarded scene in the project. |
| `ellery_the_sign_off` | KEEP | |
| `gate_early_arrival` | KEEP | |
| `gate_going_out` | KEEP | The sign-out book. Earns its read. |
| `gate_noticeboard` | REVISE_LIGHT | Third option cut. |
| `gate_waiting` | REVISE_LIGHT | Choice text renamed to behaviour. |
| `hallway_after_bell` | **REVISE_MAJOR** | Absorbed the Saturday commitment (see the cut below). Two branches now include the player in the trip; the third gets it explained to them and leaves them out. |
| `hallway_afternoon_drift` | KEEP | |
| `hallway_encounter` | **REVISE_MAJOR** | Eight lines and no choice: the only scene in the game with no agency at all. Mara describes Theo's long way round from outside; this is now the inside of the same observation, and at high familiarity the player walks it with him. |
| `hallway_lost_property` | KEEP | |
| `iris_outside` | REVISE_LIGHT | Third option was declining the scene. |
| `iris_the_apology` | KEEP | Her boundary, from the inside. |
| `iris_the_second_box` | **REVISE_MAJOR** | Three relationship states. `wary` is not a colder version — it is the same invitation extended by somebody who decided to extend it anyway. |
| `june_reads_it_flat` | REVISE_MAJOR | Reads `stance("june")` for the opening and `player->june.respect` for why the argument lands. Rule R5 with a memory. |
| `june_the_favour` | KEEP | The "I had a whole second half" beat is the best single line June has. |
| `june_the_kitchen` | KEEP | |
| `june_welcome_pack` | KEEP | |
| `june_needs_saturday` | **CUT** | See below. |
| `mara_older_story` | KEEP | |
| `mara_reads_the_room` | KEEP | |
| `mara_the_long_way` | REVISE_MAJOR | A `wary` Mara still takes the long way and turns the whole walk into a tour of things rather than a conversation. |
| `message_after_class` | **REVISE_MAJOR** | Five lines and a two-option menu in which both options meant "keep the note". Now decides whether you bring Theo the photograph, and `theo_ledger_question` reads it a day later. |
| `noah_asks_for_access` | KEEP | |
| `noah_evening_layout` | KEEP | The guarded callback still works. |
| `noah_the_sports_report` | KEEP | |
| `old_photo_glimpse` | KEEP | |
| `rain_after_school` | KEEP | Two menus, which makes it the most structurally unusual scene in the game, and it is one of the best. Reachability remains its problem, not its writing. |
| `the_saturday` | REVISE_MAJOR | June at the gate now reads `stance("june")`: a `wary` June says "You came" and means it as a receipt. |
| `theo_admits_it` | REVISE_MAJOR | Reads `theo->player.resentment`. High trust plus resentment is a person confiding in somebody they have not forgiven. |
| `theo_ledger_question` | REVISE_LIGHT | Pays off the photograph decision at one day's distance. |
| `theo_the_spreadsheet` | KEEP | |
| `town_road_evening_walk` | KEEP | "Everyone waves. Nobody has decided to stop." is the best line about the place in the game. |
| `town_road_last_bus` | KEEP | |
| `town_road_shops` | REVISE_LIGHT | Third option cut. |
| `the_common_room` (anchor) | REVISE_MAJOR | Was round-robin. Now interruptions, an unacknowledged contribution, and a conversation conducted entirely by moving a mug four inches. |
| `the_undated_column` (anchor) | KEEP | |
| `the_date` (anchor) | KEEP | |
| `arrival`, `first_shift` (anchors) | KEEP | |

## The cut

**`june_needs_saturday` — CUT.**

`hallway_after_bell` is a scene in which the player walks in on June negotiating
a lift into town on Saturday out of Mara. Milestone 3 then wrote a *second*
scene in which June asks the player about the same Saturday, from scratch, as
though the first had not happened.

Two scenes, one event, and the second one existed only to create a commitment.
That is the function-repetition failure exactly: a scene whose reason to exist
is structural rather than dramatic.

The commitment now lives in `hallway_after_bell`, where it costs something. Two
of its three branches get the player included in the trip; the third gets the
whole arrangement explained to them at length and leaves them out of it, and
June withdraws the invitation inside the sentence she offers it in.

That is a better scene *and* one fewer scene.

## Counts

| Verdict | Storylets |
| --- | ---: |
| `KEEP` | 33 |
| `REVISE_LIGHT` | 8 |
| `REVISE_MAJOR` | 9 |
| `MERGE` | 1 (into `hallway_after_bell`) |
| `CUT` | 1 |
| `NEW` | 8 |

51 → **58**.

The number is at the bottom of the 58–65 range on purpose. Eighteen scenes were
revised and one was cut; the milestone spent its effort on the fifty-one that
existed, which is what it was for.

## What the new eight are for

Every one names a thing the audit found the week could not do. None was written
to fill a cell.

| New storylet | The gap |
| --- | --- |
| `iris_the_wrong_photograph` | Iris existed only in and around the archive, which makes her the girl from the photograph rather than a person. |
| `mara_is_wrong` | Mara read people accurately in every scene she had. Nothing had ever shown her confident, specific and wrong — which turns her judgement into a mechanic. |
| `theo_the_quiz` | Theo had method and no ego. A rationalist with no vanity is a device. |
| `june_is_not_fine` | Every June scene showed her handling something for somebody else. Nothing put the player in a position to notice being deflected. |
| `noah_takes_a_call` | Three readings of Noah must survive Act 1; the evidence for "he is avoiding something unrelated" was its absence. |
| `ellery_and_the_form` | Ellery's function, decided: a wall made entirely of reasonable things, which no student character can be. |
| `courtyard_before_you` | The protagonist walked into a community that already existed and the game never showed one. |
| `classroom_the_lesson` | A game set at a school with no lessons in it. |
