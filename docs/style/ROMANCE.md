# Romance

Romance is optional, gradual, and never the reward for a resource-management
exercise. A player who never pursues it should have a complete game; a player who
does should feel it was earned by attention rather than by spending.

## What this game's romance is made of

**Shared attention.** These characters fall for people who look at the same
things they do, properly. The most romantic scene in the prototype is somebody
admitting they photograph objects before cataloguing them.

**Vulnerability, unasked for.** Not a confession — an admission. The difference
is that a confession is about the speaker's feelings and an admission is about
something true that they had not said.

**Routine.** Being reliably in the same room. Most of a relationship here is
accumulated `familiarity`, and the game should show the accumulating.

**Small gestures with a cost.** Taking something out of someone's hands gently,
and apologising for the taking rather than the gentleness.

**Conflict.** People who never disagree are not close, they are polite. A
relationship that has survived a disagreement is legible as a relationship.

**Boundaries.** A character saying no, and the game respecting it, is more
romantic than a character saying yes to everything.

**Chemistry over compatibility.** Two people who agree about everything have
nothing to talk about.

## What it is not

**Affection farming.** No repeatable action that reliably increases a number.
The `attraction` axis is not a resource; it is a description.

**Gifts.** Giving somebody an object should never move a relationship on its own.

**Characters who exist for the protagonist.** Every romanceable character has a
life, an argument with somebody else, and a reason to be busy. If a character is
always available, they are furniture.

**A route.** There is no "Iris route". There is Iris, and the accumulated state
of a specific playthrough.

## The axes

`attraction` alone is not romance. `s32_engine.relationships.romantic_potential`
weights attraction by the trust and familiarity that make it mean anything, and
subtracts fear — because a relationship built on fear is a different story and
must not score as if it were this one.

Situations the model must represent, and which the writing should actually use:

- Attraction with low trust. Someone the player is drawn to and should not tell
  things.
- Trust with no attraction. The best friendship in the game.
- Respect with resentment. Theo, if the player keeps breaking promises.
- Dependency without romance. The one to handle most carefully.

## Pacing

Romance follows the same phase escalation as everything else. In `normal` it is
barely present — proximity, a joke landing, being in the same room. It should not
be possible to reach a significant romantic state before the phase advances,
because the game has not yet earned it.

Later, romance and the mystery interfere. Who trusts the player determines what
they are shown; what the player knows determines what they can ask. That
interference is the point (`docs/canon/PREMISE.md`), and a romance scene that
could have been written before the archive existed is a scene that is not doing
its job.

## Content

Fade to black. This is not a prudish decision; it is a register decision — the
game's whole manner is understatement, and an explicit scene would be the loudest
thing in it.
