# Localisation

**Source language: English. Planned: pt-BR.**

The game is not translated yet. What is done is the preparation, which is the
part that is expensive to retrofit.

## What is already right

**Internal identifiers are technical English and never translated.** Storylet
ids, knowledge ids, character ids, labels, flags. These are code. A translated
build and the tooling still agree about what a scene is called.

**User-visible strings are wrapped.** `_("...")` in screens and configuration,
so Ren'Py's extractor finds them.

**`config.language = None`** — the source language. Set it to a translation name
to switch.

**The fonts cover it.** Source Sans 3 and Source Serif 4 have complete Latin
coverage including every diacritic pt-BR needs. That was a selection criterion,
not luck.

## The Ren'Py workflow

Ren'Py's own translation system, which is good and should not be replaced.

### Extract

```
<sdk>/renpy.sh . translate pt_br
```

Generates `game/tl/pt_br/` with a file per source file. Re-running adds only what
is new; existing translations are preserved.

### Translate

```renpy
translate pt_br s32_st_archive_intro_1e4a2c9b:
    # c_iris "Box seventeen. It's been box seventeen for three weeks."
    c_iris ""
```

The commented line is the source. Fill in the empty string.

### Check

```
<sdk>/renpy.sh . lint
```

Reports untranslated strings and mismatched interpolations.

## Rules for writers

**Give the translator whole sentences.** Never build one from fragments in
Python — word order differs, and a fragment cannot be translated in isolation.

```python
# No.
text = "You have " + str(n) + " boxes left"
# Yes.
text = __("You have {n} boxes left").format(n=n)
```

**Avoid load-bearing wordplay.** A pun in a joke is fine; a translator will
replace it. A pun carrying a plot point is a problem handed to somebody else.

**Watch the text length.** Portuguese runs roughly 20–30% longer than English.
The dialogue box has to hold it, and a translation that overflows is the
translator's problem only in the sense that they will be blamed for it.

**Give context.** A short line out of context is often untranslatable. Ren'Py
supports translator comments; use them for anything ambiguous — especially who is
speaking and to whom, since Portuguese marks formality and gender that English
does not.

**Names are not translated.** Character names, place names, September 32 itself.

## The thing that needs deciding

The protagonist has no stated gender, which is comfortable in English and is not
a position Portuguese lets you hold. Adjectives agree.

Options: pick one, offer a choice at the start, or write the Portuguese around it
(harder, and not always possible).

This is not a translation problem to be solved at translation time. It is a
design question, and it is in `docs/canon/OPEN_QUESTIONS.md`.

## Not translated

- `assets/catalog/assets.toml` and the evidence files — legal records, and they
  quote sources verbatim.
- Everything in `docs/` — working documents for the team.
- Anything in `AGENTS.md` or `CLAUDE.md`.
