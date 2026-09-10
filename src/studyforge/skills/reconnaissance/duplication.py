r"""The same material twice — as a whole file, and as a region of one.

**What it does.** Finds material this corpus carries more than once, in the two
shapes it actually arrives in, and reports the second shape even where nothing
can be done about it.

**How you use it.** `aggregates(inventory)` finds whole-file duplication;
`structural(inventory)` finds a region of one document reproducing the heading
tree of another.

**Depends on.** `inventory`, `report`.

## ⛔ Whole-file duplication is the easy half

⚠️ **Measured (ISO-8583):** the corpus ships per-unit files *and* three
whole-series aggregates that are **exact ordered concatenations** of their
groups — `9,181 of 18,304 lines, 50.2%`, digest-identical. A glob over `*.md`
ingests everything twice, **nothing fails**, narration synthesises the whole
corpus twice, and the reader gets three table-of-contents entries that are each
a whole series.

⭐ Because the duplication is *total* rather than approximate, the detector can
assert digest equality rather than similarity — which is what makes this
checkable instead of a judgement call.

## ⛔ And the hard half is a region, not a file

⚠️ **Measured (ISO-8583):** `README.md` is 674 lines; lines 313–674 carry **361
of its 367 headings, digest-identical to the whole heading tree of
`TestCases.md`** — **53.7% of the curriculum document's lines**. ⛔ No file
duplicates a file, so the whole-file test finds nothing.

⛔ **And the file cannot be excluded**, because it is the only record of the
corpus's addresses, titles, ordinals and grouping. `content.exclude` names
files; this is not a file.

⭐ **So this is reported even though nothing can be done about it.** A report
that says *"no duplication found"* about a corpus in that state is wrong in a
way its reader will act on (R6) — they will trust a heading count, or a word
count, or a narration estimate, and every one of them is nearly double.

## ⚠️ A limit worth knowing before excluding anything

Excluding a file discards the copy **and the attestation the copy constituted**.
ISO's three aggregates are pure duplication *and* a second, independent,
machine-checkable recording of the reading order — the one property of that
corpus nothing else can verify. ⛔ There is nothing to fix; a planner should
extract what an excluded file attests **before** excluding it.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from studyforge.skills.reconnaissance.inventory import Inventory
from studyforge.skills.reconnaissance.report import Observation, Uncertainty

HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s{0,3}(?:`{3,}|~{3,})")

#: How much of a document's heading tree must reappear elsewhere before it is
#: worth a person's attention. ⚠️ Not a similarity score — the comparison is
#: digest equality over a *run* of headings, so this is "how long a run".
STRUCTURAL_RUN = 12

#: The shortest file worth testing as a concatenation of others. ⚠️ Small,
#: because the test is **exact** — a file that is the ordered concatenation of
#: two others is a duplicate whatever its length, and the strength of the claim
#: comes from digest equality rather than from size.
MIN_AGGREGATE_LINES = 4


@dataclass(frozen=True, slots=True)
class Aggregate:
    """One file whose content is the ordered concatenation of others."""

    path: str
    covers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Structural:
    """A run of headings in one document reproducing another's heading tree."""

    path: str
    reproduces: str
    headings: int
    of_document: float


def normalised(text: str) -> list[str]:
    """Content lines with blanks and trailing space removed — the comparable form."""
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def digest(lines: list[str]) -> str:
    """Digest a line sequence, so equality is asserted rather than eyeballed."""
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def headings_of(text: str) -> list[str]:
    """Every heading outside a fence, as `level:text` — a document's structure.

    ⚠️ Fence-aware, and that is the whole difficulty: a `#` at the start of a
    line inside a fence is a comment in half the languages real material
    quotes, and counting it would make this report duplication that is not
    there.
    """
    found: list[str] = []
    fenced = False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = HEADING.match(line)
        if match is not None:
            found.append(f"{len(match.group(1))}:{match.group(2).strip()}")
    return found


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:  # pragma: no cover - reported by the walk
        return None


def aggregates(inventory: Inventory) -> list[Aggregate]:
    """Every file that is an ordered concatenation of other material files.

    ⛔ Ordered, and asserted by digest. A file that merely *contains* the same
    words is a different and much weaker claim; this one says "these N files,
    in this order, are that file", which is a statement somebody can act on.
    """
    contents = {}
    for path in inventory.material:
        text = _read(path)
        if text is not None:
            contents[path] = normalised(text)
    found: list[Aggregate] = []
    for candidate, whole in contents.items():
        if len(whole) < MIN_AGGREGATE_LINES:
            continue
        parts = _covered(candidate, contents, whole)
        if parts:
            found.append(
                Aggregate(
                    path=candidate.relative_to(inventory.root).as_posix(),
                    covers=tuple(p.relative_to(inventory.root).as_posix() for p in parts),
                )
            )
    return found


def _covered(candidate: Path, contents: dict, whole: list[str]) -> list[Path]:
    """Which files, in order, exactly reconstruct `candidate`'s content."""
    at = 0
    used: list[Path] = []
    while at < len(whole):
        for path, lines in contents.items():
            if path is candidate or not lines:
                continue
            if whole[at : at + len(lines)] == lines:
                used.append(path)
                at += len(lines)
                break
        else:
            return []
    return used if len(used) > 1 else []


def structural(inventory: Inventory) -> list[Structural]:
    """Every document reproducing a long run of another's heading tree."""
    trees = {}
    for path in inventory.material:
        text = _read(path)
        if text is not None:
            trees[path] = headings_of(text)
    found: list[Structural] = []
    for path, tree in trees.items():
        for other, whole in trees.items():
            if other is path or len(whole) < STRUCTURAL_RUN:
                continue
            if digest(whole) in {digest(tree[i : i + len(whole)]) for i in range(len(tree))}:
                found.append(
                    Structural(
                        path=path.relative_to(inventory.root).as_posix(),
                        reproduces=other.relative_to(inventory.root).as_posix(),
                        headings=len(whole),
                        of_document=len(whole) / len(tree) if tree else 0.0,
                    )
                )
    return found


def observe(inventory: Inventory) -> Iterator[Observation | Uncertainty]:
    """Report both shapes of duplication, and what can be done about each."""
    whole = aggregates(inventory)
    yield Observation("files that are concatenations of others", str(len(whole)))
    for item in whole:
        yield Uncertainty(
            question=f"is {item.path} material, or a copy of {len(item.covers)} other files?",
            why=(
                f"its content is the exact ordered concatenation of "
                f"{list(item.covers[:3])}{'…' if len(item.covers) > 3 else ''}, "
                f"asserted by digest"
            ),
            settles_it=(
                "almost certainly exclude it — ingesting both reads the corpus "
                "twice and nothing fails. ⚠️ But it is also an independent "
                "recording of the reading order, so extract what it attests "
                "before excluding it"
            ),
        )
    regions = structural(inventory)
    yield Observation("documents copying another's heading tree", str(len(regions)))
    for item in regions:
        yield Uncertainty(
            question=f"how much of {item.path} is really about this corpus?",
            why=(
                f"{item.headings} of its headings ({item.of_document:.0%}) reproduce "
                f"the whole heading tree of {item.reproduces}"
            ),
            settles_it=(
                "confirm which region of it is the curriculum. ⛔ It probably "
                "cannot be excluded — a document that records the corpus's "
                "titles and ordinals has to be read — so the answer is a "
                "region, not an exclusion"
            ),
        )
