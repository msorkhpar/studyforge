r"""Math on a page: which pages link KaTeX, and the files a corpus with math writes.

**What it does.** Says whether a rendered body carries a formula and, when it does, the four tags
that draw it: KaTeX's stylesheet and script (vendored, `katex.LICENSE`) and this framework's
`math.css` and `math.js`. `files()` are those four, by name, for `generate.site` to write.

**How you use it.** `page.document` appends `links(body, placement)` to a body; `generate.site`
writes `files()` for a corpus whose lessons carry math (`generate.mathpages.wanted`).

**Depends on.** `render.markup` and `render.pageassets.source`. ⛔ Not on `serve`: the formulas
are drawn in the browser from files beside the page, so a page opened from disk draws them (R8).

## ⭐ The syntax is GitHub's, so a lesson reads the same on GitHub and on the site

A display formula is a ```` ```math ```` fence and an inline one is a code span between dollar
signs, $`x_{i,t}`$. The archive keeps both as it keeps any fence and any code span, so a corpus
needs no new block type and no new key, and a page without math is byte for byte what it was.

## ⛔ Absent means today, byte for byte

A body with no formula links nothing, and a corpus with none writes no file: KaTeX is about 640 KB
with its faces, and no corpus that does not use it carries it.

## ⭐ The faces are inlined when the stylesheet is written, never stored inlined

`katex.min.css` is kept as KaTeX ships it, naming each face as `fonts/<face>.woff2`. Its 20 faces
sit in `assets/katex/`, each pinned by sha256 in `FACES`, and `files()` writes the stylesheet with
every face's source list replaced by that face's bytes as a `data:` URI, as `pageassets.faces`
does for the site's own faces: a page opened from a file draws them with no request (R8).
"""

from __future__ import annotations

import base64
import hashlib
import re

from studyforge.render.markup import escape_attribute
from studyforge.render.pageassets.errors import AssetError
from studyforge.render.pageassets.source import ASSET_DIR, text

KATEX_STYLESHEET = "katex.min.css"
KATEX_SCRIPT = "katex.min.js"
STYLESHEET_NAME = "math.css"
SCRIPT_NAME = "math.js"
PARTS = (KATEX_STYLESHEET, KATEX_SCRIPT, STYLESHEET_NAME, SCRIPT_NAME)

#: Where KaTeX's faces sit, under the asset directory, and each face's sha256 as vendored.
FACE_DIR = "katex"
FACES = {
    "KaTeX_AMS-Regular.woff2":
        "0cdd387c9590a1a9f9794560022dbb59654a7d86f187aa0c81495ad42d3a7308",
    "KaTeX_Caligraphic-Bold.woff2":
        "de7701e42cf1f4cf0b766c03fb27977207eee2f4fd5d76fa82188406da43ea4c",
    "KaTeX_Caligraphic-Regular.woff2":
        "5d53e70ad607c2352162dec9e0923fb54ecdafaccbf604cd8dcf7d00facb989b",
    "KaTeX_Fraktur-Bold.woff2":
        "74444efd593c005e3f4573b44524704c0af0a937fe911cca9e94068d0d140d3f",
    "KaTeX_Fraktur-Regular.woff2":
        "51814d270d06ff0255dba0799994fa4d8c84d11f09951d47595f4abb1f3602dc",
    "KaTeX_Main-Bold.woff2":
        "0f60d1b897938ec918c8ce073092411baf9438f6739465693ff18b0f9d20b021",
    "KaTeX_Main-BoldItalic.woff2":
        "99cd42a3c072d918f2f44984a807cf7aa16e13545fd0875fc07c6c65f99e715b",
    "KaTeX_Main-Italic.woff2":
        "97479ca6cce906abc961ecac96faa5f9ca2e61b8e7670d475826bcdee9a7c267",
    "KaTeX_Main-Regular.woff2":
        "c2342cd8b869e01752a9321dc17213fc40d4d04c79688c1d43f2cf316abd7866",
    "KaTeX_Math-BoldItalic.woff2":
        "dc47344dbb6cb5b655c8460d561f4df5f501b90c804ad3c6cec65fe322351ab1",
    "KaTeX_Math-Italic.woff2":
        "7af58c5ec8f132a2ddde9027c6d7814decce4d3b822a11192a42a20e2e973264",
    "KaTeX_SansSerif-Bold.woff2":
        "e99ae51144bf1232efcc1bfe5add36262c6866b0faab24fa75740e1b98577a62",
    "KaTeX_SansSerif-Italic.woff2":
        "00b26ac825e2095056396e0553b8ac26d3f8ad158c3826e28b4c45b385c4714a",
    "KaTeX_SansSerif-Regular.woff2":
        "68e8c73ef42afd3ccec58bf0fba302cce448938e7fc020a5e31f8a952eee1342",
    "KaTeX_Script-Regular.woff2":
        "036d4e95149b69ff9bcc0cd55771efeb25ffa3947293e69acd78d5ac328c684b",
    "KaTeX_Size1-Regular.woff2":
        "6b47c40166b6dbe21a5dfca7718413f2147fd2399be1ba605d8ad39cedf25dfe",
    "KaTeX_Size2-Regular.woff2":
        "d04c54219f9eaec6d4d4fd42dfb28785975a4794d6b2fc71e566b9cd6db842dd",
    "KaTeX_Size3-Regular.woff2":
        "73d591271b1604960cb10bb90fee021670af7297017e0e98480b332d11f51995",
    "KaTeX_Size4-Regular.woff2":
        "a4af7d414440a1c1790825cfb700cf9cf43b0f2c4b04f0ebc523011ad9853ec0",
    "KaTeX_Typewriter-Regular.woff2":
        "71d517d67827787cfabdf186914cc3358eda539e37931941f2b2fd4a21f68c0b",
}

