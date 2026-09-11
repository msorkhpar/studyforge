r"""What a container page is written as, in what order, out of which templates.

**What it does.** Composes one container page: the same skeleton every unit page
has, filled with a container's own regions — what this container is, its units
in order, and the bar that points out of it.

**How you use it.** `compose(document, placement, links)` returns the page's
text; `container.render` is the public entry point and turns it into bytes.

**Depends on.** `render.templates` for the markup, `listing` for the body,
`render.markup` for the escaping, `corpus.placement.identity` for R4's block,
and `render.page` for `PageError`, `Links` and `between_units` — the bar itself,
taken from the page package's published surface rather than from inside it
(`W76`).

## ⛔ The skeleton is `page.html`, the unit page's own, and that is the design

⭐ **The two documents are one product.** A container page with its own skeleton
would be a second masthead, a second head, a second place a `<meta viewport>`
has to be remembered — and the day one gains a region the other silently would
not. ⚠️ **The epic asks the root index to share the unit page's palette and type
stack *by importing them rather than restating them*; this is the same ruling
one page earlier**, and it is why this task adds no template file.

⛔ **Five of the skeleton's slots are empty here, and they are empty
explicitly.** `templates.fill` refuses a placeholder with no value **and** a
value with no placeholder, so `outline`, `pending`, `player`, `breadcrumb` and
`mark` are passed as `""` rather than omitted — which means the day the skeleton drops a
slot this module fails by name instead of quietly losing a region. ⭐ **And the
day it GAINS one this module fails too, which is how `breadcrumb` arrived** —
`SF-15` added the slot and could not add it silently.

⚠️ **A container page has no outline, no pending panel, no player and no read
control, and each absence is a fact rather than an oversight:** its own contents
*are* the unit list, it declares no practices of its own, `SF-18`'s narration is
a unit's — and a read mark is a unit's too. A container is read by reading what
is under it, so the page that offers the control is the one whose reading it
records (`SF-30`). ⭐ **The marks themselves DO reach this page**, as a state on
the rows below, which is why each row carries the unit key a mark is filed under.
⚠️ **The trail is the one of the five that is a GAP rather than an absence**: a
container page sits in the hierarchy and has ancestors to name, and that its
`up` link is the root index is `SF-27`'s own note. ⛔ Wiring a trail here is that
task's row and not `SF-15`'s — see finding `SF-15/2`.

## ⛔ This module is the format (R10)

⚠️ The order of the slots below **is** the page, and an unchanged document must
re-render to identical bytes. ⛔ So: no clock, no filesystem enumeration, no set
iteration, and every optional region is exactly empty or exactly its markup plus
one newline — never a conditional newline somewhere else.

## ⛔ The identity block says `kind="container"`, and nothing infers it (R4)

⚠️ **`SF-04` discovers these pages by identity, not by filename.** The suffix
`.section.html` is what makes a scan *open* the file; what the file **is** comes
out of the block `corpus.placement.identity` renders and parses, so the two
halves cannot drift. ⭐ A container page moved or renamed is still exactly the
container it says it is.
"""

from __future__ import annotations

from studyforge.address import AddressError
from studyforge.corpus.placement import PlacementError
from studyforge.corpus.placement import identity as identity_block
from studyforge.render import templates
from studyforge.render.container import listing
from studyforge.render.container.entries import Document
from studyforge.render.container.placement import Placement
from studyforge.render.markup import escape, escape_attribute, inline
from studyforge.render.page import Links, PageError, between_units

#: The skeleton every page of this site is filled from — the unit page's own.
SKELETON = "page.html"

#: What a container page says it is, in R4's block. ⛔ One of
#: `placement.identity.KINDS`, and the reason a scan can tell the two pages
#: apart without reading a path.
KIND = "container"

#: What separates two regions of the body, and what closes an optional region.
JOIN = "\n"

#: What separates the parts of the masthead's second line.
META_SEPARATOR = " · "

#: Every page ends in exactly one newline. ⚠️ Appended here rather than left as
#: a trailing blank line in the template, because the loader strips one trailing
#: newline so an editor cannot silently lengthen it.
TRAILING_NEWLINE = "\n"

#: The skeleton slots a container page has nothing to put in. ⛔ Named and
#: passed rather than omitted — see this module's docstring.
EMPTY_SLOTS = ("breadcrumb", "mark", "outline", "pending", "player")


def compose(document: Document, placement: Placement, links: Links | None = None) -> str:
    """Return one container page's exact text.

    ⛔ Pure: the same document and the same placement give byte-identical
    output, every run, on every machine (R10).
    """
    rows = listing.render(document.address, document.items)
    body = JOIN.join(part for part in (note(document), rows) if part)
    return (
        templates.fill(
            SKELETON,
            title=escape(document.title),
            heading=escape(document.title),
            identity=_region(identity(document, placement)),
            stylesheet=escape_attribute(placement.stylesheet()),
            script=escape_attribute(placement.script()),
            meta=_region(meta(document)),
            body=body,
            nav=_region(between_units(links)),
            **dict.fromkeys(EMPTY_SLOTS, ""),
        )
        + TRAILING_NEWLINE
    )


def identity(document: Document, placement: Placement) -> str:
    """Return R4's block, saying which container this page is wherever it ends up.

    ⛔ Built from the record's own fields and never from the page's path:
    inferring identity from a location is the thing R4 forbids.
    """
    try:
        record = identity_block.Identity(
            corpus=placement.corpus,
            address=document.address,
            variant=document.variant,
            kind=KIND,
        )
    except (PlacementError, AddressError) as error:
        # ⛔ Re-typed, not re-worded: `placement` owns what an identity may say.
        # ⛔ **Narrow on purpose** — `PersonalDataLeak` is deliberately outside
        # this pair and travels through as itself (Ruling 58), so a caller
        # rendering a whole site cannot log a leak as one more page that did
        # not render.
        raise PageError(f"this container cannot identify itself: {error}") from None
    return identity_block.render(record)


def meta(document: Document) -> str:
    """Return the masthead's quieter second line: what this is, where it sits, in which variant.

    ⚠️ Assembled from the record's own fields and from no wording of this
    framework's own — `level` is the corpus's word for this depth,
    `manifest.levels[-1]`, and a sentence typed here would be one every corpus
    had to live with (R1).
    """
    parts = [document.level, *document.address.segments, document.variant]
    line = META_SEPARATOR.join(escape(part) for part in parts if part)
    return f"<p>{line}</p>" if line else ""


def note(document: Document) -> str:
    """Return what this container says about itself, or `''` when it says nothing.

    ⭐ **The corpus's own sentence, rendered as prose** — `container.note` — so
    the page answers *what is this module* with the material's words rather than
    with a heading and a list (R1).
    """
    said = document.note
    if not isinstance(said, str) or not said.strip():
        return ""
    return f"<p>{inline(said)}</p>"


def _region(markup: str) -> str:
    """Return one optional region: exactly empty, or its markup and one newline.

    ⭐ The conditional newline lives here and nowhere else. Spread across the
    slots it is a chance per slot to emit a page that differs from its golden by
    one blank line, which is the least interesting diff a reviewer can be handed.
    """
    return f"{markup}{JOIN}" if markup else ""
