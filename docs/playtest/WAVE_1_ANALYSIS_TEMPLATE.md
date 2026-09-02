# Wave 1 — tester analysis

One copy per tester. Fill it in from the questionnaire and the report together;
neither on its own is worth much.

**Do not fill this in with invented data.** An empty template is a template. A
template with plausible-looking answers in it is a document that will be quoted
back as evidence in six weeks by somebody who has forgotten where it came from.

Save completed copies to `playtests/aggregate/`. The raw questionnaires stay in
`playtests/raw/`, which is gitignored.

---

## Identity

| | |
| --- | --- |
| Tester ID | |
| Session code | |
| Questionnaire | quick / deep |
| VN experience | never / a few / occasionally / regularly / very experienced |
| Genres they like | |
| Build | |

## The run

Straight from `playtest-report.json`. `s32 playtest summarize` prints all of it.

| | |
| --- | --- |
| Finished Act 1? | |
| Day reached | |
| Playtime (report) | |
| Playtime (their estimate) | |
| Scenes played | |
| Distinct scenes | |
| Choices made | |
| Documents opened | |
| Documents reopened | |
| Calendar opens | |
| Journal opens | |
| Promises made / kept / broken | |
| Saves reloaded | |
| Replayed before answering? | |

**Estimate versus measurement.** Where the two playtimes disagree, the gap is
itself a finding: somebody who played for fifty minutes and thinks it was ninety
was not enjoying it, and somebody who played for ninety and thinks it was fifty
was.

## Continue intention

| | |
| --- | --- |
| Would continue | definitely / probably / not sure / probably not / definitely not |
| Reason, in their words | |

## Characters

| | |
| --- | --- |
| Favourite, and why | |
| Least favourite, and why | |

**Their descriptions**, verbatim. Do not paraphrase — the phrasing is most of
the data, and a paraphrase is a small act of interpretation performed before
anybody has decided what the interpretation should be.

| Character | What they wrote | Matches the bible? |
| --- | --- | --- |
| Iris | | |
| Mara | | |
| Theo | | |
| June | | |
| Noah | | |

Note whether any two descriptions could be swapped between names. That is the
H02 failure and it is not visible one row at a time.

## Recall

The three moments they named, before any scene was listed to them:

```
1.
2.
3.
```

For each, check the report: was it a scene this run actually contained? A
remembered moment that never happened is worth chasing.

## Choices

| | |
| --- | --- |
| Thought about longest | |
| Regretted | |
| Felt meaningless | |
| Felt obviously correct | |

## Callbacks and reactivity

| | |
| --- | --- |
| Noticed a character reacting to earlier behaviour? | |
| What made them think so | |
| Which stance they actually reached (from the report) | |
| Real callback or coincidence? | |

The last row is the one that takes judgement. A tester who felt a reaction that
the state does not support has still had the experience the design wanted, and
that is a genuine result — but it is a different result from the design working.

## Mystery

| | |
| --- | --- |
| First thought something was wrong | |
| What they thought it was, at that moment | |
| Explanations entertained before the end | |
| Whose explanation convinced them | |
| Question they most wanted answered | |

## Named characters

| Question | Their answer | Reading |
| --- | --- | --- |
| What is Noah hiding? | | |
| Which moment made them think that? | | |
| How reliable is Mara? | | |
| What does Theo care about? | | |
| What does June want? | | |
| What would Iris be doing? | | |

On the Noah row, record whether they named `noah_takes_a_call` specifically, and
whether the report says they saw it. The decision rule is fixed in
[`SCENE_REVIEW_GUIDE.md`](SCENE_REVIEW_GUIDE.md) §12 and was written before the
wave.

## Protagonist

| | |
| --- | --- |
| Felt like: you / a character / in between | |
| Any incompatible moment | |

## Interfaces

| | |
| --- | --- |
| Opened the calendar? (their answer) | |
| Opened the calendar? (the report) | |
| What they used it for | |
| Documents interesting? | |
| Any document unnecessary? | |
| Text comfortable? | |
| Reopened a document? | |

Where their answer and the report disagree, the report is what happened and
their answer is what they remember. Both matter; only one is a measurement.

## Placeholders

| | |
| --- | --- |
| Any placeholder made a scene hard to follow | |
| Any placeholder reduced impact | |
| The class photograph specifically | |
| Ms. Ellery's absence noticed? | |

## Free text

| | |
| --- | --- |
| Best thing | |
| Worst thing | |
| Major confusion | |
| Would recommend to | |
| One thing they would change | |
| Anything else | |

Anything they said in a message rather than on the form goes here too, marked as
such. It is often the most honest item in the file.

## Bugs

| # | What happened | Category | Reproduced | Severity |
| --- | --- | --- | --- | --- |
| | | | | |

## Action candidates

What this one tester's feedback would suggest doing, if it turns out others
agree. **One tester is never enough to act on** — this column exists so that the
wave summary can count convergence, not so that anything here gets done.

| Candidate | Category | Which hypothesis | Confidence |
| --- | --- | --- | --- |
| | | | |

Categories: `BLOCKER` `BUG` `CONFUSION` `CHARACTER` `RELATIONSHIP` `CHOICE`
`PACING` `MYSTERY` `UI` `ART` `POSITIVE`
