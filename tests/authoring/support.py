"""Reading `docs/authoring/` as data, so its claims can be compared to the code.

**What it does.** Turns the authoring reference into structures a test can
assert against: the documents, their sections, their tables, and their fenced
blocks.

**How you use it.** `document(name)` for one document's text, `documents()` for
all of them, `rows_under(text, heading)` for a table's cells, `fences(text)`
for the code blocks, and `vocabulary_under(text, heading)` for the backticked
first column that names a closed set.

**Depends on.** `pathlib`, `re`, `json` and `tests.support`. ⛔ Nothing under
`src/` — this half reads the document; the assertions import the code.

⚠️ **The parsers here are deliberately small and strict.** A lenient markdown
parser that silently found nothing would turn every check that reads it into a
check that cannot fail, which is the failure mode this whole module exists to
avoid. Each accessor raises when it finds no subject.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from tests.support import repository_root

#: Where the reference lives, relative to the repository root.
AUTHORING = "docs/authoring"

#: The document every other one is reached from. ⛔ Named here rather than in
#: each test, because "is this document reachable" needs one definition of
#: where reachability starts.
INDEX = "README.md"

#: A markdown heading: the hashes, then the text.
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")

#: A fenced block's opening line, with whatever info string it carries.
_FENCE = re.compile(r"^```(\S*)\s*$")

#: An inline code span. ⚠️ Single backticks only: a vocabulary is written
#: `like-this`, and a doubled span in the reference would be quoting markdown
#: rather than naming a value.
_CODE_SPAN = re.compile(r"`([^`]+)`")

#: An escaped pipe inside a table cell, which must survive the split that
#: separates cells. ⚠️ `<lesson\|practice>` is a real cell in `validate.md`.
_ESCAPED_PIPE = "\x00"


def authoring_root() -> Path:
    """Return the directory holding the reference."""
    return repository_root() / AUTHORING


def document_paths() -> list[Path]:
    """Every markdown document in the reference, sorted."""
    paths = sorted(authoring_root().glob("*.md"))
    if not paths:
        raise AssertionError(f"{AUTHORING}/ holds no markdown documents at all")
    return paths


def documents() -> dict[str, str]:
    """Map every document's filename to its text."""
    return {path.name: path.read_text(encoding="utf-8") for path in document_paths()}


def document(name: str) -> str:
    """Return one document's text, or fail naming what is missing."""
    path = authoring_root() / name
    if not path.is_file():
        raise AssertionError(f"{AUTHORING}/{name} does not exist")
    return path.read_text(encoding="utf-8")


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Return `(line number, line)` for every line outside a fenced block.

    ⛔ Fence-aware, and it is not an optimisation. A fenced block is quoted
    material: its `#` is not a heading and its backticks pair with each other,
    so a walk that read it would mis-pair every code span in the rest of the
    document — which is exactly what this module's first run did.
    """
    kept: list[tuple[int, str]] = []
    inside = False
    for number, line in enumerate(text.splitlines()):
        if _FENCE.match(line):
            inside = not inside
            continue
        if not inside:
            kept.append((number, line))
    return kept


def section(text: str, heading: str) -> str:
    """Return the lines under `heading`, up to the next heading of its level or higher.

    `heading` is matched against the heading's text with its hashes stripped,
    so a caller writes the words rather than the markup.
    """
    lines = text.splitlines()
    start = None
    depth = 0
    for number, line in prose_lines(text):
        match = _HEADING.match(line)
        if match is None:
            continue
        if start is None:
            if match.group(2).strip() == heading:
                start, depth = number + 1, len(match.group(1))
            continue
        if len(match.group(1)) <= depth:
            return "\n".join(lines[start:number])
    if start is None:
        raise AssertionError(f"no section titled {heading!r}; the reference was reorganised")
    return "\n".join(lines[start:])


def rows_under(text: str, heading: str) -> list[list[str]]:
    """Return every table row under `heading` as a list of stripped cells.

    Header rows and the `|---|` separator are dropped: a row is kept only when
    it follows a separator in the same table.
    """
    rows: list[list[str]] = []
    live = False
    for line in section(text, heading).splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            live = False
            continue
        cells = _cells(stripped)
        if all(set(cell) <= {"-", ":"} and cell for cell in cells):
            live = True
            continue
        if live:
            rows.append(cells)
    if not rows:
        raise AssertionError(f"the table under {heading!r} has no body rows")
    return rows


def _cells(line: str) -> list[str]:
    """Split one table line into cells, keeping escaped pipes inside them."""
    guarded = line.replace("\\|", _ESCAPED_PIPE)
    return [cell.strip().replace(_ESCAPED_PIPE, "|") for cell in guarded.strip("|").split("|")]


def vocabulary_under(text: str, heading: str, column: int = 0) -> set[str]:
    """Return the backticked tokens in one column of the table under `heading`.

    ⛔ Backticked, never bare: a cell that names a value writes it in code
    spans, and reading bare prose would let a sentence about a value be
    mistaken for the value.
    """
    found: set[str] = set()
    for row in rows_under(text, heading):
        if column >= len(row):
            continue
        found.update(_CODE_SPAN.findall(row[column]))
    if not found:
        raise AssertionError(f"column {column} under {heading!r} names no backticked value")
    return found


def fences(text: str, info: str | None = None) -> list[str]:
    """Return every fenced block's body, optionally only those with `info`."""
    found: list[str] = []
    body: list[str] | None = None
    opened = ""
    for line in text.splitlines():
        match = _FENCE.match(line)
        if match is None:
            if body is not None:
                body.append(line)
            continue
        if body is None:
            body, opened = [], match.group(1)
            continue
        if info is None or opened == info:
            found.append("\n".join(body))
        body = None
    return found


def json_fences(text: str) -> list[dict]:
    """Every ```json block in `text`, parsed. ⛔ A block that is not JSON fails here."""
    parsed = []
    for number, body in enumerate(fences(text, "json"), start=1):
        try:
            parsed.append(json.loads(body))
        except json.JSONDecodeError as error:  # pragma: no cover - the failure is the point
            raise AssertionError(f"json block {number} does not parse: {error}") from error
    return parsed


def code_spans(text: str) -> set[str]:
    """Every inline code span in `text`, read outside the fenced blocks."""
    found: set[str] = set()
    for _, line in prose_lines(text):
        found.update(_CODE_SPAN.findall(line))
    return found
