r"""The draft's `curriculum` block: what the survey detected, written where it is checked.

**What it does.** Turns the record `record.find` chose into the manifest's
`curriculum` declaration — the record's path, each group's label with a
proposed address, and a group's filename prefix wherever the names on disk
partition the units exactly as the record groups them — and asks about every
part of it a person has to settle.

**How you use it.** `proposal.draft` calls `heads_of(inventory, record)`, then
`declare(record, inventory, levels, linked)`, which returns
`(block or None, uncertainties)`.

**Depends on.** `record`, `inventory`, `report`, `studyforge.address` for what
a slug is, and `corpus.manifest` for what a prefix is and the version the key
needs. ⛔ Nothing source-specific (R1).

## ⭐ Detection and declaration are one act

⚠️ Before this block existed, step 2's *"the curriculum is recorded in
`<file>`"* and its prefix cross-check were detected and then **said** — in a
report nobody's adapter reads — while the adapter carried the same facts as
constants. ⭐ Written here, the adapter skill's `curriculum.filed` reads them
back with the same record reader and refuses when the tree stops agreeing, so
a detection that goes stale is a refusal rather than a memory.

## ⛔ What it proposes, and what it only asks

- **The record's path** is measured: it is the document that links the most material.
- **Each label** is the record's own text, emphasis removed.
- ⚠️ **Each address is a proposal.** §6 records an address and never derives
  one, so the slug of the label is offered and asked about, exactly as
  `source` is. ⛔ Where two labels would share one slug, or one has none, no
  group is drafted at all: a draft the manifest refuses left nothing open.
- ⛔ **A prefix is drafted only where it agrees.** Reconnaissance step 2 keeps
  the filename-prefix rule *"as a cross-check that must agree — never as the
  source"*. So a group gets a prefix only when every unit it lists
  carries that one prefix, no other group's units carry it, and no other
  material file does. ⭐ A partial agreement drafts no prefix and says so.
- ⭐ **A linked level is drafted where the record has one** (`linked.split_linked`):
  in a two-level draft whose record opens each module with a linked list
  entry beneath a label, the labels are drafted as the groups one level up and
  `linked` names the last level, so no filing is written by hand. ⛔ A record
  that only partly has the shape drafts no `linked` and says why.
"""

from __future__ import annotations

from studyforge.address import slugify
from studyforge.corpus.manifest import KEY_VERSIONS, prefix_of
from studyforge.skills.reconnaissance.inventory import Inventory
from studyforge.skills.reconnaissance.linked import Linked, NotLinked, split_linked
from studyforge.skills.reconnaissance.record import Record
from studyforge.skills.reconnaissance.report import Uncertainty

#: The `corpus_api` a draft carrying the block declares, read from the
#: manifest's own map so the two cannot drift.
CURRICULUM_API = KEY_VERSIONS[(None, "curriculum")]
LINKED_API = KEY_VERSIONS[("curriculum", "linked")]


def heads_of(inventory: Inventory, record: Record | None) -> Linked | None:
    """Return the record's linked level, or `None` when it does not have that shape."""
    if record is None or not record.groups:
        return None
    try:
        lines = (inventory.root / record.path).read_text(encoding="utf-8").splitlines()
        return split_linked(lines, record.path.as_posix(), record.entries, record.labels)
    except OSError, UnicodeDecodeError, NotLinked:
        return None


def declare(
    record: Record | None,
    inventory: Inventory,
    levels: list[str],
    linked: Linked | None = None,
) -> tuple[dict | None, list[Uncertainty]]:
    """Return the draft's `curriculum` block and every question it leaves open."""
    if record is None:
        return None, []
    block: dict[str, object] = {"record": record.path.as_posix()}
    depth = len(levels)
    if linked is not None and depth == 2:
        return _linked(block, record, linked, levels)
    if depth != 1 or not record.groups:
        # ⭐ Where the curriculum lives is still a finding worth writing down.
        return block, [_where(block)]
    addresses = [slugify(label) for label in record.groups]
    if not all(addresses) or len(set(addresses)) != len(addresses):
        return block, [_where(block), _unaddressed(record)]
    prefixes = _agreed(record, inventory)
    block["containers"] = [
        {"label": label, "address": address}
        | ({"prefix": prefixes[label]} if label in prefixes else {})
        for label, address in zip(record.groups, addresses, strict=True)
    ]
    return block, [_where(block), _addresses(addresses), _prefixes(record, prefixes)]


