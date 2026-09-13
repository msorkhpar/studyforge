r"""What on this page may be linked to — its anchors, and the outline that uses them.

**What it does.** Mints the anchors a unit page addresses itself by, and builds
the in-page outline from the document being rendered.

**How you use it.**

    from studyforge.render.page import anchors

    anchors.section_anchor("practice-java")     # 's-practice-java'
    anchors.block_anchor("practice-java", 3)    # 'practice-java-b3'
    anchors.outline(document)                   # markup, or ''

**Depends on.** `address` for the slug rule, `render.templates` for the outline's
wrapper, `render.markup` for escaping and for the one fragment composer, and
`page.errors`. ⛔ Not on `contents`: the outline is derived from the one document
being rendered, never from `toc.json`. ⛔ Not on `render.index` either, which
imports this package — which is why an href here is `render.markup.anchor` of an
id rather than a `"#"` spelled locally (`W107`, `SF-15/1`).

## ⭐ Split from `page.navigation` at the seam `SF-15/5` named (`W107`)

⚠️ One module answered four questions — anchors, the outline, the trail, the bar
— at eight lines under its ceiling. ⭐ *What may be linked to* is this module;
*where this page points* is `page.navigation`.

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

"""

from __future__ import annotations

from studyforge.address import is_slug
from studyforge.render import templates
from studyforge.render.markup import anchor, escape_attribute, inline
from studyforge.render.page.errors import PageError

#: Deepest heading level that earns a line in the outline.
OUTLINE_MAX_LEVEL = 3

#: The markup of the outline's region. ⛔ **A file, not an f-string** (R13, and
#: `SF-34`): the wrapper carries a product string — the word `Contents` and an
#: `aria-label` — and a product string typed in Python is a sentence every corpus
#: has to live with. ⭐ The row bodies stay in code, which is the line
#: `render/page/__init__.py` draws.
OUTLINE_TEMPLATE = "outline.html"

#: What a section's own anchor is prefixed with. ⛔ So a section can never
#: collide with a block anchor, which always reads `<key>-b<n>`.
SECTION_PREFIX = "s-"

#: What a block's anchor puts between the section key and the position.
BLOCK_INFIX = "-b"


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
            out.append((1, str(section.get("heading") or key or ""), anchor(section_anchor(key))))
        for position, block in enumerate(section.get("blocks") or ()):
            if not isinstance(block, dict) or block.get("type") != "heading":
                continue
            level = heading_level(block)
            if level > OUTLINE_MAX_LEVEL:
                continue
            out.append((level, str(block.get("text") or ""), anchor(block_anchor(key, position))))
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
