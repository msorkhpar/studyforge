"""A real site on disk for the browser to open, and the broken ones beside it.

**What it does.** Writes one subtree per `FND-04` fixture corpus exactly as a
build would — a page for every kind the three renderers emit, plus `page.css`
and `page.js` at `placement.shared.assets` — and returns `file://` URLs into it.
`damaged()` writes a second tree with one thing deliberately wrong.

**How you use it.** The `built_site` fixture in `conftest.py` builds one per
session; a test asks it for `site.url("depth2-unit-01")` or
`site.damaged("contrast").url(...)`. `cases()` names the unit pages and
`pages()` names every page of every kind.

**Depends on.** `studyforge.render` and the three fixture builders the committed
golden pages come from — `tests.studyforge.render.page.pages`,
`…render.container.containers` and `…render.index.indexes` — imported and never
re-spelled.

## ⛔ Why the damaged tree exists, and why it is not optional

⚠️ **Ruling 70's form, applied to a screenshot.** A harness that has only ever
seen a good page has never been shown to notice a bad one — and a visual check
that cannot fail is the most convincing check in the repository and the most
worthless. ⭐ So every acceptance clause here is run **twice**: once against the
real site, which must pass, and once against a tree broken in exactly the way
that clause exists to catch, which must fail. ⛔ A control that passes is a
failure of the harness, reported as one.

## ⛔ Why all three page kinds are written, and what it was blind to (`W98`)

⚠️ **`SF-34` rules six chrome regions and this harness could judge two.** It
wrote the two unit fixtures and nothing else, rendered with `links=None`, so no
page it opened carried a between-pages bar, a practice panel, a container's unit
listing or a root index tree. ⛔ **The class this harness exists to catch lives
in exactly those regions:** `--measure: 80ch` resolves against *the element's
own font*, so one correct declaration produced three different columns — and no
assertion over a stylesheet can see a resolved value.

⛔ **Each corpus gets its own subtree, and that is not tidiness.** Both fixtures
place their root index at `index.html`, so a single tree would have the second
corpus's index overwrite the first's — and the harness would judge one contents
tree twice while reporting two.

⛔ **The practice panel needs a unit neither fixture contains.** Both declare
exactly as many practices as they archived, which is what a finished unit looks
like, so `_outstanding()` derives a short unit from a finished one rather than a
third fixture being invented. ⚠️ The panel's whole subject is a unit that is
**not** finished; a region that is only emitted by a state no fixture is in is a
region no harness can reach.

⛔ **The between-units bar carries both shapes `navigation` can emit**, not only
the easy one: a live relative href for the index slot, and a **declared
absence** (`Link(href=None, key=…)`) either side of it, which falls back to that
unit's own row on the root index. ⚠️ The slots are not a reading order and are
not asserted as one — prev/next traversal over a generated site is
`tests/studyforge/render/page/sites.py`'s subject and `SF-15`'s clause. What is
under test here is the **region**.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path, PurePosixPath

from studyforge.contents import order
from studyforge.corpus.placement import relative_href
from studyforge.generate.navigation import trail
from studyforge.render import pageassets
from studyforge.render.page import Crumb, Link, Links, Placement, render
from tests.studyforge.render.container import containers
from tests.studyforge.render.index import indexes
from tests.studyforge.render.page.sites import FIXTURES as UNIT_CASE_OF
from tests.studyforge.render.pageassets import test_chrome

#: The damage each control applies, and the clause it is the control for.
#: ⛔ Keys are the argument to `damaged()`; `test_init` asserts every one of
#: them is used by some test, so a control cannot be added and forgotten.
DAMAGE = {
    "contrast": "--fg is set to --bg's value in both themes: text on its own ground",
    "keyboard": "every link and control is given tabindex=-1: nothing is reachable",
    "network": "the page gains an <img> pointing at a remote host",
    "noscript": "the prose is moved into a script that writes it on load",
    "blank": "the body is emptied: a page that renders nothing at all",
    "column": "one chrome region is given a max-width in ch: a column of its own",
}

#: ⚠️ Two of those break the **stylesheet** rather than the page bytes, and which
#: two is `STYLESHEET_DAMAGE` near the bottom of this module — it has to sit below
#: the two functions it names, and it is ONE declaration rather than a branch in
#: `build` and a tuple in `_damage_page`.

#: The region the `column` control gives a measure of its own. ⛔ The masthead,
#: because it is the one region **every** page kind emits — a control applied to
#: a region only some pages carry would report *"this harness cannot see the
#: failure"* for the pages that never had the region in the first place.
OWN_COLUMN_REGION = "header"

#: What the `column` control gives it. ⛔ In `ch`, which is the whole point: a
#: `px` bound would be a different defect that a stylesheet assertion could see.
OWN_COLUMN_MEASURE = "40ch"

#: The three kinds of page the framework emits, named once. ⛔ A test that wants
#: *the unit pages* asks for this value rather than matching on a name, because a
#: fixture's name is a corpus's text and the kind is this framework's.
UNIT = "unit"
CONTAINER = "container"
INDEX = "index"

#: The one chrome region whose links resolve **on the page they are on**, as a
#: CSS selector. ⛔ **Ruling 164's fork arriving in a selector**: an outline is
#: CONTENT of its own page, so every one of its hrefs is a fragment; every other
#: region here is CHROME pointing somewhere else, so none of theirs is.
#: ⚠️ Spelled once, and `test_site` asserts it is a member of `chrome_regions()`
#: — a renamed region is then a red check rather than a selector matching
#: nothing, which is the shape a narrowed assertion fails silently in.
OUTLINE_REGION = 'nav[aria-label="Outline"]'

#: The fixture corpora, in a stated order, each written into its own subtree.
#: ⛔ Read from the container fixtures rather than listed here: a third fixture
#: corpus declared there joins this harness by itself, which is the half of
#: `SF-34`'s founding defect that was about a list nobody re-measures.
CORPORA = containers.FIXTURES


@dataclass(frozen=True)
class Built:
    """One page this harness writes: what it is, where it lands, and its bytes.

    `page` and `assets` are relative to the tree root, so one `Built` describes
    the same page in the real tree and in every damaged one.
    """

    name: str
    kind: str
    page: PurePosixPath
    assets: PurePosixPath
    body: bytes


@dataclass(frozen=True)
class Site:
    """A built tree, and what is wrong with it if anything is."""

    root: Path
    damage: str | None = None

    def url(self, case: str) -> str:
        """The `file://` URL of one built page.

        ⛔ `file://` and not a served URL: R8's floor is a page opened by
        double-clicking it, and a harness that started a web server would be
        proving something about a configuration no reader has.
        """
        return "file://" + str(self.path(case))

    def path(self, case: str) -> Path:
        """Where one built page sits in this tree."""
        return self.root / str(_one(case).page)

    def assets(self, case: str) -> Path:
        """The shared asset directory the named page links to."""
        return self.root / str(_one(case).assets)

    def kind(self, case: str) -> str:
        """Which of the three renderers wrote the named page."""
        return _one(case).kind


def build(root: Path, damage: str | None = None) -> Site:
    """Write every fixture page and the shared assets under `root`, damaged or not."""
    if damage is not None and damage not in DAMAGE:
        raise ValueError(f"no such damage {damage!r}; declared: {sorted(DAMAGE)}")
    written: dict[str, str] = dict(pageassets.written_files())
    if damage in STYLESHEET_DAMAGE:
        written[pageassets.STYLESHEET_NAME] = STYLESHEET_DAMAGE[damage](
            written[pageassets.STYLESHEET_NAME]
        )
    for built in pages_built():
        page = root / str(built.page)
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_bytes(_damage_page(built.body, damage))
    # ⛔ One enumeration, sorted: several page kinds share one asset directory,
    # and a set walked in iteration order would write the same files in an order
    # that differs between runs (R10).
    for directory in sorted({str(built.assets) for built in pages_built()}):
        assets = root / directory
        assets.mkdir(parents=True, exist_ok=True)
        for name, body in written.items():
            (assets / name).write_text(body, encoding="utf-8")
    return Site(root=root, damage=damage)


def pages() -> tuple[str, ...]:
    """Every page this harness opens, of every kind, in a stated order."""
    return tuple(built.name for built in pages_built())


def cases() -> tuple[str, ...]:
    """The unit pages alone, as the page fixtures spell them.

    ⚠️ Kept apart from `pages()` because three clauses are about a *unit's own
    prose* — the sentence taken from the material, the stylesheet and script a
    unit page links, the outline it carries — and a container page or a root
    index answers a different question rather than the same one badly.
    """
    return tuple(built.name for built in pages_built() if built.kind == UNIT)


def chrome_regions() -> tuple[str, ...]:
    """Every region `SF-34`'s disposition table says `chrome.css` answers for.

    ⛔ **DERIVED from that table, never listed again here.** `SF-34`'s founding
    defect is a scope line that read as complete while the tree had grown two
    regions past it, and a second list one directory away would be the same
    defect wearing this package's name. ⭐ A region added there — `SF-30`'s
    read-mark control already was — joins this harness's census the day it lands,
    and a region this tree cannot reach is then a red check rather than a silence.
    """
    return tuple(
        sorted(
            anchor
            for anchor, (answers_for, _) in test_chrome.REGIONS.items()
            if answers_for == test_chrome.CHROME_RULED
        )
    )


def kinds() -> tuple[str, ...]:
    """The page kinds this harness actually wrote, sorted, for a check that counts them."""
    return tuple(sorted({built.kind for built in pages_built()}))


@cache
def pages_built() -> tuple[Built, ...]:
    """Every page of every kind, per corpus, units then containers then the index.

    ⭐ Cached because the renderers are pure (R10) and this is called once per
    tree — one real tree and one per declared damage, six times a session.
    """
    out: list[Built] = []
    for corpus in CORPORA:
        out.append(_unit_page(corpus))
        out.extend(_container_pages(corpus))
        out.append(_index_page(corpus))
    return tuple(out)


def _one(case: str) -> Built:
    """The one built page called `case`."""
    for built in pages_built():
        if built.name == case:
            return built
    raise KeyError(f"no fixture page {case!r}; have {pages()}")


def _unit_page(corpus: str) -> Built:
    """One corpus's unit page, with a populated bar and an unfinished unit's panel."""
    case = UNIT_CASE_OF[corpus]()
    where = case.placement
    return Built(
        name=case.name,
        kind=UNIT,
        page=_under(corpus, where.unit.page),
        assets=_under(corpus, where.shared.assets),
        body=render(
            _outstanding(case.document), where, _bar(corpus, where), _trail(corpus, case.document)
        ),
    )


def _container_pages(corpus: str) -> tuple[Built, ...]:
    """Every container page one corpus declares, as its own fixture builder renders it."""
    return tuple(
        Built(
            name=case.name,
            kind=CONTAINER,
            page=_under(corpus, case.placement.container.page),
            assets=_under(corpus, case.placement.shared.assets),
            body=case.render(),
        )
        for case in containers.fixture_cases(corpus)
    )


def _index_page(corpus: str) -> Built:
    """One corpus's root index, as its own fixture builder renders it."""
    case = indexes.case(corpus)
    return Built(
        name=f"{case.name}-{INDEX}",
        kind=INDEX,
        page=_under(corpus, case.placement.shared.root_index),
        assets=_under(corpus, case.placement.shared.assets),
        body=case.render(),
    )


