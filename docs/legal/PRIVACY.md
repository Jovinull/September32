# Privacy

## The whole policy

**September 32 collects nothing, stores nothing about the player, and never
connects to the internet.**

## What that means concretely

The game has:

- no account, no login, no profile;
- no telemetry, analytics, crash reporting or usage statistics;
- no network code of any kind — not for updates, not for leaderboards, not for
  anything;
- no advertising or third-party SDKs.

Saves and preferences are ordinary files in Ren'Py's save directory
(`config.save_directory = "September32-1"`), on the player's own machine. They
are never transmitted anywhere, because there is no code capable of transmitting
them.

## How it is enforced

`s32_engine` is standard-library only, and a test walks every module in the
package and fails on an import of `socket`, `urllib`, `http`, `ftplib`,
`smtplib`, `asyncio` or `ssl`.

Since Milestone 5 the same check covers the **whole game tree**, not just the
engine: `tests/test_playtest_privacy.py` reads every `.rpy` as well, and fails
on a bare URL in any line that is not a comment. The one exception is named
rather than pattern-matched — `credits_data.rpy`, where several bundled
licences require an attribution link to be *shown* — so adding a second is a
decision somebody has to make on purpose.

`AGENTS.md` forbids adding a network call. A pull request that added one would
be rejected on sight.

This is not primarily a privacy stance. It falls out of
`docs/decisions/ADR-0004-no-runtime-ai.md`: a single-player game should not need
a connection to tell its story, and a player should not have to wonder what is
being sent anywhere. Privacy is what you get for free when there is nothing to
send.

## Development analytics

The simulator and coverage tools produce statistics — scenes reached,
relationship distributions, dead ends. These are generated from *simulated*
playthroughs on a developer's machine, written to `tools/reports/`, and have no
connection to any player.

## The private playtest report

Added in Milestone 5, and the one thing on this page that observes a real
session. It is written down here in specifics, before the section below asks
for exactly that.

A build handed to a private tester asks them, once, whether the game may keep a
report on their computer. If they say yes it records which scenes they saw,
which options they took, which documents they opened, how far through the week
they got, and roughly how many seconds the game was in front of them. The file
is written into their own save directory when they ask for it, and it stays
there.

**It changes nothing above.** There is still no network code: the report cannot
be sent by the game because the game cannot send anything. Getting it to the
developer means a person choosing to attach a file to a message.

What the report may never contain is enforced rather than promised.
`s32_engine.playtest.privacy_violations` searches the serialised report for
absolute paths, email addresses, IP addresses, machine-identifier words and
timestamps, and the game **refuses to write the file** if it finds one. No wall
clock of any kind is recorded, so the file cannot say when somebody was awake.
The identifier in it is a session code derived from a random number the
installation generated for itself, which is not derived from the machine and
cannot be walked back to one.

Declining deletes the report rather than pausing it, and the game is otherwise
identical.

`docs/playtest/PLAYTEST_DATA.md` has the full field list and the tests that
hold each of these claims. `FEEDBACK_INSTRUCTIONS.md` is what the tester reads,
and it asks them to open the human-readable copy before sending anything —
being able to read your own report is most of what makes the consent mean
something.

This section applies to private playtest builds. A public release should not
carry the recorder at all, and if it ever does, this document is rewritten
again first.

## If this ever changes

It should not. If a future version wants cloud saves, achievements, or a store
integration:

1. It requires an ADR that supersedes ADR-0004.
2. This document is rewritten first, in specifics, before any code is written.
3. Anything optional is off by default and asked for plainly.

Adding data collection quietly to a game that shipped saying it collects nothing
is a breach of the only promise it made.
