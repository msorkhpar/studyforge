"""The rail shows which units the reader marked read, in a real browser.

⛔ **A built site, opened over `file://`, and the mark made by pressing the
page's own control** — never by writing the store's record here, which would
be a second spelling of the store's format and would pass against a rail that
reads a different one.

⭐ **Asserted both ways (R12).** A fresh store marks no rail row; a marked unit
is marked in the rail on a page in ANOTHER container and on its own page; an
unmark clears it. ⚠️ And the control: the same tree with the rail's keys cut
out shows no mark at all while the store still holds one — so what lights a
row is the key, and a harness that has only seen marked rows has been shown to
notice an unmarked one.

⭐ **And the words a screen reader is told**: absent on a fresh store,
present on exactly the marked unit's rows in the rail and both lists, taking no
room on the screen, following the control both ways, and never matched by the
index filter.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest

from studyforge.generate import page_paths, read_corpus, unit_location, write_site
from tests.support import repository_root
from tests.visual.page import OpenPage

#: The fixture corpus with more than one container, so a rail is emitted.
CORPUS = "depth2"

#: The region under test and its unit rows: a nested row that holds no
#: disclosure, since a container row and a group row each hold one.
RAIL = 'nav[aria-label="Containers"]'
ROWS = RAIL + " li li:not(:has(> details))"

#: What `chrome.css` draws on a marked rail row (`\2713`), as the computed
#: `content` of the pseudo-element reads back.
TICK = '"✓"'

#: The rail's key attribute, cut out of every page for the control tree.
KEY_ATTRIBUTE = re.compile(r' data-unit="[^"]*"(?=[^<]*data-readable)')

#: Every rail row: its key, whether the script marked it, and what its tick
#: pseudo-element draws. ⭐ The tick is read off the element that carries it —
#: the anchor, or the row itself when the row carries none (the current unit).
READING = (
    "Array.from(document.querySelectorAll('" + ROWS + "')).map(row => {"
    " const host = row.querySelector(':scope > a') || row;"
    " return {key: row.getAttribute('data-unit'),"
    "  marked: row.getAttribute('data-marked') === 'true',"
    "  tick: getComputedStyle(host, '::after').content}; })"
)

#: The page's own read-mark control, pressed; resolves after the turn in which
#: `progress-view.js` repaints the rail from the store's answer.
PRESS = (
    "new Promise(done => {"
    " document.querySelector('section[data-section=\"read-mark\"] button').click();"
    " setTimeout(() => requestAnimationFrame(() => done(true)), 0); })"
)


#: The key the page's own read-mark control carries.
CONTROL_KEY = (
    "document.querySelector('section[data-section=\"read-mark\"]').getAttribute('data-unit')"
)


@dataclass(frozen=True)
class Built:
    """One corpus on disk: each unit's page, its container, and each container's page."""

    pages: dict[str, Path]
    containers: dict[str, str]
    container_pages: tuple[Path, ...]
    index: Path

    def url(self, key: str) -> str:
        """The `file://` URL of one unit's page (R8's floor is a double-click)."""
        return "file://" + str(self.pages[key])


def _build(root: Path, *, keyless: bool = False) -> Built:
    """Write the fixture corpus under `root`, optionally with the rail's keys cut out."""
    source = repository_root() / "tests" / "fixtures" / CORPUS
    root.mkdir(parents=True, exist_ok=True)
    write_site(source, root)
    corpus = read_corpus(source)
    if keyless:
        for page in sorted(root.rglob("*.html")):
            text = page.read_text(encoding="utf-8")
            page.write_text(KEY_ATTRIBUTE.sub("", text), encoding="utf-8")
    return Built(
        pages={unit.key: root / str(unit_location(corpus, unit).page) for unit in corpus.units},
        containers={unit.key: unit.container.address.key for unit in corpus.units},
        container_pages=tuple(root / str(page) for page in page_paths(corpus).values()),
        index=root / "index.html",
    )


@pytest.fixture(scope="session")
def built(tmp_path_factory: pytest.TempPathFactory) -> Built:
    """The fixture corpus, built the way a build builds it."""
    return _build(tmp_path_factory.mktemp("visual-rail-marks"))


