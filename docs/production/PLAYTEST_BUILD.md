# The playtest build

How a build somebody outside the project can run gets made, and what has to be
true before one is sent.

## Version

```
0.2.0-playtest.1
```

The milestone brief suggested `0.0.5-playtest.1`. It is not what was used,
because it sorts *before* the `0.1.0-prototype` it succeeds, and a version that
goes backwards is one nobody can reason about six months later. `0.2.0` keeps
the project's existing convention — semver with a prerelease tag — and
`playtest.1` is the counter that increments if a second build has to go out
during the wave.

`s32_engine.version.GAME_VERSION` is the source of truth.
`game/options.rpy` restates it as a literal because Ren'Py evaluates `define`
before any import can run, and `tests/test_content_and_tooling.py` fails if the
two drift.

Any correction after a build has been sent is `0.2.0-playtest.2`. **A build that
has gone out is never modified in place.**

## Making one

```bash
uv run python scripts/check.py     # all eleven gates, first
uv run s32 build                   # pc by default
uv run s32 build --packages pc linux
uv run s32 build --prepare-only    # mirror and stamp, no Ren'Py
```

Three things happen that Ren'Py's own `distribute` does not do, and each is a
way the build could ship broken and silent.

**The content is mirrored.** `data/` sits beside `game/` in the repository and
the engine finds it there; a distribution has no repository, so the build copies
it into `game/data/`. Without this the built game loads zero storylets and the
director selects nothing — which is not a crash, and would therefore reach a
tester. `s32tools.build.MIRRORED` lists the kinds, and a test fails if a new
directory appears under `data/` that it does not name.

**The build stamps itself.** `game/build_stamp.json` carries the version, a
build id and the commit hash; `game/engine/03_s32_build.rpy` reads it back at
init and the main menu shows it. A bug report that says "the one you sent me" is
worth very little.

Both files are generated and gitignored. A committed mirror would be loaded in
preference to the real content — the engine checks the game directory first —
and would be invisible to every tool in the project, all of which read `data/`.
A committed stamp would name the commit that contains it, which is not a thing
that can be true.

**The repository does not ship.** The base directory Ren'Py scans is a working
repository. Its own default rules end with a catch-all that sweeps everything
into the distribution, so without the exclusions in `game/options.rpy` a tester
would receive the canon, the character briefs, the internal reports, every scene
card and every milestone post-mortem.

Two details about those rules decide their shape. **First match wins**, so the
three documents a tester is meant to receive are classified *above* the sweep
that would otherwise catch them. And the scan does not descend into a directory
it has excluded, so each exclusion is written `docs/` rather than `docs/**` —
the `**` form leaves the directory itself unmatched and ships an empty folder
named after the thing that was supposed to be private.

`tests/test_playtest_build.py` lists the repository root and fails on an entry
no rule accounts for. A directory added next year is a failing test rather than
a leak.

## What the tester receives

```
September32-Act1-Playtest-0.2.0-playtest.1-pc/
    September32.exe
    lib/
    game/
    PLAYTEST_README.md
    FEEDBACK_INSTRUCTIONS.md
    THIRD_PARTY_NOTICES.md
    LICENSE
```

And nothing else. In particular not `docs/playtest/` — every document in there
names the answer it is hoping for.

## What it must not contain

```
vendor archives          the download cache        licence evidence
PSD / KRA source files   source asset packs        internal reports
canon documents          scene cards               developer notes
game/testcases/          any AI prompt
```

The vendor archives matter most. The Potat0Master licence forbids
redistributing the files in the form they were downloaded or in a modified form,
so the packs may only ship as part of the game. `assets/` is excluded, the
processed derivatives live under `game/images/vendor/` and go into the archive,
and `s32 assets verify` is one of the eleven gates.

`game/testcases/` is the other one worth naming. It holds the harness that
answers menus automatically for the golden path, and that harness is only safe
to have at all because it cannot reach a build.

## Placeholders

The build ships with labelled placeholder art. That is deliberate and is said
plainly in three places: the splash, the About screen, and `PLAYTEST_README.md`.

It is **not** said inside the fiction. Repeating it in a scene would make the
game apologise for itself, which changes how the scene reads and therefore
changes what the playtest measures. A test asserts that no line in `game/story/`
mentions a placeholder.

The class photograph is the important one. It is `P0` in
[`ART_PRODUCTION_PLAN.md`](ART_PRODUCTION_PLAN.md), it is the object the premise
turns on, and it is currently a labelled box. Whether that blunts the ending is
question G3 on the deep questionnaire and it is the one art question this wave
can settle.

## Expected playtime

Measured, not guessed:

```bash
uv run python scripts/playtime.py
```

Across 360 completed runs — nine profiles at forty seeds — a playthrough is a
median of **46 scenes and 12,750 spoken words**, range 8,650 to 15,971.

| Reading speed | Median | Range |
| --- | --- | --- |
| 200 wpm | 64 min | 43–80 min |
| 240 wpm | 53 min | 36–67 min |
| 300 wpm | 42 min | 29–53 min |

Menus, travel, the day cards and the time somebody spends deciding are on top of
that. `PLAYTEST_README.md` therefore says **an hour to an hour and a half**,
which is the honest shape of it rather than a single number.

Every one of those 360 runs reached the end of the act.

## Before a build is sent

The full sequence, in order. It is a checklist because the interesting failures
are the ones that only appear outside the repository.

1. `uv run python scripts/check.py` — all eleven gates
2. `uv run s32 renpy test act1_golden` — a full week, played by Ren'Py
3. `uv run s32 build`
4. Unpack the archive **somewhere else entirely** and run it there. Not in the
   repository, not next to it. A build that quietly depends on `uv`, on a local
   Python, on the SDK, or on `data/` sitting beside it will work perfectly in
   the checkout and fail on the first machine it reaches.
5. Fresh profile: delete the save directory, start a new game, answer the
   consent question, save, load, roll back, open the calendar, open a document,
   reach the end of the act, generate a report.
6. Open `playtest-report.json` and read it. Then run
   `uv run s32 playtest summarize` on it.
7. Record the version, build id, commit, size and SHA-256 below.

## Build register

Every build that has been produced. **A build that has gone out is never
modified in place**: a correction is a new row and a new version, so that a bug
report can always be matched to the exact bytes the tester ran.

| Version | Build id | Commit | Package | Size | SHA-256 | Sent to |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

## If a build has to be replaced mid-wave

1. Fix, commit, bump to `playtest.2`.
2. Rebuild and re-run the checklist in full. Not the parts that seem relevant —
   the whole thing.
3. Add a row above and mark the old one superseded.
4. Tell every tester which build they have. A report from `playtest.1` and one
   from `playtest.2` are not directly comparable, and the report says which is
   which so that they do not get averaged by mistake.

Storylet ids do not change during a wave. They appear in reports, and renaming
one would silently break the comparison between two testers.
