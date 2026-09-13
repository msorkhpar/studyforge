"""`W149`: a merge subject whose PROSE states a READING is refused BEFORE the merge.

**What it does.** Reads one merge subject. It sets aside the header (`Merge <branch>`, and
an optional `(<ROW>[, …])` after it) and a closing `(CTO: …)` bracket. It then
ENUMERATES the claims in the prose and classifies each one as a PROPERTY or a READING.
⛔ A claim that carries a bare count is a READING (`CTO-63/6`). It is true at the ref it
was composed at and false at the next one, and a merge subject cannot be annotated
after it lands (Ruling 320). Exit `0` means every claim is a property. Exit `1` means a
claim is a reading, and the output names that claim and the count in it. Exit `2` means
no claim was read: an empty population is never the pass reading (Ruling 191).

**How you use it.** It is run before the merge, by whoever composes the subject:

    python3 -m tools.quality.subject "Merge fix/W<n>-slug (W<n>): <prose>"
    echo "$SUBJECT" | python3 -m tools.quality.subject

`read_subject(text)` returns the `Reading` that the command prints. The pass condition
lives in `docs/conventions/review-rubric.md`, under the `W149` heading beside Ruling 320.

**Depends on.** `argparse`, `re`, `sys` and `dataclasses`; `clauses.NUMBER_WORDS` for
the number words, and `markdown.strip_code_spans` for what counts as a mention.

## ⛔ WHAT IT MUST NOT BECOME (the row)

⛔ **It never edits a subject and never proposes one.** It REFUSES, and it names the
claim and the count. ⛔ **It is not in `CHECKS` or `NOTICES`, and it reads no history.**
A landed subject is frozen (Rulings 106, 174), and a report on frozen subjects is a
backlog that no office is permitted to clear. ⭐ It ADDS a reader and removes none: the
verdict token and the bracket are still read where they always were.

## ⚠️ DECIDED, AND DECLARED (Ruling 292)

⭐ **Decided, a count:** digits that stand alone (`57`, `0 of 25`, `3-5`), and a number
word from `two` upward. **Decided, not a count:** digits glued to an identifier (`W149`,
`INT-06/7`, `ab9e765`, `R12`, `§11.0`, `ISO-8583`), a date (`2026-09-12`), and digits
after a word in `NAMING` (`Ruling 320`, `Rulings 223-234`, `round 77`, `order 0`,
`exit 0`). A naming word binds a run of numerals joined by `,`, `and` or `-`.

⚠️ **Declared, not decided.** Each item is asserted SILENT in the mirror:

1. `one` and `zero` name a case (`one home`, `at zero ahead`) as often as they count;
2. a hyphen compound (`three-name contract`, `3-way`) names a kind;
3. an ordinal (`the second time`);
4. a code span is a mention, as it is for every reader in this package;
5. a quantifier with no numeral (`both`, `all`, `every`), which is the remedy's own form;
6. a reading that carries no count at all (`measured GREEN`).

⛔ **A claim ends at `;`, or at a dash (`--`, an em dash, an en dash) with spaces
around it.** A comma does not end a claim, so a count is reported against the longer
claim, never lost.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass

from tools.quality.clauses import NUMBER_WORDS
from tools.quality.markdown import strip_code_spans

#: Exit codes: `0` passed, `1` refused, `2` no claim read.
PASSED, REFUSED, UNREAD = 0, 1, 2

#: ⛔ A word that makes the numeral after it a NAME, not a count. A name is true at every ref.
NAMING = (
    "ruling",
    "rulings",
    "round",
    "rounds",
    "step",
    "steps",
    "wave",
    "waves",
    "milestone",
    "clause",
    "clauses",
    "item",
    "check",
    "section",
    "order",
    "answer",
    "exit",
    "exits",
    "version",
)

_WORDS = sorted((word for word, value in NUMBER_WORDS.items() if value >= 2), key=len)
_DIGITS = r"\d+(?:[.,]\d+)*"
_NUMERAL = rf"(?:{_DIGITS}|{'|'.join(reversed(_WORDS))})"
_NAMED_RUN = re.compile(
    rf"\b(?:{'|'.join(NAMING)})\s+{_NUMERAL}(?:(?:\s*,\s*|\s+and\s+|\s*[-–]\s*){_NUMERAL})*\b",
    re.IGNORECASE,
)
_DATE = re.compile(r"(?<![\w-])\d{4}-\d{2}-\d{2}(?![\w-])")
_BARE_DIGITS = re.compile(
    rf"(?<![\w/#§.\-–]){_DIGITS}(?:[-–]{_DIGITS})?(?![\w/]|[-–][^\W\d])", re.UNICODE
)
_BARE_WORD = re.compile(rf"(?<![\w\-–])(?:{'|'.join(reversed(_WORDS))})(?![\w\-–])", re.I)
_HEADER = re.compile(r"^Merge\s+\S+(?:\s+\([^)]*\))?:\s*")
_BRACKET = re.compile(r"\s*\(CTO:[^)]*\)\s*$")
_CLAIM_END = re.compile(r"\s*;\s*|\s+(?:--|—|–)\s+")


@dataclass(frozen=True)
class Claim:
    """One claim of a subject's prose, and the bare counts that make it a reading."""

    text: str
    counts: tuple[str, ...]

    @property
    def is_property(self) -> bool:
        """Report whether the claim holds at every ref, which means it carries no bare count."""
        return not self.counts