@pytest.fixture(scope="session")
def keyless(tmp_path_factory: pytest.TempPathFactory) -> Built:
    """The same corpus with every rail row's key removed — the control."""
    return _build(tmp_path_factory.mktemp("visual-rail-marks-control"), keyless=True)


@pytest.fixture
def fresh(open_page: OpenPage, built: Built) -> Iterator[OpenPage]:
    """A tab whose store holds no mark, before the check and after it.

    ⚠️ Every `file://` page shares one storage origin and the browser outlives
    the test, so a mark left behind would be read by the next check.
    """
    open_page.open(built.url(next(iter(built.pages))))
    open_page.evaluate("localStorage.clear()")
    yield open_page
    open_page.evaluate("localStorage.clear()")


def rows(page: OpenPage) -> list[dict]:
    """Every rail row of the open page, read live."""
    return list(page.evaluate(READING))  # type: ignore[arg-type]


def two_containers(built: Built) -> tuple[str, str]:
    """The first unit, and the first unit that sits in a different container."""
    first = next(iter(built.pages))
    other = next(key for key in built.pages if built.containers[key] != built.containers[first])
    return first, other


def every_page(built: Built) -> list[str]:
    """The `file://` URL of every page that carries a rail: each unit's and each container's."""
    return [built.url(key) for key in built.pages] + [
        "file://" + str(page) for page in built.container_pages
    ]


def test_a_fresh_store_marks_no_rail_row_and_draws_no_tick(fresh: OpenPage, built: Built) -> None:
    for url in every_page(built):
        fresh.open(url)
        found = rows(fresh)
        assert found, f"{url} carries no rail rows to judge"
        assert all(row["key"] for row in found), f"a rail row on {url} carries no key"
        assert not [row for row in found if row["marked"] or row["tick"] == TICK]


def test_a_marked_unit_shows_marked_in_the_rail_on_a_page_in_another_container(
    fresh: OpenPage, built: Built
) -> None:
    marked, elsewhere = two_containers(built)
    fresh.open(built.url(marked))
    fresh.evaluate(PRESS)
    fresh.open(built.url(elsewhere))

    found = rows(fresh)
    assert [row["key"] for row in found if row["marked"]] == [marked]
    assert [row["key"] for row in found if row["tick"] == TICK] == [marked]


def test_a_marked_unit_shows_marked_in_the_rail_on_every_page_that_carries_one(
    fresh: OpenPage, built: Built
) -> None:
    marked = next(iter(built.pages))
    fresh.open(built.url(marked))
    fresh.evaluate(PRESS)
    for url in every_page(built):
        fresh.open(url)
        found = rows(fresh)
        assert [row["key"] for row in found if row["marked"] and row["tick"] == TICK] == [marked], (
            f"{url} does not show exactly the one marked unit"
        )


def test_the_rail_row_of_the_page_being_read_joins_the_control_and_follows_it_both_ways(
    fresh: OpenPage, built: Built
) -> None:
    key = next(iter(built.pages))
    fresh.open(built.url(key))
    control = fresh.evaluate(CONTROL_KEY)
    assert control == key, "the rail's key and the read-mark control's key are not the same key"

    fresh.evaluate(PRESS)
    assert [row["key"] for row in rows(fresh) if row["marked"] and row["tick"] == TICK] == [key]

    fresh.evaluate(PRESS)
    assert not [row for row in rows(fresh) if row["marked"] or row["tick"] == TICK]


def test_with_the_keys_cut_out_the_same_mark_lights_no_rail_row(
    fresh: OpenPage, keyless: Built
) -> None:
    marked, elsewhere = two_containers(keyless)
    fresh.open(keyless.url(marked))
    fresh.evaluate(PRESS)
    assert fresh.evaluate(f"window.studyforge.progress.marked({marked!r})") is True
    fresh.open(keyless.url(elsewhere))

    found = rows(fresh)
    assert found, "the control tree lost its rail, not only its keys"
    assert not [row for row in found if row["key"] or row["marked"] or row["tick"] == TICK]


# --- a screen reader hears what the tick shows --------------------------------

