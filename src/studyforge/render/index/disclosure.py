r"""The tree the root index exists to show, as real disclosure elements.

**What it does.** Renders a corpus's hierarchy to any depth as nested
`<details>`/`<summary>` elements with a row per unit, and mints the fragment
another page deep-links a row by.

**How you use it.** `disclosure.render(document)` returns the markup;
`index.document` puts it in the page's body. `anchor(key)` is the fragment for
a row — ⛔ **ask, never compose**.

**Depends on.** `entries`, `policy` for which levels start open, `render.markup`
for the escaping and the href gate, and `render.page` for `PageError`.
⛔ Nothing that knows where a file is: an `Item` arrives with its href already
answered.

## ⛔ Real disclosure elements, because the floor is a double-clicked file

⭐ **`<details>` opens, closes and takes keyboard focus with scripting off
entirely** (R8). ⚠️ A `div` with a click handler does none of those things
without a script, and a page that needs a script to reveal its own contents has
made the reading floor conditional on something the floor does not have.

⛔ **So this module emits no script, and the page it is part of carries none of
its own.** ⭐ That is subtask (d) discharged the strongest way available: an
enhancement gated on protocol is one that can be absent, and the one that is
absent here cannot be a dependency.

## ⛔ Ruling 164 — this list is CONTENT, so a refused href RAISES

⚠️ **`page.navigation._link` DROPS a slot whose scheme is refused**, on the
argument that chrome which cannot be followed is worse than chrome that is not
there. ⭐ **That argument is right for the between-pages bar and wrong here**,
and the two disagree on purpose:

> ⛔ *If this element vanishes, has the reader lost a WAY TO GET SOMEWHERE, or
> has the page lost THE THING IT EXISTS TO SHOW?*

⛔ **This page is nothing but this tree.** A silently dropped anchor here is
every title present, nothing logged, and not one unit openable — from the one
page a reader lands on first. ⭐ `render.container.listing` reaches the same
answer for the same reason one page along, and the two are consistent by
argument rather than by imitation.

⚠️ **And absence is a third state, not a quiet version of either** (§7).
`Item(href=None)` is a unit this machine has no page for: it is listed, marked
`data-readable="false"`, and it raises nothing — because a renderer that could
not tell *"no page yet"* from *"bad href"* would always pick the wrong one of
drop-or-raise.

## ⛔ A row's anchor IS its key, and that is why deep links land

⭐ **Every row and every section carries the key the rest of the framework joins
on**, so a link into this page needs no table to consult and nothing to mint.
⚠️ The target of a deep link is the row **inside** its disclosures, never the
disclosure itself, which is what lets a user agent that implements the HTML
Standard's auto-expanding `details` open every ancestor on fragment navigation.

⛔ **What this does NOT guarantee, stated rather than discovered** (Ruling 56):
that a user agent opens them. ⭐ Where one does not, the reader lands on the
section holding the target — with every ancestor summary addressable, focusable
and one keystroke from open — rather than on nothing. ⚠️ **What no policy here
can rescue is a link to a key this corpus does not declare**; that is the
producer's, and `anchor` exists so no producer spells one.

## ⛔ Markup on one line, in code, and not in a template (R13)

⭐ `render/page/__init__.py` draws the line and this is on its far side: *"loop
bodies and inline wrappers stay in code, because a file for a closing tag
removes no duplication and adds a hop."* ⚠️ `container.listing` and
`page.navigation.outline` render the same shape the same way.

## ⭐ Not one class name is typed here

⚠️ Every hook is an element, an `aria-label` or a `data-*` attribute, so this
page costs no entry in `SURFACE_HOOKS` and none in the stylesheet's own
vocabulary — which is what let `SF-34` be scheduled after the markup it styles.
⛔ **Two of the three hooks are spelled in `render.container.listing` too**, and
that duplication is reported rather than smuggled — `SF-14/1`.
"""

from __future__ import annotations

from studyforge.render.index import policy
from studyforge.render.index.entries import Document, Item, Section
from studyforge.render.markup import escape, escape_attribute, inline, safe_href
from studyforge.render.page import PageError

