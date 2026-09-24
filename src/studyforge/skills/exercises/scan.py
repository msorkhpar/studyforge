r"""What a raw material file carries: its fenced blocks, and the headings over each.

**What it does.** Walks Markdown **as bytes on disk** and answers one question
the framework had no answer to — *which headings enclose this fenced block?*
It reports; it decides nothing and refuses nothing.

**How you use it.** `scan(text)` returns a `Scan`: every `Fence` in the order
the file carries them, every heading it carries outside a fence, and whether
the file ended inside a fence.

**Depends on.** `dataclasses`, and `studyforge.validate.headings` for
`HEADING_LINE` and `FENCE`. ⛔ **Nothing else, and never `archive.markdown`** —
see below. Standard library only.

## ⛔ IT BORROWS THE TWO PATTERNS AND NOT THE WALK

⭐ **`validate.headings` owns what a heading is and what a fence is**, so this
module imports both patterns rather than writing a second pair that could drift
from them. ⚠️ **What it cannot borrow is the WALK**: `headings()` skips fenced
regions by design and `region()` answers about one named section, and neither
can say which headings enclose a *fence*, because neither records where a fence
is. ⭐ So the shared thing is the grammar and the new thing is the traversal,
which is the split that leaves one definition of each in the tree.

## ⛔ THE MARKDOWN READER IS NOT USED, AND THAT IS THE REGION RULE'S REASON

⚠️ **The ledger exists to say what the SOURCE carries.** A scan built on
`archive.markdown` would agree with the parser by construction and could never
report an example the parser dropped — ⛔ which is precisely the failure
*nothing is lost* is written to catch.

## ⚠️ IT REPORTS AN UNCLOSED FENCE; IT DOES NOT REFUSE ONE

⭐ **`Region.occurrences` is the precedent, character for character**: that
module returns zero and two and refuses to pick, and its caller refuses. ⛔ A
file ending inside a fence is a real fault, and the sentence that names it
belongs to the module that knows what the file was being read *for* — so
`unclosed` travels, and `ledger.take` is what raises.

## ⚠️ A CLOSING FENCE IS THE SAME CHARACTER, WHICH IS WHAT `validate.headings` SAYS

⭐ **Followed deliberately rather than corrected to CommonMark's length rule.**
Two modules walking one file with two ideas of where a fence ends is the drift
this whole arrangement exists to avoid; ⛔ a marker of the *other* character
inside an open fence is body text here, because it is body text to a reader.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.validate.headings import FENCE, HEADING_LINE


@dataclass(frozen=True, slots=True)
class Fence:
    """One fenced block as the raw source carries it, before it is an entry.

    ⛔ `sections` is the chain of headings that encloses it, **outermost
    first**, so an origin naming any ancestor section can be resolved against
    it. `language` is the fence's info word, or `None` where it opens with none.
    """

    ordinal: int
    sections: tuple[str, ...]
    language: str | None
    body: str


@dataclass(frozen=True, slots=True)
class Scan:
    """One pass over a material file, and everything that pass saw.

    ⛔ **All three come out of ONE walk**, and that is not a saving of time: a
    second pass would be a second answer to *what is a heading outside a
    fence*, and two answers to that question is the drift `validate.headings`
    was extracted to prevent. ⭐ `headings` keeps its repeats, because a name
    a file carries twice is what makes a region ambiguous.
    """

    fences: tuple[Fence, ...]
    headings: tuple[str, ...]
    unclosed: bool


def scan(text: str) -> Scan:
    """Every fenced block in `text`, with the heading chain that encloses it."""
    found: list[Fence] = []
    seen: list[str] = []
    stack: list[tuple[int, str]] = []
    marker_char: str | None = None
    opened: tuple[tuple[str, ...], str | None] = ((), None)
    body: list[str] = []
    for line in text.splitlines():
        marker = FENCE.match(line)
        run = marker.group(1) if marker is not None else ""
        if marker_char is None:
            if marker is not None:
                marker_char = run[0]
                opened = (tuple(name for _, name in stack), _language(line, run))
                body = []
            else:
                _push(stack, seen, line)
            continue
        if run[:1] == marker_char:
            marker_char = None
            found.append(_fence(len(found) + 1, opened, body))
            continue
        body.append(line)
    return Scan(tuple(found), tuple(seen), marker_char is not None)


def _language(line: str, run: str) -> str | None:
    """Return the fence's info word, or `None` where it opens with none."""
    info = line.lstrip()[len(run) :].strip().split()
    return info[0] if info else None


def _fence(ordinal: int, opened: tuple[tuple[str, ...], str | None], body: list[str]) -> Fence:
    """One closed fence, with the chain and the language recorded when it opened."""
    sections, language = opened
    return Fence(ordinal, sections, language, "".join(f"{line}\n" for line in body))


def _push(stack: list[tuple[int, str]], seen: list[str], line: str) -> None:
    """Fold one line into the heading chain, popping every heading it closes.

    ⛔ **A heading closes every heading of its own depth or deeper**, which is
    a heading-bounded region's boundary read from the other end: what remains on the
    stack is exactly the set of regions the next fence sits inside.
    """
    heading = HEADING_LINE.match(line)
    if heading is None:
        return
    depth = len(heading.group(1))
    while stack and stack[-1][0] >= depth:
        stack.pop()
    text = (heading.group(2) or "").strip()
    stack.append((depth, text))
    seen.append(text)
