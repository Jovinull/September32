# ADR-0004 — No AI in the shipped game

**Status:** Accepted · 2026-08-30 · **Binding**

## Context

AI is used heavily to build this project: code, research, drafting, continuity
checking, tooling. A natural next step would be to use it at runtime — dynamic
dialogue, generated variation, an LLM-driven character.

## Decision

**The shipped game contains no AI of any kind.**

Specifically, it does not and will not include:

- any LLM, local or remote, from any vendor;
- any API call to any service;
- procedural text generation of dialogue or narration;
- runtime image or audio generation;
- a chatbot, an "AI character", or generated variation of any authored line;
- any network access at all.

Every line the player reads is pre-written by a person and committed here. The
engine decides *which* pre-written scene fits the current state, when, and in
what variant. It never writes one.

## Alternatives

**LLM-generated ambient dialogue.** Rejected on four independent grounds, any one
of which would be sufficient:

1. *Quality.* This game's writing depends on a voice: what a character does not
   say, how long they pause, which word they choose twice. Generated prose does
   not have a voice, it has a register, and the difference is exactly the thing
   the project is about.
2. *Continuity.* A generated line can contradict canon, and by the time it is
   read it is already in the player's head. Every scene here is reviewable
   before it ships. That is not a constraint, it is the product.
3. *Reproducibility.* A bug that cannot be reproduced cannot be fixed. Generated
   content makes every bug report approximate.
4. *Player trust.* Offline, no account, no telemetry, no network. A single-player
   game should not need a connection to tell its story, and a player should not
   have to wonder what is being sent anywhere.

**A small local model for variation.** Rejected: same continuity and voice
problems, plus hundreds of megabytes of download and a hardware floor, in
exchange for variation that authored variants provide better.

## Consequences

**Good**

- The game runs forever, offline, with no dependency on a service that can
  change its terms, its prices, or its existence.
- Every line is reviewable, translatable, and attributable.
- No inference cost, no latency, no rate limit, no privacy question.
- Reproducible: a seed plus a save is a complete bug report.

**Bad, and accepted**

- Variation must be authored. Mitigated by the storylet architecture, which is
  precisely a machine for recombining authored content.
- We cannot claim "infinite" content, and will not. See
  `docs/narrative-design/PACING.md` — the honest claim is hundreds of
  hand-written scenes recombined by state.

## Enforcement

- `s32_engine` has no third-party dependencies and no network code.
- A test asserts the engine imports nothing outside the standard library.
- `AGENTS.md` states the rule for every future contributor.
- Any PR adding a network call to the game is rejected on sight.
