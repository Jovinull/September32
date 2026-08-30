# Writing style

The register the whole game is written in. The genre-specific guides
(`DIALOGUE`, `ROMANCE`, `HORROR`, `MYSTERY`, `HUMOR`) sit on top of this one.

## The voice

**Report; do not instruct.** The prose says what is there. It does not say how to
feel about it. "The gate is open. Someone has wedged it with a brick, which
suggests it does not stay open on its own." — the reader draws the conclusion,
and the conclusion is theirs.

**Specific over general.** Not "old boxes" but "box seventeen, which has been box
seventeen for three weeks". The specific detail is load-bearing everywhere in
this game; it is the difference between a class photograph and *this* class
photograph, which is what the whole story is about.

**Understate.** The most frightening sentence in the prototype is "You read the
stamp twice, which is once more than a date needs." Nothing is italicised,
nothing is announced.

**Let sentences end.** The default rhythm is medium, medium, short. The short one
is where the meaning lands, and it only works if the two before it were not also
short.

**Dry, not arch.** There is a joke in most paragraphs and it does not announce
itself. The prose is amused by the world, not by itself.

## Things to avoid

**Telling the reader something is wrong.** "Something felt off." "A chill ran
through you." "Little did you know." This is the single most damaging habit
available to this game: it converts a reader who was noticing into a reader who
is being told.

**Adverbs doing the work of verbs.** "She said quietly" versus "She went back to
the scanner, which is her way of finishing a sentence."

**Explaining the joke.** Or the metaphor, or the character's motivation. If it
needs the next sentence to land, rewrite the first one.

**Purple prose in the horror.** The temperature *drops* in the later phases. The
sentences get shorter and plainer, not longer and more ornate.

**Everyone sounding the same.** Cover the names and see if a reader can still
tell who is speaking. If not, the scene is not finished. See `DIALOGUE.md`.

## Mechanics

**Second person, present-ish.** "You put the photograph on the desk, face down,
and then turn it face up again, and then leave it." The protagonist's interiority
is narration, not dialogue.

**British spelling** in prose and documentation. Consistency matters more than
which variety; this is the one that was picked.

**Numbers.** Spelled out below ten in prose, except where the precision is the
point — "ninety-one pages", "fourteen entries", "September 32".

**Ren'Py text tags** sparingly. `{i}` for genuine emphasis, and it should be rare
enough that it means something. Never `{b}` in dialogue. Never a size or colour
change for effect.

## Length

**Dialogue blocks are short.** One to three sentences. A four-line block is a
speech and needs a reason.

**Narration blocks are one paragraph.** If it runs to two, it is two blocks, and
the break is doing work.

**Scenes are 8–25 blocks.** Under eight is usually a fragment; over twenty-five
is usually two scenes. Ambient storylets are the exception and should be three or
four blocks.

## Localisation

The game will be translated (English source, pt-BR planned). That is why:

- **Internal identifiers stay in technical English**, always. A storylet id, a
  knowledge id, a label — these are code, not content.
- **Avoid untranslatable wordplay** in anything load-bearing. A pun in a joke is
  fine and a translator will replace it. A pun that carries a plot point is a
  problem you have handed to somebody else.
- **Avoid concatenating sentence fragments** in Python. Word order differs; give
  the translator whole sentences.
