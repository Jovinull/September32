# Act 1 playtest hypotheses

Nineteen things this project believes about Act 1 and cannot check.

Everything a machine can check has been: reachability, references, continuity
guards, relationship direction, choice-shape distribution, declared outcomes,
voice fingerprints, and the absence of the phrases that give machine prose away.
None of it is evidence that anybody enjoys reading the result. Five milestones
have improved numbers; none has confirmed that a person would want to keep
playing.

## How to use this document

**Testers must not read it.** Every hypothesis below names the answer it
expects, and a tester who knows what is being looked for stops being able to
supply it. The questions in
[`PLAYTEST_QUESTIONNAIRE_QUICK.md`](PLAYTEST_QUESTIONNAIRE_QUICK.md) and
[`PLAYTEST_QUESTIONNAIRE_DEEP.md`](PLAYTEST_QUESTIONNAIRE_DEEP.md) are the
tester-facing form, and they are deliberately blander than what is here.

Each entry has the same five parts. **What contradicts it** is the one that
earns its keep: a hypothesis with nothing under that heading has not been
thought about, only asserted.

## The rule about majorities

Five testers agreeing is a pattern, not a fact. It can mean the thing is true,
or that five people share a taste, or that one scene misled all five in the same
way, or that the wave recruited the wrong five people. Where a result would be
expensive to act on — a rewrite, a commission — the correct next step is usually
a second wave asked a sharper question, not a rewrite. See §70 of the milestone
brief and [`WAVE_1_PLAN.md`](WAVE_1_PLAN.md).

---

## H01 — Character attachment

**Hypothesis.** Players finish the week caring about at least one member of the
cast, and can say which one without being prompted with a list.

**Why it matters.** This is the load-bearing one. Act 2 assumes the player has
somebody they would be sorry to lose; if nobody does, the mystery is all there
is, and the mystery on its own is not enough to carry twenty more hours.

**What supports it.** Five characters with separate arcs
([`ACT_1_CHARACTER_ARCS.md`](../narrative-design/ACT_1_CHARACTER_ARCS.md)),
measurably distinct speech (words per line: Ellery 14.6, June 11.4, Iris 10.7,
Noah 9.9, Theo 9.3, Mara 8.9), and nine scenes that behave differently depending
on how somebody has come to see the player.

**What contradicts it.** The cast is met through a job. Every character is
introduced doing something adjacent to the archive, which is an efficient way to
build a cast and a suspicious way to build affection. Milestone 4's own audit
found that thirty-three of fifty-one scenes had the same shape.

**How to test without leading.** Open, unordered, before any character is named
by us: *Who did you most want to spend time with? Who did you least want to
spend time with? Why?* Never *did you like Iris?* first — naming a character
first makes them the subject and manufactures an opinion.

---

## H02 — Character differentiation

**Hypothesis.** A player can describe Iris, Mara, Theo, June and Noah in their
own words, and the descriptions resemble the character bibles.

**Why it matters.** Differentiation is the claim the writing metrics support
most strongly and the claim a reader is least obliged to agree with. Words per
line is a fingerprint, not a personality.

**What supports it.** `docs/characters/` gives each of them a want, a habit and
a way of being wrong. The registers are measurably separate.

**What contradicts it.** They are five people of similar age in one building
with one shared subject, written by one hand. The register of the whole game is
warm and understated, which is a house style and can flatten a cast.

**How to test without leading.** *Describe each of these characters in your own
words.* Compare the free text against the bible. What we are looking for is not
accuracy — a player is allowed to read a character differently — but
**distinctness**: five descriptions that could be swapped between names is the
failure.

---

## H03 — Character recall

**Hypothesis.** A player can name three specific moments afterwards.

**Why it matters.** A week that leaves nothing behind is a week nobody will
return to. Candidate moments are listed in
[`HUMAN_ACT1_REVIEW.md`](../production/HUMAN_ACT1_REVIEW.md); whether any of
them are the ones that stick is precisely what cannot be assessed from inside.

**What supports it.** The scenes were written to have objects in them — a mug
moved four inches, a notebook with four names in it, a dog called Bill.

**What contradicts it.** Nothing in Act 1 is loud. A deliberately quiet act can
be a week that is pleasant while it happens and gone by Tuesday.

**How to test without leading.** *What are the first three character moments you
remember?* Asked **before** any scene is named or listed. Spontaneous recall and
prompted recognition are different measurements, and once we have shown a list
the first is no longer available.

---

## H04 — Relationships feel reactive

