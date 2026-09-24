"""`W326` in a real browser: the rail sizes no row of the reading column.

⛔ **A MANY-UNIT container, and that is the whole reason this module exists
beside `test_rail.py`.** `W325` placed the rail at `grid-row: 1` — the masthead's
row — and a grid row is as tall as its tallest item, so the masthead's row became
as tall as the entire course list and every later element of the reading column
began at the rail's bottom edge. ⭐ **A reader opened a unit, saw the title, and
then the height of the rail in blank page.**

⚠️ **It shipped because every fixture was too small to show it.** The gap is
exactly the rail's overhang past the masthead, so it scales with the number of
units the open container declares — and the largest container in any committed
fixture corpus declares three. ⚠️ At that size the overhang reads as spacing in a
capture rather than as a defect, and no clause was taking the reading anyway.
⛔ **So this module WIDENS a fixture corpus** — one container carried out to
`UNITS` units — and takes its readings on a page inside that container, which is
the one page whose disclosure is open and whose rail is therefore at full height.

## ⛔ Every reading is a COMPARISON, and never a number typed here

⚠️ **A pixel figure in this file would be a figure about one font on one host.**
Each clause below opens the SAME built page twice — once as built, once with the
rail region cut out of it — and asserts the reading column is laid out the same
in both. ⭐ That is what *"the masthead's row is sized by the masthead"* means
operationally, and on the tree this row was opened over the two readings differ
by the rail's whole overhang — reported by the failure, never written down here.

⛔ **And it is asserted the other way too**: a third tree is built
with the repaired declaration put back to the one that shipped, and the two
clauses above are asserted to FAIL on it. A control that only ever sees the fixed
stylesheet has not been shown to notice the defect it exists for.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest

from studyforge.generate import read_corpus, unit_location, write_site
from tests.support import repository_root
from tests.visual.page import NARROW, WIDE, OpenPage

#: The fixture corpus this module widens. ⛔ More than one container, because the
#: rail is absent below two and there would be nothing to lay out.
CORPUS = "depth2"

#: How many units the widened container declares. ⚠️ **Not a round number for
#: its own sake**: the rail has to end up TALLER than the masthead's row by more
#: than a subpixel, or the defect and the repair read the same page. ⛔ That the
#: fixture is big enough is ASSERTED rather than assumed, in two places: the
#: clause about the rail running past the masthead, and — the stronger of the
#: two — the control at the foot of this module, which requires the regressed
#: tree to differ from the repaired one by MORE than a subpixel and therefore
#: goes red on a fixture too small to show the defect at all.
UNITS = 16

#: The region under test, spelled as `chrome.css` and `test_rail.py` spell it.
RAIL = 'nav[aria-label="Containers"]'

#: The whole region, for the control that removes it — the same pattern
#: `test_rail.py` strips with, because it is the same control one clause along.
RAIL_REGION = re.compile(r'<nav aria-label="Containers">.*?</nav>\n?', re.DOTALL)

#: The page's aside, cut out by the same control. ⛔ Since `W388` the outline is
#: laid out BESIDE the reading column at this width, so a control that removed
#: the rail alone would leave the compared page with a region in its column that
#: the page under test has beside it — two different columns, compared as one.
OUTLINE_REGION = re.compile(r'<nav aria-label="Outline">.*?</nav>\n?', re.DOTALL)

#: The repaired placement, and the one that shipped. ⛔ The regressed control
#: rewrites the FIRST into the SECOND in a built tree's own stylesheet, so the
#: control is this row's actual defect rather than an impression of it.
REPAIRED = re.compile(r"grid-row:\s*1\s*/\s*span\s+\d+\s*;")
REGRESSED = "grid-row: 1;"

#: How far two readings may differ and still be the same reading, in CSS pixels
#: — the same subpixel allowance `test_rail.TOUCHING` makes.
TOUCHING = 0.5

#: The regions that are laid out BESIDE the reading column rather than in it:
#: the rail on the left, and since `W388` the aside on the right — a unit's
#: outline, the index's explanation. ⛔ Dropped from the population below for one
#: reason: this module is about the ROWS of the reading column, and a region in
#: another column occupies none of them.
BESIDE_THE_COLUMN = ("Containers", "Outline", "About this site")

#: Every laid-out top-level element of the page except those, as
#: `[name, top, height]`. ⛔ `display: none` children are dropped because they
#: are not grid items and occupy no row — the read control ships `hidden`, and a
#: population that counted it would be counting a row that does not exist.
COLUMN = """
(() => {
  const label = el => el.tagName + '[' + (el.getAttribute('aria-label') || el.id || '') + ']';
  const beside = <beside>;
  return Array.from(document.body.children)
    .filter(el => getComputedStyle(el).display !== 'none')
    .filter(el => getComputedStyle(el).position !== 'absolute')
    .filter(el => !beside.includes(el.getAttribute('aria-label')))
    .map(el => { const box = el.getBoundingClientRect();
      return [label(el), box.top, box.height]; });
})()
""".replace("<beside>", json.dumps(list(BESIDE_THE_COLUMN)))


@dataclass(frozen=True)
class WideCorpus:
    """One widened corpus built onto disk, and the page every clause opens."""

    root: Path
    page: Path

    @property
    def url(self) -> str:
        """The `file://` URL of a unit page inside the widened container.

        ⛔ **Inside it, and that is load-bearing.** The rail opens the reader's
        own container and closes the others, so a page in a small container shows
        a short rail and this whole module would measure nothing.
        """
        return "file://" + str(self.page)


def _widen(source: Path, destination: Path) -> str:
    """Copy `source` to `destination` with its largest container carried to `UNITS`.

    ⭐ Returns the address of the container it widened, so the caller can open a
    page inside it. ⛔ Nothing here names a corpus's own subject (R1): the unit it
    adds is titled by its number and its prose is one sentence of filler.

    ⚠️ **The added unit inherits the copied entry's `origin` rather than being
    given one**, and that is deliberate: the shared-origin sweep asserts the tree holds ONE
    reader and one writer of that key, and a fixture builder that wrote it would
    be a second writer nobody declared. ⭐ Nothing here reads the value either —
    the rail is built from titles, and where a unit came from is the placement's
    business and not this module's.
    """
    shutil.copytree(source, destination, dirs_exist_ok=True)
    biggest = max(
        destination.rglob("container.json"),
        key=lambda path: len(json.loads(path.read_text(encoding="utf-8"))["units"]),
    )
    container = json.loads(biggest.read_text(encoding="utf-8"))
    raw = biggest.parent / "raw" / container["variant"]
    pattern = json.loads((sorted(raw.iterdir())[0] / "lesson-1.json").read_text(encoding="utf-8"))
    for number in range(len(container["units"]) + 1, UNITS + 1):
        title = f"Unit number {number}"
        entry = dict(container["units"][-1])
        entry.pop("note", None)
        entry |= {"n": number, "title": title, "practices": 0}
        container["units"].append(entry)
        lesson = dict(pattern) | {
            "unit": number,
            "title": title,
            "blocks": [
                {"type": "heading", "level": 2, "text": title},
                {"type": "para", "text": "One paragraph of prose, so the page has a body."},
            ],
        }
        (raw / f"unit-{number:02d}").mkdir(parents=True, exist_ok=True)
        (raw / f"unit-{number:02d}" / "lesson-1.json").write_text(
            json.dumps(lesson, indent=2), encoding="utf-8"
        )
    biggest.write_text(json.dumps(container, indent=2), encoding="utf-8")
    return "/".join(container["address"])


def _build(root: Path) -> WideCorpus:
    """Widen the fixture corpus under `root` and build the whole site from it."""
    source = root / "source"
    address = _widen(repository_root() / "tests" / "fixtures" / CORPUS, source)
    site = root / "site"
    site.mkdir(parents=True, exist_ok=True)
    write_site(source, site)
    corpus = read_corpus(source)
    inside = [
        unit
        for unit in corpus.units
        if str(unit_location(corpus, unit).page).startswith(address + "/")
    ]
    assert inside, f"nothing was built under the widened container {address}"
    return WideCorpus(root=site, page=site / str(unit_location(corpus, inside[0]).page))


def _strip_rail(built: WideCorpus) -> None:
    """Cut the two regions laid out beside the column out of every page, in place.

    ⭐ What is left is the reading column alone, which is what every clause here
    compares the page beside a rail against.
    """
    for page in sorted(built.root.rglob("*.html")):
        body = page.read_text(encoding="utf-8")
        page.write_text(OUTLINE_REGION.sub("", RAIL_REGION.sub("", body)), encoding="utf-8")


def _regress(built: WideCorpus) -> None:
    """Put the placement `W325` shipped back into a built tree's own stylesheet."""
    sheets = [
        sheet for sheet in sorted(built.root.rglob("*.css")) if REPAIRED.search(sheet.read_text())
    ]
    assert len(sheets) == 1, f"{len(sheets)} built stylesheets place the rail, not one"
    sheets[0].write_text(REPAIRED.sub(REGRESSED, sheets[0].read_text(encoding="utf-8")))


