r"""Where this page points — into itself, and back, forward and up.

**What it does.** Mints the anchors a unit page addresses itself by, builds the
in-page outline from the document being rendered, renders the trail that says
where in the material the reader is, and renders the bar that points at the
previous unit, the next one and the index.

**How you use it.**

    from studyforge.render.page import navigation

    navigation.section_anchor("practice-java")     # 's-practice-java'
    navigation.outline(document)                   # markup, or ''
    navigation.breadcrumb((navigation.Crumb("section", "Basics", "../i.html"),
                           navigation.Crumb("", "Your first class")))
    navigation.between_units(navigation.Links(previous=…, next=…, index=…))

**Depends on.** `render.templates` for the region wrappers and the link rows,
`render.pageassets` for the two hooks the trail's level word carries,
`render.markup` for escaping, and `page.errors`. ⛔ Not on `contents`: the
outline is derived from the one document being rendered, never from `toc.json`,
and a trail and a bar arrive as **plain values a caller built**, so this module
imports nothing from the package that computes a reading order and nothing from
a peer renderer. ⛔ Not on `render.index` either, which imports this package —
hence `FRAGMENT` below rather than `index.anchor`, and finding `SF-15/1`.

## ⛔ An anchor is derived from structure, never from a heading

⚠️ **A retitled section must not move every anchor beneath it.** `unit.sections`
makes exactly this argument for section keys — *"a content-derived key would
make a copy-edit silently orphan a unit's narration"* — and an anchor is the
same fact one layer out: a link into a page from a contents document, or from a
reader's own bookmark, survives an edit to the prose it points at.

⭐ So an anchor is `(section key, block position)`, both structural, and the
section key is already required to be a slug by the module that mints it.

## ⛔ These are anchors. `SF-12` mints no speech id (R21 open, `SF-12-survey/3`)

⚠️ **`SF-16` owns speech ids at M3** and the extraction source's own docstring
says why the two must not be one scheme: *"two numbering schemes that agree
today are exactly the coupling that breaks silently tomorrow."* ⭐ So this
module answers the question a page has at M1 — *what may be linked to?* — and
answers it for **headings and sections only**, which is what an outline and a
cross-page link actually address.

⛔ **Deliberately not one id per block.** Minting an anchor for every paragraph
would be the speech-id scheme under another name, arriving one milestone before
the task that owns it, and its agreement with `SF-16` would be a coincidence
nothing checks.

## The outline stops at level 3

⚠️ Level 4 and below are sub-points within a topic. Listing them turns a rail
that can be scanned in one glance into a second document — and a second document
that disagrees with the first is worse than no rail.

## ⛔ Ruling 164 here: every region is CHROME, so a refused href DROPS

⭐ **The bar drops the whole slot** — a bar with a dead `next` is worse than one
with no `next`, and the reader still has the trail, the outline and the page.

⛔ **The trail drops the LINK and keeps the CRUMB**, and that is the same ruling
rather than an exception to it. Its question is *"has the reader lost a WAY TO
GET SOMEWHERE, or has the page lost THE THING IT EXISTS TO SHOW?"* — and a crumb
is both at once: the **anchor** is the way somewhere, the **trail of labels** is
what the region exists to show. ⚠️ Dropping a crumb renumbers the hierarchy on
the page — *"Basics › Your first class"* where the material says *"Basics ›
Getting Started › Your first class"* is a true statement about a different
corpus, which is worse than an unlinked word.

## ⛔ A neighbour with NO PAGE is a declared type, not a guessed href

⚠️ **`Link(href=None)` is §7's third state**, spelled as
`render.index.Item(href=None)` spells it: *no page on this machine*. ⛔ A
renderer that cannot tell that from a **bad** href always picks the wrong one of
drop-or-raise, so the type is what makes Ruling 164 applicable rather than a coin
toss. ⭐ And it degrades instead of dangling: that unit still has a row on the
root index anchored by its own key (`SF-14`), so the slot points at `<the
index>#<the key>`, where the reader can see it is not built yet. ⛔ With no key,
or no index to hang the fragment on, nothing useful is left and the slot drops.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from studyforge.address import is_slug
from studyforge.render import templates
from studyforge.render.markup import escape, escape_attribute, inline, safe_href
from studyforge.render.page.errors import PageError
from studyforge.render.pageassets import SURFACE_HOOKS

#: Deepest heading level that earns a line in the outline.
OUTLINE_MAX_LEVEL = 3

#: The markup of the chrome regions this module renders. ⛔ **Files, not
#: f-strings** (R13, and `SF-34`): each wrapper carries a product string — the
#: word `Contents` and three `aria-label`s — and a product string typed in Python
#: is a sentence every corpus has to live with, in the one language nobody
#: thinks to look in when the page's wording is wrong. ⭐ The row bodies stay in
#: code, which is the line `render/page/__init__.py` draws: *"loop bodies and
#: inline wrappers stay in code, because a file for a closing tag removes no
#: duplication and adds a hop."*
OUTLINE_TEMPLATE = "outline.html"
BETWEEN_UNITS_TEMPLATE = "between-units.html"
BREADCRUMB_TEMPLATE = "breadcrumb.html"

#: What stands between two crumbs. ⛔ **A file for one glyph, which is R13 read
#: exactly as written**: `›` is a character a reader sees, chosen by this
#: framework, and a glyph in a loop body is the finding `SF-34` handed over.
#: ⚠️ Markup rather than a `::before` rule because the `file://` floor is the
#: baseline (R8) — a page opened with no stylesheet still reads as a trail.
SEPARATOR_TEMPLATE = "crumb-separator.html"

#: What a section's own anchor is prefixed with. ⛔ So a section can never
#: collide with a block anchor, which always reads `<key>-b<n>`.
SECTION_PREFIX = "s-"

#: What a block's anchor puts between the section key and the position.
BLOCK_INFIX = "-b"

#: How a fragment is introduced. ⛔ Named so this module has ONE composer of one
#: and no `"#" +` in a loop body — `render.index.disclosure.FRAGMENT` is the same
#: character for the same reason, and the two are deliberately not shared
#: because this package is the one `render.index` imports (finding `SF-15/1`).
FRAGMENT = "#"

#: The three slots of the between-units bar, in emitted order: the `Links` field,
#: and the template its row is authored in. ⛔ A tuple, so the order is stated
#: rather than depending on iteration (R10).
#:
#: ⛔ **The `rel` and the arrows left Python here — `SF-34`'s handed finding
#: discharged** (R13). They were `("previous", "prev", "← ")` and a `" →"`
#: decided by an `== "next"` test inside `_link`. ⭐ Three files rather than one
#: with a `${lead}` slot: a template whose glyph arrives as a substitution has
#: not moved the glyph out of Python, only the markup around it.
LINK_SLOTS = (
    ("previous", "link-previous.html"),
    ("index", "link-index.html"),
    ("next", "link-next.html"),
)

#: The attribute the trail's level word is reached by, and the value saying it is
#: one. ⛔ Taken from the published surface, never typed: `SF-34` made these the
#: one spelling after two renderers had each invented their own (`SF-14/1`).
KIND_ATTRIBUTE = SURFACE_HOOKS["kind"]
LEVEL_KIND = SURFACE_HOOKS["level"]

#: What the trail says about the crumb the reader is already on. ⛔ Structure,
#: never wording: it names no language, and is not a word on the page.
CURRENT = ' aria-current="page"'

#: How many crumbs earn a trail. ⛔ One crumb is a list of one, which is the
#: same argument `outline` makes: chrome that says nothing at all.
BREADCRUMB_MINIMUM = 2


@dataclass(frozen=True, slots=True)
class Link:
    """One destination outside this page: a relative href and what to call it.

    ⛔ `href` is relative and is emitted verbatim after a scheme check, because
    only the study order knows the path arithmetic (`SF-13`, `SF-14`) and this
    module must not invent it.

    ⭐ **`href=None` is a DECLARED absence** — *no page on this machine* — and
    `key` is the unit key its root-index row is anchored by, so the slot degrades
    to that row instead of dangling. ⛔ `None` rather than `""` for the reason
    `render.index.Item` gives: an empty string is an anchor that goes nowhere.
    """

    href: str | None
    label: str
    key: str = ""


@dataclass(frozen=True, slots=True)
class Links:
    """Where a unit page points when the reader has finished it.

    ⭐ Every field optional, and all three absent is the normal state at M1:
    nothing computes a reading order before `SF-13`, and a page with no bar is a
    page that renders exactly as it will once one does — minus the bar.
    """

    previous: Link | None = None
    next: Link | None = None
    index: Link | None = None


@dataclass(frozen=True, slots=True)
class Crumb:
    """One step of the trail: what the corpus calls this depth, and what sits there.

    ⛔ `level` is the **corpus's own word** for the depth — `manifest.levels[d]`,
    carried through `contents.Group.level` — and never a number, which would be
    this framework's vocabulary in a corpus's own chrome (R1). ⭐ Empty for a step
    the corpus names with nothing, and for the unit itself, which is the page.

    ⚠️ `href` is how **this page** addresses that step, or `None` where there is
    no page for it — the ordinary case for a container, which is then listed
    rather than linked.
    """

    level: str
    title: str
    href: str | None = None


def section_anchor(key: object) -> str:
    """Return the DOM id of a whole section: `practice-java` -> `s-practice-java`."""
    return SECTION_PREFIX + _slug(key, "a section key")


def block_anchor(section_key: object, position: int) -> str:
    """Return the DOM id of one addressable block: `java`, 3 -> `java-b3`."""
    if not isinstance(position, int) or isinstance(position, bool) or position < 0:
        raise PageError("a block's position on its page is 0 or more")
    return f"{_slug(section_key, 'a section key')}{BLOCK_INFIX}{position}"


def entries(document: dict) -> tuple[tuple[int, str, str], ...]:
    """`(level, label, href)` for the outline, in reading order.

    A section contributes one level-1 entry — ⚠️ **only on a page that has more
    than one**, because a lone section's name is already the page's title and
    listing it says nothing — and one entry per heading shallow enough to earn a
    line. ⭐ Every entry points at an anchor this page actually emitted, because
    both come from the same walk.
    """
    sections = list(document.get("sections") or ())
    out: list[tuple[int, str, str]] = []
    for section in sections:
        key = section.get("key")
        if len(sections) > 1:
            out.append(
                (1, str(section.get("heading") or key or ""), FRAGMENT + section_anchor(key))
            )
        for position, block in enumerate(section.get("blocks") or ()):
            if not isinstance(block, dict) or block.get("type") != "heading":
                continue
            level = heading_level(block)
            if level > OUTLINE_MAX_LEVEL:
                continue
            out.append(
                (level, str(block.get("text") or ""), FRAGMENT + block_anchor(key, position))
            )
    return tuple(out)


def heading_level(block: dict) -> int:
    """Clamped to h2..h6, never h1: the page's single h1 is the unit's title.

    ⚠️ Spelled here rather than in the block renderer because the outline and
    the heading itself must agree about the level, and two clamps are two
    chances to disagree by one.
    """
    try:
        level = int(block.get("level", 2))
    except TypeError, ValueError:
        level = 2
    return max(2, min(6, level))


def outline(document: dict) -> str:
    """Return the page's own contents, or `''` when nothing is worth listing.

    ⛔ One entry means a list of one, which is chrome that says nothing, so a
    document with a single section and no headings gets no outline at all.
    """
    found = entries(document)
    if len(found) < 2:
        return ""
    items = "".join(
        f'<li data-level="{level}"><a href="{escape_attribute(href)}">{inline(label)}</a></li>'
        for level, label, href in found
    )
    return templates.fill(OUTLINE_TEMPLATE, items=items)


def breadcrumb(crumbs: Sequence[Crumb] | None) -> str:
    """Return where the reader is, or `''` when the trail would say nothing.

    ⛔ The **last** crumb is the page itself: it carries `aria-current="page"` and
    is never a link, whatever href it was handed, because a page that links to
    itself is a way to get nowhere. ⚠️ A trail of one is no trail — see
    `BREADCRUMB_MINIMUM`.
    """
    if crumbs is None or len(crumbs) < BREADCRUMB_MINIMUM:
        return ""
    last = len(crumbs) - 1
    rows = "".join(
        _crumb(
            crumb,
            lead="" if position == 0 else templates.fill(SEPARATOR_TEMPLATE),
            current=position == last,
        )
        for position, crumb in enumerate(crumbs)
    )
    return templates.fill(BREADCRUMB_TEMPLATE, crumbs=rows)


def _crumb(crumb: Crumb, *, lead: str, current: bool) -> str:
    """Return one step of the trail, linked where there is something to link to.

    ⛔ The crumb survives a refused or absent href and the **anchor** is what
    drops — see this module's reading of Ruling 164. ⚠️ Both branches emit the
    same words, so a trail is never short by a step and never silently renumbers
    the hierarchy.
    """
    body = f"{_level(crumb)}{inline(crumb.title)}"
    target = None if current or crumb.href is None else safe_href(crumb.href)
    row = body if target is None else f'<a href="{escape_attribute(target)}">{body}</a>'
    return f"<li{CURRENT if current else ''}>{lead}{row}</li>"


def _level(crumb: Crumb) -> str:
    """Return the corpus's own word for this depth and its trailing space, or `''`.

    ⚠️ Empty for a step the corpus names with nothing, and the space goes with it
    — a conditional separator left in the caller is a page that differs from its
    golden by one character on every such corpus. ⭐ Spelled exactly as
    `render.index.disclosure` spells it, from the same two published hooks, so
    the trail and the index say *"section"* the same way.
    """
    if not crumb.level:
        return ""
    return f'<span {KIND_ATTRIBUTE}="{LEVEL_KIND}">{escape(crumb.level)}</span> '


def between_units(links: Links | None) -> str:
    """Return the previous/index/next bar, or `''` when nothing is pointed at."""
    if links is None:
        return ""
    parts = [
        rendered
        for field, row in LINK_SLOTS
        if (rendered := _link(getattr(links, field), row, links.index))
    ]
    if not parts:
        return ""
    return templates.fill(BETWEEN_UNITS_TEMPLATE, links="".join(parts))


def _link(link: Link | None, row: str, index: Link | None) -> str:
    """Return one slot of the bar, or `''` when there is nothing useful to point at.

    ⚠️ A refused scheme drops the slot rather than rendering dead text: this is
    chrome, and chrome that cannot be followed is worse than chrome that is not
    there. ⭐ A **declared** absence is not a refusal — it falls back to the
    unit's own row on the root index, and drops only when there is no key or no
    index to address that row from.
    """
    if link is None:
        return ""
    target = _destination(link, index)
    if target is None:
        return ""
    return templates.fill(row, href=escape_attribute(target), label=escape(link.label))


def _destination(link: Link, index: Link | None) -> str | None:
    """Return where this slot actually points, or `None` when nowhere useful does.

    ⛔ **The fallback is gated as ONE string, after composing.** A key is a
    corpus's own text; gating only the index's half would let a key no href can
    be spelled with reach the page, which is the half of `W57`'s lesson that was
    about the *set* rather than about the prefixes in it.
    """
    if link.href is not None:
        return safe_href(link.href)
    if not link.key or index is None or index.href is None:
        return None
    return safe_href(f"{index.href}{FRAGMENT}{link.key}")


def _slug(value: object, what: str) -> str:
    """Return an already-slug key, or refuse without quoting it.

    ⛔ **Required, never made.** `unit.sections` refuses a non-slug key when the
    section is built, for the reason that a filename is minted from it; this is
    the same rule one layer out, where a DOM id is minted from it. ⚠️ The value
    is not quoted: it comes from a file a person edits and can be a path (R7).
    """
    if not isinstance(value, str) or not is_slug(value):
        raise PageError(
            f"{what} must already be a slug, because a DOM id is minted from it and a "
            f"link into this page has to survive an edit to its prose"
        )
    return value
