r"""The words, script and stylesheet of a course's read-only preview, and the edits of one page.

**What it does.** Holds, for `preview`, everything that is TEXT: the banner every page
carries, the note that stands where a server-only part was, the small script that
builds the repository's links from `location`, its stylesheet, and the edits that
take one built page to its read-only form (`remove_server_parts`, `finish`).

**How you use it.** `remove_server_parts(html)` first, which drops every server-only part and says
whether the page had narration; then `finish(html, ...)`, once every page's links are
known, which adds the banner, the script and the stylesheet.

**Depends on.** `re` and `html` only. ⛔ Nothing here reads a file, starts a process or
names an account, a host or a repository.

## ⛔ The preview is made from the built page, and the library is not touched

⭐ Every edit is a deterministic text edit of a page the site already built, and
the shipped `page.js` and `page.css` are copied as they are. ⛔ A part is not
hidden by a style that a script could undo: it is REMOVED, and a note stands in its
place, so nothing in the preview can ask a server that is not there.

## ⭐ The repository is never written down

⛔ No page holds an owner or a repository name. `PREVIEW_JS` builds the links at
run time from `location`: a project page is served at
`https://<owner>.github.io/<repo>/`, so the owner is the host's first label and the
repository is the path's first segment. ⭐ Anywhere else (a local server, another
domain) it builds nothing, and the text stays without a link.
"""

from __future__ import annotations

import re
from html import escape

#: The README section every note points to, as GitHub spells its anchor.
RUN_ANCHOR = "run-it-locally-with-docker"

#: The attribute that marks a link the script points at the README's section.
RUN_LINK = "data-preview-run"

#: The attribute that marks a source link the script points at the source viewer.
SOURCE_LINK = "data-code-path"

#: ⭐ An empty icon, so a browser does not ask a static host for a `favicon.ico` it does not have.
NO_ICON = "data:,"

#: The words of the banner every page carries.
BANNER = (
    "<strong>Read-only preview.</strong> Reading, the quizzes, your reading marks and the "
    "index filter work here. Running and submitting practices, the editor, code examples "
    "that open in the editor and narration need the course running "
    f"<a {RUN_LINK}>locally with Docker</a>."
)

#: The note that stands where a practice's Run, Submit and editor were.
PRACTICE_NOTE = (
    "Run and Submit, and the editor to write your answer in, are available when the "
    f"course runs locally with Docker: see <a {RUN_LINK}>Run it locally with Docker</a>. "
    "This preview shows the statement only."
)

#: The note that stands where a code example's editor and Run were.
EXAMPLE_NOTE = (
    "Opening this example in the editor beside the lesson, and running its test, are "
    f"available when the course runs locally with Docker: see <a {RUN_LINK}>Run it locally "
    "with Docker</a>. The links above open the files in the repository's source viewer."
)

#: The note that stands where the narration player was.
NARRATION_NOTE = (
    "Narration is available when the course runs locally with Docker: see "
    f"<a {RUN_LINK}>Run it locally with Docker</a>."
)

PREVIEW_CSS = """\
/* The read-only preview: a banner on every page and a note where a server-only part was. */
[data-preview-banner] {
  padding: 0.6rem var(--gutter, 1rem);
  background: var(--surface-2, #e8eef7);
  color: var(--fg, #14213d);
  border-bottom: 1px solid var(--rule-strong, #94a3b8);
  font: 0.9rem/1.45 var(--font-ui, system-ui, sans-serif);
  text-align: center;
}
[data-preview-banner] p { margin: 0; }
[data-preview-note] {
  margin: 0.75rem 0;
  padding: 0.6rem 0.8rem;
  border-left: 4px solid var(--accent, #2563eb);
  background: var(--surface-2, #e8eef7);
  color: var(--fg, #14213d);
  font: 0.95rem/1.5 var(--font-ui, system-ui, sans-serif);
}
[data-preview-banner] a, [data-preview-note] a { color: inherit; text-decoration: underline; }
"""

