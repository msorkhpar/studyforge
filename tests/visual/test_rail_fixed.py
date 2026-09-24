"""`W328` in a real browser: the rail is flush left and fixed, and the column uses the page.

⛔ **THE ROW IS A USER REQUIREMENT AND IT IS QUOTED, because every clause below
is one half of it:**

> the left panel shou go all the way to the left side and be fixed. the context
> panel should be dynamic using more content of the page than longer scroll than
> needed.

⭐ **A RAIL TALLER THAN THE WINDOW IS THE FIXTURE THIS MODULE EXISTS FOR.** A
rail that no longer scrolls with the page is a rail whose last containers are
unreachable unless it scrolls itself — and that is invisible on every committed
corpus, because the biggest container in any of them declares THREE units.
⚠️ `test_rail_rows.py` widens ONE container to sixteen, which is
enough to overhang a masthead and not enough to overhang a window; this module
widens EVERY container far enough that the rail runs past the bottom of the
screen, and then asserts the reader can still get to the end of it.

## ⛔ Which box each reading measured is named in the reading itself

⚠️ **A probe that does not say what it measured gets misread.** Every
reading below is taken with `getBoundingClientRect()` — the **border box**, in
**viewport** coordinates — except the two that say otherwise: `scrollHeight` and
`clientHeight` on the rail, which are the rail's own **scrollable content** and
its **padding box**, and are the pair that says whether anything is past its
fold. ⭐ The element each one was read from is named in the failure message.

## ⛔ Asserted the other way, on the tree that shipped

⚠️ A control that has only ever seen the repaired stylesheet has not been shown
to notice the defect it exists for. ⭐ A third tree is built with the
wide shape rewritten back to what `W326` merged — the centred cap, the constant
track, no sticky — and the three settling clauses are asserted to FAIL on it.
"""

from __future__ import annotations

import json
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

#: How many units EVERY container is carried out to. ⚠️ **Not a round number for
#: its own sake and not `test_rail_rows.UNITS` either**: this module needs a rail
#: TALLER than the window it is opened in, and sixteen units in one container is
#: not that. ⛔ That the fixture is big enough is ASSERTED rather than assumed —
#: `test_a_rail_taller_than_the_window_has_content_past_its_own_fold` goes red on
#: a fixture too small to exhibit the defect at all.
UNITS = 40

#: The region under test, spelled as `chrome.css` and `test_rail.py` spell it.
RAIL = 'nav[aria-label="Containers"]'

#: How far two readings may differ and still be the same reading, in CSS pixels
#: — the same subpixel allowance `test_rail.TOUCHING` makes.
TOUCHING = 0.5

#: A second wide viewport, wider than `WIDE`. ⭐ Clause 2 is *"a function of the
#: viewport"*, and a function is shown by two points on it, never by one reading
#: and an argument. ⚠️ Since `W388` stage 4 this width is ABOVE the ceiling
#: `--page-max` declares, so the pair reads the function on the stretch where it
#: still rises — which is the stretch a reader's own screen is on.
WIDER = (1920, WIDE[1])

#: The wide shape as it stands, and as `W326` merged it — the control rewrites
#: the first into the second in a BUILT tree's own stylesheet, so what the
#: clauses below are refuted against is this row's actual defect.
SHIPPED = (
    (
        "grid-template-columns: var(--rail) minmax(0, 1fr);",
        "grid-template-columns: var(--rail) minmax(0, calc(var(--measure) + 2 * var(--gutter)));",
    ),
    (
        # ⚠️ Since `W388` stage 4 the wide page carries `--page-max` on `body`
        # again and CENTRES under it, so the text rewritten here is that pair;
        # the shape it is rewritten back to is still `W326`'s.
        "max-width: var(--page-max);\n"
        "    margin-left: max(0px, (100% - var(--page-max)) / 2);\n"
        "    padding-left: 0;",
        "max-width: min(var(--page-max), calc(var(--rail) + var(--measure) + 5 * var(--gutter)));",
    ),
    (
        # ⚠️ The rail's own block, named by `grid-column: 1`: since `W388` the
        # aside in column 3 sticks and scrolls by the same four declarations,
        # and a pattern that matched both would rewrite a region this row is
        # not about — and the control then asserts nothing about the rail.
        "grid-column: 1;\n    grid-row: 1 / span 10;\n    align-self: start;\n"
        "    position: sticky;\n    top: 0;\n    max-height: 100vh;\n    overflow-y: auto;\n",
        "grid-column: 1;\n    grid-row: 1 / span 10;\n    align-self: start;\n",
    ),
)

