"""The exam-form keys of a mock exam: timer, layout, scenarios, difficulties, sittings, scale,
weights and multiple response. Read, written back byte for byte, refused by name, scored.

**What it asserts.** The fixture course's pool round-trips; a mock with none of the keys writes
what it always wrote; every wrong value is refused and never quoted; a question under an undeclared
scenario, a scenario with no question, a sitting that asks for more than the pool holds and a
pool too thin in one domain for the largest sitting are each refused; a multiple-response question
is right only when exactly its keys are chosen; `quotas` adds up; the scale is linear.
"""

from __future__ import annotations

import copy

import pytest

from studyforge.exercise import ExerciseError, from_document, to_document
from studyforge.exercise.quiz import (
    Scale,
    grade,
    mock_document,
    mock_of,
    quotas,
    questions_of,
    scores,
    scores_by_difficulty,
)
from tests.studyforge.exercise.quiz import mock_exam, mock_form
from tests.studyforge.exercise.quiz.depth1 import PAGE, record, section

WHERE = "depth-one/unit-01/practice-1"
ORIGIN = {"path": PAGE, "section": section()}


def pool(**changes) -> dict:
    parts = {"questions": mock_form.questions(ORIGIN), "mock": mock_form.mock(), **changes}
    return record(**parts)


def refused(document: dict) -> str:
    with pytest.raises(ExerciseError) as raised:
        from_document(document, WHERE)
    return str(raised.value)


def with_mock(**changes) -> dict:
    return pool(mock={**mock_form.mock(), **changes})


def without(key: str) -> dict:
    made = copy.deepcopy(mock_form.mock())
    del made[key]
    return made


def edited_questions(**by_id) -> list[dict]:
    made = copy.deepcopy(mock_form.questions(ORIGIN))
    for one in made:
        for key, value in by_id.get(one["id"], {}).items():
            if value is None:
                one.pop(key, None)
            else:
                one[key] = value
    return made


# ------------------------------------------------------------------ the round trip


def test_the_pool_reads_every_key_and_writes_it_back_byte_for_byte():
    document = pool()
    exercise = from_document(document, WHERE)
    written = to_document(exercise)
    assert written["mock"] == document["mock"] and written["questions"] == document["questions"]
    mock = exercise.mock
    assert (mock.minutes, mock.layout) == (40, "exam")
    assert [s.id for s in mock.scenarios] == ["support-bot", "report-tool", "night-job"]
    assert [d.weight for d in mock.domains] == [60, 40]
    assert mock.scale == Scale(100, 1000, 720) and mock.opts_in
    assert [s.questions for s in mock.sittings] == [10, 5, None]
    assert next(q for q in exercise.questions if q.select).select == 2


def test_a_mock_with_none_of_the_keys_writes_the_bytes_it_always_wrote():
    document = record(
        questions=mock_exam.questions(ORIGIN), mock=mock_exam.mock()
    )
    exercise = from_document(document, WHERE)
    written = to_document(exercise)
    assert written["mock"] == document["mock"] and written["questions"] == document["questions"]
    assert exercise.mock.opts_in is False
    assert set(mock_document(exercise.mock)) == {"pass_mark", "domains"}


# ------------------------------------------------------------------ the mock's own keys


@pytest.mark.parametrize("value", [0, -1, 1441, 1.5, True, "40", None])
def test_minutes_is_a_whole_number_of_minutes_in_range(value):
    assert "minutes" in refused(with_mock(minutes=value))


@pytest.mark.parametrize("value", ["page", "wide", True, None])
def test_the_layout_is_the_exam_layout_or_absent(value):
    assert "layout" in refused(with_mock(layout=value))


def test_a_mock_key_nobody_defines_is_refused():
    assert "nothing else" in refused(with_mock(timer=40))


def test_scenarios_are_distinct_tokens_with_a_title_and_a_context():
    base = mock_form.mock()["scenarios"]
    assert "scenario" in refused(with_mock(scenarios=[]))
    assert "more than once" in refused(with_mock(scenarios=[base[0], base[0], *base[1:]]))
    assert "scenario" in refused(with_mock(scenarios=[{**base[0], "context": " "}, *base[1:]]))
    assert "scenario" in refused(with_mock(scenarios=[{**base[0], "id": "has space"}, *base[1:]]))
    assert "scenario" in refused(with_mock(scenarios=[{"id": "a", "title": "t"}, *base[1:]]))


