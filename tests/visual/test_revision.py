"""A deck of flashcards and a spaced-review bank work in the PAGE, and keep their state in this
browser.

⭐ Every reading is taken over `file://` on a page a real build wrote (`mock_corpus` with a deck, or
a
quiz that declares `review`). What it asserts:

- a deck shows every card's front, hides every back until it is turned, marks a card known or to see
  again, counts what is known, filters to what is not, starts again, and keeps its marks across a
  reload; a store that throws changes nothing a reader sees; and nothing is requested of any origin;
- a bank shows what is due by `exercise.quiz.review.due`, whatever the stored streak and day, grades
a
  chosen answer in the page, files the streak, and shows a wrong item again at once and a right one
  not until its interval has passed.

⛔ **WHY THIS NEEDS A BROWSER.** The flip, the marks and the schedule exist only while a page runs.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from studyforge.exercise.quiz import Review, due
from tests.studyforge.exercise.quiz.mock_corpus import mock_corpus
from tests.studyforge.serve.routes.quizzing import page_of
from tests.visual.page import OpenPage

SETTLE = 3.0
CARDS = [
    {"id": f"c-{n}", "front": f"Front number {n}?", "back": f"Back number {n}."}
    for n in range(1, 5)
]
STEPS = (1, 3, 7)


@pytest.fixture(scope="module")
def deck_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    root = mock_corpus(
        tmp_path_factory.mktemp("deck-visual"), mock=False,
        kind="flashcards", questions=None, cards=CARDS,
    )
    return "file://" + str(page_of(root))


@pytest.fixture(scope="module")
def bank_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    root = mock_corpus(
        tmp_path_factory.mktemp("bank-visual"), mock=False, review={"intervals_days": list(STEPS)}
    )
    return "file://" + str(page_of(root))


def fresh(page: OpenPage, url: str) -> OpenPage:
    page.open(url)
    page.evaluate("localStorage.clear()")
    page.open(url)
    page.open_practice()
    return page


@pytest.fixture
def deck(open_page: OpenPage, deck_url: str):
    yield fresh(open_page, deck_url)
    open_page.evaluate("localStorage.clear()")


@pytest.fixture
def bank(open_page: OpenPage, bank_url: str):
    yield fresh(open_page, bank_url)
    open_page.evaluate("localStorage.clear()")


DECK_STATE = """
(() => {
  const root = document.querySelector('section[data-deck]');
  const part = (el, name) => el.querySelector('[data-deck-part="' + name + '"]');
  return {
    count: part(root, 'count').textContent.trim(),
    status: part(root, 'status').textContent.trim(),
    offline: !part(root, 'offline').hidden,
    controls: !part(root, 'controls').hidden,
    cards: Array.from(root.querySelectorAll('[data-deck-card]')).map((card) => ({
      hidden: card.hidden,
      state: card.getAttribute('data-deck-state'),
      backShown: !part(card, 'back').hidden,
      mark: part(card, 'mark').textContent.trim(),
    })),
    stored: localStorage.getItem('studyforge.deck.v1') || '',
    actions: root.querySelectorAll('[data-deck-act="flip"]').length,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  };
})()
"""


def read(page: OpenPage) -> dict:
    return page.evaluate(DECK_STATE)


def click(page: OpenPage, selector: str, index: int = 0) -> None:
    assert page.evaluate(
        f"(() => {{ const all = document.querySelectorAll({json.dumps(selector)});"
        f" if (!all[{index}]) return false; all[{index}].click(); return true; }})()"
    ) is True, selector


def test_a_deck_shows_every_front_and_hides_every_back_and_says_nothing_is_marked(deck):
    state = read(deck)
    assert state["count"] == "0 of 4 known" and state["status"] == ""
    assert state["controls"] and not state["offline"] and state["actions"] == 4
    assert all(
        not c["backShown"] and c["state"] is None and not c["hidden"] for c in state["cards"]
    )


def test_turning_a_card_shows_its_back_and_marks_are_kept_and_counted(deck):
    click(deck, '[data-deck-act="flip"]', 1)
    assert read(deck)["cards"][1]["backShown"] is True
    click(deck, '[data-deck-act="known"]', 1)
    click(deck, '[data-deck-act="again"]', 2)
    state = read(deck)
    assert state["count"] == "1 of 4 known"
    assert [c["state"] for c in state["cards"]] == [None, "known", "again", None]
    assert [c["mark"] for c in state["cards"]] == ["", "Known", "To see again", ""]
    assert json.loads(state["stored"])


def test_the_marks_survive_a_reload_and_start_again_forgets_them(deck, deck_url):
    click(deck, '[data-deck-act="known"]', 0)
    click(deck, '[data-deck-act="again"]', 3)
    deck.open(deck_url)
    deck.open_practice()
    assert [c["state"] for c in read(deck)["cards"]] == ["known", None, None, "again"]
    click(deck, '[data-deck-act="reset"]')
    state = read(deck)
    assert state["count"] == "0 of 4 known" and all(c["state"] is None for c in state["cards"])


def test_the_filter_shows_only_what_is_not_yet_known_and_every_card_known_says_so(deck):
    for index in range(4):
        click(deck, '[data-deck-act="known"]', index)
    assert read(deck)["status"] == "Every card is marked known."
    click(deck, '[data-deck-act="filter"]')
    state = read(deck)
    assert all(c["hidden"] for c in state["cards"])
    assert state["status"] in ("Every card is marked known.", "No card is left to see again.")
    click(deck, '[data-deck-act="reset"]')
    assert all(not c["hidden"] for c in read(deck)["cards"])


def test_a_store_that_refuses_changes_nothing_a_reader_sees(deck):
    deck.evaluate(
        "Storage.prototype.setItem = function () { throw new Error('refused'); }; true"
    )
    click(deck, '[data-deck-act="known"]', 0)
    state = read(deck)
    assert state["count"] == "1 of 4 known" and state["cards"][0]["state"] == "known"
    assert state["stored"] == ""


def test_a_deck_asks_no_origin_for_anything_and_scrolls_nowhere_sideways(deck):
    mark = len(deck.browser.events)
    click(deck, '[data-deck-act="known"]', 0)
    asked = [
        event["params"]["request"]["url"]
        for event in deck.browser.events[mark:]
        if event.get("method") == "Network.requestWillBeSent"
    ]
    assert asked == [] and read(deck)["overflow"] <= 0


BANK_STATE = """
(() => {
  const root = document.querySelector('section[data-review]');
  const part = (name) => root.querySelector('[data-review-part="' + name + '"]');
  const questions = Array.from(root.querySelectorAll('[data-practice-question]'));
  return {
    summary: part('summary').textContent.trim(),
    status: part('status').textContent.trim(),
    ids: questions.map((q) => q.getAttribute('data-practice-question')),
    due: questions.filter((q) => !q.hidden).map((q) => q.getAttribute('data-practice-question')),
    verdicts: questions.map((q) => q.getAttribute('data-review-verdict')),
    stored: JSON.parse(localStorage.getItem('studyforge.review.v1') || '{}'),
    check: !root.querySelector('[data-review-act="check"]').hidden,
    again: !root.querySelector('[data-review-act="again"]').hidden,
    offline: !part('offline').hidden,
    day: Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000),
  };
})()
"""


def bank_state(page: OpenPage) -> dict:
    return page.evaluate(BANK_STATE)


def seed(page: OpenPage, url: str, items: dict) -> None:
    key = page.evaluate(
        "document.querySelector('section[data-review]').getAttribute('data-practice-quiz')"
    )
    page.evaluate(
        "localStorage.setItem('studyforge.review.v1', "
        f"{json.dumps(json.dumps({key: items}))}); true"
    )
    page.open(url)
    page.open_practice()


COVER = """
(() => {
  const shell = document.querySelector('div[data-workspace]');
  const b = shell.getBoundingClientRect();
  const w = window.innerWidth, h = window.innerHeight;
  const at = (x, y) => {
    const hit = document.elementFromPoint(x, y);
    return !!(hit && hit.closest('div[data-workspace], section[data-workspace-open]'));
  };
  return {
    covers: b.left <= 0 && b.top <= 0 && b.right >= w && b.bottom >= h,
    hits: [at(8, h - 2), at(w / 2, h - 2), at(w - 8, h - 2), at(w / 2, h - 40)],
    markers: Array.from(document.querySelectorAll('ol[data-review-part="questions"]'))
      .map((ol) => getComputedStyle(ol).listStyleType),
    legends: Array.from(document.querySelectorAll('section[data-review] legend'))
      .map((l) => getComputedStyle(l, '::before').content),
  };
})()
"""


def test_the_overlay_covers_the_viewport_and_nothing_under_it_is_reachable_at_its_foot(
    deck, open_page, deck_url, bank_url
):
    for url in (deck_url, bank_url):
        fresh(open_page, url)
        reading = open_page.evaluate(COVER)
        assert reading["covers"], reading
        assert all(reading["hits"]), f"the page under the overlay is hit at its foot: {reading}"


def test_a_review_bank_shows_each_question_number_once(bank, open_page):
    reading = open_page.evaluate(COVER)
    assert reading["markers"] == ["none"], "the list also draws its own marker"
    assert reading["legends"] and all("counter(" in c for c in reading["legends"])


def test_a_deck_and_a_bank_are_kept_as_pictures(
    deck, bank, open_page, capture_dir, deck_url, bank_url
):
    fresh(open_page, deck_url)
    open_page.capture(capture_dir / "deck.png", whole=False)
    fresh(open_page, bank_url)
    open_page.capture(capture_dir / "review-bank.png", whole=False)
    open_page.evaluate("localStorage.clear()")


def test_a_new_bank_shows_every_question_and_says_none_has_been_seen(bank):
    state = bank_state(bank)
    assert state["due"] == state["ids"] and len(state["ids"]) >= 1
    assert state["summary"].endswith("none seen yet") and state["check"] and not state["offline"]


@pytest.mark.parametrize("streak", [0, 1, 2, 3, 5])
@pytest.mark.parametrize("age", [0, 1, 2, 3, 6, 7, 8, 40])
def test_what_is_due_is_what_the_python_rule_says_whatever_the_streak_and_the_age(
    bank, bank_url, streak, age
):
    ids = bank_state(bank)["ids"]
    today = bank_state(bank)["day"]
    items = {one: {"streak": streak, "last": today - age} for one in ids}
    seed(bank, bank_url, items)
    state = bank_state(bank)
    expected = due(Review(STEPS), streak, today - age, today)
    assert (state["due"] == ids) is expected, (streak, age, state["summary"])
    if not expected:
        assert state["due"] == [] and "Nothing is due now" in state["summary"]


def test_a_right_answer_files_a_streak_and_waits_and_a_wrong_one_is_due_again_at_once(bank):
    state = bank_state(bank)
    first, *others = state["ids"]
    chosen = bank.evaluate(
        """
