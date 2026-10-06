"""A mock exam is scored in the PAGE, per domain, and a reader can leave it and come back.

⭐ **Every reading is taken in TWO places and must come out the same**: over `file://` (the page a
reader double-clicks) and over a served origin, on a page a real build wrote
(`tests/studyforge/exercise/quiz/mock_corpus.py`). The rule the page implements is
`exercise.quiz.mock.scores`, and each score read off the page is compared with the reference's.

**What it asserts.** The progress line counts answers; a submit with a question open names each by
its number and grades nothing; a submit with every question answered shows a verdict and the chosen
option's sentence per question, a score per domain and the whole exam's score against the pass mark,
and asks nothing of any origin; a pass is kept as the card's pass and a fall short is not; the
answers survive a reload and a submitted exam reads as submitted until the reader starts again; and
at phone width nothing scrolls sideways.

⛔ **WHY THIS NEEDS A BROWSER.** What a reader is told about their score is a runtime identity: the
radios, the line that counts them, the table the script fills and the store that keeps the answers
exist only while a page is running.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from studyforge.exercise.quiz import mock_of, passed, questions_of, scores
from tests.studyforge.exercise.quiz import mock_exam
from tests.studyforge.exercise.quiz.mock_corpus import ORIGIN, mock_corpus
from tests.studyforge.serve.routes.quizzing import page_of, served_instance
from tests.visual.page import OpenPage

SETTLE = 5.0
PLACES = ("as_file", "served")
WHERE = "the visual mock exam"
QUESTIONS = questions_of(mock_exam.questions(ORIGIN), WHERE)
MOCK = mock_of(mock_exam.mock(), WHERE)

#: What the page is asked for. ⛔ Counted over the WHOLE DOCUMENT where a Run button would show.
STATE = """
(() => {
  const exam = document.querySelector('section[data-practice-mock]');
  if (!exam) return null;
  const part = (name) => exam.querySelector('[data-mock-part="' + name + '"]');
  const shown = (el) => !!el && !el.hidden && el.checkVisibility();
  const questions = Array.from(exam.querySelectorAll('[data-practice-question]'));
  const card = document.querySelector('[data-practice-kind="quiz"]');
  const slot = card && card.querySelector('[data-practices-part="state"]');
  const passedState = slot && slot.querySelector('[data-practice-state="passed"]');
  return {
    questions: questions.length,
    radios: exam.querySelectorAll('input[type="radio"]').length,
    acts: document.querySelectorAll('[data-practice-act]').length,
    frames: document.querySelectorAll('iframe').length,
    sharedCheck: !!exam.querySelector('[data-practice-part="check"]'),
    count: part('count').textContent.trim(),
    meter: part('meter').value,
    controls: shown(part('controls')),
    submit: shown(part('submit')),
    again: shown(part('again')),
    offline: shown(exam.querySelector('[data-practice-part="offline"]')),
    missing: shown(part('missing')) ? part('missing').textContent.trim() : '',
    result: shown(part('result')),
    overall: shown(part('result')) ? part('overall').textContent.trim() : '',
    domains: Array.from(part('domains').querySelectorAll('tbody tr')).map(
      (row) => [row.querySelector('th').textContent.trim(),
                row.querySelector('td').textContent.trim()]),
    verdicts: questions.map((one) => one.getAttribute('data-practice-verdict')),
    said: questions.map((one) => {
      const line = one.querySelector('[data-practice-part="says"]');
      return line.hidden ? '' : line.textContent.trim();
    }),
    locked: Array.from(exam.querySelectorAll('input[type="radio"]')).every((r) => r.disabled),
    anyLocked: Array.from(exam.querySelectorAll('input[type="radio"]')).some((r) => r.disabled),
    chosen: questions.map((one) => {
      const picked = one.querySelector('input[type="radio"]:checked');
      return picked ? picked.value : null;
    }),
    passedAttribute: exam.getAttribute('data-mock-passed'),
    cardPassed: !!slot && !slot.hidden && !!passedState && !passedState.hidden,
    keptQuizzes: localStorage.getItem('studyforge.quizzes.v1') || '',
    keptExam: localStorage.getItem('studyforge.mock.v1') || '',
    focusedId: (() => {
      const here = document.activeElement;
      const at = here && here.closest('[data-practice-question]');
      return at ? at.getAttribute('data-practice-question') : null;
    })(),
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
  };
})()
"""

CHOOSE = """
(() => {
  const exam = document.querySelector('section[data-practice-mock]');
  const want = <answers>;
  Object.keys(want).forEach((question) => {
    const at = exam.querySelector('[data-practice-question="' + question + '"]');
    at.querySelector('input[value="' + want[question] + '"]').click();
  });
  return true;
})()
"""

PRESS = "document.querySelector('[data-mock-part=\"<part>\"]').click()"


def read_state(page: OpenPage) -> dict:
    return page.evaluate(STATE)


def choose(page: OpenPage, answers: dict[str, str]) -> None:
    page.evaluate(CHOOSE.replace("<answers>", json.dumps(answers)))


def press(page: OpenPage, part: str) -> None:
    page.evaluate(PRESS.replace("<part>", part))


def asked_since(page: OpenPage, mark: int) -> list[str]:
    return [
        event["params"]["request"]["url"]
        for event in page.browser.events[mark:]
        if event.get("method") == "Network.requestWillBeSent"
        and not event["params"]["request"]["url"].endswith("/favicon.ico")
    ]


def settled(page: OpenPage, until) -> dict:
    deadline = time.monotonic() + SETTLE
    read = read_state(page)
    while not until(read) and time.monotonic() < deadline:
        time.sleep(0.05)
        read = read_state(page)
    return read


def submit(page: OpenPage, answers: dict[str, str]) -> tuple[dict, list[str]]:
    mark = len(page.browser.events)
    choose(page, answers)
    press(page, "submit")
    read = settled(page, lambda s: s["result"] or s["missing"])
    time.sleep(0.2)
    return read, asked_since(page, mark)


@pytest.fixture(scope="module")
def corpus(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return mock_corpus(tmp_path_factory.mktemp("mock-visual"))


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


def reference(answers: dict[str, str]):
    whole, per_domain = scores(QUESTIONS, MOCK, answers)
    rows = [
        (domain.title, f"{one.right} of {one.asked} ({one.percent}%)")
        for domain, one in zip(MOCK.domains, per_domain, strict=True)
    ]
    line = (
        f"You scored {whole.right} of {whole.asked} ({whole.percent}%). The pass mark is "
        f"{MOCK.pass_mark}%, and you {'reached' if passed(whole, MOCK) else 'did not reach'} it."
    )
    return whole, rows, line


@pytest.mark.parametrize("where", PLACES)
def test_the_exam_shows_its_questions_progress_and_controls_and_nothing_to_run(where, request):
    read = read_state(request.getfixturevalue(where))
    assert read is not None, "the page carries no mock exam"
    assert (read["questions"], read["radios"]) == (6, 18)
    assert (read["count"], read["meter"]) == ("0 of 6 answered", 0)
    assert (read["controls"], read["submit"], read["again"], read["offline"]) == (
        True,
        True,
        False,
        False,
    )
    assert (read["acts"], read["frames"], read["sharedCheck"]) == (0, 0, False)
    assert read["result"] is False and read["missing"] == ""


@pytest.mark.parametrize("where", PLACES)
def test_the_progress_line_counts_each_answer(where, request):
    page = request.getfixturevalue(where)
    choose(page, {"x1": "a", "x2": "b", "x3": "c"})
    read = read_state(page)
    assert (read["count"], read["meter"]) == ("3 of 6 answered", 3)
    choose(page, {"x1": "b"})
    assert read_state(page)["count"] == "3 of 6 answered", "changing an answer is not a new answer"


@pytest.mark.parametrize("where", PLACES)
def test_a_submit_with_questions_open_names_each_by_number_and_grades_nothing(where, request):
    page = request.getfixturevalue(where)
    read, asked = submit(page, {"x1": "a", "x3": "c", "x4": "a"})
    assert asked == []
    said = "Answer every question before you submit. Not answered yet: 2, 5 and 6."
    assert read["missing"] == said
    assert read["result"] is False and read["verdicts"] == [None] * 6
    assert read["focusedId"] == "x2", "focus did not go to the first question left open"
    assert not read["anyLocked"] and not read["cardPassed"] and read["keptQuizzes"] == ""


@pytest.mark.parametrize("where", PLACES)
def test_one_open_question_is_named_alone(where, request):
    page = request.getfixturevalue(where)
    answers = {**mock_exam.keyed()}
    del answers["x4"]
    read, _ = submit(page, answers)
    assert read["missing"].endswith("Not answered yet: 4.")


@pytest.mark.parametrize("where", PLACES)
def test_the_missing_line_goes_once_every_question_is_answered(where, request):
    page = request.getfixturevalue(where)
    submit(page, {"x1": "a"})
    assert read_state(page)["missing"] != ""
    choose(page, {key: value for key, value in mock_exam.keyed().items() if key != "x1"})
    assert read_state(page)["missing"] == ""


@pytest.mark.parametrize("where", PLACES)
def test_a_perfect_exam_scores_every_domain_full_passes_and_asks_nothing(where, request):
    page = request.getfixturevalue(where)
    read, asked = submit(page, mock_exam.keyed())
    assert asked == [], f"scoring an exam sent {asked}"
    whole, rows, line = reference(mock_exam.keyed())
    assert read["result"] and read["overall"] == line
    assert [tuple(row) for row in read["domains"]] == rows
    assert read["passedAttribute"] == "true" and passed(whole, MOCK)
    assert read["verdicts"] == ["correct"] * 6
    assert read["said"][0].startswith("Right. ") and read["said"][2].startswith("Right. ")
    assert read["locked"] and read["again"] and not read["submit"]
    assert read["cardPassed"] and read["keptQuizzes"]


@pytest.mark.parametrize("where", PLACES)
def test_a_score_is_read_per_domain_and_a_pass_needs_the_declared_mark(where, request):
    page = request.getfixturevalue(where)
    answers = {**mock_exam.keyed(), "x1": "b", "x2": "a", "x5": "a"}
    read, _ = submit(page, answers)
    _, rows, line = reference(answers)
    assert read["overall"] == line and "did not reach" in line
    assert [tuple(row) for row in read["domains"]] == rows
    assert [row[1] for row in read["domains"]] == ["0 of 2 (0%)", "2 of 2 (100%)", "1 of 2 (50%)"]
    assert read["passedAttribute"] == "false"
    assert read["verdicts"] == ["wrong", "wrong", "correct", "correct", "wrong", "correct"]
    assert read["said"][0].startswith("Not this one. ")
    assert not read["cardPassed"] and read["keptQuizzes"] == ""


@pytest.mark.parametrize("where", PLACES)
def test_the_pass_mark_is_reached_at_the_percent_it_names_and_rounds_down(where, request):
    page = request.getfixturevalue(where)
    answers = {**mock_exam.keyed(), "x1": "b", "x2": "a"}  # 4 of 6 is 66, over the mark of 60
    read, _ = submit(page, answers)
    assert read["overall"] == reference(answers)[2]
    assert "(66%)" in read["overall"] and "you reached it" in read["overall"].lower()
    assert read["cardPassed"]


@pytest.mark.parametrize("where", PLACES)
def test_the_key_sentence_of_a_wrong_choice_shows_its_own_not_the_keys(where, request):
    page = request.getfixturevalue(where)
    answers = {**mock_exam.keyed(), "x1": "b"}
    read, _ = submit(page, answers)
    assert "x1 option b" in read["said"][0] and "x1 option a" not in read["said"][0]


@pytest.mark.parametrize("where", PLACES)
def test_the_answers_survive_a_reload_and_a_returning_reader_carries_on(where, request):
    page = request.getfixturevalue(where)
    choose(page, {"x1": "a", "x4": "c"})
    assert json.loads(read_state(page)["keptExam"])["version"] == 1
    reopen(page)
    read = read_state(page)
    assert read["chosen"] == ["a", None, None, "c", None, None]
    assert (read["count"], read["meter"]) == ("2 of 6 answered", 2)
    assert not read["result"]


@pytest.mark.parametrize("where", PLACES)
def test_a_submitted_exam_stays_submitted_across_a_reload_until_started_again(where, request):
    page = request.getfixturevalue(where)
    submit(page, mock_exam.keyed())
    reopen(page)
    read = read_state(page)
    assert read["result"] and read["locked"] and read["again"] and not read["submit"]
    assert read["overall"] == reference(mock_exam.keyed())[2]
    press(page, "again")
    cleared = read_state(page)
    assert cleared["chosen"] == [None] * 6 and not cleared["result"] and not cleared["anyLocked"]
    assert (cleared["count"], cleared["verdicts"]) == ("0 of 6 answered", [None] * 6)
    assert cleared["submit"] and not cleared["again"]
    reopen(page)
    assert read_state(page)["chosen"] == [None] * 6, "starting again was not kept"


@pytest.mark.parametrize("where", PLACES)
def test_a_passed_exam_keeps_the_pass_across_a_reload(where, request):
    page = request.getfixturevalue(where)
    submit(page, mock_exam.keyed())
    reopen(page)
    assert read_state(page)["cardPassed"]


@pytest.mark.parametrize("where", PLACES)
def test_the_exam_works_at_phone_width_with_no_sideways_scroll(where, request):
    page = request.getfixturevalue(where)
    page.resize(390, 844)
    reopen(page)
    before = read_state(page)
    assert before["overflow"] <= 0, before["overflow"]
    read, _ = submit(page, {**mock_exam.keyed(), "x2": "a"})
    assert read["result"] and read["overflow"] <= 0, read["overflow"]
    sticky = page.evaluate(
        "getComputedStyle(document.querySelector('[data-mock-part=\"progress\"]')).position"
    )
    assert sticky == "sticky"


def test_the_exam_still_reads_with_scripts_off(corpus: Path, open_page: OpenPage):
    open_page.open("file://" + str(page_of(corpus)), scripts=False)
    html = open_page.html()
    assert html.count("<legend>") >= 6 and "Scoring this exam needs this page's script" in html
    assert 'data-mock-part="controls" hidden' in html, "a control shows that nothing can honour"