**Hypothesis.** A player notices at least once that a character treated them
differently because of something they had done earlier.

**Why it matters.** Milestone 4's first finding was that relationships were
write-only: fifty-one storylets wrote to eight axes and no line of prose read
one back. Nine scenes now read state. Whether that reads as *reactivity* or as
coincidence is the whole question.

**What supports it.** `stance()` distinguishes four readings, and `wary` is
written as a third thing rather than as a colder version of `distant`.

**What contradicts it.** The reactive scenes are nine out of fifty-eight, a
player sees perhaps forty scenes, and the differences are tonal rather than
structural. A tonal difference is invisible to somebody who only ever sees one
version.

**How to test without leading.** *Did any character seem to treat you
differently later because of something you had done before?* then *What made you
think that?* Never mention a relationship system, and never mention axes — a
player told that trust is tracked will find trust being tracked.

---

## H05 — Choices feel meaningful

**Hypothesis.** Players think about at least one choice, and few choices read as
obviously correct or as obviously the "kind" one.

**Why it matters.** Milestone 4 found three trait sets accounting for twenty-one
of forty-two menus. The revision cut filler options and rewrote choice text from
label to behaviour. Whether that produced *decisions* is unverifiable from here.

**What supports it.** No option in Act 1 announces its own consequence, and the
only branch that lowers a trust axis is a real option rather than a trap.

**What contradicts it.** A warm, understated game with a warm, understated
protagonist has a natural gravity toward the kind answer, and gravity of that
sort is invisible to the person writing it.

**How to test without leading.** Four open questions: *Which choice did you think
about the longest? Which did you regret, if any? Did any feel meaningless? Did
any feel obviously correct?* The last is the one to weight: a morally labelled
choice is the specific failure being hunted.

---

## H06 — Different players live different weeks

**Hypothesis.** Two testers who play naturally see substantially different
weeks.

**Why it matters.** It is the entire justification for a storylet architecture.
If everyone sees the same forty scenes, four milestones of density work bought
nothing a linear script would not have given more cheaply.

**What supports it.** Five simulated profiles share about 23% of their scenes.
The top scene takes 12.7% of everything played, down from 71.7% at the
bootstrap.

**What contradicts it.** The simulated profiles are caricatures — one of them
takes every romantic option every time. Real people are less consistent, and a
cast of real people may converge on the middle. Until Milestone 5 every
installation also started from the same seed, which would have removed the
random contribution to divergence entirely; that is fixed, and the fix is
untested against real installs.

**How to test without leading.** Do not ask. This one is measured, by comparing
playtest reports across the wave: scenes played, choices, commitments,
documents, relationship outcomes, facts learned. Telling a tester that variety
is being measured is the fastest way to make them go looking for it.

---

## H07 — The slice of life works on its own

**Hypothesis.** Part of the week would have been worth playing with no mystery
in it at all.

**Why it matters.** `PACING.md`'s founding rule: before you break the routine,
the player has to like the routine. September 32 earns its strangeness or it
does not have any.

**What supports it.** Whole scenes contain no mystery content — the common room,
the long way home, the television quiz, the lesson.

**What contradicts it.** Every one of them still sits inside a week framed by an
archive job, and a reader who is waiting for the plot will experience an
ordinary scene as a delay rather than as the point.

**How to test without leading.** *Which part of the week would still have been
enjoyable if the mystery did not exist?* then *Was there any ordinary scene you
especially liked?* The second question exists because the first invites an
abstract answer and the second forces a specific one.

---

## H08 — Mystery escalation

**Hypothesis.** Players notice something is wrong at roughly the intended point
— the undated column on day four, sharpening at the date on day six — and not
before.

**Why it matters.** Too early and the ordinary week is spent; too late and the
act has no hook. The phase model exists to hold this and has never been
validated against a person.

**What supports it.** The phase turns exactly once in Act 1, at
`the_undated_column`, and the act deliberately ends inside `odd` rather than
escalating to `unsettling`.

**What contradicts it.** A player who knows the game is called September 32 is
already looking. The title is a spoiler and cannot be removed.

**How to test without leading.** *At what point did you first think something was
genuinely wrong?* then *What did you think the explanation might be at that
moment?* The second answer is worth more than the first: it says whether the
player is doing the reasoning the act wants, or has jumped to the ending.

---

## H09 — Ordinary explanations stay plausible

**Hypothesis.** Right up to the final discovery, players are still entertaining
mundane explanations.

**Why it matters.** Canon rule R5: a player must never feel stupid for having
believed the ordinary account. If the mundane reading collapses on day two, the
act has no tension left, only waiting.

