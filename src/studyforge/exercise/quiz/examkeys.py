"""The optional keys of a question that only a mock exam's page reads.

**What it does.** Names them and reads the two that carry a rule of their own: `select` (how many
options a multiple-response question asks the reader to choose) and `shuffle` (only ever `false`).
The others, `scenario` and `difficulty`, are tokens read like an id.

**How you use it.** `questions` calls `read_select` and `read_shuffle` and writes `EXTRA_KEYS` after
`domain`, only where a question carries them, so a question written before them round-trips to the
same bytes (R10).

**Depends on.** `exercise.errors` and `studyforge.describe` (R7).

## The keys

- `scenario`: an id of the mock's `scenarios`, the situation the question is asked under.
- `difficulty`: an id of the mock's `difficulties`, shown beside the question and scored apart.
- `select`: a whole number of at least 2, how many options the reader chooses. Exactly that many
  options are keyed, and a question with no `select` keys one.
- `shuffle`: `false` keeps this question's options in the order written; leaving it out lets the
  page shuffle them in a mock that has sittings.
"""

from __future__ import annotations

from studyforge.describe import describe
from studyforge.exercise.errors import ExerciseError

SCENARIO_KEY = "scenario"
SELECT_KEY = "select"
SHUFFLE_KEY = "shuffle"
DIFFICULTY_KEY = "difficulty"

#: In the order they are written, after `domain`.
EXTRA_KEYS = (SCENARIO_KEY, SELECT_KEY, SHUFFLE_KEY, DIFFICULTY_KEY)

#: A multiple-response question keys at least this many options, and states the number.
MINIMUM_SELECT = 2


def read_select(value: object, where: str) -> int:
    """Refuse a `select` that is not a whole number of at least two (a bool is not a number)."""
    if not isinstance(value, int) or isinstance(value, bool) or value < MINIMUM_SELECT:
        raise ExerciseError(
            f"{where}: a question's 'select' is how many options a reader chooses and it is "
            f"a whole number of at least {MINIMUM_SELECT}; a question with one key leaves it "
            f"out. The value is {describe(value)}."
        )
    return value


def read_shuffle(value: object, where: str) -> bool:
    """Refuse anything but `false`: shuffling is the default and is not a key to restate."""
    if value is not False:
        raise ExerciseError(
            f"{where}: a question's 'shuffle' is only ever false, to keep its options in the "
            f"order they were written; a question that may be shuffled leaves it out. The "
            f"value is {describe(value)}."
        )
    return False


def require_no_exam_keys_on_questions(
    questions: tuple, where: str, allow_select: bool = False
) -> None:
    """⛔ Refuse a mock-only question key on a quiz that declares no `mock`.

    ⭐ `select` is allowed when a stepper draws the quiz (`allow_select`), not with `layout: page`.
    """
    for question in questions:
        if (
            question.scenario is not None
            or (question.select is not None and not allow_select)
            or question.shuffle is not None
            or question.difficulty is not None
        ):
            raise ExerciseError(
                f"{where}: a question names a 'scenario', 'select', 'shuffle' or 'difficulty' "
                f"on a quiz that "
                f"declares no 'mock'. Those are what a mock exam's page reads, so on a plain "
                f"quiz they are keys nothing reads while the corpus validates green."
            )
