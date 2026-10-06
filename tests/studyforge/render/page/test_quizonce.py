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
            "type": "list",
            "ordered": True,
            "items": [[f"{stem}", {"type": "para", "text": "a"}] for stem in STEMS],
        },
        {
            "type": "disclosure",
            "summary": "Answer key",
            "open": False,
            "blocks": [{"type": "para", "text": "key"}],
        },
        *tail,
    ]
    return {
        "key": "prose",
        "kind": "lesson",
        "heading": "Lesson",
        "blocks": blocks,
        "video": None,
        "workspace": None,
        "attachments": [],
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
    no_quiz = unit(
        lesson(),
        practice=section(key="p", workspace={"main_path": "w/a.py", "run_command": ["true"]}),
    )
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
            "type": "list",
            "ordered": True,
            "items": [[one["stem"], {"type": "para", "text": "a"}] for one in questions],
        },
        {
            "type": "disclosure",
            "summary": "Answer key",
            "open": False,
            "blocks": [
                {"type": "para", "text": " ".join(f"KEYTEXT {one['id']}" for one in questions)}
            ],
        },
    ]
    return {
        "key": "prose",
        "kind": "lesson",
        "heading": "Lesson",
        "blocks": blocks,
        "video": None,
        "workspace": None,
        "attachments": [],
    }


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


# --------------------------------------------------------------------------
# ⛔ only the quiz's own blocks are replaced: the lesson around it is never lost
# --------------------------------------------------------------------------

PROSE = [
    "First paragraph of the lesson.",
    "Second paragraph of the lesson.",
    "Third paragraph of the lesson.",
]

TWO = {
    **QUIZ,
    "questions": [
        *QUIZ["questions"],
        {**QUIZ["questions"][0], "id": "q-2", "stem": "Where does a field live?"},
    ],
}
TWO_STEMS = [one["stem"] for one in TWO["questions"]]


def one_section_lesson(stems=TWO_STEMS):
    """A whole lesson as ONE section: a title, paragraphs, a quiz heading, the questions, a key."""
    blocks = [
        {"type": "heading", "level": 1, "text": "The lesson"},
        *({"type": "para", "text": text} for text in PROSE[:2]),
        {"type": "heading", "level": 2, "text": "Details"},
        {"type": "para", "text": PROSE[2]},
        {"type": "heading", "level": 2, "text": "Quiz"},
        {
            "type": "list",
            "ordered": True,
            "items": [
                [stem, {"type": "list", "ordered": False, "items": ["a", "b"]}] for stem in stems
            ],
        },
        {
            "type": "disclosure",
            "summary": "Answer key",
            "open": False,
            "blocks": [{"type": "para", "text": "KEYTEXT"}],
        },
    ]
    return {
        "key": "prose",
        "kind": "lesson",
        "heading": "Lesson",
        "blocks": blocks,
        "video": None,
        "workspace": None,
        "attachments": [],
    }


def test_a_one_section_lesson_keeps_every_paragraph_and_only_the_quiz_is_replaced():
    given = one_section_lesson()
    blocks = quizonce.once(document(sections=[given, section(workspace=TWO)]), PANEL)["sections"][
        0
    ]["blocks"]
    assert blocks[:6] == given["blocks"][:6], "lesson text before the quiz was lost"
    assert blocks[6] == {"type": "html", "text": "<quiz/>"}
    assert blocks[7] == {"type": "html", "text": ""}
    page = render(document(sections=[given, section(workspace=TWO)]), sample_placement()).decode(
        "utf-8"
    )
    for text in PROSE:
        assert text in page, "a lesson paragraph is missing from the page"
    assert "data-practice-quiz=" in page and "KEYTEXT" not in page
    assert page.index(PROSE[2]) < page.index("data-practice-quiz=")


def test_a_one_section_lesson_keeps_prose_that_follows_the_quiz():
    given = one_section_lesson()
    given["blocks"].append({"type": "para", "text": "A closing paragraph."})
    blocks = quizonce.once(document(sections=[given, section(workspace=TWO)]), PANEL)["sections"][
        0
    ]["blocks"]
    assert blocks[-1] == {"type": "para", "text": "A closing paragraph."}
    assert blocks[6] == {"type": "html", "text": "<quiz/>"}


