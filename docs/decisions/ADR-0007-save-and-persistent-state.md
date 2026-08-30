# ADR-0007 — Game state is plain containers, built through a seam

**Status:** Accepted · 2026-08-30 · **This one bit us**

## Context

Ren'Py implements rollback by substituting its own `RevertableDict` and
`RevertableList` for the builtins **inside Ren'Py's own Python blocks**. Code in
an ordinary imported package does not get that substitution: a `{}` written in
`s32_engine/state.py` is a plain `dict`.

A plain dict in the store saves correctly. It loads correctly. It does not roll
back. Nothing raises, nothing logs. The player scrolls up, the text rewinds, and
the world does not.

This is not hypothetical. The first implementation had exactly this bug, and it
was found by the `smoke_rollback` testcase asserting on state rather than on
text — which is the whole reason that test asserts on state.

## Decision

**No custom classes in game state, and no container literals in the engine.**

State is a nested tree of dicts, lists and scalars, typed with `TypedDict` for
mypy's benefit. Every container is created through `s32_engine.containers`:

```python
_dict_factory: Callable[..., Any] = dict  # headless default
_list_factory: Callable[..., Any] = list
```

At init, the Ren'Py bridge repoints them:

```python
from renpy.revertable import RevertableDict, RevertableList

s32.configure_containers(RevertableDict, RevertableList)
```

Headless tooling and pytest see ordinary builtins; the game sees revertable
ones. One codebase, both hosts, no `if renpy:` anywhere in the engine.

Saves loaded from disk arrive as whatever pickle produced, so
`migrate_state` runs `containers.adopt()` over the whole tree — otherwise
loading an old save would produce a session where rollback quietly stops
working, the same invisible bug by a different route.

### Randomness

`random` is banned. Its generator state lives outside the save, so rolling back
past a draw and replaying gives a *different* result. `s32_engine.rng.Rng` holds
no state: every draw is a hash of `(seed, counter)`, and the counter lives in
the ordinary game state that Ren'Py already rolls back. Same counter, same
number, always — which is also what makes `--seed` reproducible in the
simulator and "it happened on seed 4211" a complete bug report.

### Versioning

- `save_schema_version` — the shape of the run state. Migrations are ordered,
  forward-only steps in `state.migrate_state`.
- `META_SCHEMA_VERSION` — the shape of `persistent`. Its migration must never
  raise: a player whose persistent file is from a newer build must still be able
  to launch.
- Content is **not** versioned into saves. It is rebuilt from `data/` every
  launch, so editing a storylet does not invalidate a save; `sync_with_library`
  adds state for characters authored since.

## Alternatives

**Dataclasses or classes for state.** The obvious design, and it produces the
rollback bug. Ren'Py can be told to make a class revertable, but only from
inside Ren'Py — which would mean the engine could no longer be imported
headless, losing the simulator and the test suite.

**`renpy.random` directly.** Would work in-game and not at all in the simulator.

**Storing state in `persistent`.** A classic way to produce a save file that
contradicts itself.

## Consequences

**Good**

- Rollback, save and load work, and a test proves it walks the *whole* state
  tree rather than the parts we remembered.
- The engine runs headless, which is what the simulator and 131 tests depend on.
- Deterministic randomness: a seed reproduces a run exactly.

**Bad, and accepted**

- No methods on state. Logic lives in module functions taking state as the first
  argument. This reads slightly less nicely and is a small price.
- Every contributor must know the container rule. Hence this ADR, a rule in
  `AGENTS.md`, and `tests/test_containers_and_rollback.py`, which fails with the
  exact path of any container that bypassed the seam.
