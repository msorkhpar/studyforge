"""Mirror of `src/studyforge/render/page/mockform.py` (R12): the exam form's markup, both ways.

⛔ **Every clause is asserted BOTH WAYS**: a card, a checkbox, a label that is present where the
mock asks for it, and absent where it does not. The behaviour is `tests/visual/test_mock_form.py`'s.
"""

from __future__ import annotations

import json
import re

from studyforge.exercise import from_document
from studyforge.render.page import mock, mockform
from tests.studyforge.exercise.quiz import mock_exam, mock_form
from tests.studyforge.render.page.test_practice import panel, section

ORIGIN = {"path": "basics/01.md", "section": "What a class is"}
POOL = {"kind": "quiz", "questions": mock_form.questions(ORIGIN), "mock": mock_form.mock()}
PLAIN = {"kind": "quiz", "questions": mock_exam.questions(ORIGIN), "mock": mock_exam.mock()}


def markup(workspace) -> str:
    return panel(sections=[section(workspace=workspace)])


def block(said: str, name: str) -> dict:
    found = re.findall(
        rf'<script type="application/json" data-form-part="{name}">(.*?)</script>', said, re.S
    )
    assert len(found) == 1, f"{len(found)} {name} blocks"
    return json.loads(found[0])


def test_only_an_opted_in_mock_wants_the_exam_form():
    assert mockform.wanted_for(from_document(POOL, "x")) is True
    assert mockform.wanted_for(from_document(PLAIN, "x")) is False
    plain_quiz = {"kind": "quiz", "questions": [mock_exam.questions(ORIGIN)[0]]}
    only = plain_quiz["questions"][0]
    plain_quiz["questions"] = [{k: v for k, v in only.items() if k != "domain"}]
    assert mockform.wanted_for(from_document(plain_quiz, "x")) is False


def test_a_plain_mock_is_rendered_as_it_always_was():
    said = markup(PLAIN)
    assert "data-mock-part=\"controls\"" in said and "data-mock-form" not in said
    assert "mock-form" not in said and "data-form-part" not in said


def test_the_exam_form_carries_every_question_with_its_card_label_and_inputs():
    said = markup(POOL)
    assert 'data-mock-form="exam"' in said and said.count("<legend") == 12
    assert said.count('data-form-part="scenario"') == 6
    assert said.count('type="checkbox"') == 4 and said.count("Choose 2.") == 1
    assert said.count('data-form-part="difficulty"') == 12
    assert 'data-mock-select="2"' in said and 'data-mock-shuffle="false"' in said
    assert "A support bot that forgets" in said and "Scenario, hard" in said


def test_the_key_names_every_keyed_option_and_every_sentence():
    key = block(markup(POOL), "key")
    assert len(key) == 12 and key["p9"]["keys"] == ["a", "b"]
    assert all(set(one["says"]) >= set(one["keys"]) for one in key.values())
    assert all(len(one["says"]) in (3, 4) for one in key.values())


def test_the_plan_states_the_clock_the_sittings_and_the_scale():
    plan = block(markup(POOL), "plan")
    assert (plan["minutes"], plan["layout"], plan["pass_mark"]) == (40, "exam", 70)
    assert [one["id"] for one in plan["sittings"]] == ["full", "short", "scenarios"]
    assert plan["scale"] == {"min": 100, "max": 1000, "pass": 720}
    assert [d.get("weight") for d in plan["domains"]] == [60, 40]
    assert len(plan["difficulties"]) == 3


def test_a_mock_with_a_timer_alone_still_names_no_sitting_or_scale():
    only = {**POOL, "questions": mock_form.questions(ORIGIN)}
    only["mock"] = {**mock_exam.mock(), "minutes": 30}
    only["questions"] = mock_exam.questions(ORIGIN)
    plan = block(markup(only), "plan")
    assert plan["minutes"] == 30 and "sittings" not in plan and "scale" not in plan
    assert plan["layout"] == "page"


def test_the_words_are_ours_and_in_a_block_no_sentence_can_close():
    said = markup(POOL)
    words = block(said, "words")
    assert words["scaled"].count("{score}") == 1 and "linear illustration" in words["scaled"]
    assert "</script><" not in said.split('data-form-part="words">')[1].split("</script>")[0]


def test_the_four_files_are_written_for_an_opted_in_corpus():
    assert sorted(mockform.files()) == sorted(mockform.PARTS)
    assert mockform.PARTS[-1] == "mock-form.js" and mockform.PARTS.index(
        "mock-form-core.js"
    ) < mockform.PARTS.index("mock-form-panels.js") < mockform.PARTS.index("mock-form.js")
    assert mock.files().keys() == {"mock-exam.css", "mock-exam.js"}


def test_the_page_links_the_scripts_in_the_order_they_run():
    said = markup(POOL)
    names = ("mock-form-core.js", "mock-form-panels.js", 'mock-form.js"')
    order = [said.index(name) for name in names]
    assert order == sorted(order)


def test_a_mock_exam_says_it_was_written_from_the_pages_of_the_whole_level():
    for workspace in (POOL, PLAIN):
        said = markup(workspace)
        assert "Written for this site from the pages of the whole level." in said
        assert "Written for this site from this page." not in said
