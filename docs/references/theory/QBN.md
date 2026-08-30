# Quality-based narrative and storylets

The design theory this project is built on, and where it departs.

## The problem it solves

A branching narrative multiplies. Three binary choices give eight paths; ten give
a thousand. Every new choice doubles the content that must exist, so in practice
branches are written to converge fast — and the player correctly perceives that
their choices did not matter.

The costs land in the worst place: **late content is the most expensive**, because
it must exist in every combination of everything before it. That is exactly
backwards, since late content is where the payoffs are.

## The alternative

**Qualities.** Numbers and states describing the player and the world.
Relationship axes, knowledge stances, traits, world flags, phase, location, time.

**Storylets.** A pre-written scene plus a declaration of the situation it belongs
in. Not a node in a graph — a description of a fit.

**A director.** At defined moments, it asks which storylets fit the current
qualities and picks one.

The author never draws the graph. They write scenes and say when each belongs.
Content becomes **additive**: the hundredth scene costs the same as the tenth.

## What that buys

**Delayed consequence for free.** A storylet can require a state set days ago. No
branch had to be maintained in between.

**Recombination.** Two scenes written independently can occur in either order if
neither requires the other, and the player experiences a sequence nobody
authored.

**Analysability.** Because requirements are declarative, tooling can reason about
them. This is not a side benefit — it is what makes the approach viable at scale.

## What it costs, and what this project does about it

### Drift

QBN produces *situations*, not a story. A player can feel things happening
without feeling that anything is going anywhere.

**Answer: anchor scenes.** Ordered, gated beats that carry the dramatic shape,
with storylets filling the space between them. ADR-0002.

### Illegibility

If the player cannot tell what changed or where anything is happening, systemic
richness is experienced as an empty corridor.

**Answer: model finding things as part of the design.**
`s32_engine.world.locations_with_content` answers "is anyone in the club room
right now", which is a question a student in a small school can answer by
looking. When the simulator's model of a player stopped wandering at random, the
dead-end rate went from **81% to zero** — a measurement of a real design problem,
not a tooling artefact.

### Content starvation

Below a threshold, the same handful of scenes recur and the system looks broken
rather than sparse.

**Answer:** repeat damping (weight halves per play), plus honest measurement.
`s32 coverage` reports how much content exists and in what state.

### Invisible authoring errors

A requirement nobody can satisfy is a locked door with no key, and it is
invisible by inspection.

**Answer: three layers of checking**, and all three found real bugs here.

1. **Cross-reference validation** — every id named by a condition exists.
2. **Static reachability** — a monotone fixed point over what content can grant.
   Sound in the direction that matters: if it says unreachable, it is. It caught
   `iris.trust >= 12` when nothing could exceed 10.
3. **Simulation** — a thousand headless playthroughs across nine player profiles.
   It caught a scene gated on `weather == rain` when nothing made it rain, and a
   run-completion rule that ended runs on day two and made three storylets look
   unreachable.

### Prose that the tools cannot see

A choice inside a scene changes state, and that state lives in prose no analyser
reads. Content depending on it then looks dead.

**Answer:** storylets declare `outcomes` — the effect sets their choices produce.
The prose stays in the `.rpy`; the consequences are declared where the tools can
read them. ADR-0006.

## What this project does not take

**The action economy.** Fallen London gates content on a regenerating resource
because of its business model. This game has no economy and must not acquire one.

**Grind.** `docs/style/ROMANCE.md` forbids affection farming explicitly.

**Infinite claims.** The honest description is: hundreds of hand-written scenes,
recombined by state. Combinatorially large, not infinite, and marketing it as
infinite would be a lie about a system that does something better than that.

## Sources

Failbetter Games' published design writing on storylets and quality-based
narrative; Emily Short's essays on storylet architecture; the design of Fallen
London, Sunless Sea and Sunless Skies as played. Consulted and summarised, not
reproduced. See `docs/references/games/fallen-london.md`.
