"""`W324` in a real browser: the crossing from one container to another, followed.

⛔ **A built site, not a hand-assembled tree.** `tests/visual/site.py` writes one
unit page per fixture corpus, which is enough to judge a REGION and not enough to
judge a CROSSING: the page a rail row points at has to be on disk before
*"resolves, and lands on the right page"* can mean anything. ⭐ So this module
asks `studyforge.generate.write_site` for the whole corpus and opens what it
wrote.

⛔ **Every path is asked of the build, never spelled here.** `unit_location` is
what owns the geography of a unit page; a literal `…/01-getting-started/…` in
this file would be a second answer to where a page goes, and it would go stale
the day placement moves one.

⚠️ **Run twice, as everything in this package is.** The control strips the rail
region out of the same tree: a harness that has only ever seen a page with a rail
has not been shown to notice one without.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest

from studyforge.contents import order
from studyforge.generate import read_corpus, unit_location, write_site
from studyforge.render.pageassets import text as stylesheet
from tests.support import repository_root
from tests.visual.page import NARROW, WIDE, OpenPage

#: The fixture corpus with more than one container. ⛔ `depth1` declares one, so
#: it has no crossing at all — which is clause 4 and is asserted in
#: `tests/studyforge/generate/test_navigation.py`, on the artifact.
CORPUS = "depth2"

#: The region under test, as `chrome.css` and the disposition table spell it.
RAIL = 'nav[aria-label="Containers"]'

#: What the rail is measured against. ⛔ The same element `test_site.py` calls
#: the reading surface, spelled the same way, because *"beside the reading
#: column"* is a claim about that element and no other.
READING_SURFACE = "main#content"

#: The whole region, for the control that removes it.
RAIL_REGION = re.compile(r'<nav aria-label="Containers">.*?</nav>\n?', re.DOTALL)

#: The stylesheet the two shapes live in, and the pattern that finds the one
#: threshold between them. ⛔ **Read back, never retyped.** A breakpoint moved in
#: `chrome.css` and not here would leave `WIDE` and `NARROW` on the same side of
#: it, and every geometry check below would pass while judging one layout twice.
LAYOUT_PART = "chrome.css"
THRESHOLD = re.compile(r"@media\s*\(min-width:\s*([0-9.]+)rem\)")

#: Pixels per `rem` **in a media query**. ⛔ Not `html`'s font size: a media
#: query resolves `rem` against the document's INITIAL font size, so this is the
#: browser default and is not a figure `reading.css` can move.
ROOT_FONT = 16

#: How far two edges may differ and still be touching, in CSS pixels — the same
#: subpixel allowance `test_site.SAME_COLUMN` makes, and for the same reason.
TOUCHING = 0.5


@dataclass(frozen=True)
class BuiltCorpus:
    """One corpus built onto disk, and the two questions this module asks it."""

    root: Path
    pages: dict[str, Path]
    titles: dict[str, str]

    def url(self, key: str) -> str:
        """The `file://` URL of one declared unit's page.

        ⛔ `file://` and not a served URL: R8's floor is a page opened by
        double-clicking it (`tests/visual/site.py` makes the same argument).
        """
        return "file://" + str(self.pages[key])


def _build(root: Path, *, without_rail: bool = False) -> BuiltCorpus:
    """Write the whole fixture corpus under `root`, optionally with its rail cut out."""
    source = repository_root() / "tests" / "fixtures" / CORPUS
    root.mkdir(parents=True, exist_ok=True)
    write_site(source, root)
    corpus = read_corpus(source)
    pages = {unit.key: root / str(unit_location(corpus, unit).page) for unit in corpus.units}
    if without_rail:
        for page in sorted(root.rglob("*.html")):
            page.write_text(RAIL_REGION.sub("", page.read_text(encoding="utf-8")), encoding="utf-8")
    return BuiltCorpus(
        root=root,
        pages=pages,
        titles={entry.key: entry.title for entry in order(corpus.contents)},
    )


@pytest.fixture(scope="session")
def built_corpus(tmp_path_factory: pytest.TempPathFactory) -> BuiltCorpus:
    """The fixture corpus, built once for the session the way a build builds it."""
    return _build(tmp_path_factory.mktemp("visual-rail"))


@pytest.fixture(scope="session")
def railless_corpus(tmp_path_factory: pytest.TempPathFactory) -> BuiltCorpus:
    """The same corpus with the rail region removed — the control for every check."""
    return _build(tmp_path_factory.mktemp("visual-rail-control"), without_rail=True)


@pytest.fixture
def here(built_corpus: BuiltCorpus) -> Iterator[str]:
    """The unit key of the first declared unit — the page every check starts on."""
    yield next(iter(built_corpus.pages))


def crossings(page: OpenPage, from_url: str) -> list[dict]:
    """Every rail link that leaves the container the open page is in.

    ⭐ **`a.href` and not `getAttribute('href')`**: the browser resolves it
    against the document, which is the half of *"resolves"* a string comparison
    cannot see. ⚠️ The container is told apart by the directory the page sits
    in, which is what a crossing has to change under either placement profile.
    """
    where = from_url.rsplit("/", 1)[0]
    return [
        found
        for found in page.evaluate(
            # ⭐ The link's own words, without the read words a screen reader
            # is given on a marked row (`W383`): those are not what it names.
            "(shown => "
            f"Array.from(document.querySelectorAll('{RAIL} a'))"
            ".map(a => ({href: a.href, text: shown(a),"
            " closed: !!a.closest('details:not([open])')})))"
            "(a => { const c = a.cloneNode(true);"
            " c.querySelectorAll('span[data-kind=\"read-state\"]').forEach(w => w.remove());"
            " return c.textContent.trim(); })"
        )  # type: ignore[arg-type]
        if str(found["href"]).endswith(".unit.html")
        and not str(found["href"]).startswith(where + "/")
    ]


def breakpoint_px() -> float:
    """The one width `chrome.css` changes shape at, in CSS pixels.

    ⛔ Refuses anything but exactly one threshold: two of them and *"wide"* and
    *"narrow"* stop naming two layouts, which is a harness measuring one of them
    twice and reporting two. The unit mirror asserts the same count, from the
    other side — `tests/studyforge/render/pageassets/test_chrome.py`.
    """
    found = THRESHOLD.findall(stylesheet(LAYOUT_PART))
    assert len(found) == 1, f"{LAYOUT_PART} declares {len(found)} width thresholds, not one"
    return float(found[0]) * ROOT_FONT


def box(page: OpenPage, selector: str) -> dict:
    """The laid-out rectangle of the one element `selector` names.

    ⛔ Read off the live layout and never off a declaration: which side of the
    reading column a region ends up on is exactly the thing no assertion over a
    stylesheet can see, which is `W98`'s whole argument one region along.
    """
    found = page.evaluate(
        "(() => { const el = document.querySelector('" + selector + "');"
        " if (!el) return null; const r = el.getBoundingClientRect();"
        " return {left: r.left, right: r.right, top: r.top,"
        "  bottom: r.bottom, width: r.width}; })()"
    )
    assert found is not None, f"the open page carries no {selector}"
    return dict(found)  # type: ignore[arg-type]


def test_the_two_widths_this_module_judges_at_straddle_the_stylesheets_threshold() -> None:
    """⛔ Runs with no browser, and it is what makes the two widths mean anything.

    ⚠️ `WIDE` and `NARROW` are stated in `page.py` — deliberately, so the harness
    reads no stylesheet to decide what to open at. ⭐ This is the join: the
    stated pair is asserted against the file's own threshold, so moving the
    breakpoint reds HERE rather than silently collapsing both readings onto one
    layout.
    """
    at = breakpoint_px()
    assert NARROW[0] < at, f"the narrow viewport {NARROW[0]}px is not below the threshold {at}px"
    assert at <= WIDE[0], f"the wide viewport {WIDE[0]}px is not at or above the threshold {at}px"


def test_the_rail_is_beside_the_reading_column_at_the_wide_width(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⛔ `W325`'s first clause: a bar down the LEFT, and the user's own words.

    ⭐ **Opened with scripts DISABLED**, because R8's floor makes the layout's
    scriptlessness part of the clause and not a separate one: a rail that is only
    a rail once something has run is not one for a page opened from a file.

    ⚠️ *"Down the left"* is asserted as three facts and not one, because each
    alone has a passing shape that is not a rail: the rail ends before the column
    begins (a full-width card above it does not), it starts level with the
    masthead rather than below the prose, and the column is genuinely indented
    past it rather than the rail hanging off the page.
    """
    open_page.resize(*WIDE)
    open_page.open(built_corpus.url(here), scripts=False)
    rail = box(open_page, RAIL)
    column = box(open_page, READING_SURFACE)
    masthead = box(open_page, "body > header")

    assert rail["right"] <= column["left"] + TOUCHING, (
        f"the rail spans {rail['left']:.2f}–{rail['right']:.2f}px and the reading column "
        f"starts at {column['left']:.2f}px, so it is not to the left of it"
    )
    assert rail["top"] <= masthead["top"] + TOUCHING, (
        f"the rail starts at {rail['top']:.2f}px and the masthead at "
        f"{masthead['top']:.2f}px, so it hangs below the page's own top rather than "
        "running down its left"
    )
    assert column["left"] >= rail["width"] > 0, (
        f"the reading column starts at {column['left']:.2f}px and the rail is "
        f"{rail['width']:.2f}px wide, so the column is not indented past it"
    )


