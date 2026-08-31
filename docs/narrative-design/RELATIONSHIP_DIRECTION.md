# Relationship direction

Every relationship edge is directed and the direction must be written. There is
no default and there is no shorthand.

```json
"rel iris->player.trust += 3"      Iris warms to you
"rel player->iris.suspicion += 2"  you start doubting her
"rel mara->june.resentment += 2"   nothing to do with you
```

```renpy
$ rel("iris->player", "trust", 3)
$ rel_get("player->iris", "suspicion")
```

## Why there is no default

There used to be one. `rel iris.trust += 3` meant the **player's** trust toward
Iris, because `source` defaulted to `player`.

An audit of every relationship expression in the game found **114 of them, and
all 114 meant the other direction.** They are almost all the same shape: the
player does something, and a character responds to it.

```json
"rel iris.trust += 4"        after the player answers Iris kindly
"rel mara.suspicion += 3"    after the player presses Mara for an answer
"rel noah.dependency += 2"   after the player helps Noah with the layout
"rel theo.respect -= 1"      after the player takes Iris's side against Theo
```

Not one of them was the player's own stance. The default was not merely
ambiguous; it was wrong in one hundred per cent of its uses.

## Why nothing caught it

Only two conditions in the whole game read a relationship, and both read the
same wrong edge:

| Where | Was | Means | Should have meant |
| --- | --- | --- | --- |
| `rain_after_school` requirement | `rel iris.trust >= 7` | the player trusts Iris | Iris trusts the player enough to confide — the scene is her asking *"Can I tell you something that makes me sound strange?"* |
| `hallway_encounter` blocker | `rel theo.resentment >= 40` | the player resents Theo | Theo resents the player enough not to stop and talk — the whole scene is Theo choosing to speak |

Because the writes and the reads were consistently wrong together, the game
behaved exactly as intended. Every test passed. The simulator reported healthy
relationship ranges. The debug screen showed a number going up next to the right
character's name. The data was on the wrong arrow the entire time and there was
no observation that could distinguish it.

`hallway_encounter`'s blocker is the sharper case: nothing in the game ever
raised `player->theo.resentment`, so it could never fire. Under the direction it
means, it is a legitimate hook waiting for content. Under the direction it had,
it was a dead clause pointing the wrong way.

## What changed

| Layer | Before | After |
| --- | --- | --- |
| Condition grammar | `rel iris.trust >= 5` | `rel iris->player.trust >= 5` |
| Effect grammar | `rel iris.trust += 3` | `rel iris->player.trust += 3` |
| Ren'Py helper | `rel("iris", "trust", 3)` | `rel("iris->player", "trust", 3)` |
| Ren'Py helper, NPC pair | `rel("june", "suspicion", 2, source="mara")` | `rel("mara->june", "suspicion", 2)` |
| Python API | `get(state, "iris", "trust")` | `get(state, "iris", "player", "trust")` |
| Debug screen | `player -> them` | both edges, always |

The grammars **refuse** the old form rather than accepting it quietly, and the
refusal names both replacements:

```
ambiguous relationship direction in 'rel iris.trust':
write 'rel player->iris.trust' for the player's stance toward iris,
or 'rel iris->player.trust' for theirs toward the player
```

The Python API takes `source` before `target` and neither has a default, so
`get(state, "iris", "player", "trust")` reads in the direction it means.

The internal representation did not change. `state["relationships"]` is still
keyed `"source->target"` and the graph is still directed, which is why this was
an authoring fix rather than an engine one.

## Saves

Save schema **v3**. A v2 save has the entire cast's feelings about the player
filed under `player->them`, so `migrate_state` flips those edges.

Flipping is a repair rather than a guess: the v2 grammar had no way to express
the player's own stance, so no `player->x` edge in a v2 save was deliberate. An
edge that already exists in the correct direction wins, since only content
written after the fix could have produced it.

NPC-to-NPC edges were never affected — they always required the arrow — and are
left untouched.

## Choosing a direction when writing

Ask what the scene is about.

- **The character reacts to the player.** `x->player`. This is most scenes.
  Trust, respect, resentment, suspicion, attraction, fear and dependency are all
  about how *they* have come to see *you*.
- **The player forms a view.** `player->x`. Rarer than it sounds, and worth
  being sure about: a scene where the player privately decides they do not
  believe someone. If the scene has no moment where the player's own opinion
  changes, this is not it.
- **Two characters, and the player is a witness.** `a->b`. The best of these
  cost the player something — `courtyard_lunch_table` moves `june->noah` and
  `noah->june` in opposite directions depending on whose side the player takes.

`familiarity` is the one axis that is genuinely close to symmetric, and it is
still directed, because "how well she knows you" and "how well you know her" go
out of step exactly when a story gets interesting.

## Checking it

- `s32 validate` fails on a relationship expression with no direction.
- `tests/test_relationship_direction.py` holds the grammars, the content, the
  Ren'Py notation, and the save migration.
- `Shift+C` in a development build shows both edges for every character. It
  shows the empty one too, on purpose: a screen that displays only the edge you
  wrote is a screen that agrees with you.
