"""The mock exam's exam form, read in a real browser: timer, navigator, flags, scenario cards,
multiple response, sittings that draw from a pool, and the results.

⭐ Every reading is taken over `file://` and over a served origin, on a page a real build wrote
(`form_corpus`: the course shape's twelve-question pool). The scoring rule is
`exercise.quiz.mock`; each score read off the page is compared with it.

**What it asserts.** The start panel offers the three sittings and begins none until asked; a
sitting draws the count its sitting names, whole scenarios kept together, by domain weight; the
exam layout shows one question at a time with its scenario card and a navigator whose numbers say
answered, open and flagged; a multiple-response question says how many to choose, stops at that
many and is scored all or nothing; the timer counts down, survives a reload (the start time is
stored), and submits by itself at zero; the order of the questions and of the options survives a
reload; a start again draws a new set that prefers questions not yet seen; the results give a
score per domain and per difficulty, the linear scaled line with its note, and every option's
sentence with the key marked; the review filters narrow to missed or flagged; nothing is requested
from any origin; phone width never scrolls sideways; and the exam works by keyboard.

⛔ WHY THIS NEEDS A BROWSER. The order, the timer, the draw and the stored state exist only while
a page is running.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from studyforge.exercise.quiz import mock_of, questions_of, scores, scores_by_difficulty
from tests.studyforge.exercise.quiz import mock_form
from tests.studyforge.exercise.quiz.mock_corpus import ORIGIN, form_corpus
from tests.studyforge.serve.routes.quizzing import page_of, served_instance
from tests.visual.page import OpenPage

SETTLE = 5.0
PLACES = ("as_file", "served")
WHERE = "the visual exam form"
POOL = mock_form.questions(ORIGIN)
QUESTIONS = questions_of(POOL, WHERE)
MOCK = mock_of(mock_form.mock(), WHERE)
KEYED = mock_form.keyed(POOL)

STATE = """
(() => {
  const exam = document.querySelector('section[data-mock-form]');
  if (!exam) return null;
  const part = (name) => exam.querySelector('[data-form-part="' + name + '"]');
  const shown = (el) => !!el && !el.hidden && el.checkVisibility();
  const text = (el) => (el ? el.textContent.trim() : null);
  const id = (el) => el.getAttribute('data-practice-question');
  const all = (root, selector) => Array.from(root.querySelectorAll(selector));
  const rows = (table) => all(table, 'tbody tr').map(
    (r) => [text(r.querySelector('th')), text(r.querySelector('td'))]);
  const items = all(exam, '[data-practice-question]');
  const visible = items.filter(shown);
  const first = visible[0];
  const within = (name) => (first ? first.querySelector('[data-form-part="' + name + '"]') : null);
  const card = within('scenario');
  const optionIds = (item) => all(item, '[data-practice-option]').map(
    (o) => o.getAttribute('data-practice-option'));
  const inputs = first ? all(first, 'input') : [];
  const shownText = (name) => (shown(part(name)) ? text(part(name)) : '');
  return {
    pool: items.length,
    drawn: items.filter((i) => !i.hasAttribute('data-form-out')).map(id),
    visible: visible.map(id),
    numbers: visible.map((i) => i.querySelector('legend').getAttribute('data-n')),
    start: shown(part('start')),
    sittings: all(exam, '[data-form-part="start"] label').map(text),
    bar: shown(part('bar')),
    timer: shown(part('timer')) ? text(part('timer')) : null,
    count: text(part('count')),
    navigator: shown(part('navigator')),
    nav: all(exam, '[data-form-part="number"]').filter(shown).map((b) => ({
      n: b.textContent, state: b.getAttribute('data-form-state'),
      flagged: b.getAttribute('data-flagged') === 'true',
      current: b.getAttribute('aria-current') === 'true',
      label: b.getAttribute('aria-label')})),
    pager: shown(part('pager')),
    previous: part('previous').disabled, next: part('next').disabled,
    card: card && shown(card) ? text(card) : null,
    difficulty: text(within('difficulty')),
    choose: text(within('choose')),
    kinds: inputs.map((i) => i.type),
    boxesDisabled: Object.fromEntries(inputs.map((i) => [i.value, i.disabled])),
    options: Object.fromEntries(items.map((i) => [id(i), optionIds(i)])),
    flagText: text(within('flag')),
    flagPressed: within('flag') ? within('flag').getAttribute('aria-pressed') : null,
    controls: shown(part('controls')), submit: shown(part('submit')), again: shown(part('again')),
    missing: shownText('missing'),
    result: shown(part('result')),
    overall: shownText('overall'),
    scaled: shownText('scaled'),
    scaledAttr: exam.getAttribute('data-mock-scaled'),
    domains: rows(part('domains')),
    difficulties: shown(part('difficulties')) ? rows(part('difficulties')) : [],
    verdicts: Object.fromEntries(
      items.map((i) => [id(i), i.getAttribute('data-practice-verdict')])),
    reviews: visible.map((i) => ({id: id(i),
      verdict: text(i.querySelector('[data-form-part="verdict"]')),
      rows: all(i, '[data-form-part="explanations"] li').map((l) => ({
        key: l.getAttribute('data-form-key'), chosen: l.getAttribute('data-form-chosen'),
        text: text(l)}))})),
    reviewNone: shown(part('review-none')),
    passedAttribute: exam.getAttribute('data-mock-passed'),
    kept: localStorage.getItem('studyforge.mockform.v1') || '',
    focus: (() => {
      const a = document.activeElement;
      return a ? (a.getAttribute('data-form-part') || a.tagName.toLowerCase()) : null;
    })(),
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
  };
})()
"""

CLICK = "document.querySelector('<selector>').click()"


def read_state(page: OpenPage) -> dict:
    return page.evaluate(STATE)


def click(page: OpenPage, selector: str) -> None:
    page.evaluate(CLICK.replace("<selector>", selector))
    time.sleep(0.05)


FLAG = 'li[data-practice-question]:not([hidden]) [data-form-part="flag"]'


def part(name: str) -> str:
    return f'[data-form-part="{name}"]'


def pick(page: OpenPage, question: str, option: str) -> None:
    click(page, f'[data-practice-question="{question}"] input[value="{option}"]')


def begin(page: OpenPage, sitting: str = "full") -> dict:
    page.evaluate(
        f"document.querySelector('[data-form-part=\"start\"] input[value=\"{sitting}\"]').click()"
    )
    click(page, part("begin"))
    return read_state(page)


def sit_with_question(page: OpenPage, question: str) -> None:
    """Begin full sittings, drawing afresh, until the draw holds `question`."""
    for _ in range(30):
        page.evaluate("localStorage.clear()")
        reopen(page)
        if question in begin(page, "full")["drawn"]:
            return
    raise AssertionError(f"{question} was not drawn in 30 full sittings")


def goto(page: OpenPage, number: int) -> None:
    click(page, f'{part("number")}[data-index="{number - 1}"]')


def answer_all(page: OpenPage, answers: dict, drawn: list[str]) -> None:
    for question in drawn:
        chosen = answers[question]
        for option in chosen if isinstance(chosen, list) else [chosen]:
            pick(page, question, option)


def asked_since(page: OpenPage, mark: int) -> list[str]:
    return [
        event["params"]["request"]["url"]
        for event in page.browser.events[mark:]
        if event.get("method") == "Network.requestWillBeSent"
        and not event["params"]["request"]["url"].endswith("/favicon.ico")
    ]


@pytest.fixture(scope="module")
def corpus(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return form_corpus(tmp_path_factory.mktemp("form-visual"))


@pytest.fixture(scope="module")
def origin(corpus: Path):
    with served_instance(corpus) as server:
        host, port = server.server_address[:2]
        relative = page_of(corpus).relative_to(corpus.parent).as_posix()
        yield f"http://{host}:{port}/{relative}"


def fresh(page: OpenPage, url: str) -> OpenPage:
    page.open(url)
    page.evaluate("localStorage.clear()")
    page.open(url)
    page.open_practice()
    return page


@pytest.fixture
def as_file(open_page: OpenPage, corpus: Path):
    yield fresh(open_page, "file://" + str(page_of(corpus)))
    open_page.evaluate("localStorage.clear()")


@pytest.fixture
def served(open_page: OpenPage, origin: str):
    yield fresh(open_page, origin)
    open_page.evaluate("localStorage.clear()")


def reopen(page: OpenPage) -> None:
    page.open(page.evaluate("location.href.split('#')[0]"))
    page.open_practice()


def reference(drawn: list[str], answers: dict):
    subset = tuple(q for q in QUESTIONS if q.id in drawn)
    return scores(subset, MOCK, answers)


# ------------------------------------------------------------------ the start and the draw


@pytest.mark.parametrize("where", PLACES)
def test_the_exam_offers_its_sittings_and_starts_none_until_asked(where, request):
    read = read_state(request.getfixturevalue(where))
    assert read["pool"] == 12 and read["start"] and not read["bar"] and not read["navigator"]
    assert read["visible"] == [] and read["kept"] == ""
    assert read["sittings"] == [
        "Full sitting: 10 questions, 40 minutes",
        "Short sitting: 5 questions, 20 minutes",
        "Scenario sitting: 2 scenarios, 16 minutes",
    ], read["sittings"]


@pytest.mark.parametrize("where", PLACES)
def test_the_full_sitting_draws_ten_by_weight_and_keeps_scenarios_whole(where, request):
    read = begin(request.getfixturevalue(where), "full")
    drawn = read["drawn"]
    assert len(drawn) == 10 and len(set(drawn)) == 10
    domains = [next(q.domain for q in QUESTIONS if q.id == one) for one in drawn]
    assert abs(domains.count("AS1") - 6) <= 1, "the draw is by the 60/40 weights"
    for scenario in {q.scenario for q in QUESTIONS if q.scenario}:
        mine = [q.id for q in QUESTIONS if q.scenario == scenario]
        held = [one in drawn for one in mine]
        assert all(held) or not any(held), f"scenario {scenario} was split: {held}"
    assert read["timer"] and read["timer"].startswith("40:0") or read["timer"].startswith("39:5")


@pytest.mark.parametrize("where", PLACES)
def test_the_short_sitting_draws_five_with_proportional_time(where, request):
    read = begin(request.getfixturevalue(where), "short")
    assert len(read["drawn"]) <= 5 and len(read["drawn"]) >= 3
    kept = json.loads(read["kept"])["exams"]
    state = next(iter(kept.values()))
    assert state["sitting"] == "short" and state["minutes"] == 20


@pytest.mark.parametrize("where", PLACES)
def test_the_scenario_sitting_draws_two_whole_scenarios(where, request):
    read = begin(request.getfixturevalue(where), "scenarios")
    assert len(read["drawn"]) == 4
    assert {next(q.scenario for q in QUESTIONS if q.id == one) for one in read["drawn"]}.issubset(
        {"support-bot", "report-tool", "night-job"}
    )
    assert len({next(q.scenario for q in QUESTIONS if q.id == one) for one in read["drawn"]}) == 2


# ------------------------------------------------------------------ the exam layout


@pytest.mark.parametrize("where", PLACES)
def test_the_exam_layout_shows_one_question_with_its_card_and_a_navigator(where, request):
    page = request.getfixturevalue(where)
    read = begin(page)
    assert len(read["visible"]) == 1 and read["numbers"] == ["1"]
    assert read["navigator"] and len(read["nav"]) == 10 and read["pager"]
    assert read["previous"] is True and read["next"] is False
    assert [n["state"] for n in read["nav"]] == ["open"] * 10
    assert read["nav"][0]["current"] and read["count"] == "0 of 10 answered"
    drawn = read["drawn"]
    scenario_first = next(i for i, one in enumerate(drawn)
                          if next(q.scenario for q in QUESTIONS if q.id == one))
    goto(page, scenario_first + 1)
    shown = read_state(page)
    assert shown["card"] and shown["visible"] == [drawn[scenario_first]]
    assert shown["difficulty"] in ("Foundational", "Applied", "Scenario, hard")


@pytest.mark.parametrize("where", PLACES)
def test_previous_and_next_walk_the_questions(where, request):
    page = request.getfixturevalue(where)
    drawn = begin(page)["drawn"]
    click(page, part("next"))
    read = read_state(page)
    assert read["visible"] == [drawn[1]] and read["numbers"] == ["2"] and read["previous"] is False
    click(page, part("previous"))
    assert read_state(page)["visible"] == [drawn[0]]


@pytest.mark.parametrize("where", PLACES)
def test_the_navigator_says_answered_open_and_flagged_and_filters(where, request):
    page = request.getfixturevalue(where)
    drawn = begin(page)["drawn"]
    first = next(q for q in QUESTIONS if q.id == drawn[0])
    keyed = KEYED[drawn[0]]
    pick(page, drawn[0], keyed[0] if isinstance(keyed, list) else keyed)
    click(page, FLAG)
    read = read_state(page)
    assert read["flagPressed"] == "true" and read["flagText"] == "Flagged for review"
    assert read["nav"][0]["flagged"] and read["nav"][0]["state"] in ("answered",)
    assert "flagged" in read["nav"][0]["label"] and "Question 1" in read["nav"][0]["label"]
    assert read["nav"][1]["state"] == "open" and "not answered" in read["nav"][1]["label"]
    click(page, part("filter-flagged"))
    assert [n["n"] for n in read_state(page)["nav"]] == ["1"]
    click(page, part("filter-flagged"))
    select = "document.querySelector('[data-form-part=\"filter-domain\"]')"
    page.evaluate(
        f"{select}.value = '{first.domain}';"
        f" {select}.dispatchEvent(new Event('change', {{bubbles: true}}))"
    )
    shown = [n["n"] for n in read_state(page)["nav"]]
    expected = [str(i + 1) for i, one in enumerate(drawn)
                if next(q.domain for q in QUESTIONS if q.id == one) == first.domain]
    assert shown == expected
    click(page, FLAG)
    assert read_state(page)["flagPressed"] == "false"


@pytest.mark.parametrize("where", PLACES)
def test_a_multiple_response_question_says_how_many_and_stops_at_that_many(where, request):
    page = request.getfixturevalue(where)
    sit_with_question(page, "p9")
    goto(page, read_state(page)["drawn"].index("p9") + 1)
    read = read_state(page)
    assert read["choose"] == "Choose 2." and read["kinds"] == ["checkbox"] * 4
    pick(page, "p9", "a")
    pick(page, "p9", "c")
    read = read_state(page)
    assert read["boxesDisabled"] == {"a": False, "b": True, "c": False, "d": True}, "extra boxes"
    pick(page, "p9", "c")
    assert read_state(page)["boxesDisabled"] == {"a": False, "b": False, "c": False, "d": False}


# ------------------------------------------------------------------ keeping state


@pytest.mark.parametrize("where", PLACES)
def test_a_reload_keeps_the_order_the_options_the_answers_the_flags_and_the_clock(where, request):
    page = request.getfixturevalue(where)
    before = begin(page)
    drawn = before["drawn"]
    pick(page, drawn[0], "b" if drawn[0] != "p9" else "a")
    click(page, FLAG)
    time.sleep(1.2)
    reopen(page)
    after = read_state(page)
    assert after["drawn"] == drawn and after["options"] == before["options"]
    assert not after["start"] and after["bar"] and after["count"] == "1 of 10 answered"
    assert after["nav"][0]["flagged"] and after["nav"][0]["state"] == "answered"
    assert after["timer"] != "40:00", "the clock did not run across the reload"
    kept = next(iter(json.loads(after["kept"])["exams"].values()))
    assert isinstance(kept["seed"], int) and kept["order"] == drawn


@pytest.mark.parametrize("where", PLACES)
def test_option_order_is_shuffled_per_sitting_and_a_question_can_keep_its_own(where, request):
    page = request.getfixturevalue(where)
    seen_orders = set()
    for _ in range(6):
        page.evaluate("localStorage.clear()")
        reopen(page)
        read = begin(page)
        seen_orders.add(json.dumps(read["options"][read["drawn"][0]]))
        assert read["options"]["p8"] == ["a", "b", "c"], "p8 keeps the order it was written in"
    assert len(seen_orders) > 1, "the options were never shuffled"


@pytest.mark.parametrize("where", PLACES)
def test_start_again_draws_a_new_set_that_prefers_questions_not_yet_seen(where, request):
    page = request.getfixturevalue(where)
    first = begin(page, "short")["drawn"]
    click(page, part("submit"))
    click(page, part("submit"))
    assert read_state(page)["result"]
    click(page, part("again"))
    start = read_state(page)
    assert start["start"] and not start["bar"] and start["visible"] == []
    second = begin(page, "short")["drawn"]
    assert len(set(first) & set(second)) <= 2, (first, second)
    held = json.loads(read_state(page)["kept"])["seen"]
    assert set(next(iter(held.values()))) >= set(first) | set(second)


# ------------------------------------------------------------------ the timer


@pytest.mark.parametrize("where", PLACES)
def test_time_up_submits_by_itself_and_a_reload_after_time_does_too(where, request):
    page = request.getfixturevalue(where)
    drawn = begin(page)["drawn"]
    pick(page, drawn[0], "b" if drawn[0] != "p9" else "a")
    page.evaluate(
        "(() => { const held = JSON.parse(localStorage.getItem('studyforge.mockform.v1'));"
        " const name = Object.keys(held.exams)[0];"
        " held.exams[name].started = Date.now() - 41 * 60000;"
        " localStorage.setItem('studyforge.mockform.v1', JSON.stringify(held)); })()"
    )
    reopen(page)
    deadline = time.monotonic() + SETTLE
    read = read_state(page)
    while not read["result"] and time.monotonic() < deadline:
        time.sleep(0.05)
        read = read_state(page)
    assert read["result"] and read["again"] and not read["submit"]
    assert read["count"].startswith("1 of 10"), "only the answered question counts as answered"
    assert json.loads(read["kept"])["exams"] and next(
        iter(json.loads(read["kept"])["exams"].values()))["submitted"] is True


@pytest.mark.parametrize("where", PLACES)
def test_the_timer_counts_down_while_the_page_is_open(where, request):
    page = request.getfixturevalue(where)
    begin(page)
    first = read_state(page)["timer"]
    time.sleep(2.2)
    assert read_state(page)["timer"] != first


# ------------------------------------------------------------------ the results


def finish(page: OpenPage, answers: dict) -> dict:
    drawn = read_state(page)["drawn"]
    answer_all(page, answers, drawn)
    click(page, part("submit"))
    return read_state(page)


@pytest.mark.parametrize("where", PLACES)
def test_a_perfect_sitting_scores_every_domain_difficulty_and_the_scale(where, request):
    page = request.getfixturevalue(where)
    begin(page, "full")
    mark = len(page.browser.events)
    read = finish(page, KEYED)
    assert asked_since(page, mark) == []
    whole, per_domain = reference(read["drawn"], KEYED)
    assert read["result"] and "you reached it" in read["overall"] and "(100%)" in read["overall"]
    assert [tuple(r) for r in read["domains"]] == [
        (d.title, f"{s.right} of {s.asked} ({s.percent}%)")
        for d, s in zip(MOCK.domains, per_domain, strict=True)
    ]
    assert len(read["difficulties"]) == 3
    assert all("100%" in r[1] or "0 of 0" in r[1] for r in read["difficulties"])
    assert read["scaled"].startswith("Scaled score: 1000 on a scale of 100 to 1000")
    assert "linear illustration" in read["scaled"]
    assert "not the exam's own scaling" in read["scaled"]
    assert read["passedAttribute"] == "true" and read["again"] and not read["submit"]


@pytest.mark.parametrize("where", PLACES)
def test_every_option_is_explained_with_the_key_marked_and_the_choice_shown(where, request):
    page = request.getfixturevalue(where)
    begin(page, "full")
    drawn = read_state(page)["drawn"]
    wrong = {q: ("a" if KEYED[q] != "a" and not isinstance(KEYED[q], list) else "c") for q in drawn}
    read = finish(page, wrong)
    assert read["result"]
    for review in read["reviews"]:
        assert review["rows"], review
        question = next(q for q in QUESTIONS if q.id == review["id"])
        assert len(review["rows"]) == len(question.options)
        keyed = [r for r in review["rows"] if r["key"] == "true"]
        assert len(keyed) == len(question.keys)
        assert all("Correct answer" in r["text"] for r in keyed)
        assert all(r["text"] for r in review["rows"])


@pytest.mark.parametrize("where", PLACES)
@pytest.mark.parametrize(
    "chosen,right",
    [(["a"], False), (["a", "c"], False), (["b", "d"], False), (["c", "d"], False),
     (["a", "b"], True), (["b", "a"], True)],
)
def test_a_multiple_response_question_is_scored_all_or_nothing(where, chosen, right, request):
    page = request.getfixturevalue(where)
    sit_with_question(page, "p9")
    drawn = read_state(page)["drawn"]
    answers = {**KEYED, "p9": chosen}
    read = finish(page, answers)
    assert read["verdicts"]["p9"] == ("correct" if right else "wrong")
    rows = next(r for r in read["reviews"] if r["id"] == "p9")["rows"]
    assert [r["chosen"] for r in rows].count("true") == len(chosen)
    whole, per_domain = reference(drawn, answers)
    assert whole.right == whole.asked - (0 if right else 1)
    assert f"You scored {whole.right} of {whole.asked} ({whole.percent}%)" in read["overall"]
    assert [tuple(r) for r in read["domains"]] == [
        (d.title, f"{s.right} of {s.asked} ({s.percent}%)")
        for d, s in zip(MOCK.domains, per_domain, strict=True)
    ]
    subset = tuple(q for q in QUESTIONS if q.id in drawn)
    by_difficulty = scores_by_difficulty(subset, MOCK, answers)
    assert [tuple(r) for r in read["difficulties"]] == [
        (d.title, f"{s.right} of {s.asked} ({s.percent}%)")
        for d, s in zip(MOCK.difficulties, by_difficulty, strict=True)
    ]
    applied = next(s for s in by_difficulty if s.domain == "applied")
    assert applied.right == applied.asked - (0 if right else 1)


@pytest.mark.parametrize("where", PLACES)
def test_the_results_label_the_key_and_the_readers_choice_in_sentence_case(where, request):
    page = request.getfixturevalue(where)
    sit_with_question(page, "p9")
    read = finish(page, {**KEYED, "p9": ["a", "c"]})
    rows = next(r for r in read["reviews"] if r["id"] == "p9")["rows"]
    heads = [r["text"].split(":")[0] if ":" in r["text"] else "" for r in rows]
    assert "Correct answer, your choice" in heads
    assert "Correct answer" in heads and "Your choice" in heads
    assert not any("Your choice" in h and "," in h for h in heads)


@pytest.mark.parametrize("where", PLACES)
def test_submitting_with_questions_open_asks_once_more_then_grades_them_wrong(where, request):
    page = request.getfixturevalue(where)
    drawn = begin(page, "full")["drawn"]
    pick(page, drawn[0], "b" if drawn[0] != "p9" else "a")
    click(page, part("submit"))
    read = read_state(page)
    assert read["missing"].startswith("Not answered yet: 2, 3") and not read["result"]
    click(page, part("submit"))
    read = read_state(page)
    assert read["result"] and "did not reach it" in read["overall"]


@pytest.mark.parametrize("where", PLACES)
def test_the_review_shows_only_missed_or_only_flagged_questions(where, request):
    page = request.getfixturevalue(where)
    drawn = begin(page, "full")["drawn"]
    flagged = drawn[2]
    goto(page, 3)
    click(page, FLAG)
    wrong = {q: (["a", "b"] if q == "p9" else KEYED[q]) for q in drawn}
    wrong[drawn[1]] = "c" if KEYED.get(drawn[1]) != "c" and drawn[1] != "p9" else "a"
    read = finish(page, {**wrong})
    missed = [q for q in drawn if read["verdicts"][q] == "wrong"]
    assert len(read["visible"]) == 10 and missed
    click(page, '[data-review="missed"]')
    assert read_state(page)["visible"] == missed
    click(page, '[data-review="flagged"]')
    assert read_state(page)["visible"] == [flagged]
    click(page, '[data-review="all"]')
    assert len(read_state(page)["visible"]) == 10


# ------------------------------------------------------------------ phone width and keyboard


@pytest.mark.parametrize("where", PLACES)
def test_the_exam_form_never_scrolls_sideways_at_phone_width(where, request):
    page = request.getfixturevalue(where)
    page.resize(390, 844)
    reopen(page)
    assert read_state(page)["overflow"] <= 0
    begin(page)
    assert read_state(page)["overflow"] <= 0
    read = finish(page, KEYED)
    assert read["result"] and read["overflow"] <= 0, read["overflow"]


@pytest.mark.parametrize("where", PLACES)
def test_the_exam_can_be_sat_by_keyboard_alone(where, request):
    page = request.getfixturevalue(where)
    page.evaluate("document.querySelector('[data-form-part=\"begin\"]').focus()")
    page.press("Enter")
    time.sleep(0.2)
    read = read_state(page)
    assert read["bar"] and read["visible"], "Enter on Begin did not begin"
    page.evaluate("document.querySelector('[data-form-part=\"next\"]').focus()")
    page.press("Enter")
    assert read_state(page)["numbers"] == ["2"]
    assert read_state(page)["focus"] == "legend"
    page.evaluate("document.querySelector('[data-form-part=\"number\"][data-index=\"4\"]').focus()")
    page.press("Enter")
    assert read_state(page)["numbers"] == ["5"]
    page.evaluate(f"document.querySelector('{FLAG}').focus()")
    page.press(" ")
    assert read_state(page)["flagPressed"] == "true"


# ------------------------------------------------------------------ the captures


def test_the_exam_form_is_captured(corpus: Path, open_page: OpenPage, capture_dir: Path):
    page = fresh(open_page, "file://" + str(page_of(corpus)))
    page.resize(900, 1100)
    page.capture(capture_dir / "01-start-panel.png")
    drawn = begin(page, "full")["drawn"]
    scenario_at = next(i for i, one in enumerate(drawn)
                       if next(q.scenario for q in QUESTIONS if q.id == one))
    goto(page, scenario_at + 1)
    pick(page, drawn[scenario_at], "b" if drawn[scenario_at] != "p9" else "a")
    page.capture(capture_dir / "02-exam-layout-scenario-card.png")
    click(page, FLAG)
    goto(page, 1)
    pick(page, drawn[0], "b" if drawn[0] != "p9" else "a")
    click(page, FLAG)
    page.capture(capture_dir / "03-navigator-with-flag.png")
    if "p9" in drawn:
        goto(page, drawn.index("p9") + 1)
        pick(page, "p9", "a")
        page.capture(capture_dir / "04-multiple-response.png")
    page.capture(capture_dir / "05-timer.png")
    answer_all(page, KEYED, drawn)
    click(page, part("submit"))
    page.capture(capture_dir / "06-results.png")
    click(page, '[data-review="missed"]')
    page.resize(390, 844)
    page.capture(capture_dir / "07-results-phone.png")


def test_the_exam_form_still_reads_with_scripts_off(corpus: Path, open_page: OpenPage):
    open_page.open("file://" + str(page_of(corpus)), scripts=False)
    html = open_page.html()
    assert html.count("<legend") >= 12 and "Scoring this exam needs this page's script" in html
    assert 'data-form-part="controls" hidden' in html, "a control shows that nothing can honour"