#: One page's geometry, in the vocabulary the clauses are written in. ⛔ Every
#: rectangle here is a BORDER BOX in viewport coordinates; the two rail figures
#: that are not are named for what they are.
GEOMETRY = """
(() => {
  const at = s => { const el = document.querySelector(s); if (!el) return null;
    const b = el.getBoundingClientRect();
    return {left: b.left, right: b.right, top: b.top, bottom: b.bottom,
            width: b.width, height: b.height}; };
  const rail = document.querySelector('<rail>');
  return {
    'body border box': at('body'),
    'rail border box': at('<rail>'),
    'main#content border box': at('main#content'),
    'rail scrollable content height': rail ? rail.scrollHeight : null,
    'rail padding box height': rail ? rail.clientHeight : null,
    'rail computed position': rail ? getComputedStyle(rail).position : null,
    'window inner width': window.innerWidth,
    'window inner height': window.innerHeight,
    'document scroll height': document.documentElement.scrollHeight,
    'page scroll offset': window.scrollY,
  };
})()
""".replace("<rail>", RAIL)


@dataclass(frozen=True)
class TallCorpus:
    """One widened corpus built onto disk, and the page every clause opens."""

    root: Path
    page: Path

    @property
    def url(self) -> str:
        """The `file://` URL of a unit page inside one of the widened containers."""
        return "file://" + str(self.page)


def _widen(source: Path, destination: Path) -> None:
    """Copy `source` to `destination` with EVERY container carried to `UNITS` units.

    ⚠️ **Every container, and that is the difference from `test_rail_rows._widen`
    rather than a copy of it.** The rail lists every container the corpus has and
    opens the reader's own, so its height is driven by BOTH counts — and the
    clause here is about a rail overhanging a window, which one long course does
    not reliably produce while the others are short.

    ⛔ Nothing here names a corpus's own subject (R1): the units it adds are
    titled by their number and their prose is one sentence of filler. ⭐ The added
    unit inherits the copied entry's `origin` rather than being given one —
    the shared-origin sweep asserts the tree holds one declared reader and one declared
    writer of that key, and a fixture builder that wrote it would be a second.
    """
    shutil.copytree(source, destination, dirs_exist_ok=True)
    for manifest in sorted(destination.rglob("container.json")):
        container = json.loads(manifest.read_text(encoding="utf-8"))
        raw = manifest.parent / "raw" / container["variant"]
        pattern = json.loads(
            (sorted(raw.iterdir())[0] / "lesson-1.json").read_text(encoding="utf-8")
        )
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
        manifest.write_text(json.dumps(container, indent=2), encoding="utf-8")


def _build(root: Path) -> TallCorpus:
    """Widen the fixture corpus under `root` and build the whole site from it.

    ⛔ **The page every clause opens is the LONGEST one the corpus builds**, and
    that is a choice rather than an arbitrary first unit: the *"and be fixed"*
    clause is taken after scrolling to the foot of the page, and a page that fits
    the window has no foot to scroll to. ⚠️ Read as the largest built unit page by
    byte size — measured off the tree, so it follows a fixture that changes.
    """
    source = root / "source"
    _widen(repository_root() / "tests" / "fixtures" / CORPUS, source)
    site = root / "site"
    site.mkdir(parents=True, exist_ok=True)
    write_site(source, site)
    corpus = read_corpus(source)
    longest = max(
        (site / str(unit_location(corpus, unit).page) for unit in corpus.units),
        key=lambda page: page.stat().st_size,
    )
    return TallCorpus(root=site, page=longest)


def _revert(built: TallCorpus) -> None:
    """Put the wide shape `W326` merged back into a built tree's own stylesheet."""
    sheets = [
        sheet
        for sheet in sorted(built.root.rglob("*.css"))
        if SHIPPED[0][0] in sheet.read_text(encoding="utf-8")
    ]
    assert len(sheets) == 1, f"{len(sheets)} built stylesheets lay the page out, not one"
    written = sheets[0].read_text(encoding="utf-8")
    for now, before in SHIPPED:
        assert written.count(now) == 1, f"the built stylesheet does not carry {now!r} once"
        written = written.replace(now, before)
    sheets[0].write_text(written, encoding="utf-8")


