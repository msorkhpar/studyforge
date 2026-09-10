r"""Which renderer answers for this block type — and the one recursion over them.

**What it does.** Maps every block type in the archive vocabulary to exactly one
renderer, walks a document's blocks in order, and recurses into the two types
that hold other blocks.

**How you use it.**

    from studyforge.render.page import blocks

    markup = blocks.render_all(section["blocks"], placement=where, section=key)

`RENDERERS` is the mapping and `RAW_TYPES` is the set that bypasses escaping —
published because a test asserts what it is, not because a caller branches on it.

**Depends on.** `archive.blocks` for the vocabulary, the three renderer modules,
and `page.errors`. ⛔ The keys are the archive's and are never retyped here.

## ⛔ Every block type is answered for, or this package will not import

⚠️ A type in the vocabulary that no module claims, and a module claiming a type
the vocabulary does not have, are both refused at import — where today the first
would render a lesson's content as a silently missing paragraph and the second
would be dead code nobody could see. ⭐ Same shape as `pageassets.surface`, for
the same reason and against the same list.

⛔ **And no type is claimed twice.** Two renderers for one type is a mapping
whose answer depends on module import order, which is exactly the class of thing
R10 forbids.

## ⛔ `RAW_TYPES` is derived from the module, never typed here

⚠️ **The one thing this package must never let drift** is which types skip
escaping. `verbatim.RENDERS` is that list, and this module reads it rather than
restating it; the package's test then derives the *expected* set from
`BLOCK_TYPES` and asserts it is exactly `{"html"}`. ⭐ Three statements of the
same fact would be two chances to disagree — so there is one, and a check.

## ⛔ The recursion is here, and it is derived

⚠️ A container's children are rendered by this module and handed to the
container's renderer as `children`. ⭐ Which types recurse comes from
`CONTAINER_TYPES`, so a third container type is walked on the day it is added —
the same argument `archive.blocks.walk` makes: *a consumer that names `quote`
itself is the next `disclosure` waiting to be forgotten.*

## ⚠️ One signature, for every renderer

⛔ Each renderer takes `(block, position, *, placement, section, children)` and
ignores what it does not need. A renderer that took fewer would be the one that
has to be special-cased the day it needs one more, and the dispatcher would grow
a branch per module — which is the shape this package exists to avoid.
"""

from __future__ import annotations

from studyforge.archive.blocks import BLOCK_TYPES, CONTAINER_TYPES
from studyforge.render.page.blocks import figure, prose, verbatim
from studyforge.render.page.errors import PageError

#: The modules that answer for block types, in a stated order. ⛔ A tuple, so
#: the mapping below does not depend on iteration order (R10).
MODULES = (prose, figure, verbatim)

#: What separates two rendered blocks. ⭐ A newline, so a generated page can be
#: read and diffed by a person — a page emitted on one line is one no reviewer
#: will ever look at.
JOIN = "\n"

__all__ = ["JOIN", "MODULES", "RAW_TYPES", "RENDERERS", "render_all", "render_one"]


def _mapping() -> dict:
    """`block type -> its renderer`, checked against the vocabulary as it is built."""
    built: dict = {}
    for module in MODULES:
        for block_type in module.RENDERS:
            if block_type in built:
                raise PageError(
                    f"two renderers answer for {block_type!r}; which one wins would "
                    f"depend on import order"
                )
            if block_type not in BLOCK_TYPES:
                raise PageError(
                    f"{module.__name__} renders {block_type!r}, which is not in the "
                    f"archive's vocabulary; the keys are the archive's"
                )
            built[block_type] = module.render
    missing = [name for name in BLOCK_TYPES if name not in built]
    if missing:
        raise PageError(
            f"no renderer answers for {missing}; a block type nobody renders is a "
            f"lesson's content missing from the page with no error anywhere"
        )
    return {name: built[name] for name in BLOCK_TYPES}


#: `block type -> renderer`, in vocabulary order.
RENDERERS = _mapping()

#: ⛔ The block types whose text reaches the page unescaped. Derived from the
#: module that owns them — see `verbatim` for what makes this the one line in
#: the package that must not drift.
RAW_TYPES = frozenset(verbatim.RENDERS)


def render_all(blocks, *, placement=None, section: str = "") -> str:
    """Render a run of blocks in reading order, joined by `JOIN`."""
    return JOIN.join(
        render_one(block, position, placement=placement, section=section)
        for position, block in enumerate(blocks or ())
    )


def render_one(block, position: int, *, placement=None, section: str = "") -> str:
    """Render one block, recursing first into the blocks it holds."""
    if not isinstance(block, dict):
        raise PageError(f"a block is an object; block {position} of this section is not")
    block_type = block.get("type")
    renderer = RENDERERS.get(block_type)
    if renderer is None:
        raise PageError(
            f"nothing renders a block of type {block_type!r}; the archive's vocabulary "
            f"is {list(BLOCK_TYPES)}, and a block silently dropped is a lesson short "
            f"of a paragraph with nothing to show for it"
        )
    children = (
        render_all(block.get("blocks"), placement=placement, section=section)
        if block_type in CONTAINER_TYPES
        else ""
    )
    return renderer(block, position, placement=placement, section=section, children=children)
