r"""A lesson's links to its own code: marked, and the panel they open in.

**What it does.** Marks every link on a unit page that leads to a code file of
the corpus with that file's corpus-relative path (`data-code-path`), and
renders, once per page that has one, the panel such a file opens in — which
says, as built, why the link opens the file as plain text.

**How you use it.** `page.document` calls `body, paths = mark(body, placement)`
over the page's rendered sections, and places `render(paths, placement)` after
`<main>`; both are empty-handed for a page that links no code, which then
renders byte for byte as it did.

**Depends on.** `corpus.placement` for the generated directory's name,
`render.templates` and `render.markup`. ⛔ Not on `serve` and not on `execute`:
a page renders over `file://`, and this names no API, no origin and no port
(R8).

## ⭐ Which link is code is read from the page's own geometry

⭐ **A link to a corpus file is written relative to the page by `unit.mentions`
(W488)**, and the page knows where it sits, so the file is the link resolved
from the page. It is code when it stays inside the corpus, stays outside the
generated directory — a page, a clip or an asset is never code — and ends in a
suffix the corpus's declared runtimes write (`Placement.code`, which is `()` for
a page that does not sit beside the corpus's files, and for a corpus that
declares no runtime). ⛔ **The link is left exactly as it is**: its href is
W488's plain file view, which is what it opens whenever the editor does not.

⚠️ **The anchor is found by the one shape `render.markup.text` writes**,
`<a href="…" rel="noopener noreferrer">`, over text in which every literal
character the material carried is escaped — so a `<a` inside a code block is
`&lt;a` and is never read as a link.

## ⛔ The panel says WHY as built, and the served page says the rest

⭐ **Built, the panel is one sentence**: a code file opens as plain text,
because the course's editor is not running here — and how to start it. That is
true over `file://` and true on a served page whose corpus has no editor up, so
it ships visible. ⭐ **Served with the editor up**, `code-links.js` hides it,
shows the sentence saying the editor opens a COPY of the code, and opens each
marked link in the panel's two windows. ⛔ **The panel is framework structure**
(R1): its words are this framework's, in `CODE_TEMPLATE`, and never the
material's.
"""

from __future__ import annotations

import re
from html import unescape
from pathlib import PurePosixPath
from urllib.parse import unquote

from studyforge.corpus.placement.profile import GENERATED_ROOT
from studyforge.render import templates
from studyforge.render.markup import escape_attribute
from studyforge.render.page.assets import Placement

#: The panel a page's code opens in.
CODE_TEMPLATE = "code-panel.html"

#: The attribute a code link carries: the file's path, relative to the corpus.
PATH_ATTRIBUTE = "data-code-path"

#: The one shape `render.markup.text` writes an inline link in.
ANCHOR = re.compile(r'<a href="(?P<href>[^"]*)" rel="noopener noreferrer">')

#: An href that carries a scheme, and so names no file of the corpus.
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def mark(body: str, placement: Placement) -> tuple[str, tuple[str, ...]]:
    """Return `body` with each code link marked, and the files marked, in order, once each."""
    if not placement.code:
        return body, ()
    found: list[str] = []

    def marked(match: re.Match[str]) -> str:
        path = code_file(unescape(match["href"]), placement)
        if path is None:
            return match.group(0)
        if path not in found:
            found.append(path)
        opening = match.group(0)
        return f'{opening[:-1]} {PATH_ATTRIBUTE}="{escape_attribute(path)}">'

    return ANCHOR.sub(marked, body), tuple(found)


def code_file(href: str, placement: Placement) -> str | None:
    """Return the corpus-relative code file `href` leads to from this page, or `None`."""
    path = re.split(r"[?#]", href, maxsplit=1)[0]
    if not path or SCHEME.match(href) or href.startswith("/") or href.startswith("#"):
        return None
    walked: list[str] = []
    for part in [*PurePosixPath(placement.unit.page).parent.parts, *unquote(path).split("/")]:
        if part in ("", "."):
            continue
        if part == "..":
            if not walked:
                return None
            walked.pop()
        else:
            walked.append(part)
    if not walked or walked[0] == GENERATED_ROOT or not walked[-1].endswith(placement.code):
        return None
    return "/".join(walked)


def render(paths: tuple[str, ...], placement: Placement) -> str:
    """Return the panel a page's code opens in, or `''` for a page that links none."""
    if not paths:
        return ""
    return templates.fill(CODE_TEMPLATE, corpus=escape_attribute(placement.corpus))
