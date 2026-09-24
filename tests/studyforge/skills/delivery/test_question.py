"""Mirror of `src/studyforge/skills/delivery/question.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.delivery import Answer, Question, QuestionRefused, numbered


def question(**overrides: object) -> Question:
    fields: dict[str, object] = {
        "number": 1,
        "asks": "does placement re-read its own output?",
        "routed_at": "RS-31",
        "blocks": ("C-02",),
        "rerun": "python3 -m pytest tests/studyforge/cli/plan",
    }
    fields.update(overrides)
    return Question(**fields)  # type: ignore[arg-type]


def test_a_question_with_no_way_to_re_run_it_is_refused():
    # ⛔ Answered once and believed forever, which is the failure this field
    # exists to stop.
    with pytest.raises(QuestionRefused, match="does not say how to re-run it"):
        question(rerun="ask")


def test_a_question_routed_at_nobody_is_refused():
    with pytest.raises(QuestionRefused, match="routed at nobody"):
        question(routed_at="")


def test_a_question_that_blocks_nothing_is_curiosity():
    with pytest.raises(QuestionRefused, match="curiosity"):
        question(blocks=())


def test_questions_are_numbered_from_one():
    with pytest.raises(QuestionRefused, match="numbered from 1"):
        question(number=0)


def test_a_question_with_no_text_is_not_one():
    with pytest.raises(QuestionRefused, match="not a question"):
        question(asks="  ")


# --- the decay, which is the point ----------------------------------------


def test_an_open_question_cannot_be_acted_on_and_says_what_to_re_run():
    with pytest.raises(QuestionRefused, match="is open — re-run: python3 -m pytest"):
        question().act_on("8146bdb")


def test_an_answer_stamped_at_the_current_ref_can_be_acted_on():
    settled = question().settled("no, not since the ignore walk", at="8146bdb")
    assert settled.is_current("8146bdb")
    assert settled.act_on("8146bdb") == "no, not since the ignore walk"


def test_a_stale_answer_does_not_come_back_with_a_warning_it_does_not_come_back():
    # ⚠️ A question can close because the framework moved, with nothing having
    # moved in the material, so an answer at another ref does not come back.
    settled = question().settled("no", at="8146bdb")
    assert not settled.is_current("83f767e")
    with pytest.raises(QuestionRefused, match="Re-run before acting"):
        settled.act_on("83f767e")


def test_an_answer_with_no_ref_cannot_be_told_from_a_stale_one():
    with pytest.raises(QuestionRefused, match="no ref"):
        Answer("no", "")


def test_an_answer_with_no_text_answers_nothing():
    with pytest.raises(QuestionRefused, match="answers nothing"):
        Answer("  ", "8146bdb")


def test_settling_a_question_leaves_the_original_untouched():
    original = question()
    original.settled("no", at="8146bdb")
    assert original.open


# --- numbering, because a number is how a question is cited across repos ---


def test_a_repeated_number_is_refused():
    with pytest.raises(QuestionRefused, match=r"\[1, 1\]"):
        numbered((question(number=1), question(number=1, asks="and this one?")))


def test_a_gap_is_a_question_somebody_deleted_rather_than_answered():
    with pytest.raises(QuestionRefused, match=r"\[1, 3\]"):
        numbered((question(number=1), question(number=3)))


def test_a_clean_set_comes_back_in_order():
    ordered = numbered((question(number=2), question(number=1)))
    assert [item.number for item in ordered] == [1, 2]


def test_an_empty_set_is_legal_because_having_no_questions_is_an_answer():
    assert numbered(()) == ()


def test_the_rendered_question_carries_all_five_lines_a_reader_acts_on():
    lines = question().lines()
    assert len(lines) == 5
    assert "routed at:" in lines[1] and "blocks:" in lines[2]
    assert "re-run:" in lines[3] and "⛔ OPEN" in lines[4]
