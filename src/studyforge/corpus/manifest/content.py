"""What in a source directory is material, what is deliberately not, and why.

**What it does.** Models `corpus.json`'s `content` key — plain `include`
globs, `exclude` entries that each name one file and carry a `why`, and
`not_material` globs that each carry one too — and answers one question about
one path: **included**, **excluded**, **not material**, **contested** or
**unclassified**?

**How you use it.** `policy.classify("src/whole-series.md")`. ⛔ It takes a
path and does no I/O; enumerating a source root is `studyforge validate`'s job
(SF-25), and refusing the unclassified ones is its verdict.

**Depends on.** `pathlib.PurePosixPath` for glob semantics — a pure path
object that never touches a disk — and `errors`.

## Why this is a schema field and not a convention

⛔ **C2 is a schema problem, so the countermeasure is a schema field.** One of
the four designed shapes ships per-unit files *and* three whole-series
aggregates that are digest-identical ordered concatenations of them, so
`src/*.md` ingests all 38 units twice and **nothing complains**. Nothing in a
manifest without this field could say otherwise, and no heuristic should:
"these two files overlap" is a finding for reconnaissance to report, not a
guess for an ingest to make.

⭐ **The asymmetry is the design.** An inclusion needs no justification; an
**exclusion is material withheld from the reader**, and a withholding nobody
has to explain is one nobody audits — the same argument `permitted_edits`
already makes about an edit. So `include` is plain globs and every `exclude`
entry carries its `why`, long enough to be a reason.

⭐ **An exclusion names one path, never a glob**, and that follows from the
`why`. One justification covering a pattern is one justification for a set
whose membership changes when somebody adds a file — which is the audit
quietly widening itself. Each withheld file is named and explained on its own.

⚠️ **Exclusion wins over inclusion, and that is that shape's case exactly**:
`include: ["src/*.md"]` with `exclude: [{path: "src/whole-series.md", …}]`. A file may
match both, and when it does it is withheld.

## ⛔ The third state, and why it takes globs where an exclusion takes a path

⛔ **Two states are not enough, because a real repository is mostly a third.**
Measured against one, 2026-09-10: of 141 files, 38 were included, 3 excluded
and **100 unclassified — and only 3 of the hundred were material withheld from
anybody**. The rest were a licence, ignore files, an editor's workspace, a
generated cache. Filing those under `exclude` makes every `why` a small lie
and makes an audit nobody reads.

⭐ **The three states are about whether a file's prose is read into the
archive**, never about materiality in the abstract: `include` reads it in,
`exclude` is prose that *would* be read and deliberately is not, and
`not_material` is not prose to read at all. ⭐ A source `README.md` lands in
the third by that test rather than as a special case — it is the corpus's own
navigation, and the reader loses nothing because every address, title and
ordinal it records is declared in the manifest's container maps.

⚠️ **An exclusion's refusal of globs is right and does not carry over**,
because the two audits are about different harms: a new member of an
exclusion's set is a new withholding and needs its own reason, and a new
member of a `not_material` glob's set is only a harm if it is **actually
material** — which is caught per file, against a real tree, as `CONTESTED`.
⛔ **The category also cannot be enumerated file by file:** writing the finding
that produced this field took the count from 100 to 101, because the new entry
was the file containing it. ⭐ **`X1` is not weakened, and its domain is now
stated** — an inclusion needs no justification, and every declaration that the
framework will *not* read a file needs one.

## ⛔ Rule 1a — an entry is an exact path, or one directory's wildcard

⛔ **A wildcard whose fixed prefix is not a directory is refused**, however
exactly it matches today. ⚠️ **`CONTESTED` catches a loose glob only when the
swept file is *also* in `include`**, so it is not this rule: the hole is the
file that does not exist yet, classified under a `why` that was never about it
— ⛔ **and `UNCLASSIFIED`, the catch that would have surfaced it, goes quiet
because the file is now classified.** ⭐ A directory-scoped glob can only
silence that *inside* a directory already declared not-material, which is the
declaration doing its job.

⚠️ **The rule refuses the clever pattern that covers today's tree exactly**: a
bracket class matching three root files because a fourth happens to begin with
another letter encodes the collision rather than the intent, and a `why` must
be true of everything its glob matches, including what nobody has written yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath

from studyforge.corpus.manifest.errors import ManifestError
from studyforge.describe import describe, describe_keys

#: Minimum characters of reason on an exclusion, and on a `not_material`
#: entry. ⛔ Not a quality bar — it only stops `"why": "n/a"` from being a way
#: through the gate, which is the same argument and the same number
#: `tools.quality.config` already uses for a size exception. Two rules, one
#: precedent.
MIN_WHY_CHARS = 20

#: The characters that make a pattern a glob rather than a path. ⚠️ Stated
#: once because two checks ask the same question of a string: an exclusion
#: refuses all of them, and rule 1a asks where the first one falls.
WILDCARDS = ("*", "?", "[")


class Classification(Enum):
    """What the content policy says about one path."""

    INCLUDED = "included"
    EXCLUDED = "excluded"
    #: ⛔ Not material at all: the repository's own scaffolding, or content
    #: *about* the material. ⚠️ Nothing is withheld from a reader here, which
    #: is why it is not `EXCLUDED`.
    NOT_MATERIAL = "not-material"
    #: ⛔ Matched by `include` **and** by `not_material`, and this build
    #: refuses to choose. ⭐ **Never a precedence** — one would let a loose
    #: glob quietly drop material, or read the scaffolding aloud. `validate`
    #: exits 1 on it under its own rule id, which is what stops the third
    #: state becoming a place to sweep things into.
    CONTESTED = "contested"
    #: ⛔ Not a further kind of content — it is the absence of a decision, and
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
class NotMaterial:
    """One glob of files that were never material, and the reason they are not."""

    glob: str
    why: str


@dataclass(frozen=True, slots=True)
class ContentPolicy:
    """`corpus.json`'s `content`: what is material here, and what is not."""

    include: tuple[str, ...]
    exclude: tuple[Exclusion, ...]
    #: ⛔ Defaults to empty, and that is the whole compatibility story: a
    #: manifest at `corpus_api: 1` declares no third state and classifies
    #: exactly as it did before.
    not_material: tuple[NotMaterial, ...] = ()

    def classify(self, path: str) -> Classification:
        """Say what this manifest declares about `path`, without choosing for it.

        `path` is relative to the source root and spelled with forward
        slashes, the way every path in every one of this project's documents
        is.

        ⛔ **Two matches are reported, not resolved.** An exclusion still wins
        over an inclusion — one file, named once and withheld deliberately —
        but `include` and `not_material` disagreeing is two glob authors
        contradicting each other, and the honest answer is `CONTESTED`.
        """
        if not isinstance(path, str) or not path:
            raise ManifestError(f"path to classify must be a non-empty str, got {describe(path)}")
        candidate = PurePosixPath(path)
        if any(exclusion.path == path for exclusion in self.exclude):
            return Classification.EXCLUDED
        included = any(candidate.full_match(pattern) for pattern in self.include)
        scaffolding = any(candidate.full_match(entry.glob) for entry in self.not_material)
        if included and scaffolding:
            return Classification.CONTESTED
        if included:
            return Classification.INCLUDED
        if scaffolding:
            return Classification.NOT_MATERIAL
        return Classification.UNCLASSIFIED

    def why_excluded(self, path: str) -> str | None:
        """Return the recorded reason `path` is withheld, or None if it is not."""
        for exclusion in self.exclude:
            if exclusion.path == path:
                return exclusion.why
        return None

    def why_not_material(self, path: str) -> str | None:
        """Return the recorded reason `path` was never material, or None.

        ⭐ The first matching entry: a `why` nobody can retrieve is a
        declaration nobody audits, which is the argument that makes it
        mandatory in the first place.
        """
        candidate = PurePosixPath(path)
        for entry in self.not_material:
            if candidate.full_match(entry.glob):
                return entry.why
        return None