def test_a_question_under_an_undeclared_scenario_is_refused_without_quoting_it():
    message = refused(pool(questions=edited_questions(p1={"scenario": "nowhere"})))
    assert "not declared" in message and "nowhere" not in message


def test_a_declared_scenario_with_no_question_is_refused():
    questions = edited_questions(p5={"scenario": None}, p6={"scenario": None})
    assert "has no question" in refused(pool(questions=questions))


def test_sittings_name_questions_or_scenarios_not_both_and_count_within_the_pool():
    base = mock_form.mock()["sittings"]
    both = {"id": "x", "title": "X", "questions": 3, "scenarios": 1}
    assert "both" in refused(with_mock(sittings=[both]))
    assert "sitting" in refused(with_mock(sittings=[{"id": "x", "title": "X", "questions": 0}]))
    assert "more than once" in refused(with_mock(sittings=[base[0], base[0]]))
    assert "13 questions" in refused(
        with_mock(sittings=[{"id": "x", "title": "X", "questions": 13}])
    )
    assert "4 scenarios" in refused(
        with_mock(sittings=[{"id": "x", "title": "X", "scenarios": 4}])
    )
    assert "minutes" in refused(
        with_mock(sittings=[{"id": "x", "title": "X", "minutes": 0}])
    )


def test_a_pool_too_thin_in_a_domain_for_the_largest_sitting_is_refused():
    thin = edited_questions(**{f"p{n}": {"domain": "AS1"} for n in (3, 4, 6, 8, 10)})
    with pytest.raises(ExerciseError):
        from_document(pool(questions=thin), WHERE)
    # every domain used still; make AS2 hold one question only while its weight asks for four
    mostly = edited_questions(**{f"p{n}": {"domain": "AS1"} for n in (4, 6, 8, 10)})
    assert "pool holds" in refused(pool(questions=mostly))


def test_the_scale_is_whole_numbers_with_the_pass_between():
    assert "scale" in refused(with_mock(scale={"min": 100, "max": 1000}))
    assert "scale" in refused(with_mock(scale={"min": 1000, "max": 100, "pass": 500}))
    assert "scale" in refused(with_mock(scale={"min": 100, "max": 1000, "pass": 1001}))
    assert "scale" in refused(with_mock(scale={"min": 100, "max": 1000, "pass": 7.5}))


def test_the_scale_is_linear_in_the_questions_right():
    scale = Scale(100, 1000, 720)
    assert [scale.scaled(r, 10) for r in (0, 5, 10)] == [100, 550, 1000]
    assert scale.scaled(0, 0) == 100
    assert scale.scaled(2, 3) == 700


def test_weights_are_stated_for_every_domain_and_sum_to_one_hundred():
    domains = mock_form.mock()["domains"]
    assert "weights" in refused(with_mock(domains=[domains[0], {**domains[1]} | {"weight": 30}]))
    only = [domains[0], {k: v for k, v in domains[1].items() if k != "weight"}]
    assert "weights" in refused(with_mock(domains=only))
    assert "weight" in refused(with_mock(domains=[{**domains[0], "weight": 0}, domains[1]]))


def test_difficulties_are_declared_and_used():
    assert "difficult" in refused(pool(questions=edited_questions(p1={"difficulty": "zzz"})))
    assert "labels no question" in refused(
        with_mock(difficulties=[*mock_form.mock()["difficulties"], {"id": "extra", "title": "E"}])
    )
    assert "difficulties" in refused(with_mock(difficulties=[]))


def test_a_mock_with_no_difficulty_declared_refuses_a_question_that_names_one():
    document = pool(mock=without("difficulties"))
    assert "difficulty" in refused(document)


# ------------------------------------------------------------------ the question's keys


def test_a_question_keys_as_many_options_as_it_asks_the_reader_to_choose():
    questions = edited_questions(p9={"select": 3})
    assert "choose 3" in refused(pool(questions=questions))
    questions = edited_questions(p9={"select": 4})
    assert "choose 4" in refused(pool(questions=questions))
    one_key = edited_questions(p1={"select": 2})
    assert "choose 2" in refused(pool(questions=one_key))


@pytest.mark.parametrize("value", [1, 0, -2, True, "2", 2.0])
def test_select_is_a_whole_number_of_at_least_two(value):
    assert "select" in refused(pool(questions=edited_questions(p9={"select": value})))


def test_a_question_with_two_keys_and_no_select_is_still_refused():
    assert "keys 2" in refused(pool(questions=edited_questions(p9={"select": None})))


