"""`W140`: the anchor names one document answers to TWICE, and the links that land on them.

**What it does.** Counts, for every markdown document, the anchor names that
more than one heading answers to, and reports the pointers that link into one.
⛔ **The FINDING is the inbound link, never the duplicate heading** — a repeated
heading nobody addresses costs a reader nothing, while a `](…#what-settles-it)`
lands on whichever of six a renderer picks and the pointer floor calls it
resolved. ⭐ The population itself is printed through the notice channel, in
full, because a collision with no inbound link is a fact rather than a
violation.

**How you use it.** `check_anchor_collisions(root)` is registered in
`tools.quality.CHECKS`; `collision_census(root)` is registered in `NOTICES`,
immediately after `pointer_coverage` — the line it exists to qualify.
`scan(root)` is the one pass both read, so the census and the findings can
never describe different walks.

**Depends on.** `tools.quality.pointers` for the parser — `heading_bases`,
`pointers`, `resolve_target` — `config` for the walk, `report` for the answer,
and `collections`. Standard library only. ⛔ **The seam runs ONE WAY:** this
module imports `pointers`, and `pointers` imports nothing back.

## ⛔ WHY THE FLOOR COULD NOT SEE THIS, AND IT IS NOT A MISSING CHECK

⚠️ **`CTO-62/3`, re-measured here:** `heading_slugs()` returns a `set[str]`, so
a duplicate heading is **absorbed at the moment it is produced**. ⭐ The floor's
`0 unresolved` is TRUE — every anchor in the tree names a heading — and it is
not the property a reader takes from it, ⛔ **which is the worst shape a green
reading can have.** The remedy is not to change `heading_slugs`: its callers ask
*does this document answer to this anchor*, and a set answers that correctly.
The remedy is a companion that does not fold, and a census built on it.

## ⛔ AND THE POPULATION GROWS ON EVERY CLOSE, BY CONSTRUCTION

⭐ **A close moves a row's body into the archive, and a row is written from a
house template whose section names are the same in every row** — so
`what-settles-it` and `findings` accumulate at a rate nobody is being careless
about. ⚠️ **MEASURED at `94ad941` by `wt/dev2`, with the shipped parser:** the
archive alone reads `753` headings, `722` distinct, `31` excess over `11`
colliding names. ⛔ **A row is NOT the remedy and neither is a rename sweep:**
archived bytes are frozen (Ruling 106), and the template is a GOOD template.
⭐ What an instrument can do is make the growth reportable, and make the one
shape that actually costs a reader — an inbound link — fail the build.

## ⚠️ WHY AN EXPLICIT SUFFIX IS NOT A FINDING

⭐ `#same-1` addresses the second `## Same` deterministically, under the same
suffixing rule GitHub applies and `heading_slugs` reproduces. ⛔ **Only the BASE
name is ambiguous**, so only a link to the base is reported — a reader who has
already disambiguated is not failed for it.

## ⛔ AND THE POPULATION IS WHAT GIT TRACKS, NAMED IN THE LINE (`W148`)

⭐ **This census and `pointer_coverage`'s denominator are the SAME population**,
so they take it from the same `config.markdown_population` and each prints
`(tracked walk)` or `(disk walk)` beside its figure. ⛔ Before `W148` both came
off the disk, and one untracked file in a main checkout made every figure here
irreproducible from a linked worktree at the same ref — ⚠️ **the denominator
moved and the numerator did not.**

## ⭐ WHY THE CENSUS PRINTS ONE LINE PER DOCUMENT

⛔ **Ruling 128 — the population was the finding; the count concealed it** — so
every colliding name is printed with its count rather than summed into a
scalar. ⚠️ **Grouped by document, because the document is the unit of remedy**
(a minting office is asked to make the heading it is writing unique in the
document it is writing it in), and because the line count then grows with
DOCUMENTS rather than with names — the archive can gain a thousand duplicate
headings without gaining a line here.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.pointers import Pointer, heading_bases, pointers, resolve_target
from tools.quality.report import WALK_CAVEAT, Finding

RULE_COLLISION = "collision"


@dataclass(frozen=True)
class Collision:
    """One anchor name that more than one heading in one document answers to."""

    document: str
    name: str
    headings: int
    inbound: tuple[Pointer, ...]


@dataclass(frozen=True)
class CollisionScan:
    """One pass over the tree: the census and the findings, from one walk.

    ⛔ `walk` is `report.TRACKED_WALK` or `report.DISK_WALK`, carried rather
    than re-derived so the census and the sentence naming how its population
    was reached can never describe different walks (`W148`).
    """

    documents: int
    anchored: int
    collisions: tuple[Collision, ...]
    findings: tuple[Finding, ...]
    walk: str

    @property
    def documents_colliding(self) -> int:
        """How many documents carry at least one colliding anchor name."""
        return len({collision.document for collision in self.collisions})

    @property
    def headings(self) -> int:
        """How many headings all the colliding names answer for, together."""
        return sum(collision.headings for collision in self.collisions)


def colliding_names(text: str) -> dict[str, int]:
    """Every anchor name in `text` that more than one heading answers to.

    ⭐ The fence-awareness and the slugging are `heading_bases`'s, inherited
    rather than restated: an instrument that parsed headings its own way could
    report a collision the floor's own resolver does not believe in.
    """
    counts = Counter(heading_bases(text))
    return {name: count for name, count in counts.items() if count > 1}


def _order(collision: Collision) -> tuple[int, int, str, str]:
    """Sort key: inbound pointers first, then depth, then document and name.

    ⛔ **Ordered by inbound pointers because that is the order of cost.** A
    name six headings deep with nothing pointing at it is a curiosity; a name
    two deep with a live link into it is a reader sent to the wrong section.
    """
    return (-len(collision.inbound), -collision.headings, collision.document, collision.name)


def _finding(pointer: Pointer, collision: Collision) -> Finding:
    """Return the finding one inbound link earns, where a reader can act on it."""
    where = pointer.path_part or "this document"
    return Finding(
        pointer.document,
        pointer.line,
        RULE_COLLISION,
        f"points at anchor {pointer.anchor!r} in {where!r}, which {collision.headings} "
        f"headings answer to. It RESOLVES — to whichever one a renderer reaches first — "
        f"so the pointer check reads it as green while the reader lands somewhere "
        f"nobody chose. Address the one you mean by its suffix, or name a heading that "
        f"is unique.",
    )


def scan(root: Path) -> CollisionScan:
    """One pass over every markdown document: the census and the findings.

    ⛔ **One walk, read by both channels.** A census counted in one pass and
    findings gathered in another could report `0 with an inbound pointer` over
    a population the finding half never looked at — Ruling 48's defect wearing
    a denominator.
    """
    population = config.markdown_population(root)
    documents = 0
    collisions: dict[Path, dict[str, int]] = {}
    names: dict[Path, str] = {}
    found: list[Pointer] = []
    for path in population.paths:
        text = config.read_text(path)
        if text is None:
            continue
        documents += 1
        document = config.relative(path, root)
        duplicates = colliding_names(text)
        if duplicates:
            collisions[path.resolve()] = duplicates
            names[path.resolve()] = document
        found.extend(pointers(document, text))

    anchored = [pointer for pointer in found if pointer.anchor]
    inbound: dict[tuple[Path, str], list[Pointer]] = {}
    for pointer in anchored:
        target = resolve_target(root, root / pointer.document, pointer)
        if target is None:
            continue
        # ⚠️ A same-document link comes back exactly as it was handed in, so
        # the key has to be resolved here rather than assumed resolved.
        duplicates = collisions.get(target.resolve())
        if duplicates is None:
            continue
        name = pointer.anchor.lower()
        if name in duplicates:
            inbound.setdefault((target.resolve(), name), []).append(pointer)

    census = [
        Collision(names[path], name, count, tuple(inbound.get((path, name), ())))
        for path, duplicates in collisions.items()
        for name, count in duplicates.items()
    ]
    census.sort(key=_order)
    findings = [
        _finding(pointer, collision) for collision in census for pointer in collision.inbound
    ]
    return CollisionScan(
        documents, len(anchored), tuple(census), tuple(sorted(findings)), population.walk
    )


def check_anchor_collisions(root: Path) -> list[Finding]:
    """Every pointer that lands on an anchor name more than one heading answers to."""
    return list(scan(root).findings)


def _document_line(document: str, collisions: list[Collision]) -> str:
    """One document's colliding names, every one of them, deepest first."""
    parts = []
    for collision in collisions:
        carried = f", {len(collision.inbound)} inbound" if collision.inbound else ""
        parts.append(f"{collision.name} x{collision.headings}{carried}")
    return f"  {document}: " + "; ".join(parts)


