r"""Gated text, answered: judged once per file version, then sent whole, streamed or gzip-coded.

**What it does.** `answer` takes one text file the assets route resolved — a page, a
script, a stylesheet, a source file — and answers it: `304` on a matching validator,
`500` when its served bytes fail the personal-data gate or are too large to gate, and
otherwise `200` with the identity bytes or, when the client accepts it, their gzip
coding. Split from `routes.assets` (R11), whose contract this module keeps.

**How you use it.** `answer(judged, request, ctype, etag, Served(client, live, source))`,
where `judged` is a `serve.versions.Judged` over the resolved file and `etag` the
identity validator `routes.assets` composed.

**Depends on.** `archive.scrub` for the gate, `serve.caching` for validators and the
coding, `serve.response`, `serve.versions`, and `routes.pagetag` for a page's tags.

## ⭐ What is judged, and when

⛔ **The gate runs over what LEAVES this process** — a page with its client tag inserted —
exactly as before; what moved is how often. `Judged.verdict` holds a verdict against the
file's version, so a settled 3 MB index is read and gated once, and every later request is
a `stat` and a stream. ⭐ The compressed bytes are held the same way, coded from the bytes
the gate passed.

⭐ **A streamed answer carries its version**: `serve.app` opens the file, compares, and
refuses to send bytes from a version nobody judged. An answer whose bytes this request
already read is sent from those bytes.

⚠️ **Text still ignores `Range`** (`Accept-Ranges: none`), so a compressed answer never
meets a range; a source file too large to read is still streamed unread, and any other
text that large is still refused.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from studyforge.archive.scrub import PersonalDataLeak, assert_clean
from studyforge.serve.caching import GZIP, accepts_gzip, gzip_etag, gzipped, not_modified
from studyforge.serve.response import TEXT_TYPE, Request, Response
from studyforge.serve.routes.pagetag import with_client
from studyforge.serve.versions import Judged

#: Assets revalidate every time; a `304` costs one `stat` and a held verdict.
ASSET_CACHE = "no-cache"

#: Largest text the gate reads. ⛔ Above it a file is refused, not served ungated.
GATE_MAX_BYTES = 4 * 1024 * 1024

#: Smallest body worth coding: below it, the coding's own framing outweighs the saving.
MIN_GZIP_BYTES = 1024

#: ⭐ Sample data a source file may carry: never refused for a sample address or token, while
#: a home path or hostname still is.
SAMPLES = re.compile(r"\b[\w.%+\-]+@[\w.\-]+\.[A-Za-z]{2,}\b|\bBearer\s+[\w.\-]{8,}")

#: The header a text answer varies on, since its coding follows `Accept-Encoding`.
VARY = ("Vary", "Accept-Encoding")


@dataclass(frozen=True)
class Served:
    """What a text's served form depends on: the tags a page gains, and whether it is source."""

    client: str | None = None
    live: str | None = None
    source: bool = False
    limit: int = GATE_MAX_BYTES


def answer(judged: Judged, request: Request, ctype: str, etag: str, served: Served) -> Response:
    """Answer one gated text file: `200`, `304` or `500`."""
    size = judged.stat.st_size
    coded = size >= MIN_GZIP_BYTES and accepts_gzip(request.headers.get("Accept-Encoding"))
    tag = gzip_etag(etag) if coded else etag
    validators = (("ETag", tag), ("Cache-Control", ASSET_CACHE), VARY)
    if not_modified(request.headers.get("If-None-Match"), tag):
        return Response(304, validators)
    headers = (("Content-Type", ctype), *validators, ("Accept-Ranges", "none"))
    if size > served.limit:
        if not served.source:
            return _refused(b"text too large to gate\n")
        return _streamed(judged, headers)
    shape = (served.client, served.live, served.source)
    if not judged.verdict(("gate", shape), lambda: _clean(_bytes(judged, served), served)):
        return _refused(b"asset failed the gate\n")
    if coded:
        body = judged.verdict(("gzip", shape), lambda: gzipped(_bytes(judged, served)))
        return Response(200, (*headers, ("Content-Encoding", GZIP)), body)
    if served.client or judged.read:
        return Response(200, headers, _bytes(judged, served))
    return _streamed(judged, headers)


def _bytes(judged: Judged, served: Served) -> bytes:
    """Return the bytes that leave: a page with its tags, anything else as it is on disk."""
    return with_client(judged.bytes(), served.client, served.live)


def _clean(body: bytes, served: Served) -> bool:
    """Say whether `body` passes the personal-data gate; a source's sample data is set aside."""
    text = body.decode("utf-8", errors="replace")
    if served.source:
        text = SAMPLES.sub("", text)
    try:
        assert_clean(text, "asset")
    except PersonalDataLeak:
        return False
    return True


def _streamed(judged: Judged, headers: tuple) -> Response:
    """Stream the file at the version it was judged at."""
    size = judged.stat.st_size
    span = (0, size - 1) if size else None
    return Response(200, headers, file=judged.path, span=span, version=judged.version)


def _refused(message: bytes) -> Response:
    """Return the fixed `500` a text that cannot be served gets."""
    return Response(500, (("Content-Type", TEXT_TYPE),), message)