def _under(corpus: str, path: PurePosixPath) -> PurePosixPath:
    """Where one corpus's page sits inside this harness's tree."""
    return PurePosixPath(corpus) / path


def _outstanding(document: dict) -> dict:
    """The same unit, with one more practice declared than it archived.

    ⛔ **Derived from the document rather than typed**: the panel renders when
    `declared > archived`, and a count written here would be a number that is
    right for today's two fixtures and silently wrong for a third.
    """
    practices = dict(document.get("practices") or {})
    practices["declared"] = (practices.get("archived") or 0) + 1
    return {**document, "practices": practices}


def _bar(corpus: str, where: Placement) -> Links:
    """The between-units bar for one unit page, pointing at files in this tree.

    ⛔ Every href is asked of `relative_href`, never composed: the `tree` and
    `sibling` profiles put a unit page at different depths, and a `../` counted
    here would be right for one corpus and dangle in the other (`W57`).

    ⭐ **Both neighbours are declared absences** — `Link(href=None, key=…)` —
    which is the shape `navigation._destination` falls back from, so the bar
    emits a direct href and two fallbacks rather than three of one kind.
    ⚠️ They are the corpus's first and last declared units, which is not a
    reading order and is not asserted as one; see this module's docstring.
    """
    contents = indexes.case(corpus).contents
    walked = order(contents)
    return Links(
        previous=Link(None, walked[0].title, key=walked[0].key),
        index=Link(
            href=relative_href(where.unit.page, where.shared.root_index),
            label=contents.title,
        ),
        next=Link(None, walked[-1].title, key=walked[-1].key),
    )


