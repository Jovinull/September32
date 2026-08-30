# Scene card template

Every non-trivial scene gets one of these **before** the prose. It takes ten
minutes and it is the difference between a scene that does something and a scene
that happens.

The two fields nobody wants to fill in — **PLAYER MUST NOT LEARN YET** and
**CONTINUITY RISKS** — are the two that catch the expensive mistakes.

---

```
SCENE ID           <storylet or anchor id — must match data/>
STATUS             prototype | draft | active | retired
CHARACTERS         <who is present, and who is mentioned but absent>
LOCATION
TIME               <slot, and phase if it matters>

PURPOSE
    One sentence. What this scene is FOR. If it takes two sentences, it is
    probably two scenes.

NARRATIVE FUNCTION
    What it does structurally: introduces, escalates, complicates, pays off,
    rests. "Rests" is a real function and the pacing budget needs it.

EMOTIONAL START    Where the player is when it begins.
EMOTIONAL END      Where they are when it ends. If these are the same, say why.

CHARACTERS KNOW
    Per character. What each one knows walking in — including the things they
    are wrong about.

CHARACTERS DON'T KNOW
    The gaps that make the scene work.

PLAYER MAY LEARN
    Facts the player can come away with. Every one must appear in the
    storylet's `effects` or `outcomes`, or the tooling cannot see it.

PLAYER MUST NOT LEARN YET
    The important half. Name what this scene must not give away, and the ending
    stays intact.

SETUPS             What is planted here for later.
PAYOFFS            What earlier setups land here.

CHOICES
    Per choice: what it reveals about the player, what it changes, what it
    costs. A choice that costs nothing is flavour — fine, but label it.

STATE EFFECTS
    The concrete changes. Must match the storylet's `effects` and `outcomes`
    exactly. If they disagree, the metadata is what the tools believe, and
    the tools are what report unreachable content.

CONTINUITY RISKS
    What could contradict what. Names, dates, who was present, what somebody
    already said. Check the timeline and the character bibles before writing.
```

---

## Worked example

```
SCENE ID           theo_ledger_question
STATUS             prototype
CHARACTERS         Theo. Iris mentioned, absent.
LOCATION           archive_room
TIME               any slot, phase normal or odd

PURPOSE
    Turn "an odd photograph" into "a documented anomaly", by having the most
    rigorous person in the cast confirm it against ninety-one pages.

NARRATIVE FUNCTION
    Escalates. Also the payoff for keeping a promise, which is the first time
    the game charges for one.

EMOTIONAL START    Mild curiosity; the player is doing a favour.
EMOTIONAL END      The specific discomfort of a system that does not fail,
                   failing once.

CHARACTERS KNOW
    Theo: the column has no date header; fourteen entries; ninety-one pages
        checked; nobody has ever forgotten.
    Player: the photograph exists and is unlisted.

CHARACTERS DON'T KNOW
    Theo does not know about Iris's second index.
    Neither knows what the stamp says.

PLAYER MAY LEARN
    attendance_sheet_anomaly
    theo_checks_the_ledger (through him, not stated)

PLAYER MUST NOT LEARN YET
    The date itself. That belongs to the `the_date` anchor. A scene that lets
    the player read "32" here spends the reveal for nothing.

SETUPS             The eleven items in box seventeen. The two in the maybe pile.
PAYOFFS            The promise made in message_after_class.

CHOICES
    "Someone forgot."      — skeptical. +respect. He has already checked.
    "What's in the column?" — curious. +trust. Names the photograph, and the
                              player feels their own pocket.
    "Does Iris know?"      — direct. +familiarity, +suspicion. Puts Iris between
                              them, and moves her stance on the anomaly.

STATE EFFECTS
    fulfil(meet_theo_archive)
    know(attendance_sheet_anomaly, theo_showed_me)
    item(attendance_ledger)
    rel theo.trust +6, rel theo.respect +3
    (per choice: see `outcomes` in data/storylets/theo_ledger_question.json)

CONTINUITY RISKS
    - Ninety-one pages and three volumes are now canon. Do not contradict.
    - Fourteen entries: 11 in box seventeen, 2 in the maybe pile, 1 photograph.
      That arithmetic is load-bearing.
    - Theo must not have met Iris about this yet; check `npc_stance` effects.
```
