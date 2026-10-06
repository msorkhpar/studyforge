r"""The assets namespace and the static mount: a built site's bytes, unchanged.

**What it does.** Maps a URL path onto one regular file under the served root —
refusing every traversal — and answers it with a weak ETag, `304` on a matching
`If-None-Match`, and `206` / `416` for a `Range`. Text passes the personal-data
gate before it leaves; binary media is streamed.

**How you use it.** `route(root, private, request, rest)` for `/api/v1/assets/`;
`serve(root, request, url_path, private)` for the static mount, which is the same
function — ⛔ **one resolver, never two**, because two are two traversal surfaces.

**Depends on.** `corpus.placement.profile` for the generated directory's name,
`serve.caching`, `serve.response`, `serve.versions` for what a file version was judged
to be, `routes.gated` for answering text (and, through it, `archive.scrub`), and
`serve.withheld` for a quiz's key.

⭐ **A file is read and judged once per version, not once per request.** `serve.app`
hands both mounts one `serve.versions.Versions`, and every verdict below — a quiz's
key, the personal-data gate, a text's gzip coding — is held against the file's
version and reached again only when the file moves (or its quizzes do). ⛔ The rules
themselves are unchanged: what was refused is refused, in the same order.

⭐ **A missing `/favicon.ico` is `204`, not `404`**: a browser asks every origin for
it unprompted, a page names no icon, and a `404` is an error in the reader's
console on every served page.

## ⛔ `resolve` is the whole traversal control, and its order is the control

1. split on `/` **before** decoding, so `%2f` cannot manufacture a separator;
2. decode each segment, then refuse `.`, `..`, a separator, a backslash or a NUL;
3. refuse a dot-prefixed segment — ⭐ **except the build's own generated directory,
   as the first segment or beside a `corpus.json`**, because every page a build
   writes links into it and a blanket dotfile rule would serve a site with no
   stylesheet. ⛔ **Beside a manifest, not "at any depth"**: a
   root holding several corpora puts each one's generated directory one level
   down, and the manifest on disk is what says a corpus is there — no mount list is
   configured, and any other nested dot-directory is still refused;
4. `resolve()` (following symlinks) and require the result inside the root and a
   regular file.

## ⚠️ Text ignores `Range`, and is gzip-coded for a client that accepts it

A range over text would bypass the gate by construction, so gated text is always
answered whole, with `Accept-Ranges: none` — RFC 9110 §14.2 lets a server ignore
`Range`. The extraction source answered `416` there instead, which refuses a range
that was satisfiable. Text too large to gate is refused, never served ungated.

⭐ **`private` is the seam for a file that sits under the root and is not content**
— the reader's own record is the first. It answers `404`, as does every refusal,
so a prober never learns which guess was interesting.

## ⛔ A file carrying a quiz's key or sentence is REFUSED — unless it is a page

⭐ **A quiz's key lives only in the page it grades**, so a page is served whole. ⛔
**Every other file carrying one is refused**: a corpus built into its own root puts the
archive's `practice-M.json` and the bundle's `tests/quiz.json` under the served root, so
`withheld` is asked of every other text — and every file of an unknown type, where an
editor's backup lands — before anything is answered, a `304` included: `404`. ⭐ **The
default withholds nothing**: what a file may not carry is decided by the quizzes an
instance SERVES, and `serve.app` hands both mounts that predicate. ⚠️ Media is not read,
and an unknown-type file over `GATE_MAX_BYTES` is served unread: a compressed archive
holding a bundle cannot be read here at all.

## ⛔ The run client reaches a page ONE way, and this is it

⭐ **The serving process adds the client to the page it answers; a built page
never loads it.** When an instance registers the run namespace it hands this
route the client's path, and an HTML page leaves here with exactly one
`<script src="…" defer></script>` inserted before its first `</head>`. ⛔ **The
file on disk is untouched** — nothing is written, and the same bytes are served
again the next time with no client when the namespace is not registered.

⚠️ **Why this way and no other** (how a served page loads the run
client): every alternative puts the client's address into the BUILD. A
`<script src="/api/…">` is a rooted reference that names the API; a relative
`api/v1/…` resolved against `location.origin` names no origin and still loads
it; a copy of the client in the site names the API on every line. ⭐ Only the
server knows it is a server, so only the server says so — and R8's floor
(`tests/studyforge/cli/serving.py`) reads a built text that names the client as
a defect.

⛔ **A served page carries a DIFFERENT validator from the same file on disk.**
The weak ETag is taken from the file's size and mtime, which do not move when
the client is inserted — so a page cached from a served origin and one cached
from a plain file mount would collide under one ETag. `client_etag` marks the
served form, and the mark is part of the opaque tag rather than a second header.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from urllib.parse import unquote

from studyforge.corpus.manifest import all_link_suffixes
from studyforge.corpus.manifest.document import MANIFEST_FILENAME
from studyforge.corpus.placement.profile import GENERATED_ROOT
from studyforge.progress import store_dir
from studyforge.serve.caching import UNSATISFIABLE, WHOLE, not_modified, parse_range, weak_etag
from studyforge.serve.response import TEXT_TYPE, Request, Response
from studyforge.serve.routes.gated import (  # noqa: F401 - names callers import from here
    ASSET_CACHE,
    GATE_MAX_BYTES,
    SAMPLES,
    Served,
    answer,
)
from studyforge.serve.routes.pagetag import (  # noqa: F401 - names callers import from here
    CLIENT_ETAG_MARK,
    CLIENT_PATH_FORBIDDEN,
    CLIENT_TAG,
    HEAD_CLOSE,
    LIVE_ETAG_MARK,
    client_etag,
    client_tag,
    with_client,
)
from studyforge.serve.versions import UNHELD, Judged, Moved, Versions, build_digest

#: What a browser asks every served origin for, unprompted. ⭐ Answered `204` when
#: the site has none: a `404` is an error in the reader's console on every page,
#: and a page names no icon, so there is nothing a build could fix.
FAVICON = "/favicon.ico"

#: How many times a file rewritten while it is answered is looked at afresh before `503`.
MOVED_ATTEMPTS = 3

#: Longest URL path accepted, before decoding.
MAX_PATH = 1024

#: The file a directory request resolves to.
INDEX_FILENAME = "index.html"

#: The one dot-prefixed name served: first, or where a corpus manifest sits beside it.
EXPOSED_DOT_DIRECTORY = GENERATED_ROOT

#: Content types that are text, and so gated and never ranged.
GATED_TYPES = ("text/", "application/json", "image/svg+xml")

#: By extension, from a fixed table: `mimetypes` reads system files and varies by
#: machine. An unknown extension is opaque bytes, which `nosniff` makes inert.
#: ⭐ A code file of any declarable runtime is TEXT, so a lesson's link to one is
#: a plain view the browser shows rather than a download (a code example's fallback);
#: every entry spelled below wins over that, so `.js` stays a script.
CONTENT_TYPES = {
    **dict.fromkeys(all_link_suffixes(), TEXT_TYPE),
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

#: ⭐ **A source file: the code a lesson links to, served VERBATIM** (plain-text suffixes only;
#: `.js` stays a script). ⛔ Never refused for a sample address or token, or its size; a home path
#: or hostname still is, and `withheld` is still asked.
SOURCE_SUFFIXES_SERVED = frozenset(
    one for one in all_link_suffixes() if CONTENT_TYPES[one] == TEXT_TYPE
)

Private = Callable[[Path], bool]

#: Whether a file's bytes carry what a site never serves.
Withheld = Callable[[bytes], bool]

#: ⭐ The one type `withheld` never reads: a page, where a quiz's key lives.
PAGE_TYPE = CONTENT_TYPES[".html"]

#: ⛔ **The reader's progress record, which is never content**. It sits
#: at `<generated root>/progress/` beside the pages a `tree` profile writes, so the
#: static mount would otherwise serve it. Refused BY PATH, on the resolved file, so
#: a symlink into it is refused too; the state namespace is where the
#: record is served. ⚠️ A hard link to it elsewhere under the root is not seen.
#: ⛔ **Matched ANYWHERE in the resolved absolute path, never relative to the served
#: root**: a root that is a corpus's generated directory, or one holding
#: several corpora, puts a store at a different depth, and no caller has to pass
#: `private=` to keep it unserved.
#: ⭐ **Derived from `progress.store_dir`, the store's one spelling**, so
#: the store cannot move without this refusal moving with it.
PROGRESS_PREFIX = store_dir(".").parts


def nothing_private(path: Path) -> bool:
    """Treat no file under the root as private: the default until a store names one."""
    return False


def nothing_withheld(body: bytes) -> bool:
    """Withhold no file: the default where no instance has named the quizzes it serves."""
    return False


def resolve(root: Path, url_path: str) -> Path | None:
    """Return the regular file under `root` that `url_path` names, or `None`."""
    try:
        base = Path(root).resolve(strict=True)
    except OSError, RuntimeError:
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
        if segment.startswith(".") and not _exposed(base, segments, segment):
            return None
        segments.append(segment)
    target = base.joinpath(*segments)
    if target.is_dir():
        target = target / INDEX_FILENAME
    try:
        real = target.resolve(strict=True)
    except OSError, RuntimeError:
        return None
    if base not in real.parents or not real.is_file():
        return None
    if in_a_progress_store(real):
        return None
    return real


def _exposed(base: Path, above: list[str], segment: str) -> bool:
    """Say whether a dot-prefixed segment is a generated directory the mount serves.

    ⭐ The served root's own, or one whose parent holds a corpus manifest. ⛔ The
    progress store inside it is still refused, on the resolved path, by `resolve`.
    """
    if segment != EXPOSED_DOT_DIRECTORY:
        return False
    return not above or base.joinpath(*above, MANIFEST_FILENAME).is_file()


def in_a_progress_store(path: Path) -> bool:
    """Say whether `PROGRESS_PREFIX` occurs anywhere in a resolved path's parts."""
    parts, width = path.parts, len(PROGRESS_PREFIX)
    return any(parts[i : i + width] == PROGRESS_PREFIX for i in range(len(parts) - width + 1))


