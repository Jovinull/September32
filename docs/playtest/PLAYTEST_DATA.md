# Playtest data

What the build records, what it refuses to record, where it goes, and how any of
that is enforced rather than promised.

The tester-facing version of this is `FEEDBACK_INSTRUCTIONS.md`, which ships
with the build. This one is for whoever maintains the code.

## The shape of it

`s32_engine/playtest.py` is the whole model: a `TypedDict` for the report, a
`TypedDict` per run, a session-code derivation, a privacy check and two
renderers. Standard library only, like the rest of the engine, so the same code
is exercised by `pytest` and by the game.

`game/engine/04_s32_playtest.rpy` is the recorder. It lives in `persistent`,
which is the correct home for two reasons: it survives quitting, which the run
state does not, and **it is not rolled back**. What a tester did includes the
parts they took back, and a notebook that unwrites itself when somebody scrolls
up is not a record of anything.

`game/screens/playtest.rpy` is the consent question and the end-of-act screen.

## Consent

Three states, and the third one is load-bearing:

| `persistent.s32_playtest_consent` | Meaning |
| --- | --- |
| `None` | Not asked yet. This is what makes the question appear exactly once. |
| `True` | Recording. |
| `False` | Not recording, and the report was deleted rather than paused. |

The question is asked once per installation, immediately after `Start` and
before the first line of the game, by `label s32_playtest_consent`. Declining
leaves the game entirely playable, which is what makes it a real answer rather
than a dark pattern with two buttons.

Declining **deletes** any existing report. Somebody who says no should not have
a file about them sitting in their save folder.

Every recorder goes through `s32_pt_run()`, which returns `None` when consent is
absent. That is one gate rather than fifteen, and it is why a new recorder
cannot forget to check.

## What is recorded

Per run:

```
index              which playthrough this is
seed               the run's RNG seed -- makes any bug reproducible exactly
completed          reached the end of Act 1
first_completed    true for the first completed run only
days_reached
active_seconds     renpy.get_game_runtime(), which excludes menu time
scenes             storylet and anchor ids, in order
anchors            the five mandatory beats
choices            stable choice ids, including travel
documents          archive documents opened, in order
archive_reopens    how many of those were re-readings
calendar_opens
journal_opens
commitments_made / _kept / _broken
loads              saves reloaded
```

Per report: the schema version, the build stamp (version, build id, commit,
save-schema version), the session code, and the consent flag.

### Choice ids

`playtest.choice_id(storylet_id, index, caption)` produces:

```
iris_the_second_box.0.take-the-lid-off
```

Three parts because each is unreliable alone. The storylet id is permanent once
a storylet is active, so it is the anchor. The index is Ren'Py's own option
index and survives a typo fix in the caption. The slug is what makes a report
readable without opening the script, and it is what visibly changes if somebody
rewrites an option — which is exactly when reports from two builds should stop
being comparable.

The alternative was an explicit `$ choice("...")` in each of the fifty menus.
That was rejected: Milestone 5's instruction was to leave the writing alone, and
a hundred and fifty insertions into scene files is not leaving it alone. The
recorder hooks the store's `menu` instead, which is the same seam nvl mode uses.

Travel is recorded in the same list as `travel.<location_id>`, so a report reads
as one sequence of decisions rather than as dialogue with the navigation
missing.

### Commitments are read from the state

Not hooked at the `promise()` verb. There are two ways to make a promise and
only one of them is that verb: a storylet's declared `commit(...)` effect goes
through the effects engine. The first version hooked the verb, and the golden
path duly produced a run with a commitment in its state and none in its report.
`s32_pt_commitments()` now syncs from `S32State["commitments"]`, which is
authoritative for every path.

## What is never recorded

```
name            email           IP address
MAC address     hardware id     Windows or POSIX username
file paths      documents       browser data
location        machine fingerprint
wall-clock time of any kind
```

Durations are accumulated elapsed seconds. **No absolute time is stored
anywhere.** That is two things at once: a report stays reproducible from a
fixture, and the file cannot say when somebody was awake.

It is also a lesson from Milestone 3, where `THIRD_PARTY_NOTICES.md` embedded
`datetime.now()` and the credits gate failed every midnight. A wall clock in a
generated artefact is a bug waiting for a date.

## How the privacy rule is enforced

`playtest.privacy_violations()` serialises the whole report and searches it for
absolute paths, email addresses, IP addresses, machine-identifier words and
ISO timestamps. It checks the *serialised* form rather than the structure,
because the risk is not a field somebody added on purpose — it is a value that
arrived inside one. A save path used as a document id would pass any
field-by-field review and fail this.

`s32_export_report()` **refuses to write the file** if the check returns
anything. Not a warning: a check that can be clicked past is not a check.

`tests/test_playtest_privacy.py` runs the same check against synthetic reports,
against a deliberately poisoned one, and against the report the golden path
produces.

## No network

There is none. Not disabled, not configured off — absent.

`tests/test_playtest_privacy.py` walks every module in `s32_engine` and every
`.rpy` in the game tree and fails on `socket`, `urllib`, `http`, `requests`,
`ssl`, `ftplib`, `smtplib`, `telnetlib`, `xmlrpc`, or a literal `http://` or
`https://` outside a comment. The engine's existing standard-library-only test
covers the first half of that already; this covers the game tree, which nothing
had been checking.

**Feedback goes to no model.** No tooling in this repository sends a tester's
words anywhere. `s32 playtest summarize` counts and lists; it does not classify
sentiment and it does not summarise prose. If the developer later wants a
model's opinion on a particular question, that is a deliberate act with a
specific extract, not a default of the pipeline.

## Where the files go

The player's save directory — `config.savedir`. Per-user, already writable,
already exists, and somewhere a tester can be talked to over a message.

```
%APPDATA%\RenPy\September32-1\playtest-report.json      Windows
~/.renpy/September32-1/playtest-report.json             Linux
```

Two files, both written by **Generate playtest report** on the end-of-act
screen:

- `playtest-report.json` — what `s32 playtest summarize` reads
- `playtest-summary.md` — the same facts, readable

The Markdown exists so a tester can see exactly what they would be sending
before sending it. Being able to read your own report is most of what makes the
consent meaningful, and `FEEDBACK_INSTRUCTIONS.md` asks them to.

## Collecting it

```
playtests/
    raw/          one directory per session code -- GITIGNORED
    aggregate/    filled-in analysis templates
```

`playtests/raw/` is gitignored, and there is no automation that could put a real
person's words into version control by accident. Synthetic material for the
tests lives in `tests/fixtures/playtests/` and every file there says `SYNTHETIC`
in its session code and in a `note` field, so that a fixture can never be
reported as a tester.

## The summarizer

```
uv run s32 playtest summarize playtests/raw
uv run s32 playtest summarize path/to/playtest-report.json
```

Validates each file against `playtest.validate()` first and refuses anything it
does not recognise rather than half-reading it. Then it counts: completion rate,
playtime, scene coverage, which scenes everybody saw and which only one person
did, calendar and archive usage, commitments, and the divergence figure H06 is
measured by.

It deliberately does **not** read questionnaires. Free text is a person's job.

## Schema versioning

`PLAYTEST_REPORT_SCHEMA_VERSION` in `s32_engine/version.py`. Bump it when the
report's shape changes.

A stored report from an older schema is **not** migrated. It belongs to a build
that is no longer the one being tested, and merging the two would produce a file
that describes neither; the recorder discards it and starts again. That is the
opposite of the policy for save games, and deliberately so — a save is the
player's, and a report is a measurement of one build.
