"""The exam-form parts of a mock exam: scenarios, difficulties, sittings and the scale.

**What it does.** Defines `Scenario`, `Difficulty`, `Sitting` and `Scale` and reads each from a
`mock` record, refusing every way it can be wrong in one value: a repeated id, a count that is not a
whole number, a scale whose pass lies outside it, a sitting that names both questions and scenarios.

**How you use it.** `quiz.mock.mock_of` calls the readers; `Scale.scaled` is the linear
illustration the page shows.

**Depends on.** `exercise.errors`, `exercise.quiz.options` for the id token, `studyforge.describe`.
What is wrong with the SET (a scenario nobody asks about, a pool too thin for a sitting) is
`mock.require_against_questions`, which needs the questions.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.describe import describe, describe_keys
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.quiz.options import QUIZ_ID, QUIZ_ID_PERMITTED

DIFFICULTY_KEYS = ("id", "title")
SCENARIO_KEYS = ("id", "title", "context")
SITTING_KEYS = ("id", "title", "questions", "scenarios", "per_domain", "minutes")
REQUIRED_SITTING_KEYS = ("id", "title")
SCALE_KEYS = ("min", "max", "pass")

#: The layouts a mock may name. ⭐ Absent is the page it always was: every question on one page.
EXAM_LAYOUT = "exam"
LAYOUTS = (EXAM_LAYOUT,)

#: The longest sitting a timer may state, in minutes: a day, so a typo is a refusal.
LONGEST_SITTING = 1440

#: A scenario's context is two to four sentences, a gate reads it (`P1`), the record does not.
SCENARIO_SENTENCES = (2, 4)


@dataclass(frozen=True, slots=True)
class Difficulty:
    """One label a question may carry, and a score is reported under: a token and its words."""

    id: str
    title: str


@dataclass(frozen=True, slots=True)
class Scenario:
    """A situation several questions are asked about: a token, a title and the context."""

    id: str
    title: str
    context: str


@dataclass(frozen=True, slots=True)
class Sitting:
    """One way to sit the exam: all of it, or a stated number of questions or scenarios.

    ⭐ At most one of `questions` and `scenarios` is set; neither means every question. `minutes`
    is the sitting's own time, and absent it the page takes the mock's time in proportion to the
    questions drawn.
    """

    id: str
    title: str
    questions: int | None = None
    scenarios: int | None = None
    minutes: int | None = None
    #: ⭐ `(domain id, count)` pairs: draw exactly that many questions of each domain. Mutually
    #: exclusive with `questions` and `scenarios`; the sitting's total is the sum.
    per_domain: tuple[tuple[str, int], ...] | None = None


@dataclass(frozen=True, slots=True)
class Scale:
    """A linear illustration of a score on the exam's own scale: its lowest, highest and pass."""

    min: int
    max: int
    pass_: int

    def scaled(self, right: int, asked: int) -> int:
        """The score on this scale, linear in the questions right, rounded to a whole number."""
        if asked <= 0:
            return self.min
        return self.min + ((self.max - self.min) * right * 2 + asked) // (2 * asked)



def sitting_document(sitting: Sitting) -> dict:
    written: dict = {"id": sitting.id, "title": sitting.title}
    for key in ("questions", "scenarios"):
        if getattr(sitting, key) is not None:
            written[key] = getattr(sitting, key)
    if sitting.per_domain is not None:
        written["per_domain"] = dict(sitting.per_domain)
    if sitting.minutes is not None:
        written["minutes"] = sitting.minutes
    return written




def minutes_of(value: object, where: str, sitting: bool = False) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 1 <= value <= LONGEST_SITTING
    ):
        raise ExerciseError(
            f"{where}: {'a sitting' if sitting else 'a mock exam'}'s 'minutes' is a whole "
            f"number from 1 to {LONGEST_SITTING}. The value is {describe(value)}."
        )
    return value


def layout_of(value: object, where: str) -> str:
    if value not in LAYOUTS:
        raise ExerciseError(
            f"{where}: a mock exam's 'layout' is {list(LAYOUTS)}, and the page of old is what "
            f"leaving it out gives. The value is {describe(value)}."
        )
    return value


def _exact(value: object, required: tuple[str, ...], allowed: tuple[str, ...], what: str,
           where: str) -> dict:
    if not isinstance(value, dict) or not set(required) <= set(value) <= set(allowed):
        carried = value if isinstance(value, dict) else {}
        unknown = [key for key in carried if key not in allowed]
        raise ExerciseError(
            f"{where}: {what} is {list(required)} and may also carry "
            f"{[key for key in allowed if key not in required]}, nothing else"
            + (f"; this one carries {describe_keys(unknown)}" if unknown else "")
            + f". The value is {describe(value)}."
        )
    return value


def _token(value: object, whose: str, where: str) -> str:
    if not isinstance(value, str) or not QUIZ_ID.match(value):
        raise ExerciseError(
            f"{where}: {whose} 'id' must be {QUIZ_ID_PERMITTED}. The value is not reproduced "
            f"here, since a refusal never quotes a value that may be personal."
        )
    return value


