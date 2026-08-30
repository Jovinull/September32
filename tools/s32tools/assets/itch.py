"""A minimal client for itch.io's public free-download flow.

Scope, stated plainly because it matters: this uses exactly the endpoints a
browser uses when a visitor clicks **Download Now** and then **"No thanks, just
take me to the downloads"** on a free or pay-what-you-want page. It does not log
in, does not hold an account session, does not solve a CAPTCHA, does not touch
paid files, and does not use a mirror. If a pack ever requires a purchase or a
signed-in session, this client fails and the fetcher records a
``MANUAL DOWNLOAD REQUIRED`` block instead -- see ``docs/legal/ASSET_LICENSING.md``.

The flow is three requests:

1. ``GET  <game_url>/purchase``          -- to obtain a CSRF token.
2. ``POST <game_url>/download_url``      -- returns the download-page URL.
3. ``POST <game_url>/file/<upload_id>``  -- returns a signed, short-lived URL.

Upload ids come from the download page, which lists only the files the visitor
is entitled to.
"""

from __future__ import annotations

import http.cookiejar
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

#: Identify the tool honestly rather than impersonating a browser.
USER_AGENT = "september32-asset-tool/0.1 (+local development tooling; contact via project repo)"

_CSRF_RE = re.compile(r'csrf_token"\s+value="([^"]+)"')
_UPLOAD_RE = re.compile(
    r'data-upload_id="(?P<uid>\d+)".*?title="(?P<name>[^"]+)"', re.DOTALL
)

#: HTTP statuses worth retrying. itch.io returns 429 under load and, less
#: predictably, 404 for a request that arrives too fast after the previous one.
_RETRYABLE = frozenset({403, 404, 429, 500, 502, 503, 504})


class ItchError(RuntimeError):
    """The itch.io flow could not be completed without manual intervention."""


@dataclass(frozen=True, slots=True)
class Upload:
    """One downloadable file listed on a download page."""

    upload_id: str
    filename: str


class ItchClient:
    """Stateful only in the sense that it keeps a cookie jar for one session."""

    def __init__(self, *, timeout: int = 120, delay: float = 2.0, retries: int = 4) -> None:
        self._jar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._jar),
            urllib.request.HTTPRedirectHandler(),
        )
        self._opener.addheaders = [("User-Agent", USER_AGENT)]
        self._timeout = timeout
        self._delay = delay
        self._retries = retries

    def _open(self, request: urllib.request.Request | str) -> str:
        """Perform a request, backing off politely on rate limiting.

        itch.io answers a burst of requests with 429 and, occasionally, 404.
        Hammering it would be both rude and counter-productive, so every call
        goes through here: a fixed pause before each request, and exponential
        backoff on a throttling response.
        """
        last: Exception | None = None
        for attempt in range(self._retries):
            time.sleep(self._delay * (2**attempt) if attempt else self._delay)
            try:
                with self._opener.open(request, timeout=self._timeout) as response:
                    body: bytes = response.read()
                    return body.decode("utf-8", errors="replace")
            except urllib.error.HTTPError as exc:
                last = exc
                if exc.code not in _RETRYABLE:
                    raise
            except urllib.error.URLError as exc:
                last = exc
        raise ItchError(f"gave up after {self._retries} attempts: {last}")

    def _get(self, url: str) -> str:
        return self._open(url)

    def _post(self, url: str, fields: dict[str, str]) -> str:
        payload = urllib.parse.urlencode(fields).encode()
        request = urllib.request.Request(url, data=payload, method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        return self._open(request)

    def csrf_token(self, game_url: str) -> str:
        """Fetch a CSRF token from the game's purchase page."""
        html = self._get(f"{game_url.rstrip('/')}/purchase")
        match = _CSRF_RE.search(html)
        if match is None:
            raise ItchError(
                f"no CSRF token on {game_url}/purchase; the page layout may have changed, "
                "or this pack may not offer a free download"
            )
        return match.group(1)

    def download_page(self, game_url: str, token: str) -> str:
        """Follow the 'no thanks' path and return the download-page URL."""
        raw = self._post(f"{game_url.rstrip('/')}/download_url", {"csrf_token": token})
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ItchError(f"unexpected response from download_url for {game_url}") from exc
        if "url" not in payload:
            errors = payload.get("errors") or ["unknown error"]
            raise ItchError(f"itch.io refused the free download for {game_url}: {errors}")
        # Returned already percent-encoded, and it must stay that way: some
        # tokens contain an encoded '/', which decoding would turn into an extra
        # path segment and a 404.
        return str(payload["url"])

    def list_uploads(self, download_page_url: str) -> list[Upload]:
        """Return the files the download page offers."""
        html = self._get(download_page_url)
        uploads = [
            Upload(upload_id=m.group("uid"), filename=m.group("name"))
            for m in _UPLOAD_RE.finditer(html)
        ]
        if not uploads:
            raise ItchError(f"no downloadable files listed at {download_page_url}")
        return uploads

    def signed_url(self, game_url: str, upload_id: str, token: str) -> str:
        """Return a short-lived signed URL for one upload."""
        raw = self._post(
            f"{game_url.rstrip('/')}/file/{upload_id}",
            {"csrf_token": token, "source": "game_download"},
        )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ItchError(f"unexpected response requesting upload {upload_id}") from exc
        if "url" not in payload:
            raise ItchError(f"itch.io refused upload {upload_id}: {payload.get('errors')}")
        return str(payload["url"])

    def fetch(self, game_url: str, filename: str, destination: Path) -> Path:
        """Download one named file from a free itch.io page.

        Args:
            game_url: The pack's page URL.
            filename: Exact file name as listed on the download page.
            destination: Directory to write into.

        Returns:
            The path written.

        Raises:
            ItchError: If the file is not offered for free download.
        """
        token = self.csrf_token(game_url)
        page = self.download_page(game_url, token)
        uploads = self.list_uploads(page)

        match = next((u for u in uploads if u.filename == filename), None)
        if match is None:
            available = ", ".join(u.filename for u in uploads)
            raise ItchError(
                f"{filename!r} is not among the free downloads for {game_url}. "
                f"Available: {available}"
            )

        url = self.signed_url(game_url, match.upload_id, token)
        destination.mkdir(parents=True, exist_ok=True)
        target = destination / filename
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=self._timeout) as response, target.open("wb") as handle:  # noqa: S310
            while chunk := response.read(1 << 20):
                handle.write(chunk)
        return target
