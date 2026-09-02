# CLAUDE.md

Working notes for Claude Code in this repository.

**[`AGENTS.md`](AGENTS.md) is the binding document.** Read it first; this file is
the practical layer on top.

## Before anything

```bash
uv run s32 doctor
```

If it fails, fix that first. Then read
[`docs/production/PROJECT_STATE.md`](docs/production/PROJECT_STATE.md).

## Orientation

This is a visual novel with a quality-based narrative architecture. Two things
are unusual and both are load-bearing:

**The engine is standard-library only.** `game/python-packages/s32_engine/` is
imported by Ren'Py, which ships its own interpreter and cannot install wheels.
A test walks the package and fails on any third-party import. This is also what
lets the same code run in a headless simulator.

**Game state is plain containers, built through a seam.** Never a dataclass,
never a literal `{}`. `s32_engine.containers` supplies them, and Ren'Py repoints
the factories at its revertable types at init. Get this wrong and rollback
silently stops working — it already happened once.
[ADR-0007](docs/decisions/ADR-0007-save-and-persistent-state.md).

## Before calling anything done

```bash
uv run s32 doctor
uv run s32 validate
uv run ruff format --check . && uv run ruff check .
uv run mypy
uv run pytest
uv run s32 renpy lint
uv run s32 renpy test
uv run s32 simulate --runs 500
```

Or `uv run python scripts/check.py`.

All green, or say plainly what is not, and mark it `BLOCKED` / `PARTIAL` /
`FAILED` in `PROJECT_STATE.md`. Never write `DONE` without evidence.

## Adding content

**A storylet** needs two files:

```
data/storylets/<id>.json          conditions, effects, priority, tags
game/story/storylets/*.rpy        label s32_st_<id>:
```

Then `s32 validate`. It checks that every id exists, every condition parses,
every label is defined, and nothing is unreachable.

**Declare choice outcomes.** If a menu inside the scene changes state, it goes in
the storylet's `outcomes` list too. A change only the prose knows about makes
later content look dead, and the reachability report will say so — that is not
hypothetical, it happened during the bootstrap.

**A character** needs `data/characters/<id>.json` and a bible in
`docs/characters/`. Then `s32 assets images` to regenerate the Ren'Py image
definitions.

## Handing it to a person

The playtest build is the one artefact in this project that leaves the machine.

```bash
uv run s32 build
```

Three things it does that Ren'Py's `distribute` does not, each of which fails
silently if it stops happening: it mirrors `data/` into `game/data/` (a built
game with no content loads zero storylets and does not crash), it writes
`game/build_stamp.json` so a bug report can name the build, and it relies on the
exclusions in `options.rpy` to keep the repository out of the archive — the base
directory Ren'Py scans is this repo, and its own rules end with a catch-all.

**First match wins** in `build.classify`, and the scanner does not descend into
a directory it has excluded. Write `docs/`, never `docs/**`: the `**` form
leaves the directory itself unmatched and ships an empty folder.

`docs/production/PLAYTEST_BUILD.md` has the checklist. The item that matters is
unpacking the archive somewhere else entirely and running it there.

## Things that will bite

**Ren'Py `define` runs before any import.** `game/options.rpy` holds a literal
version string; a test keeps it in sync with `s32_engine.version.GAME_VERSION`.

**`init offset = -5` applies to unadorned `init` blocks.** A negative literal
(`init -4 python:`) runs *earlier*, not later. That produced a NameError at
launch once.

**Ren'Py text interpolation evaluates what is inside the brackets.**
`[d[key]]` looks up a *variable* named `key`. Compute into a local first.

**Ren'Py testcase assertions need `eval` and parentheses.**
`assert eval (x >= 1)`, never `assert x >= 1`.

**Randomness goes through `s32_engine.rng.Rng`.** Never `random` — its state is
outside the save, so rolling back and replaying gives a different answer.

**Storylet ids are permanent** once a storylet is `active`. They appear in saves
— and, since Milestone 5, in playtest reports. Renaming one during a wave
silently breaks the comparison between two testers.

**The playtest recorder lives in `persistent`, not in the run state.** It has to
survive quitting, and it must *not* be rolled back: what a tester did includes
the parts they took back. Every recorder goes through `s32_pt_run()`, which is
where consent is checked, so a new one cannot forget to.

**Record state, not call sites.** `s32_pt_commitments()` reads
`S32State["commitments"]` rather than hooking `promise()`, because a storylet's
declared `commit(...)` effect never goes near that verb. The first version
hooked the verb and reported runs with a commitment in the state and none in
the report.

## The hard rules

From `AGENTS.md`, repeated because they are the ones with consequences:

- **No AI in the shipped game.** No model, no API, no network. Ever.
- **Never invent canon.** Not even as an implication in a line of narration.
  Propose it in `docs/canon/OPEN_QUESTIONS.md` instead.
- **Never send third-party artwork to an AI service.** Not for analysis, not for
  "just looking at it". The audit tooling is local and deterministic for exactly
  this reason.
- **Never commit third-party binaries.**
- **Never push, release, or publish** without being asked.

## When a scene will not fire in the game rather than in the tools

The simulator never opens a `.rpy`. `renpy lint` never runs one. For four
milestones that meant the prose was checked by nothing, and the game's `start`
label played six time slots and stopped — three of the five anchors had never
fired outside the simulator while every gate was green.

`game/story/act1.rpy` is the loop that plays the week, and
`uv run s32 renpy test act1_golden` plays it end to end in about thirteen
seconds. It is the only test that executes a scene.

## When a scene will not fire

```bash
uv run s32 explain <storylet_id>
```

In-game, `Shift+S` shows every storylet, its eligibility, and which clause failed
with the actual value. `Shift+C` shows characters, relationships and beliefs;
`Shift+W` shows world state. Developer mode only — they are absent from a release
build, not hidden.

## Style

Match the surrounding code. In short: full sentences in docstrings, comments that
explain *why* rather than what, no abstraction with one implementation, and a
dict where a dict will do.

For prose, `docs/style/` is the authority. The register is warm, understated, and
never tells the reader that something is wrong.