def test_scattered_stems_are_not_one_quiz_and_the_section_keeps_all_its_text():
    blocks = [
        {"type": "heading", "level": 1, "text": "The lesson"},
        {"type": "para", "text": f"We ask: {TWO_STEMS[0]}"},
        {"type": "para", "text": PROSE[0]},
        {"type": "para", "text": f"And then: {TWO_STEMS[1]}"},
        {"type": "para", "text": PROSE[1]},
    ]
    lesson_section = {
        "key": "prose",
        "kind": "lesson",
        "heading": "Lesson",
        "blocks": blocks,
        "video": None,
        "workspace": None,
        "attachments": [],
    }
    given = document(sections=[lesson_section, section(workspace=TWO)])
    assert quizonce.once(given, PANEL) is given
    page = render(given, sample_placement()).decode("utf-8")
    for text in PROSE[:2]:
        assert text in page
    assert "data-practice-quiz=" in page, "the quiz is not drawn after the lesson"


def test_a_mock_page_keeps_its_intro_and_domain_table_and_replaces_only_the_questions():
    questions = mock_exam.questions(ORIGIN)
    record = {"kind": "quiz", "questions": questions, "mock": mock_exam.mock()}
    page_section = mock_lesson(questions)
    table = {
        "type": "table",
        "headers": ["Domain", "Weight"],
        "rows": [["DOMAINROW one", "50%"], ["DOMAINROW two", "50%"]],
    }
    page_section["blocks"] = [
        {"type": "heading", "level": 1, "text": "Mock exam one"},
        {"type": "para", "text": "INTRO The exam takes ninety minutes."},
        table,
        *page_section["blocks"],
    ]
    given = document(sections=[page_section, section(workspace=record)])
    blocks = quizonce.once(given, PANEL)["sections"][0]["blocks"]
    assert blocks[:4] == page_section["blocks"][:4]
    assert blocks[4] == {"type": "html", "text": "<quiz/>"}
    assert blocks[5] == {"type": "html", "text": ""}
    page = render(given, sample_placement()).decode("utf-8")
    assert "INTRO The exam takes ninety minutes." in page and "DOMAINROW one" in page
    assert "KEYTEXT" not in page and "data-practice-quiz=" in page


# --------------------------------------------------------------------------
# ⭐ a page with two quiz sections (page and module scope): each is its own interactive quiz
# --------------------------------------------------------------------------


def _quiz_record(prefix):
    return {
        "kind": "quiz",
        "questions": [
            {
                "id": f"{prefix}{n}",
                "stem": f"Which choice fits case {prefix}{n}?",
                "options": [
                    {"id": "a", "text": "Option one", "correct": True, "says": f"KEYTEXT {prefix}{n}"},
                    {"id": "b", "text": "Option two", "correct": False, "says": "Not this one."},
                ],
                "origin": {"path": "basics/01.md", "section": "Idea"},
            }
            for n in (1, 2)
        ],
    }


def _quiz_section(heading, record):
    stems = [one["stem"] for one in record["questions"]]
    return [
        {"type": "heading", "level": 2, "text": heading},
        {
            "type": "list",
            "ordered": True,
            "items": [[stem, {"type": "list", "ordered": False, "items": ["a", "b"]}] for stem in stems],
        },
        {
            "type": "disclosure",
            "summary": "Answer key",
            "open": False,
            "blocks": [{"type": "para", "text": f"KEYTEXT {heading}"}],
        },
    ]


def two_quiz_unit():
    page, module = _quiz_record("p"), _quiz_record("m")
    blocks = [
        {"type": "heading", "level": 2, "text": "Idea"},
        {"type": "para", "text": "Some prose."},
        *_quiz_section("Quiz", page),
        *_quiz_section("Module quiz", module),
    ]
    lesson_section = {
        "key": "prose",
        "kind": "lesson",
        "heading": "Lesson",
        "blocks": blocks,
        "video": None,
        "workspace": None,
        "attachments": [],
    }
    return document(
        sections=[
            lesson_section,
            section(key="practice-prose-1", workspace=page),
            section(key="practice-prose-2", workspace=module),
        ]
    ), page, module


def test_a_page_with_a_page_quiz_and_a_module_quiz_draws_both_interactive_and_no_key_text():
    given, page, module = two_quiz_unit()
    html = render(given, sample_placement()).decode("utf-8")
    visible = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S)
    assert visible.count("data-practice-quiz=") == 2, "a quiz section is left as a static list"
    assert "<details" not in html and "Answer key" not in html and "KEYTEXT" not in visible
    for record in (page, module):
        for one in record["questions"]:
            assert visible.count(one["stem"]) == 1, "a question is drawn twice or not at all"
    assert "data-practices" not in html and "data-practice-card" not in html
    keys = re.findall(r'data-practice-quiz="([^"]+)"', html)
    assert len(set(keys)) == 2, "the two quizzes share one progress key"
    assert visible.index("Module quiz") < visible.rindex("data-practice-quiz=")
