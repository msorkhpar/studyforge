r"""What a raw material file carries: its fenced blocks, and the headings over each.

**What it does.** Walks Markdown **as bytes on disk** and answers one question
the framework had no answer to — *which headings enclose this fenced block?*
It reports; it decides nothing and refuses nothing.

**How you use it.** `scan(text)` returns a `Scan`: every `Fence` in the order
the file carries them, every heading it carries outside a fence, and whether
the file ended inside a fence.

**Depends on.** `dataclasses`, `studyforge.validate.headings` for
`HEADING_LINE`, and `studyforge.archive.markdown.fences` and `.patterns` for
what a fence is and where a list item runs. ⛔ **Never the archive reader's
parser** — see below. Standard library only.

## ⛔ IT BORROWS THE GRAMMAR AND NOT THE WALK

⭐ **`archive.markdown.fences` owns where a fence opens and where it closes**,
and the archive reader reads its fences by the same module, so the ledger reads
every fence the archive reader reads — ⚠️ measured: a pattern of the ledger's
own (three spaces at most) missed five examples indented under list items in
one course and refused a page whose fence the archive reader accepted.
⭐ **`validate.headings` owns what a heading is.** What neither can lend is the
WALK: which headings enclose a fence. So the shared thing is the grammar and the
new thing is the traversal, which leaves one definition of each in the tree.

⚠️ **A list item is followed the way the archive reader follows one**: it opens
at a list marker, runs through lines indented under it, lazy continuation and
blank lines, and ends at a heading, or at an unindented line after a blank one
that is not another item. Inside it a fence may be indented any distance.

## ⛔ THE MARKDOWN PARSER IS NOT USED, AND THAT IS THE REGION RULE'S REASON

⚠️ **The ledger exists to say what the SOURCE carries.** A scan built on
the archive's parser would agree with it by construction and could never
report an example the parser dropped — ⛔ which is precisely the failure
*nothing is lost* is written to catch.

## ⚠️ IT REPORTS AN UNCLOSED FENCE; IT DOES NOT REFUSE ONE

⭐ **`Region.occurrences` is the precedent, character for character**: that
module returns zero and two and refuses to pick, and its caller refuses. ⛔ A
file ending inside a fence is a real fault, and the sentence that names it
belongs to the module that knows what the file was being read *for* — so
`unclosed` travels, and `ledger.take` is what raises.

## ⚠️ A FENCE IS BACKTICKS, BECAUSE THAT IS THE ONLY FENCE THE ARCHIVE KEEPS

⛔ A `~~~` run is not a fence to the archive reader, so it is not one here:
counting it would ask an exercise of an example no page renders as code.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.archive.markdown import fences, patterns
from studyforge.validate.headings import HEADING_LINE


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
    opened: fences.Opened | None = None
    context: tuple[tuple[str, ...], str | None] = ((), None)
    body: list[str] = []
    listing = _Listing()
    for line in text.splitlines():
        if opened is None:
            opened = fences.opening(line, in_list=listing.inside)
            if opened is not None:
                context = (tuple(name for _, name in stack), _language(opened.info))
                body = []
            else:
                listing.step(line)
                _push(stack, seen, line)
            continue
        if fences.closes(line, opened):
            opened = None
            found.append(_fence(len(found) + 1, context, body))
            listing.fenced()
            continue
        body.append(line)
    return Scan(tuple(found), tuple(seen), opened is not None)


class _Listing:
    """Whether the line being read continues a list item, as the archive reader follows one."""

    def __init__(self) -> None:
        self.inside = False
        self.blank = False

    def step(self, line: str) -> None:
        """Fold one line read outside a fence into the list state."""
        if not line.strip():
            self.blank = True
            return
        if patterns.THEMATIC.match(line) or HEADING_LINE.match(line):
            self.inside = False
        elif patterns.UNORDERED.match(line) or patterns.ORDERED.match(line):
            self.inside = True
        elif self.inside and self.blank and not line[:1].isspace():
            self.inside = False
        self.blank = False

    def fenced(self) -> None:
        """Record that a fence just closed, so the item it sat in goes on."""
        self.blank = False


def _language(info: str) -> str | None:
    """Return the fence's info word, or `None` where it opens with none."""
    words = info.strip().split()
    return words[0] if words else None


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
