"""`Q4` and `Q5`: the two gates anybody holding the bundle can re-take, refusing real plants.

⛔ **`AX-06`'s Acceptance, verbatim:** *`Q4` and `Q5` refuse their planted
defects mechanically — two keyed options, a duplicate option, a missing
sentence, an `origin` whose digest drifted.* ⭐ Each is a real edit to the
quiz's own material or to the page's bytes, each is asserted present and
printed before any gate is read, and each is refused **alone** — with the
unplanted quiz clearing both gates as the negative control.

⚠️ **The three `Q4` plants are read at BOTH heights** (`material`'s contract):
the planted document is put to `quiz.questions_of`, which refuses it, and the
planted built questions are put to `Q4`, which is the only thing standing
between them and a bundle at authoring time.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates import Cited
from studyforge.exercise.gates.quiz import (
    Q4,
    Q5,
    cited_for,
    cited_role,
    key_total_and_single,
    origin_still_resolves,
)
from studyforge.exercise.quiz import questions_of
from tests.studyforge.exercise.gates.quiz import material
from tests.studyforge.exercise.gates.quiz.material import WHERE


def clean() -> tuple:
    """The unplanted questions — ⭐ this suite's negative control."""
    return material.built(material.planted(material.NONE))


def origins(questions=None, plant: str = material.NONE) -> tuple[Cited, ...]:
    """The cited passages a record would carry, built from the ledger at authoring time."""
    return cited_for(questions or clean(), material.ledger(plant), WHERE)


def test_the_unplanted_quiz_holds_both_mechanical_gates():
    questions = clean()
    for read in (
        key_total_and_single(questions),
        origin_still_resolves(questions, origins(questions), material.ledger()),
    ):
        print(read.id, read.held, read.says)
        assert read.held is True, read.says
    assert key_total_and_single(questions).id == Q4
    assert origin_still_resolves(questions, origins(questions), material.ledger()).id == Q5


@pytest.mark.parametrize(
    ("plant", "sentence"),
    [
        (material.TWO_KEYS, "keys 2 of its options correct"),
        (material.DUPLICATE_OPTION, "identical to another after normalisation"),
        (material.SILENT_OPTION, "without the one sentence"),
        (material.TOO_FEW_OPTIONS, "cannot choose wrongly"),
    ],
)
def test_q4_refuses_each_planted_defect_alone_and_names_the_question(plant, sentence):
    documents = material.planted(plant)
    questions = material.built(documents)

    # ⭐ THE PLANT, OBSERVED at the other height: the same edit really is a
    # defect, because the document reader refuses it. ⛔ The exception TYPE is
    # read, because a TypeError from a wrong call looks exactly like a refusal.
    with pytest.raises(ExerciseError) as raised:
        questions_of(documents, WHERE)
    assert raised.type is ExerciseError
    print(plant, "->", raised.value)

    read = key_total_and_single(questions)
    print(read.says)
    assert read.held is False
    assert sentence in read.says
    # ⛔ And it is THIS gate refusing, not the suite: Q5 still holds over the
    # same planted questions, because nothing about the page moved.
    assert origin_still_resolves(questions, origins(questions), material.ledger()).held is True


def test_q4_answers_for_every_question_rather_than_the_first_one_that_is_wrong():
    documents = material.planted(material.TWO_KEYS)
    documents[1]["options"][0]["says"] = "  "
    questions = material.built(documents)
    read = key_total_and_single(questions)
    print(read.says)
    assert read.held is False
    assert "keys 2 of its options correct" in read.says
    assert "without the one sentence" in read.says


def test_q5_refuses_a_page_that_has_drifted_in_the_source():
    questions = clean()
    authored = origins(questions)
    drifted = material.ledger(material.DRIFTED_PAGE)

    # ⭐ THE PLANT, OBSERVED: the page's bytes really changed, and the ledger
    # really answers a different digest for the same path. ⚠️ The comparison
    # is between two values this run produced, never against a constant.
    print("page moved:", material.page(material.NONE) != material.page(material.DRIFTED_PAGE))
    print("ledger moved:", material.ledger()[material.PAGE_PATH] != drifted[material.PAGE_PATH])
    assert material.page(material.NONE) != material.page(material.DRIFTED_PAGE)
    assert material.ledger()[material.PAGE_PATH] != drifted[material.PAGE_PATH]

    read = origin_still_resolves(questions, authored, drifted)
    print(read.says)
    assert read.held is False
    assert "has changed in the source" in read.says
    assert material.PAGE_PATH in read.says
    # ⛔ Alone: Q4 reads the questions and nothing about the page.
    assert key_total_and_single(questions).held is True


def test_q5_refuses_a_question_whose_passage_the_record_does_not_carry():
    questions = clean()
    authored = origins(questions)
    dropped = tuple(entry for entry in authored if entry.role != cited_role(questions[0].id))
    print("passages before:", len(authored), "after:", len(dropped))
    assert len(dropped) == len(authored) - 1
    read = origin_still_resolves(questions, dropped, material.ledger())
    assert read.held is False
    assert "no cited passage in the record" in read.says


def test_q5_refuses_a_record_that_cites_material_the_ledger_does_not_account_for():
    questions = clean()
    authored = origins(questions)
    read = origin_still_resolves(questions, authored, {})
    print(read.says)
    assert read.held is False
    assert "does not account for" in read.says


def test_q5_refuses_a_passage_cited_for_a_question_this_quiz_does_not_ask():
    questions = clean()
    stray = (
        *origins(questions),
        Cited(
            role=cited_role("q-9"),
            path=material.PAGE_PATH,
            section=material.PAGE_SECTION,
            digest=material.ledger()[material.PAGE_PATH],
        ),
    )
    read = origin_still_resolves(questions, stray, material.ledger())
    print(read.says)
    assert read.held is False
    assert "a question this quiz does not ask" in read.says


def test_q5_refuses_a_digest_recorded_against_a_different_passage():
    questions = clean()
    authored = list(origins(questions))
    authored[0] = Cited(
        role=authored[0].role,
        path=authored[0].path,
        section="Some other heading entirely",
        digest=authored[0].digest,
    )
    read = origin_still_resolves(questions, tuple(authored), material.ledger())
    print(read.says)
    assert read.held is False
    assert "belongs to different material" in read.says


def test_neither_gate_holds_over_a_quiz_that_asks_nothing():
    # ⛔ `all(())` is true, and a quiz whose questions were all dropped must
    # not clear the two gates it owed a reading for.
    for read in (key_total_and_single(()), origin_still_resolves((), (), material.ledger())):
        assert read.held is False
        assert "asks nothing" in read.says


def test_cited_for_refuses_a_passage_the_ledger_does_not_account_for():
    questions = clean()
    with pytest.raises(ExerciseError) as raised:
        cited_for(questions, {}, WHERE)
    assert raised.type is ExerciseError
    assert "does not account for" in str(raised.value)
    with pytest.raises(ExerciseError, match="not a digest"):
        cited_for(questions, {material.PAGE_PATH: 7}, WHERE)
    # ⭐ The positive control: with the ledger it was authored against, it
    # builds one passage per question and each names its question.
    built = cited_for(questions, material.ledger(), WHERE)
    assert [entry.role for entry in built] == [cited_role(q.id) for q in questions]
    assert {entry.digest for entry in built} == {material.ledger()[material.PAGE_PATH]}
