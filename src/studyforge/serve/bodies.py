"""A `POST` body, read to a limit: what `serve.app` hands a route, or drops.

**What it does.** `read(headers, stream, limit)` reads the `Content-Length` bytes a request
declared and returns them, or `None` when the length is not a non-negative number or is over
`limit`. ⛔ Nothing is read past the declared length and nothing is interpreted.

**How you use it.** `serve.app` calls it with `MAX_BODY` for a path registered in `bodies` (the
live run's, whose key can arrive no other way) and with `MAX_DISCARDED` for every other `POST`,
where the bytes are drained so the answer is not lost to a reset, and dropped.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import BinaryIO


def read(headers: Mapping[str, str], stream: BinaryIO, limit: int) -> bytes | None:
    """Return the declared body, `b""` for none, or `None` for a length that is bad or too large."""
    try:
        length = int(headers.get("Content-Length") or 0)
    except ValueError:
        return None
    if length < 0 or length > limit:
        return None
    return stream.read(length) if length else b""