def _words(value: object, whose: str, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExerciseError(
            f"{where}: {whose}, and it must be text. The value is {describe(value)}."
        )
    return value


def _distinct(ids: list[str], what: str, where: str) -> None:
    repeated = len(ids) - len(set(ids))
    if repeated:
        raise ExerciseError(
            f"{where}: a mock exam names {repeated} {what} id more than once. The ids are not "
            f"reproduced here, since a refusal never quotes a value that may be personal."
        )


def scenarios_of(value: object, where: str) -> tuple[Scenario, ...]:
    if isinstance(value, str) or not isinstance(value, (list, tuple)) or not value:
        raise ExerciseError(
            f"{where}: a mock exam's 'scenarios' is a non-empty array of {list(SCENARIO_KEYS)} "
            f"objects, or left out. The value is {describe(value)}."
        )
    found = []
    for entry in value:
        entry = _exact(entry, SCENARIO_KEYS, SCENARIO_KEYS, "a scenario", where)
        found.append(Scenario(
            _token(entry["id"], "a scenario's", where),
            _words(entry["title"], "a scenario's 'title' names it", where),
            _words(entry["context"], "a scenario's 'context' is the situation it sets", where),
        ))
    _distinct([one.id for one in found], "scenario", where)
    return tuple(found)


def _count(value: object, what: str, where: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ExerciseError(
            f"{where}: a sitting's {what!r} is a whole number of at least 1. The value is "
            f"{describe(value)}."
        )
    return value


def _per_domain(value: object, where: str) -> tuple[tuple[str, int], ...]:
    if not isinstance(value, dict) or not value:
        raise ExerciseError(
            f"{where}: a sitting's 'per_domain' is a non-empty object of domain id to a count. "
            f"The value is {describe(value)}."
        )
    return tuple(
        (_token(domain, "a per_domain domain", where), _count(count, "per_domain", where))
        for domain, count in value.items()
    )


def sittings_of(value: object, where: str) -> tuple[Sitting, ...]:
    if isinstance(value, str) or not isinstance(value, (list, tuple)) or not value:
        raise ExerciseError(
            f"{where}: a mock exam's 'sittings' is a non-empty array of sitting objects, or "
            f"left out. The value is {describe(value)}."
        )
    found = []
    for entry in value:
        entry = _exact(entry, REQUIRED_SITTING_KEYS, SITTING_KEYS, "a sitting", where)
        if "questions" in entry and "scenarios" in entry:
            raise ExerciseError(
                f"{where}: a sitting draws a number of 'questions' or a number of 'scenarios', "
                f"and this one names both."
            )
        if "per_domain" in entry and ("questions" in entry or "scenarios" in entry):
            raise ExerciseError(
                f"{where}: a sitting draws a count 'per_domain' or a number of 'questions' or "
                f"'scenarios', and this one names more than one."
            )
        found.append(Sitting(
            _token(entry["id"], "a sitting's", where),
            _words(entry["title"], "a sitting's 'title' names it", where),
            _count(entry["questions"], "questions", where) if "questions" in entry else None,
            _count(entry["scenarios"], "scenarios", where) if "scenarios" in entry else None,
            minutes_of(entry["minutes"], where, sitting=True) if "minutes" in entry else None,
            _per_domain(entry["per_domain"], where) if "per_domain" in entry else None,
        ))
    _distinct([one.id for one in found], "sitting", where)
    return tuple(found)


def scale_of(value: object, where: str) -> Scale:
    entry = _exact(value, SCALE_KEYS, SCALE_KEYS, "a scale", where)
    numbers = [entry[key] for key in SCALE_KEYS]
    if any(not isinstance(one, int) or isinstance(one, bool) for one in numbers):
        raise ExerciseError(
            f"{where}: a scale's 'min', 'max' and 'pass' are whole numbers. The value is "
            f"{describe(value)}."
        )
    low, high, line = numbers
    if not 0 <= low < high or not low <= line <= high:
        raise ExerciseError(
            f"{where}: a scale runs from a 'min' of at least 0 to a higher 'max', and its "
            f"'pass' lies between them."
        )
    return Scale(low, high, line)


def difficulties_of(value: object, where: str) -> tuple[Difficulty, ...]:
    if isinstance(value, str) or not isinstance(value, (list, tuple)) or not value:
        raise ExerciseError(
            f"{where}: a mock exam's 'difficulties' is a non-empty array of "
            f"{list(DIFFICULTY_KEYS)} objects, or left out. The value is {describe(value)}."
        )
    found = []
    for entry in value:
        entry = _exact(entry, DIFFICULTY_KEYS, DIFFICULTY_KEYS, "a difficulty", where)
        found.append(Difficulty(
            _token(entry["id"], "a difficulty's", where),
            _words(entry["title"], "a difficulty's 'title' names it", where),
        ))
    _distinct([one.id for one in found], "difficulty", where)
    return tuple(found)
