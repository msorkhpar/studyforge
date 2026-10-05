r"""The site's search index: what a reader can find, read back off the pages a build wrote.

**What it does.** Reads each rendered page, keeps its title, its trail and the text under
each heading, and writes one script, `search-index.js`, that the search part loads when a
reader first opens the search. The library that ranks the words, `minisearch.js`, is
vendored beside it.

**How you use it.** `files(pages)` takes `(url, html)` pairs, `url` being the page's address
from the shared asset directory, and returns `filename -> content` for the two files a build
writes beside `page.js`.

**Depends on.** `html.parser` and `json`. Nothing here touches a corpus: the index is read from
the HTML, so it can only ever say what a page says.

## ⛔ What is never indexed

⭐ **A page is read, never its answers.** Everything inside an element that carries any
`data-practice*`, `data-mock*`, `data-form*`, `data-deck*` or `data-review*` attribute is
skipped: that is where a quiz's questions, its key and a mock exam's key live, and where a
practice's solution does. ⛔ A `<details>` whose summary says answer, key or solution is
skipped as well. Scripts, styles, templates and hidden elements are skipped, and so is
everything outside `<main>`.

⭐ **A code example is indexed once.** The language tabs of one example hold the same idea in
each language; only its first panel is read, so a search finds the example and does not
list it once per language.

## ⭐ One record per heading

A page is cut at each heading (`h1` to `h4`) into records of `(heading, anchor, text)`, so a
result can name the part of the page a word is in and open it at that heading. Only a page whose
identity says it is a unit is read in full; the contents pages and the root index are indexed
by their title and trail alone, because their body is a list of the units' titles.
"""

from __future__ import annotations

import html as htmllib
import json
import re
from html.parser import HTMLParser

from studyforge.render.pageassets.source import text as part
from studyforge.render.pageassets.surface import SURFACE_HOOKS

#: The two files written beside the page bundle.
INDEX_NAME = "search-index.js"
LIBRARY_NAME = "minisearch.js"

#: The part files this module writes, for the census of what is on disk.
SEARCH_PARTS = (LIBRARY_NAME,)

#: What the script assigns, and the shape version a reader of it checks.
GLOBAL = "window.studyforge=window.studyforge||{};window.studyforge.searchIndex="
VERSION = 1

#: The shape version of a sharded index (a manifest, shards, repeated texts as record numbers).
SHARDED_VERSION = 2

#: ⭐ The most bytes one index file may hold. The serve gate refuses a text file over 4 MiB, so an
#: index that would pass this is split into shards of about this size and a small manifest
#: (`search-index.js`) that names them. A small course stays one file.
SHARD_BYTES = 3 * 1024 * 1024

#: Where a shard puts its records for the search part to merge: `searchShards[<file name>]`.
SHARD_GLOBAL = "window.studyforge=window.studyforge||{};window.studyforge.searchShards=window.studyforge.searchShards||{};window.studyforge.searchShards["

#: Elements that never carry something a reader searches for.
SILENT_TAGS = frozenset({"script", "style", "template", "noscript", "svg", "head"})

#: Elements with no end tag, so they never open a level.
VOID_TAGS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track",
     "wbr"}
)

#: An attribute name that marks a region holding answers or exercises.
WITHHELD_PREFIXES = ("data-practice", "data-mock", "data-form", "data-deck", "data-review")

#: A summary that marks a folded answer.
FOLDED_ANSWER = re.compile(r"\b(answer|answers|key|solution|solutions)\b", re.IGNORECASE)

#: Where a record is cut.
HEADINGS = frozenset({"h1", "h2", "h3", "h4"})

#: Elements after which a space is needed so two words never fuse.
BLOCK_TAGS = frozenset(
    {"p", "li", "ul", "ol", "div", "section", "pre", "figure", "figcaption", "table", "tr", "td",
     "th", "br", "dt", "dd", "blockquote", "details", "summary", "h1", "h2", "h3", "h4", "h5", "h6"}
)

SPACE = re.compile(r"\s+")


def _squash(text: str) -> str:
    return SPACE.sub(" ", text).strip()


