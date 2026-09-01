# Milestone 4 — Act 1 narrative depth, and the first playable draft

**Verdict: PASS WITH CONCERNS.**

Act 1 is now coherent enough to justify a real human playtest, which is the
milestone's stated bar. The concerns are that nobody has read it yet, and that
the two most important questions — whether these people are likeable and whether
the jokes land — are not questions a machine can answer about its own prose.

All figures: 5000 runs, seed 1234.

---

## Editorial audit

Every one of the fifty-one existing storylets read as prose and classified.
Full table and reasoning:
[`ACT_1_EDITORIAL_AUDIT.md`](../narrative-design/ACT_1_EDITORIAL_AUDIT.md).

| Verdict | Storylets |
| --- | ---: |
| `KEEP` | 33 |
| `REVISE_LIGHT` | 8 |
| `REVISE_MAJOR` | 9 |
| `MERGE` | 1 |
| `CUT` | 1 |
| `NEW` | 8 |

**Before: 51. After: 58.** Deliberately at the bottom of the 58–65 range. The
milestone's instruction was to revise more than expand and it did: eighteen
scenes changed, one was cut, eight were added.

### The cut

**`june_needs_saturday`.** `hallway_after_bell` is a scene in which the player
walks in on June negotiating a lift into town on Saturday out of Mara. Milestone
3 then wrote a second scene in which June asks the player about the same
Saturday from scratch, as though the first had not happened.

Two scenes, one event, and the second existed only to create a commitment. The
commitment now lives in the group scene where it costs something: two branches
get the player included in the trip, and the third gets the whole arrangement
explained to them at length and leaves them out of it — June withdraws the
invitation inside the sentence she offers it in.

One fewer scene and a better one.

### The two findings that reading all fifty-one produced

Neither is visible in any individual scene, which is why the audit was the
milestone rather than a preliminary to it.

**1. Relationships were write-only.** Not one line of prose in the game read a
relationship value. Fifty-one storylets wrote to eight axes across dozens of
directed edges; two requirement clauses read one; the prose read none. `rel_get`
had zero callers. `is_close`, `is_strained` and `romantic_potential` had zero
callers outside their own tests.

A player could take Iris's trust from nought to forty-one across six scenes and
not one sentence anywhere in the game would be different. That is the precise
shape of *accumulating relationship variables* rather than *building
relationships*, and the honest answer before this milestone was the former.

**2. Half of all forty-two menus were the same three choices.**

| Trait set | Menus |
| --- | ---: |
| `{gentle, curious, reserved}` | 7 |
| `{gentle, curious, direct}` | 7 |
| `{gentle, direct, reserved}` | 7 |
| everything else combined | 21 |

38 of 42 menus had exactly three options. 21 of 42 offered "say nothing" or its
equivalent. The game asked the same question — *be warm, be nosy, or be quiet* —
forty-two times in different scenery.

Worse, the structural shape was narrower still: **33 of 51 storylets were
exactly** setup → one three-option menu → three declared outcomes → character
leaves. The other eighteen were: pick one of two or three random paragraphs, no
choice, no state. Two scene shapes, fifty-one scenes.

Both findings are now held by tests in `tests/test_act1_depth.py`.

---

## Character arcs

Full matrix: [`ACT_1_CHARACTER_ARCS.md`](../narrative-design/ACT_1_CHARACTER_ARCS.md).
Every entry passes the test *the character wants something today, and it is not
"solve September 32"*.

| | Wants this week | Turning point | Stays hidden |
| --- | --- | --- | --- |
| **Iris** | The second index looked at properly by somebody who is not her | `iris_the_second_box` — she has started it, four cards against two hundred and six boxes | Why it matters to her |
| **Mara** | The town understood correctly, without being asked to perform it | `mara_is_wrong` — confident, specific, and wrong | Why she stays |
| **Theo** | Column J full, and to not be told he is overthinking it | `theo_admits_it` — he marked a box `seen` that he had not seen | What was filed wrongly before |
| **June** | A birthday nobody noticed to get noticed; a phone call to be four o'clock's problem | `june_reads_it_flat` — she argues the ordinary reading, well | What she transferred away from |
| **Noah** | Eight centimetres for the third column; twenty minutes with a camera | `annexe_two_of_them` — he and Iris are both right | Why it matters that it be him |
| **Ellery** | To sign the sheet on Thursday | Function decided: a wall made entirely of reasonable things | Nothing — she is not hiding anything, and canon is explicit |

