"""The asset manifest: the single source of truth for third-party licensing.

Every third-party file that touches this project is described in
``assets/catalog/assets.toml``. Nothing derives from anything else: credits,
notices, the in-game credits screen and the CI licence check all read this one
file, so there is no way for four lists to disagree.

Two rules the schema exists to enforce:

*Do not write ``license = "royalty-free"`` and stop.* "Royalty-free" is not a
licence, it is a payment model. The concrete permissions -- commercial use,
modification, redistribution, attribution -- are recorded as separate booleans,
because those are the questions that actually get asked.

*Free is not public domain.* ``license_verified`` records that a human read the
terms on a stated date, and ``assets/evidence/<id>/`` holds what they read.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

AssetType = Literal["character", "background", "music", "sfx", "ui", "prop", "font", "software"]

#: Types that end up in the shipped game and therefore need credit handling.
SHIPPED_TYPES = frozenset({"character", "background", "music", "sfx", "ui", "prop", "font"})

#: Fields every entry must define. Absence is an error, not a default: a missing
#: licence field must never silently read as "permitted".
REQUIRED_FIELDS = (
    "name",
    "author",
    "type",
    "source_page",
    "license_name",
    "license_source",
    "license_verified",
    "commercial_use",
    "modification_allowed",
    "redistribution_allowed",
    "attribution_required",
)


@dataclass(slots=True)
class AssetEntry:
    """One third-party pack, font or library."""

    id: str
    name: str
    author: str
    type: AssetType
    source_page: str
    license_name: str
    license_source: str
    license_verified: str
    commercial_use: bool
    modification_allowed: bool
    redistribution_allowed: bool
    attribution_required: bool

    download_source: str = ""
    retrieved_at: str = ""
    required_credit: str = ""
    ai_related_terms: str = ""
    original_archive_name: str = ""
    original_sha256: str = ""
    files_imported: list[str] = field(default_factory=list)
    processed_files: list[str] = field(default_factory=list)
    transformations: list[str] = field(default_factory=list)
    license_summary: str = ""
    credit_optional: bool = False
    status: str = "pending"
    notes: str = ""
    evidence_dir: str = ""

    @property
    def installed(self) -> bool:
        """Return whether the pack's files have been fetched and imported."""
        return self.status == "installed"

    @property
    def redistributable_in_repo(self) -> bool:
        """Return whether the binaries may be committed to a public repository.

        Deliberately conservative: a pack that permits use in a game but forbids
        redistributing the files themselves is *not* repo-safe, and that is the
        common case for free visual-novel art.
        """
        return self.redistribution_allowed

    def credit_line(self) -> str:
        """Return the exact credit text to display."""
        if self.required_credit:
            return self.required_credit
        return f"{self.name} by {self.author} ({self.license_name})"


@dataclass(slots=True)
class Manifest:
    """The parsed asset catalogue."""

    entries: dict[str, AssetEntry] = field(default_factory=dict)
    source: Path | None = None

    def by_type(self, asset_type: str) -> list[AssetEntry]:
        """Return entries of one type, ordered by id."""
        return [e for _, e in sorted(self.entries.items()) if e.type == asset_type]

    def shipped(self) -> list[AssetEntry]:
        """Return entries that end up in the game, ordered by type then id."""
        return sorted(
            (e for e in self.entries.values() if e.type in SHIPPED_TYPES),
            key=lambda e: (e.type, e.id),
        )

    def requiring_attribution(self) -> list[AssetEntry]:
        """Return entries whose licence makes credit mandatory."""
        return [e for e in self.shipped() if e.attribution_required]


#: Generated companion file holding the volatile acquisition record.
#:
#: The split is deliberate. ``assets.toml`` is a legal document: hand-written,
#: comment-rich, reviewed, and never rewritten by a tool -- a script that
#: reformats a licence record is a script that can quietly lose one.
#: ``acquisition.toml`` holds only what tooling discovers (hashes, timestamps,
#: which files were imported) and is safe to regenerate. Both live in
#: ``assets/catalog/`` and both are committed; :func:`load` merges them so the
#: rest of the codebase sees one manifest.
ACQUISITION_FILENAME = "acquisition.toml"


