r"""Validators and byte ranges: what lets a response revalidate instead of re-download.

**What it does.** Mints the two validators the serving API sends — a **strong**
ETag over a content document's bytes and a **weak** ETag over an asset's size and
modification time — answers the `304` question for `If-None-Match`, and reads a
single `Range` header against a file's length.

**How you use it.** `strong_etag(body)` and `weak_etag(stat, build)`;
`not_modified(header, etag)`; `parse_range(header, size)` returns `WHOLE`,
`UNSATISFIABLE`, or an inclusive `(first, last)` pair. `accepts_gzip(header)` reads
`Accept-Encoding`, `gzip_etag(etag)` tells a compressed representation's validator
from the identity one's, and `gzipped(body)` is the one compressor.

**Depends on.** `gzip`, `hashlib` and `os`. No request, no response, no disk.

⭐ **An asset's weak validator folds in the build's own digest** where a build recorded
one (`serve.versions.build_digest`): a rebuild that leaves a file's size and times alone
still moves it. A root no build recorded keeps `W/"<size>-<mtime>"`.

⭐ **A compressed answer is its own representation** (RFC 9110 §8.4): it carries
`gzip_etag`'s mark inside the opaque tag, and `Vary: Accept-Encoding` is sent beside it.
⛔ `gzipped` writes no timestamp, so one file's compressed bytes are the same every time.

## ⭐ Why the two namespaces get different validators

Content is reproducible: one corpus builds the same bytes on every machine, so its
validator is a hash two machines agree on, and it is strong. An asset's validator
is its local `stat` — cheap on a large file, meaningless on another machine — so it
is weak and says so. ⛔ A weak validator never satisfies `If-Range` (RFC 9110
§13.1.4), which is why `routes.assets` ignores `Range` whenever `If-Range` is sent.

## ⚠️ The range rulings (RFC 9110 §14)

- **One range only.** A multi-range header is answered with the whole file, which
  is legal and all an `<audio>` element ever needs.
- **An unknown unit is ignored** (§14.2) and answered with the whole file.
- **A malformed `bytes=` spec is refused** as `UNSATISFIABLE`, which §14.2 permits.
- ⭐ **Any range over an empty file is unsatisfiable**, `bytes=-N` included, and so
  is `bytes=-0` (§14.1.2). The extraction source served the whole file there; this
  is the RFC's answer instead, a deliberate difference from the extraction source.
"""

from __future__ import annotations

import gzip
import hashlib
import os

#: `parse_range`'s answer when the whole representation is to be sent.
WHOLE = "whole"

#: `parse_range`'s answer when the request must be refused with `416`.
UNSATISFIABLE = "unsatisfiable"

#: The range unit this server understands.
BYTES = "bytes"


def strong_etag(body: bytes) -> str:
    """Return a quoted content hash: the same bytes give the same tag everywhere.

    ⛔ The whole digest, never a slice: exactly one framework module may truncate a
    digest into a short name (`narrate.speakable.naming`), and a validator is not a name.
    """
    return f'"{hashlib.sha256(body).hexdigest()}"'


#: The content coding offered for text, and the mark its validator carries.
GZIP = "gzip"
GZIP_ETAG_MARK = "+gzip"


def weak_etag(stat: os.stat_result, build: str | None = None) -> str:
    """Return `W/"<size>-<mtime>"`, a local validator marked weak because it is not content.

    ⭐ `build` is the build's own digest, folded in after the times where there is one.
    """
    tail = f"-{build}" if build else ""
    return f'W/"{stat.st_size:x}-{stat.st_mtime_ns:x}{tail}"'


def accepts_gzip(header: str | None) -> bool:
    """Say whether `Accept-Encoding` admits gzip: named, or `*`, with a non-zero weight."""
    weights: dict[str, float] = {}
    for item in (header or "").split(","):
        coding, _, params = item.strip().partition(";")
        weight = 1.0
        for param in params.split(";"):
            name, _, value = param.strip().partition("=")
            if name.strip().lower() == "q":
                try:
                    weight = float(value)
                except ValueError:
                    weight = 0.0
        weights[coding.strip().lower()] = weight
    for coding in (GZIP, "x-" + GZIP, "*"):
        if coding in weights:
            return weights[coding] > 0
    return False


def gzip_etag(etag: str) -> str:
    """Return the validator of the gzip-coded representation of the one `etag` names."""
    return f'{etag[:-1]}{GZIP_ETAG_MARK}"' if etag.endswith('"') else etag + GZIP_ETAG_MARK


def gzipped(body: bytes) -> bytes:
    """Return `body` gzip-coded, with no timestamp, so the same bytes code the same way."""
    return gzip.compress(body, compresslevel=6, mtime=0)


def not_modified(header: str | None, etag: str) -> bool:
    """Say whether `If-None-Match` names `etag`, by the weak comparison §13.1.2 requires."""
    if not header:
        return False
    if header.strip() == "*":
        return True
    wanted = _opaque(etag)
    return any(_opaque(candidate.strip()) == wanted for candidate in header.split(","))


def parse_range(header: str | None, size: int) -> str | tuple[int, int]:
    """Return `WHOLE`, `UNSATISFIABLE`, or the inclusive `(first, last)` byte pair."""
    if header is None:
        return WHOLE
    unit, equals, spec = header.strip().partition("=")
    if not equals or unit.strip().lower() != BYTES:
        return WHOLE
    spec = spec.strip()
    if "," in spec:
        return WHOLE
    first, dash, last = (part.strip() for part in spec.partition("-"))
    if not dash or not (first or last) or not (_digits(first) and _digits(last)):
        return UNSATISFIABLE
    if not first:
        length = int(last)
        if length == 0 or size == 0:
            return UNSATISFIABLE
        return max(0, size - length), size - 1
    start = int(first)
    end = size - 1 if not last else int(last)
    if end < start or start >= size:
        return UNSATISFIABLE
    return start, min(end, size - 1)


def _opaque(tag: str) -> str:
    """Return a tag without its weakness marker, for the weak comparison."""
    return tag[2:] if tag.startswith("W/") else tag


def _digits(text: str) -> bool:
    """Say whether `text` is empty or ASCII digits — `int()` also accepts `²` and `٣`."""
    return not text or (text.isascii() and text.isdigit())
