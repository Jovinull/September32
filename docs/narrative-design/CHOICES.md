# Choices

## The test

A choice must do at least one of these:

1. Reveal something about who the player is.
2. Change a relationship.
3. Change what somebody knows.
4. Create, keep or break a commitment.
5. Change a resource — time, access, an object.
6. Change who is available, and when.
7. Open or close a possibility.
8. Produce a consequence somewhere else.

A choice doing none of these is flavour. Flavour is fine — a menu that only lets
the player pick a tone is doing real work — but label it, and do not let the
game fill up with it.

## What good choices are not

**Not morality tiers.**

```
A = kind
B = neutral
C = cruel
```

The player is not choosing an alignment; they are choosing between things they
want. A cruel option that no reasonable player picks is not a choice, it is
decoration.

**Trade-offs instead:**

```
A protects Iris, and disappoints Theo.
B helps Theo, and breaks a promise to Iris.
C tries for both, and loses the thing you went there for.
```

Every option costs something. The player should feel the cost before they pick,
and find out afterwards that it was different from what they expected.

**Not a knowledge check.** A choice whose correctness depends on information the
player could not have is a trap, and it teaches them to save-scum. A choice whose
correctness depends on information they *did* have and did not use is legitimate,
and it is one of the best things this architecture can do.

**Not the same choice repeatedly.** If a character offers "be warm / be distant"
in every scene, that is one choice made eight times. Vary what is actually at
stake.

## Trait-gated choices

Traits accumulate; they are never chosen. A trait-gated option is *additional* —
it never replaces an ordinary one, and never makes the player who lacks it feel
short-changed.

```renpy
menu:
    "Ask her about the folder.":
        ...
    "[trait_label('curious')] You have seen this keyring before." if has_trait("curious"):
        ...
```

The label is bracketed so the player can see they earned it. Threshold is 3 by
default — three or four consistent decisions. Low on purpose: being *seen* as
curious should be cheap, and being *rewarded* for it should be frequent enough to
notice.

## Declaring what a choice does

Every state change a choice makes must appear in the storylet's `outcomes` list,
in the order the choices appear. This is not bookkeeping:

> The simulator reported `rain_after_school` unreachable because it needs
> `iris.trust >= 10` and no declared effect could raise trust past 2. The trust
> was there — it came from choices inside the prose, where nothing could see it.

A state change the tooling cannot see makes later content look dead, and the
report will say so. See ADR-0006.

## Presentation

- Options read as things a person would say or do, not as summaries of their
  effects.
- Never number the consequences in the option text.
- Keep options roughly the same length: a visibly longer one reads as the
  "real" answer.
- If two options would produce the same state, they are one option with two
  phrasings. That is allowed, and it should be deliberate.
