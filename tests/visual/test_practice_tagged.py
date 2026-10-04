"""A language-tagged practice opens with its editor filling the pane, and the dividers still work.

⛔ The reading modes' generated rules show a tagged section the reader is linked to with
`display: block`, which once outweighed the workspace's flex column: the editor stayed about eight
lines tall, the rest of the pane was empty and no divider changed anything. Here the page carries
that very rule and a tagged panel, and a real drag and real keys move the editor's height.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.visual import panes, served, site
from tests.visual.page import OpenPage
from tests.visual.panes import DESKTOP, capture, drag, focus, middle, read_panes, submit, url

#: The rule a corpus's reading modes generate (`modes.files`), for a section tagged for the other
#: language that the reader reached by a link.
MODE_RULE = (
    'html[data-mode="python"] section[data-lang][data-linked]:not([data-lang="python"])'
    " { display: block; }"
)

TAG = """
(() => {
  const style = document.createElement('style');
  style.textContent = %r;
  document.head.appendChild(style);
  document.documentElement.setAttribute('data-mode', 'python');
  document.querySelectorAll('section[data-practice]').forEach((one) => {
    one.setAttribute('data-lang', 'java');
    one.setAttribute('data-linked', '');
  });
  return true;
})()
""" % MODE_RULE


@pytest.fixture(scope="module")
def tree(tmp_path_factory: pytest.TempPathFactory) -> site.Site:
    return panes.build(tmp_path_factory)


@pytest.fixture
def origin(tree: site.Site) -> Iterator[served.Served]:
    yield from panes.serve(tree)


def opened(page: OpenPage, origin: served.Served) -> dict:
    page.resize(*DESKTOP)
    panes.fresh(page, url(origin))
    page.evaluate(TAG)
    page.open_practice(0)
    return panes.until(page, lambda r: r["frame"] is not None, "built its editor frame")


def test_the_editor_fills_the_pane_instead_of_keeping_eight_lines(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    reading = opened(open_page, origin)
    panel, editor = reading["panel"], reading["editor"]
    assert open_page.evaluate(
        "getComputedStyle(document.querySelector('section[data-practice][data-workspace-open]')).display"
    ) == "flex"
    assert editor["height"] >= (panel["height"] - 160) * 0.7, (editor, panel)
    capture(open_page, capture_dir, "practice-tagged-fills.png")


def test_dragging_the_handle_and_the_arrow_keys_change_the_editor_height(
    open_page: OpenPage, origin: served.Served
) -> None:
    opened(open_page, origin)
    submitted = submit(open_page, origin)
    start = middle(submitted["reportDivider"])
    before = read_panes(open_page)["editor"]["height"]
    drag(open_page, start, (start[0], start[1] + 150))
    after = read_panes(open_page)["editor"]["height"]
    assert after > before + 50, (before, after)
    focus(open_page, 'section[data-workspace-open] [data-practice-part="report-divider"]')
    open_page.press("ArrowUp")
    open_page.press("ArrowUp")
    assert read_panes(open_page)["editor"]["height"] < after, "the arrow keys did not move it"