@pytest.fixture(scope="session")
def widened(tmp_path_factory: pytest.TempPathFactory) -> WideCorpus:
    """The widened corpus, built once for the session the way a build builds it."""
    return _build(tmp_path_factory.mktemp("visual-rail-rows"))


@pytest.fixture(scope="session")
def railless(tmp_path_factory: pytest.TempPathFactory) -> WideCorpus:
    """The same tree with the rail cut out — what the reading column looks like alone."""
    built = _build(tmp_path_factory.mktemp("visual-rail-rows-none"))
    _strip_rail(built)
    return built


@pytest.fixture(scope="session")
def regressed(tmp_path_factory: pytest.TempPathFactory) -> WideCorpus:
    """The same tree with `W325`'s placement put back — the defect itself."""
    built = _build(tmp_path_factory.mktemp("visual-rail-rows-regressed"))
    _regress(built)
    return built


@pytest.fixture
def column(open_page: OpenPage) -> Iterator[object]:
    """Read one page's reading column at one width, as `{name: (top, height)}`."""

    def read(built: WideCorpus, width: tuple[int, int]) -> dict[str, tuple[float, float]]:
        open_page.resize(*width)
        open_page.open(built.url, scripts=False)
        found: list = open_page.evaluate(COLUMN)  # type: ignore[assignment]
        return {str(name): (float(top), float(height)) for name, top, height in found}

    yield read


