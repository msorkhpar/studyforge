"""A corpus of four languages asks which to read, on a first visit, in a browser.

⭐ **Every clause drives the real question and the real switch.** The corpus declares four
languages and one mode for each, the first the default; its pages are opened in the headless
browser: the question lists exactly the declared modes and fits a phone, a choice is shown and
remembered across pages, the switch moves between the four in place, and a crawl, a page with
scripts off and a page whose storage is refused read the default mode and ask nothing.

⛔ **Each clause is asserted both ways (R12).** Each of the four choices shows its own language
and hides the others; a revisit does not ask and a refused store never asks; a section that
names two languages shows in both of their modes and in no other.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.studyforge.generate import four_corpus as four
from tests.visual import served
from tests.visual.four import (
    ASKING,
    CLEAR,
    QUESTION,
    REFUSED,
    SWITCHED,
    UNIT,
    VISIBLE,
    built,
    choose,
    in_mode,
    served_from,
)
from tests.visual.page import NARROW, WIDE, OpenPage


@pytest.fixture(scope="module")
def pure_origin(tmp_path_factory: pytest.TempPathFactory) -> Iterator[served.Served]:
    with served_from(built(tmp_path_factory, "pure", four.declared(absent=None))) as running:
        yield running


def reopen(page: OpenPage, origin: served.Served, where: str = UNIT, **kwargs: object) -> None:
    page.open(f"{origin.origin}/{where}", **kwargs)


def test_the_first_visit_lists_exactly_the_four_declared_modes_and_fits_a_phone(
    open_page: OpenPage, pure_origin: served.Served, capture_dir: Path
) -> None:
    for size in (WIDE, (360, 640)):
        open_page.resize(*size)
        reopen(open_page, pure_origin)
        open_page.evaluate(CLEAR)
        reopen(open_page, pure_origin)
        asking = open_page.evaluate(ASKING)
        assert asking["shown"] is True
        assert [one[:2] for one in asking["options"]] == [
            [f"only-{x}", f"{four.LABELS[x]} only"] for x in four.LANGS
        ]
        assert asking["left"] >= 0 and asking["right"] <= asking["width"]
        assert asking["page"] <= asking["width"], "no horizontal scroll"
        for _, _, left, right, height in asking["options"]:
            assert left >= 0 and right <= asking["width"] and height >= 44
        switched = open_page.evaluate(SWITCHED)
        assert switched["choices"] == [f"only-{x}" for x in four.LANGS]
        assert switched["pressed"] == ["only-aa"], "until answered the page is the default mode"
        open_page.capture(capture_dir / f"four-question-{size[0]}.png")
    open_page.evaluate(CLEAR)


def test_each_of_four_choices_shows_its_language_and_is_remembered_across_pages(
    open_page: OpenPage, pure_origin: served.Served
) -> None:
    where = four.PAGES[2]
    open_page.resize(*WIDE)
    reopen(open_page, pure_origin, where)
    open_page.evaluate(CLEAR)
    for number, lang in enumerate(four.LANGS, start=1):
        reopen(open_page, pure_origin, where)
        open_page.evaluate(CLEAR)
        reopen(open_page, pure_origin, where)
        open_page.evaluate(
            f"document.querySelector('{QUESTION} [data-mode-choice=\"only-{lang}\"]').click()"
        )
        shown = ["prose"] if number == 1 else [f"prose-{number}"]
        assert open_page.evaluate(VISIBLE) == shown, lang
        assert open_page.evaluate(ASKING)["shown"] is False
        for other in (where, "index.html", four.PAGES[1], where):
            reopen(open_page, pure_origin, other)
            assert open_page.evaluate(ASKING)["shown"] is False, f"{other} asked again"
            assert open_page.evaluate(SWITCHED)["pressed"] == [f"only-{lang}"], other
    open_page.evaluate(CLEAR)


def test_the_switch_moves_between_all_four_in_place_and_back(
    open_page: OpenPage, pure_origin: served.Served
) -> None:
    in_mode(open_page, pure_origin, "only-aa", four.PAGES[2])
    for lang, shown in (("dd", "prose-4"), ("bb", "prose-2"), ("cc", "prose-3"), ("aa", "prose")):
        choose(open_page, f"only-{lang}")
        assert open_page.evaluate(VISIBLE) == [shown], lang
        assert open_page.evaluate(SWITCHED)["pressed"] == [f"only-{lang}"]
    open_page.evaluate(CLEAR)


def test_a_crawl_and_scripts_off_read_the_default_mode_and_a_refused_store_asks_nothing(
    open_page: OpenPage, pure_origin: served.Served
) -> None:
    open_page.resize(*NARROW)
    open_page.open(f"{pure_origin.origin}/{four.PAGES[2]}", scripts=False)
    assert open_page.evaluate(VISIBLE) == ["prose"]
    assert open_page.evaluate(ASKING)["shown"] is False
    assert open_page.evaluate(SWITCHED)["mode"] == "only-aa"
    open_page.browser.call(
        "Page.addScriptToEvaluateOnNewDocument", {"source": REFUSED}, session=open_page.session
    )
    reopen(open_page, pure_origin, four.PAGES[2])
    assert open_page.evaluate(ASKING)["shown"] is False
    assert open_page.evaluate(SWITCHED)["mode"] == "only-aa"
