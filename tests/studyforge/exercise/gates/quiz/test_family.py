"""The `quiz` family: registered by import, ordered by the registry, and unweakenable.

⭐ **The gate framework has a seam and this is the reading that says it is used rather
than widened**: the family exists because `family.py` was imported, the record
requires all five from that moment, and not one line of `families.py`,
`record.py`, `digests.py` or `runs.py` was edited to make it so.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates import (
    Family,
    GateRecord,
    Verdict,
    declared_order,
    family_of,
    record_document,
    record_of,
    register,
    registered,
)
from studyforge.exercise.gates.code import CODE
from studyforge.exercise.gates.quiz import (
    JUDGED,
    MECHANICAL,
    Q1,
    Q2,
    Q3,
    Q4,
    Q5,
    QUESTION_ROLE,
    QUIZ,
    cited_role,
    verdict,
)

WHERE = "corpus/message-shapes/unit-01/practice-1"


def test_the_quiz_family_is_registered_by_importing_the_sub_package():
    # ⭐ THE SEAM, read: nothing named this module at run time and nothing
    # discovered it. The one line outside `gates/quiz/` is the import in the
    # parent package's contract, which R17 obliges a sub-package to have.
    assert QUIZ in registered()
    assert QUIZ.gates == (Q1, Q2, Q3, Q4, Q5)
    for gate in QUIZ.gates:
        assert family_of(gate) == QUIZ.name
    assert family_of("Q0") is None


def test_the_five_split_into_the_three_that_ship_and_the_two_that_are_re_run():
    # ⛔ The distinction R5 turns on, named rather than inferred from which
    # module a gate lives in.
    assert JUDGED == (Q1, Q2, Q3)
    assert MECHANICAL == (Q4, Q5)
    assert (*JUDGED, *MECHANICAL) == QUIZ.gates
    assert not set(JUDGED) & set(MECHANICAL)


def test_the_write_order_puts_the_quiz_after_the_code_family_by_name_alone():
    order = declared_order()
    assert [gate for family, gate in order if family == QUIZ.name] == list(QUIZ.gates)
    families = [family for family, _ in order]
    assert families == sorted(families)
    assert families.index(CODE.name) < families.index(QUIZ.name)


def test_a_family_redeclaring_one_of_these_gates_is_refused():
    # ⛔ The interesting attack is REDECLARING a gate, not deleting one: a
    # second family answering for Q4 with a weaker rule would leave every
    # reader of the record seeing a Q4 that held.
    with pytest.raises(ExerciseError, match="belongs to exactly one"):
        register(Family("weaker-quiz", (Q4,)))
    assert family_of(Q4) == QUIZ.name


def test_registering_the_same_family_again_returns_the_one_already_registered():
    assert register(Family(QUIZ.name, QUIZ.gates)) is QUIZ
    with pytest.raises(ExerciseError, match="registered once and never replaced"):
        register(Family(QUIZ.name, QUIZ.gates[:-1]))


def test_a_cited_role_names_the_question_and_is_a_role_a_record_can_carry():
    assert cited_role("q-1") == f"{QUESTION_ROLE}:q-1"
    # ⛔ OBSERVED rather than reasoned about: the role really does survive the
    # record's own reader, which is what `digests.require_role` decides.
    document = record_document(
        GateRecord(
            origins=(),
            verdicts=tuple(
                Verdict(id=gate, family=QUIZ.name, held=True, says=f"{gate} was read")
                for gate in QUIZ.gates
            ),
        )
    )
    document["origins"] = [
        {
            "role": cited_role("q-1"),
            "path": "lessons/what-a-header-carries.md",
            "section": "What a message header carries",
            "digest": "sha256:" + "0" * 64,
        }
    ]
    assert record_of(document, WHERE).origins[0].role == cited_role("q-1")


def test_a_verdict_for_a_gate_this_family_does_not_declare_is_refused():
    assert verdict(Q4, held=True, says="read").family == QUIZ.name
    with pytest.raises(ExerciseError, match="declares"):
        verdict("G1", held=True, says="answering for somebody else's gate")
    with pytest.raises(ExerciseError, match="declares"):
        verdict("Q6", held=True, says="a gate nothing declares")


def test_a_verdict_whose_held_is_merely_truthy_is_refused():
    # ⚠️ A TypeError from a wrong call signature looks exactly like a refusal,
    # so the exception TYPE is read rather than the fact that something raised.
    with pytest.raises(ExerciseError) as raised:
        verdict(Q4, held=1, says="truthy is not a verdict")
    assert raised.type is ExerciseError
    assert "true or false" in str(raised.value)
    # ⭐ The positive control: the same call with a real boolean does not raise.
    assert verdict(Q4, held=False, says="a real boolean").held is False
