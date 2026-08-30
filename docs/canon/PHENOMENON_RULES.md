# Phenomenon rules

**Status: PROVISIONAL** — these constraints are the working contract. They exist
so that scenes can be written *before* the explanation is chosen, without any of
them having to be retracted later.

A rule here is a promise about what the finished game will not contradict.

## Rules

**R1. The archive is more reliable than the people.** `PROVISIONAL`
Documents are consistent with each other more often than memories are. This is
the inversion the whole story turns on, and it is the source of the unease: the
player learns to trust paper over the person in front of them, and that is a
loss.

**R2. Nothing is ever proven by a single document.** `PROVISIONAL`
Any single item admits an ordinary explanation. Only accumulation is
persuasive, which means the player's confidence is built by *volume* — and
volume can be wrong.

**R3. No character has the full picture.** `PROVISIONAL`
Not Iris, not Ms. Ellery, not the town. Anyone who appears to have it is either
mistaken or lying, and the game must eventually show which.

**R4. The phenomenon never performs.** `PROVISIONAL`
It does not manifest, appear, chase, or address anyone. It is a discrepancy in a
record. Everything frightening about it is inferential. A scene where it *does*
something has broken this rule and should be rewritten.

**R5. Ordinary explanations stay available.** `PROVISIONAL`
Until an anchor forecloses it, a sceptical player must be able to maintain a
mundane reading and not feel stupid. June is that reading's advocate and she must
never be written as a fool.

**R6. Escalation is one-way.** `CANON`
The phase advances `normal → odd → unsettling → impossible → consequences` and
never goes back. Enforced in code: `s32_engine.effects` raises on a backwards
phase change.

**R7. The protagonist does not remember previous runs.** `CANON`
The *player* does. Nothing in a new run gives the protagonist knowledge they did
not earn in that run. See `docs/narrative-design/META.md`.

**R8. Contradictions are tracked, not hand-waved.** `CANON`
When two facts cannot both be true, the engine knows
(`s32_engine.knowledge.contradictions`). A contradiction the player has actually
noticed is a dramatic event and gets a scene; one they have not noticed is a
scene waiting to happen.

## Under consideration

**The date is not the point.** `IDEA`
September 32 might be a symptom rather than a cause — the visible edge of
something about how this institution keeps records. Recorded because it changes
what the ending needs to resolve.

## Rejected

**The phenomenon is dangerous to look at.** `REJECTED`
Makes the archive into a monster and the investigation into a survival mechanic.
The story is about people and records; a hazard would flatten it.

**A character is secretly from September 32.** `REJECTED` for now.
It is the first idea everyone has, it resolves the mystery into a person, and it
would make the archive scenery. If it returns, it needs an argument that does not
reduce the story to a reveal.