def test_the_mastheads_row_is_sized_by_the_masthead_and_not_by_the_rail(
    column, widened: WideCorpus, railless: WideCorpus
) -> None:
    """⛔ `W326`'s first clause, taken as a comparison and not against a figure.

    ⭐ The masthead is a grid item and stretches to its row, so its own laid-out
    height IS that row's height. ⚠️ On the tree this row was opened over it read
    as the whole course list; the page it is compared against is the same page
    with the region cut out, which is the reading column laid out alone.
    """
    railed = column(widened, WIDE)
    alone = column(railless, WIDE)
    name = next(iter(alone))

    assert railed[name][1] == pytest.approx(alone[name][1], abs=TOUCHING), (
        f"the masthead is {railed[name][1]:.2f}px tall beside the rail and "
        f"{alone[name][1]:.2f}px tall without it, so its row is sized by the rail"
    )


def test_the_reading_column_begins_where_it_does_with_no_rail_at_all(
    column, widened: WideCorpus, railless: WideCorpus
) -> None:
    """⛔ `W326`'s second clause: the element after the masthead has not moved.

    ⚠️ **The element AFTER the masthead**, because the masthead itself starts at
    the top of the page whether the row beneath it is right or wrong — it is the
    thing that follows which the defect pushed down the page.

    ⭐ **Only the first two are compared, and the reason is worth keeping.** A
    grid item stretches to its row and margins between grid items do not collapse,
    so further down the page the two layouts differ for reasons that are grid's
    and not this row's. The defect is about where the reading starts.
    """
    railed = column(widened, WIDE)
    alone = column(railless, WIDE)
    assert len(alone) >= 2, "the page has nothing after its masthead, so this judges nothing"
    name = list(alone)[1]

    assert railed[name][0] == pytest.approx(alone[name][0], abs=TOUCHING), (
        f"{name} begins at {railed[name][0]:.2f}px beside the rail and at "
        f"{alone[name][0]:.2f}px without it, so the rail is pushing the reading down"
    )


def test_the_rail_is_laid_out_at_its_full_height_and_is_not_clipped(
    open_page: OpenPage, widened: WideCorpus
) -> None:
    """⛔ The other way the two clauses above could be made to pass, and it is wrong.

    ⭐ A rail given a height of its own would leave the masthead's row alone and
    the reading column where it belongs, and would hide every course past the
    fold of a box nobody can scroll. ⚠️ So the rail is asserted to be laid out
    WHOLE and to run past the masthead — the shape a span produces and a height
    cannot. ⭐ It is also what says this module's fixture is big enough to be
    measuring anything at all.
    """
    open_page.resize(*WIDE)
    open_page.open(widened.url, scripts=False)
    overflow = open_page.evaluate(
        f"(() => {{ const el = document.querySelector('{RAIL}');"
        " return {hidden: el.scrollHeight - el.clientHeight,"
        "  bottom: el.getBoundingClientRect().bottom,"
        "  masthead: document.querySelector('body > header').getBoundingClientRect().bottom}; })()"
    )
    reading = dict(overflow)  # type: ignore[arg-type]

    assert float(reading["hidden"]) <= TOUCHING, (
        f"{float(reading['hidden']):.2f}px of the course list is clipped out of the rail"
    )
    assert float(reading["bottom"]) > float(reading["masthead"]) + TOUCHING, (
        "the rail ends inside the masthead's own box, so it is not a rail down the "
        "side of the page at all"
    )


