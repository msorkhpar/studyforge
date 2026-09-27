"""What the two pane modules share: their page, their readings and real input.

⭐ `test_practice_panes.py` reads the description's side and
`test_practice_report.py` the report's; both read one page, built here, and
drive it with the browser's own input pipeline.

⭐ **Register ruling (2026-09-26), read where only a browser can read it.** In a
code practice's workspace the reader drags the divider between the description
and the editor — mouse, touch or pen — and moves it with the keyboard; closes
the description and opens it again; drags the divider above the report, and
collapses the report to a bar at the bottom that still shows the last verdict;
and finds every one of those choices again after a reload.

⛔ **Real input, never a synthetic `dispatchEvent`.** A drag is pressed, moved
and released through the browser's own input pipeline, which is the only place
an `iframe` can swallow the pointer — the failure the drag's frame rule exists
to prevent. Keys are real key events for `test_keyboard`'s reason.

⭐ **The page is the two modules' own**, written beside the depth-2 unit page:
two code practices that declare a breakdown, and a quiz.
"""

from __future__ import annotations

import base64
import copy
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.render.page import render
from studyforge.serve.routes.breakdown import said
from tests.studyforge.render.page.sites import FIXTURES as UNIT_CASE_OF
from tests.studyforge.render.page.test_practice import QUIZ
from tests.visual import served, site
from tests.visual.page import OpenPage
from tests.visual.test_practice_breakdown import BROKEN_DOWN

#: The corpus this module borrows a document and a placement from.
CORPUS = "depth2"

#: The page this module writes beside that corpus's own unit page.
PAGE = "a-panes.unit.html"

DESKTOP = (1280, 800)
PHONE = (390, 844)

#: Seconds a reading waits for a state the page's script produces.
SETTLE = 15.0

#: The clamps `practice-panes.js` holds, in pixels: the description's least
#: width and the editor side's.
LEAST_LEFT = 240
LEAST_RIGHT = 360

#: The gutter the left divider stands in, and the edge that reopens.
GUTTER = 12
EDGE = 36

#: The whole of what this module reads, as the browser holds it now.
STATE = """
(() => {
  const box = (el) => {
    if (!el || !el.checkVisibility()) return null;
    const b = el.getBoundingClientRect();
    return {top: b.top, bottom: b.bottom, left: b.left, right: b.right,
            width: b.width, height: b.height};
  };
  const shell = document.querySelector('div[data-workspace]');
  const statement = document.querySelector('section[data-kind][data-workspace-open]');
  const panel = document.querySelector('section[data-practice][data-workspace-open]');
  const inPanel = (name) => panel
    ? panel.querySelector('[data-practice-part="' + name + '"]') : null;
  const divider = shell.querySelector('[data-workspace-part="divider"]');
  const toggle = shell.querySelector('[data-workspace-act="statement"]');
  const edge = shell.querySelector('[data-workspace-act="reopen"]');
  const rdiv = inPanel('report-divider');
  const bar = inPanel('report-bar');
  const frame = panel ? panel.querySelector('iframe') : null;
  const aria = (el) => el ? {
    role: el.getAttribute('role'), orientation: el.getAttribute('aria-orientation'),
    now: Number(el.getAttribute('aria-valuenow')), min: Number(el.getAttribute('aria-valuemin')),
    max: Number(el.getAttribute('aria-valuemax')), controls: el.getAttribute('aria-controls'),
    expanded: el.getAttribute('aria-expanded'), tabindex: el.getAttribute('tabindex'),
    text: el.innerText.replace(/\\s+/g, ' ').trim()
  } : null;
  let stored = null;
  try { stored = localStorage.getItem('studyforge.display.v1'); } catch (e) { stored = 'blocked'; }
  return {
    viewport: {w: window.innerWidth, h: window.innerHeight},
    open: document.documentElement.hasAttribute('data-workspace-open'),
    statementId: statement ? statement.id : null,
    statement: box(statement), panel: box(panel), frame: box(frame),
    framePointer: frame ? getComputedStyle(frame).pointerEvents : null,
    dragging: document.documentElement.getAttribute('data-workspace-dragging'),
    divider: box(divider), dividerAria: aria(divider),
    toggle: box(toggle), toggleAria: aria(toggle),
    edge: box(edge), edgeAria: aria(edge),
    editor: box(inPanel('editor')), report: box(inPanel('report')),
    reportBody: box(inPanel('report-body')),
    reportDivider: box(rdiv), reportDividerAria: aria(rdiv),
    bar: box(bar), barAria: aria(bar),
    glance: bar ? bar.querySelector('[data-practice-part="glance"]').textContent.trim() : null,
    panelPadding: panel ? parseFloat(getComputedStyle(panel).paddingBottom) : 0,
    panelOverflow: panel ? panel.scrollHeight - panel.clientHeight : 0,
    focused: document.activeElement ? (document.activeElement.getAttribute('data-workspace-part')
      || document.activeElement.getAttribute('data-workspace-act')
      || document.activeElement.getAttribute('data-practice-part') || '') : '',
    stored: stored
  };
})()
"""

