# Architecture

## The shape

```
                        ┌───────────────────────────────┐
                        │        s32_engine             │
   data/*.json  ──────► │  pure Python, stdlib only     │
   (authored content)   │  no mutable state of its own  │
                        └───────────┬───────────────────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 ▼                                     ▼
       ┌───────────────────┐                 ┌────────────────────┐
       │  Ren'Py           │                 │  s32tools          │
       │  presents         │                 │  validates,        │
       │  owns the state   │                 │  simulates,        │
       │  rolls back       │                 │  reports           │
       └───────────────────┘                 └────────────────────┘
```

One engine, two hosts. That is the whole design, and everything unusual about
this codebase follows from it.

## Why the engine is standard-library only

Ren'Py ships its own Python interpreter. It cannot `pip install`. So an engine
importable by Ren'Py must have no third-party dependencies.

That constraint turned out to be a gift: the same code runs headless, which is
where the 131 tests, the reachability analysis and the thousand-run simulator
come from. A test asserts the constraint holds by walking the package's imports.

## Why the engine owns no state

The engine is a library of pure functions over a state tree it does not own. The
host owns the state — Ren'Py in the game, the simulator in the tooling.

This is what makes `NarrativeDirector` stateless enough for one instance to drive
a thousand parallel simulated runs, and it is what keeps Ren'Py's rollback from
ever encountering an object it does not control.

## The container seam

Ren'Py implements rollback by substituting `RevertableDict` and `RevertableList`
inside its own Python blocks. Code in an imported package does not get that
substitution.

So `s32_engine.containers` supplies `new_dict()` and `new_list()`, defaulting to
the builtins, and the Ren'Py bridge repoints them at the revertable types at
init. Headless tooling sees ordinary dicts; the game sees revertable ones; there
is no `if renpy:` anywhere in the engine.

This is not a stylistic preference. Without it, rollback silently does nothing —
which is what happened, and what
[ADR-0007](../decisions/ADR-0007-save-and-persistent-state.md) is about.

## Modules

| Module | Responsibility |
| --- | --- |
| `types` | Enums, authored-content dataclasses, runtime `TypedDict`s. |
| `containers` | The rollback seam. |
| `definitions` | Loads `data/*.json` into an immutable `ContentLibrary`. |
| `state` | Creates, mutates and migrates the run state. |
| `conditions` | The requirement grammar. Matched, never `eval`ed. |
| `effects` | The effect grammar. Same. |
| `director` | Eligibility, priority tiers, weighted selection, the trace. |
| `relationships` | Eight directed axes and derived readings. |
| `knowledge` | Five stances, per agent, with a transition table. |
| `commitments` | Promises and their outcomes. |
| `traits` | Accumulated player tendencies. |
| `world` | Weather, and finding where content is. |
| `meta` | Cross-run `persistent` state. |
| `rng` | Counter-based, rollback-safe randomness. |
| `devlog` | Structured developer logging. Off in release. |

## Why the grammars are not `eval`

Requirements read like `rel iris.trust >= 10`. They are matched against a fixed
table of forms, not evaluated as Python.

The reason is not safety — we write the content. It is **analysability**. Because
every condition declares what state it reads, the static checker can tell that
`knows(old_letter)` is unsatisfiable when nothing grants `old_letter`. An
arbitrary Python expression could not be checked that way, and the checking is
what makes a quality-based narrative maintainable past thirty scenes.

## Three layers of checking

Each found a real bug during the bootstrap.

**1. Cross-reference validation** — every id named by a condition or effect
exists; every storylet's label is defined; every declared cooldown does something.

**2. Static reachability** — a monotone fixed point over what content can grant.
Sound in the direction that matters: if it says unreachable, it is. It catches a
threshold nothing can reach.

**3. Simulation** — a thousand headless playthroughs across nine player profiles.
It catches what the static pass over-approximates, and reports the content mix
against the pacing budget.

## Data flow at runtime

```
launch          load data/ → ContentLibrary (immutable, not saved)
new game        new_state() → GameState (plain containers, saved)
time passes     advance_time() → weather rolls on a new day
director runs   evaluate every storylet → priority tier → weighted pick
scene plays     renpy.call(storylet.label)
scene returns   apply effects, record history
rollback        Ren'Py reverts the containers; the engine is not involved
save / load     pickle the state; migrate_state() on load
```

## Where things live

```
game/python-packages/s32_engine/   the engine
game/engine/                       the Ren'Py bridge and generated definitions
game/story/                        prose: anchors, storylets, the prototype
game/screens/                      credits, developer inspectors
game/testcases/                    Ren'Py smoke tests (excluded from builds)
data/                              authored content + generated JSON Schemas
tools/s32tools/                    the dev toolchain behind `s32`
tests/                             131 tests
```

## What is deliberately absent

**A creator-defined statement.** [ADR-0008](../decisions/ADR-0008-creator-defined-statements.md)
— it would duplicate the JSON and make the tooling parse Ren'Py script.

**An ORM, a database, a config framework.** The content is a few dozen JSON files
and it fits in memory in milliseconds.

**Any network code.** [ADR-0004](../decisions/ADR-0004-no-runtime-ai.md).

**Abstraction with one implementation.** There is one director, one state shape,
one host that matters. Interfaces would be decoration.
