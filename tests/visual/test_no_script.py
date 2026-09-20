"""Clause 4 — the page is run with JavaScript disabled, and still reads.

⛔ **`SF-14`'s acceptance, made runnable before `SF-14` needs it.** The reading
floor is a page opened from a file with no server; a reader who has scripts off,
or whose browser blocked a `file://` script, must still get the words. What they
may lose is decoration — the copy button, the syntax colours — and the point of
this module is that the line between the two is asserted rather than assumed.
"""

from __future__ import annotations

import pytest

from tests.visual import site
from tests.visual.page import OpenPage

#: Sentences the fixture units carry in their prose. ⛔ Taken from the material,
#: not from the renderer, so a renderer that dropped its body would fail here
#: rather than agree with itself.
#:
#: ⚠️ **Unit pages only, and `test_every_unit_page_carries_a_row_in_this_census`
#: holds it total over them.** A container page and a root index carry no prose
#: of their own — their words are the corpus's titles and notes — so the check
#: that reaches every page kind is the derived one below: `MASTHEAD`, which every
#: kind emits and every kind fills from the material (`W98`).
PROSE = {
    "depth2-unit-01": "A class is a name plus the state and behaviour filed under it.",
    "depth1-unit-02": None,
}

#: The masthead's own words — region 1, and the one region every page kind emits.
#: ⛔ Read from the page rather than listed per fixture: it is a corpus's text, so
#: a sentence typed here would be a third copy of two fixtures' titles.
#:
#: ⚠️ The theme control is inside the masthead and is NOT the masthead's words:
#: it ships `hidden` and the page script reveals it, so reading it here would
#: make this check say "the masthead is script-dependent" about the one region
#: that is supposed to appear only when a script can back it. ⛔ Excluded by the
#: hook it carries, not by its words, so renaming a label cannot re-admit it.
MASTHEAD = (
    "Array.from(document.querySelector('header').children)"
    ".filter(el => !el.matches('[data-section=\"theme\"]'))"
    ".map(el => el.innerText).join(' ').replace(/\\s+/g, ' ').trim()"
)

#: Every `nav` region that is NOT the outline, as a selector. ⛔ Derived from the
#: disposition table so the two halves of Ruling 164's fork are one population
#: split in one place — see `site.OUTLINE_REGION`.
CHROME_NAVS = tuple(
    region
    for region in site.chrome_regions()
    if region.startswith("nav[") and region != site.OUTLINE_REGION
)

#: The page's own text, with what a *script* added taken back out.
#: ⚠️ `copy-code.js` inserts a button reading "Copy" into every code figure, so
#: a raw `innerText` comparison between the two runs fails on the decoration
#: rather than on the words — which is a true difference and the wrong one.
#: ⛔ Removing it from the scripted side, and nothing else, keeps the comparison
#: about the material.
TEXT_WITHOUT_DECORATION = (
    "(() => { const copy = document.cloneNode(true);"
    " copy.querySelectorAll('.copy').forEach(node => node.remove());"
    " return copy.getElementById('content').innerText.replace(/\\s+/g, ' ').trim(); })()"
)


def test_every_unit_page_carries_a_row_in_this_census() -> None:
    """⛔ `PROSE` is total over the unit pages, or a new fixture is silently unchecked.

    ⚠️ Needed because the check below reads `PROSE.get(case)`: every page kind is
    in its population now (`W98`), and a `.get` over a hand-written mapping is a
    sentence that stops being asserted the moment a third unit fixture arrives.
    """
    assert sorted(PROSE) == sorted(site.cases()), (
        f"the material census names {sorted(PROSE)}, the harness opens {sorted(site.cases())}"
    )


@pytest.mark.parametrize("case", site.pages())
def test_the_words_survive_with_scripts_disabled(
    open_page: OpenPage, built_site: site.Site, case: str
) -> None:
    """Every visible character of the page's own text is there without a script.

    ⭐ **Every page kind, since `W98`** — a container's unit listing and the root
    index's disclosure tree are the two regions where *"it still reads with
    scripts off"* is least obvious, because both are built out of elements a
    script could have been tempted to mint.
    """
    open_page.open(built_site.url(case), scripts=True)
    with_scripts = open_page.evaluate(TEXT_WITHOUT_DECORATION)
    titled = open_page.evaluate(MASTHEAD)
    open_page.open(built_site.url(case), scripts=False)
    without = open_page.evaluate(TEXT_WITHOUT_DECORATION)
    untitled = open_page.evaluate(MASTHEAD)
    assert without, "with scripts off the page has no text at all"
    assert without == with_scripts, (
        "the text of the page differs with scripts disabled — the reading floor depends on a script"
    )
    # ⛔ The masthead is asserted separately and derived rather than typed,
    # because it is NOT inside `#content`: every page kind carries one, on every
    # kind its words come out of the material, and on a unit page it happens to
    # be repeated in the reading surface — which is why reading the column alone
    # checked it on two pages and nothing on the other five.
    assert untitled, f"{case} renders no masthead with scripts off"
    assert untitled == titled, f"{case}: the masthead {titled!r} is script-dependent"
    expected = PROSE.get(case)
    if expected:
        assert expected in str(without)


