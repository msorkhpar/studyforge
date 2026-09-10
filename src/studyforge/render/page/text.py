r"""How a string becomes safe page text — escaping, hrefs, and inline markers.

**What it does.** Turns the archive's text into markup: escapes it, checks a
link's scheme, and renders the four inline markers the Markdown reader
deliberately left in place.

**How you use it.**

    from studyforge.render.page import text

    text.escape("a < b")            # 'a &lt; b'
    text.escape_attribute(value)    # additionally neutralises "'"
    text.inline("see `x` and **y**")

**Depends on.** `re` and `page.errors`. ⛔ Nothing that knows what a block is:
every block renderer depends on this module, and it depends on none of them.

## ⛔ Escaping is not optional, and it is the only thing between the archive and
## the browser

⚠️ Teaching material quotes `<`, `>`, `&` and `"` constantly — inside code
blocks on almost every page, and inside prose whenever the subject is markup.
Getting this wrong is a rendering bug and an injection bug at the same time, so
**every** text path goes through `escape`, every attribute through
`escape_attribute`, and every href is additionally scheme-checked.

⭐ **`&` is replaced first**, or every entity the later replacements write is
escaped a second time and the page shows `&amp;lt;`.

## ⭐ The inline markers are rendered here, and this is their one definition

⚠️ **`archive.markdown` states that emphasis, inline code and links are left
untouched inside `text`** — *"because stripping them is exactly the loss it
exists to prevent"*. ⛔ **So something has to render them, and if nothing does,
the reading floor shows a reader literal backticks and `[label](href)`.** That
is this module.

⛔ **`SEGMENT_KINDS` and `segments()` are published for `SF-16`** (narration,
M3), which needs the same split for the *spoken* half and must take it from here
rather than write a second one. ⚠️ The extraction source made the same argument
in the opposite direction — its renderer imported the split from its speech
module — and the argument is the ordering, not the direction: **display and
speech must never disagree about where a marker begins.** ⭐ Only the
*rendering* differs, which is the whole point: speech drops the href, display
keeps it clickable.

⚠️ **A marker is rendered, never shown literally.** A parser that gains a marker
and a renderer that does not is exactly how markup reaches the page as text, so
the branch list below is checked against `SEGMENT_KINDS` by this module's test.

## ⛔ A refused scheme keeps its words and loses its link

⭐ `javascript:`, `data:` and `vbscript:` render as plain text rather than as a
live anchor. The corpus is trusted-ish; a page the reader opens in their own
browser is not the place to find out that it was not. ⚠️ A bare `example.com/x`
has no scheme and no path prefix — treating it as relative is wrong and treating
it as `http` is inventing intent — so it loses its link and keeps its words.
"""

from __future__ import annotations

import re

#: Ordered, and `&` is first. ⛔ Any other order double-escapes.
_ESCAPES = (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;"))

#: The prefixes a link may keep. ⛔ A closed set of what is permitted, never a
#: list of what is refused: the forbidden list is the one that is silently
#: incomplete, and `vbscript:` is the entry every version of it forgets.
SAFE_SCHEMES = ("http://", "https://", "mailto:", "#", "/", "./", "../")

#: What one inline segment can be. ⛔ Ordered as `_INLINE` alternates, so a
#: position where two markers could both start resolves the same way here as it
#: does in the expression.
SEGMENT_KINDS = ("text", "code", "link", "strong", "em")

#: The four markers, in precedence order. ⚠️ Code first: a backtick span may
#: contain any of the others and none of them may be read inside it.
_INLINE = re.compile(
    r"`([^`]+)`"  # 1    `code`
    r"|\[([^\]\n]+)\]\(([^)\s]*)\)"  # 2,3  [label](href)
    r"|\*\*([^\s*](?:[^*\n]*[^\s*])?)\*\*"  # 4    **strong**
    r"|\*([^\s*](?:[^*\n]*[^\s*])?)\*"  # 5    *em*
    r"|(?<!\w)_([^\s_](?:[^_\n]*[^\s_])?)_(?!\w)"  # 6    _em_
)


def escape(value: object) -> str:
    """Escape text content. ⛔ `&` first, or every later entity double-escapes."""
    out = str(value if value is not None else "")
    for char, entity in _ESCAPES:
        out = out.replace(char, entity)
    return out


def escape_attribute(value: object) -> str:
    """Escape for a double-quoted attribute value; also neutralises `'`.

    ⚠️ The apostrophe matters even though every attribute this renderer writes
    is double-quoted: a page is edited, and an attribute re-quoted by hand
    tomorrow must not become an escape hatch today.
    """
    return escape(value).replace("'", "&#39;")


def safe_href(href: object) -> str | None:
    """Return the href when its scheme is permitted, else `None` — render as text."""
    candidate = (href or "").strip() if isinstance(href, str) else ""
    if not candidate:
        return None
    lowered = candidate.lower()
    return candidate if lowered.startswith(SAFE_SCHEMES) else None


def segments(value: object) -> tuple[tuple[str, str, str], ...]:
    """Split text into `(kind, body, href)` segments, left to right.

    `kind` is one of `SEGMENT_KINDS`; `href` is empty for everything but a link,
    and `body` is the marker's *content* with the marker characters already
    removed. ⛔ Markers are never nested and never re-escaped — the archive
    stores them verbatim and this is their only reader.
    """
    text = value if isinstance(value, str) else ""
    out: list[tuple[str, str, str]] = []
    position = 0
    for match in _INLINE.finditer(text):
        if match.start() > position:
            out.append(("text", text[position : match.start()], ""))
        code, label, href, strong, em_star, em_score = match.groups()
        if code is not None:
            out.append(("code", code, ""))
        elif label is not None:
            out.append(("link", label, href or ""))
        elif strong is not None:
            out.append(("strong", strong, ""))
        else:
            out.append(("em", em_star if em_star is not None else em_score, ""))
        position = match.end()
    if position < len(text):
        out.append(("text", text[position:], ""))
    return tuple(out)


def inline(value: object) -> str:
    """Render one run of prose: the markers become markup, everything else escapes.

    ⛔ **Every branch escapes.** The marker decides which element the body is
    wrapped in; it never decides whether the body is trusted, and there is no
    path through this function on which text reaches the page unescaped.
    """
    out: list[str] = []
    for kind, body, href in segments(value):
        if kind == "code":
            out.append(f"<code>{escape(body)}</code>")
        elif kind == "strong":
            out.append(f"<strong>{escape(body)}</strong>")
        elif kind == "em":
            out.append(f"<em>{escape(body)}</em>")
        elif kind == "link":
            out.append(_anchor(body, href))
        else:
            out.append(escape(body))
    return "".join(out)


def _anchor(body: str, href: str) -> str:
    """One inline link, or its words alone when the scheme was refused."""
    target = safe_href(href)
    if target is None:
        return escape(body)
    return f'<a href="{escape_attribute(target)}" rel="noopener noreferrer">{escape(body)}</a>'
