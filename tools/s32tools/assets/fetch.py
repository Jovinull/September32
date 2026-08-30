"""Downloading third-party assets from their official sources.

Nothing here bypasses anything. If a pack needs a login, a purchase or a CAPTCHA,
the fetcher stops and emits a ``MANUAL DOWNLOAD REQUIRED`` block precise enough
to follow without guessing, then carries on with the next pack. A failed
download must never take the rest of the pipeline with it.

Everything downloaded lands in ``assets/.downloads/`` (gitignored) and is
SHA-256 hashed. The hash goes into the manifest, which is committed, so the
repository records exactly which bytes were reviewed even though it does not
contain them.
"""

from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from s32tools.assets.itch import ItchClient, ItchError
from s32tools.assets.sources import Source

USER_AGENT = "september32-asset-tool/0.1 (+local development tooling)"


@dataclass(slots=True)
class FetchResult:
    """The outcome of one attempted download."""

    source_id: str
    status: str
    path: Path | None = None
    sha256: str = ""
    size_bytes: int = 0
    message: str = ""
    manual_instructions: str = ""

    @property
    def ok(self) -> bool:
        """Return whether the file is now on disk."""
        return self.status in {"downloaded", "cached"}


def sha256_of(path: Path) -> str:
    """Return the SHA-256 of a file, streamed."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_source(source: Source, downloads: Path, *, force: bool = False) -> FetchResult:
    """Fetch one source, or explain precisely why it could not be fetched."""
    downloads.mkdir(parents=True, exist_ok=True)

    if source.method == "manual":
        return FetchResult(
            source.id,
            "manual",
            message="this pack must be obtained by hand",
            manual_instructions=manual_block(source),
        )

    existing = _cached(source, downloads)
    if existing is not None and not force:
        return FetchResult(
            source.id,
            "cached",
            path=existing,
            sha256=sha256_of(existing),
            size_bytes=existing.stat().st_size,
            message=f"already present at {existing.name}",
        )

    try:
        if source.method == "direct":
            path = _fetch_direct(source, downloads)
        else:
            path = _fetch_itch(source, downloads)
    except (ItchError, urllib.error.URLError, OSError) as exc:
        return FetchResult(
            source.id,
            "blocked",
            message=f"{type(exc).__name__}: {exc}",
            manual_instructions=manual_block(source),
        )

    return FetchResult(
        source.id,
        "downloaded",
        path=path,
        sha256=sha256_of(path),
        size_bytes=path.stat().st_size,
        message=f"downloaded {path.name}",
    )


def _cached(source: Source, downloads: Path) -> Path | None:
    """Return an already-downloaded archive for this source, if any."""
    directory = downloads / source.id
    if not directory.is_dir():
        return None
    archives = sorted(p for p in directory.iterdir() if p.suffix.lower() == ".zip")
    return archives[0] if archives else None


def _fetch_direct(source: Source, downloads: Path) -> Path:
    """Download a plain HTTPS URL from an official project or creator site."""
    target = downloads / source.id
    target.mkdir(parents=True, exist_ok=True)
    filename = source.target.rsplit("/", 1)[-1]
    path = target / filename

    request = urllib.request.Request(source.target, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response, path.open("wb") as handle:  # noqa: S310
        while chunk := response.read(1 << 20):
            handle.write(chunk)
    return path


def _fetch_itch(source: Source, downloads: Path) -> Path:
    """Download a free itch.io file through the public no-payment path."""
    client = ItchClient()
    target = downloads / source.id

    filename = source.target
    if not filename:
        # The source did not pin a file name; resolve the smallest 1080p WebP
        # archive on offer, which is the variant policy in sources.py.
        token = client.csrf_token(source.page)
        page = client.download_page(source.page, token)
        uploads = client.list_uploads(page)
        preferred = [
            u.filename
            for u in uploads
            if "1080" in u.filename and u.filename.lower().endswith(".zip")
            and "webp" in u.filename.lower()
        ]
        if not preferred:
            preferred = [u.filename for u in uploads if u.filename.lower().endswith(".zip")]
        if not preferred:
            raise ItchError(f"no zip archive offered at {source.page}")
        filename = sorted(preferred)[0]

    return client.fetch(source.page, filename, target)


def manual_block(source: Source) -> str:
    """Return copy-pasteable instructions for a download that must be done by hand."""
    lines = [
        "MANUAL DOWNLOAD REQUIRED",
        "",
        f"  asset id     : {source.id}",
        f"  page         : {source.page}",
        f"  file to pick : {source.target or '(the 1080p WebP archive)'}",
        f"  save to      : assets/.downloads/{source.id}/",
        "",
        "  Then carry on exactly as if it had been fetched:",
        "      s32 assets install     extracts it, records its SHA-256, and",
        "                             copies the result into the game",
        "      s32 assets images      regenerates the Ren'Py image definitions",
        "      s32 doctor             confirms the result",
        "",
        "  The game runs without this pack; every missing image becomes a",
        "  labelled MISSING ASSET placeholder until it is installed.",
        "",
        "  Do NOT commit the archive or anything extracted from it unless the",
        "  entry's redistribution_allowed is true. It almost certainly is not.",
    ]
    if source.manual_steps:
        lines += ["", "  Extra steps:", *[f"      - {s}" for s in source.manual_steps]]
    return "\n".join(lines)