**Protagonist.** Documented for the first time:
[`PROTAGONIST.md`](../characters/PROTAGONIST.md). Five characters had carefully
differentiated bibles while the sixth voice — 68% of the game's words — was
written by instinct.

---

## Character voice

The fingerprints in `VOICES.md` turn out to be **measurably present**, which was
not guaranteed:

| Speaker | Lines | Words | Words per line |
| --- | ---: | ---: | ---: |
| narrator | 572 | 12,684 | 22.2 |
| Ellery | 23 | 336 | **14.6** |
| June | 111 | 1,263 | 11.4 |
| Iris | 115 | 1,226 | 10.7 |
| Noah | 89 | 884 | 9.9 |
| Theo | 100 | 932 | 9.3 |
| Mara | 94 | 833 | **8.9** |
| the player, aloud | 102 | 445 | **4.4** |

That ordering is the bible: Mara flat and shortest, Theo full stops where others
use commas, June fluent, Ellery explaining institutions at length. The
protagonist's 4.4-vs-22.2 gap is the documented *"four words out loud, wry on
the page"*, and it is real rather than aspirational.

**Humour was audited for sameness**, which is the AI failure mode: Iris is
deadpan about her own oddness, Mara is dry and easy to miss and always about the
town, June jokes first and generously, Theo is funny by accident and does not
know it, Noah is funny on purpose and slightly too pleased. **Whether any of it
is funny is not a claim this document makes.**

---

## Relationship depth

Nine scenes now behave differently depending on relationship state. Five, with
what is actually visible:

**1. `iris_the_second_box` — `trust` high, `suspicion` high**

*State:* she trusts you enough to reach this scene and you told Noah about the
photograph, or took Noah's side in the corridor.
*Visible:* the shoebox is on the desk and she does not move it toward you and
does not move it away, and you can see the shape of the deciding in how
deliberately she is not looking up. She extends the invitation anyway. Later,
she checks two of your cards early on and none after that, and neither of you
mentions the checking.

**2. `theo_admits_it` — `trust` ≥ 8, `resentment` ≥ 4**

*State:* he trusts you, and you told him a script could do his job in a weekend.
*Visible:* he opens with *"I'm telling you this because you'll be unbearable
about it if you find out on your own"*, and then *"That's not why."* / *"No."*
A person confiding in somebody they have not forgiven.

**3. `mara_the_long_way` — `familiarity` high, `trust` low**

*State:* she knows you and you pressed her about the town on the road.
*Visible:* she still takes the long way. She names four more things without
being asked about any of them and says nothing about herself, and about halfway
you notice it is a tour rather than a conversation and that she could keep it up
for an hour. The gentle branch gets *"I go this way sometimes"* instead of
*"No."*

**4. `the_saturday` — `familiarity` high, recently let down**

*State:* she has been let down before — the favour, or a message left until
morning.
*Visible:* *"You came." / "I said I would." / "You did say that."* Warm, and a
receipt, and both at once.

**5. `courtyard_small_talk` — who the player is close to**

*State:* the set of characters at `comfortable` or better.
*Visible:* with nobody, you watch two crows argue on a bike rack for longer than
you would admit to. With somebody, they hit the vending machine once in the
specific place and keep walking without looking back, and you realise you have
watched somebody do that this week and did not register learning it.

Also: `june_reads_it_flat` reads `player->june.respect`;
`archive_theo_returns` reads `iris->theo` and `theo->iris` — the one place an
NPC-to-NPC edge is visible to the player; `dorm_late_night` reads open
commitments and close friendships; `hallway_encounter` reads Theo's familiarity
and lets the player walk the long way round with him.

Semantics documented:
[`RELATIONSHIP_SEMANTICS.md`](../narrative-design/RELATIONSHIP_SEMANTICS.md).

---

## Callbacks

