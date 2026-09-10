r"""The unit page: one served document and one placement decision in, bytes out.

**What it does.** Renders the reading surface for one unit — the page a reader
opens by double-clicking it.

**How you use it.**

    from studyforge.corpus import placement
    from studyforge.render.page import Placement, render

    profile = placement.profile_for(manifest.placement)
    where = Placement(
        corpus=manifest.source,
        unit=profile.unit(address, document["unit"], document["title"]),
        shared=profile.corpus(),
    )
    (root / where.unit.page).write_bytes(render(document, where))

`Links` carries the previous/next/index bar when something knows the reading
order; left out, the page renders without it. `PageError` is the only exception
this package raises.

**Depends on.** `unit` for what a served document is, `corpus.placement` for
where things go and for R4's identity block, `archive.blocks` for the
vocabulary, and `render.templates` and `render.pageassets` for the markup and
the class names. ⛔ Not on `serve`: a page that needed a server to render is a
page that fails the `file://` floor, and that floor is the baseline rather than
a fallback.

## The five rulings this package exists to hold

⛔ **R8 — the page works over `file://`, with no network and no server.** Every
asset, every clip and every media file is addressed **relative to the page**, so
a unit directory copied anywhere still reads and still plays. A remote video
becomes a link the reader chooses to follow, never an embed that fetches on
open.

⛔ **R10 — what is emitted is byte-for-byte reproducible.** No clock, no
directory enumeration, no set iteration. `document` states the slot order and
`blocks` states the vocabulary order; both are tuples.

⛔ **R13 — markup is a source file, never a Python string.** The skeleton, the
section wrapper, the figures, the pending panel and the player are files under
`render/templates/`; loop bodies, inline wrappers and one-line containers stay
in code, because a file for a closing tag removes no duplication and adds a hop.

⛔ **R4 — every page carries its own identity and nothing infers it from a
path.** The block is rendered by `corpus.placement.identity`, which also parses
it, so the two halves cannot drift.

⛔ **R1 — the framework knows nothing about any source.** Not a corpus name, not
a language table, not a sentence of one site's wording. Every string on the page
that is not this framework's own structure comes out of the document.

## What sits where

| module | the question it answers |
|---|---|
| `text` | how does a string become safe page text? |
| `blocks` | which renderer answers for this block type — and which bypass escaping? |
| `blocks.prose` | heading, para, list, table, rule, quote, disclosure — all escaped |
| `blocks.figure` | what does the reader look at rather than read? |
| `blocks.verbatim` | ⛔ which block types bypass escaping — `html`, and nothing else |
| `section` | what wraps one section, and what sits above it? |
| `navigation` | where does this page point — into itself, back, forward, up? |
| `assets` | where does this page reach, relative to itself? |
| `document` | what is written, in what order, out of which templates? |
| `errors` | `PageError`, the only exception any of it raises |

## ⛔ The seam whose failure is silent, and why it is its own module

⚠️ **`para` and `html` are byte-identical in shape** — both `{"type": …,
"text": str}` — and `html` is the only one of eleven block types emitted
unescaped. ⛔ **Decide escaping from the *text* rather than from the declared
*type* and a tag-shaped paragraph is consumed as markup: the page renders, is
well-formed, carries every other word, `validate` passes, nothing logs — and the
sentence is gone.** ⭐ That is the promise `SF-07` declined CommonMark's type-7
raw-HTML rule to keep, and this package is its only enforcer. See
`blocks/verbatim.py`, which exists so the answer to *which types are raw?* is
`ls` rather than reading branches.

## ⛔ Not one class name is typed outside a template file

⚠️ Every class in code comes from `pageassets.class_for` or `SURFACE_HOOKS`, and
every class in a template is asserted against that published set. ⭐ **That makes
the two-sided markup contract structural**: a stylesheet and a template that
disagree about a class name produce a page that renders, carries every word, and
is unstyled — with no error anywhere — and this package cannot reach that state
by typing a name, because it does not type one.
"""

from __future__ import annotations

from studyforge.render.page.assets import AUDIO_ATTRIBUTE, Placement
from studyforge.render.page.document import compose
from studyforge.render.page.errors import PageError
from studyforge.render.page.navigation import Link, Links

#: What a page is written as. ⛔ Stated once: a page written as anything else is
#: a page whose bytes depend on a locale, which R10 forbids.
ENCODING = "utf-8"

#: ⛔ The package's whole public surface. A consumer that has to import
#: `studyforge.render.page.document` directly is a consumer this contract failed.
__all__ = [
    "AUDIO_ATTRIBUTE",
    "ENCODING",
    "Link",
    "Links",
    "PageError",
    "Placement",
    "compose",
    "render",
]


def render(document: dict, placement: Placement, links: Links | None = None) -> bytes:
    """Render one unit page.

    ⭐ **Bytes, not text, and that is the contract.** What is compared against a
    golden file, written to disk and served is a byte string; handing back text
    would leave the encoding to whoever wrote the file, and R10's guarantee
    would hold everywhere except the one step that matters.
    """
    return compose(document, placement, links).encode(ENCODING)
