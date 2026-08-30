# ADR-0001 — Ren'Py as the engine

**Status:** Accepted · 2026-08-30

## Context

September 32 is a visual novel: text, dialogue, sprites, backgrounds, music,
choices, saves, rollback, history, skip, auto-forward, preferences,
localisation, and a three-platform desktop build. The novel part is the product;
everything else is plumbing that has been solved.

The alternatives considered were general-purpose engines (Godot, Unity) and
writing a renderer directly.

## Decision

Use **Ren'Py 8.5.3**, the current stable release as verified on
<https://www.renpy.org/latest.html> on 2026-08-30. Not a nightly.

The SDK is pinned by version *and* SHA-256 in `tools/s32tools/renpy_sdk.py`, and
installs to `.tools/renpy/` which is gitignored. `S32_RENPY_SDK` overrides the
location for a developer who already has one.

Advanced narrative logic lives in Python (`s32_engine`), not in Ren'Py script.
Ren'Py presents; the engine decides.

## Alternatives

**Godot** — a capable engine, and a worse fit. Every item in the list above
would be rebuilt: save/load, rollback, a text-history screen, skip modes,
preference persistence, translation extraction. That is months of work to arrive
at what Ren'Py ships, and the result would be less tested than Ren'Py's, which
has shipped thousands of commercial visual novels.

**Unity** — the same objection, plus a licensing relationship this project does
not need.

**A custom engine** — only defensible if the presentation were the novel part of
the product. It is not; the *narrative architecture* is, and that is being built
custom, on top of an engine that handles the rest.

## Consequences

**Good**

- Save, load, rollback, history, skip, auto-forward, preferences and
  translation all work on day one, correctly, including the edge cases.
- The build pipeline produces Windows, Linux and macOS packages from one
  command.
- A large body of existing knowledge and a community that has hit these problems
  before.

**Bad, and accepted**

- Ren'Py's rollback imposes real constraints on how state may be stored. This is
  the single biggest architectural consequence and is addressed in ADR-0007.
- Python 3 inside Ren'Py's own interpreter: no pip, no wheels. Hence
  `s32_engine` being standard-library only, and the dev toolchain living in a
  separate package.
- Ren'Py's default GUI has a recognisable look. Replacing it is planned work,
  not accidental (see `docs/style/VISUAL_DESIGN_SYSTEM.md`).
- Web export exists but is not a production target; the architecture does not
  block a later port.

## Revisit if

The project stops being primarily a visual novel — if real-time systems, 3D, or
significant simulation become central, the balance changes.
