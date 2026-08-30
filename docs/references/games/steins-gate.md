# Steins;Gate

Original analysis. No content from the work is reproduced here.

## USE FOR

**Small actions with large, delayed consequences.** The mechanism is
deliberately mundane — a message sent or not — and the distance between cause and
effect is where the dread lives.

**Comedy and warmth as investment.** Its first act is largely jokes. That is the
budget the second act spends, and the exchange rate is excellent.

**Consequence discovered rather than announced.** The player finds out what they
did by living in the result.

**A single tight cast** whose relationships are the actual stakes.

## DO NOT COPY

Time travel. The scientific apparatus. Any character. The lab, the messaging
mechanic, the specific structure of its consequences.

## PRINCIPLE

> Let a small, unremarkable decision produce a consequence far enough away that
> the player has to reconstruct the link themselves.

## RELEVANCE TO SEPTEMBER 32

This is what the commitment system is for. `promise("meet_theo_archive", "theo",
in_days=1)` creates an obligation that comes due later, and skipping it does not
subtract a number — it changes where Theo is, which changes what he finds.

The design brief's own example is exactly this shape: skipping class with Iris
improves her trust, breaks a promise to Theo, sends Theo somewhere alone, and
alters a scene hours later.

The delay is the point. `days_since()` and `commitment()` conditions exist so a
storylet can depend on something that happened days ago.

## RISKS

**Making the mechanism the subject.** Its consequences flow through an explicit
device the player operates. This game's flow through ordinary social obligation,
which is subtler and much easier to make invisible. If the player cannot
reconstruct the link at all, it is not delayed consequence — it is randomness.
