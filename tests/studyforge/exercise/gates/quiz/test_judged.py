"""`Q1`–`Q3`: a shipped judgement is checkable because its INPUTS are, and that is read here.

⛔ **The clause this file exists for** (`E14` § `AX-06`): *`Q1`–`Q3` are
recorded with the prompt, the pass and the outcome, and a question whose
`Q1`–`Q3` record is absent or whose recorded inputs no longer match is
refused.* ⭐ Each half is taken by doing it: the record is read back out of a
verdict, and the question is really re-authored before the gate is read again.

⚠️ **Every plant asserts the planted STATE and prints it before any gate is
read**, and the negative control — the same quiz with nothing planted — clears
all three, so a suite that refused everything could not pass these.
"""

from __future__ import annotations

import dataclasses

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates.quiz import (
    JUDGED_FIELDS,
    Judgement,
    Q1,
    Q2,
    Q3,
    Q4,
    WHOLE_QUESTION,
    judged_gate,
    question_digest,
    require_judgements,
)
from tests.studyforge.exercise.gates.quiz import material
from tests.studyforge.exercise.gates.quiz.material import WHERE


def clean() -> tuple[tuple, tuple]:
    """The unplanted quiz and every judgement it owes — ⭐ this suite's negative control."""
    questions = material.built(material.planted(material.NONE))
    return questions, material.judgements(questions)


def test_the_unplanted_quiz_holds_every_judged_gate():
    questions, taken = clean()
    for gate in (Q1, Q2, Q3):
        read = judged_gate(gate, questions, taken)
        print(gate, read.held, read.says)
        assert read.held is True, read.says
        assert read.id == gate


def test_q3_owes_one_judgement_per_wrong_option_and_not_one_per_question():
    # ⛔ A gate coarser than the claim it backs is theatre — `G3`'s rule, on a
    # quiz. MEASURED: this quiz has two questions and three wrong options.
    questions, taken = clean()
    wrong = [option for question in questions for option in question.options if not option.correct]
    print("questions:", len(questions), "wrong options:", len(wrong))
    assert len(questions) == 2 and len(wrong) == 3
    assert len([entry for entry in taken if entry.gate == Q3]) == len(wrong)
    assert len([entry for entry in taken if entry.gate == Q1]) == len(questions)

    # ⭐ Dropping ONE wrong option's judgement refuses, which is what "per
    # option" means and what a per-question judgement could never see.
    without = tuple(
        entry
        for entry in taken
        if not (entry.gate == Q3 and entry.option == wrong[0].id and entry.question == "q-1")
    )
    print("judgements dropped:", len(taken) - len(without))
    assert len(without) == len(taken) - 1
    read = judged_gate(Q3, questions, without)
    assert read.held is False
    assert "carries no Q3 judgement at all" in read.says


def test_a_question_with_no_judgement_at_all_is_refused_by_each_gate():
    questions, taken = clean()
    for gate in (Q1, Q2, Q3):
        without = tuple(entry for entry in taken if not (entry.gate == gate))
        # ⭐ The plant, OBSERVED: the judgements really are gone.
        print(gate, "judgements left:", len([e for e in without if e.gate == gate]))
        assert not [entry for entry in without if entry.gate == gate]
        read = judged_gate(gate, questions, without)
        assert read.held is False
        assert "carries no" in read.says
        # ⛔ And the other two still hold, so this is one gate refusing and
        # not a suite that refuses whatever it is handed.
        others = [other for other in (Q1, Q2, Q3) if other != gate]
        assert all(judged_gate(other, questions, without).held for other in others)


def test_a_judgement_that_did_not_hold_is_refused_and_its_outcome_is_quoted():
    questions, taken = clean()
    negative = tuple(
        dataclasses.replace(entry, held=False, outcome="picked a different option each time")
        if entry.gate == Q1 and entry.question == "q-1"
        else entry
        for entry in taken
    )
    planted = [entry for entry in negative if entry.gate == Q1 and not entry.held]
    print("negative judgements:", [(e.gate, e.question, e.held) for e in planted])
    assert len(planted) == 1
    read = judged_gate(Q1, questions, negative)
    assert read.held is False
    assert "picked a different option each time" in read.says
    assert judged_gate(Q2, questions, negative).held is True


def test_a_question_re_authored_after_its_judgement_was_taken_is_refused():
    # ⛔ THE HOLE A SHIPPED JUDGEMENT OPENS, closed: re-author the question,
    # keep the record, and the gate would otherwise still read as held.
    questions, taken = clean()
    rewritten = material.built(material.planted(material.RE_AUTHORED_QUESTION))
    # ⭐ The plant, OBSERVED: the edit is real and it really moved the digest.
    before, after = question_digest(questions[0]), question_digest(rewritten[0])
    print("stem before:", questions[0].stem)
    print("stem after: ", rewritten[0].stem)
    print("digest moved:", before != after)
    assert questions[0].stem != rewritten[0].stem
    assert before != after
    assert question_digest(questions[1]) == question_digest(rewritten[1])

    for gate in (Q1, Q2, Q3):
        read = judged_gate(gate, rewritten, taken)
        assert read.held is False, read.says
        assert "no longer asks" in read.says
    # ⛔ And the control: judgements re-taken over the rewritten question hold.
    assert judged_gate(Q1, rewritten, material.judgements(rewritten)).held is True


