"""A quiz shows its questions, the PAGE grades them, and nothing is asked of any origin.

⭐ **The user's ruling (2026-09-25): a quiz's answers remain in its own page, in
a script local to that page, and nothing about a quiz is a server function.**
It reverses the ruling that kept the key on the local study server. ⭐ So every
reading here is taken in TWO places and must come out the SAME:

- **over `file://`** — the page a reader double-clicks;
- **over a served origin** — `studyforge serve`'s own instance
  (`serve.instance.instance_of`) over the BUILT prose fixture with a quiz in it.

In both, a right answer and a wrong answer each show the page's verdict and
the chosen option's sentence, the verdicts are the ones the rule's reference
(`exercise.quiz.grading.grade`) gives the same answers, ⛔ the network log shows
NO request from choosing or checking, and a complete quiz is kept as *passed*
in the reader's browser store, so its card reads *passed* after a reload.

⭐ A quiz opens in the workspace in ONE column — its intro above its questions —
where a code practice keeps its split.

⛔ **WHY THIS NEEDS A BROWSER.** Whether a reader who chooses an answer is told
the right thing about it is a runtime identity: the radios, the sentence that
appears under a question, the line that counts them and the store that keeps
the pass exist only while a page is running.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from studyforge.exercise.quiz.grading import grade
from studyforge.exercise.quiz.questions import questions_of
from tests.studyforge.serve.routes.quizzing import (
    KEYED,
    QUESTIONS,
    WRONG,
    page_of,
    quiz_corpus,
    says,
    served_instance,
)
from tests.visual.page import NARROW, WIDE, OpenPage

#: Seconds a reading waits for the page's verdict to land.
SETTLE = 5.0

#: Both places a quiz is read, by fixture name.
PLACES = ("as_file", "served")

#: What the page is asked for, once it has settled.
#:
#: ⛔ **`acts` and `frames` are counted over the WHOLE DOCUMENT and not over the
#: quiz**: a Run button emitted BESIDE the quiz section would leave a scoped
#: version of this reading GREEN.
STATE = """
(() => {
  const quiz = document.querySelector('section[data-practice-quiz]');
  if (!quiz) return null;
  const part = (name) => quiz.querySelector('[data-practice-part="' + name + '"]');
  const questions = Array.from(quiz.querySelectorAll('[data-practice-question]'));
  const card = document.querySelector('[data-practice-kind="quiz"]');
  const slot = card && card.querySelector('[data-practices-part="state"]');
  const passed = slot && slot.querySelector('[data-practice-state="passed"]');
  return {
    questions: questions.length,
    radios: quiz.querySelectorAll('input[type="radio"]').length,
    acts: document.querySelectorAll('[data-practice-act]').length,
    frames: document.querySelectorAll('iframe').length,
    disabled: quiz.querySelectorAll('[disabled], [aria-disabled="true"]').length,
    check: !!part('check') && part('check').checkVisibility(),
    offline: !!part('offline') && part('offline').checkVisibility(),
    status: part('status').textContent.trim(),
    verdicts: questions.map((one) => one.getAttribute('data-practice-verdict')),
    said: questions.map((one) => {
      const line = one.querySelector('[data-practice-part="says"]');
      return line.hidden ? '' : line.textContent.trim();
    }),
    shown: quiz.innerText,
    cardPassed: !!slot && !slot.hidden && !!passed && !passed.hidden,
    kept: localStorage.getItem('studyforge.quizzes.v1') || ''
  };
})()
"""

#: Choose one option per question by its id, the way a reader's click does.
#: ⛔ A real `click()` on the input and a real `change` event.
CHOOSE = """
(() => {
  const quiz = document.querySelector('section[data-practice-quiz]');
  const want = <answers>;
  Object.keys(want).forEach((question) => {
    const at = quiz.querySelector('[data-practice-question="' + question + '"]');
    at.querySelector('input[value="' + want[question] + '"]').click();
  });
  return true;
})()
"""

#: Press the control that grades, as a reader's click does.
CHECK = "document.querySelector('[data-practice-part=\"check\"]').click()"

#: The quiz's own key, as the page carries it.
QUIZ_KEY = (
    "document.querySelector('section[data-practice-quiz]').getAttribute('data-practice-quiz')"
)


def choose(page: OpenPage, answers: dict[str, str]) -> None:
    page.evaluate(CHOOSE.replace("<answers>", json.dumps(answers)))


def settled(page: OpenPage, until) -> dict:
    """Read the page until `until(state)` holds or `SETTLE` runs out; return the last reading."""
    deadline = time.monotonic() + SETTLE
    state = page.evaluate(STATE)
    while not until(state) and time.monotonic() < deadline:
        time.sleep(0.05)
        state = page.evaluate(STATE)
    return state


def graded(state: dict) -> bool:
    return bool(state) and state["status"] != ""


def asked_since(page: OpenPage, mark: int) -> list[str]:
    """Every request the page issued after event `mark` — the network log's reading.

    ⚠️ The browser's own late ask for the origin's icon is not the page's, and
    it lands whenever the browser gets to it: it is left out by its path alone.
    """
    return [
        event["params"]["request"]["url"]
        for event in page.browser.events[mark:]
        if event.get("method") == "Network.requestWillBeSent"
        and not event["params"]["request"]["url"].endswith("/favicon.ico")
    ]


def answer(page: OpenPage, answers: dict[str, str]) -> tuple[dict, list[str]]:
    """Choose `answers`, press Check, and return the settled state and what was asked."""
    mark = len(page.browser.events)
    choose(page, answers)
    page.evaluate(CHECK)
    state = settled(page, graded)
    time.sleep(0.2)  # ⭐ room for a request the check might have sent late
    return state, asked_since(page, mark)


def reference(answers: dict[str, str]):
    """The rule's reference verdict for the same answers (`exercise.quiz.grading`)."""
    return grade(questions_of(QUESTIONS, "the visual quiz"), answers)


