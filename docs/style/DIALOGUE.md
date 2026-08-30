# Dialogue

## The test

Cover the character names and read the scene. If a reader cannot tell who is
speaking, the dialogue is not finished.

This is not a stylistic aspiration. It is achievable with four or five concrete
habits per character, recorded in the character bibles: sentence length, whether
they finish thoughts, what they say instead of answering, what they will not
discuss.

```
Theo:  "Archive."
Iris:  "You're late, which is fine, because I'm early, which is not a virtue."
Mara:  "No."
June:  "Okay but hear me out —"
```

## People do not talk in paragraphs

Real speech is short, interrupted, and frequently does not answer the question
asked. A character who delivers three grammatical sentences on their first turn
is delivering exposition wearing a hat.

## The main failure: exposition

Two characters explaining to each other something they both already know is the
most common bad scene in this genre, and this game is unusually exposed to it —
it is *about* an archive, and archives generate facts.

What to do instead:

**Let one of them be wrong.** Correction is dramatic; recitation is not.

**Let them disagree about what it means.** Theo and Iris both know the ledger has
a column with no header. They disagree completely about what follows, and that
disagreement conveys the fact better than either explaining it.

**Give the information a cost.** If saying it out loud is difficult, saying it is
a scene.

**Cut to after.** Sometimes the player does not need to hear the explanation; they
need to see the person who has just heard it.

## Silence and refusal

The most useful thing a character can do is not answer.

```
c_theo "Does Iris know?"
c_theo "..."
c_theo "Iris photographs things before she catalogues them."
```

The ellipsis block is a beat. Used once in a scene it is heavy with meaning; used
four times it is a tic.

Ways of not answering, and what each means: changing the subject (deflection),
answering a smaller question (management), stating a fact instead of an opinion
(Mara), making a joke (June), going back to work (Iris), producing a document
(Theo).

## Naming

Characters rarely use each other's names in conversation. Real people almost
never do. A name in dialogue is emphasis — use it when someone is being serious,
or angry, or is about to say something difficult.

## Ren'Py specifics

**One idea per block.** The player advances with a click; each click should
deliver something.

**Do not chain three blocks from the same speaker** unless the pauses are the
point.

**Use expressions deliberately.** `show iris school_summer concerned` is a beat.
Changing expression on every line makes the sprite twitch.

**Reactions are blocks too.** Sometimes the most important line in an exchange is
a narration block describing what the other person did with their face.

## A worked example

Wrong — both characters know this, and are saying it for the reader:

```
c_theo "As you know, every item in the archive gets an accession number and
        every accession number gets a date, and this has been the system since
        the school was founded."
```

Right — the same information, arriving as a person:

```
c_theo "Every item gets a number. Every number gets a date."
c_theo "That's the whole system. It's not sophisticated, it just has to be
        complete."
show theo school_summer concerned
c_theo "Look at this column."
```
