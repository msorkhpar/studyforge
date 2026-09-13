r"""LOCATION citations — a `<path>:<line>` in a LIVE document, read for its PATH and its INTEGER.

**What it does.** Reads every tracked live document — markdown whole, Python as its
comments and docstrings — finds every citation spelled `<path>:<line>`, and gives each
exactly ONE verdict: *the path does not resolve*, *the integer moves*, or admitted. The
population is printed as a notice, the two harms counted apart.

**How you use it.** `classify(document, lines, tracked)` is the predicate; `scan(root)` is
the one pass; `location_notice(root)` is registered in `tools.quality.NOTICES`;
`remedy(verdict)` is Ruling 163's remedy for a harm.

**Depends on.** `ast`, `io`, `posixpath`, `re`, `tokenize`, `dataclasses`, `functools`, `pathlib`,
`tools.quality.config`, `tools.quality.handoffs` for the record directory, and
`tools.quality.report` for the walk caveat. Standard library only.

## ⛔ TWO HARMS, TWO VERDICTS — never one predicate with one message (`W150`)

⭐ **Ruling 163 forbids the INTEGER into a file a live document does not own. It says
nothing about the PATH**, so a bare basename satisfied its letter while being strictly
worse: the integer cannot be checked and the file cannot be found (`W78/3`). ⛔ **Ruling
185(b): the class is its own verdict, not a widening of 163's.** The path is asked FIRST,
because an integer into a file nobody can find has no second question.

| Verdict | Fires when | Harm |
|---|---|---|
| `PATH` | names no tracked file from the root or the document | ⛔ the path does not resolve |
| `INTEGER` | the path resolves to a file the document does not own | ⛔ the integer moves |
| `OWN` | the path resolves to the citing document itself | none — it owns the file |
| `REF` | an `INTEGER` inside a fence whose block names a sha or a date | none — Ruling 169 |

⚠️ **`REF` admits the INTEGER and never the PATH**: Ruling 169 speaks about a reading's
integer, so a fenced reading that cites an unresolvable basename is still `PATH`.

## ⛔ THE POPULATION, AND WHAT IS NOT IN IT BY NAME (Rulings 106, 174, 292)

⭐ **LIVE = tracked `.md` and `.py`, minus the RECORDS** — `HANDOFF_DIR` and
`docs/tasks/BOARD-ARCHIVE.md`. ⛔ A record is a reading taken at an instant and no office
may edit it, so a notice over records would print what nobody can remedy. ⭐ **The declared
non-members, each asserted in the mirror rather than forced into a verdict:**

| Non-member | Why | Printed as |
|---|---|---|
| a Python string literal | a FIXTURE member, not prose | `in string literals` |
| a suffix no tracked file has | NOT A PATH: a `host:port`, a ratio | `with no tracked suffix` |
| a backslash before the path | `W78/3`'s PARSE GAP: a `\n` escape read as `n` | not counted |

## ⚠️ A NOTICE, NOT A CHECK — and what would promote it

⛔ **At `79db35b` the path harm's live members sit in `docs/conventions/`, `rows/` and
test comments that no office of this row may edit**, so a gate would be red for work no
office holds (Ruling 245's form). ⭐ The notice prints every `PATH` member by site, so the
population is read rather than assumed; a later row promotes it once the residue is zero.

## ⛔ WHAT THIS CANNOT SEE — a closed claim (Ruling 258)

1. ⛔ A bare `:<n>` continuing an earlier citation carries no path and is not read.
2. ⛔ A citation QUOTED as a refused example is a mention and is read as a citation.
3. ⛔ A basename that happens to resolve at the root — `README.md` — resolves, whichever
   of the tree's same-named files its author meant (`W78/4`).
4. ⚠️ A ref written in DIGITS ONLY is not read as a ref, so its fenced reading reads
   `INTEGER`: a seven-digit sha and a seven-digit count look the same (found by plant).
"""

from __future__ import annotations

import ast
import io
import posixpath
import re
import tokenize
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from tools.quality import config
from tools.quality.handoffs import HANDOFF_DIR
from tools.quality.report import WALK_CAVEAT

