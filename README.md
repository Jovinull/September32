# September 32

> September has thirty days. Your school has records of one more.

A visual novel in early development. A student arrives at a small residential
school and is assigned to digitising the archive — photographs, yearbooks,
ledgers, decades of administrative sediment. The job is tedious, the people doing
it are interesting, and for a while that is the whole game.

**This repository is infrastructure and a vertical slice, not a game.** The
scenes present exist to exercise the systems.

---

## What is here

| | |
| --- | --- |
| **Engine** | Ren'Py 8.5.3, 1920×1080, Windows / Linux / macOS |
| **Narrative architecture** | Quality-based narrative: storylets, anchors, a director |
| **Toolchain** | Python 3.12, uv, Ruff, mypy, pytest |
| **Tooling** | Validation, static reachability analysis, headless simulation, coverage, graph export, asset pipeline with licence tracking |

Two things worth knowing up front:

**No AI runs in the game.** Every line is pre-written and committed. AI was used
heavily to *build* this; the shipped product contains no model, no API and no
network access at all. [ADR-0004](docs/decisions/ADR-0004-no-runtime-ai.md).

**No third-party binaries are committed.** Most of the asset licences permit use
in a game and forbid redistributing the files. `s32 assets fetch` reconstructs
everything from official sources. [ADR-0003](docs/decisions/ADR-0003-asset-licensing.md).

---

## Getting started

### 1. Install uv

<https://docs.astral.sh/uv/getting-started/installation/>

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Set up the toolchain

```bash
uv sync
```

That is the whole Python setup. Everything below runs through `uv run s32`.

### 3. Install Ren'Py

```bash
uv run s32 renpy install
```

Downloads the pinned 8.5.3 SDK (~163 MB) to `.tools/renpy/`, verifying its
SHA-256. Already have one? Set `S32_RENPY_SDK` to its path instead.

### 4. Install the assets

```bash
uv run s32 assets fetch      # ~90 MB from official sources, hashes recorded
uv run s32 assets install    # extract, process, copy into game/
uv run s32 assets images     # regenerate the Ren'Py image definitions
```

Automatic, from each creator's own page. No account, no mirrors, no scraping
around anything — `fetch` uses the public download flow and verifies every file
against the SHA-256 recorded in `assets/catalog/acquisition.toml`.

**The game runs without any of this.** Every missing image becomes a labelled
`MISSING ASSET` placeholder, missing music is silent, and missing fonts fall
back to a bundled face. Lint and all six testcases pass in that state, which is
also how CI runs.

**If a download fails** — a page moved, a pack went behind a purchase — `fetch`
prints the exact page, the exact file to pick and where to save it, then carries
on with the rest. Drop the file in `assets/.downloads/<asset id>/` and run
`s32 assets install`: it records the hash and proceeds exactly as if it had been
fetched.

### 5. Check everything

```bash
uv run s32 doctor
```

```
[  ok  ] python                     3.12.10 on Windows
[  ok  ] ren'py sdk                 8.5.3.26051504
[  ok  ] content                    15 storylets, 3 anchors, 6 characters, 9 facts, 8 locations, 3 items
[  ok  ] content validation         no findings
[  ok  ] asset manifest             12 entries, 11 installed
[  ok  ] asset licensing            evidence and terms recorded for every entry
[  ok  ] installed assets           audio: 6, background: 282, character: 720, ...
[  ok  ] credits                    CREDITS, NOTICES, game credits all current
[  ok  ] json schemas               generated schemas match the engine's enums
```

### 6. Play it

```bash
uv run s32 renpy run
```

---

## Commands

### Content

```bash
uv run s32 validate            # schemas, cross-references, reachability
uv run s32 explain <storylet>  # one storylet's conditions and effects
uv run s32 schemas             # regenerate JSON Schemas from the engine's enums
```

### Analysis

```bash
uv run s32 simulate --runs 1000 --seed 1234
uv run s32 coverage --runs 300
uv run s32 graph                # Mermaid; --format dot for Graphviz
uv run s32 report               # everything at once
```

`simulate` runs headless playthroughs across nine player profiles and reports
what a player can actually reach. It is the tool that makes this architecture
maintainable — it found three real content bugs during the bootstrap.

### Assets

```bash
uv run s32 assets fetch [--group characters|backgrounds|cc0|audio|fonts]
uv run s32 assets install
uv run s32 assets verify        # hashes, evidence, licence hygiene
uv run s32 assets credits       # regenerate CREDITS, NOTICES, in-game credits
uv run s32 assets evidence      # regenerate per-asset licence evidence
uv run s32 assets images        # regenerate Ren'Py image definitions
uv run s32 assets audit         # measure character-art consistency
uv run s32 assets sheets        # contact sheets
```

