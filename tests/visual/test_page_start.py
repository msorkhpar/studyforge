"""`W333` in a real browser: the index and a unit page start in the same place.

⛔ **THE ROW IS A CROSSING, AND THAT IS WHY IT NEEDS TWO PAGES AT ONE VIEWPORT.**
Every clause the package already carries reads ONE page — the rail's edge, the
rail's scroll, the column's share, the row the masthead sizes. ⭐ **The defect
here is invisible to all of them, because each of the two pages is defensible
alone:** `W328` made the page WITH a rail flush left and wide, and the page
WITHOUT one — the root index, whose own body IS the tree — kept the centred,
measure-derived cap the column section declares. ⛔ **A reader clicking a unit
out of the index saw the whole page slide to the left edge and widen, and the
wider they had opened the window the further it slid.**

## ⛔ Which box each reading measured is named in the reading itself

⚠️ **A probe that does not say what it measured gets misread.** Every
rectangle below is `getBoundingClientRect()` — the **border box**, in **viewport**
coordinates. ⭐ The three readings that are not rectangles say so: the computed
`margin-left`, `padding-left` and `display` of `body`, which are strings out of
`getComputedStyle` and are asserted BEFORE any geometry is believed.

## ⛔ The computed style is read first, and why

⚠️ **A probe that establishes a state by script and then measures it can certify
something the reader never gets.** ⭐ Nothing here drives the page: every check
opens a built file with **scripts disabled** and reads it. The computed
declarations are asserted first all the same, so a geometry reading that happened
to agree for some other reason cannot stand in for the rule that should have
produced it.

## ⛔ Never against a number this module typed

⚠️ The settling clause is *"a reader crossing between the two page kinds sees no
jump in where the content starts"*, and it is asserted as a **comparison between
two real pages of one built site at one viewport** — and, for the half that says
it is a shape rather than a coincidence of one width, as the same comparison
repeated at three. ⛔ No layout figure is written down here. ⚠️ **Since `W388`
stage 4 the shell is CENTRED above a ceiling**, so a clause that read one page
against ITSELF at two widths would now be asserting that the page never moves —
which is a different row's claim and one this row's own title never made.

## ⛔ Asserted the other way, on the shape that shipped

⚠️ A control that has only ever seen the repaired stylesheet has not been shown
to notice the defect it exists for. ⭐ A second tree is built with
this row's one rule cut back out of its own generated stylesheet; the settling
clauses are asserted to FAIL on it, and the narrow readings are asserted to be
IDENTICAL on it — which is how *"the narrow page is unchanged"* is measured
rather than promised.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest

from studyforge.generate import read_corpus, unit_location, write_site
from tests.support import repository_root
from tests.visual.page import NARROW, WIDE, OpenPage

#: The fixture corpus this module builds. ⛔ More than one container, because the
#: rail is absent below two and the site would then have only one page kind —
#: which is a corpus this row cannot be exhibited on at all.
CORPUS = "depth2"

#: The fixture corpus whose pages carry NO rail. ⛔ Since `W388` the root index
#: carries one too, so the page kind this row's second half is about — a page the
#: wide shape does not lay out as a grid — is only produced by a corpus with ONE
#: container, where the rail is below `RAIL_MINIMUM` and no page has it.
RAILLESS_CORPUS = "depth1"

#: The region whose presence tells the two page kinds apart, as `chrome.css` and
#: `test_rail.py` spell it.
RAIL = 'nav[aria-label="Containers"]'

#: How far two readings may differ and still be the same reading, in CSS pixels
#: — the same subpixel allowance `test_rail.TOUCHING` makes.
TOUCHING = 0.5

#: A second wide viewport, far wider than `WIDE` and past the ceiling the wide
#: shape declares. ⭐ **The defect GREW with the window** — that is what made it
#: a layout that moves rather than an offset somebody could learn — so a single
#: wide reading would have been the weakest point on the curve.
WIDER = (2560, WIDE[1])

#: This row's whole product change, as it stands in the generated stylesheet.
#: ⛔ The control cuts exactly this out of a BUILT tree, so what the clauses are
#: refuted against is the layout that actually shipped.
SHIPPED_WITHOUT = (
    '  body:not(:has(nav[aria-label="Containers"])) {\n'
    "    margin-left: max(0px, (100% - var(--page-max)) / 2);\n  }\n\n",
    "",
)

#: One page's layout, in the vocabulary the clauses are written in. ⛔ Every
#: rectangle is a BORDER BOX in viewport coordinates; the three computed
#: declarations are strings and are named for what they are.
GEOMETRY = """
(() => {
  const at = s => { const el = document.querySelector(s); if (!el) return null;
    const b = el.getBoundingClientRect();
    return {left: b.left, right: b.right, width: b.width}; };
  const computed = getComputedStyle(document.body);
  return {
    'body border box': at('body'),
    'masthead border box': at('body > header'),
    'reading surface border box': at('main#content'),
    'rail border box': at('<rail>'),
    'body computed margin-left': computed.marginLeft,
    'body computed padding-left': computed.paddingLeft,
    'body computed display': computed.display,
    'window inner width': window.innerWidth,
  };
})()
""".replace("<rail>", RAIL)


@dataclass(frozen=True)
class Crossing:
    """Two built sites: the pages a reader crosses between, and a page with no rail.

    ⚠️ `railless` is a page of a ONE-container corpus (`W388`): a build of this
    module's own corpus now gives every page kind a rail, including the index,
    so the railless shape has to be exhibited on a corpus that has no crossing
    to offer rather than on the index.
    """

    root: Path
    index: Path
    unit: Path
    container: Path
    railless: Path
    railless_root: Path

    def url(self, page: Path) -> str:
        """The `file://` URL of one page in this tree."""
        return "file://" + str(page)


def _build(root: Path) -> Crossing:
    """Build the committed fixture corpus the way a build builds it.

    ⛔ **`write_site` and not the page fixtures.** The two kinds this row is
    about are told apart by whether the renderer was handed a rail, and only a
    real build decides that — measured: the harness's own
    container fixtures render WITHOUT one while a build gives every container
    page a rail, so a tree assembled from them would have disagreed with the site
    a reader opens about which pages this row even touches.

    ⚠️ The corpus is copied before it is read, so nothing is written into the
    repository's own fixtures by a test run.
    """
    source = root / "source"
    shutil.copytree(repository_root() / "tests" / "fixtures" / CORPUS, source)
    site = root / "site"
    site.mkdir(parents=True, exist_ok=True)
    write_site(source, site)
    corpus = read_corpus(source)
    unit = max(
        (site / str(unit_location(corpus, each).page) for each in corpus.units),
        key=lambda page: page.stat().st_size,
    )
    index = site / str(corpus.shared.root_index)
    containers = sorted(page for page in site.rglob("*.section.html"))
    assert index.exists(), "the build wrote no root index, so there is no crossing to measure"
    assert containers, "the build wrote no container page"
    alone_source = root / "railless-source"
    shutil.copytree(repository_root() / "tests" / "fixtures" / RAILLESS_CORPUS, alone_source)
    alone = root / "railless"
    alone.mkdir(parents=True, exist_ok=True)
    write_site(alone_source, alone)
    railless = alone / str(read_corpus(alone_source).shared.root_index)
    assert railless.exists(), "the one-container build wrote no root index"
    return Crossing(
        root=site,
        index=index,
        unit=unit,
        container=containers[0],
        railless=railless,
        railless_root=alone,
    )


def _revert(built: Crossing) -> None:
    """Cut this row's one rule back out of both built trees' own stylesheets.

    ⚠️ Both, since `W388`: the control compares the railless corpus's page with
    this corpus's unit page, and a rule cut out of one tree only would be a
    comparison between the shape that shipped and the shape that did not.
    """
    for root in (built.root, built.railless_root):
        sheets = [
            sheet
            for sheet in sorted(root.rglob("*.css"))
            if SHIPPED_WITHOUT[0] in sheet.read_text(encoding="utf-8")
        ]
        assert len(sheets) == 1, f"{len(sheets)} built stylesheets carry this row's rule, not one"
        written = sheets[0].read_text(encoding="utf-8")
        assert written.count(SHIPPED_WITHOUT[0]) == 1, "the rule is written more than once"
        sheets[0].write_text(written.replace(*SHIPPED_WITHOUT), encoding="utf-8")


@pytest.fixture(scope="session")
def crossing(tmp_path_factory: pytest.TempPathFactory) -> Crossing:
    """The built site, written once for the session the way a build writes it."""
    return _build(tmp_path_factory.mktemp("visual-page-start"))


@pytest.fixture(scope="session")
def as_shipped(tmp_path_factory: pytest.TempPathFactory) -> Crossing:
    """The same site with this row's rule removed — the defect itself."""
    built = _build(tmp_path_factory.mktemp("visual-page-start-shipped"))
    _revert(built)
    return built


