r"""File a corpus's units from its manifest's `curriculum`, and refuse a tree that disagrees.

**What it does.** Reads the document `corpus.json`'s `curriculum.record` names,
files each unit it lists under the address its group is declared at, and
checks every declared filename prefix against that filing in both directions
⭐ `counted` is the second reading: the units each prefix's files
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

## ⭐ One reader detects and files, so the two are one act

⚠️ The record is read with **the reader reconnaissance proposed the
declaration from** — positional roles, every entry shape, the region and not
the file. A second reader here could disagree with the survey about a record
both of them call correct, and nobody would learn which one filed the corpus.
⛔ **The declaration is then held to the reading exactly**: the record's groups
must be the declared labels, in the declared order, or this refuses.

## ⛔ A prefix never files a unit; it can only disagree

The record files every unit (§6). A declared prefix is a second partition of
the same files, and this refuses when the two differ:

- a unit filed under a group whose prefix its name does not carry;
- a unit whose name carries another group's prefix;
- an included file whose name carries a group's prefix and that the record
  never files there — the chapter somebody forgot to list.

⭐ Every disagreement is named in one refusal, by corpus path and address,
never by a title (R7): the refusal is pasted before it is read.

## ⭐ A linked level: one container per linked entry, beneath its group

Where `curriculum.linked` names the last level, each declared group is a label
one level up, and each list entry beneath it that links a file opens one
container of the last level (`reconnaissance.linked`). Its address is the
group's followed by the name of the directory holding that file, its titles are
the label's and the entry's, its `origin` is the linked file, and its units are
the entries indented beneath it. ⭐ Each unit keeps the record's written
ordinal as its `label`, so an entry nested under another unit still shows
where it sits. ⭐ `counted` then counts the included files under each linked
file's directory, which is a reading of the tree the record did not make.

## ⛔ A written ordinal is its place among its siblings

An entry's ordinal counts the entries at its own depth under the same parent,
so `2.3` is the third entry after `2.1` and `2.2`, and `2.2.1` the first
beneath `2.2`. ⭐ For a group whose ordinals all have one depth that is exactly
its position, the rule every group was held to before nesting was read.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.address import Address, AddressError
from studyforge.corpus.container import Unit
from studyforge.corpus.manifest import Classification, Manifest, prefix_of


class CurriculumDisagrees(ValueError):
    """The tree does not say what `corpus.json`'s `curriculum` declares.

    ⛔ Names corpus paths, addresses and counts — never a title or a value from
    outside the corpus (R7).
    """


@dataclass(frozen=True, slots=True)
class Filed:
    """One container the record files, and its units in the record's order."""

    address: Address
    #: The declared group's label, as the record writes it.
    label: str
    units: tuple[Unit, ...]
    #: One title per level, the container's `titles`. ⭐ `(label,)` at depth 1.
    titles: tuple[str, ...] = ()
    #: The file the container was read from, root-relative: the record, or the
    #: file a linked entry links.
    origin: str | None = None


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
    if curriculum.linked:
        return _linked(root, curriculum, record)
    found = tuple(
        Filed(
            address=declared.address,
            label=declared.label,
            units=_units(
                [e for e in record.entries if e.group == declared.label],
                declared.address,
                record.path.as_posix(),
            ),
            titles=(declared.label,),
            origin=curriculum.record,
        )
        for declared in curriculum.containers
    )
    problems = _cross_checked(found, curriculum.prefixes, included)
    if problems:
        raise CurriculumDisagrees(
            f"corpus.json declares filename prefixes as a cross-check, and "
            f"{len(problems)} file(s) disagree with {curriculum.record}: "
            f"{'; '.join(problems)}. The record files every unit and a prefix only checks "
            f"it, so settle it by correcting the record or the declared prefix"
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
    if curriculum.linked:
        return _counted_linked(Path(root), manifest)
    if any(each.prefix is None for each in curriculum.containers):
        return None
    counts = {each.address.key: 0 for each in curriculum.containers}
    for path in _included(Path(root), manifest):
        declared = curriculum.prefixes.get(prefix_of(path))
        if declared is not None:
            counts[declared.address.key] += 1
    return counts


def _linked(root: Path, curriculum, record) -> tuple[Filed, ...]:
    """File one container per linked entry beneath each declared group, or refuse.

    ⭐ The address is the group's, followed by the name of the directory the
    linked file sits in: a name the record writes, so it is recorded (§6).
    """
    # ⚠️ Deferred, as `_record` defers the reader, for the same cycle.
    from studyforge.skills.reconnaissance import NotLinked, split_linked

    lines = (root / curriculum.record).read_text(encoding="utf-8").splitlines()
    try:
        linked = split_linked(lines, curriculum.record, record.entries, record.labels)
    except NotLinked as refused:
        raise CurriculumDisagrees(
            f"corpus.json declares curriculum.linked, and in {curriculum.record}, {refused}. "
            f"Settle it by correcting the record, or by dropping 'linked'"
        ) from None
    by_label = {declared.label: declared for declared in curriculum.containers}
    found = []
    for head in linked.heads:
        declared = by_label[head.group]
        try:
            address = Address((*declared.address.segments, head.directory))
        except AddressError:
            raise CurriculumDisagrees(
                f"{curriculum.record} line {head.line} links {head.target}, and the name of "
                f"the directory holding it is not an address segment. Settle it by naming "
                f"the directory as a slug"
            ) from None
        found.append(
            Filed(
                address=address,
                label=declared.label,
                units=_units(
                    list(linked.units[head.line]), address, curriculum.record, labelled=True
                ),
                titles=(declared.label, head.title),
                origin=head.target,
            )
        )
    keys = [each.address.key for each in found]
    repeated = sorted({key for key in keys if keys.count(key) > 1})
    if repeated:
        raise CurriculumDisagrees(
            f"{curriculum.record} links more than one container's page from one directory, "
            f"so {repeated} would be filed twice. Settle it by giving each its own directory"
        )
    opened = {head.group for head in linked.heads}
    empty = [each.address.key for each in curriculum.containers if each.label not in opened]
    if empty:
        raise CurriculumDisagrees(
            f"the record opens no linked entry beneath the group(s) declared at {empty}"
        )
    return tuple(found)


def _counted_linked(root: Path, manifest: Manifest) -> dict[str, int]:
    """Count the included files under each linked file's directory, without the record.

    ⚠️ The filing is read only to learn which directory each container's linked
    file sits in; the count itself is what is on disk there.
    """
    included = _included(root, manifest)
    counts = {}
    for group in filed(root, manifest, included=included):
        directory = PurePosixPath(group.origin).parent
        counts[group.address.key] = sum(
            1 for path in included if PurePosixPath(path).is_relative_to(directory)
        )
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
    # ⚠️ Deferred: reconnaissance reaches onboarding, which imports this package.
    from studyforge.skills.reconnaissance import read

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


def _units(entries, address: Address, where: str, *, labelled: bool = False) -> tuple[Unit, ...]:
    """Return one unit per entry, numbered by its position among them.

    ⛔ **A written ordinal must agree with its place among its siblings**: it is
    the reading order, so a gap or a repeat is a decision about the order and
    not a typo. ⭐ `labelled` keeps each written ordinal as the unit's label.
    """
    units = []
    places = _Places(min((len(e.ordinal.split(".")) for e in entries if e.ordinal), default=0))
    for position, entry in enumerate(entries, start=1):
        places.check(entry.ordinal, position, address, where)
        units.append(
            Unit(
                n=position,
                title=entry.title,
                practices=0,
                origin=entry.target,
                origin_section=entry.section,
                label=entry.ordinal if labelled else None,
            )
        )
    if not units:
        raise CurriculumDisagrees(
            f"the record lists no unit under the group declared at {address.key}; an "
            f"empty container reaches the contents page as an empty row"
        )
    return tuple(units)


class _Places:
    """Each entry's place among its siblings, counted as the record is read.

    ⭐ Siblings are the entries at one depth under one parent: the group's
    shallowest ordinals, and an entry with none, share the group as their
    parent; a deeper ordinal's parent is the ordinal it extends, written
    before it.
    """

    def __init__(self, top: int) -> None:
        self.top = top
        self.counts: dict[tuple[str, ...], int] = {}
        self.seen: set[tuple[str, ...]] = set()

    def check(self, ordinal: str | None, position: int, address: Address, where: str) -> None:
        """Count one entry, refusing an ordinal that is not its place."""
        parts = tuple(ordinal.split(".")) if ordinal else ()
        parent = parts[:-1] if len(parts) > self.top else ()
        if parent and parent not in self.seen:
            raise CurriculumDisagrees(
                f"{where} numbers entry {position} of {address.key} as {ordinal}, beneath "
                f"an entry the record does not list before it"
            )
        self.counts[parent] = self.counts.get(parent, 0) + 1
        self.seen.add(parts)
        if parts and int(parts[-1]) != self.counts[parent]:
            raise CurriculumDisagrees(
                f"{where} numbers entry {position} of {address.key} as {ordinal}; the "
                f"ordinal is the reading order, so the record is corrected rather than "
                f"the gap smoothed over"
            )


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
