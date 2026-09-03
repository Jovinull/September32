# Milestone 5 — human playtest build and feedback pipeline

**Verdict: READY WITH CONCERNS.**

The build exists, it can be handed to a person with one sentence, and it plays
Act 1 from the school gate to the end of the week. The concerns are named in
full below and none of them is a reason to wait.

---

## The finding that defined the milestone

**Act 1 was not playable.**

The game's `start` label called two anchors, ran six time slots, and stopped on
a line saying it was a prototype. The other three anchors — the common room, the
undated column, and the date the act is named for — had never once fired outside
the headless simulator. Fifty-eight storylets and a seven-day structure were
reachable on paper and unreachable in the game.

Every gate was green throughout, and each of them was answering a question that
was not this one:

| Gate | What it reads |
| --- | --- |
| `s32 validate` | storylet metadata |
| `renpy lint` | images, labels, references |
| `s32 simulate --runs 5000` | storylet *definitions*; never opens a `.rpy` |
| `s32 renpy test` | the first two scenes |
| `pytest` | the engine, the containers, the content graph |

Nothing anywhere asked whether the game reaches its own ending.

Had this milestone produced only documents and a build, five testers would have
received a ten-minute prototype, met two characters, seen none of the mystery,
and been handed a questionnaire in which almost every question was unanswerable.

`game/story/act1.rpy` is the loop that fixes it. It does what the simulator has
always modelled, with the two decisions the simulator makes for the player
handed back: anchors first, then the director, and the player choosing where to
be three times a day and whenever the room empties. It ends when `the_date`
fires.

Nothing in it scores, filters or re-picks a storylet — held by a test, because
the loop is the newest place the selection algorithm could start to leak into.

---

## Build

| | |
| --- | --- |
| Version | `0.2.0-playtest.1` |
| Build id | derived from the commit, first eight characters |
| Commit | recorded in `game/build_stamp.json` and shown on the main menu |
| Platform | Windows (`pc`), which also produces the Linux payload |
| Archive | `dist/September32-Act1-Playtest-0.2.0-playtest.1-pc.zip` |

The register — size, SHA-256, who received which build — lives in
[`PLAYTEST_BUILD.md`](PLAYTEST_BUILD.md) and is filled in at the moment a build
is produced, not here.

**On the version.** The brief suggested `0.0.5-playtest.1`. Not used: it sorts
*before* the `0.1.0-prototype` it succeeds, and a version that goes backwards is
one nobody can reason about later. `0.2.0-playtest.1` keeps the project's
existing convention and increments if a second build has to go out mid-wave.

Three things the build does that Ren'Py's own `distribute` does not, each of
which would otherwise fail silently:

**It brings the content.** `data/` sits beside `game/` in the repository. A
distribution has no repository, so the build mirrors it into `game/data/`.
Without this the built game loads zero storylets and the director selects
nothing — not a crash, and therefore something that reaches a tester.

**It names itself.** `game/build_stamp.json`, read back at init. A bug report
that says "the one you sent me" is worth very little.

**It leaves the repository behind.** The base directory Ren'Py scans is a
working repository, and Ren'Py's own rules end with a catch-all. Without the
exclusions a tester would receive the canon, the briefs, the internal reports,
every scene card and every milestone post-mortem — including this one.

`tests/test_playtest_build.py` lists the repository root and fails on an entry
no rule accounts for, so a directory added next year is a red test rather than a
leak.

---

## Story content

```
Before:  58
After:   58
```

No scene was written, cut, merged or rewritten. **Two new lines of prose exist
in the whole milestone**, both in the week loop:

- "The hour goes by without asking anything of you." — for a slot where nowhere
  in the world has anything, so no menu is offered
- "A column with no date in it. A date that is not a date. An ordinary account
  of each, and neither of them survives being put next to the other." — the
  act's closing line

Plus the day card, which is a weekday and a date and nothing else.