**What supports it.** Every anomaly is given an ordinary explanation by a
character who means it, and June's argument that the undated column is somebody's
Tuesday is written to be *good*.

**What contradicts it.** Genre literacy. A visual novel with a strange title and
an archive in it teaches an experienced player what kind of story they are in
before the first anomaly arrives.

**How to test without leading.** *Before the final discovery, what explanations
were you considering?* Free text first, never a multiple choice. A list of
options would supply the very reading we are trying to find out whether they
reached on their own. Cross-reference with the visual-novel experience field:
this is where that field earns its place.

---

## H10 — The Day 7 hook

**Hypothesis.** Players finish with a specific question and would continue.

**Why it matters.** It is the closest thing to a verdict this wave can produce.

**What supports it.** The act ends on two documents that have no single ordinary
account between them, having taken care that each has one separately.

**What contradicts it.** Ending on a question is a technique with a failure mode:
a reader who does not care what the answer is experiences it as nothing
happening.

**How to test without leading.** *What question did you most want answered when
Act 1 ended?* — free text, before the continue question, so the intent answer is
not rationalised backwards from it. Then *If Act 2 were available right now,
would you continue?* on a five-point scale, then *Why?*

---

## H11 — Noah's ambiguity

**Hypothesis.** `noah_takes_a_call` reads as a person avoiding something
unrelated, not as a clue.

**Why it matters.** This is the scene the project is least confident about, and
it was left deliberately untouched in Milestone 5 so that it could be tested
rather than pre-emptively rewritten. The risk is specific and was written down
before any tester saw it: a phone call somebody does not want to take may read
as a clue no matter how ordinary the prose is, in which case the scene achieves
the opposite of its purpose and should be cut.

**Why it stays as it is.** Rewriting a scene to pre-empt feedback destroys the
evidence the feedback would have been. If testers converge on *Noah knows the
supernatural truth*, the scene is sabotaging the ambiguity and the answer is to
cut it — not to soften it and retest a different scene.

**What supports it.** The call is domestic, the prose declines to dwell, and
Noah's arc has an unrelated reason to be evasive.

**What contradicts it.** In a mystery, an unexplained private phone call is a
genre signal, and the wrong pocket is a detail readers are trained to collect.

**How to test without leading.** Only after Act 1, and never named as a scene:
*What do you think Noah is hiding, if anything?* then *Which moment made you
think that?* The second question is the measurement — if the phone call is named
by most testers, the hypothesis has failed regardless of what they think he is
hiding.

---

## H12 — Mara's reliability

**Hypothesis.** Players come away reading Mara as confident and not always
correct, and can say why.

**Why it matters.** `confidence != correctness` is the load-bearing property of
the whole mystery structure: it is what lets the game present a wrong
explanation honestly, through somebody who believes it.

**What supports it.** `mara_is_wrong` has her read a situation specifically,
from two real observations, and be wrong where the player can see it.

**What contradicts it.** That is one scene out of fifty-eight, reached by some
runs and not others, and a player who misses it meets a Mara who is only ever
right.

**How to test without leading.** *How reliable do you think Mara is?* then *Why?*
Cross-reference against the report: did this tester's run actually contain
`mara_is_wrong`? A tester who never saw it and still says "confident, sometimes
wrong" is much stronger evidence than one who did.

---

## H13 — Theo's humanity

**Hypothesis.** Players can name something Theo cares about besides being right.

**Why it matters.** A pedant who exists to supply corrections is a narrative
device. If testers cannot answer this, Theo is a tool with dialogue.

**What supports it.** `theo_the_quiz`: a notebook with four names in it, three
of whom have stopped playing, and he does not say the thing.

**What contradicts it.** Milestone 4's own review flagged that scene as the most
sentimental in the game and the one most likely to have overreached. Overreach
and effectiveness are hard to tell apart from the inside.

**How to test without leading.** *What does Theo care about besides being right?*
An "I don't know" is a clean result, not a missing one.

---

## H14 — June's humanity

**Hypothesis.** Players can say what June wants during the week, and it is not
"to deliver local history".

**Why it matters.** June carries most of the act's exposition. A character who
carries exposition tends to become the mechanism that delivers it.

**What supports it.** `june_is_not_fine` is an ordinary bad afternoon with no
plot in it, and her four-minute plan for a birthday nobody else noticed is about
her rather than about the archive.

**What contradicts it.** She is also the one who explains the undated column,
the school's history and the booklet. Volume of exposition is its own kind of
characterisation and not the intended kind.

