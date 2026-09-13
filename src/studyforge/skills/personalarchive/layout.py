"""The archive file's shape: its members, its manifest, and the checks every file passes.

**What it does.** Names the members of an archive file. Builds and reads its manifest,
`personal-archive.json`, which `personal_archive_api` versions (R9). Answers the two
questions every carried file is asked, on the way out and on the way in: may the
archive carry this path, and does it carry a personal-data shape (R7).

**How you use it.** `manifest_document(kind, source, files, progress=...)` and `render`
to write. `read_manifest(text)` to read: it refuses and never repairs.
`refused_path(path, store)` and `gate(path, data)` on every file. For a sharing
archive, `judge_bytes(path, data)` on every file `gate` could not read as text.
`speaker(stream)` for the report, which scrubs every line.

**Depends on.** `studyforge.version` for R9, `studyforge.archive.scrub` for R7, and
`studyforge.corpus.manifest` for its exceptions. ⛔ Not on `studyforge.progress`:
`record`, the one module that asks the store, passes in where the store lives.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import PurePosixPath

from studyforge.archive.scrub import assert_clean, leaks, scrub
from studyforge.corpus.manifest import RAISES as MANIFEST_RAISES
from studyforge.version import check

#: R9's key for this contract, registered in `version.CONTRACT_FIELDS` in the commit
#: that minted it. ⛔ Read through `check`: an unknown version is refused, never migrated.
PERSONAL_ARCHIVE_API = 1
KNOWN_PERSONAL_ARCHIVE_API = frozenset({PERSONAL_ARCHIVE_API})

#: The archive file's members. The material sits under one prefix, so no carried file
#: can be taken for the manifest or the progress record. ⚠️ The progress member is not
#: spelled like the store's own file, so a literal of that name outside `record` is a
#: finding in `test_thin.py` rather than a coincidence.
MANIFEST_MEMBER = "personal-archive.json"
PROGRESS_MEMBER = "progress-record.json"
MATERIAL_PREFIX = "material/"

#: Who an archive is for. ⛔ Chosen at the call, never defaulted (E11 § SK-06, R7).
OWNER = "owner"
SHARING = "sharing"
KINDS = (OWNER, SHARING)

#: Path segments that are never material: version-control metadata and bytecode caches.
NEVER_MATERIAL = frozenset({".git", "__pycache__"})

MANIFEST_KEYS = frozenset({"personal_archive_api", "kind", "source", "material", "progress"})
FILE_KEYS = frozenset({"path", "sha256", "bytes", "executable"})

#: The shortest run of printable characters that `judge_bytes` reads as text. ⚠️ Measured,
#: not chosen (`W235`'s handoff): over random bytes, runs of 12 still misfire on a short
#: tilde fragment or an address-shaped one and runs of 16 do not, so real audio passes. A
#: shape in a shorter run is not seen, and `SKILL.md` states that cost.
TEXT_RUN = 16

#: How a run of text is spelled in bytes: single bytes, then UTF-16 in both byte orders.
_CHARACTER = rb"[\x20-\x7e\t]"
TEXT_RUNS: tuple[tuple[re.Pattern[bytes], str], ...] = (
    (re.compile(_CHARACTER + b"{%d,}" % TEXT_RUN), "ascii"),
    (re.compile(b"(?:" + _CHARACTER + b"\x00){%d,}" % TEXT_RUN), "utf-16-le"),
    (re.compile(b"(?:\x00" + _CHARACTER + b"){%d,}" % TEXT_RUN), "utf-16-be"),
)

#: A zip entry's date. ⭐ Fixed, so two exports of one tree are the same bytes.
EPOCH = (1980, 1, 1, 0, 0, 0)


class ArchiveError(Exception):
    """An archive or a corpus this skill refuses. ⛔ Its message names places, never values."""


#: What any call into this skill lets out as a refusal rather than a crash.
REFUSALS: tuple[type[Exception], ...] = (ArchiveError, OSError, *MANIFEST_RAISES)


@dataclass(frozen=True)
class Material:
    """One carried file: its path relative to the corpus root, its bytes, its executable bit."""

    path: str
    data: bytes
    executable: bool

    def described(self) -> dict:
        """Return this file's manifest entry."""
        return {
            "path": self.path,
            "sha256": digest(self.data),
            "bytes": len(self.data),
            "executable": self.executable,
        }


def digest(data: bytes) -> str:
    """Return the SHA-256 hex digest of `data`."""
    return hashlib.sha256(data).hexdigest()


def render(document: dict) -> str:
    """Return a JSON document's exact text: sorted keys, two-space indent, one newline."""
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def speaker(stream=None) -> Callable[[str], None]:
    """Return the report's printer. ⛔ Every line is scrubbed on the way out (R7)."""
    target = sys.stdout if stream is None else stream

    def say(line: str) -> None:
        print(scrub(line), file=target, flush=True)

    return say