The opening at the gate, "You walk for a while without deciding to", "The room
came furnished" and "Tomorrow there will be more boxes" all moved across from
the deleted prototype file unchanged.

**One continuity bug fixed while moving them.** The closing beat first read
"You put the two of them side by side on the desk", which assumes the player is
carrying both — and the third branch of `the_date` has them put the photograph
back under the programmes, while the attendance sheet is a document in the
archive and never leaves it. The same class as the three callbacks earlier
milestones caught by reading the prose against the requirements, and caught the
same way.

`game/story/prototype/00_start.rpy` was deleted. It held the six-slot loop, the
wander, and the prototype ending; keeping it would have meant two `label start`
definitions, which is a Ren'Py error.

**`noah_takes_a_call`: core ambiguity preserved — YES.** Not touched. Not a
typo, not a line, not a stage direction. Its decision rule is written down in
[`SCENE_REVIEW_GUIDE.md`](../playtest/SCENE_REVIEW_GUIDE.md) §12 *before* any
tester has seen it: if most testers who saw the scene name it as their reason
for suspecting Noah, cut it — do not soften it, because softening produces a
different scene and destroys the comparison.

---

## Playtest hypotheses

Nineteen, in
[`ACT1_PLAYTEST_HYPOTHESES.md`](../playtest/ACT1_PLAYTEST_HYPOTHESES.md), each
with what supports it, **what contradicts it**, and how to ask without leading.

| | |
| --- | --- |
| H01 | Character attachment |
| H02 | Character differentiation |
| H03 | Character recall |
| H04 | Relationships feel reactive |
| H05 | Choices feel meaningful |
| H06 | Different players live different weeks |
| H07 | The slice of life works on its own |
| H08 | Mystery escalation |
| H09 | Ordinary explanations stay plausible |
| H10 | The Day 7 hook |
| H11 | Noah's ambiguity |
| H12 | Mara's reliability |
| H13 | Theo's humanity |
| H14 | June's humanity |
| H15 | Iris beyond the mystery |
| H16 | The protagonist |
| H17 | The Calendar |
| H18 | The Archive viewer |
| H19 | Placeholder impact |

Three of them are measured rather than asked. H06 is compared across reports —
telling a tester that variety is being measured is the fastest way to make them
go looking for it. H17 and H18 are asked *and* measured, because what somebody
did and what they remember doing are two different findings and both are worth
having.

Deliberately not hypothesised: whether the jokes are funny, whether the romance
reads as chemistry, and whether the prose is good. There is no way to ask any of
those without leading, so they are left to the free-text fields.

---

## Questionnaires

| | Questions | Time |
| --- | --- | --- |
| [Quick](../playtest/PLAYTEST_QUESTIONNAIRE_QUICK.md) | 12, plus 2 optional | about 5 minutes |
| [Deep](../playtest/PLAYTEST_QUESTIONNAIRE_DEEP.md) | 34 across eight sections | about 25 minutes |

Open text almost everywhere. Two five-point scales in the whole set, both on
"would you continue", which is the one question where a scale is genuinely the
measurement. No Likert grid.

The deep form says **answer in order and do not skip ahead**, because several
questions are deliberately asked before others: spontaneous recall before any
scene is named, mystery explanations before any list of options, the Day 7
question before the continue question. Once a list has been shown, the
spontaneous answer is no longer available.

---

## Playtest reporting

**Collected**, per run: seed, whether the act was completed, whether it was the
first completed run, day reached, active seconds, scenes in order, anchors,
choice ids including travel, documents opened, re-reads, calendar and journal
opens, promises made and kept and broken, saves reloaded.

**Not collected**: name, email, IP, MAC, hardware id, username, file paths,
documents, browser data, location, machine fingerprint, and any wall-clock time
at all. Durations are accumulated elapsed seconds, so the file cannot say when
somebody was awake — and stays reproducible from a fixture.

**Storage**: the player's own save directory. `playtest-report.json` and
`playtest-summary.md`, written only when the tester clicks the button.

