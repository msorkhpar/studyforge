r"""The `content.not_material` globs a draft proposes, with every reason left open.

**What it does.** Reads the files `studyforge validate` will classify in a
source root and proposes one `not_material` glob for every file the draft
neither includes nor excludes, so a person types the reasons and never the
globs (R19, `W249`).

**How you use it.** `propose(root, include, exclude)` returns a `Furniture`:
its `entries` (each `{"glob": ..., "why": None}`), how many files it judged,
whether git's ignore rules were read, the globs the root's manifest already
declares, how many files those cover, and `stands_down`: why the proposal
cannot be read as complete, by name, or `None` (`W269`).

**Depends on.** `studyforge.validate.source.source_files` for the population,
`studyforge.skills.onboarding.RECORD_FILE` for what onboarding wrote, and
`studyforge.corpus.manifest.MANIFEST_FILENAME` for what the corpus declares.
⛔ Nothing source-specific (R1): no file name is special here.

## ⛔ The population is validate's walk, never a list here

What `validate` will call unclassified is exactly what a draft must propose
for. So the files come from `source_files`, the walk `check_unclassified`
uses: the framework's own directories and generated output are skipped, and
so is whatever the repository's git ignore rules declare.

## ⭐ Which state a file lands in follows SF-02's own semantics

An exclusion is prose an `include` would read and deliberately does not. So
only a file an include pattern matches can be withheld. Every other file no
pattern reads was never going to be read, and it is proposed here. A root
record, a licence and an ignore file all fall out of that one rule.

## ⛔ Two shapes, both legal under rule 1a

A glob is `D/**` for the shallowest directory `D` holding nothing included,
excluded or written by onboarding. Otherwise it is the file's exact path.

## ⛔ Onboarding's footprint is never proposed

Paths listed in onboarding's record are declared by `SK-07`'s own generated
globs. A drafted glob equal to one of those is refused by `promote`, never
resolved by precedence (`W239`), so a re-survey of an onboarded corpus must
not propose them. ⚠️ An unreadable record reads as no footprint, and any
collision that follows is refused by `promote` by name. ⛔ The record is a list
of paths, so it is gated before a field is read (R7, W7), and a leak raises.

## ⛔ A file a declared glob covers is never re-proposed (`W269`, `INT-10/2`)

A re-survey reads the root's own manifest. A file one of its `not_material`
globs covers, by the manifest's own match, is neither proposed nor swept by a
directory glob: it holds its directory, as a read file does. ⚠️ An unreadable
manifest reads as no declaration, and it is gated before a field is read (R7).

## ⛔ A proposal that stands down says so (`W269`, `INT-10/1`)

Judging no file, or judging without git's ignore rules, is named in
`stands_down` whatever was proposed. ⚠️ A root inside another repository's
ignored directory is answered for by THAT repository, so it judges no file:
the silence this names.

## ⛔ The reasons are a person's (`W240/3`)

Every `why` is `None`. SF-02 refuses it, and `promote` pairs it from the
reasons a person gives. A generated reason would be an audit nobody performed.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.archive.scrub import assert_clean
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.skills.onboarding import RECORD_FILE
from studyforge.validate.source import source_files

#: What a proposed entry carries where its reason goes. ⛔ Never a string:
#: SF-02 refuses `None`, so an unsettled draft cannot pass as settled.
OPEN_REASON = None


@dataclass(frozen=True, slots=True)
class Furniture:
    """The proposed `not_material` entries, and the population they were judged over."""

    entries: tuple[dict[str, str | None], ...]
    #: ⭐ Printed with the proposal: an empty list over zero files is not a result.
    judged: int
    #: False where the root is not a git working tree, so no ignore rule was read.
    consulted: bool
    #: ⭐ `W269`: the `not_material` globs the root's own manifest already declares.
    declared: tuple[str, ...] = ()
    #: ⭐ `W269`: files a declared glob covers, and so never re-proposed.
    covered: int = 0

    @property
    def globs(self) -> list[str]:
        """The proposed globs, in the order they are drafted."""
        return [str(entry["glob"]) for entry in self.entries]

    @property
    def stands_down(self) -> str | None:
        """Name why this proposal cannot be read as complete, or return `None` (`W269`)."""
        if not self.judged and self.consulted:
            return (
                "it judged no file: git's ignore rules, answered by the working tree that "
                "holds this root, declare every file output, which is how a root inside "
                "another repository's ignored directory reads"
            )
        if not self.judged:
            return "it judged no file, and git's ignore rules were not read"
        if not self.consulted:
            return (
                "git's ignore rules were not read, as this root is not a git working tree, "
                "so generated output was judged as if it were material"
            )
        return None


def propose(root: Path | str, include: Sequence[str], exclude: Iterable[str]) -> Furniture:
    """Return a glob for every file validate will classify that the draft reads nowhere."""
    root = Path(root)
    scan = source_files(root)
    seen = sorted(path.relative_to(root).as_posix() for path in scan.files)
    withheld = set(exclude)
    read = {
        where
        for where in seen
        if where in withheld or any(PurePosixPath(where).full_match(g) for g in include)
    }
    declared = _declared(root)
    covered = {where for where in seen if any(PurePosixPath(where).full_match(g) for g in declared)}
    occupied = read | covered | _footprint(root)
    held = {parent.as_posix() for where in occupied for parent in PurePosixPath(where).parents}
    left = [where for where in seen if where not in occupied]
    globs = sorted({_glob(where, held) for where in left})
    return Furniture(
        entries=tuple({"glob": glob, "why": OPEN_REASON} for glob in globs),
        judged=len(seen),
        consulted=scan.consulted,
        declared=declared,
        covered=len(covered),
    )


def _glob(where: str, held: set[str]) -> str:
    """Return `D/**` for the shallowest directory above `where` holding nothing read."""
    parts = PurePosixPath(where).parts
    for depth in range(1, len(parts)):
        directory = "/".join(parts[:depth])
        if directory not in held:
            return f"{directory}/**"
    return where


def _footprint(root: Path) -> frozenset[str]:
    """Every path onboarding's record says it wrote, or none if there is no readable record."""
    try:
        document = json.loads((root / RECORD_FILE).read_text(encoding="utf-8"))
    except OSError, ValueError:
        return frozenset()
    assert_clean(document, RECORD_FILE)
    files = document.get("files") if isinstance(document, dict) else None
    if not isinstance(files, list):
        return frozenset()
    return frozenset(
        entry["where"]
        for entry in files
        if isinstance(entry, dict) and isinstance(entry.get("where"), str)
    )


def _declared(root: Path) -> tuple[str, ...]:
    """Every `not_material` glob the root's manifest declares, or none if it cannot be read."""
    try:
        document = json.loads((root / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    except OSError, ValueError:
        return ()
    assert_clean(document, MANIFEST_FILENAME)
    content = document.get("content") if isinstance(document, dict) else None
    entries = content.get("not_material") if isinstance(content, dict) else None
    if not isinstance(entries, list):
        return ()
    return tuple(
        entry["glob"]
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("glob"), str)
    )