#: The breakdown's three declared cases: a main ask and two edges.
VERDICTS = {"test_greets": True, "test_empty": True, "test_accent": False}


def build(tmp_path_factory: pytest.TempPathFactory) -> site.Site:
    """A real built tree, with one extra page: two code practices and a quiz."""
    root = tmp_path_factory.mktemp("panes-site")
    built = site.build(root)
    case = UNIT_CASE_OF[CORPUS]()
    document = copy.deepcopy(case.document)
    practice = next(part for part in document["sections"] if part.get("kind") == "practice")
    others = [part for part in document["sections"] if part.get("kind") != "practice"]
    made = []
    for key, heading in (
        ("practice-java", "Practice: Greeter"),
        ("practice-shout", "Practice: Shouter"),
        ("practice-quiz", "Practice: Check yourself"),
    ):
        one = copy.deepcopy(practice)
        record = QUIZ if key == "practice-quiz" else BROKEN_DOWN
        one.update(key=key, heading=heading, workspace=dict(record))
        made.append(one)
    document["sections"] = [*others, *made]
    where = Path(root / CORPUS / str(case.placement.unit.page))
    (where.parent / PAGE).write_bytes(render(document, case.placement))
    return built


def serve(tree: site.Site) -> Iterator[served.Served]:
    """One loopback origin over the tree, whose editor route answers two windows."""
    with served.serving(tree, CORPUS, windows=True) as running:
        yield running


def relative() -> str:
    case = UNIT_CASE_OF[CORPUS]()
    return str(Path(str(case.placement.unit.page)).parent / PAGE)


def url(origin: served.Served) -> str:
    return f"{origin.origin}/{relative()}"


def file_url(tree: site.Site) -> str:
    return tree.url("depth2-unit-01").rsplit("/", 1)[0] + "/" + PAGE


def read_panes(page: OpenPage) -> dict:
    return dict(page.evaluate(STATE))  # type: ignore[call-overload]


def until(page: OpenPage, ready, what: str) -> dict:
    deadline = time.monotonic() + SETTLE
    reading = read_panes(page)
    while time.monotonic() < deadline:
        if ready(reading):
            return reading
        time.sleep(0.05)
        reading = read_panes(page)
    raise AssertionError(f"the workspace never {what}; it reads {reading}")


def fresh(page: OpenPage, url: str, *, scheme: str = "light") -> None:
    """Open `url` with no pane choice kept from an earlier check on this origin."""
    page.open(url, scheme=scheme)
    page.evaluate(
        "(() => { try { localStorage.removeItem('studyforge.display.v1'); }"
        " catch (e) { return; } })()"
    )
    page.open(url, scheme=scheme)


def reload(page: OpenPage) -> None:
    """Reload the page as a reader would, keeping its address and its store."""
    page.browser.events.clear()
    page.browser.call("Page.reload", {}, session=page.session)
    page.browser.wait("Page.loadEventFired", timeout=30.0)
    page._settle()