**Consent**: asked once per installation, before the first line of the game.
Three states, and the third is load-bearing: `None` means not yet asked, which
is what makes the question appear exactly once. Declining **deletes** the report
rather than pausing it, and the game is otherwise identical. Every recorder goes
through one function that checks consent, so a new one cannot forget to.

**Schema**: `PLAYTEST_REPORT_SCHEMA_VERSION = 1`. A report from an older schema
is discarded rather than migrated — it describes a build that is no longer the
one being tested. That is the opposite of the save-game policy, deliberately: a
save is the player's, a report is a measurement.

**Export**: two files, one machine-readable and one not. The human-readable copy
exists so a tester can see exactly what they would be sending, and
`FEEDBACK_INSTRUCTIONS.md` asks them to open it. Being able to read your own
report is most of what makes consent mean anything.

### Choice ids

```
iris_the_second_box.0.take-the-lid-off
travel.archive_room
```

Storylet id, Ren'Py's own option index, and a slug of the caption. Each part is
unreliable alone: the id is permanent, the index survives a typo fix, the slug
makes a report readable and changes *visibly* when somebody rewrites an option —
which is exactly when two builds' reports should stop being comparable.

The alternative was an explicit `$ choice("...")` in each of the fifty menus.
Rejected: this milestone's instruction was to leave the writing alone, and a
hundred and fifty insertions into scene files is not that. The recorder hooks
the store's `menu` instead, which is the seam nvl mode uses.

---

## Privacy

**No automatic upload.** There is no code path that could.

**No personal identifiers.** `privacy_violations()` searches the serialised
report for absolute paths, email addresses, IP addresses, machine-identifier
words and timestamps. The export **refuses to write the file** if it finds one —
not a warning; a check that can be clicked past is not a check.

**No networking.** `tests/test_playtest_privacy.py` now walks the whole game
tree, not only the engine package, and fails on a networking import or a bare
URL in any non-comment line. One exception, named rather than pattern-matched:
`credits_data.rpy`, where several bundled licences require an attribution link
to be shown.

**Nothing goes to a model.** `s32 playtest summarize` counts and lists. It does
not classify sentiment and it does not summarise prose, and a test asserts that
its output contains no verdict words at all.

`docs/legal/PRIVACY.md` has been rewritten to say all of this in specifics. It
had claimed "nothing observes a real session", which stopped being true the
moment a consented report existed — and its own procedure demanded the rewrite
come first.

---

## The main human questions

Condensed from the hypotheses, in the order they matter.

**Characters.** Who did they want to spend time with, and can they describe five
people distinctly enough that two descriptions could not be swapped? Can they
say what Theo cares about besides being right, what June wants, and what Iris
would be doing without the archive? An "I don't know" to any of those is a clean
result: it means that character is currently a function.

**Relationship reactivity.** Did anybody seem to treat them differently because
of something earlier — and what made them think so? Nine scenes read state, out
of fifty-eight, in a game where a player sees one version and has nothing to
compare it to.

**Choice meaning.** Which choice did they think about longest, which did they
regret, and — the failure being hunted — did any feel obviously correct or
obviously the kind option?

**Mystery.** When did they first think something was wrong, what did they think
it was at that moment, and what explanations were they still entertaining at the
end? If no tester lists a mundane explanation, canon rule R5 is not surviving
contact and the act has tension only in theory.

**Day 7.** What question did they most want answered, and would they continue?
Asked in that order, so the intent is not rationalised backwards from the
question.

**Noah.** What is he hiding, and which moment made them think that? The second
half is the measurement.

**Calendar and Archive.** Opened voluntarily? Used for what? Any document
unnecessary? Ever reopened one? Each asked *and* checked against the report.

**Placeholders.** Did any make a scene hard to follow or blunt it — and,
specifically and only once, did the placeholder photograph make the final
discovery less effective? A clear majority there moves a commission to the front
of the queue.

