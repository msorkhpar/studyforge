"""`W91`'s derivation: every numbered ruling, with the site that states it.

**What it does.** Reads the CTO round records, derives the whole numbered ruling
series from them, and renders one index row per ruling: the record's **own
words, quoted**, and an **anchored** address for the section that carries them.
⛔ **Nothing here paraphrases a ruling** (Ruling 195), and ⛔ **nothing here
types a count** — the population, the tail and every row are derived on each
run, which is what makes the completeness claim checkable rather than asserted
(Ruling 192's subject, taken the other way).

**How you use it.**

    python3 -m tools.quality.rulings            # rewrite the index
    python3 -m tools.quality.rulings --check    # exit 1 when it is stale

`entries(root)` is the derivation, `document.text(root)` is the rendered
index, and this package's `check_rulings_index` asserts the two agree on every
floor run.

**Depends on.** `re`, `dataclasses`, `pathlib`, and `tools.quality.pointers` for
`slug` and `prose_lines`. ⛔ The slug algorithm is **reused, never re-derived**:
this module writes 197 anchors and `check_pointers` reads every one of them, so
a second copy of that function would be a second answer to the same question.

## ⛔ Why this is an index of ADDRESSES and QUOTES, and not of summaries

⚠️ **An index is a second copy of everything it indexes**, and this project's
standing remedy for an unmaintainable second copy is to remove the subject
rather than maintain the copy (Rulings 161, 150, 136). ⭐ **A quote cannot
diverge and a pointer resolves at read time** (Ruling 195), so the only columns
here are a verbatim quote and an anchored address — both re-derived from the
record on every run. ⛔ **The round-17 index's `where it landed` column is
deliberately NOT carried:** it is a per-ruling claim about an artifact nobody
re-measures, it was already wrong for six of its own 42 rows when it shipped,
and it is precisely the column that cannot be kept true.

## ⛔ The series starts at round 14, and the rounds before it are a DIFFERENT series

⚠️ **Measured: `Ruling 1` is a heading in four records** —
`CTO-2026-09-09-m0-readiness.md`, `…-round3.md`, `…-round4.md` and
`…-round7.md` each open their own local 1–5, and the numbered series that the
project cites as `(Ruling N)` begins in `…-round14.md` and runs unbroken from
there. ⭐ **`SERIES_FIRST_ROUND` is therefore a DECLARED boundary with an
inhabited negative control**: `tools/tests/quality/rulings/test_derive.py` asserts the
excluded records really do restart at 1, so the declaration cannot quietly
become false.

⛔ **R1–R21 are the spec's own rulings and are a different series again.** They
are never read by this module: the population comes from the literal spelling
`Ruling <digits>`, which no `R7`-style citation can match.

## ⚠️ A number in a record is not always a ruling

⛔ **Measured: `Ruling 9999` appears in `…-round49.md`** as an *impossible*
control in a probe table. ⭐ **So the series is the CONTIGUOUS run from 1**, and
anything beyond the first gap is reported as `outside` rather than indexed —
printed, never dropped silently.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.pointers import prose_lines, slug
from tools.quality.rulings.quote import cell, passage

__all__ = [
    "INDEX_PATH",
    "RECORD_DIR",
    "SERIES_FIRST_ROUND",
    "Entry",
    "Record",
    "Site",
    "Series",
    "entries",
    "disagreements",
    "minted_in",
    "records",
    "series",
    "sites",
]

#: The directory holding the ruling records. ⛔ One directory, by construction:
#: a ruling is minted in a CTO round record and nowhere else.
RECORD_DIR = "docs/tasks/handoffs"

#: The generated document. ⭐ It sits beside the board rather than inside
#: `RECORD_DIR`, because a record is frozen (Ruling 106) and this is regenerated
#: every time a ruling is minted — the one thing a record may never be.
INDEX_PATH = "docs/tasks/rulings-index.md"

#: ⛔ The first round of the numbered series, declared rather than derived. The
#: module docstring carries the measurement and the test carries the control.
SERIES_FIRST_ROUND = 14

#: `CTO-…-round<n>.md`. ⚠️ The PO's records cite rulings and mint none, so they
#: are not read here: a citation is not a statement, and indexing one would
#: hand the reader a pointer at somebody quoting the ruling.
_RECORD_NAME = re.compile(r"^CTO-\d{4}-\d{2}-\d{2}-round(?P<round>\d+)\.md$")

_HEADING = re.compile(r"^#{1,6}\s+(?P<text>.*?)\s*#*\s*$")

#: A ruling citation, in the one spelling every office writes.
_RULING = re.compile(r"Ruling\s+(?P<number>\d+)")

#: Leading decoration a heading may carry before its subject: markers, emphasis,
#: blockquote marks and an ordinal like `3.` or `1d.`.
_DECORATION = re.compile(r"^(?:[⛔⭐⚠️✅>\s*_`]|\d+[a-z]?\.)+")

#: ⭐ The disposition-table mint: the CTO routes a finding by writing
#: `Ruled — Ruling N, landed in …` in a table cell. ⛔ Measured: for Rulings 72,
#: 73 and 75 this cell is the ONLY statement of the ruling anywhere.
_RULED = re.compile(r"RULED\s*[—–-]\s*\*{0,2}Ruling\s+(?P<number>\d+)\b", re.IGNORECASE)

#: `Ruling N —` or `Ruling N:` in prose: the ruling introducing its own clause.
_DECLARES = re.compile(r"(?<!\()Ruling\s+(?P<number>\d+)\*{0,2}\s*[—–:]")

#: ⛔ The round's own declaration of what it minted, in either shape the records
#: use. ⚠️ The body is read only as far as its leading run of wrapped numbers:
#: every one of these lines continues into prose that names OTHER rulings —
#: `(high-water mark was 110)` and `Ruling 168 binds me` both sit one token past
#: the end of the declaration.
_MINTED = re.compile(r"^\*\*Rulings minted[^:]*:\*\*\s*(?P<body>.*)$")
_MINTED_HEADING = re.compile(r"^#{1,6}\s*Rulings this round:\s*(?P<body>[\d,\s]+)$")
_WRAPPED_RUN = re.compile(r"^(?:\*\*\d+\*\*|`\d+`)(?:\s*[,–—-]\s*(?:\*\*\d+\*\*|`\d+`))*")

#: The ranks a site can have, best first. ⭐ The rank is part of the row: it is
#: what tells a reader whether the quote is the ruling's own heading or a
#: sentence inside a section they should open.
RANK_HEADING = 1
RANK_RULED = 2
RANK_DECLARES = 3
RANK_MENTION = 4


@dataclass(frozen=True)
class Record:
    """One ruling record, with the round number its filename declares."""

    round: int
    relative: str
    text: str


@dataclass(frozen=True)
class Site:
    """One place a ruling number is written, and the section it sits in."""

    number: int
    rank: int
    round: int
    record: str
    line: int
    anchor: str
    heading: str
    quote: str

    @property
    def on_heading(self) -> bool:
        """True when the quote IS the heading the address points at."""
        return self.quote == self.heading


@dataclass(frozen=True)
class Entry:
    """One index row: a ruling, its quoted site, and where that site is."""

    number: int
    site: Site


@dataclass(frozen=True)
class Series:
    """The derived population: the contiguous run from 1, and what fell outside."""

    numbers: tuple[int, ...]
    outside: tuple[int, ...]

    @property
    def tail(self) -> int:
        """The highest ruling in the contiguous series, or 0 when there is none."""
        return self.numbers[-1] if self.numbers else 0


def record_round(name: str) -> int | None:
    """Return the round a record's filename declares, or None when it is not one."""
    match = _RECORD_NAME.match(name)
    return int(match.group("round")) if match else None


