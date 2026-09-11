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
#:
#: ⭐ **Deliberately LOOSE, and Ruling 236 is why that is stated here rather than
#: left to be inferred.** A capture's size is a text-layout output and text layout
#: is a font metric. ⭐ **`fonts-liberation` is now pinned by version AND checksum
#: in `docker/dev/Dockerfile` (`W124` landed), so the font is no longer an
#: undeclared input** — ⛔ **but the looseness below stays, and stating it is still
#: required: a pin records which face arrives, and it does not make a threshold
#: that was chosen loosely into a tight one.** ⚠️ The pin is what a *recorded px*
#: assertion would have needed; these two figures never did, and the reason is the
#: margin. ⛔ **The figure is
#: unchanged and its MARGIN is not, because `W98` widened the population:** the
#: CTO measured `45k – 112k` over two unit pages and a margin of `5.7x`; over
#: seven pages of three kinds the same threshold reads **20 296 – 122 397** bytes,
#: so the nearest margin is **2.54x**. ⭐ The blank control captures **5 293**
#: bytes, which is 1.51x under this line — a metric-compatible font moves line
#: heights by percents and cannot carry a reading across either gap.
MINIMUM_BYTES = 8_000

#: The height a real rendering of each page kind clears and a blank one cannot.
#:
#: ⛔ **Per kind since `W98`, and the reason is a measurement rather than taste.**
#: The single `400` this replaces was a unit-page number, and the clause's
#: population is now every page kind: a container page is a title, a note and a
#: list of units, and a root index is a disclosure tree — both are legitimately
#: short, and a threshold that reds on a correct short page is a threshold that
#: would be "fixed" by narrowing the population back.
#:
#: ⛔ **No threshold here is TIGHTER than the one it replaces.** `400` survives
#: unchanged as the unit floor — which is the figure Ruling 236 examined — and the
#: two rows beside it are LOOSER floors for two kinds that were never photographed
#: before. ⚠️ Tightening one of these would be a different act from widening the
#: harness, and `W98` did not perform it.
#:
#: ⭐ **Loose on purpose, and stated as Ruling 236 requires.** Measured in the
#: pinned image at `f71c566`, viewport 1280x900, every reading printed:
#: unit **960 / 2 212 px**, container **387 / 434 / 466 px**, index
#: **303 / 529 px**. Margins: unit **2.40x** (wider than the 1.87x the CTO
#: measured, because a populated bar and a practice panel are new height),
#: container **2.58x**, index **2.02x**. ⛔ The nearest is the index's **2.02x**,
#: and the blank control renders at **0 px** on every kind — so no font can carry
#: a blank page over any row here, and none can carry a real one under it.
MINIMUM_HEIGHT = {site.UNIT: 400, site.CONTAINER: 150, site.INDEX: 150}


def test_every_kind_this_clause_photographs_has_a_declared_floor() -> None:
    """⛔ `MINIMUM_HEIGHT` is total over the kinds the harness writes, both ways.

    ⚠️ A `KeyError` would be a loud failure and a *missing* row would not: the
    defect this forbids is a fourth page kind arriving and being photographed
    against whatever row happened to be nearest.
    """
    assert sorted(MINIMUM_HEIGHT) == sorted(site.kinds()), (
        f"floors declared for {sorted(MINIMUM_HEIGHT)}, harness writes {sorted(site.kinds())}"
    )


@pytest.mark.parametrize("case", site.pages())
@pytest.mark.parametrize("scheme", SCHEMES)
def test_a_generated_page_renders_and_is_captured(
    open_page: OpenPage, built_site: site.Site, capture_dir: Path, case: str, scheme: str
) -> None:
    """Every page kind, both themes, opened over `file://` and photographed."""
    open_page.open(built_site.url(case), scheme=scheme)
    shot = open_page.capture(capture_dir / f"{case}-{scheme}.png")
    body = shot.read_bytes()
    assert body.startswith(PNG)
    assert len(body) > MINIMUM_BYTES, f"{len(body)} bytes — that is the size of an empty page"
    assert open_page.evaluate("document.title"), "the page rendered with no title"
    floor = MINIMUM_HEIGHT[built_site.kind(case)]
    painted = open_page.evaluate("document.body.getBoundingClientRect().height")
    assert isinstance(painted, (int, float)) and painted > floor, (
        f"body is {painted}px tall, and a rendered {built_site.kind(case)} page clears {floor}"
    )


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


@pytest.mark.parametrize("case", site.pages())
def test_the_capture_notices_a_page_that_renders_nothing(
    open_page: OpenPage, damaged_sites: dict[str, site.Site], capture_dir: Path, case: str
) -> None:
    """⛔ Negative control: the `blank` tree must fail the check above.

    A page whose body was emptied still loads, still has a title, and still
    captures cleanly. What it does not have is height or bytes — so this asserts
    the two things that actually separate a rendered page from a photograph of
    the background.

    ⭐ **Run on every page kind, because the floors are now per kind** (`W98`): a
    control taken on one kind says nothing about whether the lowest floor still
    separates a rendering from a blank page.
    """
    blank = damaged_sites["blank"]
    open_page.open(blank.url(case))
    shot = open_page.capture(capture_dir / f"control-blank-{case}.png").read_bytes()
    assert shot.startswith(PNG), "the control is only a control if the capture itself worked"
    floor = MINIMUM_HEIGHT[blank.kind(case)]
    height = open_page.evaluate("document.body.getBoundingClientRect().height")
    assert len(shot) < MINIMUM_BYTES or float(height) < floor, (  # type: ignore[arg-type]
        f"a page with an empty body captured {len(shot)} bytes at {height}px against a "
        f"floor of {floor} — this harness cannot tell a rendered page from a blank one"
    )