@pytest.fixture(scope="session")
def tall(tmp_path_factory: pytest.TempPathFactory) -> TallCorpus:
    """The widened corpus, built once for the session the way a build builds it."""
    return _build(tmp_path_factory.mktemp("visual-rail-fixed"))


@pytest.fixture(scope="session")
def as_shipped(tmp_path_factory: pytest.TempPathFactory) -> TallCorpus:
    """The same tree with the wide shape `W326` merged — the defect itself."""
    built = _build(tmp_path_factory.mktemp("visual-rail-fixed-shipped"))
    _revert(built)
    return built


@pytest.fixture
def geometry(open_page: OpenPage) -> Iterator[object]:
    """Open one built page at one width, scripts OFF, and read its boxes back."""

    def read(built: TallCorpus, width: tuple[int, int], scroll_to_bottom: bool = False) -> dict:
        open_page.resize(*width)
        open_page.open(built.url, scripts=False)
        if scroll_to_bottom:
            # ⛔ `behavior: "instant"` is NOT decoration. `reset.css` sets
            # `scroll-behavior: smooth` on `html`, so a plain `scrollTo` is
            # ANIMATED and the reading taken straight after it is a reading of
            # the page still at the top — measured, and it read `scrollY` 0 on a
            # page 1,000px longer than the window.
            open_page.evaluate(
                "window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'})"
            )
        return dict(open_page.evaluate(GEOMETRY))  # type: ignore[arg-type]

    yield read


# --- clause 1: all the way to the left side ---------------------------------


def test_the_rail_starts_at_the_windows_own_left_edge(geometry, tall: TallCorpus) -> None:
    """⛔ *"the left panel shou go all the way to the left side"*, read as pixels.

    ⚠️ **Flush means the WINDOW's left edge and never the layout's.** Before this
    row the page was capped and centred at a width no window matched, so the rail
    — the first grid track — started wherever centring had put it, and on a wide
    screen that was a long way in. ⭐ Both boxes are asserted, because a page
    flush left with a rail inset inside it is the same defect one element along.

    ⛔ **Taken at `WIDE`, which is BELOW the ceiling `W388` stage 4 gave the
    shell, and that is the point rather than a convenience.** The shell centres
    only where a window has room past the ceiling; at every width a reader's
    laptop opens, `auto` resolves to nothing and this clause is the page.
    ⚠️ Where the rail sits once the shell does centre is
    `test_reading_width.py`'s, and it is the shell's edge, not the window's.
    """
    read = geometry(tall, WIDE)

    assert read["body border box"]["left"] == pytest.approx(0, abs=TOUCHING), (
        f"the body's border box starts at {read['body border box']['left']:.2f}px in a "
        f"{read['window inner width']}px window, so the page is still centred"
    )
    assert read["rail border box"]["left"] == pytest.approx(0, abs=TOUCHING), (
        f"the rail's border box starts at {read['rail border box']['left']:.2f}px, so it "
        "is inset from the window's edge rather than flush against it"
    )
    assert read["rail border box"]["width"] > 0, "the rail has no width, so this judges nothing"


def test_the_reading_column_still_clears_the_rail_at_the_wide_width(
    geometry, tall: TallCorpus
) -> None:
    """⛔ `W325`'s clause re-taken, and the hazard a flush rail creates.

    ⚠️ **A rail taken out of flow orphans the column**: the prose lays out under
    it and the reader loses the left of every line. ⭐ That is why this row is
    `position: sticky` and not `position: fixed` — the rail keeps its grid track,
    so the column clears it by construction rather than by a matching inset.
    """
    read = geometry(tall, WIDE)

    assert read["rail border box"]["right"] <= read["main#content border box"]["left"] + TOUCHING, (
        f"the rail's border box ends at {read['rail border box']['right']:.2f}px and the "
        f"reading surface's starts at {read['main#content border box']['left']:.2f}px, so "
        "the prose is laid out underneath the rail"
    )


# --- clause 1: and be fixed -------------------------------------------------