@pytest.fixture(scope="module")
def corpus(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The prose fixture with its quiz, copied and built."""
    return quiz_corpus(tmp_path_factory.mktemp("quiz-visual"))


@pytest.fixture(scope="module")
def origin(corpus: Path):
    """`studyforge serve`'s own instance over the corpus, and the page's URL on it."""
    with served_instance(corpus) as server:
        host, port = server.server_address[:2]
        relative = page_of(corpus).relative_to(corpus.parent).as_posix()
        yield f"http://{host}:{port}/{relative}"


def fresh(page: OpenPage, url: str) -> OpenPage:
    """Open `url` with the reader's store emptied, then open the quiz's card.

    ⚠️ The browser outlives a test, and `file://` shares one store: a pass kept
    by an earlier test would otherwise read as this one's.
    """
    page.open(url)
    page.evaluate("localStorage.clear()")
    page.open(url)
    page.open_practice()
    return page


@pytest.fixture
def as_file(open_page: OpenPage, corpus: Path):
    """The harness's own tab, on the quiz page opened as a double-clicked file."""
    yield fresh(open_page, "file://" + str(page_of(corpus)))
    open_page.evaluate("localStorage.clear()")


@pytest.fixture
def served(open_page: OpenPage, origin: str):
    """The harness's own tab, on the SAME built page read through the study server."""
    yield fresh(open_page, origin)
    open_page.evaluate("localStorage.clear()")


@pytest.mark.parametrize("where", PLACES)
def test_the_check_control_shows_and_nothing_to_run_is_offered(where, request):
    # ⭐ The same page in both places: the script found its key and swapped the
    # no-script sentence for the Check control. ⛔ No run affordance, not even
    # a disabled one.
    state = request.getfixturevalue(where).evaluate(STATE)
    assert state is not None, "the page carries no quiz"
    options = sum(len(one["options"]) for one in QUESTIONS)
    assert (state["questions"], state["radios"]) == (len(QUESTIONS), options)
    assert (state["check"], state["offline"]) == (True, False)
    assert (state["acts"], state["frames"], state["disabled"]) == (0, 0, 0)


@pytest.mark.parametrize("where", PLACES)
def test_a_right_answer_shows_the_verdict_and_its_sentence_and_asks_nothing(where, request):
    page = request.getfixturevalue(where)
    state, asked = answer(page, KEYED)
    assert asked == [], f"answering a quiz sent {asked}"
    verdict = reference(KEYED)
    assert state["verdicts"] == ["correct" if row.correct else "wrong" for row in verdict.answered]
    assert verdict.complete and "Every question answered correctly" in state["status"]
    for said, (question, option) in zip(state["said"], KEYED.items(), strict=True):
        # ⛔ ONE verdict word, then the corpus's sentence verbatim.
        assert said == f"Right. {says(question, option)}"


@pytest.mark.parametrize("where", PLACES)
def test_a_wrong_answer_shows_its_own_sentence_never_the_keys_and_asks_nothing(where, request):
    page = request.getfixturevalue(where)
    answers = {**KEYED, "q-2": WRONG["q-2"]}
    state, asked = answer(page, answers)
    assert asked == [], f"answering a quiz sent {asked}"
    verdict = reference(answers)
    assert state["verdicts"] == ["correct" if row.correct else "wrong" for row in verdict.answered]
    assert not verdict.complete and f"{verdict.right} of {verdict.asked}" in state["status"]
    assert state["said"][1] == f"Not this one. {says('q-2', WRONG['q-2'])}"
    # ⛔ The key's sentence is in the page's data block, and never SHOWN.
    assert says("q-2", KEYED["q-2"]) not in state["shown"]
    assert not state["cardPassed"] and state["kept"] == ""


@pytest.mark.parametrize("where", PLACES)
def test_an_unanswered_quiz_asks_for_an_answer(where, request):
    # ⛔ A question nobody answered is not wrong, it is not answered.
    page = request.getfixturevalue(where)
    page.evaluate(CHECK)
    state = page.evaluate(STATE)
    assert state["verdicts"] == [None] * len(QUESTIONS)
    assert "Choose an answer" in state["status"]


@pytest.mark.parametrize("where", PLACES)
def test_changing_an_answer_after_checking_grades_it_again(where, request):
    # ⭐ The sentence under a question can never describe an option that is no
    # longer chosen: a change after the first check is graded afresh.
    page = request.getfixturevalue(where)
    answer(page, WRONG)
    assert page.evaluate(STATE)["verdicts"] == ["wrong", "wrong"]
    choose(page, KEYED)
    state = settled(page, lambda state: "Every question" in state["status"])
    assert state["verdicts"] == ["correct", "correct"]


def test_the_check_control_grades_from_the_keyboard(served):
    # ⛔ Fully keyboard accessible: a real `<button>` pressed with a real Enter.
    choose(served, KEYED)
    served.evaluate("document.querySelector('[data-practice-part=\"check\"]').focus()")
    served.press("Enter")
    state = settled(served, graded)
    assert "Every question answered correctly" in state["status"]


@pytest.mark.parametrize("where", PLACES)
def test_a_passed_quiz_card_reads_passed_and_keeps_it_across_a_reload(where, request):
    # ⭐ Clause 3: kept in the reader's browser, where "Mark as read" is — never
    # on the server, which has no quiz route to keep it in.
    page = request.getfixturevalue(where)
    assert not page.evaluate(STATE)["cardPassed"], "the card read passed before any answer"
    key = page.evaluate(QUIZ_KEY)
    state, asked = answer(page, KEYED)
    assert asked == []
    assert state["cardPassed"], "the card does not read passed after a right answer"
    assert key in json.loads(state["kept"])["passed"]
    url = page.evaluate("location.href.split('#')[0]")
    page.open(url)
    after = page.evaluate(STATE)
    assert after["cardPassed"], "the pass was lost across a reload"
    assert after["verdicts"] == [None] * len(QUESTIONS), "a reload kept the answers too"


#: The open quiz's two parts, where they are drawn.
COLUMN = """
(() => {
  const box = (el) => { const r = el.getBoundingClientRect();
    return {left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width}; };
  const quiz = document.querySelector('section[data-practice-quiz][data-workspace-open]');
  const intro = document.querySelector('section[data-kind][data-workspace-open]');
  return {
    one: document.documentElement.hasAttribute('data-workspace-quiz'),
    intro: box(intro), quiz: box(quiz), view: innerWidth
  };
})()
"""


@pytest.mark.parametrize("size", [WIDE, NARROW], ids=["wide", "narrow"])
@pytest.mark.parametrize("where", PLACES)
def test_a_quiz_opens_in_one_column_its_intro_above_its_questions(where, size, request):
    # ⛔ The Java pilot's quiz wasted the left pane: its intro alone on the left,
    # its questions on the right. ⭐ One column: the intro above, the questions
    # below it, the same width, never overlapping.
    page = request.getfixturevalue(where)
    page.resize(*size)
    page.open(page.evaluate("location.href.split('#')[0]"))
    page.open_practice()
    got = page.evaluate(COLUMN)
    assert got["one"], "the workspace did not mark the quiz as one column"
    intro, quiz = got["intro"], got["quiz"]
    assert abs(intro["left"] - quiz["left"]) < 1 and abs(intro["width"] - quiz["width"]) < 1, got
    assert intro["bottom"] <= quiz["top"] + 1, got
    assert quiz["width"] > got["view"] * 0.5 or quiz["width"] >= 700, got


def test_closing_the_quiz_leaves_one_column_mode(served):
    served.evaluate("document.querySelector('[data-workspace-act=\"close\"]').click()")
    assert served.evaluate("document.documentElement.hasAttribute('data-workspace-quiz')") is False


#: Where each question's number is drawn, read off the live layout.
NUMBERING = """
(() => {
  const quiz = document.querySelector('section[data-practice-quiz]');
  return Array.from(quiz.querySelectorAll('[data-practice-question]')).map((one) => {
    const legend = one.querySelector('legend');
    const first = one.querySelector('[data-practice-option]');
    return {
      marker: getComputedStyle(one).listStyleType,
      number: getComputedStyle(legend, '::before').content,
      legendTop: legend.getBoundingClientRect().top,
      firstOptionTop: first.getBoundingClientRect().top,
      legendLeft: legend.getBoundingClientRect().left,
      itemLeft: one.getBoundingClientRect().left
    };
  });
})()
"""


@pytest.mark.parametrize("where", ["as_file", "served"])
def test_each_questions_number_sits_beside_its_stem_and_not_its_first_option(where, request):
    # ⛔ The list's own MARKER sits on the list item's first LINE BOX, and a
    # `<legend>` is laid out in its fieldset's border rather than as a line — so
    # a list marker lands beside the FIRST OPTION. ⭐ The number is the legend's
    # own `::before`, drawn at the
    # start of the stem's line, and the item draws no marker at all.
    page = request.getfixturevalue(where)
    for one in page.evaluate(NUMBERING):
        assert one["marker"] == "none", one
        assert "counter(question)" in one["number"], one
        assert one["legendTop"] < one["firstOptionTop"], one
        assert abs(one["legendLeft"] - one["itemLeft"]) < 1, one