def _trail(corpus: str, document: dict) -> tuple[Crumb, ...]:
    """The trail for one unit page, joined the way a build joins it.

    ⛔ **`W105`.** The disposition table rules `nav[aria-label="Breadcrumb"]`, and
    a harness that passes no trail can never open it — the reach check above
    reds by name. ⭐ `generate.navigation.trail` is called rather than imitated,
    and the index href is asked of `relative_href`, as `_bar`'s is.

    ⚠️ The unit is found by its address and its title, and anything but exactly
    one match is refused: a trail for the wrong unit would still paint.
    """
    contents = indexes.case(corpus).contents
    within = "/".join(document["address"]) + "/"
    keys = [
        entry.key
        for entry in order(contents)
        if entry.key.startswith(within) and entry.title == document["title"]
    ]
    if len(keys) != 1:
        raise LookupError(f"{corpus}: {len(keys)} units match this page, and one must")
    where = UNIT_CASE_OF[corpus]().placement
    return trail(contents, keys[0], relative_href(where.unit.page, where.shared.root_index))


def _flatten_foreground(stylesheet: str) -> str:
    """Make `--fg` equal `--bg` in both themes, so every ratio collapses to 1:1.

    ⚠️ Both themes, and by substitution on the *declared* values rather than by
    appending an override: an override at the end of the file would be a rule a
    later `:root` block could beat, and a control that the code under test can
    win is not a control.
    """
    out: list[str] = []
    ground = None
    for line in stylesheet.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("--bg:"):
            ground = stripped.split(":", 1)[1].strip().rstrip(";")
        if stripped.startswith("--fg:") and ground is not None:
            out.append(line.split("--fg:")[0] + f"--fg: {ground};\n")
            continue
        out.append(line)
    return "".join(out)