### Ren'Py

```bash
uv run s32 renpy lint
uv run s32 renpy test           # every testcase under game/testcases/
uv run s32 renpy test act1_golden   # a whole week, played by Ren'Py
uv run s32 renpy run
```

`act1_golden` is the only regression test that runs the *prose*. Everything else
about a scene is checked without executing it, so until Milestone 5 a NameError
inside a storylet would have reached a player before it reached anybody else.

### Playtest

```bash
uv run s32 build                # a distributable Act 1 playtest build
uv run s32 build --prepare-only # mirror content and stamp, no Ren'Py
uv run s32 playtest summarize   # aggregate reports testers sent back
uv run python scripts/playtime.py   # how long a playthrough actually is
```

`build` mirrors `data/` into the game tree, stamps the build with its version
and commit, and runs Ren'Py's distributor. See
[`docs/production/PLAYTEST_BUILD.md`](docs/production/PLAYTEST_BUILD.md) for the
checklist that has to pass before a build is sent to anybody.

`summarize` counts and lists. It does not interpret free text, and no tooling in
this repository sends a tester's words anywhere.

### Quality

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
```

Or `scripts/check.py`, which runs all of them and the content gates.

---

## Architecture

```
game/
  python-packages/s32_engine/   the narrative engine — pure Python, no deps
  engine/                       the Ren'Py bridge (state, verbs, generated images)
  story/                        the prose: anchors, storylets, the prototype
  screens/                      credits, developer inspectors
  testcases/                    Ren'Py smoke tests
data/                           authored content as JSON, plus generated schemas
tools/s32tools/                 the dev toolchain behind `s32`
tests/                          131 tests
docs/                           canon, characters, style, decisions, legal
assets/catalog/                 the licence record (binaries are NOT committed)
```

**The engine is standard-library only**, because Ren'Py ships its own interpreter
and cannot install wheels. That constraint is what lets the same code run inside
the game *and* inside a headless simulator — which is where the tests, the
reachability analysis and the coverage reports come from.

### How a scene gets chosen

A **storylet** is a written scene plus a declaration of the situation it belongs
in. Metadata lives in `data/storylets/*.json`; the prose lives in a Ren'Py label.

```json
{
  "id": "rain_after_school",
  "label": "s32_st_rain_after_school",
  "location": "rooftop",
  "time_slots": ["evening"],
  "requirements": ["weather == rain", "rel iris.trust >= 10", "knows(old_photo_exists)"],
  "effects": ["rel iris.trust += 5", "know(iris_keeps_a_second_index, iris_told_me)"]
}
```

The **director** evaluates which storylets fit the current state and picks one.
**Anchors** are ordered beats that must happen, carrying the dramatic shape that
a purely emergent system lacks.

Content scales **additively**: a new scene is a new file, not an edit to a
branching tree.

When a scene does not fire, ask:

```bash
uv run s32 explain rain_after_school
```

And in the game, `Shift+S` opens the storylet inspector, which shows every scene,
whether it is eligible, and which clause failed with the actual value.

---

## Documentation

Start with [`docs/production/PROJECT_STATE.md`](docs/production/PROJECT_STATE.md)
— what exists, what is verified, what is next.

| | |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Rules for anyone working on this, human or AI. **Read before contributing.** |
| [`docs/decisions/`](docs/decisions/) | Eight ADRs: why Ren'Py, why storylets, why no AI at runtime, why the state is plain dicts. |
| [`docs/canon/`](docs/canon/) | The story bible, with explicit `CANON` / `PROVISIONAL` / `IDEA` markers. |
| [`docs/style/`](docs/style/) | How to write dialogue, horror, romance, mystery, humour. |
| [`docs/legal/`](docs/legal/) | Asset licensing, the AI policy, privacy. |
| [`docs/references/`](docs/references/) | Original analysis of sixteen games and seven public-domain works. |

---

## Licence

**Provisional and conservative.** See [`LICENSE`](LICENSE) and
[`docs/legal/LICENSING.md`](docs/legal/LICENSING.md).

Third-party assets remain under their own terms, recorded in
[`assets/catalog/assets.toml`](assets/catalog/assets.toml) with evidence in
`assets/evidence/`. See [`CREDITS.md`](CREDITS.md) and
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md), both generated from the
manifest.

Made with [Ren'Py](https://www.renpy.org/).
