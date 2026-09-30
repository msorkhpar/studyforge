"""The practice workspace's description, resized and closed, in a browser.

⭐ In a code practice's workspace the reader
drags the divider between the description and the editor — mouse, touch or pen
— and moves it with the keyboard; closes the description and opens it again;
and finds both choices again after a reload. ⛔ Real input throughout, for
`panes.py`'s reason.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.visual import panes, served, site
from tests.visual.page import OpenPage
from tests.visual.panes import (
    DESKTOP,
    EDGE,
    GUTTER,
    LEAST_LEFT,
    LEAST_RIGHT,
    PHONE,
    capture,
    drag,
    file_url,
    focus,
    fresh,
    left_width,
    middle,
    mouse,
    move,
    press,
    read_panes,
    release,
    reload,
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


# --- the description's side -------------------------------------------------


def test_the_divider_stands_between_the_two_sides_and_says_what_it_is(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    reading = panes.open_practice(open_page, url(origin))
    aria = reading["dividerAria"]
    assert aria["role"] == "separator" and aria["orientation"] == "vertical"
    assert aria["tabindex"] == "0" and aria["controls"] == reading["statementId"]
    assert aria["now"] == 42 and aria["min"] == 19 and aria["max"] == 72
    assert abs(left_width(reading) - 0.42 * DESKTOP[0]) <= 1
    divider = reading["divider"]
    assert abs(divider["left"] - reading["statement"]["right"]) <= 1
    assert abs(reading["panel"]["left"] - divider["right"]) <= 1
    toggle = reading["toggleAria"]
    assert toggle["expanded"] == "true" and toggle["text"] == "Hide description"
    assert toggle["controls"] == reading["statementId"]
    assert reading["edge"] is None, "the edge that reopens shows while the description is open"
    capture(open_page, capture_dir, "panes-default.png")


def test_dragging_the_divider_with_a_mouse_widens_the_description(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    before = panes.open_practice(open_page, url(origin))
    start = middle(before["divider"])
    drag(open_page, start, (700, start[1]))
    after = read_panes(open_page)
    assert abs(after["statement"]["right"] - (700 - GUTTER / 2)) <= 2, after["statement"]
    assert abs(after["panel"]["left"] - after["divider"]["right"]) <= 1
    # ⭐ The editor follows its container: the frame is as wide as the side now.
    assert after["frame"]["width"] < before["frame"]["width"] - 100
    assert after["dividerAria"]["now"] == round((700 - GUTTER / 2) / DESKTOP[0] * 100)
    assert after["dragging"] is None
    capture(open_page, capture_dir, "panes-dragged-wider.png")
    # ⭐ And back the other way.
    drag(open_page, middle(after["divider"]), (400, start[1]))
    assert abs(read_panes(open_page)["statement"]["right"] - (400 - GUTTER / 2)) <= 2


def test_a_drag_over_the_editor_frame_is_not_swallowed_by_it(
    open_page: OpenPage, origin: served.Served
) -> None:
    before = panes.open_practice(open_page, url(origin))
    start = middle(before["divider"])
    frame = before["frame"]
    inside = (frame["left"] + 200, (frame["top"] + frame["bottom"]) / 2)
    assert inside[0] < frame["right"], "the frame is too narrow to drag over"
    press(open_page, *start)
    for step in range(1, 9):
        move(open_page, start[0] + (inside[0] - start[0]) * step / 8, inside[1])
    during = read_panes(open_page)
    # ⛔ The frame takes no pointer while the divider is held.
    assert during["dragging"] == "x" and during["framePointer"] == "none", during
    assert abs(during["statement"]["right"] - (inside[0] - GUTTER / 2)) <= 2, (
        f"the drag stopped over the frame: {during['statement']}"
    )
    move(open_page, inside[0] + 60, inside[1])
    assert abs(read_panes(open_page)["statement"]["right"] - (inside[0] + 60 - GUTTER / 2)) <= 2
    release(open_page, inside[0] + 60, inside[1])
    after = read_panes(open_page)
    assert after["dragging"] is None and after["framePointer"] != "none"
    # ⛔ Not stuck: a pointer moved with no button held moves nothing.
    mouse(open_page, "mouseMoved", 300, inside[1], down=False)
    assert read_panes(open_page)["statement"]["right"] == after["statement"]["right"]


def test_touch_and_pen_drag_the_divider_too(open_page: OpenPage, origin: served.Served) -> None:
    before = panes.open_practice(open_page, url(origin))
    start = middle(before["divider"])
    touch_drag(open_page, start, (640, start[1]))
    touched = read_panes(open_page)
    assert abs(touched["statement"]["right"] - (640 - GUTTER / 2)) <= 2, touched["statement"]
    drag(open_page, middle(touched["divider"]), (480, start[1]), pointer="pen")
    assert abs(read_panes(open_page)["statement"]["right"] - (480 - GUTTER / 2)) <= 2


def test_the_width_is_clamped_at_both_ends(open_page: OpenPage, origin: served.Served) -> None:
    before = panes.open_practice(open_page, url(origin))
    start = middle(before["divider"])
    drag(open_page, start, (5, start[1]))
    narrow = read_panes(open_page)
    assert abs(left_width(narrow) - LEAST_LEFT) <= 1, narrow["statement"]
    drag(open_page, middle(narrow["divider"]), (DESKTOP[0] - 5, start[1]))
    wide = read_panes(open_page)
    assert abs(wide["panel"]["width"] - (LEAST_RIGHT - GUTTER)) <= 2, wide["panel"]
    assert wide["panel"]["right"] >= DESKTOP[0] - 1


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_the_keyboard_moves_the_divider_and_its_focus_shows_in_the_theme(
    open_page: OpenPage, origin: served.Served, scheme: str
) -> None:
    open_page.resize(*DESKTOP)
    fresh(open_page, url(origin), scheme=scheme)
    open_page.open_practice(0)
    until(open_page, lambda r: r["frame"] is not None, "built its editor frame")
    # ⭐ Reached by Tab, so the ring is the keyboard's (`:focus-visible`).
    focus(open_page, '[data-workspace-act="close"]')
    open_page.tab()
    assert read_panes(open_page)["focused"] == "divider"
    ring = open_page.focused()["outline"]
    ink = open_page.evaluate(
        "(() => { const probe = document.createElement('i');"
        " probe.style.color = 'var(--focus)'; document.body.append(probe);"
        " const c = getComputedStyle(probe).color; probe.remove(); return c; })()"
    )
    assert ring.startswith("solid 2px") and ring.endswith(str(ink)), (ring, ink)
    open_page.press("ArrowRight")
    open_page.press("ArrowRight")
    assert read_panes(open_page)["dividerAria"]["now"] == 46
    open_page.press("ArrowLeft")
    moved = read_panes(open_page)
    assert moved["dividerAria"]["now"] == 44
    assert abs(left_width(moved) - 0.44 * DESKTOP[0]) <= 1
    open_page.press("Home")
    assert abs(left_width(read_panes(open_page)) - LEAST_LEFT) <= 1
    open_page.press("End")
    end = read_panes(open_page)
    assert abs(end["panel"]["width"] - (LEAST_RIGHT - GUTTER)) <= 2
    assert end["dividerAria"]["now"] == end["dividerAria"]["max"]


def test_the_description_closes_and_opens_again(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    before = panes.open_practice(open_page, url(origin))
    focus(open_page, '[data-workspace-act="statement"]')
    open_page.press("Enter")
    closed = read_panes(open_page)
    assert closed["statement"] is None and closed["divider"] is None
    assert abs(closed["panel"]["left"] - EDGE) <= 1 and closed["panel"]["right"] >= DESKTOP[0] - 1
    assert closed["frame"]["width"] > before["frame"]["width"] + 300
    assert closed["toggleAria"]["expanded"] == "false"
    assert closed["toggleAria"]["text"] == "Show description"
    assert closed["edge"] and closed["edgeAria"]["expanded"] == "false"
    assert closed["edgeAria"]["text"].endswith("Show description")
    capture(open_page, capture_dir, "panes-description-closed.png")
    # ⭐ The edge opens it, and focus goes to the divider it stands for.
    focus(open_page, '[data-workspace-act="reopen"]')
    open_page.press("Enter")
    opened = read_panes(open_page)
    assert opened["statement"] and opened["edge"] is None
    assert opened["toggleAria"]["expanded"] == "true" and opened["focused"] == "divider"
    assert abs(left_width(opened) - left_width(before)) <= 1
    # ⭐ And Enter on the divider closes it, handing focus to the edge.
    open_page.press("Enter")
    again = read_panes(open_page)
    assert again["statement"] is None and again["focused"] == "reopen"


def test_the_width_and_the_closed_description_survive_a_reload(
    open_page: OpenPage, origin: served.Served
) -> None:
    before = panes.open_practice(open_page, url(origin))
    start = middle(before["divider"])
    drag(open_page, start, (620, start[1]))
    focus(open_page, '[data-workspace-act="statement"]')
    open_page.press("Enter")
    stored = json.loads(read_panes(open_page)["stored"])["display"]
    assert stored["workspace-statement"] == "closed", stored
    # ⭐ The address names the open practice, so the reload opens it again.
    reload(open_page)
    back = until(open_page, lambda r: r["open"] and r["panel"] is not None, "reopened")
    assert back["statement"] is None and abs(back["panel"]["left"] - EDGE) <= 1
    assert back["toggleAria"]["expanded"] == "false"
    focus(open_page, '[data-workspace-act="reopen"]')
    open_page.press("Enter")
    assert abs(read_panes(open_page)["statement"]["right"] - (620 - GUTTER / 2)) <= 2


def test_with_no_storage_the_divider_and_close_still_work(
    open_page: OpenPage, origin: served.Served
) -> None:
    # ⛔ A browser that refuses site data throws on the property itself.
    open_page.browser.call(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": "Object.defineProperty(window, 'localStorage',"
            " {get() { throw new DOMException('blocked', 'SecurityError'); }});"
        },
        session=open_page.session,
    )
    before = panes.open_practice(open_page, url(origin))
    assert before["stored"] == "blocked"
    start = middle(before["divider"])
    drag(open_page, start, (700, start[1]))
    assert abs(read_panes(open_page)["statement"]["right"] - (700 - GUTTER / 2)) <= 2
    focus(open_page, '[data-workspace-act="statement"]')
    open_page.press("Enter")
    assert read_panes(open_page)["statement"] is None
    thrown = [e for e in open_page.browser.events if e.get("method") == "Runtime.exceptionThrown"]
    assert thrown == [], thrown


def test_over_file_the_divider_and_close_work_and_ask_nothing(
    open_page: OpenPage, tree: site.Site
) -> None:
    before = panes.open_practice(open_page, file_url(tree), frame=False)
    assert before["divider"] and before["toggle"]
    # ⭐ The plain fallback: no run, so nothing to report and no bar for it.
    assert before["bar"] is None and before["reportDivider"] is None
    asked = list(open_page.requests())
    start = middle(before["divider"])
    drag(open_page, start, (700, start[1]))
    assert abs(read_panes(open_page)["statement"]["right"] - (700 - GUTTER / 2)) <= 2
    focus(open_page, '[data-workspace-act="statement"]')
    open_page.press("Enter")
    assert read_panes(open_page)["statement"] is None
    assert list(open_page.requests()) == asked, "resizing or closing asked for something"


def test_at_phone_width_the_workspace_stacks_and_shows_no_divider(
    open_page: OpenPage, origin: served.Served
) -> None:
    # ⭐ A closed description from a wider window is shown here: the stack has
    # no room to give it back from.
    open_page.resize(*DESKTOP)
    fresh(open_page, url(origin))
    open_page.open_practice(0)
    focus(open_page, '[data-workspace-act="statement"]')
    open_page.press("Enter")
    open_page.resize(*PHONE)
    open_page.open(url(origin))
    open_page.open_practice(0)
    reading = read_panes(open_page)
    assert reading["divider"] is None and reading["toggle"] is None and reading["edge"] is None
    assert reading["statement"] and reading["panel"]
    assert reading["statement"]["bottom"] <= reading["panel"]["top"] + 1
    assert reading["statement"]["width"] >= PHONE[0] - 1


def test_a_quiz_shows_no_divider(open_page: OpenPage, origin: served.Served) -> None:
    reading = panes.open_practice(open_page, url(origin), 2, frame=False)
    assert reading["divider"] is None and reading["toggle"] is None and reading["edge"] is None
