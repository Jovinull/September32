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

**Storylet ids are permanent** once a storylet is `active`. They appear in saves.

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