@pytest.mark.parametrize("value", [True, "no", 0, None])
def test_shuffle_is_only_ever_false(value):
    questions = edited_questions(p1={"shuffle": value})
    if value is None:
        from_document(pool(questions=questions), WHERE)
    else:
        assert "shuffle" in refused(pool(questions=questions))


@pytest.mark.parametrize("key,value", [("scenario", "x"), ("select", 2), ("shuffle", False),
                                       ("difficulty", "applied")])
def test_the_exam_keys_of_a_question_are_refused_on_a_quiz_with_no_mock(key, value):
    question = {k: v for k, v in mock_exam.questions(ORIGIN)[0].items() if k != "domain"}
    question[key] = value
    if key == "select":
        question["options"][1]["correct"] = True
    with pytest.raises(ExerciseError) as raised:
        from_document(record(questions=[question]), WHERE)
    assert "declares no 'mock'" in str(raised.value)


# ------------------------------------------------------------------ scoring


def questions():
    return questions_of(mock_form.questions(ORIGIN), WHERE)


def test_a_multiple_response_question_is_all_or_nothing():
    asked = next(q for q in questions() if q.select)
    for chosen, right in [(["a", "b"], True), (["b", "a"], True), (["a"], False),
                          (["a", "c"], False), (["a", "b", "c"], False), ([], False),
                          (["a", "a"], False), (["a", "zz"], False), ("a", False), (None, False)]:
        row = grade((asked,), {asked.id: chosen}).answered[0]
        assert row.correct is right, chosen


def test_a_single_key_question_still_takes_one_id():
    asked = questions()[0]
    assert grade((asked,), {asked.id: "b"}).answered[0].correct is True
    assert grade((asked,), {asked.id: ["b"]}).answered[0].correct is False


def test_a_perfect_exam_scores_every_domain_and_difficulty_full():
    asked = questions()
    exercise = from_document(pool(), WHERE)
    answers = mock_form.keyed(mock_form.questions(ORIGIN))
    whole, per_domain = scores(asked, exercise.mock, answers)
    assert (whole.right, whole.asked) == (12, 12)
    assert [(s.domain, s.asked, s.right) for s in per_domain] == [("AS1", 7, 7), ("AS2", 5, 5)]
    by_difficulty = scores_by_difficulty(asked, exercise.mock, answers)
    assert [s.domain for s in by_difficulty] == ["foundational", "applied", "scenario-hard"]
    assert all(s.asked == s.right and s.asked > 0 for s in by_difficulty)
    answers["p9"] = ["a"]
    assert scores(asked, exercise.mock, answers)[0].right == 11


def test_quotas_follow_the_weights_and_add_up():
    exercise = from_document(pool(), WHERE)
    asked = exercise.questions
    for drawn, want in [(10, {"AS1": 6, "AS2": 4}), (5, {"AS1": 3, "AS2": 2}),
                        (7, {"AS1": 4, "AS2": 3}), (12, {"AS1": 7, "AS2": 5})]:
        got = quotas(exercise.mock, drawn, asked)
        assert sum(got.values()) == drawn
        assert got == want or drawn == 12 and got == {"AS1": 7, "AS2": 5}, (drawn, got)


def test_quotas_without_weights_follow_the_pools_shares():
    exercise = from_document(record(questions=mock_exam.questions(ORIGIN),
                                    mock=mock_exam.mock()), WHERE)
    assert quotas(exercise.mock, 3, exercise.questions) == {"D1": 1, "D2": 1, "D3": 1}


def test_mock_of_reads_a_bare_mock_as_before():
    bare = mock_of({"pass_mark": 70, "domains": [{"id": "a", "title": "A"}]}, WHERE)
    assert bare.minutes is None and bare.scenarios == () and bare.opts_in is False


def test_one_key_and_one_wrong_option_of_two_chosen_scores_nothing_and_both_keys_score():
    exercise = from_document(pool(), WHERE)
    asked = exercise.questions
    base = mock_form.keyed(mock_form.questions(ORIGIN))
    full = scores(asked, exercise.mock, base)[0].right
    for chosen, right in ((["a", "c"], False), (["b", "d"], False), (["a", "b"], True)):
        got = scores(asked, exercise.mock, {**base, "p9": chosen})[0].right
        assert got == (full if right else full - 1), chosen
    applied = lambda a: next(  # noqa: E731
        s for s in scores_by_difficulty(asked, exercise.mock, a) if s.domain == "applied"
    )
    assert applied({**base, "p9": ["a", "c"]}).right == applied(base).right - 1
