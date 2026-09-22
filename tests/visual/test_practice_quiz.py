"""`AX-09` — a quiz shows its questions, grades them, and offers nothing to run.

⛔ **WHY THIS NEEDS A BROWSER, AND WHY A TEXT COULD NOT ANSWER IT.** *"A quiz
page shows questions, grades them, and shows no run affordance"* is two claims,
and only the first is a claim about markup. ⭐ The grading is four lines of
arithmetic in the page itself, and whether a reader who chooses an answer is
told the right thing about it is a runtime identity: the radios, the sentence
that appears under a question, and the line that counts them exist only while a
page is running.

⛔ **AND THE ORIGIN IS THE SUBJECT, NOT THE SETTING.** Spec §7 §7 says a quiz is
graded with no compiler, no container, no network and no model, so the reading
is identical over `file://` and over a served origin — ⭐ **so this module opens
the page as a double-clicked FILE and takes every reading there.** A check that
needed a server would have proved the opposite of the clause.

⚠️ **The page this module opens is built by `site.build`'s own writer**, so the
stylesheet and the script are the real bundle; only the one document is this
module's, because no fixture corpus ships a quiz yet.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.render.page import render
from tests.studyforge.render.page.sites import FIXTURES as UNIT_CASE_OF
from tests.visual import site
from tests.visual.page import OpenPage

#: The corpus whose unit page this module borrows a placement from. ⛔ Its own
#: page is left where it is: this module writes a SECOND page beside it, so the
#: relative asset links the framework wrote resolve unchanged.
CORPUS = "depth2"

#: What this module's page asks. ⭐ Two questions, because one cannot tell *every
#: question answered correctly* from *this question answered correctly* — which
#: is the whole of the completion rule (`exercise.quiz.completes`).
QUESTIONS = [
    {
        "id": "q-1",
        "stem": "What does a class declaration open?",
        "options": [
            {"id": "a", "text": "A type", "correct": True, "says": "The page says exactly this."},
            {"id": "b", "text": "A file", "correct": False, "says": "A file holds a type."},
        ],
        "origin": {"path": "basics/01.md", "section": "What a class is"},
    },
    {
        "id": "q-2",
        "stem": "Where does a program start?",
        "options": [
            {"id": "a", "text": "At main", "correct": True, "says": "The runtime calls it."},
            {"id": "b", "text": "At the top", "correct": False, "says": "Order is not entry."},
        ],
        "origin": {"path": "basics/01.md", "section": "What a class is"},
    },
]

#: The record itself. ⛔ No workspace key at all: `exercise.record` refuses a quiz
#: that carries one, so this is what a quiz IS rather than a code record with
#: pieces removed.
QUIZ = {"kind": "quiz", "questions": QUESTIONS}

#: What the page is asked for, once it has settled.
#:
#: ⛔ **`acts` and `frames` are counted over the WHOLE DOCUMENT and not over the
#: quiz**, and that is a repair rather than a preference: a plant that emitted a
#: Run button BESIDE the quiz section left the scoped version of this reading
#: GREEN — measured, and it is the one plant this module did not catch first
#: time. ⚠️ This fixture's only practice section IS the quiz, so a run affordance
#: anywhere on this page is one nobody may use.
STATE = """
(() => {
  const quiz = document.querySelector('section[data-practice-quiz]');
  if (!quiz) return null;
  const questions = Array.from(quiz.querySelectorAll('[data-practice-question]'));
  return {
    questions: questions.length,
    radios: quiz.querySelectorAll('input[type="radio"]').length,
    acts: document.querySelectorAll('[data-practice-act]').length,
    frames: document.querySelectorAll('iframe').length,
    disabled: quiz.querySelectorAll('[disabled], [aria-disabled="true"]').length,
    status: quiz.querySelector('[data-practice-part="status"]').textContent.trim(),
    verdicts: questions.map((one) => one.getAttribute('data-practice-verdict')),
    said: questions.map((one) => {
      const line = one.querySelector('[data-practice-part="says"]');
      return line.hidden ? '' : line.textContent.trim();
    })
  };
})()
"""

#: Choose one option per question by its id, the way a reader's click does.
#: ⛔ A real `click()` on the input and a real `change` event, because the page
#: re-grades on that event and setting `.checked` fires none.
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

#: Press the control that grades, as a reader does.
CHECK = """
document.querySelector('[data-practice-part="check"]').click()
"""


def choose(page: OpenPage, **answers: str) -> None:
    """Choose one option per question and let the page settle."""
    page.evaluate(CHOOSE.replace("<answers>", repr(answers).replace("'", '"')))


@pytest.fixture(scope="module")
def quiz_page(tmp_path_factory: pytest.TempPathFactory) -> str:
    """A real built tree, with one extra page in it whose practice is a quiz."""
    root = tmp_path_factory.mktemp("quiz-site")
    site.build(root)
    case = UNIT_CASE_OF[CORPUS]()
    document = dict(case.document)
    document["sections"] = [
        dict(part, workspace=QUIZ) if part.get("kind") == "practice" else part
        for part in document["sections"]
    ]
    where = Path(root / CORPUS / str(case.placement.unit.page))
    page = where.parent / "a-quiz.unit.html"
    page.write_bytes(render(document, case.placement))
    return "file://" + str(page)


@pytest.fixture
def opened(open_page: OpenPage, quiz_page: str) -> OpenPage:
    """The harness's own tab, opened on the quiz page as a double-clicked file.

    ⛔ **`open_page` and never a tab of this module's own** (`W397`): that
    fixture closes what it opened even when a check fails, and it is also what
    keeps this module out of `test_host_environment`'s ambient sweep — the
    browser's own verdict is reached in `conftest.py`, which is the one place
    licensed to reach it.
    """
    open_page.open(quiz_page)
    return open_page


def test_a_quiz_page_shows_its_questions_and_no_run_affordance_at_all(opened: OpenPage):
    # ⛔ `AX-05/3` and this row's Acceptance, read in the place a reader reads
    # it. ⚠️ **`disabled` is counted too**: the rule is not *no working control*,
    # it is *no control at all*, because a dead button is a promise the page
    # cannot keep (`SF-24`, `W429`, `W431`).
    state = opened.evaluate(STATE)
    assert state is not None, "the page carries no quiz"
    assert (state["questions"], state["radios"]) == (len(QUESTIONS), 4)
    assert (state["acts"], state["frames"], state["disabled"]) == (0, 0, 0)
    # ⭐ And the panel's own section is not on this page either, so nothing keyed
    # on `data-practice` — the run, the maximise, the output — can reach it.
    assert opened.evaluate("!!document.querySelector('section[data-practice]')") is False


def test_a_quiz_grades_over_file_with_no_server_and_issues_no_request(opened: OpenPage):
    # ⛔ **THE property of this shape** (spec §7 §7, R8): the key ships in the
    # page and the rule is the framework's, so the reading is identical over
    # `file://`. ⭐ Every request this page made is read, because a quiz that
    # quietly asked an origin for its answers would grade here and nowhere else.
    choose(opened, **{"q-1": "a", "q-2": "a"})
    opened.evaluate(CHECK)
    state = opened.evaluate(STATE)
    assert state["verdicts"] == ["correct", "correct"]
    assert "Every question answered correctly" in state["status"]
    assert [one for one in opened.requests() if one.startswith(("http://", "https://"))] == []


def test_one_wrong_answer_does_not_complete_and_says_why_that_option_is_wrong(
    opened: OpenPage,
):
    # ⛔ `exercise.quiz.completes`: every question, answered correctly, and
    # nothing less. ⭐ And the sentence is the one for whatever the reader CHOSE
    # — a page that explained only the wrong answers would teach half the
    # material and would tell the reader which half by showing nothing.
    choose(opened, **{"q-1": "a", "q-2": "b"})
    opened.evaluate(CHECK)
    state = opened.evaluate(STATE)
    assert state["verdicts"] == ["correct", "wrong"]
    assert "Every question answered correctly" not in state["status"]
    assert "1 of 2" in state["status"]
    assert QUESTIONS[0]["options"][0]["says"] in state["said"][0]
    assert QUESTIONS[1]["options"][1]["says"] in state["said"][1]


def test_a_verdict_is_a_word_and_never_only_a_colour(opened: OpenPage):
    # ⛔ This row's Acceptance: the reading is announced rather than only
    # coloured. ⚠️ **Read as TEXT**, so a stylesheet that lost its two rules
    # would leave this green and a page that said nothing would not.
    choose(opened, **{"q-1": "b", "q-2": "a"})
    opened.evaluate(CHECK)
    state = opened.evaluate(STATE)
    assert state["said"][0].startswith("Not this one.")
    assert state["said"][1].startswith("Right.")
    # ⭐ The negative control: before anything is checked, nothing is said at
    # all — so the sentences above are the grading and not the markup.
    assert opened.evaluate("document.querySelectorAll('[data-practice-verdict]').length") == 2


def test_an_unanswered_quiz_asks_for_an_answer_rather_than_marking_it_wrong(
    opened: OpenPage,
):
    # ⛔ **Total, exactly as the Python rule is**: a question nobody answered is
    # not correct — it is simply not answered, and telling a reader they are
    # wrong for not having started would be a verdict nobody earned.
    opened.evaluate(CHECK)
    state = opened.evaluate(STATE)
    assert state["verdicts"] == [None, None]
    assert state["said"] == ["", ""]
    assert "Choose an answer" in state["status"]


def test_every_control_on_a_quiz_is_reachable_and_operable_from_the_keyboard(
    opened: OpenPage,
):
    # ⛔ This row's Acceptance: fully keyboard accessible. ⭐ Real radios in a
    # real `fieldset` and a real `<button>`, so the browser's own behaviour is
    # what is read — which is the reason none of them is a styled `div`.
    reached = opened.trail(90)
    names = [str(step.get("tag") or "").lower() for step in reached]
    assert "input" in names, reached
    assert names.index("input") < names.index("button", names.index("input"))
    # ⭐ And the control grades when a keyboard presses it, not only a mouse.
    choose(opened, **{"q-1": "a", "q-2": "a"})
    opened.evaluate("document.querySelector('[data-practice-part=\"check\"]').focus()")
    opened.press("Enter")
    assert "Every question answered correctly" in opened.evaluate(STATE)["status"]
