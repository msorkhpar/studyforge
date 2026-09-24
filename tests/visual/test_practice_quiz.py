"""`AX-09` — a quiz shows its questions, the SERVER grades them, and nothing runs.

⛔ **THE USER'S RULING, 2026-09-23**: *"a test with the correct answer
residing on the server side. When user answers it will get validated and result
will be returned to the user with explanation if needed"*. ⭐ So this module
takes its readings in TWO places, and the difference between them is the
subject:

- **over `file://`** — the page a reader double-clicks: the questions and the
  options show, a reader may choose, the Check control is absent and the page
  says checking needs the local study server; ⛔ nothing is asked of any origin
  and no key is anywhere in the DOM;
- **over a served origin** — `studyforge serve`'s own instance
  (`serve.instance.instance_of`) over the BUILT prose fixture with a quiz in it:
  a right answer and a wrong answer each show the SERVER's verdict and the chosen
  option's sentence, and the network log shows the grading request.

⚠️ **Superseded, and said so rather than silently rewritten:** until that ruling
this module opened the page as a FILE and graded there, because the key shipped in the
page. That reading is now the negative one.

⛔ **WHY THIS NEEDS A BROWSER.** Whether a reader who chooses an answer is told
the right thing about it is a runtime identity: the radios, the request, the
sentence that appears under a question and the line that counts them exist only
while a page is running and a server is answering it.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from tests.studyforge.serve.routes.quizzing import (
    KEYED,
    QUESTIONS,
    WRONG,
    page_of,
    quiz_corpus,
    says,
    sentences,
    served_instance,
)
from tests.visual.page import OpenPage

#: Seconds a reading waits for the server's verdict to land on the page.
SETTLE = 15.0

#: What the page is asked for, once it has settled.
#:
#: ⛔ **`acts` and `frames` are counted over the WHOLE DOCUMENT and not over the
#: quiz**: a plant that emitted a Run button BESIDE the quiz section left a
#: scoped version of this reading GREEN (measured, `AX-09`).
STATE = """
(() => {
  const quiz = document.querySelector('section[data-practice-quiz]');
  if (!quiz) return null;
  const part = (name) => quiz.querySelector('[data-practice-part="' + name + '"]');
  const questions = Array.from(quiz.querySelectorAll('[data-practice-question]'));
  return {
    questions: questions.length,
    radios: quiz.querySelectorAll('input[type="radio"]').length,
    acts: document.querySelectorAll('[data-practice-act]').length,
    frames: document.querySelectorAll('iframe').length,
    disabled: quiz.querySelectorAll('[disabled], [aria-disabled="true"]').length,
    check: !!part('check') && part('check').checkVisibility(),
    offline: !!part('offline') && part('offline').checkVisibility(),
    offlineText: part('offline') ? part('offline').textContent.trim() : '',
    status: part('status').textContent.trim(),
    verdicts: questions.map((one) => one.getAttribute('data-practice-verdict')),
    said: questions.map((one) => {
      const line = one.querySelector('[data-practice-part="says"]');
      return line.hidden ? '' : line.textContent.trim();
    }),
    dom: document.documentElement.outerHTML
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
    return bool(state) and state["status"] not in ("", "Checking…")


def posts(page: OpenPage) -> list[str]:
    """Every POST the page issued, by URL — the network log's reading of an act."""
    return [
        event["params"]["request"]["url"]
        for event in page.browser.events
        if event.get("method") == "Network.requestWillBeSent"
        and event["params"]["request"].get("method") == "POST"
    ]


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


@pytest.fixture
def as_file(open_page: OpenPage, corpus: Path) -> OpenPage:
    """The harness's own tab, on the quiz page opened as a double-clicked file."""
    open_page.open("file://" + str(page_of(corpus)))
    return open_page


@pytest.fixture
def served(open_page: OpenPage, origin: str) -> OpenPage:
    """The harness's own tab, on the SAME built page read through the study server."""
    open_page.open(origin)
    return open_page


# --- over file:// ------------------------------------------------------------


def test_over_a_file_the_questions_show_and_the_page_says_it_needs_the_server(as_file):
    # ⭐ The default over a file: the questions and options show, a reader
    # may choose, and the page says why nothing checks them — the mechanism Run
    # and Submit use. ⛔ And no run affordance, not even a disabled one.
    state = as_file.evaluate(STATE)
    assert state is not None, "the page carries no quiz"
    options = sum(len(one["options"]) for one in QUESTIONS)
    assert (state["questions"], state["radios"]) == (len(QUESTIONS), options)
    assert (state["acts"], state["frames"], state["disabled"]) == (0, 0, 0)
    assert (state["check"], state["offline"]) == (False, True)
    assert "needs the local study server" in state["offlineText"]
    choose(as_file, KEYED)
    assert as_file.evaluate(STATE)["verdicts"] == [None] * len(QUESTIONS)


def test_over_a_file_no_key_and_no_sentence_is_in_the_dom_and_nothing_is_asked(as_file):
    # ⛔ The key resides on the SERVER. ⭐ Read in the live DOM — after every
    # script ran — so a key a script wrote in would be read too.
    dom = as_file.evaluate(STATE)["dom"]
    for sentence in sentences():
        assert sentence not in dom, sentence
    assert "-correct" not in dom
    assert [one for one in as_file.requests() if one.startswith(("http://", "https://"))] == []


# --- over the served origin --------------------------------------------------


def test_served_the_check_control_shows_and_the_offline_sentence_does_not(served):
    state = served.evaluate(STATE)
    assert (state["check"], state["offline"]) == (True, False)
    assert (state["acts"], state["frames"], state["disabled"]) == (0, 0, 0)


def test_a_right_answer_shows_the_servers_verdict_and_the_request_is_in_the_network_log(
    served,
):
    choose(served, KEYED)
    served.evaluate(CHECK)
    state = settled(served, graded)
    assert state["verdicts"] == ["correct"] * len(QUESTIONS)
    assert "Every question answered correctly" in state["status"]
    for said, (question, option) in zip(state["said"], KEYED.items(), strict=True):
        # ⛔ F5: ONE verdict word — the page's own, keyed on the server's
        # `correct` — then the corpus's sentence verbatim. Never both twice.
        assert said == f"Right. {says(question, option)}"
    asked = posts(served)
    assert len(asked) == 1 and "/api/v1/quiz/" in asked[0], asked
    assert all(f"/{question}={option}" in asked[0] for question, option in KEYED.items())


def test_a_wrong_answer_shows_its_own_sentence_and_never_the_key(served):
    answers = {**KEYED, "q-2": WRONG["q-2"]}
    choose(served, answers)
    served.evaluate(CHECK)
    state = settled(served, graded)
    assert state["verdicts"] == ["correct", "wrong"]
    assert "1 of 2" in state["status"]
    assert state["said"][1] == f"Not this one. {says('q-2', WRONG['q-2'])}"
    assert says("q-2", KEYED["q-2"]) not in state["dom"]
    asked = posts(served)
    assert len(asked) == 1 and asked[0].endswith(f"/q-2={WRONG['q-2']}"), asked


def test_an_unanswered_quiz_asks_for_an_answer_and_asks_the_server_nothing(served):
    # ⛔ A question nobody answered is not wrong, it is not answered — and a
    # request carrying nothing would be a round trip that could say nothing.
    served.evaluate(CHECK)
    state = served.evaluate(STATE)
    assert state["verdicts"] == [None] * len(QUESTIONS)
    assert "Choose an answer" in state["status"]
    assert posts(served) == []


def test_changing_an_answer_after_checking_asks_the_server_again(served):
    # ⭐ The sentence under a question can never describe an option that is no
    # longer chosen: a change after the first check is graded afresh.
    choose(served, WRONG)
    served.evaluate(CHECK)
    settled(served, lambda state: state["verdicts"] == ["wrong", "wrong"])
    choose(served, KEYED)
    state = settled(served, lambda state: "Every question" in state["status"])
    assert state["verdicts"] == ["correct", "correct"]
    assert len(posts(served)) >= 2


def test_the_check_control_grades_from_the_keyboard(served):
    # ⛔ Fully keyboard accessible: a real `<button>` pressed with a real Enter.
    choose(served, KEYED)
    served.evaluate("document.querySelector('[data-practice-part=\"check\"]').focus()")
    served.press("Enter")
    state = settled(served, graded)
    assert "Every question answered correctly" in state["status"]


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
    # ⛔ The corpus office's finding F9: the list's own MARKER sits on the list
    # item's first LINE BOX, and a `<legend>` is laid out in its fieldset's
    # border rather than as a line — so the number landed beside the FIRST
    # OPTION. ⭐ The number is now the legend's own `::before`, drawn at the
    # start of the stem's line, and the item draws no marker at all.
    page = request.getfixturevalue(where)
    for one in page.evaluate(NUMBERING):
        assert one["marker"] == "none", one
        assert "counter(question)" in one["number"], one
        assert one["legendTop"] < one["firstOptionTop"], one
        assert abs(one["legendLeft"] - one["itemLeft"]) < 1, one
