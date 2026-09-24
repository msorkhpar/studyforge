"""What a quiz RECORD carries instead of a workspace, and what it may claim.

⭐ Taken through `exercise.from_document`, which is the path a build takes, so
every refusal here is the one a corpus would actually get.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import (
    EXERCISE_KEYS,
    ExerciseError,
    Origin,
    from_document,
    to_document,
)
from studyforge.exercise.quiz import (
    QUESTIONS,
    QUIZ_KEYS,
    QUIZ_PROVENANCE,
    QUIZ_REQUIRED_KEYS,
    QUIZ_TRUST,
)
from studyforge.unit.trust import PROVENANCE, TRUST
from tests.studyforge.exercise.quiz.depth1 import PAGE, record

WHERE = "depth-one/unit-01/practice-1"

#: A code record, as everything written before `M10` is: the ungraded shape.
CODE_RECORD = {"main_path": "practice/hello.py", "run_command": ["python3", "practice/hello.py"]}


def refuse(written):
    """The sentence `from_document` refuses this record with."""
    with pytest.raises(ExerciseError) as raised:
        from_document(written, WHERE)
    return str(raised.value)


# --------------------------------------------------------------------------
# ⭐ A quiz record round-trips
# --------------------------------------------------------------------------


def test_a_quiz_record_round_trips():
    written = record(provenance=QUIZ_PROVENANCE, trust=QUIZ_TRUST)
    exercise = from_document(written, WHERE)
    assert exercise.is_quiz is True
    assert to_document(exercise) == written, "a written quiz is not the one that was read"
    assert from_document(to_document(exercise), WHERE) == exercise


def test_a_quiz_writes_its_keys_in_the_records_own_order():
    written = to_document(from_document(record(origin=PAGE), WHERE))
    assert tuple(written) == tuple(key for key in EXERCISE_KEYS if key in QUIZ_KEYS)
    assert set(QUIZ_KEYS) <= set(EXERCISE_KEYS), "a quiz key the record does not define"


def test_a_quiz_that_omits_its_provenance_is_written_back_carrying_it():
    # ⚠️ The cost, asserted rather than left to be discovered: a quiz that
    # omits the pair canonicalises to one that carries it. ⭐ Affordable here
    # and not for `kind`, because the installed base of quiz records is zero.
    exercise = from_document(record(), WHERE)
    assert (exercise.provenance, exercise.trust) == (QUIZ_PROVENANCE, QUIZ_TRUST)
    written = to_document(exercise)
    assert written["provenance"] == QUIZ_PROVENANCE and written["trust"] == QUIZ_TRUST
    assert from_document(written, WHERE) == exercise, "the canonical form does not settle"


def test_a_records_own_origin_is_the_one_key_a_quiz_may_omit():
    # ⛔ Read through the RECORD and through whole-document comparison, never by
    # subscripting that key: the one-reader rule holds `origin` to ONE reader across `src/`
    # and `tests/`, and a test that reached for it would be a second one.
    bare = record(provenance=QUIZ_PROVENANCE, trust=QUIZ_TRUST)
    assert from_document(bare, WHERE).origin is None
    assert to_document(from_document(bare, WHERE)) == bare, "a key nobody wrote was written"
    carried = {**bare, "origin": PAGE}
    exercise = from_document(carried, WHERE)
    assert exercise.origin == Origin(PAGE, None)
    assert to_document(exercise) == carried, "the record's own origin did not survive"


# --------------------------------------------------------------------------
# ⛔ questions in place of a workspace, in both directions
# --------------------------------------------------------------------------


@pytest.mark.parametrize("key", ["main_path", "run_command", "test_path", "test_command"])
def test_a_quiz_carrying_a_workspace_key_is_refused(key):
    # ⛔ A quiz has no file for the reader to edit and nothing to execute, so a
    # workspace key on one is a Run affordance no page can honour.
    assert key in refuse(record(**{key: CODE_RECORD.get(key, "practice/x.py")}))


def test_questions_on_a_record_that_is_not_a_quiz_are_refused():
    # ⛔ The other direction: a `code` record carrying questions is a quiz
    # whose key nothing grades against while the corpus validates green.
    assert QUESTIONS in refuse({**CODE_RECORD, QUESTIONS: record()[QUESTIONS]})


def test_a_quiz_asking_nothing_is_refused():
    assert list(QUIZ_REQUIRED_KEYS) == [QUESTIONS]
    assert QUESTIONS in refuse({"kind": "quiz"})


def test_a_quiz_names_no_test_path_so_nothing_a_run_does_completes_it():
    # ⛔ Spec §7 §7: a quiz produces no run. `states` is untouched by the quiz shape,
    # and this is the reading that says so at the record layer.
    exercise = from_document(record(), WHERE)
    assert exercise.graded is False
    assert (exercise.main_path, exercise.run_command) == (None, None)
    assert (exercise.test_path, exercise.test_command) == (None, None)


def test_a_breakdown_on_a_quiz_is_still_refused_beside_no_grader():
    # ⚠️ `cases` and `report` report what a test RUN found, and a quiz has no
    # run. ⛔ The case record's refusal is relied on here, not relaxed.
    cases = [{"id": "T#t", "kind": "main", "says": "It reads."}]
    assert "cases" in refuse(record(cases=cases))


# --------------------------------------------------------------------------
# ⛔ R5: a quiz is never the source's own grader
# --------------------------------------------------------------------------


def test_a_quiz_is_refused_authoritative():
    message = refuse(record(provenance="bundled", trust="authoritative"))
    assert QUIZ_PROVENANCE in message and QUIZ_TRUST in message


@pytest.mark.parametrize("provenance", list(PROVENANCE))
@pytest.mark.parametrize("trust", [*TRUST, None])
def test_no_pair_at_all_makes_a_quiz_authoritative(provenance, trust):
    # ⛔ The closure, taken over EVERY pair `unit.trust` admits rather than
    # over the one R5 already refuses: Q1–Q3 are judgements taken once at
    # authoring and cannot be re-run, so there is no path to `authoritative`.
    # ⚠️ `bundled` with no `trust` is the path R5's general rule leaves open,
    # and it is in this population.
    written = record(provenance=provenance, trust=trust)
    if (provenance, trust) in ((QUIZ_PROVENANCE, QUIZ_TRUST), (QUIZ_PROVENANCE, None)):
        exercise = from_document(written, WHERE)
        assert exercise.authoritative is False
        return
    assert refuse(written), f"{provenance}/{trust} was accepted on a quiz"


def test_the_population_above_reaches_the_pair_r5_itself_allows():
    # ⛔ The sweep above is a comparison, and a population that had
    # stopped containing `bundled` + `authoritative` would satisfy it while
    # measuring nothing.
    assert "bundled" in PROVENANCE and "authoritative" in TRUST
