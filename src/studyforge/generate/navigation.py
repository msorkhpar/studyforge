r"""The contents document joined to a page's bar and its breadcrumb trail.

**What it does.** Turns the corpus's tree into the two chrome records
`render.page.render` takes — `Links` for the between-units bar and a tuple of
`Crumb` for the trail — for one unit at a time.

**How you use it.**

    bar(contents, key, absent=corpus.absent)
    trail(contents, key, index_href, above)

`above` maps a container's address key to how **this unit's page** addresses
that container's page, so a crumb links where a page exists and lists where one
does not.

**Depends on.** `contents` for the order and the labels, `render.page` for the
two records. ⛔ Nothing here touches a filesystem and nothing here composes a
path: what is passed in was answered by `corpus.placement`.

## ⛔ Why this join is a module rather than three lines in the writer

⚠️ **It did not exist in `src/` until this one.** `contents` computes a slot and
`render.page` renders one, and nothing joined them — `W57`'s lesson exactly: a
value computed on one side and dropped on the other satisfies both sides' tests.
⭐ The join lived in `tests/studyforge/render/page/sites.py`, whose own docstring
says it stands in for the caller `SF-28` would write.

## ⛔ A neighbour with no page is a DECLARED absence, never a guessed href

⚠️ The contents document computes an href for **every** declared unit, because
it is a function of the address and knows nothing about what this machine has.
⭐ Handing that href to the bar for a unit nobody generated is the one failure
neither of Ruling 164's two policies catches: the anchor is present, the shape
is legal, and the file is not there. ⛔ So an absent neighbour is
`Link(href=None, key=…)`, and the bar degrades to that unit's index row.

## ⚠️ A container crumb links only where a container page exists

⭐ Every label comes out of the contents document — `Contents.title`,
`Group.level` (the corpus's own word for the depth, R1) and `Group.title` — and
not one of them is spelled here. ⛔ **An intermediate level has no container
page**, because a container map is written at the address a corpus declares
units under and nowhere above it; that crumb is therefore listed rather than
linked, which is `SF-14/3` made visible on the page instead of invisible.
"""

from __future__ import annotations

from collections.abc import Mapping

from studyforge.contents import Contents, Entry, Group, links, order
from studyforge.describe import describe
from studyforge.generate.declarations import BuildError
from studyforge.render.page import Crumb, Link, Links

#: The two bar slots whose target is a neighbouring unit. ⛔ `index` is not one
#: of them: it addresses the root index, which every corpus has.
NEIGHBOUR_SLOTS = ("previous", "next")


def bar(contents: Contents, key: str, absent: frozenset[str] = frozenset()) -> Links:
    """Return the between-units bar for one unit, with declared absences declared."""
    computed = links(contents, key)
    walked = [entry.key for entry in order(contents)]
    if key not in walked:
        # ⛔ `walked.index(key)` would raise a ValueError carrying the value (R7).
        raise BuildError(f"no unit of this corpus is keyed {describe(key)}")
    at = walked.index(key)
    slots: dict[str, Link] = {}
    for field in NEIGHBOUR_SLOTS:
        if field not in computed:
            continue
        target = walked[at - 1] if field == "previous" else walked[at + 1]
        href = None if target in absent else computed[field]["href"]
        slots[field] = Link(href, computed[field]["label"], target)
    slots["index"] = Link(computed["index"]["href"], computed["index"]["label"])
    return Links(**slots)


def index_href(contents: Contents, key: str) -> str:
    """How the page for `key` addresses the root index."""
    return links(contents, key)["index"]["href"]


def trail(
    contents: Contents,
    key: str,
    to_index: str,
    above: Mapping[str, str] | None = None,
) -> tuple[Crumb, ...]:
    """Return the crumbs for one unit: the corpus, its containers, then itself."""
    linked = above or {}
    return (
        Crumb("", contents.title, to_index),
        *(
            Crumb(group.level, group.title, linked.get(group.key))
            for group in ancestors(contents, key)
        ),
        Crumb("", _entry(contents, key).title),
    )


def ancestors(contents: Contents, key: str) -> tuple[Group, ...]:
    """Return the groups enclosing the unit `key` names, outermost first."""
    for group in contents.groups:
        found = _descend(group, key)
        if found is not None:
            return found
    return ()


def _descend(group: Group, key: str) -> tuple[Group, ...] | None:
    """`group` and what is under it, when the unit is in there."""
    if any(entry.key == key for entry in group.entries):
        return (group,)
    for child in group.groups:
        deeper = _descend(child, key)
        if deeper is not None:
            return (group, *deeper)
    return None


def _entry(contents: Contents, key: str) -> Entry:
    """Return the declared unit `key` names. ⛔ Raises rather than inventing a title.

    ⛔ The value is **described, never echoed** (R7). The branch that fires is
    the one where the argument is not a unit key, which is exactly the branch an
    absolute path arrives at, and a crumb is rendered per unit of every corpus.
    """
    for entry in order(contents):
        if entry.key == key:
            return entry
    raise BuildError(f"no unit of this corpus is keyed {describe(key)}")