@dataclass(frozen=True)
class Reading:
    """A subject's claims, in order. The header and the verdict bracket are not claims."""

    claims: tuple[Claim, ...]

    @property
    def verdict(self) -> int:
        """Return the exit code: passed, refused, or unread when no claim was read."""
        if not self.claims:
            return UNREAD
        return PASSED if all(claim.is_property for claim in self.claims) else REFUSED


def bare_counts(claim: str) -> tuple[str, ...]:
    """Return every bare count in `claim`, in order, with mentions and names blanked first."""
    text = strip_code_spans(claim)
    for name in (_DATE, _NAMED_RUN):
        text = name.sub(lambda match: " " * len(match.group(0)), text)
    found = [(m.start(), m.group(0)) for m in _BARE_DIGITS.finditer(text)]
    found += [(m.start(), m.group(0)) for m in _BARE_WORD.finditer(text)]
    return tuple(spelling for _, spelling in sorted(found))


def prose(subject: str) -> str:
    """Return the subject's prose: its first line, without the header or a verdict bracket."""
    lines = subject.strip().splitlines()
    line = lines[0] if lines else ""
    return _BRACKET.sub("", _HEADER.sub("", line, count=1)).strip()


def read_subject(subject: str) -> Reading:
    """Enumerate the claims of `subject` and classify each one."""
    parts = [part.strip() for part in _CLAIM_END.split(prose(subject))]
    return Reading(tuple(Claim(part, bare_counts(part)) for part in parts if part))


def render(reading: Reading) -> list[str]:
    """Return the lines the command prints: the population, each claim, then the answer."""
    lines = [
        f"merge subject: {len(reading.claims)} claim(s) read "
        "(the header and a verdict bracket are not claims)"
    ]
    for number, claim in enumerate(reading.claims, start=1):
        kind = "PROPERTY" if claim.is_property else "READING "
        lines.append(f"  claim {number}  {kind}  {claim.text}")
    if reading.verdict == UNREAD:
        lines.append("⛔ UNREAD: the subject has no prose, so no claim was read (exit 2)")
    for number, claim in enumerate(reading.claims, start=1):
        if not claim.is_property:
            counts = ", ".join(f"`{count}`" for count in claim.counts)
            lines.append(
                f"⛔ REFUSED: claim {number} is a READING, because it carries the bare count "
                f"{counts} (review-rubric.md, W149; CTO-63/6, Ruling 320)"
            )
    if reading.verdict == PASSED:
        lines.append("⭐ PASSED: every claim is a PROPERTY")
    return lines


def main(argv: list[str] | None = None) -> int:
    """Read a subject from the argument or from stdin, print the reading, return the exit."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.quality.subject",
        description="Refuse a merge subject whose prose carries a bare count (W149).",
    )
    parser.add_argument("subject", nargs="?", help="the subject; read from stdin if absent")
    arguments = parser.parse_args(argv)
    text = arguments.subject if arguments.subject is not None else sys.stdin.read()
    reading = read_subject(text)
    print("\n".join(render(reading)))
    return reading.verdict


if __name__ == "__main__":  # pragma: no cover - the CLI's one line
    sys.exit(main())
