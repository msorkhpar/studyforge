"""The quiz sub-package's contract and public surface."""

from __future__ import annotations

from studyforge import exercise
from studyforge.exercise import quiz
from tests.support import assert_package_contract


def test_the_package_states_its_contract():
    assert_package_contract(quiz, "studyforge.exercise.quiz")


def test_the_public_surface_is_declared_and_complete():
    assert set(quiz.__all__) == {
        "DIFFICULTY_KEY",
        "SCENARIO_SENTENCES",
        "DOMAIN_KEY",
        "MINIMUM_SELECT",
        "MOCK_QUESTION_KEYS",
        "SCENARIO_KEY",
        "SELECT_KEY",
        "SHUFFLE_KEY",
        "Difficulty",
        "Scale",
        "Scenario",
        "Sitting",
        "quotas",
        "scores_by_difficulty",
        "DOMAIN_KEYS",
        "HIGHEST_PASS_MARK",
        "KEYED_OPTIONS",
        "LOWEST_PASS_MARK",
        "MOCK",
        "MOCK_KEYS",
        "MINIMUM_OPTIONS",
        "NO_ANSWERS",
        "OPTION_KEYS",
        "QUESTIONS",
        "QUESTION_KEYS",
        "QUIZ_ID",
        "QUIZ_ID_PERMITTED",
        "QUIZ_KEYS",
        "QUIZ_PROVENANCE",
        "QUIZ_REQUIRED_KEYS",
        "QUIZ_TRUST",
        "Answered",
        "Domain",
        "Mock",
        "Option",
        "Question",
        "Score",
        "Verdict",
        "completes",
        "grade",
        "mock_document",
        "mock_in",
        "mock_of",
        "normalised",
        "passed",
        "questions_document",
        "questions_in",
        "questions_of",
        "require_no_mock",
        "require_no_questions",
        "require_quiz_shape",
        "scores",
    }
    for name in quiz.__all__:
        assert hasattr(quiz, name), name


def test_everything_the_record_takes_from_here_is_on_that_surface():
    # ⛔ The producer half of the export rule, asserted where the consumer is a sibling
    # module: `exercise.record` reads this sub-package, and a name it takes
    # that is not exported is a surface this contract failed to declare.
    taken = ("QUESTIONS", "QUIZ_KEYS", "questions_document", "questions_in", "require_no_questions")
    assert set(taken) <= set(quiz.__all__)


def test_the_quiz_is_reachable_without_naming_a_module_inside_it():
    # ⭐ The import surface a dependent uses: the package,
    # never `studyforge.exercise.quiz.questions`.
    assert quiz.grade is not None and quiz.completes is not None
    assert exercise.QUIZ in exercise.EXERCISE_KINDS


def test_the_exercise_package_names_the_quiz_in_its_own_table():
    # ⚠️ R17: the parent's contract is where a reader finds out this exists,
    # and a sub-package missing from it is one nobody discovers.
    assert "`quiz`" in (exercise.__doc__ or "")
