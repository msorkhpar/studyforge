r"""The source ledger: one entry per fenced example and per test file a source carries.

**What it does.** Reads every file a corpus declares as its material and as its
tests, exactly once, and records what each one carries — ⭐ **an entry per
fenced example and an entry per test file** — together with the digest of every
file it read.

**How you use it.**

    from studyforge.skills.exercises.ledger import digests, key_of, take

    ledger = take(root, sources=("guide.md",), tests=("check_it.py",), where="the ledger")
    digests(ledger)              # {path: 'sha256:…'} — the mapping gate G5 asks
    key_of(ledger.entries[0])    # the token a written reason is filed under

⭐ **Whether each entry is accounted for is `accounting`'s**, which reads what
this module produces. ⛔ The seam runs ONE WAY: that module imports this one and
this one imports nothing back.

**Depends on.** `scan` for what a material file carries,
`studyforge.sourcepath` for what a path inside a source may be,
`studyforge.exercise.gates` for the one digest, and `pathlib`. Standard library
only. ⛔ Not on any adapter and not on any source (R1).

## ⛔ THE LEDGER IS THE PROOF OF *NOTHING IS LOST*, AND A PROOF IS MECHANICAL

⭐ **`E14`'s first property is the reason this module exists.** The reading
floor is untouched and every example still renders; the ledger is what makes
that a claim somebody can check rather than a sentence in a guide (spec §7 §3).

## ⛔ THE TWO POPULATIONS ARE DATA, AND THE FRAMEWORK GUESSES NEITHER (R1)

⚠️ **There is no pattern here for *what a test file looks like*, deliberately.**
`src/test/java/**`, `test_*.py`, `*_test.go` and `check_*.py` are four sources'
conventions, and a framework that knew them would know four sources. ⭐ **What
is material and what is a grader is the corpus's own declaration** — the thing
`corpus.json` already exists to say — and it arrives here as two lists of paths.

## ⛔ THE MAPPING `G5` CONSUMES IS ALREADY LANDED, AND IT IS KEYED BY PATH

⚠️ **MEASURED, not chosen:** `exercise.gates.code` and
`exercise.gates.quiz.mechanical` both take the ledger as a `Mapping[str, str]`
and ask it exactly one question — `ledger.get(origin.path)`, compared against
the `Cited` digest a gate record carries. ⭐ So `digests()` is the ledger's
gate-facing face and it is **the digest of the whole file**, per path. ⛔ The
per-entry digest is a different value for a different reader and is never
handed to a gate: an example's digest is the bytes of that example, which is
what lets a re-run say *which* example moved rather than only which file did.

## ⭐ ONE FILE IS READ ONCE, AND THE ORDER IS DERIVED (R10)

⛔ **Nothing here depends on the order the caller handed the two populations
in.** The files are read in sorted order and the entries are sorted by file and
then by position, so two runs over an unchanged corpus produce the same ledger.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from studyforge.exercise.gates import digest_of_bytes
from studyforge.skills.exercises.scan import Scan, scan
from studyforge.sourcepath import SOURCE_PATH_DESCRIBED, source_path_fault

#: One fenced example the source carries, in a material file.
EXAMPLE = "example"

#: One test file the source carries, whole.
TESTS = "tests"

#: ⛔ Closed. A third kind is a decision somebody makes here, never a file
#: appearing: the two are what spec §7 §3 names, and an entry this build cannot
#: classify is one nothing could account for.
ENTRY_KINDS = (EXAMPLE, TESTS)

#: The keys of one entry, in the order the document writes them (R10).
ENTRY_KEYS = ("kind", "path", "ordinal", "sections", "language", "digest")

#: The keys of one source file the ledger read. ⭐ `sections` is every heading
#: the file carries, in order and with its repeats, because that is what
#: answers both of `SF-36`'s questions about a region an origin names.
SOURCE_KEYS = ("path", "digest", "sections")


class LedgerError(ValueError):
    """A source the ledger cannot account for, and what about it is the reason.

    ⛔ Names the entry, the field and the permitted class — never the value of
    anything read out of a corpus (R7).
    """


@dataclass(frozen=True, slots=True)
class Source:
    """One file the ledger read: what it digested to, and the headings it carries.

    ⛔ `digest` is the file's own, and it is the value `G5` compares a `Cited`
    passage against. `sections` keeps its repeats: a name occurring twice is
    what makes a region ambiguous, and dropping the repeat would hide it.
    """

    path: str
    digest: str
    sections: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Entry:
    """One thing the source carries that an exercise could be built from.

    ⛔ Frozen and never validated here: `take` is what guarantees the path is a
    source path and the kind is one of `ENTRY_KINDS`. ⭐ A test file's
    `ordinal` is zero — it has no position inside itself — and its digest is
    the file's own.
    """

    kind: str
    path: str
    ordinal: int
    sections: tuple[str, ...]
    language: str | None
    digest: str


@dataclass(frozen=True, slots=True)
class Ledger:
    """Every file the ledger read, and every entry those files carry."""

    sources: tuple[Source, ...]
    entries: tuple[Entry, ...]


def key_of(entry: Entry) -> str:
    """Return the token a written reason is filed under — ⭐ an entry's one spelling.

    ⛔ A test file is its path and an example is its path and its position in
    that file, so a reason names an entry without anybody inventing an id.
    ⚠️ **The separator is `:` and deliberately NOT `#`.** `SF-36` refused a
    fragment in a source path outright — *"a path carrying a fragment"* — so a
    key that looked like one would invite exactly the spelling this tree
    refuses; ⭐ and `<what>:<which>` is the shape `gates.digests` already uses
    for `plant:<case id>` and `question:<id>`. ⛔ No source path carries a `:`,
    so the last segment is unambiguous.
    """
    if entry.kind == TESTS:
        return f"{TESTS}:{entry.path}"
    return f"{EXAMPLE}:{entry.path}:{entry.ordinal}"


def take(root: Path, sources: Iterable[str], tests: Iterable[str], where: str) -> Ledger:
    """Read every declared file once and return the entries it carries.

    ⛔ **A file named in both populations is refused rather than counted
    twice**: the ledger records a test file whole and scans material for the
    examples inside it, so a file that is both would be two different claims
    about the same bytes.
    """
    material = frozenset(_source_path(path, "a material path", where) for path in sources)
    graders = frozenset(_source_path(path, "a test path", where) for path in tests)
    _require_distinct(material, graders, where)
    entries: list[Entry] = []
    recorded: list[Source] = []
    for path in sorted(material | graders):
        text = _text(root, path, where)
        digest = digest_of_bytes(text.encode("utf-8"))
        read = _scanned(text, path, where) if path in material else Scan((), (), False)
        recorded.append(Source(path=path, digest=digest, sections=read.headings))
        if path in graders:
            entries.append(Entry(TESTS, path, 0, (), None, digest))
        entries.extend(
            Entry(
                kind=EXAMPLE,
                path=path,
                ordinal=fence.ordinal,
                sections=fence.sections,
                language=fence.language,
                digest=digest_of_bytes(fence.body.encode("utf-8")),
            )
            for fence in read.fences
        )
    return Ledger(tuple(recorded), tuple(sorted(entries, key=_order)))


def digests(ledger: Ledger) -> dict[str, str]:
    """Return the `Mapping[str, str]` gate `G5` asks: every file read, by path."""
    return {source.path: source.digest for source in ledger.sources}


def _scanned(text: str, path: str, where: str) -> Scan:
    """Scan one material file, refusing a fence it opens and never closes.

    ⛔ **Refused rather than guessed at.** Where the file ends inside a fence,
    nothing says where the example stopped, and a ledger that recorded one
    anyway would digest a value the next edit changes for a reason nobody wrote
    down. ⭐ `scan` reports the fact and this is where it becomes a refusal.
    """
    read = scan(text)
    if read.unclosed:
        raise LedgerError(
            f"{where}: '{path}' opens a fenced block and never closes it, so the "
            f"ledger cannot say where that example ends. The file's contents are not "
            f"reproduced here (R7)."
        )
    return read


def _order(entry: Entry) -> tuple[str, int, str]:
    """Sort entries by file, then by position, with a file's test entry first."""
    return (entry.path, entry.ordinal, entry.kind)


