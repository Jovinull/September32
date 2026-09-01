# The character network, Act 1

The protagonist walked into a community that already existed. These five did not
start knowing each other when the player arrived, and the writing has to hold
that.

## The graph

```
                          ┌──────────────────┐
                          │      IRIS        │
                          │  archive, alone  │
                          │   since March    │
                          └───┬──────────┬───┘
                  respects,   │          │  wants access,
                  finds her   │          │  has asked five times
                  method      │          │
                  irritating  │          │
                          ┌───┴───┐  ┌───┴────┐
                          │ THEO  │  │  NOAH  │
                          └───┬───┘  └───┬────┘
                              │          │
              agrees with her │          │ two years of
              and is not      │          │ mutual, cheerful
              thanked for it  │          │ non-comprehension
                          ┌───┴──────────┴───┐
                          │       JUNE       │
                          └────────┬─────────┘
                                   │  four years of Thursdays;
                                   │  June has not noticed
                          ┌────────┴─────────┐
                          │       MARA       │
                          │ here since she   │
                          │    was eleven    │
                          └──────────────────┘

        MARA ── THEO :  a mug moved four inches. Neither would call it anything.
        MARA ── IRIS :  barely know each other. Genuinely.
        NOAH ── THEO :  no relationship at all. Have never needed one.
```

## The pairs

### June ↔ Mara — **the load-bearing one**

**Before the player arrived:** four years in the same building. June arrived at
fifteen, alone, in February; Mara has been here since she was eleven. They are
comfortable and they are not close, and the difference is the interesting part.

**What each thinks:** June finds Mara restful and slightly immovable and would
call her a friend. Mara would too, and would also privately note that June has
never once asked why she does Thursday.

**Where the player sees it:** `hallway_after_bell` (June negotiating a lift out
of her), `common_room_three_way` (the rota, which is not about the rota).

**Axes that move:** `mara->june.resentment` rises if the player sides with June
on the rota. `june->mara.familiarity` rises if the player says thank you on
Mara's behalf. The player is not on either edge.

---

### Iris ↔ Noah — **the one with an actual conflict**

**Before:** he has asked for twenty minutes in the archive five times. She has
said not yet, the same way each time, which he has decided is a good sign.

**What each thinks:** Noah thinks Iris is being precious about a school store
cupboard. Iris thinks Noah has not understood that a catalogue nobody has read
in eleven years is a different object from an archive. Both are partly right.

**Where the player sees it:** `annexe_two_of_them`, entirely. This is the
sharpest fork in Act 1 and the player has to pick.

**Axes:** `noah->iris.resentment` and `iris->noah.suspicion` move in opposite
directions depending on the branch. The reserved branch moves
`iris->noah.familiarity` instead — the player makes neither of them like *them*
more, and makes the two of them marginally easier with each other.

---

### Theo ↔ Iris — **respect without ease**

**Before:** they work in the same room and have never once been social in it.
He respects her completely and finds her methodology irritating: she photographs
before she catalogues, which from a completeness standpoint is a step that
produces nothing.

**Where the player sees it:** `archive_theo_returns`. Two people being precise
at each other, both correctly, which is the stage immediately before an argument
— and the scene now reads `iris->theo.suspicion` and `theo->iris.respect` and
changes accordingly.

---

### Theo ↔ Mara — **four inches of mug**

**Before:** almost nothing. They have been in the same rooms for years.

**What each thinks:** she knows he goes the long way round with the ledger and
why. He does not know she knows. She makes his tea correctly without being asked
and he moves it four inches to the left without looking up.

**Where the player sees it:** `the_common_room`, in one sentence, once.

This is the pair that most rewards not being explained.

---

### June ↔ Noah — **cheerful non-comprehension**

**Before:** two years of liking each other and not understanding each other at
all. She thinks the paper is a hobby he has let get out of hand. He thinks she
is the most capable person here and cannot work out why she is not doing
anything with it.

**Where the player sees it:** `courtyard_lunch_table`. "It's a school paper.
Nobody reads it." / "Four hundred people live here and about six of them write
anything down."

---

### Mara ↔ Iris — **the honest gap**

**Before:** barely know each other, and this is the true answer rather than a
placeholder. Mara's map of the school is social; Iris has been in one room since
March and is not on it.

**Not a hole to fill.** In a building of four hundred people, most pairs do not
have a relationship, and a cast where everybody has history with everybody is a
cast of six people in an otherwise empty school.

---

### Noah ↔ Theo — **nothing**

They have never needed one. Recorded so that nobody writes a scene assuming
there is history and then has to invent it.

---

## Where the player fits

Everybody's `familiarity` toward the player starts at zero and everybody else's
toward each other does not. That asymmetry is the whole of "you are new", and it
is why `courtyard_before_you` exists: a running joke, a grudge and an
arrangement, none of them explained, none of them about the player.

The player can change NPC-to-NPC edges in exactly four scenes —
`common_room_three_way`, `annexe_two_of_them`, `courtyard_the_bench`,
`courtyard_lunch_table` — and in all four it costs them something on an edge
they are not standing on. That is the design: taking a side is not free, and the
consequence is not aimed at them.

## Rules

**Do not connect everybody.** Two of the ten pairs above are "barely" and "no
relationship at all", and both are load-bearing.

**Do not explain the pairs to the player.** The mug is not annotated. The four
years of Thursdays are said once, by June, as an accusation about a rota.

**Every pair needs a before.** Even if the before is "they have been in the same
rooms for years and have never spoken", write it down here first. A pair whose
history is invented in the scene that needs it will contradict the next scene
that needs it.