def test_the_rail_folds_back_into_the_column_at_the_narrow_width(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⛔ `W325`'s second clause, and the chosen degradation is NAMED.

    ⭐ **The narrow shape is the card `W324` shipped** — the region in the one
    column, above the reading surface, at the column's own width. ⚠️ A rail
    squeezed against prose is the failure this forbids, and it is refused by the
    width equality rather than by anybody's judgement of a screenshot.

    ⛔ **This check and the one above are each other's control.** A stylesheet
    that always stacked fails that one; a stylesheet that always railed fails
    this one; no single layout passes both.
    """
    open_page.resize(*NARROW)
    open_page.open(built_corpus.url(here), scripts=False)
    rail = box(open_page, RAIL)
    column = box(open_page, READING_SURFACE)

    assert rail["bottom"] <= column["top"] + TOUCHING, (
        f"at {NARROW[0]}px the rail ends at {rail['bottom']:.2f}px and the reading column "
        f"starts at {column['top']:.2f}px, so it is still beside the prose rather than above it"
    )
    assert abs(rail["width"] - column["width"]) <= TOUCHING, (
        f"at {NARROW[0]}px the rail is {rail['width']:.2f}px against the column's "
        f"{column['width']:.2f}px, so it has a measure of its own"
    )


def test_the_crossing_still_resolves_at_the_narrow_width(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⭐ `W324`'s clause re-taken in the shape `W325` added, rather than assumed.

    ⚠️ The two layouts are one set of bytes, so this cannot fail while the wide
    one passes — which is the claim, and a claim asserted is worth more than a
    claim argued.
    """
    open_page.resize(*NARROW)
    url = built_corpus.url(here)
    open_page.open(url)
    crossing = crossings(open_page, url)[0]

    open_page.open(str(crossing["href"]))
    landed = open_page.evaluate("document.querySelector('h1').textContent.trim()")

    assert str(crossing["text"]).endswith(str(landed)), (crossing["text"], landed)


def test_the_reading_surface_stays_inside_the_ceiling_the_palette_declares(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⛔ `--page-max` is painted for this layout, and this is what it buys.

    ⭐ What this asserts is the property the token gives: at a viewport far wider
    than any reader has, the surface a table and a code block fill is bounded
    rather than full-bleed, and bounded no wider than the ceiling the palette
    names.

    ⚠️ **The subject is the SURFACE and not the page, since `W388` stage 3.** The
    bound sat on `body`, and a bounded, left-aligned page is the row's own
    defect — the user read it on a 2000px window as *"the paragraph texts are
    not using the full width"*. ⛔ So the page spans the window here and the
    ceiling is asserted where it now lives.
    """
    open_page.resize(4 * WIDE[0], WIDE[1])
    open_page.open(built_corpus.url(here), scripts=False)
    ceiling = open_page.evaluate(
        "(() => { const probe = document.createElement('div');"
        " probe.style.cssText = 'width: var(--page-max); position: absolute; visibility: hidden';"
        " document.body.appendChild(probe);"
        " const width = probe.getBoundingClientRect().width;"
        " probe.remove(); return width; })()"
    )
    page = box(open_page, "body")
    surface = box(open_page, "main#content")

    assert float(ceiling) > 0, "the palette declares no --page-max, so nothing is ceiled"
    assert float(ceiling) < 4 * WIDE[0], (
        f"the ceiling of {float(ceiling):.2f}px is wider than the {4 * WIDE[0]}px window "
        "this reading is taken in, so it says nothing"
    )
    assert surface["width"] <= float(ceiling) + TOUCHING, (
        f"the reading surface is {surface['width']:.2f}px against a declared ceiling of "
        f"{float(ceiling):.2f}px, so nothing bounds it at all"
    )
    assert page["width"] >= 4 * WIDE[0] - TOUCHING, (
        f"at {4 * WIDE[0]}px the page is {page['width']:.2f}px wide, so it stops short of "
        "the window and leaves the dead strip this row exists to remove"
    )


def test_a_unit_page_offers_a_link_to_a_unit_in_another_container(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⛔ **The row's founding measurement, inverted in a browser.**

    Measured before this region: a unit page carried three `<nav>` elements and
    not one href in any of them reached a page in another container.
    """
    url = built_corpus.url(here)
    open_page.open(url)
    found = crossings(open_page, url)
    assert found, "the open unit page offers no link out of its own container"


def test_following_that_link_lands_on_the_unit_the_row_named(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⭐ Present, resolves, and lands on the right page — the three, in order."""
    url = built_corpus.url(here)
    open_page.open(url)
    crossing = crossings(open_page, url)[0]

    open_page.open(str(crossing["href"]))
    landed = open_page.evaluate("document.querySelector('h1').textContent.trim()")

    assert landed, "following the crossing landed on a page with no heading at all"
    assert str(crossing["text"]).endswith(str(landed)), (crossing["text"], landed)
    assert str(landed) in built_corpus.titles.values(), landed


def test_the_crossing_still_works_with_scripts_disabled(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⛔ R8's floor: a rail that needed a script to render its links is not navigation."""
    url = built_corpus.url(here)
    open_page.open(url, scripts=False)
    crossing = crossings(open_page, url)[0]

    open_page.open(str(crossing["href"]), scripts=False)
    landed = open_page.evaluate("document.querySelector('h1').textContent.trim()")

    assert str(crossing["text"]).endswith(str(landed)), (crossing["text"], landed)


def test_the_region_says_which_container_and_which_unit_the_reader_is_on(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⭐ Clause 2, read off the live DOM rather than off the bytes.

    ⚠️ `aria-current` is the statement; the weight and the colour `chrome.css`
    adds are the reinforcement, and this asserts the statement.
    """
    open_page.open(built_corpus.url(here))
    marked = open_page.evaluate(
        f"Array.from(document.querySelectorAll('{RAIL} [aria-current]'))"
        ".map(el => el.getAttribute('aria-current'))"
    )

    assert sorted(marked) == ["page", "true"], marked
    inside = open_page.evaluate(
        f"document.querySelector('{RAIL} [aria-current=\\\"page\\\"]')"
        f".closest('li[aria-current=\\\"true\\\"]') !== null"
    )
    assert inside, "the current unit is not inside the container marked current"


def test_the_readers_own_container_is_open_and_another_is_not(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⛔ Both states, because a rail that opened everything proves nothing about either.

    ⚠️ The closed ones still carry their links — `crossings` reports whether the
    one it followed was inside a closed disclosure — so the crossing above is
    reachable whichever way the reader opens it.
    """
    open_page.open(built_corpus.url(here))
    states = open_page.evaluate(
        # ⚠️ `li details`: since `W362` the whole rail sits inside one fold
        # (`rail.html`), which is not a container and is open at this width.
        f"Array.from(document.querySelectorAll('{RAIL} li details')).map(d => d.open)"
    )

    assert list(states).count(True) == 1, states
    assert list(states).count(False) >= 1, states


def test_a_closed_disclosure_is_reachable_with_the_keyboard(
    open_page: OpenPage, built_corpus: BuiltCorpus, here: str
) -> None:
    """⚠️ Clause 6: a `<summary>` a keyboard reader cannot reach hides its links.

    ⭐ `<details>` takes focus and opens on Enter with scripting off entirely —
    which is the whole reason this region is built out of it (R8).
    """
    open_page.open(built_corpus.url(here), scripts=False)
    summaries = open_page.evaluate(
        f"Array.from(document.querySelectorAll('{RAIL} details:not([open]) > summary'))"
        ".map(s => s.tabIndex)"
    )

    assert summaries, "no closed disclosure on the page, so this check would prove nothing"
    assert all(int(index) >= 0 for index in summaries), summaries


def test_the_checks_above_fail_on_a_tree_whose_rail_was_removed(
    open_page: OpenPage, railless_corpus: BuiltCorpus
) -> None:
    """⛔ Negative control: a harness that cannot see the region's absence sees nothing.

    ⚠️ It is the same corpus, built the same way, with exactly the rail cut out —
    so every other check in this package still passes on it.
    """
    key = next(iter(railless_corpus.pages))
    url = railless_corpus.url(key)
    open_page.resize(*WIDE)
    open_page.open(url)

    assert open_page.evaluate(f"document.querySelectorAll('{RAIL}').length") == 0
    assert crossings(open_page, url) == []
    # ⛔ `W325`'s half of the same control: the two-column page is asked for by
    # the page that CARRIES the region (`:has()`), so a tree with no rail must
    # still be laid out in one column — otherwise every page without one, the
    # root index first, gets an empty rail track down its left.
    assert open_page.evaluate("getComputedStyle(document.body).display") != "grid", (
        "a page with no rail is still laid out as a two-column grid, so the empty "
        "track is a hole down the left of every page that carries no region"
    )