| Earlier choice | Delay | Later effect |
| --- | --- | --- |
| Put the photograph in your bag when the note asks for it | ~1 day | Theo does not thank you and moves the ruler to make room, which is the same thing. Or: *"You didn't bring it." / "That's fine. That's actually the right instinct."* — and he does not sound as though it is fine |
| Tell Noah about the unlisted photograph | 2–4 days | Iris reaches `wary`, and `iris_the_second_box` becomes a different scene |
| Watch June organise a birthday nobody noticed | 2–3 days | `june_reads_it_flat`: *"You have watched her do this before, with a rota and four minutes, and it worked then too"* |
| Tell Theo a script could do his job in a weekend | 3–4 days | He opens `theo_admits_it` by pre-empting you |
| Break the promise made in `hallway_after_bell` | ~3 days | The car goes and nobody in it looks back, which is worse than somebody looking back |
| Say nothing when Mara is wrong | open-ended | *"You will be listening differently to the next thing she tells you about somebody, and she will have no idea"* |
| Take somebody's side in `annexe_two_of_them` | same scene | `noah->iris` and `iris->noah` move in opposite directions |

Seven, at distances from same-scene to open-ended. None is announced.

---

## Act 1 mystery

Full ledger with ordinary explanations:
[`ACT_1_MYSTERY_LEDGER.md`](../narrative-design/ACT_1_MYSTERY_LEDGER.md).

Typical acquisition order for the `curious` profile, by kind:

