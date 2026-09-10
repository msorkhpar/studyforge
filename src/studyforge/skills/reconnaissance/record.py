r"""The document that records the curriculum — the one thing worth finding first.

**What it does.** Finds the document that lists the material, works out which
region of it is the curriculum, reads the entries in the order it states them,
and recovers the grouping it expresses.

**How you use it.** `find(inventory)` returns a `Record` or `None`;
`Record.entries` is the reading order, `Record.groups` the containers.

**Depends on.** `inventory`, `report`.

## ⭐ Why this module exists at all

⛔ **Reading filenames is derivation; reading this document is a record** (§6:
an address is *recorded, never derived*). Every measured corpus puts its
hierarchy in a document and none of them puts it in the filesystem — a flat
directory says nothing about groups, and a directory per module says nothing
about the sections that group them.

⭐ **None of them can be read correctly from its tree.** That is not a quirk of
a few repositories; it is what hand-written curricula do. ⛔ `SKILL.md`,
appendix **A1**, holds the corpora and the counts, and is the only copy.

## ⛔ Role is positional, not syntactic

⚠️ **Two measured corpora set this trap in opposite directions**, which is why
this module keys on *position in a run of entries* rather than on Markdown
syntax. One writes its containers as headings, in a document whose headings
are mostly not containers — a heading-keyed parser emits several times too
many. The other writes its sections as bare numbered lines, with no heading
anywhere in the region — the same parser emits none. ⛔ **Neither raises.**
`SKILL.md` step 3 holds both, with their counts.

⭐ So a group label is *"a line inside the curriculum region that introduces a
run of entries and is not itself an entry"*. Both corpora fall out of that one
rule, and neither falls out of a syntax rule.

## ⛔ The region, not the file

⚠️ In one measured corpus, over half of the curriculum document is a structural
copy of another document — a run of headings digest-identical to that
document's whole heading tree (`SKILL.md` step 3). ⛔ And the file cannot be
excluded, because it is the only record of that corpus's addresses, titles,
ordinals and grouping.

So the curriculum is a **region**: it starts at the first entry and ends where
the entries stop. Everything outside it is somebody else's document.

## ⚠️ Entries arrive in more than one shape, and the odd ones are silent

**Measured:** every corpus writes a handful of its entries in a form other than
its own majority form — a heading where the rest are list items, an ordinal
outside the link where the rest carry it inside. ⛔ A parser written for the
majority form reads the wrong number and **raises nothing**. `SKILL.md`,
appendix **A2**, holds the forms and their counts. So every form is read, and
⭐ the *disagreement between forms is itself reported*, because it is the tell
that a hand-maintained document has drifted.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from studyforge.skills.reconnaissance.inventory import Inventory
from studyforge.skills.reconnaissance.report import Observation, Uncertainty

#: A Markdown link to a file: `[title](target)`. ⚠️ Deliberately permissive
#: about the target — whether it names material is decided by comparing it with
#: the inventory, not by a pattern.
LINK = re.compile(r"\[(?P<title>[^\]]*)\]\((?P<target>[^)\s]+)\)")

#: A leading ordinal on an entry line, in either place it is written:
#: `- [1.1. Title](x)` puts it inside the link text, `- 1.5. [Title](x)` outside.
ORDINAL = re.compile(r"^(?P<number>\d+(?:\.\d+)*)\.?\s+(?P<rest>.*)$")

#: A line that carries no link and no list marker — the shape a group label
#: takes when it is not a heading. ⚠️ Both are accepted; see the module
#: docstring on why syntax is not the test.
HEADING = re.compile(r"^\s{0,3}(?P<hashes>#{1,6})\s+(?P<text>.+?)\s*#*\s*$")
LIST_MARKER = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")

#: A bullet, and **only** a bullet. ⛔ Not `LIST_MARKER`: stripping a numbered
#: marker would eat the ordinal, and `1. [Title](x)` — where the ordinal *is*
#: the list marker — is the majority form in all three measured corpora.
BULLET_MARKER = re.compile(r"^\s*[-*+]\s+")

#: Markdown emphasis wrapped around a whole title: `**A Title**`. ⚠️ It is
#: presentation, not name — measured, well over half the recorded titles of one
#: corpus carry it (`SKILL.md`, appendix **A2**) — and a manifest that kept it
#: would show a reader the asterisks.
EMPHASIS = re.compile(r"^(?P<marks>\*{1,3}|_{1,3})(?P<text>.+?)(?P=marks)$")
FENCE = re.compile(r"^\s{0,3}(?:`{3,}|~{3,})")


@dataclass(frozen=True, slots=True)
class Entry:
    """One unit the record names: where it is, what it is called, and in what order."""

    target: str
    title: str
    ordinal: str | None
    line: int
    group: str | None


@dataclass
class Record:
    """The curriculum document, and what it says."""

    path: Path
    first_line: int
    last_line: int
    entries: list[Entry]
    groups: list[str]
    forms: dict[str, int]
    title: str = ""

    @property
    def order(self) -> list[str]:
        """The reading order the document states, as link targets."""
        return [entry.target for entry in self.entries]


def find(inventory: Inventory) -> Record | None:
    """Return the document that records the most of this corpus's material.

    ⛔ Chosen by **how much of the material it links to**, never by its name.
    `README.md` is the usual answer and `SUMMARY.md`, `index.md` and
    `curriculum.md` are all real conventions; keying on a filename list would
    be an open set dressed as a closed one.
    """
    targets = {path.relative_to(inventory.root).as_posix() for path in inventory.material}
    best: Record | None = None
    for candidate in inventory.material:
        record = read(candidate, inventory.root, targets)
        if record is None:
            continue
        if best is None or len(record.entries) > len(best.entries):
            best = record
    return best


def read(path: Path, root: Path, targets: set[str]) -> Record | None:
    """Read one candidate document, or return `None` if it records nothing."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError, UnicodeDecodeError:  # pragma: no cover - reported by the walk
        return None
    here = path.parent.relative_to(root).as_posix()
    found = list(_entries(lines, here, targets, path.relative_to(root).as_posix()))
    if not found:
        return None
    entries = found
    # ⛔ Imported here rather than at module scope: `grouping` needs this
    # module's `Entry` and its line patterns, so a top-level import would be a
    # cycle. ⚠️ One lazy import at one call site, stated, beats moving the
    # patterns to a third module nobody would look in.
    from studyforge.skills.reconnaissance.grouping import forms, grouping

    groups, labelled = grouping(lines, entries)
    return Record(
        path=path.relative_to(root),
        first_line=entries[0].line,
        last_line=entries[-1].line,
        entries=labelled,
        groups=groups,
        forms=forms(lines, entries),
        title=_document_title(lines),
    )