def _own_column(stylesheet: str) -> str:
    """Give one chrome region a column of its own, measured in `ch`.

    ⭐ **`SF-34`'s defect reproduced rather than imagined.** Every declaration in
    the real stylesheet is identical and correct, and the resolved columns still
    came out 800 px, 715.7 px and 680.3 px — because `ch` resolves against THE
    ELEMENT'S OWN FONT and the chrome's font is not the reading surface's.
    ⛔ So this appends a rule and changes nothing else: no class, no colour, no
    markup, nothing any assertion over declarations or goldens can see.

    ⚠️ Appended rather than substituted, which is the opposite of
    `_flatten_foreground`'s argument and right for the opposite reason: there is
    no existing declaration on this region to substitute for, and an attribute-
    free element selector at the end of the bundle is a rule nothing later beats.
    """
    return f"{stylesheet}\n{OWN_COLUMN_REGION} {{ max-width: {OWN_COLUMN_MEASURE}; }}\n"


#: Which damages break the **stylesheet** rather than the page bytes, and what
#: each does to it. ⛔ **One declaration, and it sits here because it names the two
#: functions above.** Its two readers are `build`, which applies it, and
#: `_damage_page`, which passes those trees' bytes through untouched — and a damage
#: added to one of those and not the other produces a tree that is not damaged at
#: all, which is a control that passes.
STYLESHEET_DAMAGE = {"column": _own_column, "contrast": _flatten_foreground}


def _damage_page(page: bytes, damage: str | None) -> bytes:
    """Return the page bytes with the named damage applied, or unchanged."""
    if damage is None or damage in STYLESHEET_DAMAGE:
        return page
    text = page.decode("utf-8")
    if damage == "keyboard":
        for element in ("<a ", "<button ", "<summary", "<details"):
            text = text.replace(element, f'{element.rstrip()} tabindex="-1" ')
        return text.encode("utf-8")
    if damage == "network":
        return text.replace(
            "</body>", '<img src="https://example.invalid/tracker.png" alt=""></body>'
        ).encode("utf-8")
    if damage == "noscript":
        body = text.split("<main", 1)[1].split("</main>", 1)[0]
        payload = body.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        return (
            text.split("<main", 1)[0]
            + "<main id=content></main><script>document.querySelector('main')"
            + f".innerHTML = `<div{payload}</div>`;</script>"
            + text.split("</main>", 1)[1]
        ).encode("utf-8")
    if damage == "blank":
        head = text.split("<body>", 1)[0]
        return (head + "<body></body></html>\n").encode("utf-8")
    raise ValueError(f"unhandled damage {damage!r}")  # pragma: no cover - guarded above
