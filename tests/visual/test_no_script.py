"""Clause 4 — the page is run with JavaScript disabled, and still reads.

⛔ **The reading floor, made runnable.** The reading floor is a page opened from a file with no
server; a reader who has scripts off,
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
#: kind emits and every kind fills from the material.
PROSE = {
    "depth2-unit-01": "A class is a name plus the state and behaviour filed under it.",
    "depth1-unit-02": None,
}

#: The masthead's own words — region 1, and the one region every page kind emits.
#: ⛔ Read from the page rather than listed per fixture: it is a corpus's text, so
#: a sentence typed here would be a third copy of two fixtures' titles.
#:
#: ⚠️ The top bar and the search dialog are inside the masthead and are NOT the masthead's words:
#: their controls ship `hidden` and the page script reveals them, so reading them here would
#: make this check say "the masthead is script-dependent" about the regions that are supposed
#: to appear only when a script can back them. ⛔ Excluded by the hook they carry, not by their
#: words, so renaming a label cannot re-admit them.
MASTHEAD = (
    "Array.from(document.querySelector('header').children)"
    ".filter(el => !el.matches('[data-section=\"topbar\"], [data-section=\"search\"]'))"
    ".map(el => el.innerText).join(' ').replace(/\\s+/g, ' ').trim()"
)

#: Every `nav` region that is NOT the outline, as a selector. ⛔ Derived from the
#: disposition table so the two halves — content and chrome — are one population
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
    in its population now, and a `.get` over a hand-written mapping is a
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

    ⭐ **Every page kind** — a container's unit listing and the root
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

    ⛔ **Scoped to the outline.** Over `nav[aria-label] a` it would ask
    `document.querySelector('../../index.html')`, which is not a selector at all,
    so any page carrying a between-units bar, a unit listing or a contents tree
    would throw. ⭐ The narrowing is a
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
    """⛔ The chrome half, asserted so the narrowing above holds.

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
        "disabled — this harness cannot see a page that needs a script to read"
    )


# --- the index works with JavaScript disabled ----------------------------------

#: How many presses a traversal of an index takes before giving up. ⛔ Spelled
#: here rather than imported from `test_keyboard`: one test module importing
#: another's constant joins two populations that have no reason to move together.
PRESSES = 100

#: The page kinds `site` names, so the index pages are asked for rather than
#: matched on a name (a fixture's name is a corpus's text, this framework's
#: kinds are not — `site.UNIT`, `site.INDEX`).
INDEX_PAGES = tuple(case for case in site.pages() if site.kind_of(case) == site.INDEX)

#: Every entry the root index offers, with the href it carries, read off the
#: rendered page. ⛔ Only what a reader can SEE: an entry inside a closed
#: disclosure is reached by opening the disclosure first, and this check's
#: companion below is the one that asserts a disclosure can be opened at all.
INDEX_ENTRIES = """
Array.from(document.querySelectorAll('nav[aria-label] a'))
  .filter(a => a.checkVisibility())
  .map(a => a.getAttribute('href'))
"""

#: Whether a disclosure this reader can see is shut, and where it sits.
FIRST_SHUT_SUMMARY = """
(() => {
  const all = Array.prototype.slice.call(document.querySelectorAll('*'));
  const summary = Array.from(document.querySelectorAll('details:not([open]) > summary'))
    .filter(s => s.checkVisibility())[0];
  if (!summary) return null;
  return {at: all.indexOf(summary), open: summary.parentElement.open};
})()
"""


@pytest.mark.parametrize("case", INDEX_PAGES)
def test_every_entry_the_index_offers_resolves_to_a_page_on_disk_with_scripts_off(
    open_page: OpenPage, built_site: site.Site, case: str
) -> None:
    """⛔ *The index works with JavaScript disabled*.

    ⭐ **Resolved against the TREE, not against the document.** An index's
    entries point off the page, so `document.querySelector(href)` — the outline
    check's instrument — is not a question that can be asked of them; what
    *works* means for a contents tree is that the file it names is there.
    ⚠️ Which is a reading only this harness can take: it holds the built tree on
    disk, and R8's floor is a reader double-clicking into exactly this page.

    ⛔ **Narrowed to the pages this harness WROTE, and the narrowing is stated
    rather than quiet.** `site` writes one unit page per fixture corpus — the
    tree exists to exercise the three renderers, not to be a whole corpus — so
    most of a contents tree points at units nobody built here and "the file is
    missing" would be a fact about the fixture and not about the index.
    ⭐ Whole-site resolution IS checked, over a real `studyforge build`, by
    `tests/studyforge/cli/test_serve_floor.py`; this is the SCRIPTLESS half of
    the same question and the two do not overlap.
    """
    open_page.open(built_site.url(case), scripts=False)
    hrefs = [str(href) for href in open_page.evaluate(INDEX_ENTRIES)]  # type: ignore[union-attr]
    assert hrefs, f"{case} offered no entry with scripts off, so this resolves nothing"
    root = built_site.root.resolve()
    here = built_site.path(case).parent
    written = {str(built.page) for built in site.pages_built()}
    reached, dangling = [], []
    for href in hrefs:
        target = (here / href.split("#", 1)[0].split("?", 1)[0]).resolve()
        if not target.is_relative_to(root):
            dangling.append(f"{href} (leaves the tree)")
            continue
        if target.relative_to(root).as_posix() not in written:
            continue
        reached.append(href)
        if not target.is_file():
            dangling.append(f"{href} (no such file)")
    assert reached, (
        f"{case} names none of the pages this tree wrote, so this check resolves "
        "nothing — the index's hrefs and the tree's paths stopped agreeing"
    )
    assert not dangling, f"{case} with scripts off names files that are not there: {dangling}"


def test_a_closed_group_in_the_index_opens_from_the_keyboard_with_scripts_off(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ The disclosure is `<details>`, so opening it is the browser's, not a script's.

    ⛔ **Both directions in one reading**: shut before the press and open after
    it. A check that only read the second half would pass on a tree whose
    groups were open to begin with — which is the state `render.index.policy`
    puts a small corpus in, and the reason the shut one is asserted first.

    ⛔ **One check over every index rather than one per index** (`test_keyboard`'s
    own precedent one region along): a small corpus
    has every group open, so a parametrised version would SKIP on it — a named
    skip in every run of the whole suite, for a population that is inhabited on
    one page. ⭐ The inhabitation is asserted first, so the press can never pass
    over nothing.
    """
    opened: dict[str, bool] = {}
    for case in INDEX_PAGES:
        open_page.open(built_site.url(case), scripts=False)
        shut = open_page.evaluate(FIRST_SHUT_SUMMARY)
        if shut is None:
            continue
        where = dict(shut)  # type: ignore[arg-type]
        assert where["open"] is False, f"{case}: the group this check found was already open"
        open_page.focus_body()
        for _press in range(PRESSES):
            open_page.tab()
            if open_page.focused()["at"] == where["at"]:
                break
        else:
            raise AssertionError(f"{PRESSES} Tab presses never reached the shut group in {case}")
        open_page.press("Enter")
        opened[case] = bool(open_page.evaluate("document.activeElement.parentElement.open"))
    assert opened, (
        "no index in this tree carries a closed group, so this check asserts nothing "
        "— the index policy opened them all, or the tree stopped emitting a disclosure"
    )
    assert all(opened.values()), (
        f"a shut group did not open when Enter was pressed on it with scripts off: {opened}"
    )
