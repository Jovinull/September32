"""Capturing what the licence terms said, on the day they were read.

A manifest entry asserts that a pack may be used. This directory is the reason
to believe it: the page, the date, the terms as written, and the hash of the
file that was actually downloaded.

The point is defensibility over time. Pages change, creators revise terms,
projects outlive memory. "We read this, on this date, and here is what it said"
is a materially different position from "we thought it was fine".

Each entry gets ``assets/evidence/<id>/LICENSE_EVIDENCE.md``, which is
committed. Where a page snapshot can be taken it goes beside it as
``page.html``; that snapshot is *not* committed, because a full copy of a
creator's page is their content, not ours. The extracted terms — a short
quotation for the purpose of record-keeping — are.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from s32tools.assets.manifest import AssetEntry, Manifest

TEMPLATE = """# Licence evidence — {name}

> Committed record of the terms under which this asset is used.
> Written by `s32 assets evidence`; reviewed by a human before it counts.

## Identification

| | |
| --- | --- |
| Asset id | `{asset_id}` |
| Name | {name} |
| Author | {author} |
| Type | {type} |
| Source page | <{source_page}> |
| Download source | {download_source} |
| Retrieved | {retrieved_at} |

## The file that was reviewed

| | |
| --- | --- |
| Archive | `{archive}` |
| SHA-256 | `{sha256}` |

The hash is what makes this record specific. A later re-download that produces
different bytes is detectable by `s32 assets verify`, which is the difference
between "we checked this pack" and "we checked this file".

## Licence

| | |
| --- | --- |
| Licence | {license_name} |
| Licence source | <{license_source}> |
| Terms read on | **{license_verified}** |

### Permissions, as recorded

| Permission | |
| --- | --- |
| Commercial use | {commercial_use} |
| Modification | {modification_allowed} |
| Redistribution of the files themselves | {redistribution_allowed} |
| Attribution required | {attribution_required} |

`redistribution_allowed` is the field that decides whether the binaries may be
committed. See `docs/decisions/ADR-0003-asset-licensing.md`: this project's
answer is "no third-party binaries in the repository" regardless, because one
rule is easier to follow than eleven.

### Terms as written

The following was on the source page on {license_verified}. Quoted for the
purpose of recording what the terms were.

```
{license_summary}
```

### AI-related terms

```
{ai_related_terms}
```

This project's own policy is stricter than most licences require: no
third-party asset is ever sent to an AI service, used for training, or modified
by a generative model. See `docs/legal/AI_AND_ASSETS_POLICY.md`.

## Attribution text

The exact credit shown in-game and in `CREDITS.md`:

```
{required_credit}
```

## Notes

{notes}

---

*Generated {generated_at}. If the terms on the source page have changed since
{license_verified}, this file records what they were, not what they are — re-read
them and add a new dated section rather than editing this one.*
"""


def _yes_no(value: bool) -> str:
    """Render a permission unambiguously. 'NO' shouts on purpose."""
    return "yes" if value else "**NO**"


def render(entry: AssetEntry) -> str:
    """Render the evidence document for one manifest entry."""
    return TEMPLATE.format(
        asset_id=entry.id,
        name=entry.name,
        author=entry.author,
        type=entry.type,
        source_page=entry.source_page,
        download_source=entry.download_source or "(recorded in assets.toml)",
        retrieved_at=entry.retrieved_at or "not yet downloaded",
        archive=entry.original_archive_name or "not yet downloaded",
        sha256=entry.original_sha256 or "not yet downloaded",
        license_name=entry.license_name,
        license_source=entry.license_source,
        license_verified=entry.license_verified,
        commercial_use=_yes_no(entry.commercial_use),
        modification_allowed=_yes_no(entry.modification_allowed),
        redistribution_allowed=_yes_no(entry.redistribution_allowed),
        attribution_required=_yes_no(entry.attribution_required),
        license_summary=(entry.license_summary.strip() or "(not recorded — this is a gap)"),
        ai_related_terms=(entry.ai_related_terms.strip() or "None stated on the source page."),
        required_credit=entry.credit_line(),
        notes=(entry.notes.strip() or "None."),
        generated_at=datetime.now(UTC).date().isoformat(),
    )


def write_all(manifest: Manifest, evidence_root: Path) -> list[Path]:
    """Write an evidence document for every manifest entry."""
    written: list[Path] = []
    for asset_id, entry in sorted(manifest.entries.items()):
        directory = evidence_root / asset_id
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "LICENSE_EVIDENCE.md"
        path.write_text(render(entry), encoding="utf-8")
        written.append(path)
    return written
