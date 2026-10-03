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

import re
import unicodedata
from dataclasses import dataclass

from studyforge.describe import describe, describe_keys
from studyforge.exercise.cases import Origin, origin_document, origin_in
from studyforge.exercise.errors import ExerciseError

#: One question, in the order its keys are written (R10). ⛔ All four required
#: and nothing else, except the one optional key below.
QUESTION_KEYS = ("id", "stem", "options", "origin")

#: ⭐ The one optional key of a question: the domain a mock exam scores it under. It is
#: written only where a question carries one, so every question written before it
#: round-trips to the same bytes, and it is last so it never moves another key (R10).
DOMAIN_KEY = "domain"

#: ⭐ The three further optional keys a question of a mock exam may carry, written after
#: `domain` and only where present, so a question that carries none writes the bytes it always
#: wrote: the scenario it is asked under (`scenario`, an id of the mock's `scenarios`), how many
#: options the reader must choose when it keys more than one (`select`), and whether the page may
#: shuffle its options (`shuffle`, only ever `false`: the default is the page's to decide).
SCENARIO_KEY = "scenario"
SELECT_KEY = "select"
SHUFFLE_KEY = "shuffle"
DIFFICULTY_KEY = "difficulty"
MOCK_QUESTION_KEYS = (DOMAIN_KEY, SCENARIO_KEY, SELECT_KEY, SHUFFLE_KEY, DIFFICULTY_KEY)

#: ⭐ A multiple-response question keys at least this many options, and states the number.
MINIMUM_SELECT = 2

#: One option, in the order its keys are written (R10). ⛔ All four required
#: and nothing else: the key is a fact about the option, and so is the sentence
#: the reader is shown for choosing it.
OPTION_KEYS = ("id", "text", "correct", "says")

#: ⛔ Exactly one option is keyed. Stated as the number rather than as a
#: predicate so both refusals — none, and more than one — name the same rule.
KEYED_OPTIONS = 1

#: ⛔ The fewest options a question may offer. ⚠️ One option is not a question:
#: there is nothing to rule out, gate Q3 has no wrong option to refute, and the
#: reader cannot be wrong — which is a practice that completes itself.
MINIMUM_OPTIONS = 2

#: What a question's or an option's `id` may be. ⛔ A permitted set,
#: and NARROWER than `cases.CASE_ID` on purpose: a case id is compared byte for
#: byte with what somebody else's test report spells, while this one is ours —
#: an authoring skill writes it and the reader's own state is filed under it,
#: so it is a plain token with nothing in it that needs quoting anywhere.
#: ⚠️ Anchored `\A…\Z`, so a value ending in a newline is refused.
QUIZ_ID = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]*\Z")

#: Said in a refusal instead of the value (R7): the message tells an author
#: what to write, and the value itself is corpus data.
QUIZ_ID_PERMITTED = (
    "a plain token, starting with an ASCII letter or digit and carrying only "
    "ASCII letters, digits and '. _ -', with no whitespace"
)


@dataclass(frozen=True, slots=True)
class Option:
    """One answer a reader may choose: whether it is the key, and why it is what it is.

    ⛔ Frozen, not validated: `questions_of` is what guarantees the id is a
    token, `correct` is a real boolean and `says` is a sentence.
    """

    id: str
    text: str
    correct: bool
    says: str


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


def normalised(text: str) -> str:
    """Return the form two options are compared in before one is a duplicate.

    ⭐ **NFKC, case-folded, and whitespace collapsed** — three differences that
    are typography rather than meaning, and each of which a re-authoring pass
    can introduce without anybody intending a new answer.

    ⚠️ **Punctuation and digits are NOT normalised, deliberately.** `1,000` and
    `1000` are different answers, and a normal form that folded them would
    refuse a real question as a duplicate. ⛔ The narrow form is the safe one:
    it refuses what is certainly the same and never guesses.
    """
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


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
    _require_distinct(
        [question.id for question in questions],
        where,
        "'questions' names {count} id more than once. A reader's answer is "
        "filed under the question's id, so a repeated id is one answer "
        "standing for two questions. The ids are not reproduced here, since a refusal never "
        "quotes a value that may be personal.",
    )
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
    domain = _id(value[DOMAIN_KEY], "a question's domain", where) if DOMAIN_KEY in value else None
    scenario = (
        _id(value[SCENARIO_KEY], "a question's scenario", where) if SCENARIO_KEY in value else None
    )
    select = _select(value[SELECT_KEY], where) if SELECT_KEY in value else None
    return Question(
        id=_id(value["id"], "a question's", where),
        stem=_text(value["stem"], "a question's 'stem' is what it asks", where),
        options=_options(value["options"], where, select),
        origin=_origin(value, where),
        domain=domain,
        scenario=scenario,
        select=select,
        shuffle=_shuffle(value[SHUFFLE_KEY], where) if SHUFFLE_KEY in value else None,
        difficulty=(
            _id(value[DIFFICULTY_KEY], "a question's difficulty", where)
            if DIFFICULTY_KEY in value
            else None
        ),
    )


def _select(value: object, where: str) -> int:
    """Refuse a `select` that is not a whole number of at least two (a bool is not a number)."""
    if not isinstance(value, int) or isinstance(value, bool) or value < MINIMUM_SELECT:
        raise ExerciseError(
            f"{where}: a question's 'select' is how many options a reader chooses and it is "
            f"a whole number of at least {MINIMUM_SELECT}; a question with one key leaves it "
            f"out. The value is {describe(value)}."
        )
    return value