def _document_title(lines) -> str:
    """Return the record's own first heading — what the corpus calls itself."""
    for line in lines:
        heading = HEADING.match(line)
        if heading is not None:
            return heading.group("text").strip()
    return ""


def _entries(lines, here, targets, own) -> Iterator[Entry]:
    """Every link on a non-fenced line whose target is a material file."""
    fenced = False
    for number, line in enumerate(lines, 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        for match in LINK.finditer(line):
            target = _resolve(here, match.group("target"))
            if target not in targets or target == own:
                continue
            ordinal, title = _split(line, match.group("title"))
            yield Entry(target=target, title=title, ordinal=ordinal, line=number, group=None)


def _resolve(here: str, target: str) -> str:
    """Resolve a link relative to the document that carries it."""
    target = target.split("#", 1)[0]
    if not target:
        return ""
    parts = [] if not here or here == "." else here.split("/")
    for part in target.split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part not in ("", "."):
            parts.append(part)
    return "/".join(parts)


def _split(line: str, title: str) -> tuple[str | None, str]:
    """Return `(ordinal, title)` with the ordinal taken from wherever it is written.

    ⚠️ **Three places.** `- [1.1. Title](x)` carries it inside the link text;
    `- 1.5. [Title](x)` carries it outside, after a bullet; and `1. [Title](x)`
    carries it *as* the list marker. A reader written for one form silently
    drops the entries written in the others, and ⛔ **all three occur in real
    material** — the third in every measured corpus. `SKILL.md`, appendix
    **A2**, holds the counts.
    """
    inside = ORDINAL.match(title.strip())
    if inside is not None:
        return inside.group("number"), _plain(inside.group("rest"))
    outside = ORDINAL.match(BULLET_MARKER.sub("", line).strip())
    if outside is not None and outside.group("rest").lstrip().startswith("["):
        return outside.group("number"), _plain(title)
    return None, _plain(title)


def _plain(title: str) -> str:
    """Strip emphasis that wraps a whole title, leaving the name the author wrote.

    ⛔ Only when it wraps the **whole** title. `**Basic** setup` keeps its
    marks: removing emphasis from the middle of a title would be editing the
    author's text rather than reading it.
    """
    title = title.strip()
    while True:
        match = EMPHASIS.match(title)
        if match is None:
            return title
        title = match.group("text").strip()


def observe(record: Record | None, inventory: Inventory) -> Iterator[Observation | Uncertainty]:
    """Report what the record says, and every way it did not settle something."""
    if record is None:
        yield Uncertainty(
            question="what is the reading order, and how is the material grouped?",
            why=(
                f"no document in this source links to its material; "
                f"{len(inventory.material)} file(s) were found and nothing lists them"
            ),
            settles_it=(
                "point at the document that records the curriculum, or confirm "
                "that filename order IS reading order — this skill will not "
                "assume it, because a filename sort places 37 of 38 units at the "
                "wrong index in one measured corpus and raises nothing"
            ),
        )
        return
    yield Observation("curriculum recorded in", record.path.as_posix())
    yield Observation("region of that document", f"lines {record.first_line}-{record.last_line}")
    yield Observation("units it names, in order", str(len(record.entries)))
    yield Observation("groups it expresses", f"{len(record.groups)} {record.groups[:4]}")
    yield Observation(
        "entry shapes", ", ".join(f"{n} {shape}" for shape, n in sorted(record.forms.items()))
    )
    yield from _drift(record, inventory)


def _drift(record: Record, inventory: Inventory) -> Iterator[Observation | Uncertainty]:
    """Report the three ways a hand-maintained record disagrees with its corpus."""
    if len(record.forms) > 1:
        minority = min(record.forms.values())
        yield Uncertainty(
            question="are the minority-shaped entries really units?",
            why=(
                f"the record writes its entries in {len(record.forms)} shapes "
                f"({record.forms}); {minority} are written differently from the rest"
            ),
            settles_it=(
                "confirm the odd ones are units. A reader written for the "
                "majority shape drops them and raises nothing — measured in two "
                "corpora, at 2 of 38 and 6 of 211"
            ),
        )
    listed = set(record.order)
    everything = {p.relative_to(inventory.root).as_posix() for p in inventory.material}
    unlisted = sorted(everything - listed - {record.path.as_posix()})
    if unlisted:
        yield Uncertainty(
            question=f"are these {len(unlisted)} material file(s) part of the corpus?",
            why=f"they are not named by {record.path.as_posix()}: {unlisted[:5]}",
            settles_it=(
                "exclude them in the manifest, or add them to the record. ⚠️ A "
                "whole-series aggregate looks exactly like this and must be "
                "excluded; so does a chapter somebody forgot to link, and that "
                "must not be"
            ),
        )