def test_the_page_still_navigates_itself_with_scripts_disabled(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ Navigation is `<a href="#…">` and headings, so it must not need a script.

    ⚠️ The check is that every outline link still resolves to an element that
    exists — an in-page link to an anchor no script has minted is a link that
    goes nowhere, and it looks identical in the markup.

    ⛔ **Scoped to the outline, and `W98` is why it had to be.** It read
    `nav[aria-label] a` and was true only while this harness opened no page
    carrying chrome: `document.querySelector('../../index.html')` is not a
    selector at all, so the moment a between-units bar, a unit listing or a
    contents tree entered the tree the expression threw. ⭐ The narrowing is a
    statement rather than a retreat — the companion check below asserts the other
    regions point OFF the page, so neither half can be satisfied by emitting
    nothing.
    """
    open_page.open(built_site.url("depth2-unit-01"), scripts=False)
    hrefs = open_page.evaluate(
        f"Array.from(document.querySelectorAll('{site.OUTLINE_REGION} a'))"
        ".map(a => a.getAttribute('href'))"
    )
    assert hrefs, "the page rendered no outline, so this check would pass over nothing"
    dangling = open_page.evaluate(
        f"Array.from(document.querySelectorAll('{site.OUTLINE_REGION} a'))"
        ".map(a => a.getAttribute('href'))"
        ".filter(h => !document.querySelector(h))"
    )
    assert dangling == [], f"outline links resolving to nothing without a script: {dangling}"


@pytest.mark.parametrize("case", site.pages())
def test_every_other_nav_region_points_off_the_page_rather_than_into_it(
    open_page: OpenPage, built_site: site.Site, case: str
) -> None:
    """⛔ The other half of Ruling 164's fork, asserted so the narrowing above holds.

    ⭐ An outline is **content** of the page it is on and every href it writes is
    a fragment; a bar, a unit listing and a contents tree are **chrome** pointing
    somewhere else, and not one of their hrefs is. ⚠️ Without this, the check
    above could be satisfied by a build that stopped emitting chrome at all.
    """
    open_page.open(built_site.url(case), scripts=False)
    selector = ", ".join(f"{region} a" for region in CHROME_NAVS)
    hrefs = list(
        open_page.evaluate(
            f"Array.from(document.querySelectorAll({selector!r})).map(a => a.getAttribute('href'))"
        )  # type: ignore[arg-type]
    )
    assert hrefs, f"{case} carries no chrome link at all, so this check would prove nothing"
    inward = [href for href in hrefs if str(href).startswith("#")]
    assert not inward, f"{case}: chrome pointing into its own page: {inward}"


def test_only_decoration_is_lost_when_scripts_are_off(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """What a scriptless reader gives up, named rather than discovered later.

    ⛔ Asserted in both directions. The copy button and the syntax colours are
    *expected* to be absent — so this fails if they are absent **with** scripts
    too, which would mean the check above was passing for the wrong reason.
    """
    url = built_site.url("depth2-unit-01")
    probe = (
        "[document.querySelectorAll('.copy').length, document.querySelectorAll('.token').length]"
    )
    open_page.open(url, scripts=True)
    with_scripts = list(open_page.evaluate(probe))  # type: ignore[arg-type]
    open_page.open(url, scripts=False)
    without = list(open_page.evaluate(probe))  # type: ignore[arg-type]
    assert with_scripts[0] > 0 and with_scripts[1] > 0, (
        f"with scripts ON the page has {with_scripts} copy buttons and tokens — "
        "the control for this check did not hold"
    )
    assert without == [0, 0], f"with scripts OFF the page still reports {without}"


def test_a_page_whose_prose_is_written_by_a_script_is_caught(
    open_page: OpenPage, damaged_sites: dict[str, site.Site]
) -> None:
    """⛔ Negative control: the `noscript` tree must fail the first check.

    ⚠️ It is the exact failure this clause exists to catch, and it is invisible
    to every other test in this repository: the page carries every word, the
    bytes are stable, the goldens match — and a reader with scripts off sees an
    empty column.
    """
    broken = damaged_sites["noscript"]
    open_page.open(broken.url("depth2-unit-01"), scripts=True)
    with_scripts = open_page.evaluate(TEXT_WITHOUT_DECORATION)
    open_page.open(broken.url("depth2-unit-01"), scripts=False)
    without = open_page.evaluate(TEXT_WITHOUT_DECORATION)
    assert with_scripts, "the control page is empty even with scripts on, so it proves nothing"
    assert without != with_scripts, (
        "a page whose prose is injected by a script read identically with scripts "
        "disabled — this harness cannot see the failure SF-14 is judged on"
    )