@pytest.fixture
def layout(open_page: OpenPage) -> Iterator[object]:
    """Open one built page at one width, scripts OFF, and read its boxes back."""

    def read(page: Path, width: tuple[int, int]) -> dict:
        open_page.resize(*width)
        open_page.open("file://" + str(page), scripts=False)
        return dict(open_page.evaluate(GEOMETRY))  # type: ignore[arg-type]

    yield read


# --- the fixture is a site whose two page kinds really do differ ------------


def test_the_two_page_kinds_this_row_is_about_are_both_in_the_built_tree(
    layout, crossing: Crossing
) -> None:
    """⛔ A fixture too small to exhibit the defect is how `W326` shipped.

    ⭐ What makes this one big enough is not a unit count: it is that the build
    emits BOTH shapes — a page the wide rule lays out as a grid beside a rail,
    and a page with no rail at all — and that the wide shape is actually in force
    at the width the clauses are taken at. ⚠️ Asserted, so a corpus that stopped
    producing one of them reds here rather than passing every comparison below
    over two copies of one layout.
    """
    unit = layout(crossing.unit, WIDE)
    index = layout(crossing.index, WIDE)
    alone = layout(crossing.railless, WIDE)

    assert unit["rail border box"] is not None, (
        "the unit page carries no rail, so this corpus has only one page shape "
        "and there is no crossing to measure"
    )
    assert unit["body computed display"] == "grid", (
        "the unit page is not in the two-column shape at the wide width, so the "
        f"rule this row sits beside is not in force: {unit['body computed display']}"
    )
    assert index["rail border box"] is not None, (
        "the root index of a corpus with two containers carries no rail, which "
        "`W388` says it must: the reader's left menu is gone from the first page"
    )
    assert alone["rail border box"] is None, (
        "the one-container corpus's page carries a rail, so this tree holds no "
        "railless page kind and the clauses below judge one shape twice"
    )
    assert alone["body computed display"] != "grid", (
        "the page with no rail is laid out as a grid, so it has reserved a track "
        f"for a rail it does not carry: {alone['body computed display']}"
    )


