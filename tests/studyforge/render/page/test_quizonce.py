"""Mirror of `render/page/quizonce.py` (R12): a quiz the lesson repeats is shown once, in its
practice."""

from __future__ import annotations

from studyforge.render.page import quizonce, render
from studyforge.render.page.quizonce import POINTER
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import QUIZ, document, section

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


def test_the_lessons_repeat_is_replaced_by_one_sentence_and_positions_do_not_move():
    shown = quizonce.once(unit(lesson()))
    blocks = shown["sections"][0]["blocks"]
    assert len(blocks) == 5 and blocks[2] == {"type": "heading", "level": 2, "text": "Quiz"}
    assert blocks[3] == {"type": "para", "text": POINTER}
    assert blocks[4] == {"type": "html", "text": ""}
    assert blocks[0:3] == lesson()["blocks"][0:3]


def test_the_page_carries_each_question_once_and_the_practice_still_has_them():
    page = render(unit(lesson()), sample_placement()).decode("utf-8")
    for stem in STEMS:
        assert page.count(stem) == 1, "a question is shown twice"
    assert "Answer key" not in page and POINTER in page


def test_a_range_that_stops_at_the_next_heading_keeps_what_follows():
    follow = [{"type": "heading", "level": 2, "text": "Next"}, {"type": "para", "text": "More."}]
    blocks = quizonce.once(unit(lesson(*follow)))["sections"][0]["blocks"]
    assert blocks[-2:] == follow


def test_a_quiz_heading_over_other_questions_and_a_unit_with_no_quiz_practice_stand():
    other = lesson()
    other["blocks"][3] = {"type": "list", "ordered": True, "items": ["A different question?"]}
    given = unit(other)
    assert quizonce.once(given) is given
    no_quiz = unit(lesson(), practice=section(key="p", workspace={
        "main_path": "w/a.py", "run_command": ["true"]}))
    assert quizonce.once(no_quiz) is no_quiz


def test_a_review_bank_and_a_mock_exam_are_never_what_a_lesson_repeats():
    for extra in ({"review": {"intervals_days": [1]}},):
        given = unit(lesson(), practice=section(workspace={**QUIZ, **extra}))
        assert quizonce.once(given) is given


def test_the_document_it_is_given_is_never_changed():
    given = unit(lesson())
    before = repr(given)
    quizonce.once(given)
    assert repr(given) == before
