"""What in a source directory is material, what is deliberately not, and why.

**What it does.** Models `corpus.json`'s `content` key — plain `include`
globs, and `exclude` entries that each carry a `why` — and answers one
question about one path: is this **included**, **excluded**, or
**unclassified**?

**How you use it.** `policy.classify("src/ISO.md")`. ⛔ It takes a path and
does no I/O; enumerating a source root is `studyforge validate`'s job (SF-25),
and refusing the unclassified ones is its verdict.

**Depends on.** `pathlib.PurePosixPath` for glob semantics — a pure path
object that never touches a disk — and `errors`.

## Why this is a schema field and not a convention

⛔ **C2 is a schema problem, so the countermeasure is a schema field.** The
ISO corpus ships per-unit files *and* three whole-series aggregates that are
digest-identical ordered concatenations of them, so `src/*.md` ingests all 38
units twice and **nothing complains**. Nothing in a manifest without this
field could say otherwise, and no heuristic should: "these two files overlap"
is a finding for reconnaissance to report, not a guess for an ingest to make.

⭐ **The asymmetry is the design.** An inclusion needs no justification; an
**exclusion is material withheld from the reader**, and a withholding nobody
has to explain is one nobody audits — the same argument `permitted_edits`
already makes about an edit. So `include` is plain globs and every `exclude`
entry carries its `why`, long enough to be a reason.

⭐ **An exclusion names one path, never a glob**, and that follows from the
`why`. One justification covering a pattern is one justification for a set
whose membership changes when somebody adds a file — which is the audit
quietly widening itself. Each withheld file is named and explained on its own.

⚠️ **Exclusion wins over inclusion, and that is the ISO case exactly**:
`include: ["src/*.md"]` with `exclude: [{path: "src/ISO.md", …}]`. A file may
match both, and when it does it is withheld.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath

from studyforge.corpus.manifest.errors import ManifestError
from studyforge.describe import describe

#: Minimum characters of reason on an exclusion. ⛔ Not a quality bar — it
#: only stops `"why": "n/a"` from being a way through the gate, which is the
#: same argument and the same number `tools.quality.config` already uses for
#: a size exception. Two rules, one precedent.
MIN_WHY_CHARS = 20


class Classification(Enum):
    """What the content policy says about one path."""

    INCLUDED = "included"
    EXCLUDED = "excluded"
    #: ⛔ Not a third kind of content — it is the absence of a decision, and
    #: `validate` exits 1 on it (R6). A corpus cannot grow a file without
    #: somebody saying what it is, which is the point: the alternative is a
    #: second aggregate appearing and being read as 38 more units.
    UNCLASSIFIED = "unclassified"


@dataclass(frozen=True, slots=True)
class Exclusion:
    """One file withheld from the reader, and the reason it is."""

    path: str
    why: str


@dataclass(frozen=True, slots=True)
class ContentPolicy:
    """`corpus.json`'s `content`: what is material here, and what is not."""

    include: tuple[str, ...]
    exclude: tuple[Exclusion, ...]

    def classify(self, path: str) -> Classification:
        """Say whether `path` is included, excluded, or classified by neither.

        `path` is relative to the source root and spelled with forward
        slashes, the way every path in every one of this project's documents
        is.
        """
        if not isinstance(path, str) or not path:
            raise ManifestError(f"path to classify must be a non-empty str, got {describe(path)}")
        candidate = PurePosixPath(path)
        if any(exclusion.path == path for exclusion in self.exclude):
            return Classification.EXCLUDED
        if any(candidate.full_match(pattern) for pattern in self.include):
            return Classification.INCLUDED
        return Classification.UNCLASSIFIED

    def why_excluded(self, path: str) -> str | None:
        """Return the recorded reason `path` is withheld, or None if it is not."""
        for exclusion in self.exclude:
            if exclusion.path == path:
                return exclusion.why
        return None


def parse_content(value: object) -> ContentPolicy:
    """Build a `ContentPolicy` from the manifest's `content` object."""
    if not isinstance(value, dict):
        raise ManifestError(f"'content' must be an object, got {describe(value)}")
    unknown = sorted(set(value) - {"include", "exclude"})
    if unknown:
        raise ManifestError(f"'content' has unknown key(s) {unknown}; expected include, exclude")
    return ContentPolicy(_include_of(value), _exclude_of(value))


def _include_of(value: dict) -> tuple[str, ...]:
    """Return the `include` globs, which must exist and must include something."""
    include = value.get("include")
    if not isinstance(include, list) or not include:
        raise ManifestError(
            f"'content.include' must be a non-empty list of globs, got {describe(include)} "
            f"(a corpus that includes nothing has no material)"
        )
    for position, pattern in enumerate(include, start=1):
        if not isinstance(pattern, str) or not pattern:
            raise ManifestError(
                f"'content.include[{position - 1}]' must be a non-empty str, got {pattern!r}"
            )
        _reject_absolute(pattern, f"content.include[{position - 1}]")
    return tuple(include)


def _exclude_of(value: dict) -> tuple[Exclusion, ...]:
    """Return the `exclude` entries — may be empty, each present one with its reason."""
    exclude = value.get("exclude", [])
    if not isinstance(exclude, list):
        raise ManifestError(f"'content.exclude' must be a list, got {describe(exclude)}")
    entries = []
    seen: set[str] = set()
    for index, entry in enumerate(exclude):
        where = f"content.exclude[{index}]"
        if not isinstance(entry, dict):
            raise ManifestError(f"{where} must be an object, got {describe(entry)}")
        unknown = sorted(set(entry) - {"path", "why"})
        if unknown:
            raise ManifestError(f"{where} has unknown key(s) {unknown}; expected path, why")
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            raise ManifestError(f"{where}.path must be a non-empty str, got {path!r}")
        _reject_absolute(path, f"{where}.path")
        if "*" in path or "?" in path or "[" in path:
            raise ManifestError(
                f"{where}.path must name one file, got the pattern {path!r} — "
                f"one reason cannot explain a set whose membership changes"
            )
        if path in seen:
            raise ManifestError(f"{where}.path {path!r} is excluded twice")
        seen.add(path)
        entries.append(Exclusion(path, _why_of(entry.get("why"), where)))
    return tuple(entries)


def _why_of(why: object, where: str) -> str:
    """Return the reason an exclusion gives, refused if it is not one."""
    if not isinstance(why, str) or not why.strip():
        raise ManifestError(
            f"{where}.why must say why this file is withheld from the reader, got {why!r}"
        )
    if len(why.strip()) < MIN_WHY_CHARS:
        raise ManifestError(
            f"{where}.why must be at least {MIN_WHY_CHARS} characters of reason, "
            f"got {why!r} — an exclusion nobody has to explain is one nobody audits"
        )
    return why


def _reject_absolute(pattern: str, where: str) -> None:
    """Refuse a path that escapes the source root (R7 as much as correctness)."""
    if pattern.startswith("/") or pattern.startswith("~") or ".." in PurePosixPath(pattern).parts:
        raise ManifestError(
            f"{where} must be relative to the source root and stay inside it, got {pattern!r}"
        )