def _source_path(value: object, what: str, where: str) -> str:
    """Refuse a path that is not a location inside the source, without quoting it."""
    fault = source_path_fault(value) if isinstance(value, str) else "not a string"
    if fault is not None:
        raise LedgerError(
            f"{where}: {what} must be {SOURCE_PATH_DESCRIBED} — this one is {fault}. "
            f"The value is not reproduced here (R7)."
        )
    return value  # type: ignore[return-value]


def _require_distinct(material: frozenset[str], graders: frozenset[str], where: str) -> None:
    """⛔ Refuse a file declared both material and a test: it would be two entries."""
    both = sorted(material & graders)
    if both:
        raise LedgerError(
            f"{where}: {len(both)} file is declared both material and a test, starting "
            f"at '{both[0]}'. A file is one or the other, because the ledger records a "
            f"test file whole and scans material for the examples inside it."
        )


def _text(root: Path, path: str, where: str) -> str:
    """Read one declared file, naming the file rather than the machine (R7)."""
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise LedgerError(
            f"{where}: the file at '{path}' is not UTF-8 text, so it carries no fenced "
            f"example this scan can read. Declare it a test file, or leave it out of "
            f"the material the ledger walks."
        ) from None
    except OSError:
        raise LedgerError(
            f"{where}: the file at '{path}' could not be read, so the ledger cannot "
            f"account for what it carries. A declared file that is not there is a "
            f"declaration nobody has checked."
        ) from None