def content_type_for(path: Path) -> str:
    """Return the content type served for `path`, from the fixed table."""
    return CONTENT_TYPES.get(path.suffix.lower(), DEFAULT_CONTENT_TYPE)


def route(
    root: Path,
    private: Private,
    request: Request,
    rest: str,
    *,
    client: str | None = None,
    withheld: Withheld = nothing_withheld,
    live: str | None = None,
    memo: Versions = UNHELD,
) -> Response:
    """Answer one request under `/api/v1/assets/`; `rest` is the path after it."""
    return serve(root, request, "/" + rest, private, client, withheld, live, memo)


def serve(
    root: Path,
    request: Request,
    url_path: str,
    private: Private = nothing_private,
    client: str | None = None,
    withheld: Withheld = nothing_withheld,
    live: str | None = None,
    memo: Versions = UNHELD,
) -> Response:
    """Answer one file: `200`, `206`, `304`, `404` or `416`.

    ⭐ `client` is where the run namespace serves the page's execution client,
    and `None` is an instance that registers no such namespace. ⛔ It reaches an
    HTML page's BYTES and never the file on disk — see this module's docstring.
    ⭐ `memo` holds what a file version was judged to be (`serve.versions`); the
    default holds nothing, so every request judges.
    """
    target = resolve(root, url_path)
    if target is None and url_path == FAVICON:
        return Response(204, ())
    if target is None or private(target):
        return _not_found()
    for _ in range(MOVED_ATTEMPTS):
        try:
            return _answer(
                Judged(target, target.stat(), memo), root, request, withheld, client, live
            )
        except Moved:
            continue
        except OSError:
            return _not_found()
    return Response(503, (("Content-Type", TEXT_TYPE),), b"the file is changing; ask again\n")


