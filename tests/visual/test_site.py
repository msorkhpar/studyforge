"""The tree this harness opens, and whether it reaches what it claims to judge.

⛔ **Machinery, not a sixth acceptance clause** — `test_init.py` names it as such.
The five clauses each ask a question *about a page*; this module asks whether the
pages exist at all, which is the question `W98` was: the harness judged **two** of
`SF-34`'s chrome regions and reported nothing about the other four.

## ⛔ Why a census and not a comment

⚠️ **The blindness was invisible from inside every check that had it.** Every
contrast assertion, every focus traversal and every request log passed — over a
population that carried a masthead and an outline and no bar, no practice panel,
no unit listing and no contents tree. ⭐ Nothing went red, nothing was skipped,
and the harness line said `RAN`. So the only thing that can keep this fixed is a
check whose own failure is *"this tree cannot reach region N"*.

## ⛔ Why the column check is the one `W98` exists for, and what it refuses to say

⭐ **`--measure: 80ch` resolves against THE ELEMENT'S OWN FONT.** `SF-34`
measured one correct declaration producing three different columns — 800 px,
715.7 px, 680.3 px — and ⛔ **no assertion over a stylesheet can see it**,
because every declaration involved is identical and right.

⛔ **What this module asserts is an EQUALITY between two measurements taken in the
same run** — each region's column against the reading surface's — rather than a
resolved width against a recorded number. ⭐ It is invariant under any font the
image ships and still fails the moment a region resolves a measure of its own.

⚠️ **When `W98` wrote that clause, an undeclared font was also a reason for it:**
`fonts-liberation` then arrived unconstrained from the base image's Debian
snapshot, so a px figure here would have been a recorded
value with an undeclared font behind it. ⛔ **That reason is GONE — `W124` landed
and the font is pinned by version and checksum in `docker/dev/Dockerfile`** — and
the clause is kept anyway, because an equality between two live measurements is
the stronger assertion on its own terms: it needs no figure to be re-measured
when the pin is next moved forward.

## ⛔ Why the column check now names a WIDTH, and what it excludes at one of them

⚠️ **`W325` gave the page two shapes.** The containers rail sits BESIDE the
reading column where a viewport has room for one and folds back INTO it where it
has not — so *"every chrome region resolves the reading surface's column"* is
true of every region at one width and of every region but that one at the other.

⛔ **The answer is a width-scoped exclusion and never an unconditional one.** The
wide check states its width instead of inheriting the launch window's, drops the
rail by name, and the narrow check runs the same arithmetic over the population
with **nothing** taken out. ⭐ So the region excluded at one width is compared at
the other, which is what keeps the exclusion from being the silent hole `W98`
was.

## ⭐ The one question this module still cannot ask — ⛔ THE GATE IS NOW OPEN

⚠️ **Nothing here asserts that the reading column is the measure the palette
declares.** The equality below catches a region resolving a column of its *own*;
it cannot catch every region, the reading surface included, resolving the *wrong*
one — `--measure: 80ch` against a font that changed under the image.

⛔ **The font the column is measured in is now pinned in the image, and that pin
deliberately did not add the assertion.** ⚠️ **The assertion needs things the pin
neither measured nor owns** — a recorded px figure per page kind and viewport, a
looseness statement of its own, and a negative control that reds when a face is
swapped under the image, which means building a second image to prove it can fail.

⭐ Stated rather than left as a silence, so the next reader knows the blocker is
gone and that what remains is work of its own, not an oversight.
"""

from __future__ import annotations

import json

import pytest

from tests.visual import site
from tests.visual.page import NARROW, WIDE, OpenPage

#: Where the reading surface's column is read from. ⛔ `main#content` and not a
#: number: it is the element `reading.css` and `chrome.css` agree is the column,
#: so it is the one reading every other region is compared against.
READING_SURFACE = "main#content"

#: The one chrome-ruled region that is NOT compared against the reading surface,
#: and why. ⛔ `body` **is** the column the others sit inside (`PO-22/6`, note
#: (d)), so comparing it with `main` compares a box with the box within it — it
#: measures 880 px against main's 840 because the gutter is the difference.
#: ⭐ Named here rather than filtered out by a rule, and asserted to be a member
#: of the population, so it cannot become a silent hole if the table is rewritten.
THE_COLUMN_ITSELF = "body"