---

## The thirteen priority scenes

From Milestone 4's human review queue, now with a playtest question each in
[`SCENE_REVIEW_GUIDE.md`](../playtest/SCENE_REVIEW_GUIDE.md).

| Scene | Hypothesis | Changed? | Reason |
| --- | --- | --- | --- |
| `mara_is_wrong` | H12 | No | Nothing to fix before it is read |
| `june_is_not_fine` | H14 | No | The risk is that it is about nothing, which is a reading, not a defect |
| `the_common_room` | H01, H07 | No | Every run plays it; absence from recall is the finding |
| `theo_the_quiz` | H13 | No | Suspected of overreach; testing beats guessing |
| `iris_the_second_box` | H04 | No | Three stances, all reachable |
| `annexe_two_of_them` | H05 | No | Balance is the claim; a tester decides |
| `the_date` | H08, H10, H19 | No | The ending. Now actually reachable in the game |
| `courtyard_small_talk` | H04, pacing | No | Read five times a run; F4 will say if that is too many |
| `mara_the_long_way` | H03, H07 | No | Recall is the test |
| `june_reads_it_flat` | H09 | No | R5 is measured by D3, not by editing |
| `ellery_and_the_form` | H19 | No | Whether her absence reads as choice or gap decides P0 vs P1 |
| `noah_takes_a_call` | H11 | **No — explicitly** | §54. Rewriting to pre-empt feedback destroys the evidence |
| `theo_admits_it` | H05 | No | The only cruelty in the act; regret is the good outcome |

Thirteen scenes, zero changed. That was the instruction and it is also the
correct answer: every one of these is uncertain in a way only a reader can
resolve, and polishing before the wave replaces the evidence with a guess.

---

## QA

| | |
| --- | --- |
| New game | pass |
| Save | pass |
| Load | pass — `after_load` migrates and counts the reload |
| Rollback | pass — `smoke_rollback`, state unwinds with the text |
| Calendar | pass — opened on day 4 of a real week, not day 1 |
| Archive | pass — opens, pages by keyboard, effects apply once, closes |
| Act 1 completion | pass — `act1_golden`, five anchors, day 6+, phase `odd` |
| Report export | pass — written, validated, no privacy violations |
| Consent | pass — asked once, declining deletes and the game still plays |
| Credits | pass — generated from the manifest, no wall clock |
| Licences | pass — `s32 assets verify` |
| Fresh install | see below |

**Exceptions reaching a tester**: none in the golden path. That is now a claim
with a test behind it: `act1_golden` executes every scene the director serves
across a full week, and until this milestone no test executed any scene at all.

---

## Test results

| | |
| --- | --- |
| `uv run pytest` | 312 passed (was 236) |
| `uv run s32 renpy test` | 19/19 testcases (was 16/16) |
| `uv run python scripts/check.py` | 11/11 gates |

New tests, and only what was needed:

- `tests/test_playtest_privacy.py` — 25. Network absence across the whole game
  tree, the privacy check poisoned one pattern at a time, schema validation,
  session-code stability, determinism, and that fixtures can never be mistaken
  for people.
- `tests/test_playtest_build.py` — 21. Every top-level entry accounted for,
  exclusion form, classification order, content mirroring, stamp round-trip,
  developer-only inspectors, no internal marker in a readable line, one
  language.
- `tests/test_act1_playable.py` — 18. One `start` label, the loop's shape, the
  §61 checklist run headlessly, and the act completing for every profile.
- `tests/test_playtest_summary.py` — 12. Counting, refusing, and not
  interpreting.
- `game/testcases/act1.rpy` — 3 Ren'Py testcases, including the golden path,
  which plays a full week in fourteen seconds.

The count is not the point and was not aimed at. What each of these holds is a
claim made to a tester or a failure that has already happened once.

---

## Simulation regression

5000 runs, seed 1234. Content unchanged, so this is a regression check and
nothing more.

