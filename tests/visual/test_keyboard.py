"""Clause 3 — focus is driven with the Tab key, and followed where it goes.

⛔ **Real key events, not `element.focus()`.** Sequential focus navigation is the
browser's, not the page's: it decides what is tabbable, in what order, and
whether a `tabindex` took something out of the ring. A test that called `focus()`
on each link in turn would pass on a page no keyboard reader can use.
"""

from __future__ import annotations

import time

import pytest

from tests.visual import site
from tests.visual.page import SCHEMES, OpenPage

#: How many presses a traversal takes before giving up. Comfortably more than
#: the fixture pages need, so a page that grew a control still passes.
#: ⚠️ The index carries a skip link, a progress strip, an Up next slip and a
#: filter with two buttons ahead of its tree, and every one of them is a Tab
#: stop the walk has to pass before it reaches the rows.
PRESSES = 80


def _links_in_the_chrome(page: OpenPage) -> list[str]:
    """Every anchor any `nav` region offers a keyboard reader, in document order.

    ⭐ **Every region and not only the outline.** The tree carries a
    between-units bar, a container's unit listing and a root index tree, and a
    keyboard reader has to reach those too — reaching the outline and not the
    bar is a failure.

    ⛔ **An anchor inside a CLOSED `<details>` is not in the focus ring, and that
    is the browser's rule rather than this page's**. ⚠️ It was invisible
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
            # ⚠️ Only a summary the reader can SEE: the index now opens
            # just the group holding the next unit, so a closed group inside a
            # closed group is reached by opening its parent first, not by Tab.
            ".filter(s => s.checkVisibility())"
            ".map(s => s.textContent.trim().slice(0, 40))"
        )  # type: ignore[arg-type]
    )


@pytest.mark.parametrize("case", site.pages())
def test_every_chrome_link_is_reachable_by_tab_and_in_document_order(
    open_page: OpenPage, built_site: site.Site, case: str
) -> None:
    """A page's navigation is navigation only if a keyboard reader reaches all of it.

    ⭐ **Every page kind**, because the regions that carry a corpus's
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

    ⭐ **Every page kind** — `focus.css` is shared, but the regions it has to
    reach through are not: a row in a unit listing and a `<summary>` in the
    index's disclosure tree are both focusable.
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
    """⛔ The other half of the narrowing above, or it would be a retreat.

    ⭐ A closed `<details>` takes its links out of the focus ring and puts its own
    `<summary>` in — so the links are still reachable, in two keystrokes instead
    of one. ⚠️ A page whose disclosures were closed and whose summaries were NOT
    focusable would have navigation no keyboard reader can open, and the check
    above would report it as clean.

    ⛔ **One check over every page rather than one per page**, stating its
    denominator: most pages in this tree carry no closed disclosure, and a per-page
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


# --- the narration transport, operated without a mouse --------------

#: The transport's own region, and the controls it offers, spelled as the
#: renderer spells them. ⛔ Read from the page rather than listed: a control
#: added to the transport joins this check on the day it lands.
TRANSPORT = "footer#player"

#: Seconds the transport's live region may take to say which state it reached.
ANNOUNCE_TIMEOUT = 15.0

#: What the transport's state reads as, in one evaluation: what is lit, what the
#: live region says, and what has focus. ⚠️ `textContent` and not `innerText`
#: for the status region — ⛔ **an element with no layout box answers `innerText`
#: with its WHOLE text**, hidden children included (the zero-box class: on this
#: region the three state sentences come back at once from a region whose
#: computed `display` is `none`).
TRANSPORT_STATE = """
(() => {
  const player = document.querySelector('footer#player');
  if (!player) return null;
  const status = player.querySelector('[role="status"]');
  const said = Array.from(status ? status.children : [])
    .filter((s) => s.checkVisibility())
    .map((s) => s.textContent.trim());
  const active = document.activeElement;
  return {
    visible: player.checkVisibility(),
    controls: Array.from(player.querySelectorAll('button, select'))
      .filter((el) => el.checkVisibility())
      .map((el) => el.id),
    speaking: document.querySelectorAll('[data-speaking]').length,
    said: said,
    focus: active ? active.id : ''
  };
})()
"""


#: Where each of the transport's visible controls sits in document order — the
#: same identity `page.trail` records, so the two readings join on a position
#: rather than on a word.
TRANSPORT_POSITIONS = """
(() => {
  const all = Array.prototype.slice.call(document.querySelectorAll('*'));
  return Array.from(document.querySelectorAll('footer#player button, footer#player select'))
    .filter((el) => el.checkVisibility())
    .map((el) => all.indexOf(el));
})()
"""


def _transport(page: OpenPage) -> dict:
    """The transport's state now, or a failure saying the page carries none."""
    reading = page.evaluate(TRANSPORT_STATE)
    assert reading is not None, f"this page carries no {TRANSPORT}, so it judges nothing"
    return dict(reading)  # type: ignore[arg-type]