def _answer(
    judged: Judged,
    root: Path,
    request: Request,
    withheld: Withheld,
    client: str | None,
    live: str | None,
) -> Response:
    """Answer one resolved file at the version `judged` names; `Moved` if it is rewritten."""
    target, stat = judged.path, judged.stat
    ctype = content_type_for(target)
    gated = ctype.startswith(GATED_TYPES) or ctype == DEFAULT_CONTENT_TYPE
    readable = gated and stat.st_size <= GATE_MAX_BYTES
    if readable and ctype != PAGE_TYPE and _withholds(judged, withheld):
        return _not_found()
    plain = weak_etag(stat, build_digest(Path(root).resolve(), target, judged.memo))
    added = client if client and ctype == PAGE_TYPE else None
    etag = client_etag(plain, bool(live)) if added else plain
    if ctype.startswith(GATED_TYPES):
        source = target.suffix.lower() in SOURCE_SUFFIXES_SERVED
        return answer(judged, request, ctype, etag, Served(added, live, source, GATE_MAX_BYTES))
    validators = (("ETag", etag), ("Cache-Control", ASSET_CACHE))
    if not_modified(request.headers.get("If-None-Match"), etag):
        return Response(304, validators)
    ranges = request.headers.get("Range") if request.headers.get("If-Range") is None else None
    span = parse_range(ranges, stat.st_size)
    if span == UNSATISFIABLE:
        headers = (("Content-Range", f"bytes */{stat.st_size}"), ("Accept-Ranges", "bytes"))
        return Response(416, (("Content-Type", TEXT_TYPE), *headers), b"range not satisfiable\n")
    headers = (("Content-Type", ctype), *validators, ("Accept-Ranges", "bytes"))
    held = judged.version
    if span == WHOLE:
        whole = (0, stat.st_size - 1) if stat.st_size else None
        return Response(200, headers, file=target, span=whole, version=held)
    first, last = span
    ranged = (*headers, ("Content-Range", f"bytes {first}-{last}/{stat.st_size}"))
    return Response(206, ranged, file=target, span=span, version=held)


def _withholds(judged: Judged, withheld: Withheld) -> bool:
    """Ask `withheld` of a file's bytes, once per version and set of marks where it says them."""
    marks = getattr(withheld, "marks", None)
    if marks is None:
        return withheld(judged.bytes())
    now = marks()
    return judged.verdict("withheld", lambda: withheld(judged.bytes(), now), against=now)


def _not_found() -> Response:
    """Return the one `404` every refusal shares."""
    return Response(404, (("Content-Type", TEXT_TYPE),), b"not found\n")