def records(root: Path) -> list[Record]:
    """Every ruling record of the numbered series, in round order."""
    found: list[Record] = []
    directory = root / RECORD_DIR
    for path in sorted(directory.glob("CTO-*.md")):
        number = record_round(path.name)
        if number is None or number < SERIES_FIRST_ROUND:
            continue
        text = config.read_text(path)
        if text is None:
            continue
        found.append(Record(number, config.relative(path, root), text))
    return sorted(found, key=lambda record: (record.round, record.relative))


def minted_in(text: str) -> frozenset[int]:
    """Every ruling a record DECLARES it minted, from its own header.

    ⛔ Read only as far as the declaration's leading run of wrapped numbers, and
    a two-number run joined by a dash is a range. ⚠️ Reading further would
    capture the high-water mark that follows it in the same sentence.
    """
    minted: set[int] = set()
    for _number, line in prose_lines(text):
        heading = _MINTED_HEADING.match(line)
        if heading is not None:
            minted.update(int(found) for found in re.findall(r"\d+", heading.group("body")))
            continue
        declaration = _MINTED.match(line)
        if declaration is None:
            continue
        run = _WRAPPED_RUN.match(declaration.group("body"))
        if run is None:
            continue
        found = [int(digits) for digits in re.findall(r"\d+", run.group(0))]
        if len(found) == 2 and re.search(r"[—–-]", run.group(0)):
            found = list(range(found[0], found[1] + 1))
        minted.update(found)
    return frozenset(minted)