def parse_content(value: object) -> ContentPolicy:
    """Build a `ContentPolicy` from the manifest's `content` object."""
    if not isinstance(value, dict):
        raise ManifestError(f"'content' must be an object, got {describe(value)}")
    unknown = sorted(set(value) - {"include", "exclude", "not_material"})
    if unknown:
        raise ManifestError(
            f"'content' has unknown key(s), {describe_keys(unknown)}; "
            f"expected include, exclude, not_material"
        )
    return ContentPolicy(_include_of(value), _exclude_of(value), _not_material_of(value))


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
                f"'content.include[{position - 1}]' must be a non-empty str, "
                f"got {describe(pattern)}"
            )
        _reject_absolute(pattern, f"content.include[{position - 1}]")
    return tuple(include)


def _exclude_of(value: dict) -> tuple[Exclusion, ...]:
    """Return the `exclude` entries — may be empty, each present one with its reason."""
    exclude = value.get("exclude", [])
    if not isinstance(exclude, list):
        raise ManifestError(f"'content.exclude' must be a list, got {describe(exclude)}")
    entries = []
    seen: dict[str, int] = {}
    for index, entry in enumerate(exclude):
        where = f"content.exclude[{index}]"
        if not isinstance(entry, dict):
            raise ManifestError(f"{where} must be an object, got {describe(entry)}")
        unknown = sorted(set(entry) - {"path", "why"})
        if unknown:
            raise ManifestError(
                f"{where} has unknown key(s), {describe_keys(unknown)}; expected path, why"
            )
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            raise ManifestError(f"{where}.path must be a non-empty str, got {describe(path)}")
        _reject_absolute(path, f"{where}.path")
        if any(wildcard in path for wildcard in WILDCARDS):
            raise ManifestError(
                f"{where}.path must name one file and this one is a glob — "
                f"one reason cannot explain a set whose membership changes"
            )
        if path in seen:
            # ⛔ Both positions, never the path (W19). The reader has the file
            # in front of them; what they cannot see is which other entry
            # collides, and two reasons for one exclusion is the actual defect.
            raise ManifestError(
                f"{where}.path is already excluded by content.exclude[{seen[path]}]; "
                f"two reasons for one exclusion is two audits and no record of which held"
            )
        seen[path] = index
        why = _why_of(
            entry.get("why"),
            where,
            says="why this file is withheld from the reader",
            noun="an exclusion",
        )
        entries.append(Exclusion(path, why))
    return tuple(entries)


