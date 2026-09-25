r"""The draft's `include` and `exclude`: the units the record lists, and nothing it only links.

**What it does.** Turns the record's units into include patterns a person can
check, and names every material file those patterns would read that the
record does not list, for the draft to exclude.

**How you use it.** `proposal.draft` calls `patterns(inventory, record, heads)`,
which returns `(include, exclude)`.

**Depends on.** `inventory` and `record`. ⛔ Nothing source-specific (R1).

## ⛔ An include reads units, never the pages that only hold them

⚠️ **Measured, and the reason this module exists.** A course whose modules are
linked entries opening their own contents page keeps each page in the module's
directory beside its lessons, so a directory wildcard reads every contents page
as a unit, and the first `validate` reports one `included-unread` per module.
⭐ So a pattern may not match the record, nor the file any linked entry links
(`linked.split_linked`): where the directory wildcard would, it narrows to the stem
every unit in that directory begins with, up to a separator, and failing that
it lists the files.

⛔ **An entry above the record's first group label is not a unit** when the
record has labels: a link from the overview to a contributor's guide is not
material because it sits in the record. The adapter's filing refuses such an
entry, so the draft does not include it, and `survey` still names it.

## ⭐ One pattern for many uniform directories

Where every directory holding units at the root narrows to one and the same
pattern, and `*/` in front of it reads exactly the files the per-directory
patterns read, that one pattern is drafted instead. A person then reads one
line where there were one per module.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import PurePosixPath

from studyforge.skills.reconnaissance.inventory import Inventory
from studyforge.skills.reconnaissance.record import Record

#: Where a narrowed stem may end: the characters a name separates its words with.
SEPARATORS = "_-."


def patterns(
    inventory: Inventory, record: Record | None, heads: Iterable[str] = ()
) -> tuple[list[str], list[str]]:
    """Return what to read and what to leave out, as patterns a person can check.

    ⛔ **An include glob never matches the curriculum record**, nor a file a
    linked entry links. ⚠️ The record is still not *declared* anything here;
    what it is stays a person's question.
    """
    everything = {p.relative_to(inventory.root).as_posix() for p in inventory.material}
    if record is None:
        directories = sorted({PurePosixPath(where).parent.as_posix() for where in everything})
        return [f"{d}/*.md" if d != "." else "*.md" for d in directories], []
    avoid = {record.path.as_posix(), *heads}
    units = [
        entry.target
        for entry in record.entries
        if entry.target not in avoid and (entry.group is not None or not record.groups)
    ]
    found = _collapsed(_per_directory(units, avoid), everything)
    listed = set(units)
    # ⛔ Withheld only where an include would read it; the rest is `furniture`'s.
    return found, sorted(
        where
        for where in everything - listed - avoid
        if any(PurePosixPath(where).full_match(pattern) for pattern in found)
    )


def _per_directory(units: list[str], avoid: set[str]) -> list[str]:
    """One pattern per directory holding units, narrowed until it reads nothing in `avoid`."""
    by_directory: dict[str, list[PurePosixPath]] = {}
    for target in units:
        path = PurePosixPath(target)
        by_directory.setdefault(path.parent.as_posix(), []).append(path)
    found: set[str] = set()
    for directory, paths in by_directory.items():
        # ⚠️ Distinct files: a file cut into regions is listed once per region.
        found.update(_narrowed(directory, sorted(set(paths)), avoid))
    return sorted(found)


def _narrowed(directory: str, paths: list[PurePosixPath], avoid: set[str]) -> list[str]:
    """Return the directory wildcard, else the units' common stem, else each file by name."""
    suffixes = {path.suffix for path in paths}
    stem = os.path.commonprefix([path.name for path in paths])
    under = "" if directory == "." else f"{directory}/"
    tried = [f"{under}*{suffix}" for suffix in suffixes]
    if all(_clear(pattern, avoid) for pattern in tried):
        return tried
    if len(paths) < 2:
        # ⭐ One file shares a stem with nothing: it is named, not patterned.
        return [path.as_posix() for path in paths]
    # ⚠️ Only a stem that ends at a separator, `lesson_` or `part-`, and the
    # shortest one that reads nothing it must not: a stem cut inside a word or a
    # number, `0` of `01` and `02`, is a coincidence of today's names rather than
    # a naming rule, and a longer one restates the numbering the record keeps.
    for cut in (at + 1 for at, mark in enumerate(stem) if mark in SEPARATORS):
        narrowed = [f"{under}{stem[:cut]}*{suffix}" for suffix in suffixes]
        if all(_clear(pattern, avoid) for pattern in narrowed):
            return narrowed
    return [path.as_posix() for path in paths]


def _clear(pattern: str, avoid: set[str]) -> bool:
    """Whether `pattern` reads none of the paths it must not."""
    return not any(PurePosixPath(where).full_match(pattern) for where in avoid)


def _collapsed(found: list[str], everything: set[str]) -> list[str]:
    """One `*/` pattern for root directories sharing a narrowed pattern, where it reads the same."""
    tails: dict[str, list[str]] = {}
    for pattern in found:
        head, _, tail = pattern.partition("/")
        if tail and "/" not in tail and not any(mark in head for mark in "*?["):
            tails.setdefault(tail, []).append(pattern)
    out = set(found)
    for tail, grouped in tails.items():
        wide = f"*/{tail}"
        if len(grouped) < 2:
            continue
        narrow = {w for w in everything if any(PurePosixPath(w).full_match(p) for p in grouped)}
        if {w for w in everything if PurePosixPath(w).full_match(wide)} == narrow:
            out = (out - set(grouped)) | {wide}
    return sorted(out)
