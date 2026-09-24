r"""Counting headings in raw source, and bounding the region one unit is.

**What it does.** Reads ATX heading lines out of Markdown **without a Markdown
reader**: how many a file carries, and — where a unit is a region of a shared
file — how many its region carries.

**How you use it.** `count_headings(text)` for a whole file, `region(text,
section)` for one unit's slice of it. `headings(text)` is the scan both are
built on, for a caller that wants the depths.

**Depends on.** `re` and `dataclasses`. ⛔ **Nothing else, and never
`archive.markdown`** — this module exists to produce a number the parser did
not, and a scan that borrowed the parser's would agree with it by
construction. `tests/studyforge/validate/test_headings.py` asserts the import
is absent rather than trusting this sentence.

## ⛔ Why the region is bounded by a heading

⭐ **`check_completeness` exists to disagree with the parser**, so the bound
may not come from it. An *anchor* — `TestCases.md#card-issuance` — would: a
slug is a renderer's rule about how it names a heading, and reading one back
means agreeing with a renderer about the answer. ⚠️ A **line range** is
parser-independent too and was refused for a different reason: it is brittle
against an upstream file that grows a paragraph, and these corpora are living
repositories.

⭐ **A heading needs neither.** The regex below already knows a heading's depth,
so the region is "this heading, and every heading after it that is deeper,
stopping at the first that is not" — computed from the same scan that produces
the count, with no second reading of anything.

## ⚠️ The section is matched as written, and that is a refusal, not a guess

The text compared against `section` is the heading line with its hashes and
its **surrounding** whitespace removed, and nothing else: a closing-hash
heading (`## Card issuance ##`) carries the trailing hashes in its text.
⛔ A corpus that writes the section a different way from the file gets
`occurrences == 0` — a named finding pointing at the unit — rather than a
region that quietly starts somewhere else. ⭐ **Zero and two are both loud**;
that is the whole reason uniqueness is a rule.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: An ATX heading, with its depth and its text. ⛔ Deliberately not the Markdown
#: reader's: this number exists to disagree with the parser, so it may not come
#: from it. ⚠️ Seven hashes is not a heading and `#no-space` is not one either,
#: which is what the trailing group is for.
HEADING_LINE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")

#: A fence opening or closing. ⚠️ Fence awareness is the whole difficulty: a
#: `#` inside a code block is a comment in half the languages this framework
#: will meet, and counting it would make the check cry wolf on correct output.
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


@dataclass(frozen=True, slots=True)
class Heading:
    """One ATX heading line, as the raw source carries it."""

    depth: int
    text: str


@dataclass(frozen=True, slots=True)
class Region:
    """What a `section` names in one file: whether it is unique, and how big.

    ⛔ **`occurrences` is reported rather than resolved.** A section occurring
    twice is sixteen silent short reads if the reader picks one, so the count
    travels to the caller and the caller refuses. `headings` is meaningful
    only when `occurrences` is 1, and is 0 otherwise.
    """

    section: str
    occurrences: int
    headings: int


def headings(text: str) -> list[Heading]:
    """Every ATX heading outside fenced code, in the order the file carries them.

    ⚠️ **Fence-aware, and that is not decoration.** A `#` at the start of a
    line inside a fence is a comment in Python, Ruby, shell and YAML; counting
    those would make this check fire on correct output, and a check that fires
    on correct output is a check somebody turns off.
    """
    found: list[Heading] = []
    fence: str | None = None
    for line in text.splitlines():
        marker = FENCE.match(line)
        if marker is not None:
            if fence is None:
                fence = marker.group(1)[0]
            elif marker.group(1)[0] == fence:
                fence = None
            continue
        if fence is not None:
            continue
        match = HEADING_LINE.match(line)
        if match is not None:
            found.append(Heading(len(match.group(1)), (match.group(2) or "").strip()))
    return found


def count_headings(text: str) -> int:
    """Count ATX heading lines outside fenced code."""
    return len(headings(text))


def region(text: str, section: str) -> Region:
    """Find the region `section` opens, and count the headings inside it.

    ⛔ **The bound is the next heading of the same or shallower depth**, never
    the next heading of any depth: a unit's own subsections belong to it, and
    stopping at the first of them would report a short read on every unit that
    has one. ⭐ The opening heading counts — the region *is* that heading and
    what it introduces, which is what the parser sees for the unit too.
    """
    found = headings(text)
    matched = [index for index, heading in enumerate(found) if heading.text == section]
    if len(matched) != 1:
        return Region(section, len(matched), 0)
    opening = matched[0]
    depth = found[opening].depth
    inside = 1
    for heading in found[opening + 1 :]:
        if heading.depth <= depth:
            break
        inside += 1
    return Region(section, 1, inside)
