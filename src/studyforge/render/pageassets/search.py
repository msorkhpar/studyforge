r"""The site's search index: what a reader can find, read back off the pages a build wrote.

**What it does.** Reads each rendered page, keeps its title, its trail and the prose under each
heading, and has the vendored ranking library, `minisearch.js`, build the index once, at build
time, under `node`. What it writes is that index serialised (`JSON.stringify`), which the search
part hands to `MiniSearch.loadJSON` the first time a reader opens the search: the browser loads an
index, it never builds one.

**How you use it.** `files(pages, build=...)` takes `(url, html)` pairs, `url` being the page's
address from the shared asset directory, and returns `filename -> content` for the files a build
writes beside `page.js`. `build(documents, options, library)` returns the serialised index or
raises `Unbuilt` with the reason; `execute.search_index_builder` is the one that runs `node`, and
⛔ this module starts no process itself (§8.3). `clean=` is applied to every text before it is
indexed.

**Depends on.** `html.parser` and `json`. Nothing here touches a corpus: the index is read from
the HTML, so it can only ever say what a page says.

Size exception: the reader, the record it makes and the two shapes that record is written in are
one contract with the search part, which reads them back; split, the record's shape would be
stated in two modules that must change together. Running `node` is the seam, and it is split out.

## ⛔ What is never indexed

Only lesson prose, page titles, headings and menu labels (the titles of the level, module and
unit pages) are indexed. A word in an inline `code` span of a sentence is prose and stays.

⭐ **A page is read, never its answers.** Everything inside an element that carries any
`data-practice*`, `data-mock*`, `data-form*`, `data-deck*` or `data-review*` attribute is
skipped: that is where a quiz's questions, its key and a mock exam's key live, and where a
practice's solution does. A practice section (`data-kind="practice"`) is skipped whole, and a
page that holds a mock exam is not indexed at all, title included: its prose is what the exam's
questions are written from. ⛔ A `<details>` whose summary says answer, key or solution is
skipped as well. Scripts, styles, templates and hidden elements are skipped, and so is
everything outside `<main>`.

⭐ **Code is not prose.** A `pre`, a `code` element that stands alone as a block, a code figure,
an example with its language tabs and everything in them, its run strip and its output, and
the code-example editors are all skipped.

## ⭐ One record per heading

A page is cut at each heading (`h1` to `h4`) into records of `(heading, anchor, text)`, so a
result can name the part of the page a word is in and open it at that heading. Only a page whose
identity says it is a unit is read in full; the contents pages and the root index are indexed
by their title and trail alone, because their body is a list of the units' titles.

A record stores only `title`, `trail`, `heading`, `anchor` and a `snippet` (the start of its
text, about 160 characters, cut on a word). Its `text` is indexed and not stored.

## ⭐ Files, and the path taken without `node`

`search-index.js` is a small manifest (the version, the page addresses and the index options)
that carries the serialised index itself while it fits `SHARD_BYTES`. A larger index is one JSON
string cut into pieces, `search-index-0.js`, `-1.js` and so on, each a string literal under the
cap, that the search part joins in order before one `loadJSON`.

⚠️ With no `node` on the build machine, or one that fails, the build writes the index as it
always did (version 1 or 2: the records themselves, built in the browser by `search-build.js`,
which is written only then) and prints one warning naming the reason. The build still succeeds.
"""

from __future__ import annotations

import html as htmllib
import json
import re
import sys
from collections.abc import Callable
from html.parser import HTMLParser

from studyforge.render.pageassets.source import text as part
from studyforge.render.pageassets.surface import SURFACE_HOOKS

#: The files written beside the page bundle.
INDEX_NAME = "search-index.js"
LIBRARY_NAME = "minisearch.js"

#: ⚠️ The part that builds the index in the page, written only when the build could not.
BUILD_NAME = "search-build.js"

#: The part files this module writes, for the census of what is on disk.
SEARCH_PARTS = (LIBRARY_NAME, BUILD_NAME)

#: What the script assigns, and the shape version a reader of it checks.
GLOBAL = "window.studyforge=window.studyforge||{};window.studyforge.searchIndex="
VERSION = 1

#: The shape version of a sharded index (a manifest, shards, repeated texts as record numbers).
SHARDED_VERSION = 2

#: ⭐ The shape version of a precompiled index: a manifest and the serialised index, whole or in
#: string pieces. The search part refuses any version it does not know.
PRECOMPILED_VERSION = 3

#: Where a piece of a precompiled index puts its string: `searchParts[<file name>]`.
PART_GLOBAL = (
    "window.studyforge=window.studyforge||{};"
    "window.studyforge.searchParts=window.studyforge.searchParts||{};"
    "window.studyforge.searchParts["
)

