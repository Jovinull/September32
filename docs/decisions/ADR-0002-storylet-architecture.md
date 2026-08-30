# ADR-0002 — Storylets over a branching tree

**Status:** Accepted · 2026-08-30

## Context

The design calls for a game where the player thinks *"this is the life my
decisions produced"* rather than *"I am on Iris's route"*. It also calls for
hundreds of scenes that recombine, delayed consequences, and replayability.

A conventional branching script cannot do this. Three binary choices produce
eight paths; ten produce a thousand. Every new choice multiplies the content
that must exist, so in practice branches are written to converge quickly, and
the player correctly perceives that their choices did not matter.

## Decision

Adopt **quality-based narrative** with **storylets**, as pioneered by Failbetter
Games, combined with **anchor scenes** for dramatic structure.

- A **storylet** is a pre-written scene plus metadata describing the situation it
  belongs in: location, time, phase, relationship thresholds, knowledge,
  commitments, priority, weight, repeat policy.
- The **director** (`s32_engine.director`) evaluates which storylets fit the
  current state and picks one.
- **Anchors** are ordered beats that must happen, gating the storylets around
  them. They supply the shape a purely emergent system lacks.

Content scales **additively**: a new scene is a new file, not an edit to a tree
that already has forty leaves.

Selection runs at defined moments — a time-slot change, a location change, an
explicit request — never on a frame timer.

## Alternatives

**A branching tree.** Rejected for the combinatorial reason above, and because
it makes late-game content the most expensive content, which is backwards.

**A pure state machine.** Equivalent to a tree with extra steps.

**Fully emergent, no anchors.** Rejected: quality-based narrative without
structure drifts. The player needs to feel a story is happening, not just that
scenes are. Anchors are the deliberate correction.

## Consequences

**Good**

- Every scene written increases the number of possible playthroughs rather than
  the maintenance burden.
- Delayed consequences are natural: a storylet can require a state set days ago.
- The system is analysable. Because requirements are declarative, tooling can
  find unreachable content — and did, three times during this bootstrap.

**Bad, and accepted**

- Requires tooling that a branching script would not: a validator, a static
  reachability checker, a headless simulator, coverage reports. That tooling is
  not optional; without it the combinatorics are unmanageable by hand.
- Writers must think about *conditions*, not only prose. The mitigation is that
  conditions are a small declarative language, not code.
- Pacing needs active management. Handled by anchors, priority tiers, and the
  pacing budget in `docs/narrative-design/PACING.md`.

## Revisit if

The content settles at a scale where a tree would genuinely be simpler — which
would mean the project's ambitions had shrunk considerably.
