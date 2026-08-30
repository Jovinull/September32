# Canon

## Status markers — read this first

Every claim in these documents carries one of four markers. A claim without a
marker is **not canon**; it is a draft someone forgot to mark, and it should be
marked or removed.

| Marker | Meaning |
| --- | --- |
| `CANON` | Decided. Scenes may rely on it. Changing it is a project-level decision that requires re-checking everything downstream. |
| `PROVISIONAL` | Working assumption. Scenes may use it, but it is expected to be revisited, and anything depending on it should be listed here. |
| `IDEA` | Under consideration. **No scene may rely on it.** |
| `REJECTED` | Considered and ruled out. Kept so the same idea is not re-proposed every six months. |

## The rule that matters

**Nobody — human or AI — may invent canon mid-scene.**

Writing a line that implies September 32 is caused by a machine, a ritual, a
hallucination, or anything else *makes that a fact about the world* the moment a
reader sees it. It does not matter that it was only an implication.

Structural lore changes go through the process in `AGENTS.md` §1.2: propose in
`OPEN_QUESTIONS.md`, record with a marker, update the timeline and phenomenon
rules, re-check existing scenes, run `s32 validate`.

## What is deliberately not decided

Most of it, at this stage. In particular, **the true nature of September 32 is
not decided and does not need to be yet.** Deciding it early would be worse than
useless: the whole first phase of the game is people living ordinary lives, and
that writing does not depend on the answer. What it depends on is the
*constraints* — recorded in `PHENOMENON_RULES.md` — which are what stop the
answer, whenever it arrives, from contradicting what has already shipped.

## Files

| | |
| --- | --- |
| `PREMISE.md` | What the game is, in one page. |
| `WORLD.md` | The school, the town, the archive. |
| `TIMELINE.md` | What happened when, in and out of fiction. |
| `SEPTEMBER_32.md` | The phenomenon: what is observed, what is not decided. |
| `PHENOMENON_RULES.md` | The constraints any explanation must satisfy. |
| `THEMES.md` | What the game is about, as distinct from what happens in it. |
| `OPEN_QUESTIONS.md` | Everything undecided, with the reasoning so far. |
