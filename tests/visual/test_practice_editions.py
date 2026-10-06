"""One practice in four languages: one card, a panel opening in the mode's language, a switch.

⭐ **Read where only a browser can read it.** The corpus declares four languages and a reading mode
for each; its practice unit holds one practice written in all four (four documents that name one
`edition`) and an ordinary practice beside them, each graded. Served from a loopback origin, the
page is opened in the headless browser and the clauses are driven by the real controls:

- the list holds ONE card for the four editions, titled with no language, naming them;
- the card opens its panel in the language of the mode chosen in the header, and in the next mode's
  language after the mode is changed;
- the switch at the top of the panel shows another edition (its statement, its panel, its file),
  and nothing else of the page moves;
- Submit posts the practice key of the edition shown;
- with scripts off every edition is on the page and the switch is not shown.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.studyforge.generate import four_corpus as four
from tests.studyforge.generate.test_practice_editions import practices
from tests.visual import panes, served
from tests.visual.four import CLEAR, SWITCH, built, served_from
from tests.visual.page import WIDE, OpenPage

UNIT = ".studyforge/demo/units/unit-01/unit-01-practices-1.unit.html"
SETTLE = 15.0

#: The card list, the open practice and the switch, as the page shows them.
READ = """
(() => {
  const shown = (el) => !!el && !el.hidden && el.checkVisibility();
  const cards = Array.from(document.querySelectorAll('li[data-practice-card]')).map((c) => ({
    title: c.querySelector('h3').textContent.trim(),
    editions: Array.from(c.querySelectorAll('[data-edition]'))
      .map(e => e.getAttribute('data-edition')),
    note: (c.querySelector('[data-practices-part="editions"]') || {innerText: null}).innerText,
    state: (c.querySelector('[data-practices-part="state"]') || {innerText: null}).innerText,
    greyed: c.hasAttribute('data-practice-lang')
  }));
  const statement = document.querySelector('section[data-kind][data-workspace-open]');
  const panel = document.querySelector('section[data-practice][data-workspace-open]');
  const row = panel ? panel.querySelector('[data-practice-part="editions"]') : null;
  const sections = Array.from(document.querySelectorAll('section[data-edition]'))
    .filter(s => shown(s) && s.hasAttribute('data-workspace-open'))
    .map(s => s.getAttribute('data-edition') + ':' +
      (s.hasAttribute('data-practice') ? 'panel' : 'statement'));
  return {
    cards,
    open: document.documentElement.hasAttribute('data-workspace-open'),
    title: (document.querySelector('[data-workspace-part="title"]') || {}).textContent,
    statementEdition: statement ? statement.getAttribute('data-edition') : null,
    statementId: statement ? statement.id : null,
    panelEdition: panel ? panel.getAttribute('data-edition') : null,
    panelKey: panel ? panel.getAttribute('data-practice') : null,
    rowShown: shown(row),
    rowAtTop: !!panel && panel.firstElementChild === row,
    buttons: row ? Array.from(row.querySelectorAll('button')).map(b => [
      b.getAttribute('data-edition-switch'), b.textContent, b.getAttribute('aria-pressed')]) : [],
    shownSections: sections,
    hash: location.hash,
    mode: document.documentElement.getAttribute('data-mode')
  };
})()
"""


@pytest.fixture(scope="module")
def origin(tmp_path_factory: pytest.TempPathFactory) -> Iterator[served.Served]:
    out = built(
        tmp_path_factory,
        "editions",
        four.declared(absent="grey"),
        units=practices("conversation"),
        code=True,
        graded=True,
    )
    with served_from(out) as running:
        yield running


def read(page: OpenPage) -> dict:
    return dict(page.evaluate(READ))  # type: ignore[call-overload]


def until(page: OpenPage, ready, what: str) -> dict:
    deadline = time.monotonic() + SETTLE
    reading = read(page)
    while time.monotonic() < deadline:
        if ready(reading):
            return reading
        time.sleep(0.05)
        reading = read(page)
    raise AssertionError(f"the page never {what}; it reads {reading}")


def start(page: OpenPage, origin: served.Served, mode: str) -> None:
    """Open the practice page with empty stores, then choose `mode` in the header."""
    page.resize(*WIDE)
    page.open(f"{origin.origin}/{UNIT}")
    page.evaluate(CLEAR)
    page.open(f"{origin.origin}/{UNIT}")
    page.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"{mode}\"]').click()")


def click(page: OpenPage, selector: str) -> None:
    page.evaluate(f"document.querySelector({selector!r}).click()")


def open_card(page: OpenPage, index: int = 0) -> dict:
    page.open_practice(index)
    return read(page)


def test_four_languages_are_one_card_titled_with_no_language(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    start(open_page, origin, "only-aa")
    reading = read(open_page)
    assert len(reading["cards"]) == 2, "one card for the four editions, one for the other"
    one = reading["cards"][0]
    assert one["title"] == "Keep a conversation"
    assert one["editions"] == ["aa", "bb", "cc", "dd"]
    assert one["note"] == "Available in: Aa, Bb, Cc, Dd."
    assert one["greyed"] is False
    other = reading["cards"][1]
    assert other["editions"] == [] and other["title"] == "A common practice"
    panes.capture(open_page, capture_dir, "editions-1-one-card.png")


@pytest.mark.parametrize("mode,lang", [("only-aa", "aa"), ("only-cc", "cc"), ("only-dd", "dd")])
def test_the_panel_opens_in_the_language_of_the_mode_chosen_in_the_header(
    open_page: OpenPage, origin: served.Served, capture_dir: Path, mode: str, lang: str
) -> None:
    start(open_page, origin, mode)
    reading = open_card(open_page)
    assert reading["mode"] == mode
    assert reading["statementEdition"] == lang and reading["panelEdition"] == lang
    assert reading["title"] == "Keep a conversation"
    assert sorted(reading["shownSections"]) == [f"{lang}:panel", f"{lang}:statement"]
    assert reading["rowShown"] and reading["rowAtTop"]
    assert [b[0] for b in reading["buttons"]] == ["aa", "bb", "cc", "dd"]
    assert [b[0] for b in reading["buttons"] if b[2] == "true"] == [lang]
    panes.capture(open_page, capture_dir, f"editions-2-opens-in-{lang}.png")


def test_changing_the_mode_and_opening_the_card_again_opens_the_new_language(
    open_page: OpenPage, origin: served.Served
) -> None:
    start(open_page, origin, "only-aa")
    assert open_card(open_page)["panelEdition"] == "aa"
    open_page.evaluate("document.querySelector('[data-workspace-act=\"close\"]').click()")
    open_page.evaluate(f"document.querySelector('{SWITCH} [data-mode-choice=\"only-bb\"]').click()")
    assert open_card(open_page)["panelEdition"] == "bb"


def test_the_switch_shows_another_edition_and_submit_grades_the_edition_shown(
    open_page: OpenPage, origin: served.Served, capture_dir: Path
) -> None:
    start(open_page, origin, "only-aa")
    first = open_card(open_page)
    click(open_page, 'section[data-practice][data-workspace-open] [data-edition-switch="cc"]')
    reading = until(open_page, lambda r: r["panelEdition"] == "cc", "showed the cc edition")
    assert reading["statementEdition"] == "cc"
    assert sorted(reading["shownSections"]) == ["cc:panel", "cc:statement"], "the aa pair is hidden"
    assert reading["title"] == first["title"], "the practice is the same one"
    assert [b[0] for b in reading["buttons"] if b[2] == "true"] == ["cc"]
    assert reading["panelKey"] != first["panelKey"], "each edition has its own practice key"
    assert reading["hash"] == "#" + reading["statementId"], "the edition is named in the address"
    assert reading["hash"] != first["hash"]
    panes.capture(open_page, capture_dir, "editions-3-switched-to-cc.png")

    origin.runs.started.clear()
    origin.runs.release.clear()
    origin.runs.asked.clear()
    click(open_page, 'section[data-practice][data-workspace-open] [data-practice-act="test"]')
    assert origin.runs.started.wait(SETTLE)
    origin.runs.release.set()
    time.sleep(0.3)
    posted = [one for one in origin.runs.asked if one.startswith("POST") and "/test/" in one]
    assert len(posted) == 1, origin.runs.asked
    assert posted[0].endswith("/" + reading["panelKey"]), (posted, reading["panelKey"])
    panes.capture(open_page, capture_dir, "editions-4-submit-on-cc.png")

    click(open_page, 'section[data-practice][data-workspace-open] [data-edition-switch="aa"]')
    back = until(open_page, lambda r: r["panelEdition"] == "aa", "showed the aa edition again")
    assert back["panelKey"] == first["panelKey"]


#: The reader's own record, as the state route answers it: which editions' sections have passed.
RECORD = """
(() => {
  const held = %s;
  const real = window.fetch.bind(window);
  window.fetch = (url, init) => String(url).includes('/api/v1/state/') &&
    String(url).includes('/units/')
    ? Promise.resolve(new Response(JSON.stringify({practices: held}), {status: 200}))
    : real(url, init);
})();
"""


def record(passed: list[str]) -> str:
    held = {key: {"passed": True} for key in passed}
    return RECORD % json.dumps(held)


@pytest.mark.parametrize(
    "passed,words,marked",
    [
        ([], "Not started", []),
        (["practice-prose", "practice-prose-3"], "Passed in 2 of 4 languages", ["aa", "cc"]),
        (
            ["practice-prose", "practice-prose-2", "practice-prose-3", "practice-prose-4"],
            "Passed in every language",
            ["aa", "bb", "cc", "dd"],
        ),
    ],
)
def test_the_card_summarises_the_editions_passed_and_marks_each_one(
    open_page: OpenPage,
    origin: served.Served,
    capture_dir: Path,
    passed: list[str],
    words: str,
    marked: list[str],
) -> None:
    open_page.resize(*WIDE)
    open_page.browser.call(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": record(passed)},
        session=open_page.session,
    )
    open_page.open(f"{origin.origin}/{UNIT}")
    got = until(
        open_page,
        lambda r: r["cards"][0]["state"] is not None and words in r["cards"][0]["state"],
        f"said {words!r}",
    )
    assert words in got["cards"][0]["state"]
    shown = open_page.evaluate(
        "Array.from(document.querySelectorAll('li[data-practice-card]:first-child [data-edition]'))"
        ".filter(e => e.getAttribute('data-edition-state') === 'passed')"
        ".map(e => e.getAttribute('data-edition'))"
    )
    assert shown == marked
    if passed:
        panes.capture(open_page, capture_dir, f"editions-5-progress-{len(passed)}.png")


def test_with_scripts_off_every_edition_is_on_the_page_and_the_switch_is_not(
    open_page: OpenPage, origin: served.Served
) -> None:
    open_page.resize(*WIDE)
    open_page.open(f"{origin.origin}/{UNIT}", scripts=False)
    found = open_page.evaluate(
        "(() => ({"
        " statements: document.querySelectorAll('section[data-kind][data-edition]').length,"
        " panels: document.querySelectorAll('section[data-practice][data-edition]').length,"
        " rows: Array.from(document.querySelectorAll('[data-practice-part=\"editions\"]'))"
        ".filter(r => r.closest('section[data-practice]') && r.checkVisibility()).length }))()"
    )
    assert found == {"statements": 4, "panels": 4, "rows": 0}