#: The ranking library's options. ⛔ The search part passes the same ones to `loadJSON`, read off
#: the manifest, so the two can never disagree.
FIELDS = ("title", "heading", "text")
STORE_FIELDS = ("title", "trail", "heading", "anchor", "snippet")

#: The most characters a stored snippet holds, its ellipsis included.
SNIPPET_CHARS = 160

#: ⭐ The most bytes one index file may hold. The serve gate refuses a text file over 4 MiB, so an
#: index that would pass this is split into shards of about this size and a small manifest
#: (`search-index.js`) that names them. A small course stays one file.
SHARD_BYTES = 3 * 1024 * 1024

#: Where a shard puts its records for the search part to merge: `searchShards[<file name>]`.
SHARD_GLOBAL = (
    "window.studyforge=window.studyforge||{};"
    "window.studyforge.searchShards=window.studyforge.searchShards||{};"
    "window.studyforge.searchShards["
)

#: Elements that never carry something a reader searches for.
SILENT_TAGS = frozenset({"script", "style", "template", "noscript", "svg", "head"})

#: Elements with no end tag, so they never open a level.
VOID_TAGS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track",
     "wbr"}
)

#: An attribute name that marks a region holding answers or exercises.
WITHHELD_PREFIXES = ("data-practice", "data-mock", "data-form", "data-deck", "data-review")

#: ⭐ An attribute name that marks code, an example or its output: never prose.
CODE_PREFIXES = ("data-example", "data-code-example", "data-code-part")

#: An attribute name that only a mock exam's markup carries: the page it is on is an exam page.
EXAM_PREFIXES = ("data-practice-mock", "data-mock")

#: Elements a `code` element is a block of its own in, rather than a word of a sentence.
CODE_BLOCK_PARENTS = frozenset(
    {"main", "section", "article", "div", "figure", "details", "body", "blockquote", "ol", "ul"}
)

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
        self.exam = False
        self._quizzes: list[int] = []

    # -- state -------------------------------------------------------------

    @property
    def indexing(self) -> bool:
        return self._main_depth is not None and self._silent == 0

    def _withheld(self, tag: str, attrs: dict[str, str | None]) -> bool:
        if tag in SILENT_TAGS or "hidden" in attrs:
            return True
        if any(name.startswith(WITHHELD_PREFIXES) for name in attrs):
            return True
        return self._code(tag, attrs) or attrs.get(SURFACE_HOOKS["kind"]) == "practice"

    def _code(self, tag: str, attrs: dict[str, str | None]) -> bool:
        """Code, an example or its output, never a word of a sentence."""
        if tag == "pre" or any(name.startswith(CODE_PREFIXES) for name in attrs):
            return True
        if tag == "figure" and "code" in (attrs.get("class") or "").split():
            return True
        parent = self._stack[-1][0] if self._stack else ""
        return tag == "code" and parent in CODE_BLOCK_PARENTS

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
            # ⭐ A quiz on a lesson page is drawn with the mock form's markup (it carries the
            # same `data-practice-mock` pass mark): only a region that is not a quiz marks an
            # exam page, and nothing inside a quiz does.
            if attrs.get("data-form-kind") == "quiz":
                self._quizzes.append(len(self._stack))
            if not self._quizzes and any(name.startswith(EXAM_PREFIXES) for name in attrs):
                self.exam = True
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
        if self._quizzes and self._quizzes[-1] == len(self._stack):
            self._quizzes.pop()
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
    """One page as `{title, crumb, unit, exam, sections}`.

    `sections` are `(heading, anchor, text)`.
    """
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
        "exam": reader.exam,
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


def _same(text: str) -> str:
    return text


def document(
    pages: list[tuple[str, str]], clean: Callable[[str], str] = _same
) -> dict:
    """The index record for `(url, html)` pairs: one page table and one record per heading.

    ⛔ A sentence a quiz offers as an option is cut out of the text, wherever the page's prose
    happens to say the same words: the serve gate refuses any file that holds one, and the
    index must pass it unchanged. A page's own text is still searched; only that sentence is not.
    ⛔ An exam page gives no record at all. `clean` is applied to every text that is kept.
    """
    table: list[list[str]] = []
    records: list[list] = []
    cut = _without(quiz_sentences(pages))
    for url, html in sorted(pages):
        page = read(html)
        if page["exam"]:
            continue
        page["sections"] = [(clean(h), a, clean(cut(t))) for h, a, t in page["sections"]]
        if not page["title"]:
            continue
        number = len(table)
        table.append([url, clean(page["title"]), clean(page["crumb"])])
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


