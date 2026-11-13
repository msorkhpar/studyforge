"""A ```mermaid fence is drawn as an SVG in Chrome, from `file://`, themed from the palette.

⭐ The corpus is `depth1`, copied, with one lesson given two diagrams: one Mermaid draws and one it
refuses. Opened as a file the page draws the first in place, hides its source, asks for nothing
beyond the files beside it (R8), and draws it again in the other theme's tokens when the reader
switches; the refused one keeps its source on the page.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

import pytest

from studyforge.archive.blocks import counts_of
from studyforge.archive.document import content_sha256, render
from studyforge.generate import write_site
from tests.studyforge.exercise.quiz.depth1 import fixture_root
from tests.visual.page import OpenPage

LESSON = Path("archive/depth-one/raw/prose/unit-01/lesson-1.json")
DRAWN = "graph LR\n  Terminal --> Switch --> Host"
REFUSED = "graph LR\n  A -->"
SETTLE = 10.0

READ = """
(() => Array.from(document.querySelectorAll('figure[data-frame="diagram"]')).map((f) => {
  const node = f.querySelector('[data-diagram-drawing] svg .node rect');
  return {
    drawn: f.hasAttribute('data-drawn'),
    svg: !!f.querySelector('[data-diagram-drawing] svg'),
    source: getComputedStyle(f.querySelector('pre')).display !== 'none',
    fill: node ? getComputedStyle(node).fill : null,
    bg: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim(),
  };
}))()
"""


@pytest.fixture(scope="module")
def page_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    root = tmp_path_factory.mktemp("diagram-site") / "depth1"
    shutil.copytree(fixture_root(), root)
    document = json.loads((root / LESSON).read_text(encoding="utf-8"))
    document["blocks"] += [
        {"type": "code", "lang": "mermaid", "text": DRAWN},
        {"type": "code", "lang": "mermaid", "text": REFUSED},
    ]
    document["counts"] = counts_of(document["blocks"])
    document["content_sha256"] = content_sha256(document["blocks"])
    (root / LESSON).write_text(render(document), encoding="utf-8")
    write_site(root, root)
    (page,) = [
        path
        for path in (root / ".studyforge").rglob("*.unit.html")
        if 'data-frame="diagram"' in path.read_text(encoding="utf-8")
    ]
    return page.as_uri()


def _until(page: OpenPage, ready, what: str) -> list:
    deadline = time.monotonic() + SETTLE
    reading = list(page.evaluate(READ))  # type: ignore[call-overload]
    while time.monotonic() < deadline:
        if ready(reading):
            return reading
        time.sleep(0.05)
        reading = list(page.evaluate(READ))  # type: ignore[call-overload]
    raise AssertionError(f"the diagram never {what}; it reads {reading}")


def test_a_diagram_is_drawn_in_place_from_a_file_and_redrawn_in_the_other_theme(
    open_page: OpenPage, page_url: str, capture_dir: Path
) -> None:
    open_page.resize(1280, 900)
    open_page.open(page_url, scheme="light")
    light = _until(open_page, lambda r: len(r) == 2 and r[0]["drawn"], "drew")
    assert light[0]["svg"] and not light[0]["source"]
    assert not light[1]["drawn"] and not light[1]["svg"] and light[1]["source"]
    assert light[0]["fill"] and light[0]["fill"] != "none"
    asked = open_page.requests()
    assert any(url.endswith("mermaid.min.js") for url in asked)
    assert all(url.startswith(("file://", "data:")) for url in asked), asked
    open_page.capture(capture_dir / "diagram-light.png")

    open_page.evaluate("document.documentElement.setAttribute('data-theme', 'dark'); true")
    dark = _until(
        open_page,
        lambda r: r[0]["fill"] not in (None, light[0]["fill"]),
        "was drawn again in the dark theme's tokens",
    )
    assert dark[0]["drawn"] and dark[0]["bg"] != light[0]["bg"]
    open_page.capture(capture_dir / "diagram-dark.png")
