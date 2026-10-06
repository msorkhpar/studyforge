r"""File versions: what a served file was found to be, held until the file moves.

**What it does.** `version_of(stat)` names one version of a file on disk — its device,
inode, size, modification and change times. `Versions` is a bounded, thread-safe memo
keyed by a path, an aspect and that version: what the assets route judged a file's bytes
to be (the personal-data gate, a quiz's key) and its compressed form. `Judged` is one
request's view of one file: its version, its bytes read at most once, and each verdict
asked of the memo before it is computed. `build_digest` is the digest the build's own
discovery record carries for the corpus a file belongs to, which the asset's validator
folds in.

**How you use it.**

    memo = Versions()                              # one per server
    judged = Judged(path, path.stat(), memo)
    clean = judged.verdict("gate", lambda: passes(judged.bytes()))
    digest = build_digest(root, path, memo)        # or None, for a root no build recorded

**Depends on.** `os`, `threading`, `time`, `collections`, `corpus.placement.profile`
for the generated directory's name, `corpus.placement` for the record's, and
`corpus.discovery` to read it, gate included.

## ⭐ Why a verdict is held at all

A 3 MB search index judged on every request is seconds of one core per request, and a
crawl asks for it from every page. ⭐ **The bytes of one version never change, so neither
does any verdict over them**: held against the version, it is computed once, and a file
that moves — rewritten, replaced, touched — is a different version and judged afresh.

⭐ **One verdict is reached once, however many requests ask for it at the same moment**: a
crawl's first burst asks every page's assets together, and each request judging the same
file side by side is the same seconds of one core, multiplied. The first judges under the
path and aspect's lock (`Versions.judging`); the others wait and take its verdict.

## ⛔ A file modified within `SETTLE_NS` of its judgement is NOT held

⭐ The racily-clean rule: a timestamp's granularity can be coarser than two writes, so a
file rewritten in the same tick at the same size would otherwise keep the first write's
verdict. A file is held only once its modification and change times are older than the
window, and until then it is judged on every request exactly as it always was.

⛔ **A held verdict is never a reason to serve bytes nobody judged.** `Judged.bytes` reads
from one open handle and raises `Moved` when that handle is not the version the request's
verdicts were asked at, so the caller starts again from a fresh `stat`; a streamed answer
carries its version, and `serve.app` refuses to send a file whose open handle has moved.
"""

from __future__ import annotations

import os
import threading
import time
from collections import OrderedDict
from collections.abc import Callable, Hashable
from pathlib import Path

from studyforge.corpus.discovery import read_cache
from studyforge.corpus.placement import SITE_CACHE_FILENAME
from studyforge.corpus.placement.profile import GENERATED_ROOT

#: A file's version: device, inode, size, mtime and ctime, in nanoseconds.
Version = tuple[int, int, int, int, int]

#: How long a file must have stood unmodified before a verdict over it is held.
SETTLE_NS = 2_000_000_000

#: How many verdicts a memo holds, and how many bytes of compressed bodies.
MAX_ENTRIES = 4096
MAX_BYTES = 64 * 1024 * 1024

#: What `Versions.get` answers when nothing is held.
MISSING = object()

#: The key a build's discovery record carries its digest under.
DIGEST_KEY = "scan_sha256"


def version_of(stat: os.stat_result) -> Version:
    """Return the version a `stat` names."""
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)


def settled(stat: os.stat_result, now: int | None = None) -> bool:
    """Say whether a file has stood unmodified for `SETTLE_NS`, so a verdict may be held."""
    moved = max(stat.st_mtime_ns, stat.st_ctime_ns)
    return (time.time_ns() if now is None else now) - moved > SETTLE_NS


