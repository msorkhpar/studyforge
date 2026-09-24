r"""File a corpus's units from its manifest's `curriculum`, and refuse a tree that disagrees.

**What it does.** Reads the document `corpus.json`'s `curriculum.record` names,
files each unit it lists under the address its group is declared at, and
checks every declared filename prefix against that filing in both directions
(`W340`). ⭐ `counted` is the second reading: the units each prefix's files
number on disk, taken without the record.

**How you use it.** From an adapter's `read.py`, which the scaffold writes this
way when the manifest declares its groups:

    from studyforge.corpus.manifest import load
    from studyforge.skills.adapter.curriculum import counted, filed

    manifest = load(root / "corpus.json")
    for group in filed(root, manifest):   # CurriculumDisagrees, or the filing
        group.address, group.label, group.units
    counted(root, manifest)               # {address key: n}, or None

**Depends on.** `corpus.manifest` for the declaration and the content policy,
`corpus.container` for `Unit`, reconnaissance's `record.read` for the record,
and `validate.source.source_files` for which files exist, deferred (`_included`).
⛔ Nothing source-specific (R1): every fact arrives in `corpus.json`.

## ⭐ One reader detects and files, so the two are one act (`F6`)

⚠️ The record is read with **the reader reconnaissance proposed the
declaration from** — positional roles, every entry shape, the region and not
the file. A second reader here could disagree with the survey about a record
both of them call correct, and nobody would learn which one filed the corpus.
⛔ **The declaration is then held to the reading exactly**: the record's groups
must be the declared labels, in the declared order, or this refuses.

## ⛔ A prefix never files a unit; it can only disagree

The record files every unit (§6). A declared prefix is a second partition of
the same files (`W471/1`), and this refuses when the two differ:

- a unit filed under a group whose prefix its name does not carry;
- a unit whose name carries another group's prefix;
- an included file whose name carries a group's prefix and that the record
  never files there — the chapter somebody forgot to list.

⭐ Every disagreement is named in one refusal, by corpus path and address,
never by a title (R7): the refusal is pasted before it is read.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from studyforge.address import Address
from studyforge.corpus.container import Unit
from studyforge.corpus.manifest import Classification, Manifest, prefix_of
from studyforge.skills.reconnaissance import read


class CurriculumDisagrees(ValueError):
    """The tree does not say what `corpus.json`'s `curriculum` declares.

    ⛔ Names corpus paths, addresses and counts — never a title or a value from
    outside the corpus (R7).
    """


@dataclass(frozen=True, slots=True)
class Filed:
    """One declared group, and the units the record files under it, in its order."""

    address: Address
    label: str
    units: tuple[Unit, ...]


def filed(root: Path, manifest: Manifest, *, included: set[str] | None = None) -> tuple[Filed, ...]:
    """Return every declared group with its units, or refuse naming every disagreement.

    ⭐ `included` is the root-relative files the content policy includes, for a
    caller that already enumerated them (`validate`); absent, they are read here.
    """
    curriculum = _declared(manifest)
    root = Path(root)
    included = _included(root, manifest) if included is None else included
    record = _record(root, curriculum.record, included)
    labels = [each.label for each in curriculum.containers]
    if record.groups != labels:
        raise CurriculumDisagrees(
            f"{curriculum.record} groups its units under {len(record.groups)} label(s) and "
            f"corpus.json declares {len(labels)}; the labels must be the record's own, in "
            f"its order. Settle it by declaring the labels as the record writes them, or "
            f"by correcting the record"
        )
    stray = [entry.target for entry in record.entries if entry.group is None]
    if stray:
        raise CurriculumDisagrees(
            f"{curriculum.record} lists {sorted(stray)} above its first group label, so "
            f"no declared group files them. Settle it by giving them a label"
        )
    found = tuple(
        Filed(
            address=declared.address,
            label=declared.label,
            units=_units(record, declared.label, declared.address),
        )
        for declared in curriculum.containers
    )
    problems = _cross_checked(found, curriculum.prefixes, included)
    if problems:
        raise CurriculumDisagrees(
            f"corpus.json declares filename prefixes as a cross-check, and "
            f"{len(problems)} file(s) disagree with {curriculum.record}: "
            f"{'; '.join(problems)}. The record files a unit and a prefix never does "
            f"(§6), so settle it by correcting the record or the declared prefix"
        )
    return found


def counted(root: Path, manifest: Manifest) -> dict[str, int] | None:
    """Return `{address key: units}` counted from the names on disk, or `None`.

    ⭐ **The count the record did not produce**, which is what an adapter's
    `expected_units` has to be: every included file carrying a group's prefix.
    ⚠️ `None` unless every declared group has a prefix, because a group without
    one has no second reading to give.
    """
    curriculum = _declared(manifest)
    if any(each.prefix is None for each in curriculum.containers):
        return None
    counts = {each.address.key: 0 for each in curriculum.containers}
    for path in _included(Path(root), manifest):
        declared = curriculum.prefixes.get(prefix_of(path))
        if declared is not None:
            counts[declared.address.key] += 1
    return counts


def _declared(manifest: Manifest):
    """Return the declaration, or refuse naming what is missing from it."""
    curriculum = manifest.curriculum
    if curriculum is None or not curriculum.containers:
        raise CurriculumDisagrees(
            "corpus.json declares no curriculum.containers, so there is nothing to file "
            "from; declare the record's groups with their addresses (corpus_api 7), or "
            "read the record in read.py"
        )
    return curriculum


def _record(root: Path, where: str, included: set[str]):
    """Read the declared record, refusing one that is absent or lists no material."""
    path = root / where
    if not path.is_file():
        raise CurriculumDisagrees(
            f"corpus.json declares the curriculum is recorded in {where}, and it is not "
            f"there. Restore it, or declare where the curriculum is recorded now"
        )
    record = read(path, root, included)
    if record is None:
        raise CurriculumDisagrees(
            f"{where} links to none of the files corpus.json includes, so it records no "
            f"curriculum. Declare the document that does"
        )
    return record


def _units(record, label: str, address: Address) -> tuple[Unit, ...]:
    """Return the units the record lists under `label`, numbered by their position in it.

    ⛔ **A written ordinal must agree with the position**: it is the reading
    order, so a gap or a repeat is a decision about the order and not a typo.
    """
    units = []
    for position, entry in enumerate((e for e in record.entries if e.group == label), start=1):
        written = entry.ordinal.rsplit(".", 1)[-1] if entry.ordinal else None
        if written is not None and int(written) != position:
            raise CurriculumDisagrees(
                f"{record.path.as_posix()} numbers entry {position} of {address.key} as "
                f"{entry.ordinal}; the ordinal is the reading order, so the record is "
                f"corrected rather than the gap smoothed over"
            )
        units.append(
            Unit(
                n=position,
                title=entry.title,
                practices=0,
                origin=entry.target,
                origin_section=entry.section,
            )
        )
    if not units:
        raise CurriculumDisagrees(
            f"the record lists no unit under the group declared at {address.key}; an "
            f"empty container reaches the contents page as an empty row"
        )
    return tuple(units)


def _cross_checked(found, prefixes, included: set[str]) -> list[str]:
    """Every way the declared prefixes and the record's filing disagree."""
    if not prefixes:
        return []
    problems = []
    origins: dict[str, set[str]] = {}
    for group in found:
        declared = next((p for p, d in prefixes.items() if d.address == group.address), None)
        mine = origins.setdefault(group.address.key, set())
        for unit in group.units:
            mine.add(unit.origin)
            carried = prefix_of(unit.origin)
            if declared is not None and carried != declared:
                problems.append(
                    f"{unit.origin} is filed at {group.address.key}, not named {declared!r}"
                )
            elif carried in prefixes and prefixes[carried].address != group.address:
                owner = prefixes[carried].address.key
                problems.append(f"{unit.origin} is named for {owner}, filed at {group.address.key}")
    for path in sorted(included):
        declared = prefixes.get(prefix_of(path))
        if declared is not None and path not in origins.get(declared.address.key, ()):
            problems.append(f"{path} is named for {declared.address.key} and not filed there")
    return sorted(set(problems))


def _included(root: Path, manifest: Manifest) -> set[str]:
    """Every file on disk the manifest's content policy includes, root-relative.

    ⭐ **The population `validate` judges**: `validate.source.source_files`, which
    reads the repository's own ignore rules and sets aside what a build writes.
    So the adapter's filing and `validate`'s check can never disagree about which
    files exist. ⚠️ Imported here rather than at module scope: `validate` reads
    this package's `Layout`, and a top-level import would be a cycle.
    """
    from studyforge.validate.source import source_files

    included = set()
    for path in source_files(root).files:
        relative = path.relative_to(root).as_posix()
        if manifest.content.classify(relative) is Classification.INCLUDED:
            included.add(relative)
    return included