def _linked(
    block: dict, record: Record, linked: Linked, levels: list[str]
) -> tuple[dict, list[Uncertainty]]:
    """Draft the labels one level up, with `linked` naming the last level."""
    addresses = [slugify(label) for label in record.groups]
    if not all(addresses) or len(set(addresses)) != len(addresses):
        return block, [_where(block), _unaddressed(record)]
    block["containers"] = [
        {"label": label, "address": address}
        for label, address in zip(record.groups, addresses, strict=True)
    ]
    block["linked"] = levels[-1]
    return block, [
        _where(block),
        _addresses(addresses),
        Uncertainty(
            question=(
                f"does each of the {len(linked.heads)} linked entries beneath the "
                f"{len(record.groups)} labels open one {levels[-1]}?"
            ),
            why=(
                "each is a list entry linking a page, with units indented beneath it; its "
                "address is the label's followed by the name of the directory holding that "
                "page, and the page itself is not drafted as material"
            ),
            settles_it=(
                "confirm, or drop 'linked' and file the units in read.py; the adapter "
                "refuses a record that stops having this shape"
            ),
        ),
    ]


def _agreed(record: Record, inventory: Inventory) -> dict[str, str]:
    """Each group's prefix, where the names partition exactly as the record groups."""
    carried: dict[str, set[str | None]] = {}
    for entry in record.entries:
        carried.setdefault(entry.group, set()).add(prefix_of(entry.target))
    single = {
        group: next(iter(found))
        for group, found in carried.items()
        if group is not None and len(found) == 1 and next(iter(found)) is not None
    }
    if len(set(single.values())) != len(single):
        return {}
    listed = {entry.target: entry.group for entry in record.entries}
    owner = {prefix: group for group, prefix in single.items()}
    for path in inventory.material:
        name = path.relative_to(inventory.root).as_posix()
        group = owner.get(prefix_of(name))
        if group is not None and listed.get(name) != group:
            # ⛔ A file named for a group that the record does not file there:
            # the names and the record disagree, so neither partition is drafted.
            return {}
    return single


def _where(block: dict) -> Uncertainty:
    """Ask the person to confirm the record the survey chose."""
    return Uncertainty(
        question=f"is {block['record']} the document that records this curriculum?",
        why="chosen because it links to more of the material than any other document",
        settles_it=(
            "confirm it, or name the document that records the reading order and grouping; "
            "the adapter files every unit from it"
        ),
    )


def _addresses(addresses: list[str]) -> Uncertainty:
    """Ask for the addresses, which the survey proposed and cannot know."""
    return Uncertainty(
        question=f"are these the addresses the groups are served at — {addresses}?",
        why=(
            "each is the slug of its group's label; §6 records an address and never derives "
            "one, so these are proposals"
        ),
        settles_it="replace each with the address this corpus files that group at",
    )


def _unaddressed(record: Record) -> Uncertainty:
    """Say why no group was drafted, when their labels would not give distinct slugs."""
    return Uncertainty(
        question=f"what address is each of the {len(record.groups)} groups filed at?",
        why="two labels share one slug, or a label has none, so no address could be proposed",
        settles_it="declare curriculum.containers with a label and an address for each group",
    )


def _prefixes(record: Record, prefixes: dict[str, str]) -> Uncertainty:
    """Say which groups got a prefix cross-check, and why the others did not."""
    return Uncertainty(
        question=(
            f"{len(prefixes)} of {len(record.groups)} group(s) are cross-checked by filename "
            f"prefix: {sorted(prefixes.values())}. Is that the naming rule?"
        ),
        why=(
            "a prefix is drafted only where every file a group lists carries it and no other "
            "file does; it never files a unit, and the adapter refuses when it disagrees"
        ),
        settles_it="confirm, or drop a prefix the corpus does not mean as a naming rule",
    )