def _rank(line: str, number: int, heading: str | None) -> int:
    """Return how strongly this line states ruling `number`."""
    if heading is not None:
        subject = _DECORATION.sub("", heading)
        if re.match(rf"Ruling\s+{number}\b", subject):
            return RANK_HEADING
    if any(int(found) == number for found in _RULED.findall(line)):
        return RANK_RULED
    if any(int(found) == number for found in _DECLARES.findall(line)):
        return RANK_DECLARES
    return RANK_MENTION


def sites(record: Record) -> list[Site]:
    """Every site in one record where a ruling number is written.

    The address is the nearest enclosing heading, with the duplicate suffix
    GitHub and `heading_slugs` both apply, so a record that repeats a heading
    still yields an anchor that resolves.
    """
    found: list[Site] = []
    seen: dict[str, int] = {}
    anchor = ""
    heading = ""
    lines = prose_lines(record.text)
    for index, (line_number, line) in enumerate(lines):
        match = _HEADING.match(line)
        if match is not None:
            heading = match.group("text")
            base = slug(heading)
            count = seen.get(base, 0)
            seen[base] = count + 1
            anchor = base if count == 0 else f"{base}-{count}"
        for number in sorted({int(digits) for digits in _RULING.findall(line)}):
            rank = _rank(line, number, heading if match is not None else None)
            unit = heading if match is not None else passage(lines, index)
            found.append(
                Site(
                    number,
                    rank,
                    record.round,
                    record.relative,
                    line_number,
                    anchor,
                    cell(heading, number),
                    cell(unit, number),
                )
            )
    return found


def _all_sites(root: Path) -> tuple[dict[int, list[Site]], dict[int, int]]:
    """Every site by ruling number, and the round each ruling declares as its mint."""
    by_number: dict[int, list[Site]] = {}
    declared: dict[int, int] = {}
    for record in records(root):
        for number in minted_in(record.text):
            declared.setdefault(number, record.round)
        for site in sites(record):
            by_number.setdefault(site.number, []).append(site)
    return by_number, declared


def series(numbers: set[int]) -> Series:
    """Split a set of written numbers into the contiguous series from 1, and the rest."""
    run: list[int] = []
    candidate = 1
    while candidate in numbers:
        run.append(candidate)
        candidate += 1
    return Series(tuple(run), tuple(sorted(number for number in numbers if number not in set(run))))


def _choose(candidates: list[Site], declared: int | None) -> Site:
    """Return the site an index row quotes: the best rank, earliest, in the mint round.

    ⛔ The round a ruling DECLARES as its mint wins over rank, and that is the
    whole defect it closes: `…-round49.md` states Rulings 193–195 before
    `…-round50.md` mints them, and a rank-first choice quotes the forecast.
    """
    eligible = [site for site in candidates if declared is None or site.round == declared]
    return min(eligible or candidates, key=lambda site: (site.rank, site.round, site.line))


def entries(root: Path) -> tuple[Entry, ...]:
    """One row per ruling in the derived series, in number order."""
    by_number, declared = _all_sites(root)
    population = series(set(by_number))
    return tuple(
        Entry(number, _choose(by_number[number], declared.get(number)))
        for number in population.numbers
    )


def disagreements(root: Path) -> list[tuple[int, int, int]]:
    """`(ruling, declared round, round of its best-ranked site)` where the two differ.

    ⭐ The cross-check that makes the provenance half of this index falsifiable:
    two independent derivations of one ruling's mint round, compared. ⚠️ A
    disagreement is a reading about the RECORDS, not a defect in them, so it is
    reported rather than failed on.
    """
    by_number, declared = _all_sites(root)
    found: list[tuple[int, int, int]] = []
    for number in series(set(by_number)).numbers:
        round_declared = declared.get(number)
        if round_declared is None:
            continue
        best = min(by_number[number], key=lambda site: (site.rank, site.round, site.line))
        if best.round != round_declared:
            found.append((number, round_declared, best.round))
    return found
