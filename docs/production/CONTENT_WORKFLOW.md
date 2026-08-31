# Adding content

Three companions to this file, and a scene that ignores them will pass every
gate and still be wrong:

- [`CELL_MAP.md`](../narrative-design/CELL_MAP.md) — which (location, hour)
  cells want content, which are empty on purpose, and which the player should
  not be standing in at all. **Read before choosing a location and a time slot.**
- [`PRIORITY_AUTHORING.md`](../narrative-design/PRIORITY_AUTHORING.md) — the
  five priority bands. `priority` is a hard tier, so a value nothing else shares
  removes the scene from the weighted draw entirely.
- [`CONTINUITY_REVIEW.md`](../narrative-design/CONTINUITY_REVIEW.md) — the words
  that make a claim about the player's past, and what has to be true before you
  use one. Also the policy for repeatable scenes.

## A storylet

**1. The scene card.** `docs/narrative-design/SCENE_CARD_TEMPLATE.md`. Before the
prose, not after.

**2. The metadata.** `data/storylets/<id>.json`:

```json
{
  "id": "iris_rooftop_rain",
  "label": "s32_st_iris_rooftop_rain",
  "title": "Rain, After School",
  "category": "conversation",
  "status": "prototype",
  "characters": ["iris"],
  "location": "rooftop",
  "time_slots": ["evening"],
  "tags": ["slice_of_life", "romance", "character"],
  "priority": 60,
  "requirements": ["weather == rain", "rel iris.trust >= 10"],
  "effects": ["rel iris.trust += 5"],
  "outcomes": [
    ["trait empathetic += 1", "rel iris.trust += 4"],
    ["trait sarcastic += 1", "rel iris.familiarity += 4"]
  ],
  "summary": "What this scene is for. Write it."
}
```

**3. The prose.** `game/story/storylets/*.rpy`:

```renpy
label s32_st_iris_rooftop_rain:
    scene bg rooftop evening with fade
    show iris school_summer neutral at s32_centre with dissolve
    c_iris "You're not supposed to be up here."
    ...
    return
```

**4. Validate.**

```bash
uv run s32 validate
uv run s32 simulate --runs 500
```

The first checks references and reachability. The second checks that a player can
actually get there.

## The fields that matter

**`priority`** is a **hard tier**, not a weight. Only the highest-priority
eligible storylets compete. Use it for "this must happen now"; use `weight` for
"this is more likely than that".

Five values, and nothing in between them. A scene that seems to want 45 wants a
different requirement, not a different priority.

| Value | Band | For |
| ---: | --- | --- |
| 100 | `REQUIRED` | The run is incoherent without it. Reserved; anchors cover most of this. |
| 80 | `URGENT` | A commitment falling due, or a consequence that stops making sense if deferred. |
| 60 | `CALLBACK` | Reacts to a specific earlier decision, or to a window that will close. |
| 40 | `EVENT` | The ordinary body of the game. **Most content lives here.** |
| 20 | `AMBIENT` | Texture. Must never outrank anything with something to say. |

Ranges were the old convention and they produced fifteen storylets on fifteen
distinct values, which made the top tier a singleton in 100% of selections and
`weight` a decoration. `s32 validate` reports an `off-band-priority` info
finding for anything else.

**`weight`** competes within a tier. Halves with each play, so a repeatable scene
is available rather than insistent.

**`repeat_policy`** — `once` (most content), `cooldown` (needs `cooldown` in
days), `repeatable`.

**`outcomes`** — the effect sets the scene's own choices produce, in order. **Not
optional if the scene has a menu that changes state.** See ADR-0006.

## Conditions, briefly

```
day >= 3                         weather == rain
location == rooftop              time_slot in morning, evening
phase >= unsettling              rel iris.trust >= 30
rel iris->theo.respect < 20      trait curious >= 3
flag archive_visits >= 2         knows(old_photo)
suspects(old_photo)              stance(iris, old_photo) == suspected
seen(archive_intro)              not_seen(rain_after_school)
seen_count(x) >= 2               days_since(x) >= 3
has_item(old_camera)             anchor_done(arrival)
commitment(meet_theo) == active  char iris.present == true
chance(0.25)
```

Any of them takes a leading `not `. Full grammar in
`s32_engine/conditions.py`; effects in `s32_engine/effects.py`.

## When it will not fire

```bash
uv run s32 explain iris_rooftop_rain
```

In-game, `Shift+S`. It shows every storylet, whether it is eligible, and which
clause failed **with the actual value** — "needs 30" is useless without
"currently 22".

## A character

1. `data/characters/<id>.json`
2. A bible from `docs/characters/_TEMPLATE.md`
3. `uv run s32 assets images` — regenerates the Ren'Py image definitions
4. A `Character()` in `game/characters/characters.rpy`

## An anchor

Same as a storylet, in `data/anchors/`, plus `order` and `phase`. Anchors are
ordered, are `call`ed directly rather than selected, and are the **only** content
permitted to advance the phase. See `docs/narrative-design/PACING.md`.
