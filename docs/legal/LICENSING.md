# Licensing this project's own content

**Status: undecided, deliberately, and blocking nothing.**

## The current position

`/LICENSE` says all rights reserved. That is a conservative default, not a
decision — it exists so the repository has an unambiguous answer while the actual
question stays open.

## Why not just MIT

Because this repository contains two very different things:

**Engine and tooling.** `s32_engine`, `s32tools`, the CI configuration, the
build scripts. Reusable, and a permissive licence would be reasonable.

**Narrative content.** The script, lore, characters, names, design documents, and
eventually the art and music. Making these open source would mean anyone may
publish a modified September 32, and the project has not decided it wants that.

A blanket MIT at the top of the repository licenses both. That is very easy to do
by accident and effectively impossible to undo, because the moment a permissive
grant is published somebody may have relied on it.

## The likely shape

`IDEA`, needs an ADR before it is real:

- Engine and tooling: a permissive licence (MIT or Apache-2.0), once the boundary
  with the narrative content is clean.
- Narrative content, art, music, marks: all rights reserved.
- Third-party assets: unchanged, under their own terms, forever.

The blocker is the boundary. `s32_engine` is currently clean — it contains no
story — but `game/` mixes generated engine glue with authored prose, and the
split has to be real in the directory structure before it can be real in a
licence.

## What must not happen

- A permissive licence applied repository-wide without separating the content.
- A licence change made casually. `AGENTS.md` forbids it without explicit
  instruction.
- A licence that accidentally grants rights over third-party assets. It cannot —
  they are not ours to grant — but a licence file that appears to is a problem
  even when it is legally void.

## Related

- `docs/decisions/ADR-0003-asset-licensing.md`
- `docs/legal/ASSET_LICENSING.md`
- `THIRD_PARTY_NOTICES.md` (generated)