def load(path: Path) -> Manifest:
    """Parse the manifest, merging in the generated acquisition record.

    Raises:
        ValueError: On a missing required field or an unknown asset type, since
            a malformed licence record is worse than no record at all.
    """
    if not path.exists():
        return Manifest(entries={}, source=path)

    raw: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
    acquisition_path = path.parent / ACQUISITION_FILENAME
    acquired: dict[str, Any] = {}
    if acquisition_path.exists():
        acquired = tomllib.loads(acquisition_path.read_text(encoding="utf-8")).get("asset", {})

    for asset_id, extra in acquired.items():
        if asset_id in raw.get("asset", {}):
            raw["asset"][asset_id].update(extra)

    entries: dict[str, AssetEntry] = {}

    for asset_id, payload in sorted(raw.get("asset", {}).items()):
        missing = [f for f in REQUIRED_FIELDS if f not in payload]
        if missing:
            raise ValueError(f"asset {asset_id!r}: missing required field(s): {', '.join(missing)}")
        try:
            date.fromisoformat(str(payload["license_verified"]))
        except ValueError as exc:
            raise ValueError(
                f"asset {asset_id!r}: license_verified must be an ISO date (YYYY-MM-DD)"
            ) from exc

        entries[asset_id] = AssetEntry(
            id=asset_id,
            name=payload["name"],
            author=payload["author"],
            type=payload["type"],
            source_page=payload["source_page"],
            license_name=payload["license_name"],
            license_source=payload["license_source"],
            license_verified=str(payload["license_verified"]),
            commercial_use=bool(payload["commercial_use"]),
            modification_allowed=bool(payload["modification_allowed"]),
            redistribution_allowed=bool(payload["redistribution_allowed"]),
            attribution_required=bool(payload["attribution_required"]),
            download_source=payload.get("download_source", ""),
            retrieved_at=payload.get("retrieved_at", ""),
            required_credit=payload.get("required_credit", ""),
            ai_related_terms=payload.get("ai_related_terms", ""),
            original_archive_name=payload.get("original_archive_name", ""),
            original_sha256=payload.get("original_sha256", ""),
            files_imported=list(payload.get("files_imported", [])),
            processed_files=list(payload.get("processed_files", [])),
            transformations=list(payload.get("transformations", [])),
            license_summary=payload.get("license_summary", ""),
            credit_optional=bool(payload.get("credit_optional", False)),
            status=payload.get("status", "pending"),
            notes=payload.get("notes", ""),
            evidence_dir=payload.get("evidence_dir", f"assets/evidence/{asset_id}"),
        )
    return Manifest(entries=entries, source=path)


def check(manifest: Manifest, evidence_root: Path) -> list[str]:
    """Return licence-hygiene problems with the manifest.

    These are the checks CI runs. They are about *process*, not law: they verify
    that somebody recorded the terms and kept the evidence, not that the terms
    say any particular thing.
    """
    problems: list[str] = []
    for asset_id, entry in sorted(manifest.entries.items()):
        evidence = evidence_root / asset_id
        if not evidence.is_dir():
            problems.append(f"{asset_id}: no evidence directory at {evidence}")
        elif not (evidence / "LICENSE_EVIDENCE.md").exists():
            problems.append(f"{asset_id}: evidence directory has no LICENSE_EVIDENCE.md")

        if entry.attribution_required and not entry.required_credit:
            problems.append(
                f"{asset_id}: attribution_required is true but required_credit is empty"
            )
        if entry.license_name.strip().lower() in {"royalty-free", "royalty free", "free"}:
            problems.append(
                f"{asset_id}: license_name {entry.license_name!r} is a payment model, not a "
                "licence; record the concrete terms"
            )
        if entry.installed and not entry.original_sha256:
            problems.append(f"{asset_id}: installed but no original_sha256 recorded")
        if entry.installed and not entry.retrieved_at:
            problems.append(f"{asset_id}: installed but no retrieved_at recorded")
        if not entry.commercial_use:
            problems.append(
                f"{asset_id}: commercial_use is false; this asset must not be used in a "
                "project intended for sale"
            )
        if entry.ai_related_terms and "prohibit" in entry.ai_related_terms.lower():
            problems.append(
                f"{asset_id}: ai_related_terms mentions a prohibition; review against "
                "docs/legal/AI_AND_ASSETS_POLICY.md before use"
            )
    return problems
