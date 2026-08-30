# Project state

**Read this before starting work.** Last updated: 2026-08-30.

## Summary

Bootstrap complete. The game runs, the engine works, the tooling works, and every
quality gate is green. There is a five-to-fifteen-minute vertical slice that
exercises every system end to end.

What exists is infrastructure and a proof. What does not exist is a game.

## Engine

| | |
| --- | --- |
| Ren'Py | **8.5.3** (stable, verified on renpy.org 2026-08-30) |
| SDK location | `.tools/renpy/renpy-8.5.3-sdk` (gitignored) |
| SDK SHA-256 | `ff57648f9c04f27e381c48af6d8e3ee3cdec296bed4d3831f47f09b0a71b505e` |
| Resolution | 1920 × 1080 |
| Python (tooling) | 3.12 via uv |

## What works

**Narrative engine** — `game/python-packages/s32_engine/`, standard library only,
importable by both Ren'Py and the headless tooling.

- Storylet director: eligibility, priority tiers, weighted selection, cooldowns,
  repeat damping, and a full explanation trace.
- Eight-axis directed relationships, including NPC-to-NPC.
- Five-stance knowledge model with per-agent beliefs and contradiction detection.
- Commitments: made, kept, broken, excused, expired.
- Player traits, accumulated rather than chosen.
- World state: day, calendar day, time slots, weather (Markov chain), phase.
- Rollback-safe containers and counter-based deterministic RNG.
- Save migration and cross-run `persistent` meta scaffolding.

**Tooling** — `s32` CLI: `doctor`, `validate`, `schemas`, `simulate`,
`coverage`, `graph`, `explain`, `report`, `assets *`, `renpy *`.

**Assets** — 11 packs fetched from official sources, hashed, licence evidence
recorded, processed and installed. 968 files in the game tree.

**The slice** — arrival, first shift in the archive, director-driven storylets,
a photograph, a promise, an ending note. Marked PROTOTYPE / NON-FINAL in-game.

## Verified, with numbers

| Gate | Result |
| --- | --- |
| `uv run pytest` | **131 passed** |
| `uv run ruff check .` | **clean** |
| `uv run ruff format --check .` | **clean** |
| `uv run mypy` | **clean, 61 files, strict** |
| `s32 validate` | **0 errors, 0 warnings**, 6 info |
| `s32 renpy lint` | **clean** |
| `s32 renpy test` | **5/5 testcases passed** |
| `s32 simulate --runs 1000` | **7/7 storylets reachable, 0 dead ends**, ~16s |
| `s32 doctor` | **0 failures, 0 warnings** |

## Content

| | |
| --- | --- |
| Storylets | 7 (all `prototype`) |
| Anchors | 3 |
| Characters | 6 (5 with art) |
| Locations | 8 |
| Knowledge facts | 7 |
| Items | 3 |

## Known gaps

**Content.** Seven storylets is a demonstration, not a game. Four characters have
no storylet of their own; three locations have none.

**Art.** Three characters have no casual outfit; one has no sprite; there is no
male-presenting sprite in a compatible style; the archive room is played by a
club room; the class photograph does not exist. See `ART_GAP_ANALYSIS.md`.

**Audio.** Five tracks. Nothing for investigation, romance, or the later phases.
No sound effects.

**UI.** Kenney scaffolding. The archive document viewer — the second most
important interface in the game — is unbuilt. So is the calendar.

**Canon.** Deliberately open. The nature of September 32 is undecided, and
`PHENOMENON_RULES.md` exists so that writing can proceed without it.

**`purp`.** One source expression token is unmapped because its meaning cannot be
determined from the filename. Two minutes and a human. `ASSET_NAMING.md`.

## Blocked

Nothing is blocked. Every download succeeded, including the ones that initially
looked blocked — two itch.io packs returned 404s that turned out to be rate
limiting, and one returned a corrupted URL because a percent-encoded `/` was
being decoded.

## Bugs found during the bootstrap

Recorded because they are the strongest evidence that the tooling earns its keep:

1. **Rollback silently did nothing.** Run state was built from plain dicts, which
   Ren'Py saves and loads perfectly and does not revert. Found by a testcase
   asserting on state rather than on text. Fixed with the container seam
   (ADR-0007) and now guarded by a test that walks the whole state tree.
2. **A scene gated on rain, in a world with no weather.** Found by the simulator.
   Fixed by building a weather model, and by teaching the static analyser to
   check weather requirements.
3. **A threshold nothing could reach.** `iris.trust >= 12` when the content could
   produce at most 10, because the trust came from choices inside prose the tools
   could not see. Fixed by declared `outcomes` (ADR-0006) and by tightening the
   static analyser's relationship ceiling.
4. **81% of simulated runs dead-ended.** The model of a player wandered at
   random. Fixed by modelling what a player actually does — go where something is
   happening — which turned out to be a real design requirement, not a
   simulation artefact.

## Next milestone

**Fifteen storylets and the archive document viewer.**

Not more systems. The systems work and are over-built relative to the content.
What the project needs next is to find out whether the *writing* works at volume:

1. Storylets for june, noah and mara — the three characters with no content.
2. Content for dorm_room and town_road.
3. The archive document viewer, with procedurally-generated paper. It is the
   game's most distinctive interface and it can be built without an artist.
4. Then re-run `s32 simulate` and read the content mix against
   `docs/narrative-design/PACING.md`. If fifteen storylets produce a sensible
   ordinary phase, the architecture is proven and the answer is more writing.