| | Kind | Entry |
| ---: | --- | --- |
| Day 1 | `FACT` | The bound volumes were moved to the annexe (a notice in a glass case) |
| Day 3 | `FACT` | The school history skips a year (June's booklet) |
| Day 4 | `FACT` | A column with entries and no date — **anchor, phase turns** |
| Day 4 | `BELIEF` | Iris: *"somebody was interrupted"*, and it is almost certainly right |
| Day 5 | `FACT` | The annexe is locked and the office has no key |
| Day 5 | `SUSPICION` | Mara: somebody could have faked a stamp on a photograph |
| Day 5 | `INTERPRETATION` | June: nobody writes the date for themselves, you write it for the person in forty years |
| Day 6 | `FACT` | Theo lost the annexe key; he was signed it out in March |
| Day 7 | `FACT` | The stamp — **anchor, phase does not move** |

| | Act 1 |
| --- | ---: |
| Things that objectively exist | 8 |
| With an ordinary explanation stated by a character, in the scene | 7 |
| That prove anything on their own | **0** |
| That the game confirms are connected | **0** |

Two of the eight are year-long gaps a player will want to be the same gap, and
the game will not say. `photo_is_a_forgery` is only ever granted as `suspected`,
never `known`, and it contradicts `photo_dated_sept_32` — a player can end the
week holding both.

**Questions grow faster than answers**, and every ordinary explanation offered
is still standing at the end of the week.

---

## Day 7 hook

*Why should this evidence matter to this protagonist after this week?*

By Day 7 the player has been in the archive at least twice, has read the ledger
page in the viewer themselves, holds `attendance_sheet_anomaly` in 100% of runs,
and has had at least one character offer an ordinary explanation for it and
probably be right.

The stamp then does not contradict anything on its own — the scene is explicit
that a franking machine has little wheels and the wheels turn, and that somebody
set one a click too far and went to lunch. What it does is give the player a
*second* document, and the scene says the quiet part: this explanation covers
the stamp and does not cover the column, and you now have two things instead of
one.

**Nobody reads the number aloud.** Not the protagonist, not Iris, not Theo. The
prose says only *"the number after the month is not a number that month has"* —
because a character saying "thirty-two" would be the scene deciding canon that
`SEPTEMBER_32.md` has deliberately left open.

The target is *"I want to see what happens tomorrow"*, not a jumpscare. The phase
does **not** advance: Act 1 ends inside `odd`, holding two records and no account
covering both.

**What is not yet earned is the weight.** The strongest version of that scene is
a player who has spent the week with Iris, finding it in a room they now care
about — and about half of runs do not have that relationship. That is the
argument the human review has to settle.

---

## Representative runs

Five profiles, seed 1234, seven days. Readable transcripts in
`tools/reports/m4/playthrough_*.md`.

| | Closest | Most strained | Promise | Mystery exposure | Leans toward |
| --- | --- | --- | --- | --- | --- |
| `curious` | Iris (trust 14, fam 18) | Mara — barely met her | one active, one expired | **8 facts** | Something is off in the records |
| `romantic` | June (trust 25, fam 24), Iris (trust 23, attr 10) | — | — | **4 facts, fewest** | Barely engaged with it |
| `altruistic` | June (fam 28), Theo (fam 19) | Mara→June suspicion 4 | kept | 4 facts | Trusts June's reading |
| `paranoid` | Mara (respect 12) | `player->mara.suspicion 3` | — | 6 facts | Watching people, not documents |
| `selfish` | — | — | broken | 7 facts inc. the annexe | Took what was useful |

Shared: **10 scenes of 44** across five profiles (23%). With three profiles it
was 37%, matching Milestone 3.

**Do they feel like different versions of the same week?** Yes. All five arrive,
take the first shift, sit in the common room, find the column and read the
stamp, and end in `odd`. What differs is everything else — and the `romantic`
run is the striking one: it ends the week with the *fewest* facts and the
strongest relationships, which is the design working. A player who spends the
week on people gets a complete experience, not a lesser one.

---

## Narrative metrics — regression only

Not the verdict. Recorded to show the revision pass cost nothing.

| | M3 (51) | **M4 (58)** | |
| --- | ---: | ---: | --- |
| Reachable | 51/51 | **58/58** | — |
| Dead ends | 0 | **0** | — |
| Anchors in 100% of runs | 5/5 | **5/5** | — |
| Nothing eligible | 27.4% | **25.9%** | better |
| Productive singleton | 44.5% | **39.0%** | better |
| Raw 2+ eligible | 40.5% | **45.2%** | better |
| Top-tier 2+ | 28.2% | **34.9%** | better |
| Unique scenes per run | 38.0 | **41.0** | better |
| Repeats per run | 32.1 | **31.0** | better |
| Top scene share | 13.1% | **12.7%** | better |
| Top three share | 27.8% | **26.4%** | better |

Every metric improved, including in a milestone that cut a scene. No regression
was accepted and none was needed.

Content mix: `slice_of_life` 92.8%, `school` 61.0%, `character` **35.7%**,
`friendship` **23.4%**, against `investigation` 7.9%, `archive` 7.5%,
`mystery` 7.3%. More slice-of-life than the pacing budget requires, which is
correct for a game where ordinary life is what the horror is about.

---

## Writing metrics

| | |
| --- | ---: |
| Total prose words | **18,667** |
| Spoken/narrated lines | 1,212 |
| Narration share | **67.9%** |
| Estimated reading time, whole library | ~75 minutes |
| Words in an average first week | ~9,000–11,000 |

Storylets featuring each character: Iris 10, Theo 9, June 9, Noah 7, Mara 7,
Ellery 2, no character 21.

**No gross imbalance.** The five leads sit between 4.5% and 6.8% of spoken
words, which is closer than intended and was not equalised deliberately.

**The one imbalance that matters** is that narration is 68% of the game and had
no bible until this milestone. That is now
[`PROTAGONIST.md`](../characters/PROTAGONIST.md), and it is the document most
likely to change what future scenes sound like.

---

## AI-writing review

Found and corrected:

- **The `which is` gloss.** A clause appended to an image telling the reader what
  it meant. Trimmed across three milestones now; the remaining density (13 in 531
  lines in the new file) is proportionate and most instances do real work.
- **Two narrator glosses in new prose** — *"which is her way of saying thank you
  and is not going to be acknowledged as one"* explained the emotional meaning
  of a scene that had just performed it.
- **Round-robin group scenes.** `the_common_room` and `common_room_three_way`
  were A-speaks, B-speaks, C-speaks. Now: June interrupted mid-word, Theo
  contributing and going unacknowledged, two people arriving at the ends of
  their sentences a second apart, and Mara and Theo conducting an entire
  exchange by moving a mug four inches.
- **Opt-out choices.** Seven "leave it / walk on / keep walking" options. Two
  were cut outright (one line, no state, no characterisation), two renamed to
  the behaviour, one rewritten into a real choice about tact.
- **Choice text as moral label.** `[Be kind to Iris]` shapes replaced with the
  actual action.

Scanned for and **not found**: *for some reason*, *couldn't shake*, *a chill
ran*, *little did*, *sent a shiver*, *an odd feeling*. Zero instances across
1,212 lines.

**Not corrected, and flagged:** whether the humour is funny, whether the romance
reads as chemistry, whether the narration is enjoyable across 12,700 words.
These went to human review.

---

## Continuity

Two faults found by the checklist, both mine, both in Milestone 3 prose:

| Scene | Fault |
| --- | --- |
| `iris_the_second_box` | Opened on *"not where it was and not how it was"* while gated only on `knows(iris_keeps_a_second_index)`. Knowing *about* the box is not having seen it — only one of three branches of `archive_iris_index` mentions it. |
| `june_reads_it_flat` | Closed on *"it is canals again"*, a callback to one of three variants of a scene the player may never have played. |

Both were fixed in Milestone 3's own pass; recorded here because the rule they
produced is the durable output: **a scene's requirement is the guarantee, not the
vibe.**

Milestone 4 added emotional continuity to the audit — trust trajectory,
resentment, recent commitments — which is what the nine state-reading scenes are
for. A character no longer acts intimate immediately after a scene in which the
relationship was distant, because the scene checks.

---

## Art production

Moved from a standing note to a plan:
[`ART_PRODUCTION_PLAN.md`](ART_PRODUCTION_PLAN.md). Eleven gaps, tiered.

| Tier | Items |
| --- | --- |
| **P0** | The class photograph |
| **P1** | Ms. Ellery; a male-presenting sprite in A01's style; the archive room background |
| **P2** | Casual outfits for Mara/June/Noah; Iris with a camera; Theo with the ledger; the town exterior |
| **P3** | Key art; paper textures (**done**, deterministic, in-house) |

**Class photograph — `COMMISSION REQUIRED`, P0.** The object the premise turns
on. Currently an `image_placeholder` reading *CLASS PHOTOGRAPH — ART PENDING*
inside a plausible archival mount. Cannot be generated, cannot be a stock
photograph of real people, cannot be borrowed. Brief written:
[`CLASS_PHOTO_ART_BRIEF.md`](CLASS_PHOTO_ART_BRIEF.md) — composition, the
hand-trimmed mount edge, the stamp as a separable layer with the numerals
omitted so the project can set them without a re-commission, and an explicit
list of what must *not* be visible (no figure at the back, no gap in the row —
the photograph's only strangeness is the stamp).

**Male-presenting compatible sprite — `COMMISSION REQUIRED`, P1.** Two packs
audited at 3.4/10 and rejected. The cast is one presentation *because of asset
availability*, which is not a design decision, and continuing not to decide is
itself a decision being made by default. Brief written:
[`CHARACTER_ART_BRIEF.md`](CHARACTER_ART_BRIEF.md).

**Ms. Ellery — `COMMISSION REQUIRED`, P1.** Written off-sprite twice now. **This
is the finding that changed the policy**: in Milestone 3 a missing sprite moved
a character off stage, which is the moment an art gap stops being visual and
becomes a writing problem. The placeholder policy gained the rule it was
missing — *a missing sprite may not change the writing* — and the two Ellery
scenes are logged as the standing exception rather than the precedent.

**Zero assets downloaded this milestone**, which was the intended outcome.

---

## Tests

| Gate | Result |
| --- | --- |
| `uv run s32 doctor` | 0 failures, 0 warnings |
| `uv run s32 validate` | 0 errors, 0 warnings, 9 info |
| `uv run ruff format --check .` | clean |
| `uv run ruff check .` | clean |
| `uv run mypy` | clean, 72 files, strict |
| `uv run pytest` | **236 passed** |
| `uv run s32 schemas --check` | clean |
| `uv run s32 assets credits --check` | clean |
| `uv run s32 assets verify` | clean |
| `uv run s32 renpy lint` | clean |
| `uv run s32 renpy test` | **16/16 testcases** |
| `uv run s32 simulate --runs 5000` | 58/58 reachable, 0 dead ends |
| `scripts/check.py` | **11/11** |

222 → 236 (+14), all in `tests/test_act1_depth.py`. They hold the two audit
findings rather than the prose: that the named scenes read relationship state,
that no single trait set takes more than 20% of menus, that menus are not all
one size, that choice text is behaviour rather than a label, that every stance a
scene branches on is reachable in a real run, and that declared outcomes still
match the menus after two options were trimmed.

**Testcase discovery**, fixed in Milestone 3, is still discovery — 16 cases
found by walking `game/testcases/`, not a hand-written list.

---

## Architecture changes

**`NarrativeDirector` selection algorithm: UNCHANGED.** Byte-identical to
Milestone 1. Four milestones of pressure and it has not needed changing.

No new subsystem. The only engine-adjacent addition is three reading helpers in
the Ren'Py bridge (`stance`, `regards`, `player_regards`) that wrap `rel_get`,
which already existed and had no callers.

| Change | Kind |
| --- | --- |
| `game/engine/00_s32_engine.rpy` — `stance` / `regards` / `player_regards` | Bridge helpers over existing engine functions |
| Nine `.rpy` scenes read relationship state | Content |
| Two group scenes de-round-robined | Content |
| One scene cut, one commitment relocated, two menu options trimmed | Content |
| `scripts/first_week.py` — `--markdown-dir` | Tooling |
| Nine new documents | Docs |

Nothing in `s32_engine/` changed at all.

---

## Git

Four commits this milestone, on `main`, local only.

```
78f1718  content: cut a redundant scene, and add eight for gaps the audit named
708147b  docs: audit every scene, and turn the art gap into a production plan
92da074  content: make relationships visible in behaviour rather than in variables
```

(plus the closing commit carrying this report.)

Working tree clean. **Nothing pushed. No co-authors. No history rewritten.**

---

## Human review queue

Thirteen scenes, in priority order, with a specific question for each:
[`HUMAN_ACT1_REVIEW.md`](HUMAN_ACT1_REVIEW.md). About forty minutes of reading.

Top five: `mara_is_wrong`, `june_is_not_fine`, `the_common_room`,
`theo_the_quiz`, `iris_the_second_box`.

The scene I am least confident about is `noah_takes_a_call` — it exists to keep
alive the reading that Noah is avoiding something *unrelated*, and the risk is
that a phone call he does not want to take reads as a clue no matter how
ordinary the prose makes it, in which case it achieves the opposite of its
purpose and should be cut.

---

## Honest Act 1 verdict

### 1. Would a player care about the characters without the mystery?

**PARTIALLY.**

The material is there and it is measurably differentiated: five voices with
distinct sentence lengths matching their bibles, one non-mystery scene each plus
a second for most, an ego for Theo, a wrongness for Mara, a deflection for June,
a phone call for Noah, a shoe photographed on two different days for Iris. Two
of the five now have a scene the mystery could be deleted from entirely without
changing anything.

It is `PARTIALLY` because *likeable* is not a property I can verify about my own
prose. The competence is not in doubt and competence is precisely the failure
mode of machine-written fiction. Somebody has to read it and want to keep
reading.

### 2. Is the mystery escalation compelling without being premature?

**YES.**

Eight things exist; seven have an ordinary explanation offered by a character
inside the scene; none proves anything alone; the game never confirms any two
are connected. The phase turns on the weakest available evidence — a column with
no date, explained by Iris in the same breath, and she is probably right. Days 1
to 3 contain no mandatory mystery content. `mystery` is 7.3% of played scenes
against 92.8% slice-of-life.

The `romantic` run ends the week with four facts and the strongest relationships
in the sample, which is the clearest evidence that a light-touch player gets a
complete experience.

### 3. Do choices create noticeably different emotional weeks?

**YES.**

Five profiles share 23% of their scenes. `romantic` ends with the fewest facts
and the deepest relationships; `curious` with eight facts and Mara barely met;
`selfish` with the annexe information and a broken promise; `paranoid` watching
people rather than documents. Nine scenes now read state and play differently.
Seven callbacks fire at distances from same-scene to open-ended.

The qualifier is that this is measured on scene identity and end state — what a
tool can see. Whether three people would *feel* they had different weeks is the
reading question, and it is item zero on the human queue.

### 4. Does Act 1 deserve a real human playtest?

**YES.**

It has a shape (seven days, five anchors, a beat each), an ending that creates
curiosity rather than confusion, a cast with lives outside the plot, choices
that echo, and relationships that change behaviour rather than only numbers.
Every gate is green and every intended scene is reachable.

More to the point: **the remaining questions cannot be answered any other way.**
Whether these people are likeable, whether the jokes land, whether the week is
enjoyable to live through — four more milestones of machine revision would not
settle any of them, and would risk polishing prose nobody has confirmed is worth
polishing.

That is what makes this a `PASS`, and the `WITH CONCERNS` is that nobody has
read it yet.

---

## Next milestone

**Recommended: Milestone 5 — human playtest prep and Act 1 polish.**

Not a scale to 80–100 storylets. The density metrics do not call for it and the
prose has not been validated by a person.

Milestone 5 would be: a playtest build, lightweight feedback instrumentation,
save compatibility, the bugs a real player finds in the first twenty minutes,
and the art replacement priorities in `ART_PRODUCTION_PLAN.md` order.

Only after human feedback should Act 2 scale.

If the human review comes back negative on questions 1 or 3, the correct
response is another narrative pass on the specific scenes named — not more
scenes.