def test_a_container_page_carries_the_rail_so_the_index_is_the_page_this_row_moves(
    layout, crossing: Crossing
) -> None:
    """⭐ The scope of the change, read off the built tree rather than assumed.

    ⚠️ **`generate.containers` hands every container page a rail**, so in a real
    build of a corpus with two containers or more the root index is the ONLY page
    without one. ⛔ That is asserted here because the visual package's own
    container fixtures render without a rail, and a reader of this
    module would otherwise have two incompatible answers to *which pages does
    this row move*.
    """
    container = layout(crossing.container, WIDE)

    assert container["rail border box"] is not None, (
        "a built container page carries no rail, so this row moves more page "
        "kinds than the index and its clauses are measured on the wrong pair"
    )


# --- the settling clause: no jump in where the content starts ---------------


def test_the_computed_left_margin_is_the_same_on_both_page_kinds(
    layout, crossing: Crossing
) -> None:
    """⛔ The DECLARATION first, before any geometry is believed.

    ⭐ Read off the live cascade on both pages and compared with each other, so a
    rule that stopped applying — a renamed region, a selector a browser dropped —
    reds here by name rather than surfacing as a rectangle that moved for reasons
    nobody can see.
    """
    unit = layout(crossing.unit, WIDE)
    index = layout(crossing.index, WIDE)

    assert index["body computed margin-left"] == unit["body computed margin-left"], (
        "the two page kinds resolve different left margins on `body`: the index "
        f"{index['body computed margin-left']}, a unit page "
        f"{unit['body computed margin-left']}"
    )


