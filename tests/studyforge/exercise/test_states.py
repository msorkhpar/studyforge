"""The three states, and what may complete a practice (SF-23).

⭐ **Every state is asserted from the structure**, never from a field, because
that is the design: there is no `state` to set and none to forget.
"""

import pytest

from studyforge.exercise import (
    COMMANDS,
    GRADED,
    GRADER_KEY,
    NONE,
    RUN,
    STATES,
    TEST,
    UNGRADED,
    completes_practice,
    from_document,
    state_of,
)

PROMPT = [{"type": "para", "text": "Write a greeter."}]
RECORD = {
    "main_path": "practice/src/main/java/Solution.java",
    "test_path": "practice/src/test/java/SolutionTest.java",
    "run_command": ["mvn", "-q", "compile"],
    "test_command": ["mvn", "-q", "test"],
    "provenance": "bundled",
    "trust": "authoritative",
}


# --------------------------------------------------------------------------
# ⛔ three states, read off the structure
# --------------------------------------------------------------------------


def test_no_practice_document_at_all_is_none():
    # ⚠️ The common case, and the reason this takes `None` rather than
    # refusing it: ISO-8583 is `none` for all 38 units and writes nothing.
    assert state_of(None) == NONE


def test_a_practice_document_with_no_exercise_key_is_ungraded():
    # ⭐ SPARQL's shape: all 19 lessons end in an exercise and none ships a
    # test. Recording these as "no exercise" would delete real teaching
    # content to satisfy a two-state model.
    assert state_of({"kind": "practice", "blocks": PROMPT}) == UNGRADED


def test_a_practice_document_whose_record_names_a_grader_is_graded():
    assert state_of({"kind": "practice", "blocks": PROMPT, "exercise": RECORD}) == GRADED


def test_the_state_is_not_a_field_anybody_writes():
    # ⛔ The assertion behind the design: nothing named `state` appears in a
    # document, so there is nothing to set wrongly and nothing to disagree
    # with the files.
    document = {"kind": "practice", "blocks": PROMPT, "exercise": RECORD}
    assert "state" not in document
    assert state_of(document) == GRADED


def test_a_practice_whose_record_names_a_file_and_no_grader_is_ungraded():
    # ⭐ `W357`: the unit names its file, and nothing checks it. ⛔ The key's
    # presence is no longer the graded state; the grader's is.
    record = {"main_path": RECORD["main_path"], "run_command": RECORD["run_command"]}
    assert state_of({"kind": "practice", "blocks": PROMPT, "exercise": record}) == UNGRADED
    with_grader = {**record, GRADER_KEY: RECORD[GRADER_KEY]}
    assert state_of({"kind": "practice", "blocks": PROMPT, "exercise": with_grader}) == GRADED


def test_the_state_and_the_record_answer_graded_alike():
    # ⭐ One question, asked two ways: `state_of` on the document and
    # `Exercise.graded` on the record it holds.
    for record in (RECORD, {k: RECORD[k] for k in ("main_path", "run_command")}):
        document = {"kind": "practice", "blocks": PROMPT, "exercise": record}
        assert (state_of(document) == GRADED) is from_document(record, "here").graded


@pytest.mark.parametrize("value", [None, [], "exercise", 7, True])
def test_a_record_that_is_not_an_object_is_never_graded(value):
    # ⛔ `state_of` answers on the completion path and does not validate, so
    # anything it cannot read as a grader completes nothing. `parse` refuses it.
    document = {"kind": "practice", "blocks": PROMPT, "exercise": value}
    assert state_of(document) == UNGRADED
    assert completes_practice(state_of(document), TEST, passed=True) is False


def test_the_three_states_are_three_names():
    assert STATES == (NONE, UNGRADED, GRADED)
    assert len(set(STATES)) == 3


# --------------------------------------------------------------------------
# ⛔ only a passing grader run completes a practice
# --------------------------------------------------------------------------


def test_a_passing_grader_run_on_a_graded_exercise_completes_it():
    assert completes_practice(GRADED, TEST, passed=True) is True


def test_an_ungraded_exercise_cannot_complete_a_practice():
    # ⛔ E06's named acceptance. An ungraded exercise has nothing that could
    # pass; a reader works it and it completes nothing.
    assert completes_practice(UNGRADED, TEST, passed=True) is False
    # ⭐ `W357`: including one that names its file.
    record = {"main_path": RECORD["main_path"], "run_command": RECORD["run_command"]}
    named = state_of({"kind": "practice", "blocks": PROMPT, "exercise": record})
    assert completes_practice(named, TEST, passed=True) is False


def test_a_unit_with_no_exercise_cannot_complete_a_practice():
    assert completes_practice(NONE, TEST, passed=True) is False


def test_a_run_never_completes_a_practice_however_well_it_went():
    # ⛔ **Run and Submit are different acts.** A program that printed
    # successfully has demonstrated nothing about its tests — inherited
    # verbatim from the extraction source's progress rules, not negotiable.
    assert completes_practice(GRADED, RUN, passed=True) is False


def test_a_failing_grader_run_does_not_complete_a_practice():
    assert completes_practice(GRADED, TEST, passed=False) is False


@pytest.mark.parametrize("passed", [None, 0, 1, "", "yes", [], {}])
def test_only_a_literal_pass_counts_as_passing(passed):
    # ⚠️ `passed is True`, not truthiness. A runner returning `1` for "one
    # test failed" would otherwise complete the practice, and a shell's exit
    # code is exactly that shape.
    assert completes_practice(GRADED, TEST, passed=passed) is False


@pytest.mark.parametrize("state", ["Graded", "GRADED", "done", None, 1])
def test_an_unrecognised_state_completes_nothing_and_does_not_raise(state):
    # ⭐ Returns `False` rather than raising: this is asked on the completion
    # path, and a caller that had to catch an exception to learn "no" is one
    # that will eventually not catch it and complete a practice on an error.
    assert completes_practice(state, TEST, passed=True) is False


@pytest.mark.parametrize("command", ["submit", "Test", "check", None])
def test_an_unrecognised_command_completes_nothing(command):
    # ⚠️ `submit` is the button's word; `test` is the record's field. The
    # vocabulary follows the data, so the UI's name is not accepted here.
    assert completes_practice(GRADED, command, passed=True) is False


def test_the_two_acts_are_the_two_the_record_carries():
    assert COMMANDS == (RUN, TEST)
    assert {RUN, TEST} == {"run", "test"}
