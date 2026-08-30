"""Structured developer logging.

Two hard rules:

* Release builds log almost nothing. Internal state is not the player's, and a
  debug line leaking into a shipped build is both a spoiler and a bug report
  nobody can read.
* Nothing is ever sent anywhere. This is a single-player offline game with no
  telemetry (see ``docs/legal/PRIVACY.md``). ``devlog`` writes to stdout and,
  optionally, to a local file the developer opted into.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable
from typing import TextIO

#: Global switch. Ren'Py sets this from ``config.developer`` at init time; the
#: headless tooling sets it from ``--verbose``.
enabled: bool = False

#: Channel names currently muted, so a developer chasing one system is not
#: drowned by the others.
_muted: set[str] = set()

_stream: TextIO = sys.stdout


def configure(*, active: bool, stream: TextIO | None = None, mute: Iterable[str] = ()) -> None:
    """Configure logging for the current process."""
    global enabled, _stream  # noqa: PLW0603 - one process-wide switch, by design
    enabled = active
    if stream is not None:
        _stream = stream
    _muted.clear()
    _muted.update(mute)


def log(channel: str, message: str) -> None:
    """Emit one line on a named channel, if logging is on and it is not muted."""
    if not enabled or channel in _muted:
        return
    print(f"[S32:{channel.upper()}] {message}", file=_stream)


def block(channel: str, title: str, lines: Iterable[str]) -> None:
    """Emit a titled, indented multi-line block."""
    if not enabled or channel in _muted:
        return
    print(f"[S32:{channel.upper()}] {title}", file=_stream)
    for line in lines:
        print(f"    {line}", file=_stream)
