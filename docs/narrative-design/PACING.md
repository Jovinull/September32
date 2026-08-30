# Pacing budget

**Status: CANON for the phase model; PROVISIONAL for the numbers.**

> Before you break the routine, make the player like the routine.

That is not a mood note. It is a budget, and it is enforced in code: the phase is
first-class state, it only moves forward (`s32_engine.effects` raises otherwise),
and every storylet can declare which phases it belongs to.

## The five phases

### `normal`
Ordinary school life. Nothing is wrong. **Nothing is wrong.** The archive is a
job, the people are people, and if the player is not enjoying themselves the rest
of the game does not work.

The temptation to seed unease here is very strong and must be resisted. A
"subtle hint" in the first hour is not subtle: it is a promise, and it converts
every ordinary scene afterwards into waiting.

*Content mix, provisional:* 65% slice-of-life and relationships, 25% archive as
work, 10% mystery — and that 10% is *interesting*, not ominous.

### `odd`
One thing does not fit. Singular. It has an ordinary explanation and the
characters reach for it, because that is what people do.

Entered by the `the_date` anchor. Nothing before it may advance the phase.

*Mix:* 50% slice-of-life, 30% investigation, 20% mystery.

### `unsettling`
A second and third thing. The ordinary explanations start requiring effort. Rule
R5 still holds — a sceptical player can maintain a mundane reading, and June is
still making good arguments.

*Mix:* 35% slice-of-life, 40% investigation, 25% horror-adjacent.

### `impossible`
The ordinary explanation is gone. This is where the game stops being about
whether and starts being about what to do. R4 still holds: nothing manifests.
The archive is still just paper.

*Mix:* 25% relationships, 35% investigation, 40% consequence.

### `consequences`
What people do with what they know. The endings live here.

## How the escalation is governed

**Anchors advance the phase. Storylets never do.** A storylet's `effects` may not
contain `phase = ...`; that belongs to anchors, which are ordered and gated. This
is the mechanism that stops a keen writer from accidentally shipping the horror
in week two.

**Ordinary content stays available in every phase.** A storylet with no `phases`
field is eligible everywhere, which is the default, which means the default is
that life goes on. Late-game scenes of people being ordinary are more valuable
than early-game ones, not less.

**The mix is measured, not hoped for.** `s32 simulate` reports the tag
distribution across a thousand runs (`## Content mix` in the report). If the
numbers do not match the intent, the content is wrong — not the intent.

## The failure modes this is guarding against

**Front-loading the unease.** Every scene becomes a horror scene the player is
waiting out. Guarded by: nothing may advance the phase before `the_date`.

**Abandoning the slice-of-life.** The relationships stop developing exactly when
the stakes make them matter. Guarded by: measuring the mix per phase.

**Escalating on a timer.** The phase advances because days passed, not because
the player found something. Guarded by: anchor requirements name *knowledge*, not
dates.

**A player who investigates lightly getting a worse game.** Guarded by: anchors
are the only mandatory content, and their requirements are reachable through
ordinary play — which the simulator verifies across nine player profiles.

## Current state

Two phases exist in content: `normal` (the whole vertical slice) and `odd`
(reachable, one anchor, not exercised by the prototype). The prototype
deliberately stops before `the_date`.