def test_a_judgement_for_a_question_the_quiz_no_longer_asks_is_a_finding():
    questions, taken = clean()
    stray = Judgement(
        gate=Q1,
        question="q-9",
        option=WHOLE_QUESTION,
        prompt="asked of a question that was dropped",
        taken_by="an independent pass",
        outcome="picked the keyed option",
        held=True,
        over=question_digest(questions[0]),
    )
    read = judged_gate(Q1, questions, (*taken, stray))
    print(read.says)
    assert read.held is False
    assert "does not offer" in read.says


def test_the_prompt_the_pass_and_the_outcome_are_recorded_and_decide_nothing():
    questions, taken = clean()
    read = judged_gate(Q1, questions, taken)
    recorded = dict(read.recorded)
    print(sorted(recorded))
    for question in questions:
        for field in JUDGED_FIELDS:
            assert f"{field}:{question.id}" in recorded
    assert recorded["prompt:q-1"].startswith("given this page")
    assert recorded["pass:q-1"] == "an independent pass over the page, read twice"
    assert recorded["outcome:q-1"] == "picked the keyed option on both readings"
    assert recorded["over:q-1"] == question_digest(questions[0])

    # ⛔ `held` is the verdict and nothing reads `recorded` to decide anything:
    # an outcome saying the opposite of what happened changes no answer.
    lying = tuple(
        dataclasses.replace(entry, outcome="it failed, obviously") if entry.gate == Q1 else entry
        for entry in taken
    )
    still = judged_gate(Q1, questions, lying)
    assert still.held is True
    assert dict(still.recorded)["outcome:q-1"] == "it failed, obviously"


def test_q3s_recorded_keys_name_the_option_as_well_as_the_question():
    questions, taken = clean()
    recorded = dict(judged_gate(Q3, questions, taken).recorded)
    print(sorted(recorded))
    assert "prompt:q-1:b" in recorded and "prompt:q-1:c" in recorded
    assert "prompt:q-2:a" in recorded
    # ⛔ The keyed option is never judged by Q3: there is nothing to refute.
    assert "prompt:q-1:a" not in recorded


def test_a_quiz_that_asks_nothing_holds_no_judged_gate():
    # ⛔ `all(())` is true, so a quiz whose questions were all dropped would
    # otherwise clear every judged gate it owed a reading for — and it owed
    # none. `AX-03` paid a red gate for this shape.
    _, taken = clean()
    for gate in (Q1, Q2, Q3):
        read = judged_gate(gate, (), taken)
        assert read.held is False
        assert "asks nothing" in read.says


def test_only_a_judged_gate_can_be_answered_from_a_judgement():
    questions, taken = clean()
    with pytest.raises(ExerciseError) as raised:
        judged_gate(Q4, questions, taken)
    assert raised.type is ExerciseError
    assert "mechanical" in str(raised.value)


def test_a_judgement_nobody_could_audit_is_refused():
    questions, taken = clean()
    assert require_judgements(taken, WHERE) == taken
    for field in ("prompt", "taken_by", "outcome"):
        blanked = (dataclasses.replace(taken[0], **{field: "   "}), *taken[1:])
        with pytest.raises(ExerciseError, match="is required and must be text"):
            require_judgements(blanked, WHERE)
    with pytest.raises(ExerciseError, match="not one of"):
        require_judgements((dataclasses.replace(taken[0], gate=Q4),), WHERE)
    with pytest.raises(ExerciseError, match="true or false"):
        require_judgements((dataclasses.replace(taken[0], held=1),), WHERE)
    with pytest.raises(ExerciseError, match="a digest is written"):
        require_judgements((dataclasses.replace(taken[0], over="not-a-digest"),), WHERE)
    with pytest.raises(ExerciseError, match="is a Judgement value"):
        require_judgements(({"gate": Q1},), WHERE)
    with pytest.raises(ExerciseError, match="a sequence of Judgement"):
        require_judgements("Q1", WHERE)
    assert question_digest(questions[0]).startswith("sha256:")


def test_a_q3_judgement_that_names_no_option_is_refused():
    _, taken = clean()
    whole = next(entry for entry in taken if entry.gate == Q3)
    with pytest.raises(ExerciseError, match="names no option"):
        require_judgements((dataclasses.replace(whole, option=WHOLE_QUESTION),), WHERE)


def test_one_judgement_recorded_twice_for_one_thing_is_refused():
    _, taken = clean()
    first = taken[0]
    with pytest.raises(ExerciseError, match="recorded twice"):
        require_judgements((*taken, first), WHERE)


def test_the_digest_is_taken_over_the_whole_question_and_not_only_its_stem():
    questions = material.built(material.planted(material.NONE))
    for changed in (
        material.TWO_KEYS,
        material.DUPLICATE_OPTION,
        material.SILENT_OPTION,
        material.RE_AUTHORED_QUESTION,
    ):
        moved = material.built(material.planted(changed))
        print(changed, question_digest(questions[0]) != question_digest(moved[0]))
        assert question_digest(questions[0]) != question_digest(moved[0])
    # ⭐ And it is stable: two takings of one question are the same bytes (R10).
    again = material.built(material.planted(material.NONE))
    assert question_digest(questions[0]) == question_digest(again[0])