def test_the_index_and_a_unit_page_start_in_the_same_place(layout, crossing: Crossing) -> None:
    """⛔ The row, as a comparison between two real pages at one viewport.

    ⭐ **`body`'s border box left edge**, on the page a reader leaves and the page
    they arrive at. ⚠️ Never against a number typed here: a site that moved both
    page kinds somewhere else together still passes, and that is the claim —
    *the layout does not move when the reader clicks*.
    """
    unit = layout(crossing.unit, WIDE)
    index = layout(crossing.index, WIDE)

    assert index["body border box"]["left"] == pytest.approx(
        unit["body border box"]["left"], abs=TOUCHING
    ), (
        "the page jumps when a reader clicks from the index into a unit: `body`'s "
        f"border box left edge reads {index['body border box']['left']} on the "
        f"index and {unit['body border box']['left']} on the unit page, at "
        f"{index['window inner width']}px"
    )


def test_they_still_start_in_the_same_place_on_a_much_wider_screen(
    layout, crossing: Crossing
) -> None:
    """⚠️ **The defect GREW with the window**, so one wide reading is the weakest one.

    ⭐ The same comparison at a viewport past the ceiling the wide shape declares:
    a repair that merely happened to line the two pages up at one width reds here.
    """
    unit = layout(crossing.unit, WIDER)
    index = layout(crossing.index, WIDER)

    assert index["body border box"]["left"] == pytest.approx(
        unit["body border box"]["left"], abs=TOUCHING
    ), (
        "the two page kinds agree at one width and not at another, so where a "
        f"page starts is still a function of the window: the index reads "
        f"{index['body border box']['left']} and the unit page "
        f"{unit['body border box']['left']} at {index['window inner width']}px"
    )


def test_the_page_with_no_rail_starts_where_the_page_with_one_starts_at_every_width(
    layout, crossing: Crossing
) -> None:
    """⛔ The same comparison as above, at three widths instead of one.

    ⭐ This is the half that says the repair is a shape rather than a coincidence
    of one viewport: before this row the index's left edge was a function of the
    viewport while a unit page's was not, so a reader who widened their window
    watched one of the two page kinds walk away from the other.

    ⛔ **`W388` STAGE 4 RESTATED THIS CLAUSE AND THE RESTATEMENT IS STRICTLY
    STRONGER.** It read *"the page with no rail does not MOVE when the window
    widens"*, compared with itself — which was a PROXY for the row's real clause
    and was only ever equivalent to it while the page with a rail was pinned to
    the window's left edge. ⚠️ The shell is bounded and centred now, on the
    user's instruction (*"if the display is too big having the menu and content
    in the middle"*), so above the ceiling BOTH kinds move — together, which is
    the thing this row is about. ⭐ Compared with the other page kind at each
    width, the clause says what its own title says and cannot be satisfied by a
    page that simply never moves.
    """
    for name, width in (("the narrow width", NARROW), ("the wide width", WIDE), ("wider", WIDER)):
        railless = layout(crossing.railless, width)
        unit = layout(crossing.unit, width)
        assert railless["body border box"]["left"] == pytest.approx(
            unit["body border box"]["left"], abs=TOUCHING
        ), (
            f"the two page kinds start in different places at {name}: `body`'s "
            f"border box left edge reads {railless['body border box']['left']} with no "
            f"rail and {unit['body border box']['left']} with one, at "
            f"{railless['window inner width']}px"
        )


def test_the_content_of_the_page_with_no_rail_starts_where_it_always_did(
    layout, crossing: Crossing
) -> None:
    """⭐ The gutter survives, asserted as the page against itself across the threshold.

    ⛔ The two-column page gives up its left gutter because the RAIL is what sits
    at the window's edge. A page with nothing to put there must keep it, or its
    masthead runs into the screen. ⚠️ Asserted as a comparison with the same
    page's NARROW reading — where the one shape this file has below its threshold
    already keeps that gutter — so no inset is written down here.
    """
    narrow = layout(crossing.railless, NARROW)
    wide = layout(crossing.railless, WIDE)

    assert wide["body computed padding-left"] == narrow["body computed padding-left"], (
        "the page with no rail resolves a different left gutter above the "
        f"threshold: {wide['body computed padding-left']} against "
        f"{narrow['body computed padding-left']}"
    )
    assert wide["masthead border box"]["left"] == pytest.approx(
        narrow["masthead border box"]["left"], abs=TOUCHING
    ), (
        "the masthead of the page with no rail starts somewhere else above the "
        f"threshold: {wide['masthead border box']['left']} against "
        f"{narrow['masthead border box']['left']}"
    )