def manifest_document(kind: str, source: str, files, *, progress: bool) -> dict:
    """Return the manifest for an archive of `files`, gated before anything is written."""
    if kind not in KINDS:
        raise ArchiveError(f"who the archive is for must be one of {list(KINDS)}; none is assumed")
    if kind == SHARING and progress:
        raise ArchiveError("a sharing archive never carries progress")
    document = {
        "personal_archive_api": PERSONAL_ARCHIVE_API,
        "kind": kind,
        "source": source,
        "material": [material.described() for material in files],
        "progress": progress,
    }
    assert_clean(document, MANIFEST_MEMBER)
    return document


def read_manifest(text: str) -> dict:
    """Return the manifest in `text` if it is exactly one this build speaks, else refuse."""
    try:
        data = json.loads(text)
    except ValueError:
        raise ArchiveError(f"{MANIFEST_MEMBER} is not valid JSON") from None
    if not isinstance(data, dict):
        raise ArchiveError(f"{MANIFEST_MEMBER} is not an object")
    check(
        "personal_archive_api",
        data.get("personal_archive_api"),
        KNOWN_PERSONAL_ARCHIVE_API,
        where=MANIFEST_MEMBER,
        error=ArchiveError,
    )
    assert_clean(data, MANIFEST_MEMBER)
    if set(data) != MANIFEST_KEYS:
        raise ArchiveError(f"{MANIFEST_MEMBER} must have exactly the keys {sorted(MANIFEST_KEYS)}")
    if data["kind"] not in KINDS:
        raise ArchiveError(f"{MANIFEST_MEMBER} 'kind' is not one of {list(KINDS)}")
    if not isinstance(data["source"], str) or not data["source"]:
        raise ArchiveError(f"{MANIFEST_MEMBER} 'source' is not a non-empty str")
    if not isinstance(data["progress"], bool):
        raise ArchiveError(f"{MANIFEST_MEMBER} 'progress' is not a bool")
    if data["kind"] == SHARING and data["progress"]:
        raise ArchiveError("a sharing archive declares progress, and a sharing one carries none")
    if not isinstance(data["material"], list):
        raise ArchiveError(f"{MANIFEST_MEMBER} 'material' is not a list")
    for index, entry in enumerate(data["material"], start=1):
        _file(entry, f"{MANIFEST_MEMBER} file #{index}")
    paths = [entry["path"] for entry in data["material"]]
    if len(set(paths)) != len(paths):
        raise ArchiveError(f"{MANIFEST_MEMBER} names one file twice")
    return data


def refused_path(path: str, store: str) -> str | None:
    """Return why the archive may not carry `path`, or `None` when it may."""
    pure = PurePosixPath(path)
    if not path or "\\" in path or pure.is_absolute() or pure.as_posix() != path:
        return "is not a plain relative path"
    if ".." in pure.parts:
        return "climbs out of the corpus root"
    if NEVER_MATERIAL & set(pure.parts):
        return "is inside version-control metadata or a bytecode cache"
    if pure == PurePosixPath(store) or PurePosixPath(store) in pure.parents:
        return "is inside the progress store, which only its own seam writes"
    return None


def gate_name(path: str) -> None:
    """Refuse a carried file whose name holds a personal-data shape (R7)."""
    assert_clean(path, "a material file name")


def gate(path: str, data: bytes) -> bool:
    """Refuse a carried file whose name or UTF-8 text holds a personal-data shape.

    Return whether the contents were read as text. ⛔ `False` is an answer the caller
    must act on: a sharing archive hands such a file to `judge_bytes` (`SK-06/3`).
    """
    gate_name(path)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    assert_clean(text, path)
    return True


def carried_text(data: bytes) -> list[str]:
    """Return the text in `data`: every run of `TEXT_RUN` or more printable characters."""
    return [
        found.group().decode(encoding)
        for pattern, encoding in TEXT_RUNS
        for found in pattern.finditer(data)
    ]


def judge_bytes(path: str, data: bytes) -> None:
    """Refuse, by name and with the remedy, a file that is not text whose text holds a shape.

    ⛔ For a sharing archive, on every file `gate` could not read. The message names the
    file and the shape, never the value (R7).
    """
    for _where, shape in leaks(carried_text(data), path):
        raise ArchiveError(
            f"'{path}' is not UTF-8 text and its bytes carry text shaped like {shape} (R7); "
            f"remove the file or strip what it carries before sharing it, "
            f"or keep it in an owner archive, which carries it unread"
        )


def _file(entry: object, where: str) -> None:
    """Refuse one manifest file entry that is not exactly what `Material.described` builds."""
    if not isinstance(entry, dict) or set(entry) != FILE_KEYS:
        raise ArchiveError(f"{where} must be an object with exactly the keys {sorted(FILE_KEYS)}")
    if not isinstance(entry["path"], str):
        raise ArchiveError(f"{where} 'path' is not a str")
    sha = entry["sha256"]
    if not isinstance(sha, str) or len(sha) != 64 or set(sha) - set("0123456789abcdef"):
        raise ArchiveError(f"{where} 'sha256' is not a SHA-256 hex digest")
    size = entry["bytes"]
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ArchiveError(f"{where} 'bytes' is not an int of 0 or more")
    if not isinstance(entry["executable"], bool):
        raise ArchiveError(f"{where} 'executable' is not a bool")
