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
`smtplib`, `asyncio` or `ssl`. `AGENTS.md` forbids adding a network call. A pull
request that added one would be rejected on sight.

This is not primarily a privacy stance. It falls out of
`docs/decisions/ADR-0004-no-runtime-ai.md`: a single-player game should not need
a connection to tell its story, and a player should not have to wonder what is
being sent anywhere. Privacy is what you get for free when there is nothing to
send.

## Development analytics

The simulator and coverage tools produce statistics — scenes reached,
relationship distributions, dead ends. These are generated from *simulated*
playthroughs on a developer's machine, written to `tools/reports/`, and have no
connection to any player. Nothing observes a real session.

## If this ever changes

It should not. If a future version wants cloud saves, achievements, or a store
integration:

1. It requires an ADR that supersedes ADR-0004.
2. This document is rewritten first, in specifics, before any code is written.
3. Anything optional is off by default and asked for plainly.

Adding data collection quietly to a game that shipped saying it collects nothing
is a breach of the only promise it made.