**How to test without leading.** *What do you think June actually wants during
this week?*

---

## H15 — Iris beyond the mystery

**Hypothesis.** Players can imagine Iris doing something unrelated to the
archive.

**Why it matters.** She is the closest thing to a romance route and the person
most fused with the plot. A love interest who is a function of the mystery
dissolves when the mystery resolves.

**What supports it.** `iris_the_wrong_photograph` — photographing a shoe, on two
different days, so you can see it has moved.

**What contradicts it.** She is the archive. She works there, she found the
first box, she owns the paperweight moment, and most of her scenes are set in
the room.

**How to test without leading.** *What do you think Iris would be doing if the
archive mystery did not exist?* An inability to answer is the finding.

---

## H16 — The protagonist

**Hypothesis.** The protagonist reads as somewhere between a blank and a defined
character, and never acts against the player's choices.

**Why it matters.** The protagonist speaks 68% of the game's words and had no
character bible until Milestone 4. That is a large amount of prose written
without a specification.

**What supports it.** `PROTAGONIST.md` now exists, and the narration was audited
against it.

**What contradicts it.** It was written first and specified afterwards, which is
the order that produces drift.

**How to test without leading.** *Did the protagonist feel like you, like a
defined character, or somewhere in between?* then *Was there any moment where
they acted in a way that felt incompatible with your choices?* The second is the
real one: any answer to the first is acceptable, but a named incompatibility is
a bug.

---

## H17 — The Calendar

**Hypothesis.** Some players open the calendar without being told to, and it is
useful when they do.

**Why it matters.** It is one of two signature interfaces and it cost a
milestone. If nobody opens it, it is decoration, and Act 2 should not build on
it.

**What supports it.** It derives every square from live state, it shows
commitments the player made, and it is the only surface where September's shape
is visible.

**What contradicts it.** It lives behind the game menu, alongside Save and
Preferences, which is where players go for housekeeping rather than for the
story. Nothing in the writing tells anybody it exists.

**How to test without leading.** *Did you open the Calendar? What did you use it
for? Was it useful?* — and check the answer against the report's
`calendar_opens`, which is the real measurement. Never *did you like the
Calendar?*: it invites a courteous yes.

---

## H18 — The Archive viewer

**Hypothesis.** Reading documents is interesting rather than dutiful, the text
is comfortable, and at least one player reopens one.

**Why it matters.** The viewer is where a commission budget would produce the
most distinctive result in this game. Knowing whether people read documents at
all decides whether that is worth funding.

**What supports it.** Six documents, two of them deliberately mundane, on
deterministic generated paper, with keyboard paging.

**What contradicts it.** Two of six being mundane is a deliberate choice that
can read as padding, and a reader who finds document one boring will not open
document four.

**How to test without leading.** *Did inspecting documents feel interesting? Did
any feel unnecessary? Was the text comfortable to read? Did you ever reopen
one?* The reopen question is checkable against `archive_reopens` in the report,
which makes it the one that can be trusted.

---

## H19 — Placeholder impact

**Hypothesis.** The temporary art is legible as temporary and does not stop a
scene working — with the class photograph as the specific risk.

**Why it matters.** The class photograph is the object the premise turns on and
it does not exist. It is `P0` in
[`ART_PRODUCTION_PLAN.md`](../production/ART_PRODUCTION_PLAN.md) and needs a
commission. What this wave can settle is whether it needs one *now*.

**What supports it.** Placeholders are labelled rather than disguised, and the
README says plainly that some art is temporary.

**What contradicts it.** The final discovery is a discovery *about an image*.
Asking a reader to be moved by a labelled grey box is asking a lot, and no
amount of prose around it fully compensates.

**How to test without leading.** *Did any placeholder make a scene hard to
understand? Did any significantly reduce the emotional impact?* then *Which
one?* Ask the specific question last and only once, in the deep questionnaire:
*Did the placeholder photograph make the final discovery significantly less
effective?* A consensus yes is enough to move the commission to the front.

---

## What is deliberately not hypothesised

**Whether the jokes are funny.** Humour was audited for *sameness* — the five
characters joke in measurably different registers — which is a different claim
from any of them landing. There is no way to phrase a question about this that
does not lead, so it is left to the free-text fields.

**Whether the romance reads as chemistry.** Same reason.

**Whether the prose is good.** No questionnaire can ask this usefully. What a
wave can produce is the indirect evidence: recall, continue intent, and whether
anybody quotes a line back.
