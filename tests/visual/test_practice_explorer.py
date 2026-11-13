"""A project practice's explorer runs beside the editor, and the editor fills the pane.

⭐ A project practice's explorer is a `div[data-practice-explorer]` that is also the tablist
(`data-practice-part="tabs"`). In the open workspace it stands in the first column, down the
editor slot's whole height; the pop-out link takes one line over the frame; and the frame fills
the rest. ⛔ The failure this guards: the workspace sheet put the tabs in the row ABOVE the frame,
that row grew to the explorer's height, and the frame was left its 16rem minimum, a small box in a
corner with the link floating in an empty row.

⭐ The served editor answers a window for every file, so every button of the explorer shows and
the explorer is as tall as a real project's.
"""

from __future__ import annotations

import copy
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.render.page import render
from tests.studyforge.render.page.sites import FIXTURES as UNIT_CASE_OF
from tests.visual import panes, served, site
from tests.visual.page import OpenPage
from tests.visual.panes import CORPUS, capture, fresh, until

#: The page this module writes beside the corpus's own unit page.
PAGE = "a-project.unit.html"

SIZES = {"laptop": (1280, 900), "wide": (2048, 1038)}

#: The explorer's least share of the editor slot's height, and the frame's.
EXPLORER_LEAST = 0.90
FRAME_LEAST = 0.70

WS = "practice/project"

#: A project of a realistic size: its explorer is far taller than one row of tabs.
PROJECT = {
    "main_path": f"{WS}/src/shop/model.py",
    "files": [f"{WS}/src/shop/{name}.py" for name in ("orders", "stock", "prices", "report")],
    "test_path": f"{WS}/tests/test_model.py",
    "run_command": ["python3", "-m", "shop"],
    "test_command": ["python3", "-m", "pytest", f"{WS}/tests"],
    "provenance": "generated",
    "trust": "advisory",
    "cases": [
        {"id": "a", "kind": "main", "says": "it works"},
        {"id": "b", "kind": "edge", "says": "the edge"},
        {"id": "c", "kind": "kept", "says": "the old part still works"},
    ],
    "report": {"format": "junit", "path": f"{WS}/target/report.xml"},
    "read_only": [
        f"{WS}/README.md",
        f"{WS}/pyproject.toml",
        f"{WS}/data/orders.csv",
        f"{WS}/data/stock.csv",
        f"{WS}/src/shop/__init__.py",
        f"{WS}/src/shop/io.py",
        f"{WS}/tests/conftest.py",
        f"{WS}/tests/fixtures/small.csv",
        f"{WS}/tests/fixtures/large.csv",
    ],
}

#: What the served editor answers: a window for every file, so every button shows.
WINDOWS = {
    "main": {"url": "about:blank#main", "path": PROJECT["main_path"]},
    "test": {"url": "about:blank#test", "path": PROJECT["test_path"]},
    "files": [
        {"url": f"about:blank#file{n}", "path": path} for n, path in enumerate(PROJECT["files"])
    ],
    "read_only": [
        {"url": f"about:blank#ro{n}", "path": path} for n, path in enumerate(PROJECT["read_only"])
    ],
}

#: The four boxes this module measures, and one rem in pixels.
LAYOUT = """
(() => {
  const box = (el) => {
    if (!el || !el.checkVisibility()) return null;
    const b = el.getBoundingClientRect();
    return {top: b.top, bottom: b.bottom, left: b.left, right: b.right,
            width: b.width, height: b.height};
  };
  const panel = document.querySelector('section[data-practice][data-workspace-open]');
  if (!panel) return null;
  return {
    slot: box(panel.querySelector('div[data-practice-part="editor"]')),
    explorer: box(panel.querySelector('div[data-practice-explorer]')),
    frame: box(panel.querySelector('div[data-practice-frame="main"] iframe')),
    popout: box(panel.querySelector('a[data-practice-popout]')),
    rem: parseFloat(getComputedStyle(document.documentElement).fontSize)
  };
})()
"""


@pytest.fixture(scope="module")
def tree(tmp_path_factory: pytest.TempPathFactory) -> site.Site:
    """A real built tree, with one extra page: one project practice."""
    root = tmp_path_factory.mktemp("explorer-site")
    built = site.build(root)
    case = UNIT_CASE_OF[CORPUS]()
    document = copy.deepcopy(case.document)
    practice = next(part for part in document["sections"] if part.get("kind") == "practice")
    others = [part for part in document["sections"] if part.get("kind") != "practice"]
    one = copy.deepcopy(practice)
    one.update(key="practice-project", heading="Practice: The shop", workspace=dict(PROJECT))
    document["sections"] = [*others, one]
    where = Path(root / CORPUS / str(case.placement.unit.page))
    (where.parent / PAGE).write_bytes(render(document, case.placement))
    return built


@pytest.fixture
def origin(tree: site.Site) -> Iterator[served.Served]:
    """One loopback origin over the tree, whose editor answers a window for every file."""
    for running in panes.serve(tree):
        running.runs.windows = copy.deepcopy(WINDOWS)
        yield running


def url(origin: served.Served) -> str:
    case = UNIT_CASE_OF[CORPUS]()
    return f"{origin.origin}/{Path(str(case.placement.unit.page)).parent / PAGE}"


def read_layout(page: OpenPage) -> dict:
    return dict(page.evaluate(LAYOUT))  # type: ignore[call-overload]


@pytest.mark.parametrize("size", SIZES)
def test_the_explorer_runs_beside_the_editor_and_the_frame_fills_the_slot(
    open_page: OpenPage, origin: served.Served, capture_dir: Path, size: str
) -> None:
    open_page.resize(*SIZES[size])
    fresh(open_page, url(origin))
    open_page.open_practice(0)
    until(open_page, lambda r: r["frame"] is not None, "built its editor frame")
    layout = read_layout(open_page)
    capture(open_page, capture_dir, f"explorer-open-{size}.png")
    slot, explorer, frame, popout = (layout[k] for k in ("slot", "explorer", "frame", "popout"))
    assert slot and explorer and frame and popout, f"a box is not shown: {layout}"
    # ⭐ Side by side, not stacked.
    assert explorer["left"] < frame["left"], f"the explorer is not left of the frame: {layout}"
    overlap = min(explorer["bottom"], frame["bottom"]) - max(explorer["top"], frame["top"])
    assert overlap > 0, f"the explorer and the frame do not share a band: {layout}"
    # ⭐ The explorer runs the slot's height, and the frame fills the rest.
    share = explorer["height"] / slot["height"]
    assert share >= EXPLORER_LEAST, f"the explorer is {share:.0%} of the slot: {layout}"
    share = frame["height"] / slot["height"]
    assert share >= FRAME_LEAST, f"the frame is {share:.0%} of the slot: {layout}"
    assert frame["height"] > 16 * layout["rem"], f"the frame is at its 16rem floor: {layout}"
    # ⭐ The link takes one line, over the frame.
    assert popout["height"] < 3 * layout["rem"], f"the link's row is tall: {layout}"
    assert popout["bottom"] <= frame["top"] + 1, f"the link is not above the frame: {layout}"
