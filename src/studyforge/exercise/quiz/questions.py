"""What a quiz asks: a stem, its options, the one that is keyed, and why each is what it is.

**What it does.** Reads and writes the `questions` a quiz record carries in
place of a workspace, and refuses every way a question can be wrong — no key,
two keys, two options that say the same thing, an option with no sentence.

**How you use it.** `questions_of(value, where)` returns the questions in the
order they were written; `questions_document(questions)` is the round trip.

**Depends on.** `exercise.errors` for the one exception this package raises,
**`exercise.cases.origin_in` for what a passage of the source is**, and
`studyforge.describe` for naming a value without reproducing it (R7).

## ⛔ The key ships in the document, and nothing here pretends otherwise

⚠️ **A quiz is graded with no compiler, no container, no network and no model**
(spec §7 §7). The key and the per-option sentences are written into the
practice document, the grading rule is the framework's, and the reading is
therefore identical over `file://` and over a served origin (R8). ⛔ **An
offline page cannot hide the answer it is about to grade with**, exactly as an
offline workspace cannot hide its test file, and claiming to hide either is the
theatre R5 exists to prevent. ⭐ So `questions_document` writes `correct` for
every option, always, and there is no scrubbing pass and no flag that would
remove it. The honest design shows the reader the answer after they answer.

## ⛔ The key is PER OPTION, and that is what makes both refusals real

⚠️ A question-level `key` naming one option would make *"exactly one is keyed"*
true by construction — and then *"a question with two keyed options is
refused"* would be a clause no document could ever fail, which is a gate that
measures nothing. ⭐ **So each option says whether it is correct**, and **no
keyed option** and **two keyed options** are each a document this module
refuses, and the authoring gate Q4 refuses both again.

## ⛔ Every option carries its one sentence, right or wrong

⭐ **The reader is told why, for whichever option they chose** — not only for
the wrong ones and not only for the key. A distractor with no sentence is a
reader told "no" and nothing else, which teaches nothing; and the key with no
sentence is the same failure on the other side.

## ⛔ Identity is an ID, never a position

⚠️ **A reader's state outlives the document it was recorded against.** Two
options swapped by a re-authoring pass would silently turn a recorded answer
into a different answer if answers named a position — a wrong recorded state
rather than a lost one, which is the failure mode this project keeps
diagnosing. ⭐ So a question has an `id` and so does each of its options, both
distinct within their scope, and `grading` looks answers up by those.

## ⛔ Two options that say the same thing are refused

⚠️ **After normalisation**, because whitespace and case are not what
distinguishes an answer from a distractor: a question whose two options
normalise to one string has a reader choosing between the same answer twice,
and — if one of them is the key — a reader marked wrong for picking the right
words. ⭐ The normal form is stated in `normalised` and is deliberately narrow.

## ⛔ Every question names the passage it came from

⭐ **`origin` is per QUESTION and not only per record** (spec §7 §7: the
passage is recorded by address, never paraphrased into the question). Gate Q5
resolves each one against the source ledger, so a question with no origin is a
question nothing can check was built from the page it is attached to.

⚠️ **`origin`'s rule is imported, never re-spelled**: `cases.origin_in` hands
the value to `fields.optional_origin`, the tree's one reader of that key
(so one shape has one reading), and this module reads the key nowhere else.
"""

from __future__ import annotations

from dataclasses import dataclass

from studyforge.describe import describe, describe_keys
from studyforge.exercise.cases import Origin, origin_document, origin_in
from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.quiz.options import (
    KEYED_OPTIONS,
    MINIMUM_OPTIONS,
    OPTION_KEYS,
    QUIZ_ID,
    QUIZ_ID_PERMITTED,
    Option,
    normalised,
    options_of,
    read_id,
    read_text,
    require_distinct,
)
from studyforge.exercise.quiz.examkeys import (
    DIFFICULTY_KEY,
    EXTRA_KEYS,
    MINIMUM_SELECT,
    SCENARIO_KEY,
    SELECT_KEY,
    SHUFFLE_KEY,
    read_select,
    read_shuffle,
)

#: One question, in the order its keys are written (R10). ⛔ All four required
#: and nothing else, except the one optional key below.
QUESTION_KEYS = ("id", "stem", "options", "origin")

#: ⭐ The one optional key of a question: the domain a mock exam scores it under. It is
#: written only where a question carries one, so every question written before it
#: round-trips to the same bytes, and it is last so it never moves another key (R10).
DOMAIN_KEY = "domain"

#: ⭐ Every optional key a question of a mock exam may carry (`domain` and `examkeys.EXTRA_KEYS`).
MOCK_QUESTION_KEYS = (DOMAIN_KEY, *EXTRA_KEYS)

