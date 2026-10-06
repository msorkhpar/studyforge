"""Mirror of `src/studyforge/exercise/quiz/mock.py` (R12): what makes a quiz a mock exam.

**What it asserts.** The record reads a `mock` key and a question's `domain` and writes them back
byte for byte; a quiz with neither is the quiz it always was, bytes included; every wrong value is
refused by name and never quoted; `scores` is the rule the page implements, taken on every answer a
reader can give; and a mock exam is still a quiz in every rule a quiz has.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError, from_document, to_document
from studyforge.exercise.quiz import (
    DOMAIN_KEY,
    HIGHEST_PASS_MARK,
    LOWEST_PASS_MARK,
    Mock,
    grade,
    mock_document,
    mock_of,
    passed,
    questions_of,
    scores,
)
from tests.studyforge.exercise.quiz import mock_exam
from tests.studyforge.exercise.quiz.depth1 import PAGE, record, section

WHERE = "depth-one/unit-01/practice-1"
ORIGIN = {"path": PAGE, "section": section()}


def exam(**changes) -> dict:
    """A mock exam's record: six questions, three domains, a pass mark."""
    parts = {"questions": mock_exam.questions(ORIGIN), "mock": mock_exam.mock(), **changes}
    return record(**parts)


def refused(document: dict) -> str:
    with pytest.raises(ExerciseError) as raised:
        from_document(document, WHERE)
    return str(raised.value)


def asked():
    return from_document(exam(), WHERE).questions


def mocked() -> Mock:
    return from_document(exam(), WHERE).mock


# --------------------------------------------------------------- reading and writing


def test_a_mock_exam_reads_its_mock_and_each_questions_domain():
    exercise = from_document(exam(), WHERE)
    assert exercise.is_quiz and exercise.mock.pass_mark == mock_exam.PASS_MARK
    assert [domain.id for domain in exercise.mock.domains] == ["D1", "D2", "D3"]
    assert [question.domain for question in exercise.questions] == [
        "D1",
        "D1",
        "D2",
        "D2",
        "D3",
        "D3",
    ]


def test_a_mock_exam_writes_back_the_bytes_it_was_read_from():
    document = exam(provenance="generated", trust="advisory")
    written = to_document(from_document(document, WHERE))
    assert written == document, "a mock exam does not round-trip"
    assert list(written) == ["provenance", "trust", "kind", "questions", "mock"]
    assert from_document(written, WHERE) == from_document(document, WHERE)


def test_a_question_writes_its_domain_last_and_only_where_it_has_one():
    with_domain = to_document(from_document(exam(), WHERE))["questions"][0]
    assert list(with_domain)[-1] == DOMAIN_KEY
    plain = to_document(from_document(record(), WHERE))["questions"][0]
    assert DOMAIN_KEY not in plain


def test_a_quiz_with_no_mock_is_written_exactly_as_before():
    exercise = from_document(record(), WHERE)
    assert exercise.mock is None
    assert "mock" not in to_document(exercise)
    assert all(question.domain is None for question in exercise.questions)


def test_a_domain_on_a_quiz_that_declares_no_mock_is_refused():
    one = mock_exam.questions(ORIGIN)[:1]
    message = refused(record(questions=one))
    assert "domain" in message and "mock" in message


def test_mock_on_a_record_that_is_not_a_quiz_is_refused_naming_the_key():
    code = {"main_path": "p/x.py", "run_command": ["python3", "p/x.py"], "mock": mock_exam.mock()}
    assert "mock" in refused(code)


# --------------------------------------------------------------- what is refused


@pytest.mark.parametrize(
    "value",
    [
        0,
        101,
        -5,
        70.5,
        "70",
        True,
        None,
        [70],
        {"a": 1},
    ],
)
def test_a_pass_mark_that_is_not_a_whole_percent_from_1_to_100_is_refused(value):
    message = refused(exam(mock=mock_exam.mock(pass_mark=value)))
    assert "pass_mark" in message and str(LOWEST_PASS_MARK) in message
    assert str(HIGHEST_PASS_MARK) in message


@pytest.mark.parametrize("value", [1, 60, 100])
def test_the_bounds_and_the_middle_are_accepted(value):
    assert mock_of({"pass_mark": value, "domains": mock_exam.DOMAINS}, WHERE).pass_mark == value


@pytest.mark.parametrize(
    "domains",
    [
        [],
        "D1",
        None,
        [{"id": "D1"}],
        [{"title": "x"}],
        ["D1"],
        [{"id": "D1", "title": "x", "weight": 3}],
        [{"id": "D 1", "title": "x"}],
        [{"id": "", "title": "x"}],
        [{"id": "D1", "title": "  "}],
        [{"id": "D1", "title": 3}],
    ],
)
def test_a_domain_list_that_is_not_ids_and_titles_is_refused(domains):
    assert "domain" in refused(exam(mock=mock_exam.mock(domains=domains)))


