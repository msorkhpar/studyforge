r"""Which lines in a curriculum record are group labels, and which are units.

**What it does.** Decides the grouping a curriculum document expresses, from
where its lines sit rather than from how they are marked up.

**How you use it.** `grouping(lines, entries)` returns
`(group labels, entries each carrying its group)`.

**Depends on.** `record`'s `Entry` and its line patterns. ⛔ Split out of
`record` at SK-01 because they answer different questions and the module was
over R11's ceiling: *which document records the curriculum* is one question,
*what grouping does it express* is another, and a failing check should name
the concern rather than the file.

## ⛔ Role is positional, not syntactic

⚠️ **Both measured corpora set this trap, in opposite directions:**

- **ISO-8583** records its 3 containers as `#` headings — in a file carrying
  **21** top-level headings, because `#` also means *a link to other material*
  once and *a chapter of a different document* seventeen times. A parser keyed
  on `#` emits **21 containers for a 3-container corpus and raises nothing.**
- **Java-senior** records its 10 sections as **bare numbered paragraph lines**
  with **zero headings anywhere in the curriculum region**. A parser keyed on
  headings emits **0 sections for a 10-section corpus** — the same failure from
  the other side.

⭐ So a group label is *"a line that introduces a run of entries and is not
itself an entry"*, and the labels of one grouping all share one **shape**. Both
corpora fall out of that rule; neither falls out of a syntax rule.
"""

from __future__ import annotations

from studyforge.skills.reconnaissance.record import (
    HEADING,
    LINK,
    LIST_MARKER,
    ORDINAL,
    Entry,
)

#: How much of the curriculum a grouping may leave unlabelled and still be
#: believed. ⚠️ **Not a tolerance for being wrong** — the entries above the
#: first label are *reported*, every time. It exists because a README says a
#: sentence about itself before it starts listing, and one stray link must not
#: cost a corpus its hierarchy.
#:
#: ⛔ Measured, and this is why the obvious heuristic was abandoned: the
#: "densest run of entries" rule **cannot be tuned to work on both corpora.**
#: Java-senior's largest gap *inside* its curriculum is 8 lines and its one
#: stray link sits 22 lines away — so a threshold of 12 separates them. ISO's
#: largest gap inside its curriculum is **34**, because its outline runs to
#: three levels of unlinked text. Any threshold that keeps ISO whole swallows
#: Java's stray. ⭐ So the region is the whole span, and the leftovers are named
#: rather than cut off by a constant nobody can justify.
UNLABELLED_ALLOWANCE = 0.1


def forms(lines, entries) -> dict[str, int]:
    """How many entries are written in each shape — the drift tell."""
    forms: dict[str, int] = {}
    for entry in entries:
        forms[shape(lines[entry.line - 1])] = forms.get(shape(lines[entry.line - 1]), 0) + 1
    return forms


def shape(line: str) -> str:
    """Name the shape of one line, so two lines can be compared for sameness."""
    heading = HEADING.match(line)
    if heading is not None:
        return f"h{len(heading.group('hashes'))}"
    marker = LIST_MARKER.match(line)
    if marker is not None:
        return f"list@{len(line) - len(line.lstrip())}"
    return "bare" if line.strip() else "blank"


def grouping(lines, entries: list[Entry]) -> tuple[list[str], list[Entry]]:
    """Return `(group labels, entries with a group each)`, or no grouping at all.

    ⛔ **One shape wins or none does.** Candidate labels are gathered by shape —
    `h1`, `h2`, a bare line, a list item at some indent — and a shape qualifies
    only if its labels **partition every entry**: each label is followed by at
    least one entry, and no entry sits above the first label. ⚠️ If two shapes
    qualify, or none does, this returns **nothing** and `observe` raises a
    question, because a grouping guessed here is a container tree in the built
    site and the reader would never know.

    ⭐ Both measured corpora fall out of this one rule and neither falls out of
    a syntax rule: ISO's labels are `h1`, Java's are bare numbered lines with
    **no heading anywhere in the region**.
    """
    carrying = {entry.line for entry in entries}
    candidates: dict[str, list[tuple[int, str]]] = {}
    for number in range(1, entries[-1].line + 1):
        if number in carrying:
            continue
        text = label(lines[number - 1])
        if text:
            candidates.setdefault(shape(lines[number - 1]), []).append((number, text))
    # ⚠️ Labels above the first entry are kept only as far back as the one that
    # opens it: a document's own title is a label for everything below it, and
    # ISO records its first container exactly there, two lines above its first
    # entry.
    candidates = {shape: _from_opening(found, entries) for shape, found in candidates.items()}
    qualified = {shape: found for shape, found in candidates.items() if _partitions(found, entries)}
    if len(qualified) != 1:
        return [], entries
    found = _drop_stray_opening(next(iter(qualified.values())), entries)
    return [text for _, text in found], _assign(entries, found)