def test_the_rail_is_still_at_the_top_of_the_window_at_the_foot_of_a_long_page(
    geometry, tall: TallCorpus
) -> None:
    """⛔ *"and be fixed"*, and it is measured at the one place it can fail.

    ⭐ **At the BOTTOM of the page**, because at the top every rail looks fixed.
    ⚠️ The reading is the rail's border box top in VIEWPORT coordinates after the
    page has been scrolled to its end: a rail that scrolled away is a large
    negative number there, and the courses are gone.
    """
    read = geometry(tall, WIDE, scroll_to_bottom=True)

    assert read["page scroll offset"] > 0, (
        "the page did not scroll at all, so this reading says nothing about a rail "
        "that scrolls away"
    )
    assert read["rail border box"]["top"] == pytest.approx(0, abs=TOUCHING), (
        f"after scrolling {read['page scroll offset']:.0f}px the rail's border box top is "
        f"{read['rail border box']['top']:.2f}px, so it has scrolled off the window"
    )
    assert read["rail border box"]["bottom"] > 0, "the rail is above the window entirely"


# --- clause 1: a rail taller than the window scrolls itself -----------------


def test_a_rail_taller_than_the_window_has_content_past_its_own_fold(
    geometry, tall: TallCorpus
) -> None:
    """⛔ **This is the fixture assertion, and it is the reason this module exists.**

    ⚠️ Two boxes and they are NOT the same box: `scrollHeight` is the rail's
    scrollable content and `clientHeight` is its padding box. ⭐ A rail whose
    content fits its padding box proves nothing about the clause below, so a
    corpus too small to overhang the window reds HERE, loudly, rather than
    letting the reachability check pass over a rail that was never long.
    """
    read = geometry(tall, WIDE)

    assert read["rail border box"]["height"] <= read["window inner height"] + TOUCHING, (
        f"the rail's border box is {read['rail border box']['height']:.2f}px tall in a "
        f"{read['window inner height']}px window, so a fixed rail runs off the screen"
    )
    assert read["rail scrollable content height"] > read["rail padding box height"], (
        f"the rail's scrollable content is {read['rail scrollable content height']}px against "
        f"a padding box of {read['rail padding box height']}px, so this fixture's rail fits "
        "the window and the clause about reaching past its fold is untested"
    )


def test_the_part_of_the_rail_past_the_fold_can_be_reached(
    open_page: OpenPage, tall: TallCorpus
) -> None:
    """⛔ **Clipped and unreachable is the defect; clipped and scrollable is the fix.**

    ⚠️ `max-height` without `overflow-y` hides a corpus's last containers with no
    way to get to them, which is worse than a rail that scrolls the page. ⭐ So
    the rail is SCROLLED, by the browser, and the last link it carries is
    asserted to land inside the rail's own padding box afterwards — the reading
    is the link's border box against the rail's border box, and neither is a
    number written in this file.

    ⛔ **The population is the links the browser actually LAYS OUT**, which is a
    measured correction rather than a tidiness. A closed `<details>` is rendered
    with `content-visibility: hidden` in this engine, and
    `getBoundingClientRect()` inside one returns the box it had when it was last
    laid out — 2,684px down a 900px window, in the reading that caught this. ⭐ A
    link the reader cannot see is not what "reachable" is about.
    """
    open_page.resize(*WIDE)
    open_page.open(tall.url, scripts=False)
    reached = open_page.evaluate(
        f"(() => {{ const rail = document.querySelector('{RAIL}');"
        " const links = Array.from(rail.querySelectorAll('a'))"
        "  .filter(a => !a.closest('details:not([open])'));"
        " const last = links[links.length - 1];"
        " const before = last.getBoundingClientRect().bottom;"
        " rail.scrollTop = rail.scrollHeight;"
        " const box = rail.getBoundingClientRect();"
        " const after = last.getBoundingClientRect();"
        " return {links: links.length, moved: rail.scrollTop,"
        "  'rail computed overflow-y': getComputedStyle(rail).overflowY,"
        "  'last link border box bottom before scrolling': before,"
        "  'last link border box bottom after scrolling': after.bottom,"
        "  'rail border box bottom': box.bottom, 'rail border box top': box.top}; })()"
    )
    read = dict(reached)  # type: ignore[arg-type]

    assert int(read["links"]) > 0, "the rail carries no links, so there is nothing to reach"
    # ⛔ **THE SCROLL BELOW IS NOT ENOUGH ON ITS OWN, AND THAT IS MEASURED.** A
    # box with `overflow-y: hidden` still moves when a script assigns its
    # `scrollTop` — so this whole check passed over a rail planted with `hidden`,
    # which is precisely the unreachable state it exists to refuse. ⭐ What the
    # READER gets is the computed value, so it is asserted first.
    assert read["rail computed overflow-y"] in ("auto", "scroll"), (
        f"the rail's computed overflow-y is {read['rail computed overflow-y']!r}, so the "
        "part of it past the fold is reachable by a script and by nobody else"
    )
    assert (
        float(read["last link border box bottom before scrolling"])
        > float(read["rail border box bottom"]) + TOUCHING
    ), (
        "the rail's last laid-out link is already inside its border box before anything "
        "is scrolled, so nothing here is past the fold and the clause is untested"
    )
    assert float(read["moved"]) > 0, (
        "the rail did not scroll, so whatever is past its fold cannot be reached"
    )
    assert (
        float(read["last link border box bottom after scrolling"])
        <= float(read["rail border box bottom"]) + TOUCHING
    ), "the last link is still below the rail's border box after scrolling it to its end"
    assert float(read["last link border box bottom after scrolling"]) > float(
        read["rail border box top"]
    ), "the last link is above the rail's border box, so scrolling took it past the reader"


