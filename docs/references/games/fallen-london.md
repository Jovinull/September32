# Fallen London / Failbetter Games

Original analysis. The design vocabulary discussed here (quality-based narrative,
storylets) was published by Failbetter and has been widely written about since;
this dossier summarises the ideas and cites their origin rather than reproducing
any text.

## USE FOR

**Quality-based narrative.** Content is gated on *qualities* — numbers and states
describing the player and the world — rather than on position in a tree. The
question stops being "which branch am I on" and becomes "what is true of me now".

**Storylets.** A unit of pre-written content plus the conditions under which it
is available. The system asks what fits; the author never draws the graph.

**Additive content.** A new storylet is a new file. It does not require editing
anything that already exists, which means the hundredth scene costs the same as
the tenth — the exact opposite of a branching tree, where late content is the
most expensive.

**Qualities as characterisation.** A number the player has accumulated says
something about who they have been. It is not a stat; it is a summary of
behaviour.

## DO NOT COPY

The setting, the tone, the terminology specific to it, the economy, any content.
The free-to-play action-economy structure in particular: it shapes their content
in ways that would be actively harmful here.

## PRINCIPLE

> Describe the situation a scene belongs in, and let the system find it. Content
> becomes additive, and the player's state becomes the story.

## RELEVANCE TO SEPTEMBER 32

This is the architecture. `docs/decisions/ADR-0002-storylet-architecture.md`
adopts it wholesale, with one significant addition: **anchor scenes**.

Pure QBN drifts. It produces situations rather than a story, and a player can
feel things happening without feeling that anything is *going* anywhere. Anchors
are ordered, gated beats that carry the shape, with storylets filling the space
between them. That combination is this project's actual bet.

The second addition is analysis. Because requirements are declarative, tooling
can ask questions the author cannot: which storylets are unreachable, which facts
nothing grants, which threshold no run can meet. That found three real bugs
during the bootstrap, including a scene gated on `iris.trust >= 12` when nothing
in the content could raise trust past 10.

## RISKS

**Drift.** Guarded by anchors and by the pacing budget.

**Content starvation.** QBN needs volume. Below a threshold, the same handful of
scenes recur and the system looks broken rather than sparse. The repeat damping
(halve weight per play) helps; the real answer is writing more.

**Grind.** Their economy rewards repetition. This game has no economy and must
not acquire one: `docs/style/ROMANCE.md` forbids affection farming for exactly
this reason.

**Illegibility.** A player who cannot tell what changed, or where anything is
happening, experiences combinatorial richness as an empty corridor. This is why
`s32_engine.world.locations_with_content` exists — the simulator's dead-end rate
fell from 81% to zero once the model stopped wandering at random, which is a
measurement of a real design problem, not a tooling artefact.

## Sources

Failbetter Games' published design writing on storylets and quality-based
narrative, and Emily Short's essays on storylet architecture. Consulted, not
reproduced.
