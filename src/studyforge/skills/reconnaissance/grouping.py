r"""Which lines in a curriculum record are group labels, and which are units.

**What it does.** Decides the grouping a curriculum document expresses, from
where its lines sit rather than from how they are marked up.

**How you use it.** `grouping(lines, entries)` returns
`(group labels, entries each carrying its group)`. `choose(lines, entries,
holds)` returns the labels with their lines, for a caller that needs positions.

**Depends on.** `record`'s `Entry` and its line patterns. ⛔ Split out of
`record` because they answer different questions and the module was
over R11's ceiling: *which document records the curriculum* is one question,
*what grouping does it express* is another, and a failing check should name
the concern rather than the file.

## ⛔ Role is positional, not syntactic

⚠️ **Two measured corpora set this trap in opposite directions:** one writes
its containers as headings in a document full of headings that are not
containers, and a heading-keyed parser emits far too many; the other writes its
sections as bare numbered lines with no heading anywhere in the region, and the
same parser emits none. ⛔ **Both raise nothing.** `SKILL.md` step 3 holds the
corpora and the counts.

⭐ So a group label is *"a line that introduces a run of entries and is not
itself an entry"*, and the labels of one grouping all share one **shape**. Both
corpora fall out of that rule; neither falls out of a syntax rule.

## ⛔ A heading that links a file is not a unit by the link alone

⭐ **It is read as a group label that names where its units are**, when it
stands where the grouping's labels stand, opens no entry of the record, and the
file it links is cut into regions (`regions`). Its units are those regions.

- **§6 reads a record by position, not by mark.** A link records an `origin`,
  and a container carries an `origin` exactly as a unit does, so a link says
  *where something is* and never *what role it has*. Role stays positional.
- **A unit may be a region of one file** (`origin: {path, section}`). A
  label whose file is cut into regions heads a container of sub-file units, and
  reading that label as one whole-file unit erases every unit inside it.

⚠️ **Anywhere else a linked heading is still an entry:** inside a run of
entries, at a shape that is not the labels', above entries it opens, or linking
a file that is one unit. `record.observe` asks about the last by name.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import replace

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
#: "densest run of entries" rule **cannot be tuned to work on both measured
#: corpora at once** — one's largest gap *inside* its curriculum is wider than
#: the other's distance to a stray entry *outside* it, so every threshold gets
#: one of them wrong. ⭐ So the region is the whole span, and the leftovers are
#: named rather than cut off by a constant nobody can justify. `SKILL.md`,
#: appendix **A3**, holds the two gaps that rule it out.
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


def grouping(lines, entries: list[Entry], holds=frozenset()) -> tuple[list[str], list[Entry]]:
    """Return `(group labels, entries with a group each)`; `choose` decides them."""
    found, kept = choose(lines, entries, holds)
    return [text for _, text in found], assign(kept, found)


def choose(
    lines, entries: list[Entry], holds=frozenset()
) -> tuple[list[tuple[int, str]], list[Entry]]:
    """Return `(labels as (line, text), the entries that are still entries)`.

    ⛔ **One shape wins or none does.** Candidate labels are gathered by shape —
    `h1`, `h2`, a bare line, a list item at some indent — and a shape qualifies
    only if its labels **partition every entry**: each label is followed by at
    least one entry, and no entry sits above the first label. ⚠️ If two shapes
    qualify, or none does, this returns **nothing** and `observe` raises a
    question, because a grouping guessed here is a container tree in the built
    site and the reader would never know.

    ⭐ Both measured corpora fall out of this one rule and neither falls out
    of a syntax rule — one labels with headings, the other with bare numbered
    lines and no heading anywhere in the region (`SKILL.md` step 3).

    ⭐ `holds` names the linked files cut into regions. A heading linking one
    is a candidate label of its own shape (module docstring); it is settled a
    label only if it opens no entry, and otherwise stays the entry it was.
    """
    carrying = Counter(entry.line for entry in entries)
    candidates: dict[str, list[tuple[int, str]]] = {}
    for number in range(1, entries[-1].line + 1):
        if number in carrying:
            continue
        text = label(lines[number - 1])
        if text:
            candidates.setdefault(shape(lines[number - 1]), []).append((number, text))
    linked: dict[str, list[tuple[int, str]]] = {}
    for entry in entries:
        line = lines[entry.line - 1]
        if carrying[entry.line] == 1 and entry.target in holds and HEADING.match(line):
            linked.setdefault(shape(line), []).append((entry.line, entry.title))
    qualified = {}
    for kind in sorted(set(candidates) | set(linked)):
        settled = _settle(candidates.get(kind, []), linked.get(kind, []), entries)
        if settled is not None:
            qualified[kind] = settled
    if len(qualified) != 1:
        return [], entries
    found, kept, labels = next(iter(qualified.values()))
    return _drop_stray_opening(found, kept, labels), kept


def _settle(plain, linked, entries: list[Entry]):
    """Return `(labels, entries left, linked label lines)` if this shape groups, else `None`.

    ⚠️ A linked candidate that opens an entry is put back as that entry, and the
    rest are judged again, because putting one back widens the label above it.
    """
    while True:
        lines = {number for number, _ in linked}
        kept = [entry for entry in entries if entry.line not in lines]
        if not kept:
            return None
        # ⚠️ Labels above the first entry are kept only as far back as the one
        # that opens it: a document's own title is a label for everything below
        # it, and a measured corpus records its first container exactly there —
        # see `SKILL.md`, appendix **A3**.
        found = sorted(_from_opening(plain, kept) + linked)
        opening = {number for number, _ in linked if _opens(number, found, kept)}
        if not opening:
            break
        linked = [candidate for candidate in linked if candidate[0] not in opening]
    return (found, kept, lines) if _partitions(found, kept, lines) else None


def _opens(number: int, found: list[tuple[int, str]], entries: list[Entry]) -> bool:
    """Say whether the label on line `number` has an entry before the next label."""
    after = [line for line, _ in found if line > number]
    end = after[0] if after else float("inf")
    return any(number < entry.line < end for entry in entries)


def _drop_stray_opening(
    found: list[tuple[int, str]], entries: list[Entry], linked=frozenset()
) -> list[tuple[int, str]]:
    """Drop a leading label that opens too few entries to be a group.

    ⚠️ **Measured, and it is the difference between the right number of groups
    and one too many.** A corpus links to its contributor guide from a
    blockquote above the curriculum, and the nearest line of the winning shape
    above that link is a bullet in the overview prose. Kept, it becomes an
    extra "section" holding one entry that is not a unit (`SKILL.md`, appendix
    **A3**).

    ⭐ A run smaller than the allowance is not a group; it is the stray the
    allowance exists for, and `observe` names it. ⛔ Applied only at the front:
    a genuinely small *last* container is a real thing and this must not eat it.
    ⛔ Nor a linked label: it opens no entry by construction, and its units are
    the regions of its file.
    """
    while len(found) > 2 and found[0][0] not in linked:
        opened = sum(1 for entry in entries if found[0][0] < entry.line < found[1][0])
        if opened > UNLABELLED_ALLOWANCE * len(entries):
            break
        found = found[1:]
    return found


def _from_opening(found: list[tuple[int, str]], entries: list[Entry]) -> list[tuple[int, str]]:
    """Drop labels of this shape that sit above the one opening the first entry."""
    above = [index for index, (number, _) in enumerate(found) if number <= entries[0].line]
    return found[above[-1] :] if above else found


def _partitions(found: list[tuple[int, str]], entries: list[Entry], linked=frozenset()) -> bool:
    """Judge whether these labels cut the entries into runs, leaving few above the first.

    ⛔ Every label must open at least one entry. That is the test that refuses
    a document's many top-level headings when only a few of them are
    containers: the rest head a chapter of an entirely different document, and
    no unit sits beneath any of them (`SKILL.md` step 3). ⭐ A linked label is
    the one exception, and `_settle` has already required it to open none.

    ⚠️ And almost every entry must be under a label. `UNLABELLED_ALLOWANCE`
    says how much slack that "almost" is worth, and `observe` reports whatever
    it covers — a corpus does not lose its hierarchy over one link in a
    blockquote, and nobody is left unaware that the link was there.
    """
    if len(found) < 2:
        return False
    plain = [number for number, _ in found if number not in linked]
    if not all(_opens(number, found, entries) for number in plain):
        return False
    stray = sum(1 for entry in entries if entry.line < found[0][0])
    return stray <= UNLABELLED_ALLOWANCE * len(entries)


def label(line: str) -> str | None:
    """Return the text of a line that could introduce a group, or `None`.

    ⛔ A line carrying a link is never read as a label **here**: whether a
    linked heading is one is decided by its position, in `choose`.
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


def assign(entries: list[Entry], found: list[tuple[int, str]]) -> list[Entry]:
    """Attach each entry to the label most recently opened above it."""
    out: list[Entry] = []
    for entry in entries:
        current = None
        for number, text in found:
            if number < entry.line:
                current = text
        out.append(replace(entry, group=current))
    return out
