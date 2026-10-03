"""A mock exam: a quiz that covers a whole level, scored per domain against a pass mark.

**What it does.** Reads and writes the one optional key a quiz record may carry to say it
is a mock exam: `mock`, an object with a `pass_mark` and the `domains` the questions are
scored under. Every question of a mock exam names one of those domains in its own optional
`domain` key (`questions`). A quiz with no `mock` key is the quiz it always was.

**How you use it.** `mock_of(value, where)` reads the key; `mock_document(mock)` writes it
back; `scores(questions, mock, answers)` is the rule the page implements, so a browser
test can read the page against it.

**Depends on.** `exercise.errors`, `exercise.quiz.questions` and `exercise.quiz.grading`;
`describe` to name a value without reproducing it (R7). Nothing that could reach a file, a
process or a socket: grading stays in the page.

## ⛔ A mock exam IS a quiz, and nothing about being one is looser

⭐ The record's `kind` stays `quiz`, so every rule of a quiz holds for a mock exam
unchanged: one keyed option per question, a sentence per option, a passage per question,
`generated` and `advisory`, graded with no compiler, no container, no network and no model.
⛔ `mock` adds a score and a way to read it; it takes nothing away.

## ⛔ What the record refuses, and what a gate answers

The record refuses what is wrong in ONE value: a pass mark that is not a whole percent from
1 to 100, a domain with no title, two domains with one id, a question's `domain` on a quiz
that declares no `mock`. ⚠️ It does **not** refuse a question whose domain is not declared or
a domain no question uses, because those are facts about the SET and the gate `P1` states
them for every question at once, as `Q4` does for keys (`gates.quiz.mock`).

## ⭐ The pass mark is a number the corpus declares

⚠️ The quiz rule has no pass mark (every question right); a mock exam's has one, and it is
the corpus's, never the framework's: the real exam's own scale is a fact about that exam.
The page says only that the score reached it or did not.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.describe import describe, describe_keys
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.quiz.grading import grade
from studyforge.exercise.quiz.questions import (
    QUIZ_ID,
    QUIZ_ID_PERMITTED,
    Question,
)

#: The key a quiz record carries to say it is a mock exam.
MOCK = "mock"

#: The mock's own keys, and a domain's, in the order they are written (R10).
MOCK_KEYS = ("pass_mark", "domains")
DOMAIN_KEYS = ("id", "title")

#: The lowest and highest pass mark, as a whole percent of the questions.
LOWEST_PASS_MARK, HIGHEST_PASS_MARK = 1, 100


@dataclass(frozen=True, slots=True)
class Domain:
    """One area of the exam a score is reported for: a token and the words naming it."""

    id: str
    title: str


@dataclass(frozen=True, slots=True)
class Mock:
    """What makes a quiz a mock exam: the pass mark and the domains it is scored under.

    ⛔ Frozen, not validated: `mock_of` guarantees the pass mark is a percent and the
    domains are distinct tokens, and it guarantees nothing about the questions.
    """

    pass_mark: int
    domains: tuple[Domain, ...]


@dataclass(frozen=True, slots=True)
class Score:
    """One domain's reading, or the whole exam's when `domain` is `None`."""

    domain: str | None
    asked: int
    right: int

    @property
    def percent(self) -> int:
        """The whole percent right, rounded down: 2 of 3 is 66, never a 67 that reads as a pass."""
        return 0 if self.asked == 0 else (self.right * 100) // self.asked


def mock_of(value: object, where: str) -> Mock:
    """Read the `mock` key of a quiz record, refusing every way it can be wrong."""
    if not isinstance(value, dict) or set(value) != set(MOCK_KEYS):
        raise ExerciseError(
            f"{where}: 'mock' is {list(MOCK_KEYS)}, both required and nothing else. The "
            f"value is {describe(value)}."
        )
    return Mock(
        pass_mark=_pass_mark(value["pass_mark"], where),
        domains=_domains(value["domains"], where),
    )


def mock_document(mock: Mock) -> dict:
    """Return the key as the decoded object, in `MOCK_KEYS` order (R10)."""
    return {
        "pass_mark": mock.pass_mark,
        "domains": [{"id": domain.id, "title": domain.title} for domain in mock.domains],
    }


def scores(
    questions: tuple[Question, ...], mock: Mock, answers: object
) -> tuple[Score, tuple[Score, ...]]:
    """Return the whole exam's score and one per declared domain, from the reader's answers.

    ⭐ The rule the page implements, built on `grading.grade` so a question is right here
    exactly when it is right there. ⛔ Total, like `grade`: an answer nothing recognises is
    not a right one, and a question whose domain is not declared counts toward the whole
    exam and toward no domain (the gate `P1` is what refuses such a quiz).
    """
    rows = grade(questions, answers).answered
    whole = Score(None, len(rows), sum(1 for row in rows if row.correct))
    per_domain = tuple(
        Score(
            domain.id,
            sum(1 for row in rows if row.question.domain == domain.id),
            sum(1 for row in rows if row.question.domain == domain.id and row.correct),
        )
        for domain in mock.domains
    )
    return whole, per_domain


def passed(whole: Score, mock: Mock) -> bool:
    """Did the whole exam reach the declared pass mark? ⛔ An exam that asked nothing did not."""
    return whole.asked > 0 and whole.percent >= mock.pass_mark


def _pass_mark(value: object, where: str) -> int:
    """Refuse anything but a whole percent from 1 to 100 — a bool is not a number here."""
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not LOWEST_PASS_MARK <= value <= HIGHEST_PASS_MARK
    ):
        raise ExerciseError(
            f"{where}: a mock exam's 'pass_mark' is a whole percent from {LOWEST_PASS_MARK} to "
            f"{HIGHEST_PASS_MARK}. The value is {describe(value)}."
        )
    return value


def _domains(value: object, where: str) -> tuple[Domain, ...]:
    """Read the domains: at least one, each a token and a title, the ids distinct."""
    if isinstance(value, str) or not isinstance(value, (list, tuple)) or not value:
        raise ExerciseError(
            f"{where}: a mock exam's 'domains' is a non-empty array of {list(DOMAIN_KEYS)} "
            f"objects. A score with no domain to report it under is a quiz. The value is "
            f"{describe(value)}."
        )
    domains = tuple(_domain(entry, where) for entry in value)
    repeated = len(domains) - len({domain.id for domain in domains})
    if repeated:
        raise ExerciseError(
            f"{where}: a mock exam names {repeated} domain id more than once. A question "
            f"names its domain by id, so a repeated id is one score standing for two. The ids "
            f"are not reproduced here, since a refusal never quotes a value that may be "
            f"personal."
        )
    return domains


def _domain(value: object, where: str) -> Domain:
    """Read one domain, refusing a key it does not define — a typo is one."""
    if not isinstance(value, dict) or set(value) != set(DOMAIN_KEYS):
        carried = value if isinstance(value, dict) else {}
        unknown = [key for key in carried if key not in DOMAIN_KEYS]
        raise ExerciseError(
            f"{where}: a domain is {list(DOMAIN_KEYS)}, both required and nothing else"
            + (f"; this one carries {describe_keys(unknown)}" if unknown else "")
            + f". The value is {describe(value)}."
        )
    identifier, title = value["id"], value["title"]
    if not isinstance(identifier, str) or not QUIZ_ID.match(identifier):
        raise ExerciseError(
            f"{where}: a domain's 'id' must be {QUIZ_ID_PERMITTED}. The value is not "
            f"reproduced here, since a refusal never quotes a value that may be personal."
        )
    if not isinstance(title, str) or not title.strip():
        raise ExerciseError(
            f"{where}: a domain's 'title' is the words a score is reported under, and it "
            f"must be text. The value is {describe(title)}."
        )
    return Domain(identifier, title)