def snippet(text: str) -> str:
    """The start of `text`, at most `SNIPPET_CHARS` characters, cut on a word."""
    if len(text) <= SNIPPET_CHARS:
        return text
    room = SNIPPET_CHARS - 1
    cut = text.rfind(" ", 0, room + 1)
    return text[: cut if cut > 0 else room].rstrip() + "…"


def documents(doc: dict) -> list[dict]:
    """One ranking-library document per record; its id is `"<page>.<record>"`."""
    out = []
    for at, (page, heading, anchor, text) in enumerate(doc["records"]):
        _url, title, trail = doc["pages"][page]
        out.append(
            {
                "id": f"{page}.{at}",
                "title": title,
                "trail": trail,
                "heading": heading,
                "anchor": anchor,
                "snippet": snippet(text),
                "text": text,
            }
        )
    return out


class Unbuilt(Exception):
    """No precompiled index could be built; the message is the reason, for the warning."""


#: Builds the serialised index of `(documents, options, library)`, or raises `Unbuilt`.
Build = Callable[[list, dict, str], str]


def precompile(doc: dict, build: Build | None) -> str:
    """The serialised index of `doc`, made by `build`; raises `Unbuilt`."""
    if build is None:
        raise Unbuilt("no index builder was given")
    options = {"fields": list(FIELDS), "storeFields": list(STORE_FIELDS)}
    return build(documents(doc), options, part(LIBRARY_NAME))


def pieces(json_text: str, limit: int) -> list[str]:
    """`json_text` cut in order into pieces whose string literals each fit `limit` bytes."""
    out: list[str] = []
    at = 0
    while at < len(json_text):
        width = max(1, min(len(json_text) - at, limit))
        while True:
            size = len(_dump(json_text[at : at + width]).encode("utf-8"))
            if size <= limit or width == 1:
                break
            width = max(1, min(width - 1, int(width * limit / size * 0.98)))
        out.append(json_text[at : at + width])
        at += width
    return out


def part_name(number: int) -> str:
    """The file name of piece `number` of a precompiled index (the same names shards had)."""
    return shard_name(number)


def _precompiled_files(doc: dict, json_text: str) -> dict[str, str]:
    manifest = {
        "version": PRECOMPILED_VERSION,
        "pages": [url for url, _title, _trail in doc["pages"]],
        "fields": list(FIELDS),
        "storeFields": list(STORE_FIELDS),
    }
    whole = GLOBAL + _dump({**manifest, "index": json_text}) + ";\n"
    if len(whole.encode("utf-8")) <= SHARD_BYTES:
        return {INDEX_NAME: whole}
    # Each piece file is the global, its name and the literal: the literal gets what is left.
    overhead = len(PART_GLOBAL) + len(_dump(part_name(10**6))) + 8
    cut = pieces(json_text, SHARD_BYTES - overhead)
    names = [part_name(n) for n in range(len(cut))]
    out = {
        name: f"{PART_GLOBAL}{_dump(name)}]={_dump(text)};\n"
        for name, text in zip(names, cut, strict=True)
    }
    out[INDEX_NAME] = GLOBAL + _dump({**manifest, "parts": names}) + ";\n"
    return out


def warn(reason: str) -> str:
    """The one line printed when the index is left to the browser to build."""
    return (
        "studyforge: warning: the search index is built in the browser, not precompiled: "
        + reason
    )


def files(
    pages: list[tuple[str, str]],
    *,
    build: Build | None = None,
    clean: Callable[[str], str] = _same,
) -> dict[str, str]:
    """`filename -> content` for the search index and the library that reads it.

    ⭐ Precompiled by `build` (see the module). ⚠️ Without one, or when it raises `Unbuilt`, the
    records as they always were, plus `search-build.js`, and one warning on standard error.
    """
    doc = document(pages, clean)
    out = {LIBRARY_NAME: part(LIBRARY_NAME)}
    try:
        json_text = precompile(doc, build)
    except Unbuilt as reason:
        print(warn(str(reason)), file=sys.stderr)
        out[BUILD_NAME] = part(BUILD_NAME)
        out.update(record_files(doc))
        return out
    out.update(_precompiled_files(doc, json_text))
    return out


def record_files(doc: dict) -> dict[str, str]:
    """The index as the records themselves (versions 1 and 2), for the browser to build.

    ⭐ One file, `search-index.js`, while it fits `SHARD_BYTES`; otherwise a manifest of that name
    (the page table and the shard names) plus `search-index-0.js`, `-1.js` and so on, each under
    the cap, that the search part loads and joins in order.
    """
    out: dict[str, str] = {}
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