def test_the_page_with_no_rail_reserves_no_track_for_the_rail_it_does_not_carry(
    layout, crossing: Crossing
) -> None:
    """⛔ The shape this row refused, asserted rather than left in prose.

    ⚠️ Lining the index's masthead up with a unit page's would have meant giving
    the index the rail's empty column — which `chrome.css`'s `:has()` condition
    exists to prevent, and which would make the index's own content jump by a
    rail's width as the reader widened the window: this row's defect moved from
    the click to the resize. ⭐ The computed `display` and the computed gutter are
    both read, because the track and the inset are two different ways to get it.
    """
    wide = layout(crossing.railless, WIDE)

    assert wide["body computed display"] != "grid", (
        "the page with no rail is laid out as a grid, so it has reserved a track "
        "for a rail it does not carry"
    )
    assert wide["body computed padding-left"] != "0px", (
        "the page with no rail has given up its left gutter, so its masthead "
        "runs into the edge of the screen and no rail is there to earn the inset"
    )


# --- the negative control: the clauses go red on the shape that shipped -----


def test_the_settling_clause_fails_on_the_shape_that_shipped(layout, as_shipped: Crossing) -> None:
    """⛔ The control, and it is this row's ACTUAL defect rather than an impression.

    ⭐ The same build with this row's one rule cut out of its generated
    stylesheet: the two page kinds must then disagree about where the page starts,
    at BOTH wide widths, and the disagreement must be larger at the wider one —
    which is the property that made this a layout that moves rather than an offset
    a reader could learn.
    """
    gaps = []
    for width in (WIDE, WIDER):
        unit = layout(as_shipped.unit, width)
        alone = layout(as_shipped.railless, width)
        gaps.append(alone["body border box"]["left"] - unit["body border box"]["left"])

    assert all(gap > TOUCHING for gap in gaps), (
        "the two page kinds already agree without this row's rule, so the "
        f"control is not the defect this module exists for: {gaps}"
    )
    assert gaps[1] > gaps[0], (
        "the disagreement does not grow with the window on the shape that "
        f"shipped, so the control is not the layout this row was opened over: {gaps}"
    )


def test_the_narrow_page_is_the_same_layout_it_was_before_this_row(
    layout, crossing: Crossing, as_shipped: Crossing
) -> None:
    """⛔ Settling clause 2, measured rather than promised.

    ⚠️ *"Below the threshold there is only one shape, and that must STAY true; a
    fix that changes the narrow page has broken something."* ⭐ So the narrow
    readings are taken on BOTH trees — the one this row ships and the one with its
    rule cut out — and asserted identical, on both page kinds. A rule that had
    leaked out of the threshold reds here.
    """
    for name, before, after in (
        ("the index", as_shipped.index, crossing.index),
        ("a unit page", as_shipped.unit, crossing.unit),
    ):
        was = layout(before, NARROW)
        now = layout(after, NARROW)
        assert now["body computed margin-left"] == was["body computed margin-left"], (
            f"{name} resolves a different left margin at the narrow width: "
            f"{now['body computed margin-left']} against {was['body computed margin-left']}"
        )
        for box in ("body border box", "masthead border box", "reading surface border box"):
            assert now[box]["left"] == pytest.approx(was[box]["left"], abs=TOUCHING), (
                f"{name}'s {box} starts somewhere else at the narrow width: "
                f"{now[box]['left']} against {was[box]['left']}"
            )
            assert now[box]["width"] == pytest.approx(was[box]["width"], abs=TOUCHING), (
                f"{name}'s {box} is a different width at the narrow width: "
                f"{now[box]['width']} against {was[box]['width']}"
            )
