"""Mirror of `render/page/quizonce.py` (R12): a quiz the lesson repeats is shown once, in its
practice."""

from __future__ import annotations

from studyforge.render.page import quizonce, render
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import QUIZ, document, section

PANEL = lambda one, whole: "<quiz/>"  # noqa: E731 - a stand-in for the page's own quiz markup

STEMS = [one["stem"] for one in QUIZ["questions"]]


def lesson(*tail):
    blocks = [
        {"type": "heading", "level": 2, "text": "Ideas"},
        {"type": "para", "text": "Some prose."},
        {"type": "heading", "level": 2, "text": "Quiz"},
        {
            "type": "list", "ordered": True,
            "items": [[f"{stem}", {"type": "para", "text": "a"}] for stem in STEMS],
        },
        {"type": "disclosure", "summary": "Answer key", "open": False,
         "blocks": [{"type": "para", "text": "key"}]},
        *tail,
    ]
    return {
        "key": "prose", "kind": "lesson", "heading": "Lesson", "blocks": blocks, "video": None,
        "workspace": None, "attachments": [],
    }


def unit(lesson_section, practice=None):
    return document(sections=[lesson_section, practice or section(workspace=QUIZ)])


def test_the_lessons_repeat_is_replaced_by_the_quiz_and_positions_do_not_move():
    shown = quizonce.once(unit(lesson()), PANEL)
    blocks = shown["sections"][0]["blocks"]
    assert len(blocks) == 5 and blocks[2] == {"type": "heading", "level": 2, "text": "Quiz"}
    assert blocks[3] == {"type": "html", "text": "<quiz/>"}
    assert blocks[4] == {"type": "html", "text": ""}
    assert blocks[0:3] == lesson()["blocks"][0:3]


def test_the_matched_practice_leaves_the_document_so_it_is_not_drawn_twice():
    shown = quizonce.once(unit(lesson()), PANEL)
    assert [one["kind"] for one in shown["sections"]] == ["lesson"]


def test_the_page_carries_each_question_once_in_place_and_no_key_folds_away():
    page = render(unit(lesson()), sample_placement()).decode("utf-8")
    for stem in STEMS:
        assert page.count(stem) == 1, "a question is shown twice"
    assert "Answer key" not in page and "data-practice-quiz=" in page
    # ⭐ In place: the quiz follows the lesson's own heading, before the next section starts, and
    # nothing lists it as a practice or opens it in a workspace.
    assert page.index("<h2") < page.index("data-practice-quiz=")
    assert "data-practices" not in page and "data-practice-card" not in page
    assert "Answer these" not in page, "the quiz is headed twice"


def test_two_practices_with_the_same_questions_stand_in_one_place_each_at_most():
    twin = section(key="practice-two", workspace=QUIZ)
    given = document(sections=[lesson(), section(workspace=QUIZ), twin])
    shown = quizonce.once(given, PANEL)
    assert [one["kind"] for one in shown["sections"]] == ["lesson", "practice"]


def test_a_range_that_stops_at_the_next_heading_keeps_what_follows():
    follow = [{"type": "heading", "level": 2, "text": "Next"}, {"type": "para", "text": "More."}]
    blocks = quizonce.once(unit(lesson(*follow)), PANEL)["sections"][0]["blocks"]
    assert blocks[-2:] == follow


def test_a_quiz_heading_over_other_questions_and_a_unit_with_no_quiz_practice_stand():
    other = lesson()
    other["blocks"][3] = {"type": "list", "ordered": True, "items": ["A different question?"]}
    given = unit(other)
    assert quizonce.once(given, PANEL) is given
    no_quiz = unit(lesson(), practice=section(key="p", workspace={
        "main_path": "w/a.py", "run_command": ["true"]}))
    assert quizonce.once(no_quiz, PANEL) is no_quiz


def test_a_review_bank_and_a_mock_exam_are_never_what_a_lesson_repeats():
    for extra in ({"review": {"intervals_days": [1]}},):
        given = unit(lesson(), practice=section(workspace={**QUIZ, **extra}))
        assert quizonce.once(given, PANEL) is given


def test_the_document_it_is_given_is_never_changed():
    given = unit(lesson())
    before = repr(given)
    quizonce.once(given, PANEL)
    assert repr(given) == before


# --------------------------------------------------------------------------
# ⭐ a mock exam's page lists its questions and folds the key away: the key must not be readable
# --------------------------------------------------------------------------

import json  # noqa: E402
import re  # noqa: E402

from tests.studyforge.exercise.quiz import mock_exam, mock_form  # noqa: E402

ORIGIN = {"path": "basics/01.md", "section": "What a class is"}


def mock_lesson(questions):
    blocks = [
        {"type": "heading", "level": 2, "text": "Mock exam"},
        {
            "type": "list", "ordered": True,
            "items": [[one["stem"], {"type": "para", "text": "a"}] for one in questions],
        },
        {"type": "disclosure", "summary": "Answer key", "open": False, "blocks": [
            {"type": "para", "text": " ".join(f"KEYTEXT {one['id']}" for one in questions)}]},
    ]
    return {"key": "prose", "kind": "lesson", "heading": "Lesson", "blocks": blocks,
            "video": None, "workspace": None, "attachments": []}


import pytest  # noqa: E402


@pytest.mark.parametrize("pool", ["plain", "form"])
def test_a_mock_exam_page_carries_no_key_text_outside_the_data_block_before_interaction(pool):
    questions = (mock_exam if pool == "plain" else mock_form).questions(ORIGIN)
    mock = (mock_exam if pool == "plain" else mock_form).mock()
    record = {"kind": "quiz", "questions": questions, "mock": mock}
    given = document(sections=[mock_lesson(questions), section(workspace=record)])
    page = render(given, sample_placement()).decode("utf-8")
    assert "KEYTEXT" not in page and "<details" not in page
    visible = re.sub(r"<script[^>]*>.*?</script>", "", page, flags=re.S)
    assert "data-practice-quiz=" in visible, "the exam is not drawn in place"
    for one in questions:
        assert visible.count(one["stem"]) == 1, "a question is drawn twice"
        for option in one["options"]:
            assert option["says"] not in visible, "an explanation is readable before answering"
    assert "data-practice-correct" not in visible
    # ⭐ The key the page grades from stays in its own data block, never as visible markup.
    blocks = re.findall(r'<script type="application/json"[^>]*>(.*?)</script>', page, flags=re.S)
    assert any(json.loads(b) for b in blocks if b.startswith("{") and "keys" in b or "key" in b)
