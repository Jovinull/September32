# Relationship semantics

Eight axes, what each one means, what it does not mean, and how a scene reads it.

Direction is covered separately and is not optional:
[`RELATIONSHIP_DIRECTION.md`](RELATIONSHIP_DIRECTION.md). Everything here
assumes you have already written the arrow.

## Why this file exists

Milestone 4 audited all fifty-one storylets and found that **no line of prose in
the game read a relationship value**. Every scene wrote; nothing read. A player
could take Iris's trust from nought to forty-one across six scenes and not one
sentence anywhere would be different.

Eight axes are only worth having if scenes behave differently because of them.
Otherwise they are a scoring system for a game with no score.

## The axes

### `trust`

**Is.** Whether they believe what you say and would tell you something costly.

**Is not.** Whether they like you. Somebody can enjoy your company enormously
and not trust you with a thing that matters, and June is written to demonstrate
exactly that.

**Moves when** the player is discreet, keeps a promise, or is told something and
does not repeat it. Falls when they are repeated.

```
rel iris->player.trust += 4     you waited while she photographed it
rel june->player.trust -= 3     you said you would come and did not
```

### `attraction`

**Is.** Wanting the other person to be in the room.

**Is not.** Romance, and not consent to a route. There are no routes. High
attraction with low trust is a real and interesting state and the game must be
able to hold it.

**Moves when** somebody is noticed doing something they are good at, or is
gentle when they did not have to be. It should almost never be the only axis a
choice moves.

### `respect`

**Is.** Thinking you are competent, or right, or serious.

**Is not.** Warmth. Theo's respect is easy to earn and tells you nothing about
whether he would sit next to you.

**Moves when** the player is correct, or disagrees well, or does a boring thing
properly.

### `resentment`

**Is.** A specific unforgiven thing. It has an object.

**Is not.** Dislike in general, and not the opposite of trust. Both can be high:
`theo_admits_it` is written for exactly that state — a person confiding in
somebody they have not forgiven.

**Moves when** the player is right in a way that costs the other person
something, or lands on the thing their bible says lands.

### `fear`

**Is.** Expecting to be hurt by this person.

**Is not.** Being intimidated by their competence, which is `respect` plus low
`familiarity`.

**No Act 1 content moves it, and that is deliberate.** It exists for later
phases. `romantic_potential` already subtracts it, so it is wired and unused.

### `dependency`

**Is.** Needing this person for something they cannot easily get elsewhere.

**Is not.** Affection, and not weakness. Noah depends on the player because
nobody else helps with the paper. That is a fact about the paper.

**Moves when** the player repeatedly supplies something. Only Noah and Theo have
it in Act 1.

### `suspicion`

**Is.** An unresolved question about this person's motives.

**Is not.** Dislike, and not the opposite of trust. `trust` high and `suspicion`
high is "I would tell you a secret and I am watching what you do with it", which
is the state `iris_the_second_box` is written around.

**Moves when** somebody is pressed, or caught being interested in the wrong
thing, or times a phone call.

### `familiarity`

**Is.** How much of the ordinary texture of the other person you have.
Knowing how they take their tea.

**Is not.** Closeness, and it does not decay. It is the one axis that only goes
up, because you cannot un-know how somebody takes their tea.

**Moves when** time is spent. It is the cheapest axis and should be: everything
else needs it as a floor.

**Still directed.** "How well she knows you" and "how well you know her" go out
of step precisely when a story becomes interesting.

## Reading state in a scene

The bridge exposes three readings. Use the coarsest one that works.

### `stance(who)` — the usual one

Returns `distant`, `wary`, `comfortable` or `close`: how `who` currently reads
the player, from trust, familiarity, and whichever of suspicion or resentment is
higher.

```renpy
$ _iris = stance("iris")

if _iris == "wary":
    narrator "She does not move the box toward you, and she does not move it away."
```

**`wary` is the interesting one and is not a milder `distant`.** Somebody who
knows you well and is holding something back reads completely differently from
somebody who has not decided about you yet. It is the state the eight axes exist
to make possible, and a scene that treats it as "slightly cold" has wasted them.

Three or four versions of a scene is as many as anyone can write well. If a
scene wants five, it wants to be two scenes.

### `regards(who, axis, at_least)` — one axis, explicitly

For when the summary is the wrong question.

```renpy
if regards("theo", "resentment", 4):
    c_theo "I'm telling you this because you'll be unbearable about it otherwise."
```

### `player_regards(who, axis, at_least)` — the other direction

Rare, and deliberate. The player's own view of somebody changes in only a
handful of Act 1 scenes, and this is how a later scene notices.

```renpy
if player_regards("june", "respect", 5):
    narrator "You have watched her do this before, with a rota and four minutes."
```

### `rel_get(pair, axis)` — the raw number

For NPC-to-NPC edges, mostly.

```renpy
if rel_get("iris->theo", "suspicion") >= 3:
    narrator "They have the efficiency of two people who have had the general version already."
```

## Combinations, which is the whole point

A threshold on one axis is a difficulty setting. The combinations are the
characterisation.

| State | Reads as | Where |
| --- | --- | --- |
| `trust` high, `suspicion` high | She will tell you, and she is watching what you do with it | `iris_the_second_box` |
| `trust` high, `resentment` high | He is confiding in somebody he has not forgiven | `theo_admits_it` |
| `familiarity` high, `trust` low | Perfectly warm, and a tour of things rather than a conversation | `mara_the_long_way` |
| `respect` high, `familiarity` low | Listens to your opinion, would not tell you anything | Theo, most of week one |
| `attraction` high, `familiarity` moderate | A second chair that was not there on Tuesday | `iris_the_second_box` |
| `familiarity` high, recently let down | "You came." Warm, and a receipt. | `the_saturday` |

## Rules

**Never show a number.** Not in the journal, not in a screen, not in narration.
The player should be able to feel a relationship change and not be able to
quote it.

**Never move an axis without an event.** A number that moved because time passed
is a number the player cannot account for.

**Do not farm one axis.** A scene whose three branches are `trust +3`,
`trust +4`, `trust +5` has three difficulty settings, not three choices. At
least one branch should move a different axis, and at least one should cost
something.

**Falling is allowed and is rare on purpose.** Exactly two Act 1 branches lower
a trust axis (`theo_admits_it`, `the_saturday`). If a scene has no branch that
costs anything, check whether it has a choice in it.

## Checking it

- `tests/test_relationship_direction.py` holds the grammar and the migration.
- `tests/test_act1_depth.py` holds that scenes actually read state, and that the
  readings are reachable.
- `Shift+C` in a development build shows both edges of every pair, including the
  empty one.
