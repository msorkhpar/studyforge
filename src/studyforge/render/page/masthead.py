"""The top bar's brand and section links: where a reader is, said once, on every page.

**What it does.** Turns a `Masthead` — the corpus's title, how this page
addresses the root index, and the rail it already has — into the two pieces of
the top bar the 2026-11 redesign added: the brand (the course's name, a link
home) and the course's top-level sections as links.

**How you use it.** Every page writer builds one `Masthead` per page and the
three `compose` functions pass it to `brand()` and `sections()`; `None` keeps
the old top bar (search and theme only), which is what a caller that has not
been told about the masthead gets.

**Depends on.** `studyforge.render.templates` and the rail's own records.

## ⭐ The section links come from the rail, not from a second walk

The rail already holds every container this page can reach, with hrefs relative
to this page and the groups each sits in. A top-level entry is a container's
outermost group, or the container itself at depth 1; it links to its first
readable container, because no page is written above a container.

## ⛔ At most `SECTION_LIMIT` links, or none

A course with three tracks reads them at a glance in the bar; a course with
fifteen parts does not, and a bar that wraps or scrolls is worse than no links —
the rail and the index already list them. Over the limit the bar keeps the brand
and search only.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from studyforge.render import templates
from studyforge.render.markup import anchor, escape, escape_attribute, safe_href
from studyforge.render.page.rail import RailContainer

#: The most top-level sections the bar names before it names none.
SECTION_LIMIT = 5

BRAND_TEMPLATE = "masthead-brand.html"
SECTIONS_TEMPLATE = "masthead-sections.html"
SECTION_TEMPLATE = "masthead-section.html"

#: How the section holding the page links when that page IS the section's page.
SELF = anchor("content")

#: What the link of the section holding this page carries.
CURRENT = ' aria-current="true"'


@dataclass(frozen=True, slots=True)
class Masthead:
    """What the top bar needs to know about one page's place in the course.

    ⚠️ `home` is how THIS page addresses the root index; `rail` is the same
    rail the page draws, so its hrefs are already relative to this page.
    """

    title: str
    home: str
    rail: Sequence[RailContainer] = field(default_factory=tuple)


def brand(masthead: Masthead | None) -> str:
    """Return the brand link, or `''` when the page was given no masthead."""
    if masthead is None or not masthead.title:
        return ""
    return templates.fill(
        BRAND_TEMPLATE,
        home=escape_attribute(safe_href(masthead.home) or SELF),
        title=escape(masthead.title),
    )


def sections(masthead: Masthead | None) -> str:
    """Return the section links, or `''` with none to name or more than the bar holds."""
    if masthead is None:
        return ""
    entries = top_level(masthead.rail)
    if len(entries) < 2 or len(entries) > SECTION_LIMIT:
        return ""
    links = "".join(
        templates.fill(
            SECTION_TEMPLATE,
            href=escape_attribute(safe_href(href) or SELF),
            current=CURRENT if current else "",
            title=escape(title),
        )
        for title, href, current in entries
    )
    return templates.fill(SECTIONS_TEMPLATE, links=links)


def top_level(rail: Sequence[RailContainer]) -> tuple[tuple[str, str, bool], ...]:
    """Return `(title, href, holds this page)` for each top-level entry, in rail order.

    ⭐ A group's href is its first container that has a page; a top-level entry
    with no readable container is left out, since a link to nothing is not one.
    """
    found: dict[str, list] = {}
    for container in rail:
        if container.within:
            group = container.within[0]
            key, title = f"group:{group.key or group.title}", group.title
        else:
            key, title = f"container:{container.title}:{container.href}", container.title
        entry = found.setdefault(key, [title, None, False])
        if entry[1] is None and container.href is not None:
            entry[1] = container.href
        elif entry[1] is None and container.current:
            # ⭐ The container page itself draws its own row without an href.
            entry[1] = SELF
        if container.current or any(unit.current for unit in container.units):
            entry[2] = True
    return tuple(
        (title, href, current) for title, href, current in found.values() if href is not None
    )