def _not_material_of(value: dict) -> tuple[NotMaterial, ...]:
    """Return the `not_material` globs — the third state, optional and defaulted.

    ⛔ **Absent means an empty tuple**, which is why a manifest written before
    this key existed still parses unchanged. ⚠️ The version bump is not about
    those manifests — it is about a manifest that *uses* the key being
    unreadable to an older build, which is what R9 versions.
    """
    declared = value.get("not_material", [])
    if not isinstance(declared, list):
        raise ManifestError(f"'content.not_material' must be a list, got {describe(declared)}")
    entries = []
    seen: dict[str, int] = {}
    for index, entry in enumerate(declared):
        where = f"content.not_material[{index}]"
        if not isinstance(entry, dict):
            raise ManifestError(f"{where} must be an object, got {describe(entry)}")
        unknown = sorted(set(entry) - {"glob", "why"})
        if unknown:
            raise ManifestError(
                f"{where} has unknown key(s), {describe_keys(unknown)}; expected glob, why"
            )
        glob = entry.get("glob")
        if not isinstance(glob, str) or not glob:
            raise ManifestError(f"{where}.glob must be a non-empty str, got {describe(glob)}")
        _reject_absolute(glob, f"{where}.glob")
        _reject_loose_glob(glob, f"{where}.glob")
        if glob in seen:
            # ⛔ Both positions, never the pattern — the exclusion twin's rule
            # (W19), for the twin's reason.
            raise ManifestError(
                f"{where}.glob is already declared by content.not_material[{seen[glob]}]; "
                f"two reasons for one declaration is two audits and no record of which held"
            )
        seen[glob] = index
        why = _why_of(
            entry.get("why"),
            where,
            says="why this file was never material",
            noun="a declaration that the framework will not read a file",
        )
        entries.append(NotMaterial(glob, why))
    return tuple(entries)


