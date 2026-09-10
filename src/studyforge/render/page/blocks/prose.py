r"""The blocks a reader reads — heading, para, list, table, rule, quote, disclosure.

**What it does.** Renders the seven block types that are prose or hold prose.
⛔ **Every one of them escapes its text**, and there is no path through this
module on which a block's own characters reach the page as markup.

**How you use it.** `RENDERS` names the types this module answers for and
`render(block, position, …)` renders one; both are read by the dispatcher, and
nothing else calls this module directly.

**Depends on.** `page.text` for escaping and the inline markers, `page.navigation`
for a heading's anchor, and `render.pageassets` for the class names. ⛔ Not on
`page.assets`: nothing here addresses a file.

## ⛔ Not one class name is typed in this module

⚠️ Every class comes from `pageassets.class_for` or `SURFACE_HOOKS`. ⭐ **That
makes the two-sided markup contract structural rather than checked:** this
module *cannot* invent a name the stylesheet does not target, because it does
not spell one. The failure that would otherwise be silent — a page that renders,
carries every word, and is unstyled — is unrepresentable here.

## ⛔ A container's children are rendered by the dispatcher, not here

⚠️ `quote` and `disclosure` receive their inner markup as `children`. ⭐ The one
recursion over the vocabulary lives in the dispatcher, which walks
`CONTAINER_TYPES` — the same argument `archive.blocks.walk` makes: *a consumer
that names `quote` itself is the next `disclosure` waiting to be forgotten.*

## ⚠️ `disclosure` is present-but-withheld, and `open` is the author's

⛔ Nothing here may show a disclosure by default. Every surveyed use of
`<details>` in real material hides an **exercise answer**, so the archive's own
`open` is carried through and never defaulted to true.
"""

from __future__ import annotations

from studyforge.archive.blocks import BLOCK_TYPES
from studyforge.render.page.navigation import block_anchor, heading_level
from studyforge.render.page.text import escape, escape_attribute, inline
from studyforge.render.pageassets import SURFACE_HOOKS, class_for


def render(
    block: dict,
    position: int,
    *,
    placement: object = None,
    section: str = "",
    children: str = "",
) -> str:
    """Render one prose block. ⛔ `placement` is unused and is part of the shape.

    ⚠️ Every renderer in this package takes the same arguments, so the
    dispatcher holds one call and no branch on which renderer wants what. A
    renderer that quietly took fewer would be the one that has to be special-
    cased the day it needs one more.
    """
    del placement
    return _RENDERERS[block["type"]](block, position, section, children)


def _heading(block: dict, position: int, section: str, children: str) -> str:
    """One heading, carrying the anchor the outline and any inbound link use."""
    del children
    level = heading_level(block)
    anchor = escape_attribute(block_anchor(section, position))
    return f'<h{level} id="{anchor}">{inline(block.get("text"))}</h{level}>'


def _para(block: dict, position: int, section: str, children: str) -> str:
    """Return one paragraph, escaped.

    ⛔ See this package's `verbatim` module for the one block type that is not,
    and for why the difference cannot be read off the text.
    """
    del position, section, children
    return f"<p>{inline(block.get('text'))}</p>"


def _rule(block: dict, position: int, section: str, children: str) -> str:
    """Return a thematic break: the element, and nothing else."""
    del block, position, section, children
    return "<hr>"


def _listing(block: dict, position: int, section: str, children: str) -> str:
    """One list, ordered or not, its items rendered as inline prose."""
    del position, section, children
    tag = "ol" if block.get("ordered") else "ul"
    klass = escape_attribute(class_for("list"))
    items = "".join(f"<li>{inline(item)}</li>" for item in block.get("items") or ())
    return f'<{tag} class="{klass}">{items}</{tag}>'


def _table(block: dict, position: int, section: str, children: str) -> str:
    """One table, inside its own scrolling box.

    ⛔ The wrapper is not decoration: a table wider than the reading column must
    scroll inside its own box, or the page scrolls sideways and every paragraph
    goes with it.
    """
    del position, section, children
    klass = escape_attribute(SURFACE_HOOKS["table_scroll"])
    parts = [f'<div class="{klass}"><table>']
    headers = block.get("headers") or ()
    if headers:
        cells = "".join(f"<th>{inline(header)}</th>" for header in headers)
        parts.append(f"<thead><tr>{cells}</tr></thead>")
    parts.append("<tbody>")
    for row in block.get("rows") or ():
        cells = "".join(f"<td>{inline(cell)}</td>" for cell in row)
        parts.append(f"<tr>{cells}</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def _quote(block: dict, position: int, section: str, children: str) -> str:
    """Return a quotation, holding whatever blocks it holds.

    ⚠️ A container, not a paragraph in italics: a list or a code block inside a
    quote must still read as itself.
    """
    del block, position, section
    return f"<blockquote>{children}</blockquote>"


def _disclosure(block: dict, position: int, section: str, children: str) -> str:
    """Content the archive records as shown on demand — a real `<details>`.

    ⭐ It opens, closes and takes keyboard focus with scripting off entirely,
    which is the third state between shown and absent. ⛔ `open` is the
    author's, delivered from the archive, and is never defaulted here.
    """
    del position, section
    klass = escape_attribute(class_for("disclosure"))
    opened = " open" if block.get("open") else ""
    summary = escape(block.get("summary") or "")
    return f'<details class="{klass}"{opened}><summary>{summary}</summary>{children}</details>'


#: `block type -> the function that renders it`. ⛔ Named functions rather than
#: a chain of `if`s, so what this module answers for is a mapping a diff can
#: read — and `RENDERS` below is derived from it, so the two cannot drift.
_RENDERERS = {
    "heading": _heading,
    "para": _para,
    "list": _listing,
    "table": _table,
    "rule": _rule,
    "quote": _quote,
    "disclosure": _disclosure,
}

#: The block types this module answers for, in the vocabulary's own order.
#: ⛔ **Derived from `BLOCK_TYPES`, never typed a second time.** Seven names
#: written twice in one module is the fifth copy of the block vocabulary this
#: project has now removed four of, and `test_blocks` fails a module that spells
#: four of them without saying where it got them.
RENDERS = tuple(name for name in BLOCK_TYPES if name in _RENDERERS)
