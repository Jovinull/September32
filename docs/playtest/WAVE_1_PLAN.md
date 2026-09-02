# Wave 1 — plan

The first time anybody outside the project reads September 32.

## What this is for

One question: **do real players enjoy this first week and want to continue?**

Everything a machine can answer has been answered. Two hundred and thirty-six
tests, five thousand simulated runs, eleven quality gates, and a full editorial
audit of every scene. None of it is evidence that anybody enjoys reading the
result, and no further amount of it will become that evidence.

## What this is not

**Not a statistical study.** Five to eight people cannot measure anything. What
they can do is find the problems that are obvious to a stranger and invisible
from inside — which, historically, is most of them.

**Not a review.** Nobody is being asked to say whether it is good. They are
being asked what they noticed, what they remember, and whether they would
continue.

**Not a soft launch.** Nothing is published, posted, listed, or announced. See
"Recruitment" below.

## Size and mix

**Five to eight testers.** Below five and a single unusual reader dominates;
above eight and the reading of free text becomes a job rather than an afternoon.

Aim for:

| | |
| --- | --- |
| Regular visual-novel players | 2–3 |
| Casual or infrequent VN players | 2–3 |
| Technically minded testers | 1–2 |

The mix matters more than the number, and the middle row matters most. An
experienced VN reader knows the genre's furniture and will navigate the calendar
and the archive without noticing that nothing told them to. Somebody who has
played two visual novels is the one who will find out whether this game explains
itself. The technical testers are there for the build, the install, the save
system and the crash reports — they are not the audience and their taste should
be weighted accordingly.

The optional experience question on the questionnaire exists so that answers can
be read against this, not to sort people into good and bad testers.

## Recruitment

**None, in this milestone.** No emails, no Discord post, no Reddit post, no itch
page, no announcement. The build and the paperwork are prepared and that is
where Milestone 5 stops.

When the wave does run, approach people individually and privately, and tell
them what they are getting into: an unfinished first act, some placeholder art,
about ninety minutes, and a questionnaire afterwards. Somebody who agreed to
"try a game" and received homework will answer politely, and politely is the one
kind of feedback that is worth nothing.

## What each tester receives

1. The build — `September32-Act1-Playtest-0.2.0-playtest.1-pc.zip`
2. `PLAYTEST_README.md` (inside the archive)
3. `FEEDBACK_INSTRUCTIONS.md` (inside the archive)
4. One questionnaire — [quick](PLAYTEST_QUESTIONNAIRE_QUICK.md) for most people,
   [deep](PLAYTEST_QUESTIONNAIRE_DEEP.md) for anybody who volunteers the time

Nothing else. In particular **not**
[`ACT1_PLAYTEST_HYPOTHESES.md`](ACT1_PLAYTEST_HYPOTHESES.md),
[`SCENE_REVIEW_GUIDE.md`](SCENE_REVIEW_GUIDE.md), or anything else in
`docs/`. Every one of those names the answer it is hoping for.

## What to say when handing it over

> Play this naturally, then answer the questionnaire.

That is the whole briefing, and the build was built to need no more than it. Do
not say which character to follow, which route to take, what to look out for,
what September 32 means, or what is being tested. If a tester asks a direct
question before playing, the honest answer is "I would rather not say until
afterwards, because it would change what you notice" — which is true, and which
testers generally find reasonable.

Afterwards, say anything they like.

## The one instruction that matters

**Answer the questionnaire before playing a second time.**

A first playthrough is the only unrepeatable measurement in this wave.
Everything else — pacing, variety, whether the calendar gets used — can be
recovered from a later run or from the report. What somebody thought was going
on at the end of day four cannot.

The README says this, the end-of-act screen says this, and it is worth saying
once in person as well.

## Collecting it

Per tester, into `playtests/raw/<session-code>/`:

- the questionnaire
- `playtest-report.json`, if they kept one
- any bug reports
- anything they said in a message that they would not have written on a form,
  which in practice is often the most useful item

`playtests/raw/` is gitignored. Real people's words do not go into version
control, and there is no automation that could put them there by accident.

Then fill in one [`WAVE_1_ANALYSIS_TEMPLATE.md`](WAVE_1_ANALYSIS_TEMPLATE.md)
per tester, and one [`WAVE_1_SUMMARY_TEMPLATE.md`](WAVE_1_SUMMARY_TEMPLATE.md)
for the wave.

`uv run s32 playtest summarize playtests/raw` aggregates the reports. It does
not read the questionnaires, and it does not interpret free text — that part is
a person's job and is not one a tool should be trusted with.

## Feedback goes to no model

Nothing a tester writes is sent to a language model by any tooling in this
repository. The summarizer counts and lists; it does not classify sentiment and
it does not summarise prose. If the developer later wants a model's opinion on
some particular question, that is a deliberate act with a specific extract, not
a default behaviour of the pipeline.

## Reading the results

Categories for classifying what comes back:

```
BLOCKER  BUG  CONFUSION  CHARACTER  RELATIONSHIP  CHOICE
PACING   MYSTERY  UI  ART  POSITIVE
```

**Five testers saying X does not make X true.** It can mean the thing is real,
or that five people share a taste, or that one scene misled all five in the same
way, or that the wave recruited the wrong five people. Convergence is a signal
to investigate, not a verdict to implement. Where acting would be expensive — a
rewrite, a commission — the cheaper next step is usually a second wave asked a
sharper question.

**Split opinions are not noise.** Two testers who disagree strongly about the
same scene have found something more interesting than five who agree mildly.

**One outlier is worth reading twice.** The tester who did something nobody
expected has usually found a real hole, and the temptation to file them as
unrepresentative is strong and usually wrong.

## What happens after

Nothing is planned. The next milestone is chosen from what comes back:
questionnaires, reports, bug reports, and a person's reading of them. Candidate
directions — character rewrite, choice and callback revision, mystery pacing,
a Day 7 rewrite, UI revision, art escalation, Act 2 planning — are all open, and
picking between them before the feedback exists would defeat the purpose of
collecting it.
