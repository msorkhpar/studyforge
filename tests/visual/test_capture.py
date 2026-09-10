"""Clause 1 — a generated page is rendered in a real browser and captured.

⛔ **The control is the whole of this module's credibility.** A screenshot
harness that has only ever photographed a good page has not been shown to notice
a bad one, and *"the capture succeeded"* is true of a photograph of nothing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.visual import site
from tests.visual.page import SCHEMES, OpenPage

#: The PNG magic number. A capture that is not a PNG is a capture that was not
#: taken, whatever the protocol said.
PNG = b"\x89PNG\r\n\x1a\n"

#: A page of prose at 1280x900 is tens of kilobytes. ⛔ A blank page is about
#: two, which is why the control below asserts a *size*, not a success.
MINIMUM_BYTES = 8_000


@pytest.mark.parametrize("case", site.cases())
@pytest.mark.parametrize("scheme", SCHEMES)
def test_a_generated_page_renders_and_is_captured(
    open_page: OpenPage, built_site: site.Site, capture_dir: Path, case: str, scheme: str
) -> None:
    """Both fixture units, both themes, opened over `file://` and photographed."""
    open_page.open(built_site.url(case), scheme=scheme)
    shot = open_page.capture(capture_dir / f"{case}-{scheme}.png")
    body = shot.read_bytes()
    assert body.startswith(PNG)
    assert len(body) > MINIMUM_BYTES, f"{len(body)} bytes — that is the size of an empty page"
    assert open_page.evaluate("document.title"), "the page rendered with no title"
    painted = open_page.evaluate("document.body.getBoundingClientRect().height")
    assert isinstance(painted, (int, float)) and painted > 400, f"body is {painted}px tall"


@pytest.mark.parametrize("scheme", SCHEMES)
def test_the_two_themes_do_not_produce_the_same_picture(
    open_page: OpenPage, built_site: site.Site, capture_dir: Path, scheme: str
) -> None:
    """⭐ The cheapest possible proof that the theme switch reaches the pixels.

    ⚠️ A harness that emulated `prefers-color-scheme` and had no effect would
    pass every per-theme assertion below it, twice, against the same rendering.
    """
    case = site.cases()[0]
    shots = {}
    for each in SCHEMES:
        open_page.open(built_site.url(case), scheme=each)
        shots[each] = open_page.capture(capture_dir / f"theme-probe-{each}.png").read_bytes()
    assert shots["light"] != shots["dark"], "both themes rendered identically"
    assert scheme in shots


def test_the_capture_notices_a_page_that_renders_nothing(
    open_page: OpenPage, damaged_sites: dict[str, site.Site], capture_dir: Path
) -> None:
    """⛔ Negative control: the `blank` tree must fail the check above.

    A page whose body was emptied still loads, still has a title, and still
    captures cleanly. What it does not have is height or bytes — so this asserts
    the two things that actually separate a rendered page from a photograph of
    the background.
    """
    blank = damaged_sites["blank"]
    open_page.open(blank.url(site.cases()[0]))
    shot = open_page.capture(capture_dir / "control-blank.png").read_bytes()
    assert shot.startswith(PNG), "the control is only a control if the capture itself worked"
    height = open_page.evaluate("document.body.getBoundingClientRect().height")
    assert len(shot) < MINIMUM_BYTES or float(height) < 400, (  # type: ignore[arg-type]
        f"a page with an empty body captured {len(shot)} bytes at {height}px — "
        "this harness cannot tell a rendered page from a blank one"
    )