@dataclass(frozen=True, slots=True)
class Question:
    """One question: what is asked, what may be answered, and what passage it came from.

    ⛔ Frozen, not validated. `questions_of` guarantees exactly one option is
    keyed, so `key` cannot raise for a question this module returned.
    """

    id: str
    stem: str
    options: tuple[Option, ...]
    origin: Origin
    #: ⭐ The mock-exam domain this question is scored under, or `None` (every quiz that is
    #: not a mock exam). A token like an id; whether it names a declared domain is the
    #: mock family's gate and not this reader's.
    domain: str | None = None
    #: ⭐ The scenario of the mock exam this question is asked under, or `None`.
    scenario: str | None = None
    #: ⭐ How many options a multiple-response question asks the reader to choose, or `None` for
    #: a question with one key. `questions_of` guarantees that many options are keyed.
    select: int | None = None
    #: ⭐ `False` where the question opts out of having its options shuffled; `None` otherwise.
    shuffle: bool | None = None
    #: ⭐ The difficulty of the mock's `difficulties` this question is labelled with, or `None`.
    difficulty: str | None = None

    @property
    def key(self) -> Option:
        """The first option that is correct; the one, for a question with one key.

        ⭐ Guaranteed to exist by `questions_of`.
        """
        return next(option for option in self.options if option.correct)

    @property
    def keys(self) -> tuple[Option, ...]:
        """Every option that is correct: one, or `select` of them for a multiple-response one."""
        return tuple(option for option in self.options if option.correct)

    @property
    def needed(self) -> int:
        """How many options the reader must choose: `select`, or one."""
        return self.select or KEYED_OPTIONS

    def option(self, id: object) -> Option | None:
        """Return the option with this id, or `None` for anything not offered.

        ⚠️ **`None` rather than a refusal**, for `states.completes_practice`'s
        reason: this is asked on the completion path with whatever a reader's
        stored state holds, and a caller that had to catch an exception to
        learn "that is not one of the answers" is a caller that will eventually
        not catch it.
        """
        return next((option for option in self.options if option.id == id), None)


def questions_of(value: object, where: str) -> tuple[Question, ...]:
    """Read the `questions` a quiz asks, in the order they were written."""
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise ExerciseError(
            f"{where}: 'questions' must be an array of question objects, each "
            f"{list(QUESTION_KEYS)}. The value is {describe(value)}."
        )
    if not value:
        raise ExerciseError(
            f"{where}: 'questions' is empty. A quiz is its questions — a record "
            f"that asks nothing checks nothing, and a practice nothing can fail "
            f"is one every reader completes by opening it."
        )
    questions = tuple(_question(entry, where) for entry in value)
    require_distinct([question.id for question in questions], where, "question id")
    return questions


def questions_document(questions: tuple[Question, ...]) -> list[dict]:
    """Return the questions as decoded objects, each in `QUESTION_KEYS` order (R10).

    ⛔ **`correct` is written for every option, always.** The key is in the
    material and this module does not pretend otherwise — see the contract
    above, and `grading`, which needs nothing but what this writes.
    """
    return [_question_document(question) for question in questions]


def _question_document(question: Question) -> dict:
    """Return one question as the decoded object; `domain` only where it carries one."""
    written = {
        "id": question.id,
        "stem": question.stem,
        "options": [_option_document(option) for option in question.options],
        "origin": origin_document(question.origin),
    }
    if question.domain is not None:
        written[DOMAIN_KEY] = question.domain
    if question.scenario is not None:
        written[SCENARIO_KEY] = question.scenario
    if question.select is not None:
        written[SELECT_KEY] = question.select
    if question.shuffle is not None:
        written[SHUFFLE_KEY] = question.shuffle
    if question.difficulty is not None:
        written[DIFFICULTY_KEY] = question.difficulty
    return written


def _option_document(option: Option) -> dict:
    """Return one option as the decoded object, in `OPTION_KEYS` order (R10)."""
    return {
        "id": option.id,
        "text": option.text,
        "correct": option.correct,
        "says": option.says,
    }


def _question(value: object, where: str) -> Question:
    """Read one question, refusing a key the question does not define — a typo is one."""
    if not isinstance(value, dict):
        raise ExerciseError(
            f"{where}: a question is an object, {list(QUESTION_KEYS)}. "
            f"This one is {describe(value)}."
        )
    unknown = [key for key in value if key not in (*QUESTION_KEYS, *MOCK_QUESTION_KEYS)]
    missing = [key for key in QUESTION_KEYS if key not in value]
    if unknown or missing:
        raise ExerciseError(
            f"{where}: a question is {list(QUESTION_KEYS)}, all of them required "
            f"and nothing else but the optional {list(MOCK_QUESTION_KEYS)}. This one is missing "
            f"{missing} and carries {describe_keys(unknown)} the question does not define."
        )
    domain = (
        read_id(value[DOMAIN_KEY], "a question's domain", where) if DOMAIN_KEY in value else None
    )
    scenario = (
        read_id(value[SCENARIO_KEY], "a question's scenario", where)
        if SCENARIO_KEY in value
        else None
    )
    select = read_select(value[SELECT_KEY], where) if SELECT_KEY in value else None
    return Question(
        id=read_id(value["id"], "a question's", where),
        stem=read_text(value["stem"], "a question's 'stem' is what it asks", where),
        options=options_of(value["options"], where, select),
        origin=_origin(value, where),
        domain=domain,
        scenario=scenario,
        select=select,
        shuffle=read_shuffle(value[SHUFFLE_KEY], where) if SHUFFLE_KEY in value else None,
        difficulty=(
            read_id(value[DIFFICULTY_KEY], "a question's difficulty", where)
            if DIFFICULTY_KEY in value
            else None
        ),
    )


def _origin(value: dict, where: str) -> Origin:
    """Read the passage this question was written from — required, unlike a record's.

    ⛔ **A record's `origin` is optional and a question's is not** (gate Q5):
    the record says what the exercise was built from, and a quiz's questions
    are built one passage at a time, so a question with no passage is one
    nothing can check was written from the page it is attached to.
    """
    origin = origin_in(value, where)
    if origin is None:
        raise ExerciseError(
            f"{where}: a question names no 'origin'. Every question is written "
            f"from one passage of the page and records it by address, so that "
            f"the gate can resolve it against the source ledger."
        )
    return origin