def _reject_loose_glob(glob: str, where: str) -> None:
    """Rule 1a: an entry is an exact path, or one directory's wildcard.

    ⛔ **One sentence, mechanical rather than a matter of taste — reject a
    wildcard whose fixed prefix is not a directory.** A pattern whose
    correctness depends on which files happen *not* to exist is refused
    however exactly it matches the tree in front of its author today.
    ⚠️ The pattern is not quoted back: the actionable half is which rule was
    broken, and the author has what they wrote in front of them.
    """
    cut = min((glob.find(wildcard) for wildcard in WILDCARDS if wildcard in glob), default=-1)
    if cut < 0:
        return
    if not glob[:cut].endswith("/"):
        raise ManifestError(
            f"{where} puts a wildcard where no directory precedes it. A not_material "
            f"entry is an exact path, or a wildcard under a directory that is itself "
            f"entirely not material; a pattern whose correctness depends on which files "
            f"happen not to exist silences the unclassified check for a file nobody has "
            f"considered yet"
        )


def _why_of(why: object, where: str, *, says: str, noun: str) -> str:
    """Return the reason a declaration gives, refused if it is not one.

    ⭐ `says` and `noun` are the caller's because the two declarations are
    different sentences: an exclusion withholds material from a reader, and a
    `not_material` entry says there was never any to withhold. ⛔ Writing
    *"withheld"* into the second is the small lie the third state removes.
    """
    if not isinstance(why, str) or not why.strip():
        raise ManifestError(f"{where}.why must say {says}, got {describe(why)}")
    if len(why.strip()) < MIN_WHY_CHARS:
        raise ManifestError(
            f"{where}.why must be at least {MIN_WHY_CHARS} characters of reason, "
            f"got {len(why)} — {noun} nobody has to explain is one nobody audits"
        )
    return why


def _reject_absolute(pattern: str, where: str) -> None:
    """Refuse a path that escapes the source root — and never quote it (R7).

    ⛔ **This branch fires *because* the value is an absolute or escaping path,
    which is precisely when it carries a home directory.** It quoted the value
    until W19: the check written to keep a path out of the corpus put it in the
    log instead. ⚠️ **Worse than the site W1 fixed** — `require_slug` fired on
    "not a slug", which is only *sometimes* a path; this one tests
    `startswith("/")`.

    ⭐ The fault is named instead, and it is the actionable half: a reader who
    wrote `/opt/material/x` knows what they wrote and needs to be told which
    rule it broke.
    """
    if pattern.startswith("/") or pattern.startswith("~") or ".." in PurePosixPath(pattern).parts:
        raise ManifestError(
            f"{where} must be relative to the source root and stay inside it; "
            f"it {_escape(pattern)}, and it is not reproduced here because that "
            f"shape is where a home directory lives"
        )


def _escape(pattern: str) -> str:
    """Name *how* a path leaves the source root, without reproducing it.

    ⛔ Three faults, named separately, because they are three different
    mistakes: an absolute path, a home-relative one, and one that climbs out
    with `..`. ⚠️ Reported in the order they are tested, so the sentence
    matches the branch a reader would go and look at.
    """
    if pattern.startswith("/"):
        return "begins with a slash"
    if pattern.startswith("~"):
        return "begins with a tilde"
    return "climbs above the root with '..'"
