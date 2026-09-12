"""WHERE a document's Findings section is — gate three's predicate (`W172`).

**What it does.** Returns the line ranges a document's *Findings* section
occupies. ⛔ **This is a different question from `contract.check_sections`,
which asks whether a section EXISTS**; this module asks where it *reaches*, and
nothing here is a rule or returns a finding.

**How you use it.** `findings_region(text)` returns `(first, last)` line numbers,
inclusive and 1-based, for every Findings section in the document.
`in_findings(text)` is the same answer as a predicate over a line number.

**Depends on.** `re`. ⛔ Nothing in its own package and nothing in `tools`: it is
a reader over text, so the rules can depend on it and it can depend on none of
them.

## ⛔ Why a REGION and not a heading test (Ruling 218's gate three)

⚠️ **`check_markers` is Ruling 65's *name the marker, do not spell it*, and a
`ruling record`'s prose names markers constantly and legitimately** — a
disposition argues about whether a finding was `[local]` or `[structural]`, and
every one of those sentences would be read as a finding that does not exist.
⭐ **Measured at `bec9d5c`, over the 110 records in `docs/tasks/handoffs`: the
fully widened marker rule fires 181 times in 53 documents; restricted to these
regions it fires 27 times in 7.** ⛔ The remaining 27 are the reason gate three
is more than this module, and `records.py` carries that argument.

## ⛔ The three properties that make the region readable rather than guessed

1. ⭐ **A fenced block is quoted material and holds no heading**, exactly as
   `contract.marker_lines` already treats it. ⚠️ A record that transcribes
   another document's `## Findings` would otherwise open a region on it.
2. ⭐ **The region ends at the next heading of the same depth or shallower**,
   never at the next heading of any depth — a record's findings are written as
   `###` subsections underneath a `##` heading, so ending at *any* heading would
   admit the first finding and drop the rest.
3. ⭐ **A section that is never closed runs to the end of the document.** ⚠️ That
   is the ordinary shape: *Findings* is the fifth of `agent-protocol.md`'s six,
   but a record owes none of them and usually ends there.

⛔ **The heading text is matched loosely on purpose** — `## Findings`,
`### The findings`, `## ⛔ Findings, by id` — ⚠️ because the alternative is a
closed list of spellings, and Ruling 29 records four attempts at one of those,
each of which worked on the documents its author had seen. ⭐ The emphasis and
attention markup an office puts in a heading is stripped before the match, for
the same reason `contract.LEAD_TOKENS` exists.
"""

from __future__ import annotations

import re

#: A markdown ATX heading, with its depth and its text. ⛔ Setext headings
#: (`Findings` underlined with `---`) are NOT read: no document in this tree
#: writes one, and admitting them would make a horizontal rule after a
#: one-word paragraph open a region.
_HEADING = re.compile(r"^(?P<depth>#{1,6})[ \t]+(?P<title>.*?)[ \t]*$")

#: The markup an office puts before a heading's first word. ⭐ Stripped rather
#: than enumerated into the title pattern, so the two concerns stay apart.
_HEADING_LEAD = re.compile(r"^[*_ \t⛔⭐⚠✅️]+")

#: The heading text that opens the region. ⚠️ A prefix match, not an equality:
#: `Findings, by id` and `Findings — mine` are the same section.
_FINDINGS_TITLE = re.compile(r"^(?:the[ \t]+)?findings\b", re.IGNORECASE)


def findings_region(text: str) -> tuple[tuple[int, int], ...]:
    """Inclusive 1-based `(first, last)` line numbers of every Findings section.

    The heading line itself is `first`, so a marker written on the heading is
    inside the region it opens.
    """
    lines = text.splitlines()
    regions: list[tuple[int, int]] = []
    opened_at: int | None = None
    opened_depth = 0
    fenced = False
    for number, line in enumerate(lines, start=1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        heading = _HEADING.match(line)
        if heading is None:
            continue
        depth = len(heading.group("depth"))
        if opened_at is not None and depth <= opened_depth:
            regions.append((opened_at, number - 1))
            opened_at = None
        if opened_at is None and _FINDINGS_TITLE.match(
            _HEADING_LEAD.sub("", heading.group("title"))
        ):
            opened_at, opened_depth = number, depth
    if opened_at is not None:
        regions.append((opened_at, len(lines)))
    return tuple(regions)


def in_findings(text: str) -> frozenset[int]:
    """Every line number inside a Findings section.

    ⭐ A set rather than a range test at each call site, because a caller that
    walks the document once should not walk the regions once per line.
    """
    return frozenset(
        number for first, last in findings_region(text) for number in range(first, last + 1)
    )