#: The records: read as readings at an instant, edited by nobody (Rulings 106, 174).
RECORDS = (f"{HANDOFF_DIR}/", "docs/tasks/BOARD-ARCHIVE.md")

#: ⛔ The two harms, SPELLED so a reader knows which one fired (`W150`'s clause 1).
HARM_PATH = "the path does not resolve"
HARM_INTEGER = "the integer moves"

#: The four verdicts. Two are harms; two are admissions.
PATH = "PATH"
INTEGER = "INTEGER"
OWN = "OWN"
REF = "REF"

#: `W78`'s spelling, with a backslash added to the look-behind: a `\n` escape before a
#: basename no longer reads as a path that starts with `n`.
_CITATION = re.compile(
    r"(?<![\w/.:\\-])(?P<path>(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?P<suffix>[A-Za-z0-9]+))"
    r":(?P<line>\d+)"
)

#: A REF in a fenced block (Ruling 169): a sha of 7-40 hex digits carrying a letter AND a
#: digit, or an ISO date.
_REF = re.compile(
    r"(?<![0-9A-Za-z])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,40}(?![0-9A-Za-z])"
    r"|\b\d{4}-\d{2}-\d{2}\b"
)

#: Python's literal-string token kinds, where the running version has them.
_LITERALS = frozenset(
    getattr(tokenize, kind)
    for kind in ("STRING", "FSTRING_MIDDLE", "TSTRING_MIDDLE")
    if hasattr(tokenize, kind)
)


@dataclass(frozen=True)
class Citation:
    """One `<path>:<line>` citation and its verdict."""

    document: str
    line: int
    spelling: str
    verdict: str


@dataclass(frozen=True)
class Scan:
    """One pass: the citations, the documents read, the walk, and the non-members counted."""

    citations: tuple[Citation, ...]
    documents: int
    walk: str
    literals: int
    pathless: int


@lru_cache(maxsize=4)
def _suffixes(tracked: frozenset[str]) -> frozenset[str]:
    """Every file suffix the tracked tree carries: what a citation's suffix must be one of."""
    return frozenset(posixpath.splitext(name)[1][1:] for name in tracked)


def resolve(document: str, path: str, tracked: frozenset[str]) -> str | None:
    """Return the tracked file `path` names from the root or from `document`, else None."""
    if path in tracked:
        return path
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(document), path))
    return joined if joined in tracked else None


def _fenced_refs(lines: list[tuple[int, str]]) -> dict[int, bool]:
    """Map each line inside a ``` fence to whether its block names a ref (Ruling 169)."""
    inside: dict[int, bool] = {}
    block: list[int] | None = None
    carries = False
    for number, line in lines:
        if line.lstrip().startswith("```"):
            if block is None:
                block, carries = [], False
            else:
                inside.update(dict.fromkeys(block, carries))
                block = None
            continue
        if block is not None:
            block.append(number)
            carries = carries or bool(_REF.search(line))
    if block is not None:
        inside.update(dict.fromkeys(block, carries))
    return inside


def classify(
    document: str, lines: list[tuple[int, str]], tracked: frozenset[str]
) -> tuple[list[Citation], int]:
    """Return each citation in `lines` with its verdict, and the non-paths refused.

    ⛔ **The PATH is asked before the INTEGER**, so an unresolvable citation is never
    reported as a moving integer and a resolving one is never reported as a lost path.
    """
    suffixes = _suffixes(tracked)
    fenced = _fenced_refs(lines)
    found: list[Citation] = []
    pathless = 0
    for number, line in lines:
        for match in _CITATION.finditer(line):
            if match.group("suffix") not in suffixes:
                pathless += 1
                continue
            target = resolve(document, match.group("path"), tracked)
            if target is None:
                verdict = PATH
            elif target == document:
                verdict = OWN
            elif fenced.get(number):
                verdict = REF
            else:
                verdict = INTEGER
            found.append(Citation(document, number, match.group(0), verdict))
    return found, pathless


