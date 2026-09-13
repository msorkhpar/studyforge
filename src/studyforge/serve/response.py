r"""A route's answer as a value, so routes are tested without a socket.

**What it does.** `Response` is what every route returns — a status, its headers,
and either bytes or a span of one file to stream. `Request` is what a route is
given. The helpers build the JSON envelope every API answer carries.

**How you use it.** A route returns `json_response(200, {...})`,
`error(404, "no such unit")`, or `Response(206, headers, file=path, span=(a, b))`.
`app` writes it; nothing else touches the wire.

**Depends on.** `json`, `dataclasses` and `pathlib`.

⛔ **Only messages this package wrote reach `error`.** An exception's text is the
easiest way for an absolute path — personal data (R7) — to reach a response
body, so a caller logs the exception's *type* and answers with a fixed string.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

#: Every JSON answer says which API version it speaks.
API_VERSION = 1
API_ROOT = "/api"
API_PREFIX = f"{API_ROOT}/v{API_VERSION}"

JSON_TYPE = "application/json; charset=utf-8"
TEXT_TYPE = "text/plain; charset=utf-8"

#: What every non-content JSON answer carries: never stored, always re-asked.
NO_STORE = "no-store"

#: Statuses that carry no body and, so, no `Content-Length` (RFC 9110 §8.6).
BODILESS = frozenset({204, 304})


@dataclass(frozen=True, slots=True)
class Request:
    """The parts of a request a route may read: its method, its path, its headers."""

    method: str
    path: str
    headers: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class Response:
    """One answer: bytes in `body`, or the inclusive `span` of `file` to stream."""

    status: int
    headers: tuple[tuple[str, str], ...] = ()
    body: bytes = b""
    file: Path | None = None
    span: tuple[int, int] | None = None

    @property
    def length(self) -> int:
        """Return the number of body bytes this response sends."""
        if self.file is None:
            return len(self.body)
        if self.span is None:
            return 0
        return self.span[1] - self.span[0] + 1

    def header(self, name: str) -> str | None:
        """Return the first value of header `name`, compared case-insensitively."""
        wanted = name.lower()
        return next((value for key, value in self.headers if key.lower() == wanted), None)


def envelope(payload: Mapping[str, object]) -> bytes:
    """Return a JSON answer's bytes, `api` first, one serialisation for every route."""
    text = json.dumps({"api": API_VERSION, **payload}, indent=2, ensure_ascii=False)
    return (text + "\n").encode("utf-8")


def json_response(
    status: int, payload: Mapping[str, object], headers: tuple[tuple[str, str], ...] = ()
) -> Response:
    """Return a JSON answer that is never cached, unless `headers` says otherwise."""
    cached = any(key.lower() == "cache-control" for key, _ in headers)
    cache = () if cached else (("Cache-Control", NO_STORE),)
    return Response(status, (("Content-Type", JSON_TYPE), *cache, *headers), envelope(payload))


def error(status: int, message: str) -> Response:
    """Return a JSON error carrying a message this package wrote."""
    return json_response(status, {"error": message})
