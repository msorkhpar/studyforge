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
from studyforge.exercise.quiz.exam import (
    Difficulty,
    Scale,
    Scenario,
    Sitting,
    difficulties_of,
    layout_of,
    minutes_of,
    scale_of,
    scenarios_of,
    require_per_domain,
    sitting_document,
    sittings_of,
)
from studyforge.exercise.quiz.grading import grade
from studyforge.exercise.quiz.options import QUIZ_ID, QUIZ_ID_PERMITTED
from studyforge.exercise.quiz.questions import Question

#: The key a quiz record carries to say it is a mock exam.
MOCK = "mock"

#: The mock's own keys, and a domain's, in the order they are written (R10). ⭐ The first two
#: are required. The rest are optional and written only where present, so a mock written before
#: they existed round-trips to the same bytes: `minutes` (a timer), `layout` (`"exam"` for one
#: question to a view with a navigator), `scenarios`, `sittings` and `scale`.
MOCK_KEYS = (
    "pass_mark", "domains", "minutes", "layout", "scenarios", "difficulties", "sittings", "scale",
)
REQUIRED_MOCK_KEYS = ("pass_mark", "domains")
DOMAIN_KEYS = ("id", "title")
#: ⭐ A domain may also state its `weight`, a whole percent of an exam; when every domain does, a
#: sitting that draws questions draws them by these weights and the weights sum to 100.
OPTIONAL_DOMAIN_KEYS = ("weight",)

#: The lowest and highest pass mark, as a whole percent of the questions.
LOWEST_PASS_MARK, HIGHEST_PASS_MARK = 1, 100


@dataclass(frozen=True, slots=True)
class Domain:
    """One area of the exam a score is reported for: a token and the words naming it."""

    id: str
    title: str
    weight: int | None = None


@dataclass(frozen=True, slots=True)
class Mock:
    """What makes a quiz a mock exam: the pass mark and the domains it is scored under.

    ⛔ Frozen, not validated: `mock_of` guarantees the pass mark is a percent and the
    domains are distinct tokens, and it guarantees nothing about the questions.
    """

    pass_mark: int
    domains: tuple[Domain, ...]
    minutes: int | None = None
    layout: str | None = None
    scenarios: tuple[Scenario, ...] = ()
    sittings: tuple[Sitting, ...] = ()
    scale: Scale | None = None
    difficulties: tuple[Difficulty, ...] = ()

    @property
    def opts_in(self) -> bool:
        """Does this mock use anything the page of old does not do (a timer, a layout, ...)?"""
        extras = (self.minutes, self.layout, self.scenarios, self.sittings, self.scale)
        return any(one is not None and one != () for one in extras) or bool(
            self.difficulties or any(one.weight is not None for one in self.domains)
        )


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
    if (
        not isinstance(value, dict)
        or not set(REQUIRED_MOCK_KEYS) <= set(value)
        or not set(value) <= set(MOCK_KEYS)
    ):
        raise ExerciseError(
            f"{where}: 'mock' is {list(REQUIRED_MOCK_KEYS)}, both required, and may also carry "
            f"{list(MOCK_KEYS[2:])}, nothing else. The value is {describe(value)}."
        )
    return Mock(
        pass_mark=_pass_mark(value["pass_mark"], where),
        domains=_domains(value["domains"], where),
        minutes=(
            minutes_of(value["minutes"], where) if "minutes" in value else None
        ),
        layout=layout_of(value["layout"], where) if "layout" in value else None,
        scenarios=scenarios_of(value["scenarios"], where) if "scenarios" in value else (),
        sittings=sittings_of(value["sittings"], where) if "sittings" in value else (),
        scale=scale_of(value["scale"], where) if "scale" in value else None,
        difficulties=(
            difficulties_of(value["difficulties"], where) if "difficulties" in value else ()
        ),
    )


def mock_document(mock: Mock) -> dict:
    """Return the key as the decoded object, in `MOCK_KEYS` order (R10); optional keys if set."""
    written: dict = {
        "pass_mark": mock.pass_mark,
        "domains": [_domain_document(domain) for domain in mock.domains],
    }
    if mock.minutes is not None:
        written["minutes"] = mock.minutes
    if mock.layout is not None:
        written["layout"] = mock.layout
    if mock.scenarios:
        written["scenarios"] = [
            {"id": o.id, "title": o.title, "context": o.context} for o in mock.scenarios
        ]
    if mock.difficulties:
        written["difficulties"] = [{"id": d.id, "title": d.title} for d in mock.difficulties]
    if mock.sittings:
        written["sittings"] = [sitting_document(one) for one in mock.sittings]
    if mock.scale is not None:
        written["scale"] = {
            "min": mock.scale.min, "max": mock.scale.max, "pass": mock.scale.pass_,
        }
    return written


def _domain_document(domain: Domain) -> dict:
    written: dict = {"id": domain.id, "title": domain.title}
    if domain.weight is not None:
        written["weight"] = domain.weight
    return written