class Versions:
    """A bounded memo of verdicts, each held against the file version it was reached on."""

    def __init__(self, entries: int = MAX_ENTRIES, budget: int = MAX_BYTES) -> None:
        """Hold at most `entries` verdicts and `budget` bytes of held bodies."""
        self.entries, self.budget = entries, budget
        self._held: OrderedDict[tuple, tuple[Version, object, int]] = OrderedDict()
        self._bytes = 0
        self._lock = threading.Lock()
        self._judging: dict[tuple, threading.Lock] = {}

    def judging(self, path: str, aspect: Hashable) -> threading.Lock:
        """Return the lock one verdict is reached under, so a burst of requests reaches it once.

        ⚠️ One lock per path and aspect ever judged, which is bounded by the files served.
        """
        if self.entries <= 0:
            return threading.Lock()
        with self._lock:
            return self._judging.setdefault((path, aspect), threading.Lock())

    def get(self, path: str, aspect: Hashable, version: Version) -> object:
        """Return what is held for `path`'s `aspect` at `version`, or `MISSING`."""
        with self._lock:
            held = self._held.get((path, aspect))
            if held is None or held[0] != version:
                return MISSING
            self._held.move_to_end((path, aspect))
            return held[1]

    def put(self, path: str, aspect: Hashable, version: Version, value: object) -> None:
        """Hold `value` for `path`'s `aspect` at `version`, evicting the least recently used."""
        size = (
            sum(len(one) for one in value if isinstance(one, bytes))
            if isinstance(value, tuple)
            else 0
        )
        if self.entries <= 0 or size > self.budget:
            return
        with self._lock:
            old = self._held.pop((path, aspect), None)
            self._bytes -= old[2] if old else 0
            self._held[(path, aspect)] = (version, value, size)
            self._bytes += size
            while len(self._held) > self.entries or self._bytes > self.budget:
                _, (_, _, freed) = self._held.popitem(last=False)
                self._bytes -= freed


#: The memo a caller that passes none gets: it holds nothing, so every request judges.
UNHELD = Versions(entries=0, budget=0)


class Moved(Exception):
    """The file was rewritten between the `stat` its verdicts were asked at and its read."""


class Judged:
    """One file as one request found it: its version, its bytes, and its verdicts."""

    def __init__(self, path: Path, stat: os.stat_result, memo: Versions = UNHELD) -> None:
        """Take the file at the version `stat` names; nothing is read yet."""
        self.path, self.stat, self.memo = path, stat, memo
        self.version = version_of(stat)
        self._body: bytes | None = None

    @property
    def read(self) -> bool:
        """Say whether this request has read the file's bytes."""
        return self._body is not None

    def bytes(self) -> bytes:
        """Return the file's bytes, read once; raise `Moved` when they are another version's."""
        if self._body is None:
            with self.path.open("rb") as handle:
                if version_of(os.fstat(handle.fileno())) != self.version:
                    raise Moved
                self._body = handle.read()
        return self._body

    def verdict[T](self, aspect: Hashable, judge: Callable[[], T], against: object = None) -> T:
        """Return the held verdict for `aspect`, or `judge()`, held when the file has settled.

        ⭐ `against` is what else the verdict was reached over (a quiz's marks): a verdict
        held against anything unequal to it is judged again.
        """
        held = self._held(aspect, against)
        if held is not MISSING:
            return held  # type: ignore[return-value]
        with self.memo.judging(str(self.path), aspect):
            held = self._held(aspect, against)
            if held is not MISSING:
                return held  # type: ignore[return-value]
            value = judge()
            if settled(self.stat):
                self.memo.put(str(self.path), aspect, self.version, (against, value))
        return value

    def _held(self, aspect: Hashable, against: object) -> object:
        """Return the verdict held for `aspect` against `against`, or `MISSING`."""
        held = self.memo.get(str(self.path), aspect, self.version)
        if held is MISSING or held[0] != against:  # type: ignore[index]
            return MISSING
        return held[1]  # type: ignore[index]


def build_digest(base: Path, path: Path, memo: Versions = UNHELD) -> str | None:
    """Return the digest the nearest build record above `path`, within `base`, carries.

    ⭐ The record is the generated directory's discovery cache; a root no build recorded
    has none, and the validator is then the file's size and times alone.
    """
    for directory in path.parents:
        if directory != base and base not in directory.parents:
            return None
        if directory.name == GENERATED_ROOT:
            continue
        record = directory / GENERATED_ROOT / SITE_CACHE_FILENAME
        try:
            stat = record.stat()
        except OSError:
            continue
        held = memo.get(str(record), DIGEST_KEY, version_of(stat))
        if held is MISSING:
            held = _digest_in(record)
            if settled(stat):
                memo.put(str(record), DIGEST_KEY, version_of(stat), held)
        return held  # type: ignore[return-value]
    return None


def _digest_in(record: Path) -> str | None:
    """Return a discovery record's digest, read by its own reader, when it is plain hexadecimal."""
    cached = read_cache(record)
    digest = None if cached is None or not cached.supported else cached.scan_sha256
    ok = isinstance(digest, str) and digest.isascii() and digest.isalnum() and len(digest) <= 128
    return digest if ok else None
