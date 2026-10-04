"""A practice's editor fills its pane on open, and the report is a strip until a run reports.

⭐ The workspace is opened at a wide desktop size, before any Run or Submit:
the editor is at least 70% of the pane's height and the report shows only its strip. After a
Submit the report body appears and the split is shared, the editor keeping its floor. The split
the reader drags is kept for that practice only: another practice opens at the default, and the
same one opens at the chosen split after a reload.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.visual import panes, served, site
from tests.visual.page import OpenPage
from tests.visual.panes import capture, drag, middle, read_panes, until, url

SIZES = {"desktop": (1515, 1060)}
LEAST = 0.70


@pytest.fixture(scope="module")
def tree(tmp_path_factory: pytest.TempPathFactory) -> site.Site:
    return panes.build(tmp_path_factory)


@pytest.fixture
def origin(tree: site.Site) -> Iterator[served.Served]:
    yield from panes.serve(tree)


def opened(page: OpenPage, origin: served.Served, size: tuple[int, int], index: int = 0) -> dict:
    page.resize(*size)
    panes.fresh(page, url(origin))
    page.open_practice(index)
    return until(page, lambda r: r["frame"] is not None, "built its editor frame")


def submit(page: OpenPage, origin: served.Served) -> dict:
    """Submit the open practice (the one whose panel is shown) and read the panes."""
    origin.runs.started.clear()
    origin.runs.release.clear()
    origin.runs.said = tuple(panes.said(case, panes.VERDICTS[case]) for case in panes.VERDICTS)
    page.evaluate(
        "document.querySelector('section[data-practice][data-workspace-open]"
        " [data-practice-act=\"test\"]').click()"
    )
    origin.runs.started.wait(panes.SETTLE)
    origin.runs.release.set()
    return until(page, lambda r: r["glance"] == "2/3 passed", "showed the verdict at a glance")


@pytest.mark.parametrize("size", SIZES)
def test_the_editor_fills_the_pane_and_the_report_is_only_its_strip_on_open(
    open_page: OpenPage, origin: served.Served, capture_dir: Path, size: str
) -> None:
    reading = opened(open_page, origin, SIZES[size])
    capture(open_page, capture_dir, f"editor-height-open-{size}.png")
    panel, editor = reading["panel"], reading["editor"]
    share = editor["height"] / panel["height"]
    assert share >= LEAST, f"the editor is {share:.0%} of the pane: {editor}, {panel}"
    assert reading["reportBody"] is None, "no report yet, so only its strip shows"
    assert reading["bar"] is not None


@pytest.mark.parametrize("size", SIZES)
def test_a_submit_shows_the_report_and_the_split_is_shared(
    open_page: OpenPage, origin: served.Served, capture_dir: Path, size: str
) -> None:
    opened(open_page, origin, SIZES[size])
    reading = submit(open_page, origin)
    capture(open_page, capture_dir, f"editor-height-reported-{size}.png")
    assert reading["reportBody"] is not None
    assert reading["editor"]["height"] >= 160 - 1
    assert reading["report"]["height"] > 72
    assert reading["panelOverflow"] <= 1


def test_the_chosen_split_is_kept_for_that_practice_only(
    open_page: OpenPage, origin: served.Served
) -> None:
    opened(open_page, origin, SIZES["desktop"])
    first = submit(open_page, origin)
    start = middle(first["reportDivider"])
    drag(open_page, start, (start[0], start[1] + 250))
    chosen = read_panes(open_page)["report"]["height"]
    assert abs(chosen - first["report"]["height"]) > 40, "the drag changed the split"
    panes.reload(open_page)
    open_page.open_practice(0)
    again = submit(open_page, origin)
    assert abs(again["report"]["height"] - chosen) <= 3, (again["report"], chosen)
    open_page.evaluate("document.querySelector('[data-workspace-act=\"next\"]').click()")
    until(open_page, lambda r: r["statementId"] != again["statementId"], "opened the next practice")
    other = submit(open_page, origin)
    assert abs(other["report"]["height"] - chosen) > 20, (other["report"], chosen)