# --- clause 2: the reading column is a function of the viewport -------------


def test_the_reading_column_widens_with_the_window(geometry, tall: TallCorpus) -> None:
    """⛔ *"the context panel should be dynamic using more content of the page"*.

    ⭐ **Two points on the function, never one reading and an argument.** The same
    page is opened at two wide viewports and the reading surface's border box is
    compared; a constant track gives the same number twice, which is exactly what
    shipped.
    """
    narrower = geometry(tall, WIDE)
    wider = geometry(tall, WIDER)

    assert (
        wider["main#content border box"]["width"] - narrower["main#content border box"]["width"]
        > TOUCHING
    ), (
        f"the reading surface's border box is "
        f"{narrower['main#content border box']['width']:.2f}px in a {WIDE[0]}px window and "
        f"{wider['main#content border box']['width']:.2f}px in a {WIDER[0]}px one, so it is "
        "a constant and the extra screen is margin"
    )
    assert wider["main#content border box"]["width"] > wider["window inner width"] / 2, (
        "the reading surface takes less than half a wide window, so the page is not using it"
    )


def test_the_dynamic_column_is_still_bounded_on_a_screen_nobody_has(
    open_page: OpenPage, tall: TallCorpus
) -> None:
    """⚠️ **An unbounded column is this row's own way of going wrong.**

    ⛔ A table or a code block across a whole 4K display is the full-bleed defect
    the column section was written against. ⭐ The ceiling is read off the page —
    a probe element given `width: var(--page-max)` — rather than written here, so
    a palette that moves it moves this clause with it.

    ⛔ **`W388` stage 4 settled WHERE the ceiling is and what happens above it.**
    Stage 2 held `body` at the ceiling and pinned it left, which put a dead strip
    down one side; stage 3 released the bound and let the tracks grow without
    limit. ⭐ The shell carries the ceiling again and CENTRES under it, so the
    element a wide table and a long line of code are in stops growing, and what
    the window has past the ceiling is split evenly rather than left on one side.
    """
    open_page.resize(4 * WIDE[0], WIDE[1])
    open_page.open(tall.url, scripts=False)
    read = dict(open_page.evaluate(GEOMETRY))  # type: ignore[arg-type]
    ceiling = open_page.evaluate(
        "(() => { const probe = document.createElement('div');"
        " probe.style.cssText = 'width: var(--page-max); position: absolute; visibility: hidden';"
        " document.body.appendChild(probe);"
        " const width = probe.getBoundingClientRect().width;"
        " probe.remove(); return width; })()"
    )

    assert float(ceiling) > 0, "the palette declares no --page-max, so nothing is ceiled"
    assert float(ceiling) < read["window inner width"], (
        f"the ceiling of {float(ceiling):.2f}px is wider than the "
        f"{read['window inner width']:.2f}px window, so this reading is vacuous"
    )
    assert read["body border box"]["width"] <= float(ceiling) + TOUCHING, (
        f"the shell is {read['body border box']['width']:.2f}px against a "
        f"declared ceiling of {float(ceiling):.2f}px, so the bound is not biting"
    )
    assert read["main#content border box"]["width"] < read["body border box"]["width"], (
        f"the reading surface is {read['main#content border box']['width']:.2f}px inside a "
        f"{read['body border box']['width']:.2f}px shell, so the rail and the aside are "
        "not inside the shell with it"
    )
    assert read["body border box"]["left"] == pytest.approx(
        read["window inner width"] - read["body border box"]["right"], abs=TOUCHING
    ), (
        f"the shell has {read['body border box']['left']:.2f}px of room on its left and "
        f"{read['window inner width'] - read['body border box']['right']:.2f}px on its "
        "right, so the ceiling is back to pinning the page and the dead strip with it"
    )