def python_prose(text: str) -> tuple[list[tuple[int, str]], list[str]]:
    """Return a module's comment and docstring lines, and its string literals apart.

    ⚠️ A module that does not parse yields nothing: the style floor already fails it.
    """
    try:
        tree = ast.parse(text)
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except SyntaxError, tokenize.TokenError, ValueError:
        return [], []
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            first = body[0] if body else None
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                if isinstance(first.value.value, str):
                    docstrings.update(range(first.lineno, (first.end_lineno or 0) + 1))
    source = text.splitlines()
    prose = [(number, source[number - 1]) for number in sorted(docstrings)]
    literals: list[str] = []
    for token in tokens:
        if token.type == tokenize.COMMENT:
            prose.append((token.start[0], token.string))
        elif token.type in _LITERALS and token.start[0] not in docstrings:
            literals.append(token.string)
    return sorted(prose), literals


def _universe(root: Path) -> tuple[frozenset[str], list[Path], str]:
    """Return the resolvable names, the live documents, and the walk that found them."""
    population = config.markdown_population(root)
    tracked = config.tracked_paths(root)
    python = [path for path in config.text_files(root) if path.suffix == ".py"]
    if tracked is None:
        names = frozenset(config.relative(path, root) for path in config.text_files(root))
    else:
        names = frozenset(config.relative(path, root) for path in tracked)
        python = [path for path in python if path in tracked]
    documents = [
        path
        for path in [*population.paths, *python]
        if not config.relative(path, root).startswith(RECORDS)
    ]
    return names, sorted(documents), population.walk


def scan(root: Path) -> Scan:
    """Read every live document once and return every citation with its verdict."""
    names, documents, walk = _universe(root)
    citations: list[Citation] = []
    literals = pathless = read = 0
    for path in documents:
        text = config.read_text(path)
        if text is None:
            continue
        read += 1
        name = config.relative(path, root)
        if path.suffix == ".py":
            lines, strings = python_prose(text)
            literals += sum(len(classify(name, [(0, s)], names)[0]) for s in strings)
        else:
            lines = list(enumerate(text.splitlines(), start=1))
        found, refused = classify(name, lines, names)
        citations.extend(found)
        pathless += refused
    return Scan(tuple(citations), read, walk, literals, pathless)


def remedy(verdict: str) -> str:
    """Return Ruling 163's remedy for a harm: the command's output shape, re-runnable."""
    if verdict == PATH:
        return (
            f"{HARM_PATH}: write the path from the repository root so a reader can find the "
            f"file, and cite the command that prints the line, never the integer — "
            f"`grep -n '<text on that line>' <tracked path>` prints `<n>:<text>` (Ruling 163)"
        )
    return (
        f"{HARM_INTEGER}: cite the command and its output shape, never the integer "
        f"(Ruling 163); a fenced reading is admitted when its block names its ref (Ruling 169)"
    )


def location_notice(root: Path) -> list[str]:
    """Print the live population by verdict, and every `PATH` member by site.

    ⛔ **A notice and never a finding** — see the module docstring for why and for what
    promotes it. ⭐ Both harms are counted APART, and the non-members beside them, so a
    `0` is never read without its denominator (Ruling 48).
    """
    result = scan(root)
    counts = {verdict: 0 for verdict in (PATH, INTEGER, OWN, REF)}
    for citation in result.citations:
        counts[citation.verdict] += 1
    lines = [
        f"location citations: {len(result.citations)} read in {result.documents} live "
        f"documents ({result.walk} walk, records excluded) — {HARM_PATH}: {counts[PATH]}; "
        f"{HARM_INTEGER}: {counts[INTEGER]}; admitted: {counts[OWN]} own line, "
        f"{counts[REF]} fenced with a ref; not read: {result.literals} in string literals, "
        f"{result.pathless} with no tracked suffix.{WALK_CAVEAT[result.walk]}"
    ]
    paths = [citation for citation in result.citations if citation.verdict == PATH]
    lines.extend(f"  {c.document}:{c.line} cites `{c.spelling}`" for c in paths)
    if paths:
        lines.append(f"  remedy — {remedy(PATH)}")
    return lines


__all__ = [
    "HARM_INTEGER",
    "HARM_PATH",
    "INTEGER",
    "OWN",
    "PATH",
    "RECORDS",
    "REF",
    "Citation",
    "Scan",
    "classify",
    "location_notice",
    "python_prose",
    "remedy",
    "resolve",
    "scan",
]
