"""Clause 3 — focus is driven with the Tab key, and followed where it goes.

⛔ **Real key events, not `element.focus()`.** Sequential focus navigation is the
browser's, not the page's: it decides what is tabbable, in what order, and
whether a `tabindex` took something out of the ring. A test that called `focus()`
on each link in turn would pass on a page no keyboard reader can use, which is
the failure `SF-24` will be judged on.
"""

from __future__ import annotations

import pytest

from tests.visual import site
from tests.visual.page import SCHEMES, OpenPage

#: How many presses a traversal takes before giving up. Comfortably more than
#: the fixture pages need, so a page that grew a control still passes.
PRESSES = 40


def _links_in_the_chrome(page: OpenPage) -> list[str]:
    """Every anchor any `nav` region offers a keyboard reader, in document order.

    ⭐ **Every region and not only the outline, which is what it used to be.**
    Since `W98` the tree carries a between-units bar, a container's unit listing
    and a root index tree, and a keyboard reader has to reach those too — reaching
    the outline and not the bar is the failure `SF-24` is judged on.

    ⛔ **An anchor inside a CLOSED `<details>` is not in the focus ring, and that
    is the browser's rule rather than this page's** (`W324`). ⚠️ It was invisible
    here only because no tree this harness opened had ever held a closed
    disclosure: `render.index.policy` opens every level of a corpus small enough,
    and both fixtures are. ⭐ So the population is what a reader can REACH, and
    `test_every_closed_disclosure_is_itself_reachable_by_tab` below asserts the
    other half — that nothing is hidden without an affordance in the ring.
    """
    return list(
        page.evaluate(
            "Array.from(document.querySelectorAll('nav[aria-label] a'))"
            ".filter(a => !a.closest('details:not([open])'))"
            ".map(a => a.getAttribute('href'))"
        )  # type: ignore[arg-type]
    )


def _closed_disclosures(page: OpenPage) -> list[str]:
    """Every `<summary>` in the chrome whose disclosure is shut, in document order."""
    return list(
        page.evaluate(
            "Array.from(document.querySelectorAll("
            "'nav[aria-label] details:not([open]) > summary'))"
            ".map(s => s.textContent.trim().slice(0, 40))"
        )  # type: ignore[arg-type]
    )


@pytest.mark.parametrize("case", site.pages())
def test_every_chrome_link_is_reachable_by_tab_and_in_document_order(
    open_page: OpenPage, built_site: site.Site, case: str
) -> None:
    """A page's navigation is navigation only if a keyboard reader reaches all of it.

    ⭐ **Every page kind since `W98`**, because the regions that carry a corpus's
    navigation are on the other two: a container's unit listing is the only way
    down from a section page, and the root index tree is the only way in.
    """
    open_page.open(built_site.url(case))
    expected = _links_in_the_chrome(open_page)
    assert expected, f"{case} rendered no navigation at all, so this check would prove nothing"
    reached = [step["label"] for step in open_page.trail(PRESSES)]
    hit = [label for label in reached if label in expected]
    assert hit == expected, f"{case}: tab order reached {hit}, the chrome offers {expected}"


@pytest.mark.parametrize("case", site.pages())
@pytest.mark.parametrize("scheme", SCHEMES)
def test_everything_focus_lands_on_shows_a_visible_focus_indicator(
    open_page: OpenPage, built_site: site.Site, scheme: str, case: str
) -> None:
    """⛔ In both themes: a focus ring that is invisible in dark is no ring.

    ⚠️ `outline-style: none` is the failure, and it is what a stylesheet gets
    when somebody removes the default ring and forgets to put one back.

    ⭐ **Every page kind since `W98`** — `focus.css` is shared, but the regions
    it has to reach through are not: a row in a unit listing and a `<summary>` in
    the index's disclosure tree are both focusable and neither was ever opened.
    """
    open_page.open(built_site.url(case), scheme=scheme)
    invisible = [
        f"{step['tag']}.{step['label']}: outline {step['outline']}"
        for step in open_page.trail(PRESSES)
        if step["tag"] != "BODY" and step["outline"].startswith(("none", "hidden"))
    ]
    assert not invisible, f"{case} in {scheme}: focused with no visible ring: {invisible}"


def test_shift_tab_walks_back_the_way_tab_walked_forward(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⭐ The cheap proof that focus order is an order and not a list of stops."""
    open_page.open(built_site.url("depth2-unit-01"))
    forward = [step["label"] for step in open_page.trail(4)]
    open_page.tab(backwards=True)
    assert open_page.focused()["label"] == forward[-2], (
        f"after four Tabs and one Shift+Tab focus is on {open_page.focused()['label']!r}, "
        f"not back on {forward[-2]!r}"
    )


def test_the_traversal_notices_a_page_nothing_can_be_tabbed_to(
    open_page: OpenPage, damaged_sites: dict[str, site.Site]
) -> None:
    """⛔ Negative control: `tabindex="-1"` everywhere must fail the check above.

    ⚠️ This is the control that is easy to get wrong, because a page with no
    tabbable content still *answers* every question — `document.activeElement`
    is `<body>` and a naive harness reports a clean traversal of nothing.
    """
    broken = damaged_sites["keyboard"]
    open_page.open(broken.url("depth2-unit-01"))
    expected = _links_in_the_chrome(open_page)
    assert expected, "the control page has no navigation either, so it proves nothing"
    reached = [step["label"] for step in open_page.trail(PRESSES)]
    assert not [label for label in reached if label in expected], (
        "a page whose every control carries tabindex=-1 was traversed successfully — "
        f"reached {sorted(set(reached))}"
    )


def test_every_closed_disclosure_in_the_tree_is_itself_reachable_by_tab(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ The other half of the narrowing above (`W324`), or it would be a retreat.

    ⭐ A closed `<details>` takes its links out of the focus ring and puts its own
    `<summary>` in — so the links are still reachable, in two keystrokes instead
    of one. ⚠️ A page whose disclosures were closed and whose summaries were NOT
    focusable would have navigation no keyboard reader can open, and the check
    above would report it as clean.

    ⛔ **One check over every page rather than one per page** (Ruling 48's shape
    here): most pages in this tree carry no closed disclosure, and a per-page
    version would skip on each of them — seven named skips in every run of the
    whole suite, for a population that is inhabited on one page. ⭐ The
    inhabitation is asserted first, so the walk can never pass over nothing.
    """
    found: dict[str, list[str]] = {}
    missed: dict[str, list[str]] = {}
    for case in site.pages():
        open_page.open(built_site.url(case))
        shut = _closed_disclosures(open_page)
        if not shut:
            continue
        found[case] = shut
        reached = [step["label"] for step in open_page.trail(PRESSES)]
        absent = [label for label in shut if label not in reached]
        if absent:
            missed[case] = absent
    assert found, (
        "no page in this tree carries a closed disclosure, so this check asserts "
        "nothing — the rail stopped emitting one, or the index policy opened them all"
    )
    assert not missed, f"closed disclosures no Tab reaches: {missed}"