#: One face's whole source list in KaTeX's stylesheet: its woff2, then its woff and ttf fallbacks.
FACE_SOURCE = re.compile(
    r'src:url\(fonts/(KaTeX_[A-Za-z0-9_-]+)\.woff2\) format\("woff2"\)'
    r'(?:,url\([^)]*\) format\("[a-z]+"\))*'
)

#: What marks a formula in a rendered body: a code figure captioned `math`, or a code span between
#: dollar signs. ⚠️ Spelled the same way in `math.js`, which finds the formulas to draw.
DISPLAY_MARK = '<span class="what">math</span>'
INLINE_MARK = "$<code>"


def carries(body: str) -> bool:
    """Whether a rendered body holds a formula of either form."""
    return DISPLAY_MARK in body or INLINE_MARK in body


def links(body: str, placement: object) -> str:
    """Return the tags a body with a formula links, after it, and `''` for a body with none."""
    if not carries(body):
        return ""
    href = placement.asset
    return (
        f'<link rel="stylesheet" href="{escape_attribute(href(KATEX_STYLESHEET))}">\n'
        f'<link rel="stylesheet" href="{escape_attribute(href(STYLESHEET_NAME))}">\n'
        f'<script src="{escape_attribute(href(KATEX_SCRIPT))}" defer></script>\n'
        f'<script src="{escape_attribute(href(SCRIPT_NAME))}" defer></script>\n'
    )


def files() -> dict[str, str]:
    """Return the four shared files, by name, for a corpus whose pages link them."""
    found = {name: text(name) for name in PARTS}
    found[KATEX_STYLESHEET] = inlined(found[KATEX_STYLESHEET])
    return found


def inlined(stylesheet: str) -> str:
    """Return KaTeX's stylesheet with each face's source list as its pinned woff2 bytes.

    ⛔ Refuses a face whose bytes no longer match its pin, and a stylesheet in which a face source
    is left unreplaced: either would ship a page that requests a file or draws an unpinned face.
    """
    written = FACE_SOURCE.sub(lambda match: _source(match.group(1)), stylesheet)
    if "url(fonts/" in written:
        raise AssetError("KaTeX's stylesheet names a face source this build cannot inline")
    return written


def _source(face: str) -> str:
    name = f"{face}.woff2"
    if name not in FACES:
        raise AssetError("KaTeX's stylesheet names a face that is not pinned")
    try:
        content = (ASSET_DIR / FACE_DIR / name).read_bytes()
    except OSError as error:
        # ⛔ `error.strerror`, never `error`: it would carry the absolute path (R7).
        raise AssetError(f"cannot read a KaTeX face: {error.strerror}") from None
    if hashlib.sha256(content).hexdigest() != FACES[name]:
        raise AssetError(f"the KaTeX face {name!r} does not match its pinned sha256")
    encoded = base64.b64encode(content).decode("ascii")
    return f'src:url(data:font/woff2;base64,{encoded}) format("woff2")'