def _drop_stray_opening(
    found: list[tuple[int, str]], entries: list[Entry]
) -> list[tuple[int, str]]:
    """Drop a leading label that opens too few entries to be a group.

    ⚠️ **Measured, and it is the difference between 10 groups and 11.** The
    Java corpus links to its contributor guide from a blockquote 22 lines above
    the curriculum, and the nearest line of the winning shape above that link
    is a bullet in the overview prose. Kept, it becomes an eleventh "section"
    holding one entry that is not a unit.

    ⭐ A run smaller than the allowance is not a group; it is the stray the
    allowance exists for, and `observe` names it. ⛔ Applied only at the front:
    a genuinely small *last* container is a real thing and this must not eat it.
    """
    while len(found) > 2:
        opened = sum(1 for entry in entries if found[0][0] < entry.line < found[1][0])
        if opened > UNLABELLED_ALLOWANCE * len(entries):
            break
        found = found[1:]
    return found


def _from_opening(found: list[tuple[int, str]], entries: list[Entry]) -> list[tuple[int, str]]:
    """Drop labels of this shape that sit above the one opening the first entry."""
    above = [index for index, (number, _) in enumerate(found) if number <= entries[0].line]
    return found[above[-1] :] if above else found


def _partitions(found: list[tuple[int, str]], entries: list[Entry]) -> bool:
    """Judge whether these labels cut the entries into runs, leaving few above the first.

    ⛔ Every label must open at least one entry. That is the test that refuses
    ISO's twenty-one `#` headings for a three-container corpus: seventeen of
    them head a chapter of an entirely different document and no unit sits
    beneath any of them.

    ⚠️ And almost every entry must be under a label. `UNLABELLED_ALLOWANCE`
    says how much slack that "almost" is worth, and `observe` reports whatever
    it covers — a corpus does not lose its hierarchy over one link in a
    blockquote, and nobody is left unaware that the link was there.
    """
    if len(found) < 2:
        return False
    lines_of = [entry.line for entry in entries]
    edges = [number for number, _ in found] + [entries[-1].line + 1]
    if not all(
        any(edges[index] < line < edges[index + 1] for line in lines_of)
        for index in range(len(found))
    ):
        return False
    stray = sum(1 for line in lines_of if line < found[0][0])
    return stray <= UNLABELLED_ALLOWANCE * len(entries)


def label(line: str) -> str | None:
    """Return the text of a line that could introduce a group, or `None`.

    ⛔ A line carrying a link is an entry, never a label — that is the one
    syntactic test here, and it is about the corpus rather than about Markdown.
    """
    if LINK.search(line):
        return None
    heading = HEADING.match(line)
    if heading is not None:
        return heading.group("text").strip()
    stripped = LIST_MARKER.sub("", line).strip()
    if not stripped:
        return None
    numbered = ORDINAL.match(stripped)
    return numbered.group("rest").strip() if numbered else stripped


def _assign(entries: list[Entry], found: list[tuple[int, str]]) -> list[Entry]:
    """Attach each entry to the label most recently opened above it."""
    out: list[Entry] = []
    for entry in entries:
        current = None
        for number, text in found:
            if number < entry.line:
                current = text
        out.append(Entry(entry.target, entry.title, entry.ordinal, entry.line, current))
    return out
