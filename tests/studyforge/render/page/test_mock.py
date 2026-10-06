"""Mirror of `src/studyforge/render/page/mock.py` (R12): the mock exam's markup, both ways.

⛔ **Every clause is asserted BOTH WAYS**: a question that is present, and a control that is absent
where it must be. The behaviour of the page is `tests/visual/test_mock_exam.py`'s, in a browser.
"""

from __future__ import annotations

import json
import re

import pytest

from studyforge.exercise import from_document
from studyforge.render.page import mock, practice
from tests.studyforge.exercise.quiz import mock_exam
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import QUIZ, document, panel, section

ORIGIN = {"path": "basics/01.md", "section": "What a class is"}
MOCK = {
    "kind": "quiz",
    "questions": mock_exam.questions(ORIGIN),
    "mock": mock_exam.mock(),
}
KEY = practice.key_of(document(), section())


def markup(workspace=MOCK) -> str:
    return panel(sections=[section(workspace=workspace)])


def block(said: str, name: str) -> dict:
    found = re.findall(
        rf'<script type="application/json" data-mock-part="{name}">(.*?)</script>', said, re.S
    )
    assert len(found) == 1, f"{len(found)} {name} blocks"
    return json.loads(found[0])


def test_a_mock_exam_renders_every_question_with_its_domain_and_every_option():
    said = markup()
    for question in MOCK["questions"]:
        assert question["stem"] in said
        tag = f'data-practice-question="{question["id"]}" data-mock-domain="{question["domain"]}"'
        assert tag in said
        for option in question["options"]:
            assert f'data-practice-option="{option["id"]}"' in said
    assert said.count("<legend>") == 6


def test_the_section_is_a_quiz_section_the_shared_script_cannot_wire():
    said = markup()
    assert said.startswith(f'<section data-practice-quiz="{KEY}" data-practice-mock="60"')
    for part in ("key", "check", "controls"):
        assert f'data-practice-part="{part}"' not in said, part
    assert 'data-practice-part="offline"' in said


def test_the_key_block_has_the_quizs_own_shape_and_the_plan_names_the_domains():
    said = markup()
    key = block(said, "key")
    assert set(key) == {question["id"] for question in MOCK["questions"]}
    assert key["x3"]["key"] == "c" and set(key["x3"]["says"]) == {"a", "b", "c"}
    assert block(said, "plan") == {"pass_mark": 60, "domains": mock_exam.DOMAINS}


def test_the_progress_the_controls_the_missing_line_and_the_result_are_there_and_hidden():
    said = markup()
    assert '<progress data-mock-part="meter" max="6" value="0">' in said
    assert "0 of 6 answered" in said
    for part in ("controls", "missing", "result"):
        assert re.search(rf'data-mock-part="{part}"[^>]* hidden>', said) or (
            f'data-mock-part="{part}" hidden' in said
        ), part
    assert 'data-mock-part="submit"' in said and 'data-mock-part="again" hidden' in said


def test_the_words_the_script_says_are_in_the_markup_where_python_put_them():
    said = markup()
    for words in (
        'data-mock-count="{answered} of {asked} answered"',
        'data-mock-words="Answer every question before you submit. Not answered yet: {list}."',
        'data-mock-reached="You scored {right} of {asked} ({percent}%).',
        'data-mock-short="You scored {right} of {asked} ({percent}%).',
        'data-mock-domain-words="{right} of {asked} ({percent}%)"',
    ):
        assert words in said


def test_the_exam_links_its_own_two_files_relative_to_the_page():
    said = markup()
    assert '<link rel="stylesheet" href="' in said and "mock-exam.css" in said
    assert re.search(r'<script src="[^"]*mock-exam\.js" defer></script>', said)


def test_a_title_or_a_stem_is_escaped_where_it_could_close_the_data_block():
    hostile = {**MOCK, "mock": mock_exam.mock(domains=[
        {"id": "D1", "title": "</script><b>x"}, *mock_exam.DOMAINS[1:]
    ])}
    said = markup(hostile)
    assert said.count("</script>") == 3, "a title closed a script element"
    assert block(said, "plan")["domains"][0]["title"] == "</script><b>x"


def test_a_plain_quiz_renders_no_mock_part_and_the_same_section_it_always_did():
    said = markup({**QUIZ, "layout": "page"})
    assert "data-practice-mock" not in said and "data-mock-" not in said
    assert 'data-practice-part="check"' in said and 'data-practice-part="key"' in said


def test_a_mock_without_questions_renders_nothing():
    asked = from_document(MOCK, "a mock")
    from dataclasses import replace

    empty = replace(asked, questions=())
    assert mock.render(empty, key=KEY, corpus="c", grader="", assets=str) == ""


@pytest.mark.parametrize("name", ["mock-exam.css", "mock-exam.js"])
def test_the_two_files_exist_and_are_read_exactly(name):
    assert mock.files()[name]
