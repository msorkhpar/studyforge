"""Shared by the `serve` verb's tests: a fixture the verb built, the verb on a thread, R8's floor.

⭐ Every site here is written by `studyforge build` itself, through the dispatcher,
into a directory the harness mints — never by a helper that could build a site the
command would not.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import re
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from studyforge.cli import main as dispatch
from studyforge.cli.serve import main as serve_main
from studyforge.generate import write_site
from studyforge.generate.declarations import read_corpus
from studyforge.serve.app import DEFAULT_PORT, ServingServer
from studyforge.serve.response import API_ROOT
from studyforge.serve.routes.run import CLIENT, CLIENT_FILE, CLIENT_PATH, NAMESPACE
from studyforge.validate.report import OK
from tests.fixture_checks import FIXTURES

#: Both fixture corpora.
NAMES = ("depth1", "depth2")

#: The line a serving PROCESS prints once it listens, naming the port it chose. ⛔ One home
#: the verb's process test and the `buildserve` skill's both import it from here.
LISTENING = re.compile(r"^serve http://127\.0\.0\.1:(\d+)/")


class Address:
    """What `fetch` reads off a server, for a server that lives in another process."""

    def __init__(self, port: int) -> None:
        self.server_address = ("127.0.0.1", port)


#: A reference to the serving origin: the API root as a ROOTED path (a host-qualified
#: third-party `…/api/…` is not one), a loopback host, or the default port.
SERVING_ORIGIN = re.compile(
    rf"(?<![\w.\-]){re.escape(API_ROOT)}(?![\w\-])"
    r"|\b127\.0\.0\.1\b|\blocalhost\b|\[::1\]"
    rf"|:{DEFAULT_PORT}\b"
)

#: ⛔ The run client, by its served path's tail or by its file's name. ⭐ **The one
#: sanctioned way a page gets it is the SERVING PROCESS adding it to the page it answers**
#: (the run route's contract), so a BUILT text that names it is loading it some other way — and a
#: relative `api/v1/…` resolved against `location.origin` would pass `SERVING_ORIGIN`.
RUN_CLIENT_NAMES = (f"{NAMESPACE}/{CLIENT}", CLIENT_FILE.name)
RUN_CLIENT = re.compile(
    r"(?<![\w.\-])(?:" + "|".join(map(re.escape, RUN_CLIENT_NAMES)) + r")(?![\w\-])"
)

REFERENCE = re.compile(r"""(?:src|href)\s*=\s*["']([^"']*)["']""")

#: ⛔ What a SERVING PROCESS adds to the page it answers, and the ONE way a page
#: ever gets the execution client (§8.3). ⚠️ A built text that names it is a
#: floor defect above; a SERVED page that does not carry it is an instance
#: offering Run and Submit the page cannot reach. ⭐ Both directions, one
#: constant.
CLIENT_TAG = f'<script src="{CLIENT_PATH}" defer></script>'.encode()


def served_page(on_disk: bytes) -> bytes:
    """Return the bytes an instance that registers `run` answers this built page with.

    ⛔ **A served page is not byte-identical to its file, by design**: only
    the server knows it is a
    server, so it inserts the client into what it answers and the file on disk
    stays a page that names no API at all (R8). ⭐ Derived here rather than
    imported from `routes.assets`, so a test comparing against it is comparing
    against the RULE and not against the implementation of the rule.
    """
    head = on_disk.index(b"</head>")
    return on_disk[:head] + CLIENT_TAG + on_disk[head:]


#: Every file a browser parses for references, and so every file a server URL could hide in.
TEXT_SUFFIXES = (".html", ".js", ".css")


def build(name: str, where: Path, into: Path | None = None) -> tuple[Path, Path]:
    """Build one fixture through `studyforge build`; return `(corpus root, site)`."""
    site = into if into is not None else where / f"site-{name}"
    site.mkdir(parents=True, exist_ok=True)
    root = FIXTURES / name
    code = dispatch(["build", str(root), "--out", str(site)], out=io.StringIO())
    assert code == OK, f"studyforge build {name} exited {code}"
    return root, site


def pages_of(root: Path) -> list[str]:
    """Every page the corpus declares, by the plan's own enumeration."""
    return sorted(str(p) for p in read_corpus(root).footprint.files if p.suffix == ".html")


