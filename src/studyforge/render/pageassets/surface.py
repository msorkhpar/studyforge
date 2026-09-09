"""The class names the reading surface styles, published so a renderer can use them.

**What it does.** States the markup vocabulary the shared stylesheet and
scripts target — one entry per archive block type that needs a hook.

**How you use it.** A renderer takes the class from here rather than typing it:
`SURFACE_CLASSES["code"]` is what a code block's `<figure>` must carry.

**Depends on.** Nothing.

⭐ **This exists because the failure it prevents is silent.** A stylesheet and
a template that disagree about a class name produce a page that renders,
carries every word, and is unstyled — with no error anywhere. Before the split
between them existed they were one codebase and could not disagree; SF-11
lands before SF-12, so the agreement has to be written down and checked.

⚠️ **SF-12 may rename any of these**, and that is a change to this file plus
the stylesheet, together. ⛔ What it may not do is invent a second name for
something already here: `test_surface` asserts that every class the shared
stylesheet targets appears in this mapping, so a rename that touches only one
side fails.

⛔ **These are hooks, not semantics.** The archive says what a block *is*; a
class name says what the stylesheet may reach. Nothing downstream may read a
class name back as a block type — that is R4's argument about paths, applied
to markup.
"""

from __future__ import annotations

#: `archive block type -> the class its element carries`. Only the types that
#: need a hook: a heading, a paragraph, a thematic break and a quote are styled
#: as the plain elements they are, because a class that adds nothing is a class
#: that has to be kept in step for nothing.
SURFACE_CLASSES = {
    "code": "code",
    "image": "image",
    "video": "video",
    "disclosure": "disclosure",
    "list": "items",
}

#: Wrappers and controls the surface styles that are not block types. ⛔ The
#: scroll wrapper is not decoration: a table wider than the column must scroll
#: inside its own box, or the page scrolls sideways and every paragraph with it.
SURFACE_HOOKS = {
    "table_scroll": "scroll",
    "copy_button": "copy",
    "code_caption": "what",
}


def class_for(block_type: str) -> str | None:
    """Return the class an element of `block_type` carries, or None when it needs none."""
    return SURFACE_CLASSES.get(block_type)
