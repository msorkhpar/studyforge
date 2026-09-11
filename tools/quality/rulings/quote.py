"""Quoting a record without paraphrasing it: what to quote, and how to cut it.

**What it does.** Decides the quotable UNIT around a line (one standalone line,
or the whole wrapped paragraph it belongs to) and turns that unit into a table
cell — windowed on the citation, with every cut MARKED.

**How you use it.** `passage(lines, index)` is the unit; `cell(passage, number)`
is the cell. `derive` calls both, and nothing else calls either.

**Depends on.** `re` alone. ⛔ A one-way seam: `quote` knows nothing about
records, rounds or rulings beyond the spelling of a citation, and `derive`
imports it and never the reverse (Ruling 132 — a one-way seam is a valid R11
split, and this one was forced by R11's ceiling rather than chosen).

## ⛔ Why a quote is windowed and never shortened

⚠️ **Ruling 195 forbids a row file paraphrasing the ruling that scoped it**, and
an index row is the same shape at a larger scale: 197 paraphrases would be 197
statements that can be kept freshly wrong. ⭐ **So nothing here rewrites
anything.** A passage too long for a cell is CUT, both cuts are marked with `…`,
and ⛔ **the cut is anchored on the citation** — a window that dropped
`Ruling 70` out of Ruling 70's own quote would leave a reader holding a sentence
with no subject.
"""

from __future__ import annotations

import re

__all__ = ["ELLIPSIS", "QUOTE_LIMIT", "cell", "passage"]

#: How much of a quoted passage a cell carries. ⚠️ A truncation is MARKED at
#: both ends, and a marked truncation is still a quotation; an unmarked one
#: would be a paraphrase.
QUOTE_LIMIT = 190
ELLIPSIS = "…"

#: How far past the citation a window may run when the passage has to be cut
#: from the left: enough to see what the sentence does with the number.
_TRAILING = 24

#: A line that is its own quotable unit: a heading, a table row, a list item or
#: a blockquote. ⛔ Everything else is part of a wrapped paragraph, and quoting
#: one wrapped line hands the reader a sentence fragment — measured on Rulings
#: 65, 70, 71 and 76, whose only statement anywhere is mid-paragraph.
_STANDALONE = re.compile(r"^\s*(?:#{1,6}\s|[|>]|[-*+]\s|\d+[a-z]?\.\s)")

#: A quote that opens cleanly, at a marker, a capital or a delimiter. ⭐ One
#: that does not began mid-sentence — under a list marker, or after a fence —
#: and is marked with the same ellipsis a truncation gets.
_OPENS_CLEANLY = re.compile(r"^[⛔⭐⚠️✅…#|>*_`\-\[(\"'A-Z0-9§]")


def passage(lines: list[tuple[int, str]], index: int) -> str:
    """Return the quotable unit at `index`: one standalone line, or its paragraph.

    `lines` is `(line number, line)` for the document's prose, as
    `pointers.prose_lines` returns it.

    ⭐ A paragraph is the run of adjacent wrapped prose lines around `index`,
    adjacent **by line number** — a run interrupted by a fenced block is two
    paragraphs, because `prose_lines` never hands back what was inside the fence.
    """
    line = lines[index][1]
    if _STANDALONE.match(line):
        return line
    first = last = index
    while first > 0:
        number, previous = lines[first - 1]
        if number != lines[first][0] - 1 or not previous.strip() or _STANDALONE.match(previous):
            break
        first -= 1
    while last + 1 < len(lines):
        number, following = lines[last + 1]
        if number != lines[last][0] + 1 or not following.strip() or _STANDALONE.match(following):
            break
        last += 1
    return " ".join(text for _number, text in lines[first : last + 1])


def _window(text: str, number: int) -> str:
    """Return at most `QUOTE_LIMIT` characters of `text` that CONTAIN the citation."""
    if len(text) <= QUOTE_LIMIT:
        return text
    match = re.search(rf"Ruling\s+{number}\b", text)
    end = match.end() if match else 0
    if end + len(ELLIPSIS) <= QUOTE_LIMIT:
        return text[:QUOTE_LIMIT].rstrip() + f" {ELLIPSIS}"
    stop = min(len(text), end + _TRAILING)
    start = max(0, stop - QUOTE_LIMIT)
    opened = f"{ELLIPSIS} " if start else ""
    closed = f" {ELLIPSIS}" if stop < len(text) else ""
    return opened + text[start:stop].strip() + closed


def cell(text: str, number: int) -> str:
    r"""Return `text` as a table cell: windowed on the citation, pipes escaped.

    ⚠️ `|` becomes `\|` because a quoted table row is still a quote and still
    has to survive being placed in a table. It is the only character changed.
    """
    squeezed = " ".join(text.split())
    windowed = _window(squeezed, number)
    if windowed and not _OPENS_CLEANLY.match(windowed):
        windowed = f"{ELLIPSIS} {windowed}"
    return windowed.replace("|", r"\|")
