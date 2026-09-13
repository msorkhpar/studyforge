"""`W151`: Python prose may not state a BARE COUNT of a population the file does not own.

**What it does.** Reads the prose of every Python file under `config.SCAN_ROOTS`
— module, class and function docstrings, and comments — and finds each numeral
or number word that COUNTS one of the derived populations declared in
`POPULATIONS`. ⛔ A count is BARE unless its own sentence carries the ref it was
measured at (Ruling 277), and a bare count is a finding: nothing re-derives a
scalar typed into prose, so it goes stale the first time its population grows
(Ruling 150's mechanism, arriving in docstrings).

**How you use it.** `check_derived_counts(root)` is registered in
`tools.quality.CHECKS` and fails the floor on every bare count;
`count_census(root)` is registered in `NOTICES` and prints the population, bare
and dated apart, so a green exit carries its denominator. `counts(path, source)`
is the per-file reading both are built on.

**Depends on.** `ast`, `io`, `re`, `tokenize` and `dataclasses`;
`tools.quality.clauses` for `NUMBER_WORDS`, `tools.quality.markdown` for
`strip_code_spans`, `config` for the walk and `report` for the answer.

## ⛔ THE REMEDY IS A PROPERTY, NEVER A CORRECTED FIGURE

⭐ `every markdown file of this tree` states the same fact as
`all 400 markdown files of this tree` and cannot go stale. ⛔ Correcting `400` to `399`
buys exactly one round, which is why the finding never prints the current figure.

## ⚠️ WHAT IT DECIDES, AND WHAT IT DECLARES (Ruling 292)

⭐ **Decided:** a number (digits, or a word from `clauses.NUMBER_WORDS`) directly
before a `POPULATIONS` noun, matched across the line breaks of one paragraph,
and an ordinal before *declared gap*. ⛔ **Mentions are not read:** a code span,
a docstring line quoted with `>`, a fenced block. Each is asserted in the mirror.
⚠️ A span opened at a line's end and closed on the NEXT line is a mention too
(`test_pointers.py` quotes a floor reading that way); one reaching further is not
blanked, so a stray backtick cannot hide a paragraph.

⚠️ **Declared, not decided, and each is asserted SILENT in the mirror:**

1. a count of any population outside `POPULATIONS` (rulings, tasks, sites);
2. an anaphoric count whose noun is elided (*"these two"*);
3. a count inside a string literal that is not a docstring (a message, a fixture);
4. markdown documents — `W69`'s bare TASK count in `CLAUDE.md` and
   `docs/tasks/README.md` is that row's predicate, and this one reads Python alone;
5. a ref in the sentence dates every count in it, whether or not it governs it;
6. a count of a fixture's own files is refused like any other: write *both*.

⛔ **A sentence ends at `.`, `!` or `?` before whitespace, outside a code span.**
Splitting too often makes a count LESS likely to be dated, which is the safe
direction: a ref two sentences back dates nothing (`reach.py`, measured at `1e70007`).
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.clauses import NUMBER_WORDS
from tools.quality.markdown import strip_code_spans
from tools.quality.report import Finding

RULE_COUNTS = "derived-count"

_NUMBER = r"(?:" + "|".join(NUMBER_WORDS) + r"|\d[\d,]*)(?:-odd)?"
_ORDINAL = r"(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)"


@dataclass(frozen=True)
class Population:
    """A population the floor can derive, the noun prose counts it by, and its source."""

    noun: str
    source: str
    pattern: re.Pattern[str]


#: ⛔ A CLOSED list: a noun is added here with the source it is derived from, or
#: a count of it is declared undecided (the module docstring's first gap).
POPULATIONS = (
    Population(
        "markdown files",
        "the tree's markdown files, derived by `config.markdown_population`",
        re.compile(rf"\b{_NUMBER}\s+(?:(?:tracked|live)\s+)?markdown\s+files?\b", re.I),
    ),
    Population(
        "declared gaps",
        "the gaps `citations.py` and `reach.py` declare; `reach._GAPS` counts the grammar's",
        re.compile(
            rf"\b{_NUMBER}\s+(?:of\s+the\s+{_NUMBER}\s+)?declared\s+gaps?\b"
            rf"|\b{_NUMBER}\s+of\s+the\s+{_NUMBER}\s+gaps\b"
            rf"|\b{_ORDINAL}\s+declared\s+gaps?\b",
            re.I,
        ),
    ),
)

#: A ref: seven to forty hex characters with at least one digit and one letter,
#: so neither a word nor a decimal figure reads as one.
_REF = re.compile(r"(?<![\w/-])(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![\w/-])")

#: A code span crossing ONE line break, after `strip_code_spans` blanked each line's own.
_WRAPPED_SPAN = re.compile(r"`[^`\n]*\n[^`\n]*`")

#: Where a sentence ends: terminal punctuation, an optional closing `**`, whitespace.
_SENTENCE_END = re.compile(r"[.!?](?:\*\*)?\s")


@dataclass(frozen=True)
class Count:
    """One count of a derived population, where it stands and whether it is dated."""

    path: str
    line: int
    population: str
    spelling: str
    dated: bool


def _docstring_lines(tree: ast.AST, lines: list[str]) -> list[tuple[int, str]]:
    """Every docstring line, blanks kept, with quotations and fences blanked."""
    found: list[tuple[int, str]] = []
    kinds = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for node in ast.walk(tree):
        if not isinstance(node, kinds) or not node.body:
            continue
        first = node.body[0]
        if not (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)):
            continue
        if not isinstance(first.value.value, str):
            continue
        fenced = False
        for number in range(first.lineno, (first.end_lineno or first.lineno) + 1):
            text = lines[number - 1]
            stripped = text.strip()
            if stripped.startswith("```"):
                fenced = not fenced
                text = ""
            elif fenced or stripped.startswith(">"):
                text = ""
            found.append((number, text))
        found.append((0, ""))  # a docstring's end is a paragraph's end
    return found


def _comment_lines(source: str) -> list[tuple[int, str]]:
    """Every comment's text with its line, a bare `#` or `#:` kept as a blank."""
    found: list[tuple[int, str]] = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                found.append((token.start[0], token.string.lstrip("#:")))
    except tokenize.TokenError, IndentationError:
        return []
    return found