PREVIEW_JS = """\
/* The read-only preview: the links that need the repository, built from where this page is served.

   A project page is served at https://<owner>.github.io/<repo>/, so the owner is the host's first
   label and the repository is the path's first segment. Anywhere else nothing is built and the
   text stays as it is, without a link. Nothing here makes a request. */
(function () {
  'use strict';

  var LABEL = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;
  var RUN = 'a[data-preview-run]';
  var SOURCE = 'a[data-code-path]';

  function repository(hostname, pathname) {
    var labels = String(hostname || '').toLowerCase().split('.');
    if (labels.length !== 3 || labels[1] !== 'github' || labels[2] !== 'io') { return null; }
    var first = String(pathname || '').split('/').filter(Boolean)[0];
    if (!labels[0] || !first || /\\.html?$/i.test(first)) { return null; }
    if (!LABEL.test(labels[0]) || !LABEL.test(first)) { return null; }
    return 'https://github.com/' + labels[0] + '/' + first;
  }

  function plain(link) {
    link.replaceWith(document.createTextNode(link.textContent));
  }

  window.studyforgePreview = { repository: repository };
  var base = repository(window.location.hostname, window.location.pathname);
  [].slice.call(document.querySelectorAll(RUN)).forEach(function (link) {
    if (!base) { plain(link); return; }
    link.href = base + '/blob/main/README.md#run-it-locally-with-docker';
  });
  [].slice.call(document.querySelectorAll(SOURCE)).forEach(function (link) {
    var path = link.getAttribute('data-code-path') || '';
    if (!base || !path) { plain(link); return; }
    link.href = base + '/blob/main/' + path.split('/').map(encodeURIComponent).join('/');
  });
}());
"""

_PLAYER = re.compile(r'<footer id="player"[^>]*>.*?</footer>\s*', re.DOTALL)
_NARRATOR = re.compile(r'<audio id="narrator"[^>]*></audio>\s*')
_AUDIO = re.compile(r' data-audio="[^"]*"')
_PRACTICE = re.compile(r'(<section data-practice="[^"]*"[^>]*>)(.*?)(</section>)', re.DOTALL)
_EXAMPLE = re.compile(
    r"(<details data-code-example[^>]*>)(.*?)(</details>)",
    re.DOTALL,
)
_SUMMARY = re.compile(r"<summary>.*?</summary>", re.DOTALL)
_LIST = re.compile(r'<ul class="items">.*?</ul>', re.DOTALL)
_SOURCE_TAG = re.compile(r"<a\b[^>]*\bdata-code-path=[^>]*>")
_HREF = re.compile(r' href="[^"]*"')
_BODY = re.compile(r'<body[^>]*>(\s*<a href="#content">[^<]*</a>)?')
_HEAD_END = "</head>"
_BODY_END = "</body>"
_HEADER_END = "</header>"


class PageRefused(ValueError):
    """A page whose shape this module will not edit, and why."""


def _note(kind: str, words: str) -> str:
    return f'<p data-preview-note="{kind}">{words}</p>'


def _practice(found: re.Match[str]) -> str:
    if "<section" in found.group(2):
        raise PageRefused("a practice panel holds a section, so it cannot be replaced whole")
    return found.group(1) + "\n" + _note("practice", PRACTICE_NOTE) + "\n" + found.group(3)


def _example(found: re.Match[str]) -> str:
    inside = found.group(2)
    summary, items = _SUMMARY.search(inside), _LIST.search(inside)
    if not summary or not items:
        raise PageRefused("a code example lacks its summary or its list of files")
    return (
        found.group(1)
        + summary.group(0)
        + items.group(0)
        + _note("example", EXAMPLE_NOTE)
        + found.group(3)
    )


def remove_server_parts(html: str) -> tuple[str, bool]:
    """Return the page with every server-only part removed, and whether it had narration."""
    narrated = bool(_PLAYER.search(html) or _AUDIO.search(html))
    html = _PLAYER.sub("", html)
    html = _NARRATOR.sub("", html)
    html = _AUDIO.sub("", html)
    html = _PRACTICE.sub(_practice, html)
    html = _EXAMPLE.sub(_example, html)
    html = _SOURCE_TAG.sub(lambda tag: _HREF.sub("", tag.group(0)), html)
    if narrated and _HEADER_END in html:
        html = html.replace(_HEADER_END, _HEADER_END + "\n" + _note("narration", NARRATION_NOTE), 1)
    return html, narrated


def finish(html: str, *, assets: str) -> str:
    """Return the page with the banner, the stylesheet and the script added.

    `assets` is the directory of `preview.css` and `preview.js` as this page reaches
    it: a relative path with no trailing slash.
    """
    banner = f'<div data-preview-banner role="note"><p>{BANNER}</p></div>'
    if _HEAD_END not in html or _BODY_END not in html or not _BODY.search(html):
        raise PageRefused("a page without a head and a body cannot carry the banner")
    icon = "" if 'rel="icon"' in html else f'<link rel="icon" href="{NO_ICON}">\n'
    css = f'{icon}<link rel="stylesheet" href="{escape(assets)}/preview.css">\n'
    js = f'<script src="{escape(assets)}/preview.js" defer></script>\n'
    html = html.replace(_HEAD_END, css + _HEAD_END, 1)
    html = _BODY.sub(lambda body: body.group(0) + "\n" + banner, html, count=1)
    before, end, after = html.rpartition(_BODY_END)
    return before + js + end + after
