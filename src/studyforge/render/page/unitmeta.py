"""The unit page's quieter second line: where it sits, and what it will ask of the reader.

**What it does.** Says, under a unit's title, which container it is in, its
place there ("Unit 3 of 20"), about how long it takes to read, and how many
practices and check-yourself questions it holds — the line the 2026-11 redesign
added (`Track 01 · Unit 01 of 20 · 9 min read · 4 quiz Qs` in the designer's
sample).

**How you use it.** `line(body, trail, rail)` after the body is rendered;
`''` when there is nothing to say.

**Depends on.** `studyforge.render.templates` and the trail's and rail's own
records; it reads counts off the rendered body rather than a second walk of the
document, so it can never disagree with what the page shows.

## ⭐ Every part is optional

A part with nothing true to say is left out: no container on a one-container
corpus, no "of N" without a rail, no practices line on a page without one.

## ⛔ No middle dot

The parts are list items; `chrome.css` draws the separator as a small circle,
because a typed `·` is the identity test's tell.

## ⚠️ The reading time is an estimate, and says "min read"

Prose at `WORDS_PER_MINUTE`, plus `SECONDS_PER_CODE_LINE` for every line of a
listing, rounded up, at least one minute.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from html import unescape

from studyforge.render import templates
from studyforge.render.markup import escape
from studyforge.render.page.navigation import Crumb
from studyforge.render.page.rail import RailContainer

#: How fast running prose is read, in words a minute.
WORDS_PER_MINUTE = 220

#: How long one line of a code listing takes to read, in seconds.
SECONDS_PER_CODE_LINE = 1

LINE_TEMPLATE = "unit-meta.html"
PART_TEMPLATE = "unit-meta-part.html"

#: A practice card and a quiz question, as the rendered body marks them.
PRACTICE_CARD = re.compile(r"<li\b[^>]*\bdata-practice-card=")
QUESTION = re.compile(r"<li\b[^>]*\bdata-practice-question=")

#: Markup to ignore when counting prose: a listing (counted by lines), a quiz,
#: a practice's statement and its cards (doing, not reading), and every tag.
LISTING = re.compile(r"<pre\b.*?</pre>", re.DOTALL)
NOT_READING = re.compile(
    r"<section\b[^>]*\b(?:data-(?:practice-quiz|practices)\b|data-kind=\"practice\")"
    r".*?</section>",
    re.DOTALL,
)
TAG = re.compile(r"<[^>]+>")
WORD = re.compile(r"\w+")


def line(
    body: str,
    trail: Sequence[Crumb] | None = None,
    rail: Sequence[RailContainer] | None = None,
) -> str:
    """Return the second line, or `''` when no part of it has anything to say."""
    parts = [
        part
        for part in (
            container_of(trail),
            position(rail),
            f"{minutes(body)} min read",
            _count(len(PRACTICE_CARD.findall(body)), "practice", "practices"),
            _count(len(QUESTION.findall(body)), "question", "questions"),
        )
        if part
    ]
    items = "".join(templates.fill(PART_TEMPLATE, text=escape(part)) for part in parts)
    return templates.fill(LINE_TEMPLATE, parts=items)


def container_of(trail: Sequence[Crumb] | None) -> str:
    """The title of the container the unit sits in: the trail's last step above the unit."""
    if not trail or len(trail) < 3:
        return ""
    return trail[-2].title


def position(rail: Sequence[RailContainer] | None) -> str:
    """"Unit n of m" inside the current container, or `''` without a rail that knows."""
    for container in rail or ():
        for index, unit in enumerate(container.units, start=1):
            if unit.current:
                return f"Unit {index} of {len(container.units)}"
    return ""


def minutes(body: str) -> int:
    """About how many minutes the page takes to read, at least one."""
    reading = NOT_READING.sub(" ", body)
    code_lines = sum(block.count("\n") + 1 for block in LISTING.findall(reading))
    prose = unescape(TAG.sub(" ", LISTING.sub(" ", reading)))
    seconds = len(WORD.findall(prose)) * 60 / WORDS_PER_MINUTE
    seconds += code_lines * SECONDS_PER_CODE_LINE
    return max(1, math.ceil(seconds / 60))


def _count(count: int, one: str, many: str) -> str:
    """`'1 practice'`, `'3 practices'`, or `''` for none."""
    if count <= 0:
        return ""
    return f"{count} {one if count == 1 else many}"
