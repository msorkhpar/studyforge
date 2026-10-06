"""A spaced-review bank: a quiz whose questions the reader revisits on a schedule.

**What it does.** Reads and writes the one optional key a quiz record may carry to say it is a
review bank: `review`, an object holding `intervals_days`, the days that pass before an item the
reader got right is shown again, one entry for each time they get it right in a row. A quiz with no
`review` key is the quiz it always was.

**How you use it.** `review_of(value, where)` reads the key; `review_document(review)` writes it
back; `due(...)` is the rule the page implements, so a browser test can read the page against it.

**Depends on.** `exercise.errors` and `describe`. Nothing that could reach a file, a process or a
socket: the schedule is kept in the reader's own browser, never on a server.

## ⛔ A review bank IS a quiz, and nothing about being one is looser

⭐ The record's `kind` stays `quiz`, so every rule of a quiz holds for a bank unchanged: one keyed
option per question, a sentence per option, a passage per question, `generated` and `advisory`, and
gates `Q1` to `Q5` over every item. ⛔ `review` adds a schedule and takes nothing away. A bank is
never a mock exam: the two keys are refused together.

## ⭐ The schedule is a number list the corpus declares

Item `n` is shown again `intervals_days[min(streak, last) - 1]` days after the reader last
got it right, where `streak` counts the right answers in a row; a wrong answer resets the streak
and the item is due again the same day. The list is strictly increasing whole days from 1 to
`MOST_DAYS`, at most `MOST_STEPS` long.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.describe import describe, describe_keys
from studyforge.exercise.errors import ExerciseError

#: The key a quiz record carries to say it is a review bank.
REVIEW = "review"

#: The review's own keys, in the order they are written (R10).
REVIEW_KEYS = ("intervals_days",)

#: The fewest steps, the most, and the longest wait, in whole days.
MOST_STEPS = 12
MOST_DAYS = 730


@dataclass(frozen=True, slots=True)
class Review:
    """The schedule of one review bank: the days before an item is due again, step by step."""

    intervals_days: tuple[int, ...]


def review_of(value: object, where: str) -> Review:
    """Read the `review` key, refusing every way it can be wrong."""
    if not isinstance(value, dict):
        raise ExerciseError(
            f"{where}: 'review' is an object, {list(REVIEW_KEYS)}. The value is {describe(value)}."
        )
    unknown = [key for key in value if key not in REVIEW_KEYS]
    missing = [key for key in REVIEW_KEYS if key not in value]
    if unknown or missing:
        raise ExerciseError(
            f"{where}: 'review' is {list(REVIEW_KEYS)}, all of them required and nothing else. "
            f"It is missing {missing} and carries {describe_keys(unknown)} it does not define."
        )
    days = value["intervals_days"]
    if (
        not isinstance(days, list)
        or not days
        or len(days) > MOST_STEPS
        or any(not isinstance(one, int) or isinstance(one, bool) for one in days)
    ):
        raise ExerciseError(
            f"{where}: 'intervals_days' is a list of 1 to {MOST_STEPS} whole numbers of days, "
            f"and it is {describe(days)}."
        )
    if (
        days[0] < 1
        or days[-1] > MOST_DAYS
        or any(a >= b for a, b in zip(days, days[1:], strict=False))
    ):
        raise ExerciseError(
            f"{where}: 'intervals_days' grows strictly, from at least 1 day to at most "
            f"{MOST_DAYS}, so a better-known item waits longer."
        )
    return Review(tuple(days))


def review_document(review: Review) -> dict:
    """Return the review as the decoded object, in `REVIEW_KEYS` order (R10)."""
    return {"intervals_days": list(review.intervals_days)}


def due(review: Review, streak: int, last_right_day: int, today: int) -> bool:
    """Say whether an item with `streak` right answers in a row is due on day `today`.

    ⭐ `last_right_day` and `today` are whole days from any one origin. A streak of 0 is always
    due: the item has never been got right, or was got wrong since.
    """
    if streak <= 0:
        return True
    step = min(streak, len(review.intervals_days)) - 1
    return today - last_right_day >= review.intervals_days[step]