#: What the tree is labelled for a reader who cannot see it. ⛔ This framework's
#: own structural word, never a corpus's: every string on the page that names
#: the *material* comes out of the document (R1).
LIST_LABEL = "Contents"

#: The attribute that says whether a row could be linked. ⚠️ `data-*` rather
#: than a class, so this page needs no entry in a published class set.
READABLE_ATTRIBUTE = "data-readable"

#: What wraps a unit's numbering, so a stylesheet can reach it without the
#: numbering being glued to the title in one string.
NUMBERING_KIND = "numbering"

#: What wraps the corpus's own word for a section's depth, for the same reason.
LEVEL_KIND = "level"

#: How a fragment is introduced. ⛔ Named so `anchor` is the one composer.
FRAGMENT = "#"

#: What separates the positions in a refusal's address. ⚠️ Positions, never
#: keys: a key is a corpus's own text and this message reaches a build log (R7).
POSITION_SEPARATOR = "."


def anchor(key: str) -> str:
    """Return the fragment that addresses the row `key` names, on this page.

    ⛔ **Ask, never compose.** A producer that spelled `"#" + key` would be a
    second definition of this page's anchors, correct until the day one of them
    is escaped or prefixed and silently wrong from then on.
    """
    return f"{FRAGMENT}{key}"


def render(document: Document) -> str:
    """Return the whole tree, with the levels the policy opens already open."""
    opened = policy.open_to(document)
    rows = "".join(
        _section(section, (position,), opened)
        for position, section in enumerate(document.sections, start=1)
    )
    return f'<nav aria-label="{LIST_LABEL}"><ol>{rows}</ol></nav>'


def _section(section: Section, at: tuple[int, ...], opened: int) -> str:
    """Return one section as a disclosure holding everything under it."""
    children = "".join(
        _section(child, (*at, position), opened)
        for position, child in enumerate(section.sections, start=1)
    ) + "".join(
        _item(item, (*at, position)) for position, item in enumerate(section.items, start=1)
    )
    state = " open" if len(at) <= opened else ""
    return (
        f'<li><details id="{escape_attribute(section.key)}"{state}>'
        f"<summary>{_level(section)}{inline(section.title)}</summary>"
        f"<ol>{children}</ol></details></li>"
    )


def _item(item: Item, at: tuple[int, ...]) -> str:
    """Return one unit's row: linked when it reads, plainly listed when it does not."""
    body = f"{_numbering(item)}{inline(item.title)}"
    where = f'id="{escape_attribute(item.key)}"'
    if item.href is None:
        return f'<li {where} {READABLE_ATTRIBUTE}="false">{body}</li>'
    target = safe_href(item.href)
    if target is None:
        # ⛔ The href is DESCRIBED by its position and never reproduced (R7).
        # This branch fires precisely because the value is not a permitted
        # relative reference — which is where an absolute path and a rooted
        # href both arrive — and it runs over every unit in a corpus, into a
        # build log. The position is what tells the author where to look.
        raise PageError(
            f"the row at position {POSITION_SEPARATOR.join(str(step) for step in at)} of "
            f"the root index carries a link that is neither a permitted scheme nor a "
            f"relative reference inside the site; it is refused rather than dropped, "
            f"because this page is nothing but these links and a dropped one is a unit "
            f"nobody can open"
        )
    return (
        f'<li {where} {READABLE_ATTRIBUTE}="true">'
        f'<a href="{escape_attribute(target)}">{body}</a></li>'
    )


def _level(section: Section) -> str:
    """Return the corpus's own word for this depth and its trailing space, or `''`.

    ⚠️ Empty for a corpus that names its levels with nothing, and the space goes
    with it — a conditional separator left in the caller is a page that differs
    from its golden by one character on every such corpus.
    """
    if not section.level:
        return ""
    return f'<span data-kind="{LEVEL_KIND}">{escape(section.level)}</span> '


def _numbering(item: Item) -> str:
    """Return the reader-facing numbering and its trailing space, or `''`."""
    if not item.numbering:
        return ""
    return f'<span data-kind="{NUMBERING_KIND}">{escape(item.numbering)}</span> '
