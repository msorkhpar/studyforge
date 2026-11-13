r"""Diagrams on a page: which pages link Mermaid, and the files a corpus with diagrams writes.

**What it does.** Says whether a rendered body carries a diagram (a code figure the renderer framed
as one, from a `mermaid` fence) and, when it does, the three tags that draw it: Mermaid's script
(vendored, `mermaid.LICENSE`) and this framework's `diagram.css` and `diagram.js`. `files()` are
those three, by name, for `generate.site` to write.

**How you use it.** `page.document` appends `links(body, placement)` to a body; `generate.site`
writes `files()` for a corpus whose lessons carry a diagram (`generate.diagrampages.wanted`).

**Depends on.** `render.markup` and `render.pageassets.source`; the mark is the frame
attribute `page.blocks.figure` writes. ⛔ Not on `serve`: a diagram is drawn in the browser from
files beside the page, so a page opened from disk draws it, and nothing is requested from anywhere
else (R8).

## ⭐ The syntax is GitHub's, so a lesson reads the same on GitHub and on the site

A diagram is a ```` ```mermaid ```` fence, kept by the archive as any fence is: a `code` block whose
`lang` is `mermaid`. No new block type and no new key, and with scripting off the reader keeps the
diagram's source in the figure.

## ⛔ Absent means today, byte for byte

A body with no diagram links nothing, and a corpus with none writes no file: Mermaid is about
2.5 MB, and no corpus that does not use it carries it, nor does any page that does not show one.

## ⛔ The bundle is checked against its pin before it is written

`mermaid.min.js` is stored as the registry shipped it under a vendoring header, with ONE
rewrite (below). `files()` undoes the rewrite, hashes what follows the header and refuses a
bundle that no longer matches `SHA256`, so an edited or truncated library never reaches a site.

## ⚠️ The one rewrite: a dotted read of `local` is written `x["local"]`

d3, inside Mermaid, reads an XML namespace's local name with a dot. The personal-data gate
(`archive.scrub`), which the study server runs over every file it sends, reads a name ending in
the mDNS suffix as a machine's hostname and refused the whole bundle, so no diagram drew in a
served course. ⛔ The gate is not loosened for it. The property access is spelled the other
way JavaScript allows, which means exactly the same thing and carries no such suffix.
⭐ The rewrite is exactly invertible (the shipped bundle holds no `["local"]` of its own), and
`checked` refuses a bundle whose served form is not exactly the rewrite of the pinned one.
"""

from __future__ import annotations

import hashlib
import re

from studyforge.render.markup import escape_attribute
from studyforge.render.pageassets.errors import AssetError
from studyforge.render.pageassets.source import text

MERMAID_SCRIPT = "mermaid.min.js"
STYLESHEET_NAME = "diagram.css"
SCRIPT_NAME = "diagram.js"
PARTS = (MERMAID_SCRIPT, STYLESHEET_NAME, SCRIPT_NAME)

#: Mermaid's version and the sha256 of `dist/mermaid.min.js` as the npm registry shipped it
#: (the re-vendoring script prints it, after checking the tarball's sha512).
VERSION = "11.4.1"
SHA256 = "a43bc1afd446f9c4cc66ac5dd45d02e8d65e26fc5344ec0ef787f88d6ddb6f9e"

#: Where the vendoring header ends: the bundle as shipped starts after it.
HEADER_END = "*/\n"

#: A property read of `local` as shipped (with a dot), and as served (`t["local"]`).
LOCAL_SHIPPED = ".local"
LOCAL_SERVED = '["local"]'
LOCAL_READ = re.compile(r"(?<=[\w$\])])\.local(?![\w$])")

#: What marks a diagram in a rendered body: the frame attribute the figure renderer writes
#: (`blocks.figure.DIAGRAM_FRAME`; this module's test holds the two equal). ⚠️ Spelled the same
#: way in `diagram.js`, which finds the figures to draw.
MARK = 'data-frame="diagram"'


def carries(body: str) -> bool:
    """Whether a rendered body holds a diagram."""
    return MARK in body


def links(body: str, placement: object) -> str:
    """Return the tags a body with a diagram links, after it, and `''` for a body with none."""
    if not carries(body):
        return ""
    href = placement.asset
    return (
        f'<link rel="stylesheet" href="{escape_attribute(href(STYLESHEET_NAME))}">\n'
        f'<script src="{escape_attribute(href(MERMAID_SCRIPT))}" defer></script>\n'
        f'<script src="{escape_attribute(href(SCRIPT_NAME))}" defer></script>\n'
    )


def files() -> dict[str, str]:
    """Return the three shared files, by name, for a corpus whose pages link them."""
    found = {name: text(name) for name in PARTS}
    checked(found[MERMAID_SCRIPT])
    return found


def served_form(shipped: str) -> str:
    """Return the bundle as served: every dotted read of `local` written `x["local"]`."""
    if LOCAL_SERVED in shipped:
        raise AssetError("the Mermaid bundle already holds the served spelling; not invertible")
    return LOCAL_READ.sub(lambda _: LOCAL_SERVED, shipped)


def shipped_form(served: str) -> str:
    """Return the bundle as the registry shipped it, from its served form."""
    return served.replace(LOCAL_SERVED, LOCAL_SHIPPED)


def checked(bundle: str) -> str:
    """Return `bundle` when what follows its header is Mermaid as pinned, else refuse it."""
    at = bundle.find(HEADER_END)
    if at < 0:
        raise AssetError("the vendored Mermaid bundle carries no vendoring header")
    served = bundle[at + len(HEADER_END) :]
    shipped = shipped_form(served)
    if hashlib.sha256(shipped.encode("utf-8")).hexdigest() != SHA256:
        raise AssetError(f"the vendored Mermaid bundle does not match its pinned {VERSION} sha256")
    if served_form(shipped) != served:
        raise AssetError("the vendored Mermaid bundle is not exactly the served form of its pin")
    return bundle