def missing_media(root: Path, where: Path) -> frozenset[str]:
    """What the build itself reports as named by the material and absent from the archive."""
    probe = where / "missing-probe"
    probe.mkdir()
    return frozenset(str(path) for path in write_site(root, probe).missing)


def digests(site: Path) -> dict[str, str]:
    """Every file and directory under `site`, with a digest of each file's bytes."""
    return {
        path.relative_to(site).as_posix(): (
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "dir"
        )
        for path in sorted(site.rglob("*"))
    }


@dataclass
class Serving:
    """The verb, running on a thread: its server, what it printed, and its exit code."""

    server: ServingServer
    out: io.StringIO
    thread: threading.Thread
    code: list[int]


@contextlib.contextmanager
def verb_running(argv: list[str]) -> Iterator[Serving]:
    """Run `serve.main(argv)` on a thread until the block ends, then stop it through `started=`."""
    out = io.StringIO()
    ready = threading.Event()
    held: list[ServingServer] = []
    code: list[int] = []

    def started(server: ServingServer) -> None:
        held.append(server)
        ready.set()

    def target() -> None:
        code.append(serve_main(argv, out=out, started=started))
        ready.set()

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    assert ready.wait(20), "the verb neither started serving nor returned"
    assert held, f"the verb returned {code} without serving:\n{out.getvalue()}"
    try:
        yield Serving(held[0], out, thread, code)
    finally:
        held[0].shutdown()
        thread.join(timeout=20)


@dataclass
class Floor:
    """R8's reading over one site: what was inhabited, and every defect found."""

    pages: int = 0
    references: int = 0
    texts: dict[str, int] = field(default_factory=dict)
    defects: list[str] = field(default_factory=list)


def floor(site: Path, missing: frozenset[str] = frozenset()) -> Floor:
    """Read a built site as `file://` would: no origin, no server, only files on disk.

    ⛔ Two ways to need a server and both are read: a page or script that NAMES the
    serving origin, and a reference that resolves to no file — a rooted path needs an
    origin to mean anything. ⛔ A third is read because it is the one a panel would reach
    for: a built text naming the run client, which only the server adds.
    ⚠️ `missing` is the build's own report of material the archive lacks, and is the
    only allowance.
    """
    reading = Floor()
    base = site.resolve()
    for path in sorted(site.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        where = path.relative_to(site).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        reading.texts[path.suffix] = reading.texts.get(path.suffix, 0) + 1
        reading.defects += [
            f"{where} names the serving origin: {match.group(0)}"
            for match in SERVING_ORIGIN.finditer(text)
        ]
        reading.defects += [
            f"{where} loads the run client itself: {match.group(0)}"
            for match in RUN_CLIENT.finditer(text)
        ]
        if path.suffix != ".html":
            continue
        reading.pages += 1
        for reference in REFERENCE.findall(text):
            reading.references += 1
            reading.defects += _needs_a_server(base, path, where, reference, missing)
    return reading


def _needs_a_server(
    base: Path, page: Path, where: str, reference: str, missing: frozenset[str]
) -> list[str]:
    if reference.startswith("/"):
        return [f"{where} -> {reference} (rooted: it means nothing without an origin)"]
    if "://" in reference or reference.startswith(("#", "mailto:", "data:")):
        return []
    head = reference.split("#", 1)[0].split("?", 1)[0]
    if not head:
        return []
    target = (page.parent / head).resolve()
    if target.is_file():
        return []
    if not target.is_relative_to(base):
        return [f"{where} -> {reference} (leaves the site)"]
    if PurePosixPath(target.relative_to(base).as_posix()).as_posix() in missing:
        return []
    return [f"{where} -> {reference} (no such file)"]