#: The one chrome-ruled region that is not compared against the reading surface
#: **at the wide width**, and why. ⛔ `W325` put the containers rail BESIDE the
#: column rather than above it, so at a viewport with room for one it resolves
#: `--rail` and not the column — deliberately, and it is the only region that
#: does. ⭐ **The exclusion is not a hole, because it is width-scoped:** the same
#: region IS compared, with every other, at `NARROW`, where the rail folds back
#: into the column. ⚠️ Named here rather than filtered by a rule, and asserted to
#: be a member of the population, for `THE_COLUMN_ITSELF`'s reason.
THE_RAIL_BESIDE_THE_COLUMN = 'nav[aria-label="Containers"]'

#: The regions a wide window puts in the ASIDE, on the far side of the column
#: (`W388`, folding `W369`): a unit's outline and the index's explanation. ⛔
#: Excluded at `WIDE` for the rail's reason and re-admitted at `NARROW` by the
#: same check, where both are back in the one column above the content.
THE_ASIDE_BESIDE_THE_COLUMN = (
    'nav[aria-label="Outline"]',
    'section[aria-label="About this site"]',
)

#: How far two columns may differ and still be the same column, in CSS pixels.
#: ⛔ **Not a font threshold**, which is why it needs no recorded font: both sides of
#: the comparison are measured in the same run under the same font, so a font
#: change moves them together. ⭐ It is here only for subpixel layout — measured
#: in the pinned image at `f71c566` every pair is equal to the hundredth of a
#: pixel, over seven pages.
SAME_COLUMN = 0.5

#: How many elements a region may contribute before this check stops reporting
#: them individually. ⚠️ A census that prints every node of a contents tree
#: buries its own verdict.
REPORTED = 12


def _census(page: OpenPage, regions: tuple[str, ...]) -> dict[str, int]:
    """How many of each region the open page carries, by selector."""
    return dict(
        page.evaluate(  # type: ignore[arg-type]
            "(() => { const out = {};"
            f" for (const sel of {json.dumps(list(regions))})"
            " out[sel] = document.querySelectorAll(sel).length;"
            " return out; })()"
        )
    )


def _columns(page: OpenPage, regions: tuple[str, ...]) -> list[list]:
    """`[selector, width]` for every laid-out element of every named region.

    ⛔ Zero-width elements are dropped and the drop is the point: `SF-30`'s
    read-mark control ships `hidden`, so with scripts off it has no box at all
    and a width comparison against it would be a comparison with nothing.
    """
    return list(
        page.evaluate(  # type: ignore[arg-type]
            "(() => { const out = [];"
            f" for (const sel of {json.dumps(list(regions))})"
            "   for (const el of document.querySelectorAll(sel)) {"
            "     const width = el.getBoundingClientRect().width;"
            "     if (width > 0) out.push([sel, width]);"
            "   }"
            " return out; })()"
        )
    )


def test_the_region_population_is_inhabited_and_is_the_disposition_tables() -> None:
    """⭐ The population comes from `SF-34`'s table and is non-empty.

    ⛔ A totality claim over an empty set is the most convincing check
    in the repository and says nothing at all.
    """
    regions = site.chrome_regions()
    assert regions, "no region is declared chrome-ruled, so every check below is vacuous"
    assert len(regions) == len(set(regions)), f"the same region twice: {regions}"
    assert site.OUTLINE_REGION in regions, (
        f"{site.OUTLINE_REGION} is not one of the regions the table rules — it was renamed, "
        f"and every selector narrowed to it now matches nothing: {regions}"
    )
    assert THE_COLUMN_ITSELF in regions, (
        f"{THE_COLUMN_ITSELF!r} is excluded from the column comparison as a region that "
        f"exists; it is not in {regions}, so the exclusion now hides nothing and says nothing"
    )
    assert THE_RAIL_BESIDE_THE_COLUMN in regions, (
        f"{THE_RAIL_BESIDE_THE_COLUMN!r} is excluded from the WIDE column comparison as a "
        f"region that exists; it is not in {regions}, so the exclusion hides nothing — and "
        f"the narrow check below would then be asserting an equality over one region fewer"
    )
    for aside in THE_ASIDE_BESIDE_THE_COLUMN:
        assert aside in regions, (
            f"{aside!r} is excluded from the WIDE column comparison as a region that exists; "
            f"it is not in {regions}, so the exclusion hides nothing"
        )


