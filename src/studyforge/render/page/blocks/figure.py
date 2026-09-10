r"""What the reader looks at rather than reads — code, image and video.

**What it does.** Renders the three block types that are a figure: a code
listing, a picture and a video. ⛔ **Every one of them escapes its text**, and
each is emitted from a template file rather than from a Python string (R13).

**How you use it.** `RENDERS` names the types this module answers for and
`render(block, position, …)` renders one; both are read by the dispatcher.

**Depends on.** `page.assets` for where a file sits relative to the page,
`render.markup` for escaping, `render.templates` for the markup, and `page.errors`.

## ⛔ The file is addressed relative to the page, and the profile chose where

⚠️ The archive's own `src` is `media/diagram.svg` — a path inside the *archive*.
What reaches the page is the **placed** copy, whose directory the placement
profile chose, so only the filename survives and `Placement.media` does the
arithmetic. ⭐ A renderer that echoed the archive's directory would address a
file placement never put there, on a page that renders perfectly.

## ⛔ A remote video is a link, never an `<iframe>` (R8)

⚠️ An iframe fetches the moment the page opens, and the standing rule is that a
unit page makes **no network request at all**. A link is inert until the reader
clicks it — and it is a link rather than a dropped block because *"do not lose
the lesson at any cost"*: material that teaches by embedding a player must not
render as "watch the video below" above nothing.

## ⚠️ `preload="metadata"`, and it is not a detail

⛔ A lesson video is megabytes. Opening a unit must cost the reader its
*duration* and nothing else; `preload="auto"`, or omitting the attribute and
letting the browser decide, turns every page open into a download of something
the reader may never play.

## ⭐ Highlighting happens in the browser, so the class here is the library's

⚠️ `language-<lang>` is Prism's own API — the vendored bundle reads it out of
the page it was shipped with. ⛔ It is deliberately *not* in
`pageassets.SURFACE_CLASSES`, which publishes the classes **this project's**
stylesheet targets; a library's contract is not this project's to keep in step,
and `test_surface` says so from the other side.
"""

from __future__ import annotations

from studyforge.render import templates
from studyforge.render.markup import escape, escape_attribute
from studyforge.render.page.assets import Placement, is_remote, media_kind
from studyforge.render.page.errors import PageError

#: The block types this module answers for.
RENDERS = ("code", "image", "video")

#: What a code figure's caption says when the archive recorded no language.
UNLABELLED_CODE = "code"

#: What a remote video's link says when the archive recorded no title.
REMOTE_VIDEO_LABEL = "Watch this video on the original site"


def render(
    block: dict,
    position: int,
    *,
    placement: Placement | None = None,
    section: str = "",
    children: str = "",
) -> str:
    """Render one figure. ⚠️ `position`, `section` and `children` are the shape."""
    del position, section, children
    return _RENDERERS[block["type"]](block, placement)


def _code(block: dict, placement: Placement | None) -> str:
    """One code listing, captioned with the language the archive recorded.

    ⛔ The copy button is **not** rendered. `copy-code.js` creates it, because a
    button written into the markup would sit there doing nothing with scripting
    off, and a control that does nothing is worse than no control.
    """
    del placement
    language = (block.get("lang") or "").strip()
    return templates.fill(
        "code.html",
        caption=escape(language or UNLABELLED_CODE),
        language=f' class="language-{escape_attribute(language.lower())}"' if language else "",
        text=escape(block.get("text") or ""),
    )


def _image(block: dict, placement: Placement | None) -> str:
    """One picture, sized in advance where the archive knew the width.

    ⚠️ The width is passed through so the browser can reserve the box before the
    file arrives; without it a page of diagrams reflows as each one loads. ⛔
    Only a positive integer is emitted — a width of `None`, `0` or something
    unparseable is the archive saying it does not know, and inventing a number
    would be worse than letting the image size itself.
    """
    alt = str(block.get("alt") or "")
    return templates.fill(
        "image.html",
        src=escape_attribute(_href(block, placement)),
        alt=escape_attribute(alt),
        width=_width(block),
        caption=f"<figcaption>{escape(alt)}</figcaption>" if alt.strip() else "",
    )


def _video(block: dict, placement: Placement | None) -> str:
    """Return a player when the file is on disk, a link when it never came down."""
    title = str(block.get("title") or "").strip()
    if is_remote(block.get("src")):
        return templates.fill(
            "video-link.html",
            src=escape_attribute(block.get("src") or ""),
            label=escape(title or REMOTE_VIDEO_LABEL),
        )
    return templates.fill(
        "video.html",
        src=escape_attribute(_href(block, placement)),
        poster="",
        caption=f"<figcaption>{escape(title)}</figcaption>" if title else "",
    )


def _href(block: dict, placement: Placement | None) -> str:
    """Where this figure's file sits, relative to the page showing it."""
    if placement is None:
        raise PageError(
            f"a {block['type']!r} block addresses a file, so it cannot be rendered "
            f"without knowing where this page sits"
        )
    return placement.media(media_kind(block["type"]), block.get("src"))


def _width(block: dict) -> str:
    """`' width="800"'`, or `''` when the archive declared no usable width.

    ⛔ **A positive `int` and nothing else** — deliberately narrower than
    `int(value)`, which the extraction source used. `int(1.5)` is `1`, so a
    width the archive recorded as a float would reach the page as a
    one-pixel image: a silently wrong number, which is the one outcome worse
    than no number at all.
    """
    width = block.get("width")
    if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
        return ""
    return f' width="{width}"'


#: `block type -> the function that renders it`. ⛔ Named functions rather than
#: a chain of `if`s, so `RENDERS` and the branches cannot drift.
_RENDERERS = {"code": _code, "image": _image, "video": _video}
