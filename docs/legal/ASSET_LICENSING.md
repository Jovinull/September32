# Asset licensing

How third-party material is acquired, recorded and used. The decision behind it
is `docs/decisions/ADR-0003-asset-licensing.md`; this is the working procedure.

## Two rules that catch most mistakes

### Free is not public domain

An asset being downloadable at no cost tells you nothing about what you may do
with it. Every entry records `commercial_use`, `modification_allowed`,
`redistribution_allowed` and `attribution_required` as separate booleans, because
those are the four questions that actually get asked and they have different
answers.

### "Royalty-free" is not a licence

It is a payment model: you pay once, or nothing, rather than per use. It says
nothing about redistribution. `s32 assets verify` **fails** if `license_name` is
"royalty-free", "royalty free" or "free" — the concrete terms have to be recorded
instead.

## The clause that shapes everything

From the Potat0Master pack pages, verbatim as read on 2026-08-30:

> "You can edit and modify these images. However, you cannot resell or distribute
> the images in the form that it is downloaded or even when it is modified."

Using the art in a game: permitted. Committing the files to a public git
repository: distribution of those files, including — explicitly — modified ones.

Hence: **no third-party binary is committed to this repository, regardless of its
licence.** One rule, enforceable by `.gitignore`, memorable by everyone. A
per-pack exception would mean every contributor has to know which pack has which
rule, and the failure mode is a commit that should not have happened.

## What is committed

| Path | Contents |
| --- | --- |
| `assets/catalog/assets.toml` | The licence record. Hand-written, reviewed, never rewritten by a tool. |
| `assets/catalog/acquisition.toml` | Hashes, timestamps, status. Generated. |
| `assets/catalog/import_log.json` | Which files were kept, renamed to what, processed how. |
| `assets/evidence/<id>/` | What the terms said, on the date they were read. |

Everything under `assets/vendor/`, `assets/processed/`, `game/images/vendor/`,
`game/audio/vendor/` and `game/gui/vendor/` is gitignored. A test asserts that
`git ls-files` finds nothing there.

## Adding an asset

1. **Find it at its official source.** The creator's own page, or the project's
   own release. Never a mirror, an aggregator or a reupload.
2. **Read the terms. All of them.** Including anything about AI.
3. **Write the manifest entry**, with `license_summary` quoting the terms as
   written and `license_verified` set to today.
4. **Add a `Source`** to `tools/s32tools/assets/sources.py`, with a
   `variant_rationale` explaining why that file and not the others on the page.
5. `s32 assets fetch --asset <id>` — downloads it and records its SHA-256.
6. `s32 assets evidence` — generates the evidence file. **Read it.** A generated
   record is only evidence once a human has confirmed it matches the page.
7. `s32 assets install` — extract, process, copy into the game.
8. `s32 assets credits` — regenerate every credit surface.
9. `s32 assets verify` — hygiene check.

## Manual downloads

Some pages cannot be fetched programmatically without bypassing something, and
this project does not bypass anything: no scraping around authentication, no
CAPTCHA solving, no touching paid files.

When a fetch cannot proceed, `s32 assets fetch` prints a `MANUAL DOWNLOAD
REQUIRED` block naming the page, the exact file, and the destination — and then
**continues with the next source**. A blocked download must never take the rest
of the pipeline with it.

A manually-downloaded file is a first-class citizen. Put it in
`assets/.downloads/<asset id>/` and run `s32 assets install`: it hashes the
archive, writes the hash to `acquisition.toml`, extracts, processes and copies
into the game. However the file arrived, the record ends up the same.

If an archive is already recorded and no longer matches its hash, `install`
refuses to update the record and says so. A changed hash means the file on disk
is not the one that was reviewed, and quietly re-recording it would erase the
only evidence of that.

The itch.io downloads that *do* work use the public, no-account flow — precisely
the three requests a browser makes when a visitor clicks "Download Now" and then
"No thanks, just take me to the downloads" on a free page. The client
(`tools/s32tools/assets/itch.py`) identifies itself honestly rather than
impersonating a browser, and backs off politely on rate limiting.

## Verification

`s32 assets verify` checks:

- Every entry has an evidence directory containing `LICENSE_EVIDENCE.md`.
- Every entry with `attribution_required` has non-empty `required_credit`.
- No entry uses a payment model as a licence name.
- Every installed entry has a SHA-256 and an acquisition timestamp.
- Every downloaded archive still hashes to what the manifest records — a
  mismatch means the file on disk is **not** the one that was reviewed, and it
  says so in those words.
- Any entry whose `ai_related_terms` mentions a prohibition, for human review.

## Three licences, never conflated

1. **Ren'Py's** — MIT, plus the licences of the components it bundles. The build
   step generates the required notices.
2. **This project's** — see `/LICENSE`. Provisional, all rights reserved.
3. **Each asset's** — `assets/catalog/assets.toml`, and nothing in the other two
   grants any right over them.

`THIRD_PARTY_NOTICES.md` is generated and keeps them separate by construction.