(() => {
  const root = document.querySelector('section[data-review]');
  const key = JSON.parse(root.querySelector('[data-review-part="key"]').textContent);
  const picks = {};
  Array.from(root.querySelectorAll('[data-practice-question]')).forEach((q, i) => {
    const id = q.getAttribute('data-practice-question');
    const right = key[id].key;
    const wrong = Array.from(q.querySelectorAll('input')).map((r) => r.value)
      .find((v) => v !== right);
    const value = i === 0 ? right : wrong;
    q.querySelector('input[value="' + value + '"]').click();
    picks[id] = value;
  });
  root.querySelector('[data-review-act="check"]').click();
  return picks;
})()
"""
    )
    after = bank_state(bank)
    assert after["verdicts"][0] == "correct" and set(after["verdicts"][1:]) <= {"wrong"}
    assert after["again"] and not after["check"] and "answered correctly" in after["status"]
    stored = next(iter(after["stored"].values()))
    assert stored[first] == {"streak": 1, "last": after["day"]}
    assert all(stored[other] == {"streak": 0, "last": after["day"]} for other in others)
    assert chosen
    time.sleep(0.05)
    bank.evaluate("document.querySelector('[data-review-act=\"again\"]').click(); true")
    next_round = bank_state(bank)
    assert first not in next_round["due"] and next_round["due"] == others


def test_a_bank_forgets_its_schedule_on_request(bank):
    ids = bank_state(bank)["ids"]
    today = bank_state(bank)["day"]
    bank.evaluate(
        "localStorage.setItem('studyforge.review.v1', "
        + json.dumps(json.dumps({"x": {}}))
        + "); true"
    )
    click(bank, '[data-review-act="reset"]')
    state = bank_state(bank)
    assert state["due"] == ids and today == state["day"]
