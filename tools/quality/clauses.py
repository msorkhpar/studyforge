"""`W141`: a heading that STATES its clause count is read against the children it parents.

**What it does.** Reads every tracked markdown document under `docs/conventions/`
and, for each heading whose text states a count of clauses — *"nine clauses"*,
*"one clause"*, *"2 clauses"* — counts the headings exactly one level below it,
up to the next heading at its own level or above. ⛔ **It reports the PAIR, the
stated number beside the counted one, and never a bare verdict** (Ruling 128).

**How you use it.** `check_clause_counts(root)` is registered in
`tools.quality.CHECKS` and fails the floor for every heading whose two numbers
differ; `clause_census(root)` is registered in `NOTICES` and prints every pair,
agreeing or not. `stated_count(heading)` and `claims(document, text)` are the
predicate and the per-document reading both are built on, and `scan(root)` is
the one walk they share.

**Depends on.** `tools.quality.markdown` for `headings` and `strip_code_spans` —
so a heading means here exactly what it means to the pointer floor — `config`
for the walk, `report` for the answer, and `re` and `dataclasses`.

## ⛔ SAY IT AND IT IS CHECKED — never *you must say it*

⭐ **The predicate is the heading's OWN stated number and not a style rule.** A
heading that states no count is SILENT: it is not a finding and it is not in the
census's pairs. ⛔ Requiring a count would be the gate Ruling 180 removed wearing
a new hat, and the house has already moved away from stating one — `RULED ROUND
66` onward omit it deliberately, citing this row.

## ⚠️ NUMBER WORDS ARE THE POPULATION, NOT DIGITS

⛔ **Every live instance spells its count in words**, so a predicate reading
digits alone reads EMPTY on the whole live tree and passes vacuously (Ruling 48).
⭐ The mirror asserts the live population is non-empty and word-spelled, so that
predicate turns the suite red rather than green.

## ⭐ WHY A FINDING AS WELL AS A NOTICE

⚠️ **The live population was made TRUE in the branch that landed this** — a
number nothing re-derives drifts on the next insert, and a notice alone would
let it (Ruling 348: a printed arm is not a gate until it moves the exit code).
⛔ A heading with more than one stated count is read for its FIRST; none exists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.markdown import headings, strip_code_spans
from tools.quality.report import WALK_CAVEAT, Finding

RULE_CLAUSES = "clause-count"

#: ⛔ The one directory the row binds: the conventions, where rulings land.
CONVENTIONS_DIR = "docs/conventions"

#: ⚠️ Spelled out to twenty. The live population reaches thirteen, and a count
#: above the table is not silently missed — it is simply not a claim, which the
#: census's denominator makes visible.
NUMBER_WORDS = {
    word: value
    for value, word in enumerate(
        (
            "one two three four five six seven eight nine ten eleven twelve thirteen "
            "fourteen fifteen sixteen seventeen eighteen nineteen twenty"
        ).split(),
        start=1,
    )
}

#: A number — a word from `NUMBER_WORDS` or digits — immediately followed by
#: `clause` or `clauses`. ⭐ Words FIRST: they are the live population.
_STATED = re.compile(
    r"\b(?P<count>" + "|".join(NUMBER_WORDS) + r"|\d+)\s+clauses?\b", re.IGNORECASE
)


@dataclass(frozen=True)
class Claim:
    """One heading that states a clause count, with the count it actually parents."""

    document: str
    line: int
    heading: str
    spelling: str
    stated: int
    counted: int

    @property
    def agrees(self) -> bool:
        """Whether the stated number is the number of children."""
        return self.stated == self.counted

    @property
    def title(self) -> str:
        """The heading up to its first ` — `, which is where every live one names itself."""
        return self.heading.partition(" — ")[0]


@dataclass(frozen=True)
class ClauseScan:
    """One walk: the documents read, the headings in them, and every claim."""

    documents: int
    headings: int
    claims: tuple[Claim, ...]
    walk: str


def stated_count(heading: str) -> tuple[str, int] | None:
    """`(spelling, value)` of the clause count `heading` states, or None when it states none.

    ⛔ A count inside a code span is a MENTION and is not read.
    """
    match = _STATED.search(strip_code_spans(heading))
    if match is None:
        return None
    spelling = match.group("count")
    value = int(spelling) if spelling.isdigit() else NUMBER_WORDS[spelling.lower()]
    return spelling, value


def claims(document: str, text: str) -> list[Claim]:
    """Every count-stating heading in `text`, paired with its direct children."""
    found = headings(text)
    result: list[Claim] = []
    for index, (line, level, heading) in enumerate(found):
        stated = stated_count(heading)
        if stated is None:
            continue
        counted = 0
        for _line, child_level, _heading in found[index + 1 :]:
            if child_level <= level:
                break
            counted += child_level == level + 1
        result.append(Claim(document, line, heading, stated[0], stated[1], counted))
    return result


def scan(root: Path) -> ClauseScan:
    """Read every tracked document under `CONVENTIONS_DIR` once, for both channels."""
    population = config.markdown_population(root)
    prefix = f"{CONVENTIONS_DIR}/"
    documents = 0
    heading_total = 0
    found: list[Claim] = []
    for path in population.paths:
        document = config.relative(path, root)
        if not document.startswith(prefix):
            continue
        text = config.read_text(path)
        if text is None:
            continue
        documents += 1
        heading_total += len(headings(text))
        found.extend(claims(document, text))
    return ClauseScan(documents, heading_total, tuple(found), population.walk)


def _pair(claim: Claim) -> str:
    """Render the heading, the number it states and the number it parents, side by side."""
    return f"{claim.title!r} states {claim.spelling!r} ({claim.stated}), parents {claim.counted}"


def check_clause_counts(root: Path) -> list[Finding]:
    """Return one finding per heading whose stated clause count is not its child count."""
    return [
        Finding(
            claim.document,
            claim.line,
            RULE_CLAUSES,
            f"{_pair(claim)}. The number is binding where it is written: correct it, "
            f"re-parent the children under the heading they belong to, or state no count.",
        )
        for claim in scan(root).claims
        if not claim.agrees
    ]


def clause_census(root: Path) -> list[str]:
    """Print every stated clause count beside its counted children, green run or red.

    ⚠️ An empty population still prints its denominator (Ruling 191(a)).
    """
    result = scan(root)
    disagreeing = sum(1 for claim in result.claims if not claim.agrees)
    lines = [
        f"clause counts: {len(result.claims)} of {result.headings} headings in "
        f"{result.documents} documents under {CONVENTIONS_DIR}/ ({result.walk} walk) state "
        f"a clause count; {disagreeing} disagree with their children. A heading stating "
        f"none is silent.{WALK_CAVEAT[result.walk]}"
    ]
    for claim in result.claims:
        verdict = "" if claim.agrees else " — DISAGREES"
        lines.append(f"  {claim.document}:{claim.line} {_pair(claim)}{verdict}")
    return lines


__all__ = [
    "CONVENTIONS_DIR",
    "NUMBER_WORDS",
    "RULE_CLAUSES",
    "Claim",
    "ClauseScan",
    "check_clause_counts",
    "claims",
    "clause_census",
    "scan",
    "stated_count",
]
