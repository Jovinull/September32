# Meta and cross-run knowledge

**Status: CANON for the constraints; PROVISIONAL for the budget.**

## The principle

> The protagonist does not remember. The player does.

This is rule R7, and everything else here follows from it.

A new run starts a new life. The protagonist has no memory of a previous
playthrough, gains no unearned knowledge, and never behaves as though they have
seen this before. What crosses between runs is what the *player* now knows — that
box seventeen has a photograph in it, that Theo will ask, that the rooftop door
does not lock.

The occasional payoff for that is a choice the player has earned and the
character has not:

```
[You remember.] Turn the photograph over.
```

Used sparingly. A handful across a whole game, not a mechanic.

## What is explicitly ruled out

`CANON`, all of it:

- Deleting, creating or modifying files outside the game's own save directory.
- Faking a crash, an error dialogue, or a corrupted file.
- Reading the player's filesystem, username, or anything else about their
  machine.
- A character addressing the player as the player, early or as a twist.
- Anything that looks like the game has been tampered with.

These are not off the table because they cannot be done well — one game did them
extremely well. They are off the table because they have become a genre with its
own expectations, and a game that reaches for them is instantly read as being
about that genre rather than about itself.

The unease this game wants comes from a date on a stamp, not from the desktop.

## What `persistent` holds

`s32_engine.meta`, stored in `persistent.s32_meta`, versioned by
`META_SCHEMA_VERSION`:

| Field | Purpose |
| --- | --- |
| `runs_started`, `runs_completed` | Counters. Gate first-run pacing. |
| `endings_seen` | Which endings the player has reached. |
| `discoveries` | Things seen at least once, in any run. |
| `anchors_seen` | Which beats have been witnessed. |
| `gallery_unlocked` | Presentation only. |
| `meta_clues` | The small set that gates `[You remember.]` options. |

**Per-run state never goes here.** That is the classic way to end up with a save
file that contradicts itself, and `docs/decisions/ADR-0007` says why.

The meta migration must never raise: a player whose persistent file came from a
newer build must still be able to launch. A test asserts this.

## The budget

`PROVISIONAL`, and deliberately small:

- At most a handful of `[You remember.]` options in the whole game.
- Each one gated on a specific `meta_clue`, unlocked by a specific earlier
  discovery — never by "has played before".
- None in the first run. `meta.is_first_run()` exists for this.
- None during the `normal` phase, in any run. The first hour is ordinary life,
  and ordinary life does not wink.

## Why so restrained

A meta option is the game acknowledging the player. Done once, at the right
moment, it is extraordinary. Done five times, it is a mechanic, and the player
starts looking for them — which turns the whole game into a hunt for the
brackets.

The scarcity is the effect.
