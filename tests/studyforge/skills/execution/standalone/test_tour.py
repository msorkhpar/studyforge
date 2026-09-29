"""Mirror of `src/studyforge/skills/execution/standalone/tour.py` (R12).

⭐ Read off the lines the sections return, for counts written here.
"""

from __future__ import annotations

from studyforge.skills.execution.standalone import tour
from studyforge.skills.execution.standalone.facts import Facts

FULL = Facts(modules=4, units=9, practices=12, quizzes=3, examples=5, areas=("A", "B", "C"))


def test_the_size_sentence_names_every_number_and_the_topic_areas():
    text = "\n".join(tour.holds(FULL))
    assert "9 units in 4 modules, grouped in 3 topic areas: A, B and C." in text
    assert "12 practices: 9 to write in code" in text and "3 short quizzes" in text


def test_a_single_of_each_is_singular():
    text = "\n".join(tour.holds(Facts(modules=1, units=1, practices=1, quizzes=None)))
    assert "1 module and 1 unit" in text and "1 practice." in text


def test_a_count_that_is_not_known_leaves_its_sentence_out():
    assert tour.holds(Facts()) == []
    assert "practice" not in "\n".join(tour.holds(Facts(units=2)))


def test_the_join_reads_as_a_list():
    assert tour.join_and(["a"]) == "a"
    assert tour.join_and(["a", "b"]) == "a and b"
    assert tour.join_and(["a", "b", "c"]) == "a, b and c"


def test_a_picture_appears_only_beside_its_own_feature():
    shots = {"example": "x/example.webp", "quiz": "x/quiz.webp"}
    with_quiz = "\n".join(tour.features(FULL, shots, narrated=False))
    assert "![" in with_quiz and with_quiz.count("![") == 2
    without = "\n".join(
        tour.features(Facts(units=1, examples=None, quizzes=None), shots, narrated=False)
    )
    assert "![" not in without


def test_the_comparison_lists_only_what_the_course_has_and_always_the_set_up():
    text = "\n".join(tour.ways(Facts(units=3), narrated=False))
    assert "| Set-up |" in text and "| Works offline |" in text
    assert "Quizzes" not in text and "Run and Submit" not in text and "Narration" not in text
    full = "\n".join(tour.ways(FULL, narrated=True))
    for row in ("Quizzes", "Run and Submit", "Code examples opened", "Narration"):
        assert row in full
