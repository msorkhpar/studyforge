"""A lesson's example runs its test from a Run strip, on a SERVED origin, and not over file://.

⭐ The corpus is the course shape's source tree, built: its conversation example names the file each
tab is, and a test stands beside each, so the build draws a strip under the tab. Served with a
runner up, the strip shows and a press streams the run's output into the block; opened as a file, it
stays hidden and the page names no API (R8).
"""

from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.fixtures.claude_shape import course
from tests.visual import served
from tests.visual.page import OpenPage

PAGE = ".studyforge/level-1/01-messages/units/unit-01/unit-01-reading-a-conversation.unit.html"
SETTLE = 10.0

STRIP = """
(() => {
  const strip = document.querySelector('p[data-example-run]');
  const part = (name) => strip && strip.querySelector('[data-example-part="' + name + '"]');
  const out = strip && strip.nextElementSibling;
  return {
    strips: document.querySelectorAll('p[data-example-run]').length,
    shown: !!strip && strip.checkVisibility(),
    status: part('status') ? part('status').textContent.trim() : null,
    output: out ? out.textContent : null,
    outputShown: !!out && out.checkVisibility(),
  };
})()
"""


@pytest.fixture(scope="module")
def shape(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("shape-site") / "shape"
    from studyforge.generate import write_site

    course.write_source(root)
    course.write_archive(root)
    write_site(root, root)
    return root


def _until(page: OpenPage, ready, what: str) -> dict:
    deadline = time.monotonic() + SETTLE
    reading = dict(page.evaluate(STRIP))  # type: ignore[call-overload]
    while time.monotonic() < deadline:
        if ready(reading):
            return reading
        time.sleep(0.05)
        reading = dict(page.evaluate(STRIP))  # type: ignore[call-overload]
    raise AssertionError(f"the strip never {what}; it reads {reading}")


def test_a_served_strip_runs_the_test_and_shows_its_output_beside_the_code(
    open_page: OpenPage, shape: Path, capture_dir: Path
) -> None:
    built = SimpleNamespace(root=shape.parent)
    with served.serving(built, shape.name, windows=True) as origin:
        open_page.resize(1280, 800)
        open_page.open(f"{origin.origin}/{PAGE}")
        # ⭐ A first visit is asked which language to read in; the reader answers before the page.
        open_page.evaluate(
            "(() => { const pick = Array.from("
            "document.querySelectorAll('dialog button, [role=dialog] button'))"
            ".find((b) => b.textContent.includes('Read in Python'));"
            " if (pick) pick.click(); return true; })()"
        )
        reading = _until(open_page, lambda r: r["shown"], "was shown beside the code")
        assert reading["strips"] >= 1 and reading["status"] in ("", None) or reading["shown"]
        open_page.evaluate("document.querySelector('[data-example-act=\"run\"]').click(); true")
        origin.runs.started.wait(timeout=SETTLE)
        origin.runs.release.set()
        reading = _until(open_page, lambda r: r["status"] == "Passed.", "reported the verdict")
        assert reading["outputShown"] and served.SCRIPTED[-1] in reading["output"]
        open_page.evaluate(
            "document.querySelector('p[data-example-run]')"
            ".scrollIntoView({block: 'center', behavior: 'instant'}); true"
        )
        time.sleep(0.5)
        open_page.capture(capture_dir / "example-run.png", whole=False)


def test_over_a_file_the_strip_stays_hidden_and_asks_nothing(
    open_page: OpenPage, shape: Path
) -> None:
    open_page.open("file://" + str(shape / PAGE))
    reading = dict(open_page.evaluate(STRIP))  # type: ignore[call-overload]
    assert reading["strips"] >= 1 and not reading["shown"]
    assert not [url for url in open_page.requests() if "/api/" in url]
