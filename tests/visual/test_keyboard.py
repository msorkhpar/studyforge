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


def _links_in_the_outline(page: OpenPage) -> list[str]:
    """Every in-page anchor the outline offers, in document order."""
    return list(
        page.evaluate(
            "Array.from(document.querySelectorAll('nav[aria-label] a'))"
            ".map(a => a.getAttribute('href'))"
        )  # type: ignore[arg-type]
    )


def test_every_outline_link_is_reachable_by_tab_and_in_document_order(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """The outline is the page's own navigation; a keyboard reader must reach all of it."""
    case = "depth2-unit-01"
    open_page.open(built_site.url(case))
    expected = _links_in_the_outline(open_page)
    assert expected, "the page rendered no outline, so this check would prove nothing"
    reached = [step["label"] for step in open_page.trail(PRESSES)]
    hit = [label for label in reached if label in expected]
    assert hit == expected, f"tab order reached {hit}, the outline offers {expected}"


@pytest.mark.parametrize("scheme", SCHEMES)
def test_everything_focus_lands_on_shows_a_visible_focus_indicator(
    open_page: OpenPage, built_site: site.Site, scheme: str
) -> None:
    """⛔ In both themes: a focus ring that is invisible in dark is no ring.

    ⚠️ `outline-style: none` is the failure, and it is what a stylesheet gets
    when somebody removes the default ring and forgets to put one back.
    """
    open_page.open(built_site.url("depth2-unit-01"), scheme=scheme)
    invisible = [
        f"{step['tag']}.{step['label']}: outline {step['outline']}"
        for step in open_page.trail(PRESSES)
        if step["tag"] != "BODY" and step["outline"].startswith(("none", "hidden"))
    ]
    assert not invisible, f"{scheme}: focused with no visible ring: {invisible}"


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
    expected = _links_in_the_outline(open_page)
    assert expected, "the control page has no outline either, so it proves nothing"
    reached = [step["label"] for step in open_page.trail(PRESSES)]
    assert not [label for label in reached if label in expected], (
        "a page whose every control carries tabindex=-1 was traversed successfully — "
        f"reached {sorted(set(reached))}"
    )