def open_practice(page: OpenPage, address: str, index: int = 0, *, frame: bool = True) -> dict:
    page.resize(*DESKTOP)
    fresh(page, address)
    page.open_practice(index)
    if frame:
        return until(page, lambda r: r["frame"] is not None, "built its editor frame")
    return read_panes(page)


def capture(page: OpenPage, directory: Path, name: str) -> None:
    """Keep a viewport screenshot in the run's capture directory (`conftest.capture_dir`)."""
    # ⭐ The viewport only: the workspace IS the viewport, and a full-page
    # capture would show the page under it as well.
    shot = page.browser.call("Page.captureScreenshot", {"format": "png"}, session=page.session)
    destination = directory / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(base64.b64decode(shot["data"]))


# --- real input -----------------------------------------------------------


def mouse(page: OpenPage, kind: str, x: float, y: float, *, down: bool, pointer: str = "mouse"):
    page.browser.call(
        "Input.dispatchMouseEvent",
        {
            "type": kind,
            "x": x,
            "y": y,
            "button": "left" if kind != "mouseMoved" or down else "none",
            "buttons": 1 if down else 0,
            "clickCount": 1 if kind != "mouseMoved" else 0,
            "pointerType": pointer,
        },
        session=page.session,
    )


def press(page: OpenPage, x: float, y: float, *, pointer: str = "mouse") -> None:
    mouse(page, "mouseMoved", x, y, down=False, pointer=pointer)
    mouse(page, "mousePressed", x, y, down=True, pointer=pointer)


def move(page: OpenPage, x: float, y: float, *, pointer: str = "mouse") -> None:
    mouse(page, "mouseMoved", x, y, down=True, pointer=pointer)


def release(page: OpenPage, x: float, y: float, *, pointer: str = "mouse") -> None:
    mouse(page, "mouseReleased", x, y, down=False, pointer=pointer)


def drag(page: OpenPage, start: tuple[float, float], end: tuple[float, float], **kind) -> None:
    """Press at `start`, move there in steps, and release at `end`."""
    press(page, *start, **kind)
    for step in range(1, 9):
        move(
            page,
            start[0] + (end[0] - start[0]) * step / 8,
            start[1] + (end[1] - start[1]) * step / 8,
            **kind,
        )
    release(page, *end, **kind)


def touch_drag(page: OpenPage, start: tuple[float, float], end: tuple[float, float]) -> None:
    def touch(kind: str, points: list[dict]) -> None:
        page.browser.call(
            "Input.dispatchTouchEvent", {"type": kind, "touchPoints": points}, session=page.session
        )

    touch("touchStart", [{"x": start[0], "y": start[1]}])
    for step in range(1, 9):
        x = start[0] + (end[0] - start[0]) * step / 8
        y = start[1] + (end[1] - start[1]) * step / 8
        touch("touchMove", [{"x": x, "y": y}])
    touch("touchEnd", [])


def middle(box: dict) -> tuple[float, float]:
    return ((box["left"] + box["right"]) / 2, (box["top"] + box["bottom"]) / 2)


def focus(page: OpenPage, selector: str) -> None:
    page.evaluate(f"document.querySelector({selector!r}).focus()")


LEFT_DIVIDER = 'div[data-workspace-part="divider"]'
REPORT_DIVIDER = 'section[data-workspace-open] div[data-practice-part="report-divider"]'


def left_width(reading: dict) -> float:
    return reading["statement"]["width"]


def submit(page: OpenPage, origin: served.Served) -> dict:
    origin.runs.started.clear()
    origin.runs.release.clear()
    origin.runs.said = tuple(said(case, VERDICTS[case]) for case in VERDICTS)
    page.evaluate(
        "document.querySelector('[data-workspace-open] [data-practice-act=\"test\"]').click()"
    )
    origin.runs.started.wait(SETTLE)
    origin.runs.release.set()
    return until(page, lambda r: r["glance"] == "2/3 passed", "showed the verdict at a glance")
