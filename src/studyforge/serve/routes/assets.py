r"""The assets namespace and the static mount: a built site's bytes, unchanged.

**What it does.** Maps a URL path onto one regular file under the served root —
refusing every traversal — and answers it with a weak ETag, `304` on a matching
`If-None-Match`, and `206` / `416` for a `Range`. Text passes the personal-data
gate before it leaves; binary media is streamed.

**How you use it.** `route(root, private, request, rest)` for `/api/v1/assets/`;
`serve(root, request, url_path, private)` for the static mount, which is the same
function — ⛔ **one resolver, never two**, because two are two traversal surfaces.

**Depends on.** `archive.scrub`, `corpus.placement.profile` for the generated
directory's name, `serve.caching`, `serve.response`.

## ⛔ `resolve` is the whole traversal control, and its order is the control

1. split on `/` **before** decoding, so `%2f` cannot manufacture a separator;
2. decode each segment, then refuse `.`, `..`, a separator, a backslash or a NUL;
3. refuse a dot-prefixed segment — ⭐ **except the build's own generated directory
   as the first segment**, because every page a build writes links into it and a
   blanket dotfile rule would serve a site with no stylesheet;
4. `resolve()` (following symlinks) and require the result inside the root and a
   regular file.

## ⚠️ Text ignores `Range`

A range over text would bypass the gate by construction, so gated text is always
answered whole, with `Accept-Ranges: none` — RFC 9110 §14.2 lets a server ignore
`Range`. The extraction source answered `416` there instead, which refuses a range
that was satisfiable. Text too large to gate is refused, never served ungated.

⭐ **`private` is the seam for a file that sits under the root and is not content**
— the reader's own record is the first. It answers `404`, as does every refusal,
so a prober never learns which guess was interesting.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from urllib.parse import unquote

from studyforge.archive.scrub import PersonalDataLeak, assert_clean
from studyforge.corpus.placement.profile import GENERATED_ROOT
from studyforge.serve.caching import UNSATISFIABLE, WHOLE, not_modified, parse_range, weak_etag
from studyforge.serve.response import TEXT_TYPE, Request, Response

#: Assets revalidate every time; a `304` costs one `stat`.
ASSET_CACHE = "no-cache"

#: Longest URL path accepted, before decoding.
MAX_PATH = 1024

#: The file a directory request resolves to.
INDEX_FILENAME = "index.html"

#: The one dot-prefixed name served, and only as the first segment.
EXPOSED_DOT_DIRECTORY = GENERATED_ROOT

#: Largest text the gate reads. ⛔ Above it a file is refused, not served ungated.
GATE_MAX_BYTES = 4 * 1024 * 1024

#: Content types that are text, and so gated and never ranged.
GATED_TYPES = ("text/", "application/json", "image/svg+xml")

#: By extension, from a fixed table: `mimetypes` reads system files and varies by
#: machine. An unknown extension is opaque bytes, which `nosniff` makes inert.
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".md": TEXT_TYPE,
    ".txt": TEXT_TYPE,
    ".vtt": "text/vtt; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".woff2": "font/woff2",
}
DEFAULT_CONTENT_TYPE = "application/octet-stream"

Private = Callable[[Path], bool]


def nothing_private(path: Path) -> bool:
    """Treat no file under the root as private: the default until a store names one."""
    return False


def resolve(root: Path, url_path: str) -> Path | None:
    """Return the regular file under `root` that `url_path` names, or `None`."""
    try:
        base = Path(root).resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if not url_path.startswith("/") or len(url_path) > MAX_PATH or "\x00" in url_path:
        return None
    segments = []
    for raw in url_path.split("/")[1:]:
        if not raw:
            continue
        try:
            segment = unquote(raw, encoding="utf-8", errors="strict")
        except UnicodeDecodeError:
            return None
        if segment in (".", "..") or any(c in segment for c in "/\\\x00"):
            return None
        if segment.startswith(".") and not (not segments and segment == EXPOSED_DOT_DIRECTORY):
            return None
        segments.append(segment)
    target = base.joinpath(*segments)
    if target.is_dir():
        target = target / INDEX_FILENAME
    try:
        real = target.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if base not in real.parents or not real.is_file():
        return None
    return real


def content_type_for(path: Path) -> str:
    """Return the content type served for `path`, from the fixed table."""
    return CONTENT_TYPES.get(path.suffix.lower(), DEFAULT_CONTENT_TYPE)


def route(root: Path, private: Private, request: Request, rest: str) -> Response:
    """Answer one request under `/api/v1/assets/`; `rest` is the path after it."""
    return serve(root, request, "/" + rest, private)


def serve(
    root: Path, request: Request, url_path: str, private: Private = nothing_private
) -> Response:
    """Answer one file: `200`, `206`, `304`, `404` or `416`."""
    target = resolve(root, url_path)
    if target is None or private(target):
        return _not_found()
    try:
        stat = target.stat()
    except OSError:
        return _not_found()
    etag = weak_etag(stat)
    validators = (("ETag", etag), ("Cache-Control", ASSET_CACHE))
    if not_modified(request.headers.get("If-None-Match"), etag):
        return Response(304, validators)
    ctype = content_type_for(target)
    if ctype.startswith(GATED_TYPES):
        return _text(target, stat.st_size, ctype, validators)
    ranges = request.headers.get("Range") if request.headers.get("If-Range") is None else None
    span = parse_range(ranges, stat.st_size)
    if span == UNSATISFIABLE:
        headers = (("Content-Range", f"bytes */{stat.st_size}"), ("Accept-Ranges", "bytes"))
        return Response(416, (("Content-Type", TEXT_TYPE), *headers), b"range not satisfiable\n")
    headers = (("Content-Type", ctype), *validators, ("Accept-Ranges", "bytes"))
    if span == WHOLE:
        whole = (0, stat.st_size - 1) if stat.st_size else None
        return Response(200, headers, file=target, span=whole)
    first, last = span
    ranged = (*headers, ("Content-Range", f"bytes {first}-{last}/{stat.st_size}"))
    return Response(206, ranged, file=target, span=span)


def _text(target: Path, size: int, ctype: str, validators: tuple) -> Response:
    """Read a text file whole, gate it, and answer it whole."""
    if size > GATE_MAX_BYTES:
        return Response(500, (("Content-Type", TEXT_TYPE),), b"text too large to gate\n")
    try:
        body = target.read_bytes()
    except OSError:
        return _not_found()
    try:
        assert_clean(body.decode("utf-8", errors="replace"), "asset")
    except PersonalDataLeak:
        return Response(500, (("Content-Type", TEXT_TYPE),), b"asset failed the gate\n")
    headers = (("Content-Type", ctype), *validators, ("Accept-Ranges", "none"))
    return Response(200, headers, body)


def _not_found() -> Response:
    """Return the one `404` every refusal shares."""
    return Response(404, (("Content-Type", TEXT_TYPE),), b"not found\n")
