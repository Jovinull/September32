# Writing with AI

AI is an assistant to the writing. It is not an authority over the canon, and it
is not in the shipped game at all ([ADR-0004](../decisions/ADR-0004-no-runtime-ai.md)).

This document is the working procedure. `AGENTS.md` has the binding rules.

## Before writing a scene

Read, in this order:

1. **The scene card.** If there isn't one, write it first —
   [`SCENE_CARD_TEMPLATE.md`](../narrative-design/SCENE_CARD_TEMPLATE.md). It
   takes ten minutes and it is what stops a scene from merely happening.
2. **The character bibles** for everyone present. Voice, boundaries, and
   especially **Never do** and **Never say**.
3. **The canon** the scene touches — and note the `CANON` / `PROVISIONAL` /
   `IDEA` markers. A scene may not rely on an `IDEA`.
4. **The knowledge state.** What does each character know walking in? What are
   they wrong about?
5. **The timeline**, if any date or duration appears.
6. **The style guide** for the register: `DIALOGUE`, `HORROR`, `ROMANCE`,
   `MYSTERY`, `HUMOR`.

Skipping this produces prose that reads fine and is wrong — a character who is
subtly out of voice, a fact stated that the player should not have yet, a date
that contradicts a document already shown.

## While writing

**Do not invent canon.** Not the school's history, not a character's family, not
why something happened. If the scene needs a fact that does not exist, that is a
proposal for `OPEN_QUESTIONS.md`, not a sentence.

The failure mode is subtle: implying something is enough. A line of narration
suggesting a cause for September 32 makes that a fact about the world the moment
a reader sees it.

**Declare state changes in metadata.** Every relationship change and knowledge
grant inside a menu goes in the storylet's `outcomes` list too. A change only the
prose knows about makes later content look unreachable, and the tooling will
report it as dead.

**Write to the character, not to the plot.** If a scene needs someone to behave
against their bible, the scene is wrong, or the bible needs a proposal.

## After writing — the review pass

Run each of these deliberately. They catch different things.

**Continuity.** Against the timeline, the canon, and every scene that touches the
same facts. Does anyone know something they should not?

**Voice.** Cover the names. Can you tell who is speaking? If not, it is not
finished. Check the bible's speech patterns and **Never say** list.

**Repetition.** Has this beat been used? The same joke, the same gesture, the
same construction? Search the `.rpy` sources for a distinctive phrase.

**Exposition.** Is anyone explaining something both characters already know?
[`DIALOGUE.md`](../style/DIALOGUE.md) has the alternatives.

**Foreshadowing.** What is planted, and does something later pay it off? What
earlier setups does this land? Both go on the scene card.

**Contradiction.** Not just facts — tone, characterisation, and what the phase
allows. A horror beat in the `normal` phase is a contradiction.

**Over-writing.** Cut the sentence that tells the reader how to feel. Cut the
adverb doing a verb's work. Cut the clause explaining the joke.

## What AI is good at here

- Drafting a scene from a filled-in scene card.
- Generating *variants* of a line to choose between.
- Continuity checking across many files — genuinely better than a human at this.
- Finding repeated constructions.
- Writing the tooling, the tests and the documentation.
- Asking what a scene is *for*, which is the question that fixes most bad scenes.

## What it is bad at, and what to watch for

**Reaching for the obvious.** The first draft of a mystery scene will tend toward
the most expected beat. `docs/references/` exists partly as a list of what has
already been done.

**Explaining.** It will add a sentence clarifying what the previous sentence
implied. Cut it. This is the single most common edit.

**Losing a voice under pressure.** In a long scene, characters converge on one
register. Re-read against the bible.

**Confident invention.** It will fill a gap in the canon smoothly and without
signalling that it did. This is the dangerous one, and it is why `AGENTS.md` §1.2
exists.

**Escalating too fast.** Given a horror premise it will reach for horror.
[`PACING.md`](../narrative-design/PACING.md) is the corrective, and the phase
system enforces it.

## Assets

Covered in full by [`AI_AND_ASSETS_POLICY.md`](../legal/AI_AND_ASSETS_POLICY.md).
The short version: **no third-party artwork goes to any AI service, ever** — not
for generation, not for editing, not for analysis. The visual-consistency audit
is local and deterministic for exactly this reason, and it states plainly what it
cannot tell you rather than uploading an image to find out.
