# Mystery

The player is not solving a puzzle. They are assembling an account of something
that does not admit of a clean account, and the game must be honest about the
difference.

## Fair play, and what it means here

The player must always be able to reach a conclusion from what they have seen.
That does not mean every conclusion is available — it means no conclusion depends
on information the game withheld arbitrarily.

Concretely:

- Every fact the player can hold is a `knowledge` id, granted by a scene they
  played. There is no off-screen learning.
- Every requirement gating a scene is checkable, and `s32 explain <id>` prints
  exactly why a scene did not fire.
- The static analyser refuses to ship a requirement nothing can satisfy. A locked
  door with no key is a bug, and CI treats it as one.

## Information as a mechanic

The five stances — `unknown`, `suspected`, `known`, `false_belief`, `disproven` —
are the mystery's actual vocabulary.

**`suspected` is where the game lives.** A hunch does not unlock what knowledge
unlocks, and the gap between the two is most of the tension. `knows()` in a
requirement deliberately excludes `suspected`: "I have a hunch" and "I have seen
the file" should not open the same door.

**`false_belief` is the best tool in the set.** A character who is confidently
wrong is more interesting than one who is ignorant, and a *player* who is
confidently wrong is the whole point of an unreliable archive.

**`disproven` is terminal.** A fact the story took the trouble to disprove does
not quietly become true again. Re-establishing one requires `force=True`, which
is greppable, and should be a dramatic event.

## Contradictions

`s32_engine.knowledge.contradictions` finds pairs of facts an agent holds that
cannot both be true. Rule R8: contradictions are tracked, not hand-waved.

A contradiction the player has *noticed* is a scene. A contradiction they hold
without noticing is a scene waiting to happen — and the engine knows which is
which, which is what makes the mechanic worth having.

## Per-character knowledge

Each character has their own stance on every fact. This is not bookkeeping; it is
where the mystery meets the relationships:

- Telling somebody something changes their stance, and what they do with it.
- A character who suspects will say different things to a player who knows.
- Two characters with incompatible beliefs about the same document is a scene
  that writes itself.

## Pacing the reveals

**Never reveal by exposition.** The player should learn things by finding them,
or by someone choosing to say them, and the choosing is where the drama is.

**One thing at a time.** The `odd` phase has exactly one anomaly. A second one
arriving too soon converts unease into a list.

**Withhold the specific, not the general.** The player can know a stamp exists,
that it is a date, that the date is in September — and not what the number is.
That is fair, and it is unbearable. What is not fair is withholding that a stamp
exists at all when the protagonist is holding the photograph.

## What must not happen

**A twist that invalidates the evidence.** "None of it was real" is not a
resolution; it is a refusal.

**A character who knew all along and did not say.** R3: nobody has the full
picture. If somebody appears to, the game must show whether they were mistaken or
lying.

**A solution the player could not have reached.** Test: could an attentive player
with this playthrough's knowledge have arrived here? If not, something is
missing, not clever.
