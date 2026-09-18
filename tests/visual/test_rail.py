"""`W324` in a real browser: the crossing from one container to another, followed.

⛔ **A built site, not a hand-assembled tree.** `tests/visual/site.py` writes one
unit page per fixture corpus, which is enough to judge a REGION and not enough to
judge a CROSSING: the page a rail row points at has to be on disk before
*"resolves, and lands on the right page"* can mean anything. ⭐ So this module
asks `studyforge.generate.write_site` for the whole corpus and opens what it
wrote.

⛔ **Every path is asked of the build, never spelled here.** `unit_location` and
`page_paths` are what own the geography; a literal `…/01-getting-started/…` in
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

from studyforge.address import parse_unit_key
from studyforge.contents import order
from studyforge.generate import page_paths, read_corpus, unit_location, write_site
from tests.support import repository_root
from tests.visual.page import OpenPage

#: The fixture corpus with more than one container. ⛔ `depth1` declares one, so
#: it has no crossing at all — which is clause 4 and is asserted in
#: `tests/studyforge/generate/test_navigation.py`, on the artifact.
CORPUS = "depth2"

#: The region under test, as `chrome.css` and the disposition table spell it.
RAIL = 'nav[aria-label="Containers"]'

#: The whole region, for the control that removes it.
RAIL_REGION = re.compile(r'<nav aria-label="Containers">.*?</nav>\n?', re.DOTALL)


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
    pages = {
        unit.key: root / str(unit_location(corpus, unit).page)
        for unit in corpus.units
    }
    if without_rail:
        for page in sorted(root.rglob("*.html")):
            page.write_text(
                RAIL_REGION.sub("", page.read_text(encoding="utf-8")), encoding="utf-8"
            )
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
            f"Array.from(document.querySelectorAll('{RAIL} a'))"
            ".map(a => ({href: a.href, text: a.textContent.trim(),"
            " closed: !!a.closest('details:not([open])')}))"
        )  # type: ignore[arg-type]
        if str(found["href"]).endswith(".unit.html") and not str(found["href"]).startswith(
            where + "/"
        )
    ]


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
        f"Array.from(document.querySelectorAll('{RAIL} details')).map(d => d.open)"
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
    open_page.open(url)

    assert open_page.evaluate(f"document.querySelectorAll('{RAIL}').length") == 0
    assert crossings(open_page, url) == []