def quotas(mock: Mock, drawn: int, pool: tuple[Question, ...]) -> dict[str, int]:
    """How many of `drawn` questions each domain gets: by its weight, else by its share of the pool.

    ⭐ Largest remainder, ties to the earlier domain, so the numbers add up to `drawn`. The page
    draws by the same rule; this is the reference a test and the record's check read.
    """
    weights = {
        domain.id: (domain.weight if domain.weight is not None else
                    sum(1 for one in pool if one.domain == domain.id))
        for domain in mock.domains
    }
    total = sum(weights.values()) or 1
    base = {key: (drawn * weight) // total for key, weight in weights.items()}
    order = sorted(
        weights, key=lambda key: (-((drawn * weights[key]) % total), list(weights).index(key))
    )
    for key in order[: drawn - sum(base.values())]:
        base[key] += 1
    return base


def require_against_questions(mock: Mock, questions: tuple[Question, ...], where: str) -> None:
    """⛔ Refuse what the page could not draw: a question under a scenario nobody declared, a
    declared scenario with no question, and a sitting that asks for more than the exam holds.

    ⭐ The record is read whole here (`shape.mock_in`), so these are refused when a corpus
    validates and not only when an author's draft is gated; `P1` states the same facts again.
    """
    declared = {one.id for one in mock.scenarios}
    named = {one.scenario for one in questions if one.scenario is not None}
    if named - declared:
        raise ExerciseError(
            f"{where}: {len(named - declared)} scenario id a question names is not declared in "
            f"the mock's 'scenarios', so the page has no card to show with that question. The "
            f"ids are not reproduced here, since a refusal never quotes a value that may be "
            f"personal."
        )
    if declared - named:
        raise ExerciseError(
            f"{where}: {len(declared - named)} declared scenario has no question, so a card "
            f"would be shown with nothing to answer. Every scenario is asked about."
        )
    declared_difficulties = {one.id for one in mock.difficulties}
    used = {one.difficulty for one in questions if one.difficulty is not None}
    if used - declared_difficulties:
        raise ExerciseError(
            f"{where}: {len(used - declared_difficulties)} difficulty id a question names is not "
            f"declared in the mock's 'difficulties'. The ids are not reproduced here, since a "
            f"refusal never quotes a value that may be personal."
        )
    if mock.difficulties and declared_difficulties - used:
        raise ExerciseError(
            f"{where}: {len(declared_difficulties - used)} declared difficulty labels no "
            f"question, so a score reported for it would be 0 of 0."
        )
    for sitting in mock.sittings:
        require_per_domain(sitting, mock.domains, questions, where)
        if sitting.questions is not None:
            for domain, wanted in quotas(mock, sitting.questions, questions).items():
                held = sum(1 for one in questions if one.domain == domain)
                if wanted > held:
                    raise ExerciseError(
                        f"{where}: a sitting draws {sitting.questions} questions by domain "
                        f"weight, which asks {wanted} of one domain, and the pool holds {held} "
                        f"of it. The pool must hold enough of every domain for the largest "
                        f"sitting."
                    )
        if sitting.questions is not None and sitting.questions > len(questions):
            raise ExerciseError(
                f"{where}: a sitting draws {sitting.questions} questions and the exam asks "
                f"{len(questions)}."
            )
        if sitting.scenarios is not None and sitting.scenarios > len(declared):
            raise ExerciseError(
                f"{where}: a sitting draws {sitting.scenarios} scenarios and the exam declares "
                f"{len(declared)}."
            )


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


def scores_by_difficulty(
    questions: tuple[Question, ...], mock: Mock, answers: object
) -> tuple[Score, ...]:
    """One score per declared difficulty, in the order declared; empty where none is declared."""
    rows = grade(questions, answers).answered
    return tuple(
        Score(
            difficulty.id,
            sum(1 for row in rows if row.question.difficulty == difficulty.id),
            sum(
                1 for row in rows
                if row.question.difficulty == difficulty.id and row.correct
            ),
        )
        for difficulty in mock.difficulties
    )


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
    weighed = [one.weight for one in domains if one.weight is not None]
    if weighed and (len(weighed) != len(domains) or sum(weighed) != 100):
        raise ExerciseError(
            f"{where}: domain weights are stated for every domain or none, and they sum to 100."
        )
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
    allowed = (*DOMAIN_KEYS, *OPTIONAL_DOMAIN_KEYS)
    if not isinstance(value, dict) or not set(DOMAIN_KEYS) <= set(value) <= set(allowed):
        carried = value if isinstance(value, dict) else {}
        unknown = [key for key in carried if key not in allowed]
        raise ExerciseError(
            f"{where}: a domain is {list(DOMAIN_KEYS)}, both required, and may also carry "
            f"{list(OPTIONAL_DOMAIN_KEYS)}, nothing else"
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
    weight = value.get("weight")
    if "weight" in value and (
        not isinstance(weight, int) or isinstance(weight, bool) or not 1 <= weight <= 100
    ):
        raise ExerciseError(
            f"{where}: a domain's 'weight' is a whole percent from 1 to 100. The value is "
            f"{describe(weight)}."
        )
    return Domain(identifier, title, weight)
