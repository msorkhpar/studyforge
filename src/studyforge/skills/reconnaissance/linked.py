r"""A level the record writes as linked entries: each opens a container, not a unit.

**What it does.** Finds, beneath a record's group labels, the list entries that
link a container's own page and hold that container's units indented beneath
them, and hands back those entries apart from the units.

**How you use it.** `split_linked(lines, record_path, entries, labels)` returns a
`Linked` — the heads, in record order, and the entries left as units — or
raises `NotLinked` naming what does not fit.

**Depends on.** `record`'s line patterns and `Entry`. ⛔ Nothing
source-specific (R1): the shape is positional, as a group label's is.

## ⭐ What a linked entry is, by position

⚠️ **Measured, and the reason this module exists.** A course writes its
sections as bare numbered lines, and under each one every module is a list
entry linking the module's own contents page, with that module's units
indented beneath it. The group rule (`grouping.choose`) reads the sections as
the labels, which is right, and then files every module's units under its
section, which loses a level.

⭐ **So a head is a linked list entry at the shallowest indent of the run**:
beneath a label, every link-carrying list line at the least indent the
curriculum uses opens a container, and every entry indented deeper beneath it
is one of that container's units, in the record's order. An entry nested
deeper still is a unit of the same container, in its place.

⛔ **The record either has this shape everywhere or it does not have it**:
an entry above a group's first head, a head with no unit beneath it, or no
entry deeper than the heads at all is `NotLinked`, naming the record line.
⭐ A head is read the same whether or not its page is material: a survey reads
every Markdown file as material and an adapter reads only what `corpus.json`
includes, and both must find the same heads.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from studyforge.skills.reconnaissance.record import (
    FENCE,
    LINK,
    LIST_MARKER,
    Entry,
    _resolve,
    _split,
)


class NotLinked(ValueError):
    """The record does not open containers with linked entries, and where it shows.

    ⛔ Names a record line and a count, never a title (R7).
    """


@dataclass(frozen=True, slots=True)
class Head:
    """One linked entry: the container it opens, as the record writes it."""

    #: The record line, 1-based.
    line: int
    #: The linked file, root-relative, exactly as the record resolves it.
    target: str
    title: str
    ordinal: str | None
    #: The label the head sits beneath.
    group: str

    @property
    def directory(self) -> str:
        """The name of the directory holding the linked file: the address's last segment."""
        return PurePosixPath(self.target).parent.name


@dataclass(frozen=True, slots=True)
class Linked:
    """The heads, and each one's units in the record's order."""

    heads: tuple[Head, ...]
    #: Each head's units, keyed by the head's record line.
    units: dict[int, tuple[Entry, ...]]


def split_linked(
    lines: list[str], record: str, entries: list[Entry], labels: list[tuple[int, str]]
) -> Linked:
    """Return the heads beneath `labels` and the units each one holds, or refuse.

    `record` is the record's root-relative path; `entries` its entries with
    their groups assigned, and `labels` its group labels with their lines.
    """
    if not labels or not entries:
        raise NotLinked(f"{record} has no group labels with entries beneath them")
    first, last = labels[0][0], max(entry.line for entry in entries)
    candidates = list(_linked_lines(lines, record, first, last))
    if not candidates:
        raise NotLinked(f"{record} has no linked list entry beneath its first group label")
    indent = min(depth for _, depth, _ in candidates)
    heads = [
        _head(lines, record, number, target, labels)
        for number, depth, target in candidates
        if depth == indent
    ]
    at = {head.line for head in heads}
    units: dict[int, list[Entry]] = {head.line: [] for head in heads}
    for entry in entries:
        if entry.line in at or entry.line < first:
            continue
        owner = next((h for h in reversed(heads) if h.line < entry.line), None)
        if owner is None or _label_between(labels, owner.line, entry.line):
            raise NotLinked(
                f"{record} line {entry.line} is an entry beneath a group label and above "
                f"any linked entry, so no container holds it"
            )
        if _indent(lines[entry.line - 1]) <= indent:
            raise NotLinked(
                f"{record} line {entry.line} is an entry at the linked entries' own indent"
            )
        units[owner.line].append(entry)
    empty = [head.line for head in heads if not units[head.line]]
    if empty:
        raise NotLinked(
            f"{record} has {len(empty)} linked entr(ies) with no unit indented beneath them, "
            f"first at line {empty[0]}"
        )
    return Linked(tuple(heads), {line: tuple(found) for line, found in units.items()})


def _linked_lines(lines, record: str, first: int, last: int):
    """Every list line from the first label to the last entry that links a file."""
    here = PurePosixPath(record).parent.as_posix()
    fenced = False
    for number in range(1, last + 1):
        line = lines[number - 1]
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced or number <= first or not LIST_MARKER.match(line):
            continue
        link = LINK.search(line)
        target = _resolve(here, link.group("target")) if link is not None else ""
        if target and "://" not in link.group("target"):
            yield number, _indent(line), target


def _head(lines, record: str, number: int, target: str, labels) -> Head:
    """Read one head: its title and ordinal as an entry's are read, and its label."""
    line = lines[number - 1]
    ordinal, title = _split(line, LINK.search(line).group("title"))
    group = next(text for at, text in reversed(labels) if at < number)
    if not PurePosixPath(target).parent.name:
        raise NotLinked(
            f"{record} line {number} links a file at the corpus root, so no directory "
            f"name records the container's address"
        )
    return Head(number, target, title, ordinal, group)


def _label_between(labels, above: int, below: int) -> bool:
    """Whether a group label sits between two record lines."""
    return any(above < at < below for at, _ in labels)


def _indent(line: str) -> int:
    """How far a line is indented."""
    return len(line) - len(line.lstrip())