def test_every_narration_control_is_reachable_by_tab_and_in_document_order(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ *Keyboard operation of navigation, narration and practice*.

    ⭐ The transport ships `hidden` and `narration.js` reveals it, so this is a
    reading of the page a reader gets and not of the bytes on disk. ⚠️ The
    population is asserted inhabited first: a transport that stopped being
    revealed would otherwise make this pass over an empty list.
    """
    open_page.open(built_site.url("depth2-unit-01"))
    reading = _transport(open_page)
    assert reading["visible"], "the transport was never revealed, so this traverses nothing"
    assert reading["controls"], "the transport offers no control, so this judges nothing"
    # ⛔ Joined on POSITION and never on a label (this module's own `trail`): two of these controls
    # are a single typographic character and the
    # speed control's text is its whole option list, so a label join would have
    # read *"the keyboard reaches one of four"* about a transport it reaches all
    # of — a defect reported against the page instead of against the join.
    offered = list(open_page.evaluate(TRANSPORT_POSITIONS))
    assert offered, "the transport offers no control, so this judges nothing"
    hit = [step["at"] for step in open_page.trail(PRESSES) if step["at"] in offered]
    assert hit == offered, (
        f"tab order reached {len(hit)} of the transport's {len(offered)} controls, "
        f"at {hit} against {offered}"
    )


def test_the_narration_transport_answers_the_keyboard_and_keeps_focus_where_it_was(
    open_page: OpenPage, built_site: site.Site
) -> None:
    """⛔ Reaching a control is not operating it, and only one of the two is asserted above.

    ⭐ **Both directions in one reading**: before the press nothing is lit and
    the live region says nothing; after it something is lit and the region says
    which state the transport reached. ⚠️ This fixture ships no audio on disk,
    so what it reaches is the *no clip here* state — which is exactly the state
    a reader meets on a corpus that was never narrated, and it is announced
    rather than silent.

    ⛔ **Focus must not move.** A transport that re-rendered itself and dropped
    focus would return a keyboard reader to the top of the page on every press.
    """
    open_page.open(built_site.url("depth2-unit-01"))
    before = _transport(open_page)
    assert before["speaking"] == 0, "something was already lit before anything was pressed"
    assert before["said"] == [], f"the transport announced {before['said']} before any press"

    found = None
    open_page.focus_body()
    for _press in range(PRESSES):
        open_page.tab()
        if open_page.evaluate("document.activeElement.id") == "play":
            found = open_page.focused()
            break
    assert found is not None, f"{PRESSES} Tab presses never reached the play control"

    open_page.press(" ")
    after = _until_announced(open_page)
    assert after["speaking"] == 1, "pressing play with the keyboard lit no passage"
    assert after["focus"] == "play", f"the press moved focus to {after['focus']!r}"


def _until_announced(page: OpenPage) -> dict:
    """Poll the transport until its live region says something, or fail saying so.

    ⚠️ **Polled, because the state is reached asynchronously**: the element asks
    for a clip, the request fails, and only then does the transport say which
    state it is in. ⛔ A reading taken on the press itself is a reading taken
    before the answer and would report *"it announced nothing"* about a
    transport that announces correctly a moment later.
    """
    deadline = time.monotonic() + ANNOUNCE_TIMEOUT
    reading = _transport(page)
    while time.monotonic() < deadline:
        if reading["said"]:
            return reading
        time.sleep(0.05)
        reading = _transport(page)
    raise AssertionError(f"the transport changed state and told a screen reader nothing: {reading}")