def _paragraphs(lines: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    """Split numbered prose lines into paragraphs at blanks and at line-number gaps."""
    paragraphs: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for number, text in lines:
        if not text.strip() or (current and number != current[-1][0] + 1):
            if current:
                paragraphs.append(current)
            current = []
        if text.strip():
            current.append((number, text))
    if current:
        paragraphs.append(current)
    return paragraphs


def _sentence(prose: str, start: int, end: int) -> tuple[int, int]:
    """Return the bounds of the sentence in `prose` holding the span `start`–`end`."""
    low = 0
    for match in _SENTENCE_END.finditer(prose, 0, start):
        low = match.end()
    later = _SENTENCE_END.search(prose, end)
    return low, later.start() + 1 if later else len(prose)


def counts(path: str, source: str) -> list[Count]:
    """Every count of a `POPULATIONS` member in `source`'s docstrings and comments."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    lines = source.splitlines()
    found: list[Count] = []
    for lines_of in (_docstring_lines(tree, lines), _comment_lines(source)):
        for paragraph in _paragraphs(lines_of):
            raw = "\n".join(text for _, text in paragraph)
            prose = _WRAPPED_SPAN.sub(
                lambda span: re.sub(r"[^\n]", " ", span.group()),
                "\n".join(strip_code_spans(text) for _, text in paragraph),
            )
            for population in POPULATIONS:
                for match in population.pattern.finditer(prose):
                    low, high = _sentence(prose, match.start(), match.end())
                    line = paragraph[prose.count("\n", 0, match.start())][0]
                    dated = _REF.search(raw, low, high) is not None
                    spelling = " ".join(match.group().split())
                    found.append(Count(path, line, population.noun, spelling, dated))
    return sorted(found, key=lambda count: (count.path, count.line, count.spelling))


def scan(root: Path) -> tuple[int, list[Count]]:
    """Read every Python file under the scan roots once: `(files read, counts)`."""
    files = config.python_files(root)
    found: list[Count] = []
    for path in files:
        source = config.read_text(path)
        if source is not None:
            found.extend(counts(config.relative(path, root), source))
    return len(files), found


def _source(noun: str) -> str:
    """Return the derivation source `POPULATIONS` declares for `noun`."""
    return next(population.source for population in POPULATIONS if population.noun == noun)


def check_derived_counts(root: Path) -> list[Finding]:
    """Return one finding per bare count of a derived population in Python prose."""
    return [
        Finding(
            count.path,
            count.line,
            RULE_COUNTS,
            f"states {count.spelling!r}, a bare count of {count.population} — "
            f"{_source(count.population)} — which nothing re-derives. Write the fact as a "
            f"PROPERTY (`every markdown file of this tree`, `the grammar's declared gaps`) "
            f"or put the ref it was measured at in the same sentence (Ruling 277). "
            f"⛔ Correcting the figure buys one round (W151).",
        )
        for count in scan(root)[1]
        if not count.dated
    ]


def count_census(root: Path) -> list[str]:
    """Print every count of a derived population, bare and dated apart, green run or red."""
    files, found = scan(root)
    bare = [count for count in found if not count.dated]
    lines = [
        f"derived counts: {len(found)} count(s) of {len(POPULATIONS)} declared populations "
        f"({', '.join(population.noun for population in POPULATIONS)}) in the prose of "
        f"{files} Python files; {len(bare)} bare, {len(found) - len(bare)} dated to a ref "
        f"in their own sentence. A count of any other population is not read."
    ]
    for count in found:
        verdict = "dated" if count.dated else "BARE"
        lines.append(f"  {count.path}:{count.line} {count.spelling!r} — {verdict}")
    return lines


__all__ = [
    "POPULATIONS",
    "RULE_COUNTS",
    "Count",
    "Population",
    "check_derived_counts",
    "count_census",
    "counts",
    "scan",
]
