# ADR-0006 — Metadata in JSON, prose in .rpy

**Status:** Accepted · 2026-08-30

## Context

A storylet has two halves that want opposite things. The *conditions* want to be
machine-readable, so tooling can validate references and find unreachable
content. The *prose* wants to be human-readable, so a writer can work in it
without reading a schema.

## Decision

Split them.

```
data/storylets/rain_after_school.json     conditions, effects, priority, tags
game/story/storylets/*.rpy                label s32_st_rain_after_school:
```

The JSON names a Ren'Py `label`; the label holds the writing. Validation checks
that every label exists and that every label starting `s32_st_` is claimed.

JSON Schemas (Draft 2020-12) are **generated** from the engine's enum tuples by
`s32 schemas`, and CI fails if they drift. A hand-written schema diverges from
the code within a month, and the failure mode is content that validates in CI
and crashes in the game.

### Declared outcomes

Choices inside a scene change state too, and that state lives inside prose the
tooling cannot read. This was not a theoretical problem: the simulator reported
`rain_after_school` unreachable because it needs `iris.trust >= 12` and no
declared effect could raise trust past 2 — the rest came from menu choices.

So a storylet also declares `outcomes`: the alternative effect sets its choices
produce, in order. The prose still lives in the `.rpy`; the *consequences* are
declared where the analysis can see them. `AGENTS.md` makes keeping them in sync
a rule, and the coverage report shows which storylets have menus but no declared
outcomes.

## Alternatives

**Everything in JSON, prose included.** Rejected. Dialogue as JSON strings is
unreadable, unreviewable and impossible to write in. Ren'Py script exists
because it is good at exactly this.

**Everything in .rpy, conditions included.** Rejected. Conditions in Python are
not analysable: the validator could not check a reference, the reachability
checker could not run, and the simulator would have to execute the game.

**A creator-defined statement carrying both.** Considered and prototyped in
thinking; not built. See ADR-0008.

## Consequences

**Good**

- Writers work in `.rpy` and never open a JSON file to write a scene.
- Tooling reads the metadata and never parses prose.
- Content is diffable: a storylet's conditions are a small file, reviewable
  alone.
- The reachability analysis is possible at all, which is what caught three real
  content bugs during this bootstrap.

**Bad, and accepted**

- Two files per storylet. Mitigated by `s32 explain <id>`, which prints both
  sides, and by the label naming convention making the pair obvious.
- The `id` ↔ `label` link is by name, so a rename must touch both. The validator
  catches a broken link immediately.
- Choice outcomes are declared twice — once as prose effects, once as metadata.
  This is real duplication, accepted because the alternative is analysis that
  silently reports live content as dead.