class _Reader(HTMLParser):
    """One pass over a page: its title, its trail, its identity and its records."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.identity = ""
        self.crumbs: list[str] = []
        self.sections: list[dict] = [{"heading": "", "anchor": "", "parts": []}]
        self._stack: list[tuple[str, str]] = []
        self._in_title = False
        self._in_identity = False
        self._in_crumbs = False
        self._crumb: list[str] | None = None
        self._crumb_skip = 0
        self._main_depth: int | None = None
        self._silent = 0
        self._examples: list[list[int]] = []
        self._folds: list[tuple[int, int, int]] = []
        self._summary: list[str] | None = None
        self._heading: tuple[str, list[str]] | None = None

    # -- state -------------------------------------------------------------

    @property
    def indexing(self) -> bool:
        return self._main_depth is not None and self._silent == 0

    def _withheld(self, tag: str, attrs: dict[str, str | None]) -> bool:
        if tag in SILENT_TAGS or "hidden" in attrs:
            return True
        return any(name.startswith(WITHHELD_PREFIXES) for name in attrs)

    def _add(self, text: str) -> None:
        if self.indexing and text:
            self.sections[-1]["parts"].append(text)

    # -- parser events -----------------------------------------------------

    def handle_starttag(self, tag, attr_list):  # noqa: C901 - one switch over the page's regions
        attrs = dict(attr_list)
        if tag == "title":
            self._in_title = True
        if tag == "script" and attrs.get("id") == "studyforge-identity":
            self._in_identity = True
        if tag == "nav" and attrs.get("aria-label") == "Breadcrumb":
            self._in_crumbs = True
        if self._in_crumbs and tag == "li":
            self._crumb = []
        level = attrs.get(SURFACE_HOOKS["kind"]) == "level"
        if self._in_crumbs and (attrs.get("aria-hidden") == "true" or level):
            self._crumb_skip += 1 if tag not in VOID_TAGS else 0
            kind = "crumbskip"
        else:
            kind = ""
        if tag in VOID_TAGS:
            if tag == "br":
                self._add(" ")
            return
        if tag == "main":
            self._main_depth = len(self._stack)
        marker = kind
        if self._main_depth is not None:
            if self._withheld(tag, attrs):
                self._silent += 1
                marker = "silent"
            elif tag == "div" and "data-example" in attrs:
                self._examples.append([0])
                marker = marker or "example"
            elif attrs.get("role") == "tablist" or "data-example-label" in attrs:
                self._silent += 1
                marker = "silent"
            elif attrs.get("role") == "tabpanel" and self._examples:
                if self._examples[-1][0] >= 1:
                    self._silent += 1
                    marker = "silent"
                else:
                    self._examples[-1][0] += 1
            elif tag == "details":
                mark = (len(self.sections), len(self.sections[-1]["parts"]), len(self._stack))
                self._folds.append(mark)
            elif tag == "summary" and self._folds:
                self._summary = []
            if tag in HEADINGS and self._silent == 0:
                self._heading = (attrs.get("id") or "", [])
        self._stack.append((tag, marker))

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        self._pop_to(tag)

    def _pop_to(self, tag: str) -> None:
        names = [name for name, _ in self._stack]
        if tag not in names:
            return
        while self._stack:
            name, marker = self._stack.pop()
            self._close(name, marker)
            if name == tag:
                break

    def _close(self, name: str, marker: str) -> None:
        if name == "title":
            self._in_title = False
        if name == "script":
            self._in_identity = False
        if marker == "silent":
            self._silent -= 1
        if marker == "example" and self._examples:
            self._examples.pop()
        if marker == "crumbskip":
            self._crumb_skip -= 1
        if name == "li" and self._crumb is not None:
            self.crumbs.append(_squash(" ".join(self._crumb)))
            self._crumb = None
        if name == "nav" and self._in_crumbs:
            self._in_crumbs = False
        if name == "summary" and self._summary is not None:
            said = _squash(" ".join(self._summary))
            self._summary = None
            if FOLDED_ANSWER.search(said):
                self._folds[-1] = (*self._folds[-1][:2], -1)
        if name == "details" and self._folds:
            sections, parts, depth = self._folds.pop()
            if depth == -1:
                del self.sections[sections:]
                del self.sections[-1]["parts"][parts:]
        if name in HEADINGS and self._heading is not None and self.indexing:
            anchor, words = self._heading
            self._heading = None
            heading = _squash(" ".join(words))
            if heading:
                first = self.sections[-1]
                if name == "h1" and not first["heading"] and not first["parts"]:
                    self.sections[-1].update(heading=heading, anchor=anchor)
                else:
                    self.sections.append({"heading": heading, "anchor": anchor, "parts": []})
        elif name in HEADINGS:
            self._heading = None
        if name == "main":
            self._main_depth = None
        if name in BLOCK_TAGS:
            self._add(" ")
            if self._crumb is not None:
                self._crumb.append(" ")

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)
        if self._in_identity:
            self.identity += data
        if self._crumb is not None and self._crumb_skip == 0:
            self._crumb.append(data)
        if self._summary is not None:
            self._summary.append(data)
        if self._heading is not None and self._silent == 0:
            self._heading[1].append(data)
            return
        self._add(data)


def read(html: str) -> dict:
    """One page as `{title, crumb, unit, sections}`, `sections` being `(heading, anchor, text)`."""
    reader = _Reader()
    reader.feed(html)
    reader.close()
    # ⭐ Read as text, not decoded: the page's identity says `"<field>":"unit"` for a unit and
    # no other field of it ever takes that value.
    unit = '":"unit"' in reader.identity.replace(" ", "")
    crumbs = [c for c in reader.crumbs if c]
    sections = [
        (s["heading"], s["anchor"], _squash(" ".join(s["parts"]))) for s in reader.sections
    ]
    return {
        "title": _squash("".join(reader.title_parts)),
        "crumb": " › ".join(crumbs[1:-1]),
        "unit": unit,
        "sections": [s for s in sections if s[0] or s[2]],
    }


#: A quiz option's sentence is searched for in a served file from this many words (the same floor
#: as `serve.withheld.MIN_WORDS`, which this module does not import).
MIN_WORDS = 4

_SAYS = re.compile(r'"says"\s*:\s*(?=\{)')


def quiz_sentences(pages: list[tuple[str, str]]) -> set[str]:
    """Every option sentence the pages' own quiz scripts carry, whitespace collapsed.

    ⭐ Read off the HTML, like the rest of the index: a quiz page holds its sentences in a
    `"says":{...}` object, so the index needs no corpus to know them.
    """
    decoder = json.JSONDecoder()
    found: set[str] = set()
    for _url, html in pages:
        for hit in _SAYS.finditer(html):
            try:
                value, _end = decoder.raw_decode(html, hit.end())
            except ValueError:
                continue
            for sentence in value.values() if isinstance(value, dict) else ():
                if isinstance(sentence, str):
                    for form in (sentence, htmllib.unescape(sentence)):
                        form = _squash(form)
                        if len(form.split()) >= MIN_WORDS:
                            found.add(form)
    return found


def _without(sentences: set[str]):
    """Return a function that cuts every one of `sentences` out of a text."""
    if not sentences:
        return lambda text: text
    pattern = re.compile("|".join(re.escape(s) for s in sorted(sentences, key=len, reverse=True)))
    return lambda text: _squash(pattern.sub(" ", text)) if pattern.search(text) else text


def document(pages: list[tuple[str, str]]) -> dict:
    """The index record for `(url, html)` pairs: one page table and one record per heading.

    ⛔ A sentence a quiz offers as an option is cut out of the text, wherever the page's prose
    happens to say the same words: the serve gate refuses any file that holds one, and the
    index must pass it unchanged. A page's own text is still searched; only that sentence is not.
    """
    table: list[list[str]] = []
    records: list[list] = []
    cut = _without(quiz_sentences(pages))
    for url, html in sorted(pages):
        page = read(html)
        page["sections"] = [(h, a, cut(t)) for h, a, t in page["sections"]]
        if not page["title"]:
            continue
        number = len(table)
        table.append([url, page["title"], page["crumb"]])
        if not page["unit"]:
            records.append([number, "", "", ""])
            continue
        for heading, anchor, text in page["sections"]:
            records.append([number, heading, anchor, text])
    return {"version": VERSION, "pages": table, "records": records}


def _dedupe(records: list[list]) -> list[list]:
    """⭐ A text that an earlier record already carries is replaced by that record's number.

    The same sentence under several headings (a repeated note, a shared example) is then written
    once; the search part puts the text back, so the words indexed and shown are unchanged.
    """
    seen: dict[str, int] = {}
    out: list[list] = []
    for at, (page, heading, anchor, text) in enumerate(records):
        if len(text) > 24 and text in seen:
            text = seen[text]
        elif text:
            seen[text] = at
        out.append([page, heading, anchor, text])
    return out


def _script(body: str) -> str:
    body = body.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return body


def _dump(value) -> str:
    return _script(json.dumps(value, ensure_ascii=False, separators=(",", ":")))


def shard_name(number: int) -> str:
    """The file name of shard `number`, beside `search-index.js`."""
    stem, dot, suffix = INDEX_NAME.rpartition(".")
    return f"{stem}-{number}{dot}{suffix}"


def files(pages: list[tuple[str, str]]) -> dict[str, str]:
    """`filename -> content` for the search index and the library that reads it.

    ⭐ One file, `search-index.js`, while it fits `SHARD_BYTES`; otherwise a manifest of that name
    (the page table and the shard names) plus `search-index-0.js`, `-1.js` and so on, each under
    the cap, that the search part loads and joins in order.
    """
    doc = document(pages)
    out = {LIBRARY_NAME: part(LIBRARY_NAME)}
    # ⭐ A course that fits is written exactly as it always was: one file, every text in full.
    whole = GLOBAL + _dump(doc) + ";\n"
    if len(whole.encode("utf-8")) <= SHARD_BYTES:
        out[INDEX_NAME] = whole
        return out
    records = _dedupe(doc["records"])
    # Each record is written once, then packed in order; the manifest carries the page table.
    rows = [_dump(record) for record in records]
    chunks: list[list[str]] = [[]]
    size = 0
    for row in rows:
        width = len(row.encode("utf-8")) + 1
        if size + width > SHARD_BYTES - 1024 and chunks[-1]:
            chunks.append([])
            size = 0
        chunks[-1].append(row)
        size += width
    names = [shard_name(n) for n in range(len(chunks))]
    for name, chunk in zip(names, chunks):
        out[name] = f"{SHARD_GLOBAL}{_dump(name)}]=[" + ",".join(chunk) + "];\n"
    manifest = {"version": SHARDED_VERSION, "pages": doc["pages"], "shards": names}
    out[INDEX_NAME] = GLOBAL + _dump(manifest) + ";\n"
    return out