def test_the_harness_writes_every_page_kind_the_framework_renders() -> None:
    """⛔ Three renderers, three kinds, and the tree carries one of each.

    ⚠️ The defect this forbids is the one `W98` was: a harness whose population
    is *the page kind somebody happened to start with*, which reads as complete
    because every check over it passes.
    """
    assert site.kinds() == (site.CONTAINER, site.INDEX, site.UNIT), (
        f"the harness writes {site.kinds()}, and the framework renders three kinds"
    )
    counted = {kind: 0 for kind in site.kinds()}
    for built in site.pages_built():
        counted[built.kind] += 1
    assert all(counted.values()), f"a kind with no page written: {counted}"
    assert set(site.cases()) == {
        built.name for built in site.pages_built() if built.kind == site.UNIT
    }, "cases() and the built population disagree about which pages are units"


def test_every_stylesheet_damage_is_a_declared_damage() -> None:
    """⛔ A damage that breaks the bundle is still one of the declared five.

    ⚠️ The failure this forbids is silent in the worst way: a key in
    `STYLESHEET_DAMAGE` that `DAMAGE` does not declare is a tree `build()` refuses
    to make, and a key `DAMAGE` declares and this mapping misspells is a tree that
    is **not damaged at all** — a control that passes for the wrong reason.
    """
    assert set(site.STYLESHEET_DAMAGE) <= set(site.DAMAGE), (
        f"stylesheet damages {sorted(set(site.STYLESHEET_DAMAGE) - set(site.DAMAGE))} "
        f"are not declared in DAMAGE"
    )
    assert site.OWN_COLUMN_REGION in site.chrome_regions(), (
        f"the column control damages {site.OWN_COLUMN_REGION!r}, which the disposition "
        f"table does not rule: {site.chrome_regions()}"
    )


