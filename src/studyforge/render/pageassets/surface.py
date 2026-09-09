"""The class names the reading surface styles, published so a renderer can use them.

**What it does.** States the markup vocabulary the shared stylesheet and
scripts target — one entry per archive block type that needs a hook.

**How you use it.** A renderer takes the class from here rather than typing it:
`SURFACE_CLASSES["code"]` is what a code block's `<figure>` must carry.

**Depends on.** `studyforge.archive.blocks` for the vocabulary, and nothing
else. ⛔ **The keys are the archive's, never retyped here.** A block type added
to the vocabulary and not answered for below raises at import — where today it
would silently acquire no class and render unstyled, which is the same failure
this file exists to prevent arriving by a different door.

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

from studyforge.archive.blocks import BLOCK_TYPES

#: What each block type's element carries, or `None` where it needs none.
#: ⛔ **Every block type in the vocabulary appears**, answered either way: a
#: heading, a paragraph, a thematic break, a table and a quote are styled as
#: the plain elements they are, because a class that adds nothing is a class
#: that has to be kept in step for nothing — and saying so explicitly is what
#: makes a *new* block type a loud failure here rather than an unstyled page.
#:
#: ⚠️ The values are this file's own and the keys are the archive's. That is
#: the whole of the seam: `SURFACE_CLASSES["list"] == "items"` is deliberate
#: and unchanged, so nothing can invert the mapping and read a class name back
#: as a block type (R4 applied to markup).
_CLASS_OF = {
    "heading": None,
    "para": None,
    "code": "code",
    "table": None,
    "list": "items",
    "image": "image",
    "video": "video",
    "rule": None,
    "quote": None,
    "html": None,
    "disclosure": "disclosure",
}

#: `archive block type -> the class its element carries`, for the types that
#: have one. ⛔ Built by walking `BLOCK_TYPES`, so the keys come from the one
#: block-type list (SF-06) and a vocabulary change cannot pass unnoticed.
SURFACE_CLASSES = {
    block_type: _CLASS_OF[block_type]
    for block_type in BLOCK_TYPES
    if _CLASS_OF[block_type] is not None
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