def test_the_rail_spans_at_least_as_many_rows_as_the_reading_column_has(
    open_page: OpenPage, widened: WideCorpus
) -> None:
    """⭐ The general statement behind the two comparisons, read off the live layout.

    ⛔ **`1 / -1` does not say this**, which is the measurement that sent this row
    past the repair it was opened with: a negative row line counts back from the
    end of the EXPLICIT grid, and this grid declares columns only. ⚠️ A span
    shorter than the column is the same defect further down the page, and the two
    comparisons above would not see it on a page whose masthead row survived.
    """
    open_page.resize(*WIDE)
    open_page.open(widened.url, scripts=False)
    span = open_page.evaluate(
        f"(() => {{ const end = getComputedStyle(document.querySelector('{RAIL}')).gridRowEnd;"
        " const rows = Array.from(document.body.children)"
        "  .filter(el => getComputedStyle(el).display !== 'none')"
        "  .filter(el => el.getAttribute('aria-label') !== 'Containers').length;"
        " return {end: end, rows: rows}; })()"
    )
    reading = dict(span)  # type: ignore[arg-type]
    declared = re.search(r"span\s+(\d+)", str(reading["end"]))

    assert declared, f"the rail spans no rows at all: grid-row-end is {reading['end']!r}"
    assert int(declared.group(1)) >= int(reading["rows"]), (
        f"the rail spans {declared.group(1)} rows and the reading column has "
        f"{reading['rows']}, so the rows past the span are sized by the rail"
    )


def test_at_the_narrow_width_the_rail_is_still_the_card_above_the_reading_surface(
    open_page: OpenPage, column, widened: WideCorpus, railless: WideCorpus
) -> None:
    """⛔ `W325`'s degradation, re-taken over a container this large.

    ⚠️ **The comparison the wide clauses make is NOT made here, and saying why is
    the point.** At this width the rail is back in the one column, above the
    reading surface — so the elements below it are SUPPOSED to move, and a page
    with the region cut out is a different reading column, not a control. ⭐ What
    is still comparable is the masthead, which nothing at this width may size.
    """
    open_page.resize(*NARROW)
    open_page.open(widened.url, scripts=False)
    boxes = open_page.evaluate(
        f"(() => {{ const at = s => document.querySelector(s).getBoundingClientRect();"
        f" const rail = at('{RAIL}'), main = at('main#content');"
        " return {bottom: rail.bottom, width: rail.width,"
        "  top: main.top, column: main.width}; })()"
    )
    reading = dict(boxes)  # type: ignore[arg-type]

    assert float(reading["bottom"]) <= float(reading["top"]) + TOUCHING, (
        f"at {NARROW[0]}px the rail ends at {float(reading['bottom']):.2f}px and the reading "
        f"surface starts at {float(reading['top']):.2f}px, so it is beside the prose"
    )
    assert float(reading["width"]) == pytest.approx(float(reading["column"]), abs=TOUCHING), (
        f"at {NARROW[0]}px the rail is {float(reading['width']):.2f}px against the column's "
        f"{float(reading['column']):.2f}px, so it has a measure of its own"
    )
    railed = column(widened, NARROW)
    alone = column(railless, NARROW)
    masthead = next(iter(alone))
    assert railed[masthead][1] == pytest.approx(alone[masthead][1], abs=TOUCHING), (
        f"at {NARROW[0]}px the masthead is {railed[masthead][1]:.2f}px tall beside the "
        f"region and {alone[masthead][1]:.2f}px tall without it"
    )


def test_both_wide_clauses_fail_on_a_tree_whose_placement_is_the_one_that_shipped(
    column, regressed: WideCorpus, railless: WideCorpus
) -> None:
    """⛔ The negative control, and the answer to *why did the arms already here not catch it*.

    ⭐ **The tree is the real one and the defect is the real one**: the same build,
    with the rail's placement rewritten in its own stylesheet back to the single
    row `W325` merged. ⚠️ Both clauses are asserted to go RED on it — not one —
    because either alone has a passing shape that is not the repair.
    """
    broken = column(regressed, WIDE)
    alone = column(railless, WIDE)
    names = list(alone)

    assert abs(broken[names[0]][1] - alone[names[0]][1]) > TOUCHING, (
        "the masthead is the same height under the placement that shipped, so the "
        "first clause would pass over the defect it exists for"
    )
    assert abs(broken[names[1]][0] - alone[names[1]][0]) > TOUCHING, (
        "the element after the masthead is in the same place under the placement "
        "that shipped, so the second clause would pass over the defect it exists for"
    )
