"""The `review` family, `S1`, and what it asks of a spaced-review bank that `Q1` to `Q5` do not.

**What it does.** Declares one gate, `S1`, and registers it, so a gate record that names the
`review` family is complete only when it carries `S1` as well as `Q1` to `Q5`. `S1` holds when the
bank's schedule is well formed and the bank holds enough questions for it: at least one question
for every step of the schedule, so each step has something to be shown.

**How you use it.**

    verdicts = (*check_quiz(exercise, judgements, origins, ledger, where),
                check_review(exercise, where))

**Depends on.** `family` for the quiz family's name, `gates.families` for the registry,
`gates.record` for `Verdict`, `checks.require_quiz` for what a quiz is, and
`studyforge.exercise.quiz` for the questions and the `review` key.

## ⛔ `Q1` to `Q5` ARE NOT RE-DECLARED, AND NOTHING THEY SAY IS WEAKENED

⭐ **A review bank is a quiz**, so `check_quiz` answers `Q1` to `Q5` over every item unchanged: a
bank item is a quiz question under every rule a quiz question has. ⛔ This family declares a gate of
its own rather than a second claim on one of theirs, because a gate id belongs to exactly one
family. ⚠️ **`S1` is mechanical**: it reads only the exercise, so whoever holds the bundle can
re-run it.
"""

from __future__ import annotations

from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.gates.families import Family, register
from studyforge.exercise.gates.quiz.checks import require_quiz
from studyforge.exercise.gates.quiz.family import QUIZ
from studyforge.exercise.gates.record import Verdict
from studyforge.exercise.record import Exercise

#: The one gate a review bank clears beyond a quiz's five.
S1 = "S1"

#: ⭐ Registered at import: a record naming this family is complete only with `S1`.
REVIEW = register(Family("review", (S1,)))


def check_review(exercise: Exercise, where: str) -> Verdict:
    """Answer `S1` over one review bank — ⛔ refusing an exercise that is not one."""
    questions = require_quiz(exercise, where)
    review = exercise.review
    if review is None:
        raise ExerciseError(
            f"{where}: the review gate reads a quiz that declares a 'review' and this one "
            f"declares none. A quiz is gated by {list(QUIZ.gates)} alone."
        )
    steps = len(review.intervals_days)
    if len(questions) < steps:
        return Verdict(
            id=S1,
            family=REVIEW.name,
            held=False,
            says=f"the schedule has {steps} step(s) and the bank holds {len(questions)} "
            f"question(s), so a step would have nothing to show: a bank holds at least as "
            f"many questions as the schedule has steps",
        )
    return Verdict(
        id=S1,
        family=REVIEW.name,
        held=True,
        says=f"the schedule grows over {steps} step(s) and the bank holds {len(questions)} "
        f"questions to be revisited on it",
    )
