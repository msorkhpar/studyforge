"""The practice workspace's report, resized and collapsed, in a browser.

⭐ **Register ruling (2026-09-26).** The divider above the report is dragged —
mouse or touch, over the editor frame too — and moved with Up and Down, to give
the code more height; the report collapses to a bar at the bottom that still
shows the last verdict, a new Submit opens it again, and both choices survive a
reload.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.visual import panes, served, site
from tests.visual.page import OpenPage
from tests.visual.panes import (
    DESKTOP,
    REPORT_DIVIDER,
    capture,
    drag,
    focus,
    middle,
    move,
    press,
    read_panes,
    release,
    reload,
    submit,
    touch_drag,
    until,
    url,
)


@pytest.fixture(scope="module")
def tree(tmp_path_factory: pytest.TempPathFactory) -> site.Site:
    """A real built tree, with one extra page: two code practices and a quiz."""
    return panes.build(tmp_path_factory)


@pytest.fixture
def origin(tree: site.Site) -> Iterator[served.Served]:
    """One loopback origin over the tree, whose editor route answers two windows."""
    yield from panes.serve(tree)


# --- the report under the editor -------------------------------------------


def test_the_report_divider_resizes_the_report_by_mouse_touch_and_over_the_frame(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    panes.open_practice(open_page, url(origin))
    submitted = submit(open_page, origin)
    aria = submitted["reportDividerAria"]
    assert aria["role"] == "separator" and aria["orientation"] == "horizontal"
    assert aria["tabindex"] == "0" and aria["controls"].startswith("practice-report-")
    # ⭐ First the report is made short, so the frame above it is tall enough to
    # drag across.
    low = middle(submitted["reportDivider"])
    drag(open_page, low, (low[0], DESKTOP[1] - 2))
    before = read_panes(open_page)
    start = middle(before["reportDivider"])
    frame = before["frame"]
    target = frame["bottom"] - 100
    assert target > frame["top"] + 20, "the frame is too short to drag over"
    press(open_page, *start)
    for step in range(1, 9):
        move(open_page, start[0], start[1] + (target - start[1]) * step / 8)
    during = read_panes(open_page)
    assert during["dragging"] == "y" and during["framePointer"] == "none", during
    release(open_page, start[0], target)
    after = read_panes(open_page)
    assert abs(after["reportDivider"]["top"] + after["reportDivider"]["height"] / 2 - target) <= 3
    assert after["report"]["height"] > before["report"]["height"] + 50
    assert after["editor"]["height"] < before["editor"]["height"] - 50
    # ⭐ Touch gives the height back to the code.
    touch_drag(open_page, middle(after["reportDivider"]), (start[0], target + 150))
    touched = read_panes(open_page)
    assert touched["report"]["height"] < after["report"]["height"] - 100
    capture(open_page, capture_dir, "panes-report-resized.png")


def test_the_report_height_is_clamped_and_moved_by_the_keyboard(
    open_page: OpenPage, origin: served.Served
) -> None:
    panes.open_practice(open_page, url(origin))
    before = submit(open_page, origin)
    start = middle(before["reportDivider"])
    drag(open_page, start, (start[0], 5))
    tall = read_panes(open_page)
    # ⭐ The editor keeps its floor (`min-height: 10rem`).
    assert tall["editor"]["height"] >= 160 - 1, tall["editor"]
    # ⛔ And the report stops where the editor's floor is, rather than pushing
    # the panel past its own height.
    assert tall["panelOverflow"] <= 1, tall
    assert tall["reportDividerAria"]["now"] == tall["reportDividerAria"]["max"] < 90
    assert tall["panel"]["bottom"] <= DESKTOP[1] + 1
    drag(open_page, middle(tall["reportDivider"]), (start[0], DESKTOP[1] - 2))
    short = read_panes(open_page)
    assert short["report"]["height"] >= 72 - 1 and short["report"]["height"] < 90
    focus(open_page, REPORT_DIVIDER)
    open_page.press("Home")
    low = read_panes(open_page)["reportDividerAria"]
    assert low["now"] == low["min"]
    open_page.press("ArrowUp")
    open_page.press("ArrowUp")
    up = read_panes(open_page)
    assert up["reportDividerAria"]["now"] in (low["now"] + 4, low["now"] + 3)
    assert up["report"]["height"] > short["report"]["height"]
    open_page.press("ArrowDown")
    assert read_panes(open_page)["report"]["height"] < up["report"]["height"]
    open_page.press("End")
    end = read_panes(open_page)
    assert end["reportDividerAria"]["now"] == end["reportDividerAria"]["max"]
    assert end["editor"]["height"] >= 160 - 1


def test_the_report_collapses_to_a_bar_that_keeps_the_verdict_and_a_run_opens_it(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    panes.open_practice(open_page, url(origin))
    before = submit(open_page, origin)
    assert before["barAria"]["expanded"] == "true"
    assert before["barAria"]["controls"].startswith("practice-report-body-")
    focus(open_page, 'section[data-workspace-open] [data-practice-part="report-bar"]')
    open_page.press("Enter")
    closed = read_panes(open_page)
    assert closed["reportBody"] is None and closed["reportDivider"] is None
    assert closed["barAria"]["expanded"] == "false"
    assert closed["barAria"]["text"].startswith("Show report")
    assert closed["glance"] == "2/3 passed"
    # ⭐ The bar is at the foot of the workspace, and the editor took the height.
    bottom = closed["panel"]["bottom"] - closed["panelPadding"]
    assert abs(closed["bar"]["bottom"] - bottom) <= 1, (closed["bar"], bottom)
    assert closed["editor"]["height"] > before["editor"]["height"] + 50
    capture(open_page, capture_dir, "panes-report-collapsed.png")
    # ⭐ Remembered: a reload keeps it collapsed.
    reload(open_page)
    back = until(open_page, lambda r: r["bar"] is not None, "reopened")
    assert back["reportBody"] is None and back["barAria"]["expanded"] == "false"
    # ⭐ A new Submit opens the report, so its answer is seen.
    again = submit(open_page, origin)
    assert again["reportBody"] is not None and again["barAria"]["expanded"] == "true"
    # ⭐ And the bar, pressed, collapses and opens it.
    open_page.evaluate(
        "document.querySelector('section[data-workspace-open] [data-practice-part=\"report-bar\"]')"
        ".click()"
    )
    assert read_panes(open_page)["reportBody"] is None


def test_the_report_height_survives_a_reload(open_page: OpenPage, origin: served.Served) -> None:
    panes.open_practice(open_page, url(origin))
    before = submit(open_page, origin)
    start = middle(before["reportDivider"])
    drag(open_page, start, (start[0], start[1] - 150))
    sized = read_panes(open_page)
    reload(open_page)
    back = until(open_page, lambda r: r["report"] is not None, "reopened")
    assert abs(back["report"]["height"] - sized["report"]["height"]) <= 2
