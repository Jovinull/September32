# assets/

The asset pipeline, and the legal record behind it.

## The rule

**No third-party binary is committed to this repository. Not one, regardless of
its licence.**

Most of these licences permit use in a game and forbid redistributing the files —
including modified ones, which a git repository would do. One rule for all of
them is enforceable; a per-pack exception is not.
See `docs/decisions/ADR-0003-asset-licensing.md`.

## Layout

| Path | Committed | Contents |
| --- | --- | --- |
| `catalog/assets.toml` | **yes** | The licence record. Hand-written, reviewed, never rewritten by a tool. |
| `catalog/acquisition.toml` | **yes** | Hashes, timestamps, status. Generated. |
| `catalog/import_log.json` | **yes** | Which files were kept, renamed to what, processed how. |
| `evidence/<id>/` | **yes** | What the terms said, on the date they were read. |
| `.downloads/` | no | Downloaded archives. |
| `vendor/<id>/` | no | Untouched originals. |
| `processed/<kind>/` | no | Game-ready derivatives. |

The committed half is the point: the repository records exactly which bytes were
reviewed, under what terms, without containing them.

## Reconstructing everything

```bash
uv run s32 assets fetch      # official sources only, hashes recorded
uv run s32 assets install    # extract, process, copy into game/
uv run s32 assets images     # regenerate Ren'Py image definitions
```

The game runs without any of it — Ren'Py substitutes placeholders for missing
images, which is how every new contributor first sees it.

## Adding an asset

The full procedure is in `docs/legal/ASSET_LICENSING.md`. The two rules that
catch most mistakes:

**Free is not public domain.** Record `commercial_use`,
`modification_allowed`, `redistribution_allowed` and `attribution_required`
separately, because they have different answers.

**"Royalty-free" is not a licence.** It is a payment model.
`s32 assets verify --catalog` fails if it appears in `license_name`. Use
`--installed` to check local archive hashes and installed game files as well.

## AI

No third-party asset is ever sent to an AI service — not for generation, not for
editing, not for analysis. The visual-consistency audit is local and
deterministic for exactly that reason.
See `docs/legal/AI_AND_ASSETS_POLICY.md`.