def test_two_domains_with_one_id_are_refused_without_quoting_the_id():
    twice = [{"id": "SECRET-ID", "title": "a"}, {"id": "SECRET-ID", "title": "b"}]
    message = refused(exam(mock=mock_exam.mock(domains=twice)))
    assert "more than once" in message and "SECRET-ID" not in message


@pytest.mark.parametrize("extra", [{"passmark": 70}, {"title": "x"}])
def test_a_mock_with_a_key_it_does_not_define_is_refused(extra):
    assert "mock" in refused(exam(mock={**mock_exam.mock(), **extra}))


def test_a_mock_missing_a_key_is_refused():
    assert "pass_mark" in refused(exam(mock={"domains": mock_exam.DOMAINS}))


@pytest.mark.parametrize("domain", ["", "a b", 3, ["D1"], "d/1"])
def test_a_question_domain_that_is_not_a_token_is_refused(domain):
    first, *rest = mock_exam.questions(ORIGIN)
    assert "domain" in refused(exam(questions=[{**first, "domain": domain}, *rest]))


def test_a_mock_exam_is_still_refused_authoritative_and_still_needs_one_key_per_question():
    assert refused(exam(provenance="bundled", trust="authoritative"))
    first, *rest = mock_exam.questions(ORIGIN)
    two_keys = {**first, "options": [{**o, "correct": True} for o in first["options"]]}
    assert refused(exam(questions=[two_keys, *rest]))


# --------------------------------------------------------------- the rule the page implements


def test_every_question_right_scores_the_whole_exam_and_every_domain_full():
    whole, per_domain = scores(asked(), mocked(), mock_exam.keyed())
    assert (whole.asked, whole.right, whole.percent) == (6, 6, 100)
    assert [(s.domain, s.asked, s.right) for s in per_domain] == [
        ("D1", 2, 2),
        ("D2", 2, 2),
        ("D3", 2, 2),
    ]
    assert passed(whole, mocked())


def test_every_question_wrong_scores_zero_and_does_not_pass():
    whole, per_domain = scores(asked(), mocked(), mock_exam.wrong())
    assert (whole.right, whole.percent) == (0, 0)
    assert [s.right for s in per_domain] == [0, 0, 0]
    assert not passed(whole, mocked())


def test_a_score_is_read_per_domain_not_only_in_total():
    answers = {**mock_exam.keyed(), "x1": "b", "x2": "a", "x5": "a"}
    whole, per_domain = scores(asked(), mocked(), answers)
    assert (whole.right, whole.percent) == (3, 50)
    assert [(s.domain, s.right) for s in per_domain] == [("D1", 0), ("D2", 2), ("D3", 1)]
    assert not passed(whole, mocked()), "50 is under the pass mark of 60"


def test_a_percent_is_rounded_down_so_two_of_three_is_never_a_67():
    three = Mock(pass_mark=67, domains=mocked().domains)
    questions = asked()[:3]
    whole, _ = scores(questions, three, {"x1": "a", "x2": "b", "x3": "a"})
    assert (whole.right, whole.percent) == (2, 66)
    assert not passed(whole, three)


@pytest.mark.parametrize("right,expected", [(3, False), (4, True), (5, True)])
def test_the_pass_mark_is_reached_at_exactly_the_percent_it_names(right, expected):
    answers = dict(list(mock_exam.keyed().items())[:right])
    answers.update(dict(list(mock_exam.wrong().items())[right:]))
    whole, _ = scores(asked(), mocked(), answers)
    assert passed(whole, mocked()) is expected  # 4 of 6 is 66, 3 of 6 is 50, mark 60


@pytest.mark.parametrize("answers", [None, "x", [], {}, {"x1": "zzz"}, {"nope": "a"}, 7])
def test_scoring_is_total_and_an_unrecognised_answer_is_not_a_right_one(answers):
    whole, per_domain = scores(asked(), mocked(), answers)
    assert whole.right == 0 and [s.right for s in per_domain] == [0, 0, 0]


def test_a_question_is_right_here_exactly_when_the_quiz_rule_says_it_is():
    answers = {**mock_exam.keyed(), "x3": "a", "x6": "a"}
    whole, _ = scores(asked(), mocked(), answers)
    assert whole.right == grade(asked(), answers).right == 4


def test_a_question_with_an_undeclared_domain_counts_toward_the_whole_and_no_domain():
    first, *rest = mock_exam.questions(ORIGIN)
    odd = questions_of([{**first, "domain": "ZZ"}, *rest], WHERE)
    whole, per_domain = scores(odd, mocked(), mock_exam.keyed())
    assert whole.right == 6 and sum(s.right for s in per_domain) == 5


def test_an_exam_that_asked_nothing_did_not_pass():
    whole, _ = scores((), mocked(), {})
    assert not passed(whole, mocked())


def test_a_mock_documents_itself_in_the_order_it_was_read():
    assert mock_document(mocked()) == mock_exam.mock()
    assert list(mock_document(mocked())) == ["pass_mark", "domains"]