def collision_census(root: Path) -> list[str]:
    """Return the colliding-anchor population, printed whether or not anything failed.

    ⛔ **Printed on a green run above all**, because that is the run where the
    pointer check's `0 unresolved` is most likely to be read as *no anchor in
    this tree is ambiguous* (Ruling 48, Ruling 128). ⚠️ An empty population
    returns the PASS reading with its denominator rather than no line at all
    (Ruling 191(a)): `0` is a reading here, not a silence.
    """
    result = scan(root)
    if not result.collisions:
        return [
            f"anchor collisions: none — no anchor name in {result.documents} markdown "
            f"documents ({result.walk} walk) answers for more than one heading, and "
            f"{result.anchored} anchored pointers were read.{WALK_CAVEAT[result.walk]}"
        ]
    carrying = sum(1 for collision in result.collisions if collision.inbound)
    lines = [
        f"anchor collisions: {len(result.collisions)} anchor names in "
        f"{result.documents_colliding} of {result.documents} markdown documents "
        f"({result.walk} walk) answer for {result.headings} headings; {carrying} of them "
        f"carry an inbound pointer, out of {result.anchored} anchored pointers read."
        f"{WALK_CAVEAT[result.walk]}"
    ]
    grouped: dict[str, list[Collision]] = {}
    for collision in result.collisions:
        grouped.setdefault(collision.document, []).append(collision)
    lines.extend(_document_line(document, members) for document, members in grouped.items())
    return lines