def _shuffle(value: object, where: str) -> bool:
    """Refuse anything but `false`: shuffling is the default and is not a key to restate."""
    if value is not False:
        raise ExerciseError(
            f"{where}: a question's 'shuffle' is only ever false, to keep its options in the "
            f"order they were written; a question that may be shuffled leaves it out. The "
            f"value is {describe(value)}."
        )
    return False


def _options(value: object, where: str, select: int | None = None) -> tuple[Option, ...]:
    """Read one question's options: ordered, distinct, and `select` of them keyed, or one."""
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise ExerciseError(
            f"{where}: a question's 'options' is an array of option objects, each "
            f"{list(OPTION_KEYS)}. The value is {describe(value)}."
        )
    if len(value) < MINIMUM_OPTIONS:
        raise ExerciseError(
            f"{where}: a question offers at least {MINIMUM_OPTIONS} options and "
            f"this one offers {len(value)}. A reader who cannot choose wrongly "
            f"has not been asked anything, and gate Q3 has no wrong option to "
            f"refute."
        )
    options = tuple(_option(entry, where) for entry in value)
    _require_distinct(
        [option.id for option in options],
        where,
        "a question names {count} option id more than once. A reader's answer "
        "names the option by its id, so a repeated id is an answer that means "
        "two things. The ids are not reproduced here, since a refusal never quotes a value that "
        "may be personal.",
    )
    _require_distinct(
        [normalised(option.text) for option in options],
        where,
        "a question offers {count} option that is identical to another after "
        "normalisation. Two options that say the same thing are one answer "
        "offered twice, and a reader who picks the wrong copy of the right "
        "words is marked wrong. The text is not reproduced here, since a refusal never quotes a "
        "value that may be personal.",
    )
    _require_the_key(options, where, select)
    return options


def _option(value: object, where: str) -> Option:
    """Read one option, refusing a key the option does not define — a typo is one."""
    if not isinstance(value, dict):
        raise ExerciseError(
            f"{where}: an option is an object, {list(OPTION_KEYS)}. This one is {describe(value)}."
        )
    if set(value) != set(OPTION_KEYS):
        unknown = [key for key in value if key not in OPTION_KEYS]
        missing = [key for key in OPTION_KEYS if key not in value]
        raise ExerciseError(
            f"{where}: an option is {list(OPTION_KEYS)}, all of them required and "
            f"nothing else. This one is missing {missing} and carries "
            f"{describe_keys(unknown)} the option does not define."
        )
    return Option(
        id=_id(value["id"], "an option's", where),
        text=_text(value["text"], "an option's 'text' is what the reader chooses", where),
        correct=_correct(value["correct"], where),
        says=_text(value["says"], "an option's 'says' is why it is right or wrong", where),
    )


def _correct(value: object, where: str) -> bool:
    """Refuse anything but a real boolean, because a truthy value is not a key."""
    if not isinstance(value, bool):
        raise ExerciseError(
            f"{where}: an option's 'correct' is true or false. A value that is "
            f"merely truthy would make the key depend on how a reader of this "
            f"document coerces it, and the key is what the practice is graded "
            f"against. The value is {describe(value)}."
        )
    return value


def _require_the_key(options: tuple[Option, ...], where: str, select: int | None = None) -> None:
    """⛔ Refuse a question with no key, and one with two (Acceptance, gate Q4).

    ⭐ A multiple-response question states how many it keys (`select`), and that many must be
    keyed, with at least one option left to rule out.
    """
    keyed = sum(1 for option in options if option.correct)
    if select is not None:
        if keyed != select or select >= len(options):
            raise ExerciseError(
                f"{where}: a question that asks the reader to choose {select} keys {keyed} of "
                f"its {len(options)} options correct. It keys exactly {select}, and leaves at "
                f"least one option to rule out."
            )
        return
    if keyed == KEYED_OPTIONS:
        return
    raise ExerciseError(
        f"{where}: a question keys {keyed} of its options correct and exactly "
        f"{KEYED_OPTIONS} is keyed. A question with none cannot be answered "
        f"correctly and so completes nothing; one with two grades two different "
        f"answers as right, and the reader is never told which the page taught."
    )


def _require_distinct(values: list[str], where: str, sentence: str) -> None:
    """⛔ Refuse a repeat, saying how many, never which (R7)."""
    repeated = len(values) - len(set(values))
    if repeated:
        raise ExerciseError(f"{where}: {sentence.format(count=repeated)}")


def _id(value: object, whose: str, where: str) -> str:
    """Refuse an id a reader's stored state could not be filed under."""
    if not isinstance(value, str) or not QUIZ_ID.match(value):
        raise ExerciseError(
            f"{where}: {whose} 'id' must be {QUIZ_ID_PERMITTED}. The value is not "
            f"reproduced here, since a refusal never quotes a value that may be personal."
        )
    return value


def _text(value: object, whose: str, where: str) -> str:
    """Refuse a blank where a reader is shown a sentence."""
    if not isinstance(value, str) or not value.strip():
        raise ExerciseError(
            f"{where}: {whose}, and it must be text. The value is {describe(value)}."
        )
    return value


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