# --- the narrow shape is untouched by all of it -----------------------------


def test_at_the_narrow_width_the_page_keeps_its_gutter_and_the_rail_is_a_card(
    geometry, tall: TallCorpus
) -> None:
    """⛔ **Every declaration this row added is inside the one width threshold.**

    ⚠️ A phone gets the card above the reading surface, a page with gutters on
    both sides, and nothing sticky. ⭐ The flush-left rule is the one most likely
    to leak: a body with no left gutter at 720px is prose against the glass.

    ⛔ **The gutter is read off the READING SURFACE and not off `body`'s own left
    edge**, and that is a measured correction. `body`'s bound is wider than this
    viewport, so at 720px it fills the window and its border box starts at 0 —
    the inset that survives is its PADDING, which is what holds the prose off the
    glass and what a leaked `padding-left: 0` would take away.
    """
    read = geometry(tall, NARROW)

    assert read["main#content border box"]["left"] > TOUCHING, (
        f"at {NARROW[0]}px the reading surface's border box starts at "
        f"{read['main#content border box']['left']:.2f}px inside a body starting at "
        f"{read['body border box']['left']:.2f}px, so the narrow page lost its left gutter"
    )
    assert read["rail computed position"] == "static", (
        f"at {NARROW[0]}px the rail's computed position is "
        f"{read['rail computed position']!r}, so the wide shape leaked below the threshold"
    )
    assert read["rail border box"]["bottom"] <= read["main#content border box"]["top"] + TOUCHING, (
        f"at {NARROW[0]}px the rail's border box ends at "
        f"{read['rail border box']['bottom']:.2f}px and the reading surface's starts at "
        f"{read['main#content border box']['top']:.2f}px, so it is beside the prose"
    )


# --- the negative control: the same clauses, on the tree that shipped -------


def test_the_three_settling_clauses_fail_on_the_wide_shape_that_shipped(
    geometry, as_shipped: TallCorpus
) -> None:
    """⛔ The control, and it is this row's ACTUAL defect rather than an impression.

    ⭐ The same build, with the wide shape rewritten in its own stylesheet back to
    the centred cap, the constant track and no sticky. ⚠️ All three are asserted
    to go red — not one — because each alone has a passing shape that is not the
    repair: a flush rail that scrolls away, a fixed rail floating in from the
    edge, and either of those beside a column that is still a constant.
    """
    flush = geometry(as_shipped, WIDE)
    at_the_foot = geometry(as_shipped, WIDE, scroll_to_bottom=True)
    narrower = geometry(as_shipped, WIDE)
    wider = geometry(as_shipped, WIDER)

    assert flush["rail border box"]["left"] > TOUCHING, (
        "the rail is already flush left on the tree that shipped, so the first clause "
        "would pass over the defect it exists for"
    )
    assert at_the_foot["rail border box"]["top"] < -TOUCHING, (
        "the rail is still at the top of the window at the foot of the page on the tree "
        "that shipped, so the second clause would pass over the defect it exists for"
    )
    assert (
        abs(
            wider["main#content border box"]["width"] - narrower["main#content border box"]["width"]
        )
        <= TOUCHING
    ), (
        "the reading surface already widens with the window on the tree that shipped, so "
        "the third clause would pass over the defect it exists for"
    )
