# ADR-0003 — Third-party assets are never committed

**Status:** Accepted · 2026-08-30

## Context

The project uses free third-party art, music and fonts. Their licences differ
sharply, and one clause recurs in the visual-novel asset packs this project
depends on. Verbatim, from Potat0Master's pack pages on 2026-08-30:

> "You can edit and modify these images. However, you cannot resell or
> distribute the images in the form that it is downloaded or even when it is
> modified."

Using the art in a game is permitted. Putting the files in a public git
repository is distribution of those files — including, explicitly, modified
ones. So the ordinary approach of vendoring assets into the repo is not
available.

The CC0 assets (Kenney) and the OFL fonts (Adobe) *may* be redistributed.

## Decision

**No third-party binary is committed to this repository. Not one, regardless of
its licence.**

- `assets/vendor/` — untouched originals. Gitignored.
- `assets/processed/` — game-ready derivatives. Gitignored, because a derivative
  of a non-redistributable original is still a distribution of a modified form.
- `game/images/vendor/`, `game/audio/vendor/`, `game/gui/vendor/` — what Ren'Py
  loads. Gitignored.

What **is** committed, and is the point:

- `assets/catalog/assets.toml` — the licence record, hand-written, tool-free.
- `assets/catalog/acquisition.toml` — hashes and timestamps, generated.
- `assets/catalog/import_log.json` — which files were kept, renamed to what,
  processed how.
- `assets/evidence/<id>/` — what the terms said on the date they were read.

`s32 assets fetch && s32 assets install` reconstructs everything on a
developer's machine from official sources, verifying hashes.

Git LFS is configured for but **not enabled**. When first-party art exists,
enable it then.

## Alternatives

**Vendor the CC0 assets and gitignore the rest.** Rejected. A per-pack exception
means every contributor must know which pack has which rule, and the failure
mode is committing something that should not be committed. One rule — "no
third-party binaries in the repo" — is enforceable by a `.gitignore` line and
memorable by everyone.

**Git LFS for everything.** LFS is about repository size, not licensing. It does
not make redistribution permitted.

**A private submodule.** Adds a second repository to keep in sync and does not
change the licensing question for anyone with access.

## Consequences

**Good**

- The repository can be made public without a licence audit.
- Provenance is genuinely traceable: for every project filename there is a
  recorded original name, source URL, hash and set of transformations.
- The repository stays small; a fresh clone is a few megabytes.

**Bad, and accepted**

- A new contributor must run `s32 assets fetch` before the game shows art. The
  game is designed to run without it, using placeholders (`docs/production/`).
- CI has two modes: code-only (no proprietary assets) and full local.
- If an upstream page disappears, the recorded hash proves what was used but
  does not restore the file. Developers keep local copies; that risk is accepted
  because the alternative is redistributing without permission.

## Revisit if

The project commissions or creates its own art, which is redistributable by
definition. That art *is* committed, via Git LFS.