| | M4 | M5 |
| --- | ---: | ---: |
| Storylets reachable | 58/58 | 58/58 |
| Dead ends | 0 | 0 |
| Anchors in 100% of runs | 5/5 | 5/5 |
| Top-tier 2+ | 34.9% | 34.9% |
| Unique scenes per run | 41.0 | 41.0 |

**`NarrativeDirector` algorithm: UNCHANGED.** Byte-identical to Milestone 1,
across five milestones. Nothing in `s32_engine/director.py` was touched.

Separately, and new: `scripts/playtime.py` measures the act across 360 completed
runs — nine profiles at forty seeds. Median 46 scenes and 12,750 spoken words;
range 8,650 to 15,971. At 240 words a minute that is 53 minutes of reading, plus
menus, travel and thinking. **Every one of those 360 runs reached the end of the
act.**

---

## Art status

Unchanged, as instructed.

| | |
| --- | --- |
| Class photograph | **P0** — commission required |
| Male-presenting compatible sprite | **P1** |
| Ms. Ellery | **P1** |

**Zero assets downloaded.** No generative AI. No third-party artwork sent
anywhere.

**Tester disclosure**, said in three places outside the fiction — the splash,
the About screen, and `PLAYTEST_README.md` — and in none inside it:

> Some visual assets remain temporary and should not be judged as final art.

A test asserts that no line in `game/story/` mentions a placeholder. Repeating
it in a scene would make the game apologise for itself, which changes how the
scene reads and therefore changes what the playtest measures.

The photograph is the one with a budget attached. Question G3 on the deep form
asks about it once, late, and plainly.

---

## Wave 1

**Five to eight testers.** Two to three regular visual-novel readers, two to
three casual ones, one or two technically minded.

The middle row matters most. An experienced reader knows the genre's furniture
and will find the calendar and the archive without noticing that nothing told
them to. Somebody who has played two visual novels is the one who will discover
whether this game explains itself.

**No recruitment has happened.** No emails, no Discord, no Reddit, no itch page.
§66 says prepare, not recruit, and the milestone stops here.

The briefing, in full:

> Play this naturally, then answer the questionnaire.

---

## Concerns

Named, because "ready with concerns" without a list is just "ready".

**The week loop is one day old.** It has been played end to end by a test
harness many times and by a human being never. The harness takes the first
option at every menu, which is a policy and not a person — it does not
backtrack, get lost, open the calendar out of curiosity, or quit on day three.

**Travel may be the wrong amount of agency.** The player chooses where to be
three times a day and whenever the room empties. That number was reasoned about
rather than tested, and it is the sort of thing that is either invisible or
irritating with nothing in between. F5 asks about it obliquely.

**The report is untested against a real installation.** It has been written,
validated and read on this machine, from a build made in this repository. A
fresh install on a machine that has never had the SDK is the check that matters
and is item 4 on the build checklist.

**Nine reactive scenes out of fifty-eight may not be enough to notice.** H04
could come back empty and mean either that the reactivity is too subtle or that
there is not enough of it. Those need different responses and the questionnaire
may not distinguish them.

**One wave will not settle the character questions.** Five people can find what
is broken. Whether anybody loves these characters is a bigger question than five
answers can close, and the temptation to treat the wave as a verdict on that
should be resisted.

---

## Final question

> If I had five testers available right now, should I send them this build?

# YES

The build plays a complete first act, it explains itself, it asks for consent
before it records anything, it cannot send anything anywhere, and every question
on the questionnaire is answerable by somebody who has played it.

Two days ago the honest answer would have been **no**, and not for any reason
visible in the gates: they would have received ten minutes of prototype and a
form full of questions about a week they never saw.

What remains uncertain is uncertain on purpose. `noah_takes_a_call`, the jokes,
the romance and the placeholder photograph are all unresolved because resolving
them by guesswork is what a playtest exists to replace.

Send it.
