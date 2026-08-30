# Open questions

Everything the project has deliberately not decided, with the reasoning so far.
This is the input to a design conversation, not a to-do list — several of these
are better left open for a long time.

Each entry records what is at stake, so that whoever answers it knows what the
answer costs.

---

## Narrative

### What September 32 actually is
**Status: open. Deliberately.**
Hypotheses are in `SEPTEMBER_32.md`; constraints in `PHENOMENON_RULES.md`.
*At stake:* the ending, and the meaning of every archive scene in retrospect.
*Why wait:* the first phase does not depend on it, and an early answer leaks into
scenes written now in ways that are invisible until they are expensive.

### Is there a true ending?
**Status: open.**
*At stake:* whether replaying is completion or perspective. A single true ending
makes other endings failures; no true ending risks the whole thing feeling like
it declined to conclude.
*Leaning:* several endings that are all true, differing in what the protagonist
does with what they know. Unconfirmed.

### How many runs is the game designed around?
**Status: open.**
*At stake:* pacing, meta-clue budget, and how much content must exist.
*Note:* the meta system (`docs/narrative-design/META.md`) works at any number,
but "designed for two" and "designed for six" are different games.

### Supernatural, psychological, or undetermined?
**Status: open.**
*At stake:* genre expectations, and whether June's sceptical reading is
ultimately vindicated. R5 keeps it available for now.

### Is the protagonist a defined character or a blank?
**Status: open.**
Currently written as barely-defined: they speak, they have a wry register, they
are not named.
*At stake:* whether the traits system is characterisation or self-expression.
*Leaning:* lightly defined — someone specific enough to be surprised by.

### Point of view
**Status: open.** Currently a single close third/second hybrid.
*At stake:* whether the game can ever show a scene the protagonist is not in.
*Note:* `428: Shibuya Scramble`-style cross-cutting is attractive and would
change the engine's assumptions considerably. Not free.

---

## Setting

### Country, region, era
**Status: open.** The writing is deliberately non-specific and this has cost
nothing so far.
*At stake:* names, institutions, what a school does, what a town remembers.
*Note:* it cannot stay open forever — an archive spanning decades eventually
needs a history.

### The school's name
**Status: PROVISIONAL — "Northfield".**
Chosen for the missing F on the gate, which is a better joke than the name.

### Character ages, and how long the calendar runs
**Status: open.** Affects tone, what romance means, and the pacing budget.

---

## Characters

### Casting: which sprite plays whom
**Status: open, and the current answer is mechanical.**
Casting was decided on *outfit availability* — `kohaku` and `tomomi` are the only
free characters with both uniforms and casual clothes, so they went to the two
most-featured roles. Nobody has looked at the sprites and asked whether they
suit the characters, because this toolchain deliberately cannot: no third-party
artwork is sent to any vision service (`docs/legal/AI_AND_ASSETS_POLICY.md`).
*Action:* a human should review the contact sheets in
`tools/reports/contact-sheets/` and recast if the fit is wrong. It is a one-line
edit per character in `data/characters/`.

### Which characters are romanceable
**Status: PROVISIONAL.** Currently Iris, Theo, Mara and June are flagged; Noah
and Ms. Ellery are not.
*At stake:* content budget, and whether "romanceable" is even the right frame for
a game that rejects routes.

### Does the cast need a sixth?
**Status: open.** Ms. Ellery exists and has no sprite. Whether she needs one, or
whether a faculty character is better kept at a distance, is undecided.

---

## Production

### Voice acting
**Status: open.** Leaning no. Cost is large; the register is understated and
voice would fight it.

### CG budget
**Status: open.** See `docs/production/ART_GAP_ANALYSIS.md`. The archive
documents matter more than event CGs, which is unusual and worth deciding
deliberately.

### The project's licence
**Status: open, and blocking nothing.** `/LICENSE` is conservative on purpose.
The intent is to relicense the *engine and tooling* permissively once the
boundary with the narrative content is stable. Needs an ADR.

### Platforms beyond desktop
**Status: open.** Nothing in the architecture blocks a port. Web is explicitly
not a production target.