def test_every_chrome_region_the_table_rules_is_in_the_tree_this_harness_opens(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ `W98`'s whole subject: the census, in full, before the verdict.

    ⭐ Reported per page and then as a union, because *which* page carries a
    region is the fact a reader needs when one goes missing — and the union is
    the only thing the five clauses actually see.
    """
    regions = site.chrome_regions()
    found: dict[str, list[str]] = {}
    for case in site.pages():
        open_page.open(built_site.url(case))
        census = _census(open_page, regions)
        found[case] = sorted(region for region, how_many in census.items() if how_many)
    reached = {region for present in found.values() for region in present}
    listing = "\n".join(f"  {case}: {present}" for case, present in found.items())
    assert reached == set(regions), (
        f"the harness opens {len(reached)} of {len(regions)} chrome regions.\n"
        f"never reached: {sorted(set(regions) - reached)}\n{listing}"
    )


def test_the_census_notices_a_tree_with_no_chrome_in_it(
    open_page: OpenPage, damaged_sites: dict[str, site.Site]
) -> None:
    """⛔ Negative control: the `blank` tree must fail the census above.

    ⚠️ Without it the census is a claim that a region *would* be noticed if it
    vanished, and that claim is exactly what was false for four regions.
    """
    regions = site.chrome_regions()
    blank = damaged_sites["blank"]
    reached: set[str] = set()
    for case in site.pages():
        open_page.open(blank.url(case))
        reached |= {region for region, how_many in _census(open_page, regions).items() if how_many}
    assert reached != set(regions), (
        "a tree whose every body was emptied still reported every chrome region — "
        "this census cannot see a region that is not there"
    )


def _adrift(open_page: OpenPage, compared: tuple[str, ...], case: str) -> list[str]:
    """Which of `compared` resolve a column other than the reading surface's.

    ⭐ Lifted out of the clause it served so the wide reading and the narrow one
    are the SAME arithmetic over two different populations — two copies of it
    would be two chances to write the comparison differently by accident.
    """
    surface = _columns(open_page, (READING_SURFACE,))
    assert surface, f"{case} has no {READING_SURFACE}, so there is nothing to compare against"
    column = float(surface[0][1])
    measured = _columns(open_page, compared)
    assert measured, (
        f"{case} carries no chrome region at all, so this check would pass over nothing"
    )
    return [
        f"{selector} is {float(width):.2f}px against {READING_SURFACE}'s {column:.2f}px"
        for selector, width in measured
        if abs(float(width) - column) > SAME_COLUMN
    ]


@pytest.mark.parametrize("case", site.pages())
def test_every_chrome_region_resolves_the_same_column_as_the_reading_surface(
    open_page: OpenPage, built_site: site.Site, case: str
) -> None:
    """⭐ The class `W98` exists for, and the one no stylesheet assertion can see.

    ⛔ A per-region bound written in `ch` resolves against that region's **own**
    inherited font, so one correct declaration produces as many columns as there
    are fonts on the page. ⚠️ This is an equality between two live measurements
    and never a px figure from a file — see this module's docstring.

    ⛔ **`W325` took the containers rail OUT of this population and put the width
    IN.** The rail is now beside the column at a wide viewport, so it resolves
    `--rail` by design; the width is set here rather than inherited from the
    launch window so that *"wide"* is a stated fact about this reading, and the
    check below re-admits the rail at the narrow width, where it folds back in.
    """
    open_page.resize(*WIDE)
    open_page.open(built_site.url(case))
    compared = tuple(
        region
        for region in site.chrome_regions()
        if region not in (THE_COLUMN_ITSELF, THE_RAIL_BESIDE_THE_COLUMN)
        and region not in THE_ASIDE_BESIDE_THE_COLUMN
    )
    adrift = _adrift(open_page, compared, case)
    assert not adrift, (
        f"{case} at {WIDE[0]}px: {len(adrift)} chrome region(s) resolving a column of "
        "their own:\n  " + "\n  ".join(adrift[:REPORTED])
    )


@pytest.mark.parametrize("case", site.pages())
def test_at_a_narrow_viewport_every_chrome_region_including_the_rail_is_the_column(
    open_page: OpenPage, built_site: site.Site, case: str
) -> None:
    """⛔ `W325`'s degradation clause, and the other half of the exclusion above.

    ⚠️ **A rail squeezed against prose is the failure this forbids**, and the
    shape chosen instead is the card `W324` shipped — the region back in the one
    column, above the reading surface. ⭐ So the assertion is not a new one: it is
    the SAME equality, over the population with nothing taken out of it.

    ⛔ **This is what stops the wide exclusion being a hole.** A rail excluded at
    one width and never compared at any other is a region no column check reaches.
    """
    open_page.resize(*NARROW)
    open_page.open(built_site.url(case))
    compared = tuple(region for region in site.chrome_regions() if region != THE_COLUMN_ITSELF)
    assert THE_RAIL_BESIDE_THE_COLUMN in compared, compared
    assert set(THE_ASIDE_BESIDE_THE_COLUMN) <= set(compared), compared
    adrift = _adrift(open_page, compared, case)
    assert not adrift, (
        f"{case} at {NARROW[0]}px: {len(adrift)} chrome region(s) resolving a column of "
        "their own:\n  " + "\n  ".join(adrift[:REPORTED])
    )


def test_the_column_check_notices_a_region_given_a_measure_of_its_own(
    open_page: OpenPage, damaged_sites: dict[str, site.Site]
) -> None:
    """⛔ Negative control, and it is `SF-34`'s defect reproduced rather than described.

    ⭐ The `column` tree gives one region `max-width` in `ch` and changes nothing
    else — no class, no colour, no markup. ⚠️ Every other check in this package
    passes on that tree, which is the whole argument for this one.
    """
    broken = damaged_sites["column"]
    compared = tuple(
        region
        for region in site.chrome_regions()
        if region not in (THE_COLUMN_ITSELF, THE_RAIL_BESIDE_THE_COLUMN)
        and region not in THE_ASIDE_BESIDE_THE_COLUMN
    )
    caught = {}
    open_page.resize(*WIDE)
    for case in site.pages():
        open_page.open(broken.url(case))
        surface = _columns(open_page, (READING_SURFACE,))
        column = float(surface[0][1])
        caught[case] = [
            selector
            for selector, width in _columns(open_page, compared)
            if abs(float(width) - column) > SAME_COLUMN
        ]
    assert all(caught.values()), (
        f"a tree in which one region carries its own column measured {caught} — "
        "this harness cannot see the failure SF-34 is judged on"
    )
