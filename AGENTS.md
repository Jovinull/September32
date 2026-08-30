# AGENTS.md — rules for anyone, human or AI, working on September 32

This file is binding. If something here conflicts with a general instinct about
how to build software, this file wins, because most of these rules exist to stop
a specific failure this project cannot absorb.

---

## 0. Before you touch anything

Read, in this order:

1. `docs/production/PROJECT_STATE.md` — what exists, what is broken, what is next.
2. The canon docs relevant to your task (`docs/canon/`).
3. The character bibles for anyone you are writing (`docs/characters/`).
4. `docs/style/` for the register you are writing in.

Then run `s32 doctor`. If it fails, fix that before starting the task you came
for. Working on top of a broken checkout produces changes nobody can review.

---

## 1. The three rules that are not negotiable

### 1.1 No AI at runtime, ever

The shipped game contains **no** LLM, no API call, no model, no procedural text
generation, no runtime image generation, and no network access of any kind. Every
line the player reads was written by a person and committed to this repository.

The engine decides *which* pre-written scene fits. It never writes one.

AI is used heavily *during development* — code, research, drafting, review,
continuity checking. That is a different thing and the boundary is absolute. See
`docs/decisions/ADR-0004-no-runtime-ai.md`.

### 1.2 Never invent canon

You may not decide, mid-scene, that September 32 happens because of a machine, a
ritual, a hallucination, or anything else, and then write as though that were
settled. Not even as a small implication. Not even in a line of narration.

Structural lore changes go through this process:

1. Propose it in `docs/canon/OPEN_QUESTIONS.md` with the reasoning.
2. If accepted, record it in the relevant `docs/canon/` file with an explicit
   status marker: `CANON`, `PROVISIONAL`, `IDEA`, or `REJECTED`.
3. Update `TIMELINE.md` and `PHENOMENON_RULES.md` if affected.
4. Re-check every existing scene that touches it.
5. Run `s32 validate`.

An unmarked assertion in a scene is not canon. It is a bug.

### 1.3 Never add a third-party asset without its licence

Before any asset enters this project:

- Record it in `assets/catalog/assets.toml` with **concrete** permissions, not a
  vague label. "Royalty-free" is a payment model, not a licence.
- Capture evidence in `assets/evidence/<id>/LICENSE_EVIDENCE.md`: the date, the
  page, the terms as written.
- Confirm `commercial_use`, `modification_allowed`, `redistribution_allowed`,
  `attribution_required` individually.
- Run `s32 assets credits` so the credit surfaces regenerate.

**Free is not public domain.** If the terms are ambiguous, pick a different
asset. See `docs/legal/ASSET_LICENSING.md`.

---

## 2. Assets

- **Never send third-party artwork to an AI service.** Not for analysis, not for
  upscaling, not for style transfer, not for "just looking at it". Visual
  analysis uses the local, deterministic tooling in `tools/s32tools/assets/`.
  See `docs/legal/AI_AND_ASSETS_POLICY.md`.
- **Never modify an asset with a generative model.** The processing pipeline is
  arithmetic on pixels, and it stays that way.
- **Respect an author's anti-AI request even when the licence would permit
  ignoring it.** If a page says CC0 and also says "do not use with AI", use a
  different asset. This project does not want an argument with an artist.
- **Do not mix character art across artists.** The cast comes from one character
  system (ADR-0005). A new source needs a consistency audit
  (`s32 assets audit`) and a written justification.
- **Never commit third-party binaries.** `assets/vendor/` and
  `assets/processed/` are gitignored because most of these licences forbid
  redistributing the files, including modified ones. What is committed is the
  manifest, the hashes, the evidence and the import log.

---

## 3. Code

- **No new dependency without a justification in the PR description**, and none
  at all in `s32_engine` — it must stay standard-library only, because Ren'Py
  cannot install wheels.
- **Nothing that breaks rollback.** No generators, file handles, sockets, async
  tasks, or custom class instances in game state. Containers in state come from
  `s32_engine.containers`, never from a literal. This is not stylistic: see
  ADR-0007, and note that the rollback bug this prevents is invisible until a
  player scrolls up.
- **Randomness goes through `s32_engine.rng.Rng`.** Never `random`. The engine's
  RNG is counter-based so that rolling back and replaying gives the same result.
- **Content ids are permanent.** Once a storylet is `active`, its `id` appears in
  save files, achievements and analytics. Renaming it breaks all of them.
- **No large refactors without a reason.** "I would have structured it
  differently" is not a reason.
- **Do not over-abstract.** A dict is usually fine. An interface with one
  implementation is not an interface.

---

## 4. Writing

- Consult the character bible before writing a character. If the scene requires
  them to act against it, that is a character development *proposal*, not a
  scene: raise it.
- Every non-trivial scene gets a scene card
  (`docs/narrative-design/SCENE_CARD_TEMPLATE.md`) before the prose.
- **Declare your state changes in metadata.** If a choice inside a `.rpy` menu
  changes a relationship or grants a fact, it goes in the storylet's `outcomes`
  list too. A change the tooling cannot see makes later content look
  unreachable, and the tools will report it as dead.
- After writing, review for: continuity, voice, repetition, over-explanation,
  foreshadowing that now pays off or now does not, and contradictions with canon.
- The AI is an assistant to the writing, not an authority over it.

---

## 5. Before you call anything done

```
s32 doctor
s32 validate
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
s32 renpy lint
s32 renpy test
s32 simulate --runs 500
```

All green, or the work is not done. If something cannot be made green, say so
explicitly and mark it `BLOCKED`, `PARTIAL` or `FAILED` in
`docs/production/PROJECT_STATE.md`. Never write `DONE` without evidence.

---

## 6. Things you must not do on your own initiative

- Push to a remote.
- Create a release, a tag, or a build for distribution.
- Publish to itch.io, Steam, or anywhere else.
- Change the project's licence.
- Delete or rewrite `assets/catalog/assets.toml` records.
- Rename existing storylet, knowledge, character or anchor ids.
- Change `config.save_directory`.
- Add telemetry, analytics, crash reporting, or any network call.

---

## 7. Keep the record straight

- Update `docs/production/PROJECT_STATE.md` when the state of the project
  changes.
- Add an ADR (`docs/decisions/`) for any decision a future contributor would
  otherwise have to reverse-engineer.
- Log research in `docs/research/RESEARCH_LOG.md` with sources, findings, and a
  confidence marker: `CONFIRMED`, `LIKELY`, `UNKNOWN`.
- If you were blocked, write down exactly what blocked you and what someone
  would have to do by hand. A blocked step that is documented is progress; a
  blocked step that is hidden is a trap.