#: Every read-words element on the open page: the key of the row it sits in,
#: the region, whether assistive technology is given it, and the box it takes.
WORDS = (
    "Array.from(document.querySelectorAll('span[data-kind=\"read-state\"]')).map(w => {"
    " const row = w.closest('li'); const box = w.getBoundingClientRect();"
    " return {key: row.getAttribute('data-unit') || row.id,"
    "  region: row.closest('nav').getAttribute('aria-label'),"
    "  shown: !w.hidden && getComputedStyle(w).display !== 'none',"
    "  width: box.width, height: box.height, text: w.textContent}; })"
)

#: The rail row of the page being read: its box, which the words must not move.
OWN_ROW_BOX = (
    "(() => { const r = document.querySelector('" + ROWS + '[aria-current="page"]\')'
    ".getBoundingClientRect(); return [r.width, r.height]; })()"
)


def words(page: OpenPage) -> list[dict]:
    """Every read-words element of the open page, read live."""
    return list(page.evaluate(WORDS))  # type: ignore[arg-type]


def every_listing_page(built: Built) -> list[str]:
    """Every page that carries a rail or a list: each unit's, each container's, the index."""
    return every_page(built) + ["file://" + str(built.index)]


def test_a_fresh_store_gives_a_screen_reader_no_read_words_anywhere(
    fresh: OpenPage, built: Built
) -> None:
    for url in every_listing_page(built):
        fresh.open(url)
        found = words(fresh)
        assert found, f"{url} carries no read words to judge"
        assert not [w for w in found if w["shown"]], f"{url} says a unit is read"


def test_a_marked_unit_is_said_read_in_the_rail_and_the_lists_and_nowhere_else(
    fresh: OpenPage, built: Built
) -> None:
    marked = next(iter(built.pages))
    fresh.open(built.url(marked))
    fresh.evaluate(PRESS)
    regions: set[str] = set()
    for url in every_listing_page(built):
        fresh.open(url)
        shown = [w for w in words(fresh) if w["shown"]]
        assert shown, f"{url} does not say the marked unit is read"
        assert {w["key"] for w in shown} == {marked}, f"{url} says the wrong unit is read"
        assert len({w["text"] for w in words(fresh)}) == 1, "two strings for one state"
        # ⛔ The visual mark is unchanged: the words take no room on the screen.
        assert all(w["width"] <= 1 and w["height"] <= 1 for w in shown), url
        regions |= {w["region"] for w in shown}
    assert {"Containers", "Units", "Contents"} <= regions


def test_the_words_follow_the_control_both_ways_and_move_nothing(
    fresh: OpenPage, built: Built
) -> None:
    key = next(iter(built.pages))
    fresh.open(built.url(key))
    before = fresh.evaluate(OWN_ROW_BOX)
    fresh.evaluate(PRESS)
    assert [w["key"] for w in words(fresh) if w["shown"]] == [key]
    assert fresh.evaluate(OWN_ROW_BOX) == before, "the read words moved the rail row"
    fresh.evaluate(PRESS)
    assert not [w for w in words(fresh) if w["shown"]]


def test_the_index_filter_matches_a_title_and_never_the_read_words(
    fresh: OpenPage, built: Built
) -> None:
    marked = next(iter(built.pages))
    fresh.open(built.url(marked))
    fresh.evaluate(PRESS)
    fresh.open("file://" + str(built.index))
    said = next(w["text"] for w in words(fresh) if w["shown"]).strip(" ,")
    title = fresh.evaluate(
        "Array.from(document.getElementById(" + repr(marked) + ").querySelector('a').childNodes)"
        ".filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim()"
    )
    shown = (
        "(q => { const f = document.querySelector('form[role=\"search\"] input');"
        " f.value = q; f.dispatchEvent(new Event('input'));"
        " return Array.from(document.querySelectorAll('nav[aria-label=\"Contents\"] li[id]'))"
        ".filter(r => !r.hidden).map(r => r.id); })"
    )
    assert fresh.evaluate(f"{shown}({title!r})") == [marked]
    assert fresh.evaluate(f"{shown}({said!r})") == []
