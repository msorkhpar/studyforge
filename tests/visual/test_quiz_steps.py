"""A plain quiz, drawn one question at a time, read in a real browser on a page a build wrote.

**What it asserts.** One question is in view at a time, with a progress line, Previous and Next and
a navigator; an answer is explained where it is given and the explanation never names the key;
the answers and the place survive a reload; Finish shows a verdict for every question and each
verdict jumps to its question; the whole thing works from the keyboard and never scrolls sideways
at phone width; the `page` layout opt-out draws every question on one page; and no request leaves
the page.

⛔ WHY THIS NEEDS A BROWSER. The view, the store and the focus exist only while a page is running.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from studyforge.exercise.quiz import questions_of
from tests.studyforge.exercise.quiz import mock_exam
from tests.studyforge.exercise.quiz.mock_corpus import ORIGIN, mock_corpus
from tests.studyforge.serve.routes.quizzing import page_of
from tests.visual.page import OpenPage

QUESTIONS = questions_of(
    [{k: v for k, v in one.items() if k != "domain"} for one in mock_exam.questions(ORIGIN)],
    "the visual quiz",
)
KEYED = {one.id: next(o.id for o in one.options if o.correct) for one in QUESTIONS}
WRONG = {one.id: next(o.id for o in one.options if not o.correct) for one in QUESTIONS}
QUIZ = 'section[data-form-kind="quiz"]'


def part(name: str) -> str:
    return f'{QUIZ} [data-form-part="{name}"]'


@pytest.fixture(scope="module")
def stepped_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    root = mock_corpus(tmp_path_factory.mktemp("quiz-steps"), mock=False)
    return "file://" + str(page_of(root))


@pytest.fixture(scope="module")
def paged_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    root = mock_corpus(tmp_path_factory.mktemp("quiz-paged"), mock=False, layout="page")
    return "file://" + str(page_of(root))


def run(page: OpenPage, script: str) -> object:
    result = page.evaluate(script)
    time.sleep(0.05)
    return result


def shown(page: OpenPage) -> list[str]:
    return page.evaluate(
        f"Array.from(document.querySelectorAll('{QUIZ} li[data-practice-question]'))"
        ".filter((x) => !x.hidden).map((x) => x.getAttribute('data-practice-question'))"
    )


def click(page: OpenPage, selector: str) -> None:
    run(page, f"document.querySelector({selector!r}).click()")


def pick(page: OpenPage, question: str, option: str) -> None:
    click(page, f'{QUIZ} [data-practice-question="{question}"] input[value="{option}"]')


def text(page: OpenPage, selector: str) -> str:
    return str(page.evaluate(f"document.querySelector({selector!r}).textContent.trim()"))


def fresh(page: OpenPage, url: str) -> None:
    page.open(url)
    page.evaluate("localStorage.clear()")
    page.open(url)
    page.open_practice()


def test_one_question_is_in_view_with_a_progress_line_and_a_way_through(
    open_page: OpenPage, stepped_url: str
) -> None:
    fresh(open_page, stepped_url)
    first = QUESTIONS[0].id
    assert shown(open_page) == [first]
    assert text(open_page, part("count")).startswith(f"Question 1 of {len(QUESTIONS)}")
    assert open_page.evaluate(f"document.querySelector({part('previous')!r}).disabled") is True
    click(open_page, part("next"))
    assert shown(open_page) == [QUESTIONS[1].id]
    assert text(open_page, part("count")).startswith(f"Question 2 of {len(QUESTIONS)}")
    click(open_page, part("previous"))
    assert shown(open_page) == [first]
    click(open_page, f'{part("numbers")} button[data-index="3"]')
    assert shown(open_page) == [QUESTIONS[3].id]


def test_an_answer_is_explained_where_it_is_given_and_never_names_the_key(
    open_page: OpenPage, stepped_url: str
) -> None:
    fresh(open_page, stepped_url)
    first = QUESTIONS[0]
    pick(open_page, first.id, WRONG[first.id])
    said = text(open_page, f'{QUIZ} [data-practice-question="{first.id}"] [data-form-part="review"]')
    assert said.startswith("Not this one.")
    assert "Correct answer" not in said
    pick(open_page, first.id, KEYED[first.id])
    assert text(open_page, f'{QUIZ} [data-practice-question="{first.id}"] [data-form-part="review"]').startswith("Right.")


def test_the_answers_and_the_place_survive_a_reload(open_page: OpenPage, stepped_url: str) -> None:
    fresh(open_page, stepped_url)
    pick(open_page, QUESTIONS[0].id, KEYED[QUESTIONS[0].id])
    click(open_page, part("next"))
    open_page.open(stepped_url)
    assert shown(open_page) == [QUESTIONS[1].id]
    checked = open_page.evaluate(
        f"document.querySelector('{QUIZ} [data-practice-question=\"{QUESTIONS[0].id}\"] input:checked').value"
    )
    assert checked == KEYED[QUESTIONS[0].id]


def test_finish_gives_a_verdict_per_question_and_each_verdict_jumps_back(
    open_page: OpenPage, stepped_url: str, capture_dir: Path
) -> None:
    fresh(open_page, stepped_url)
    for index, one in enumerate(QUESTIONS):
        pick(open_page, one.id, KEYED[one.id] if index % 2 == 0 else WRONG[one.id])
    click(open_page, part("submit"))
    verdicts = open_page.evaluate(
        f"Array.from(document.querySelectorAll('{part('summary')} li')).map((x) => x.getAttribute('data-form-verdict'))"
    )
    assert verdicts == ["right" if i % 2 == 0 else "wrong" for i in range(len(QUESTIONS))]
    assert text(open_page, part("overall")).startswith(f"You answered {(len(QUESTIONS) + 1) // 2} of")
    click(open_page, f'{part("summary")} li:nth-child(5) button')
    focused = open_page.evaluate("document.activeElement.closest('li[data-practice-question]').getAttribute('data-practice-question')")
    assert focused == QUESTIONS[4].id
    open_page.capture(capture_dir / "quiz-summary.png", whole=False)


def test_it_works_from_the_keyboard(open_page: OpenPage, stepped_url: str) -> None:
    fresh(open_page, stepped_url)
    run(open_page, f"document.querySelector({part('next')!r}).focus()")
    open_page.press("Enter")
    time.sleep(0.1)
    assert shown(open_page) == [QUESTIONS[1].id]


@pytest.mark.parametrize("size", [(390, 800), (1920, 1000)])
def test_nothing_scrolls_sideways_and_the_quiz_has_no_scroll_box_of_its_own(
    open_page: OpenPage, stepped_url: str, size: tuple[int, int]
) -> None:
    open_page.resize(*size)
    fresh(open_page, stepped_url)
    assert open_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth") is True
    inner = open_page.evaluate(
        f"Array.from(document.querySelectorAll('{QUIZ}, {QUIZ} *')).filter((x) => {{"
        " const s = getComputedStyle(x);"
        " return (s.overflowY === 'auto' || s.overflowY === 'scroll') && x.scrollHeight > x.clientHeight;"
        "}).length"
    )
    assert inner == 0


def test_the_page_layout_opt_out_draws_every_question_with_one_check(
    open_page: OpenPage, paged_url: str
) -> None:
    open_page.open(paged_url)
    count = open_page.evaluate(
        "Array.from(document.querySelectorAll('section[data-practice-quiz] li[data-practice-question]'))"
        ".filter((x) => !x.hidden).length"
    )
    assert count == len(QUESTIONS)
    assert open_page.evaluate("!!document.querySelector('[data-practice-part=\"check\"]')") is True
    assert open_page.evaluate(f"!!document.querySelector({QUIZ!r})") is False


def test_no_request_leaves_the_page(open_page: OpenPage, stepped_url: str) -> None:
    fresh(open_page, stepped_url)
    pick(open_page, QUESTIONS[0].id, KEYED[QUESTIONS[0].id])
    click(open_page, part("submit"))
    assert all(url.startswith(("file://", "data:")) for url in open_page.requests())
