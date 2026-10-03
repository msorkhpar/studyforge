"""One option, and the readers every part of a question is read with.

**What it does.** Reads one question's options (`options_of`), refuses every way they can be wrong
(none keyed, the wrong number keyed, two that say the same thing, an option with no sentence), and
holds the token and text readers `questions` reads an id and a stem with.

**How you use it.** `questions` calls these; `exercise.quiz` re-exports `Option` and `normalised`.

**Depends on.** `exercise.errors` and `studyforge.describe` (R7). A multiple-response question
keys as many options as it states in `select` (`examkeys`), and one with no `select` keys one.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from studyforge.describe import describe, describe_keys
from studyforge.exercise.errors import ExerciseError

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



def options_of(value: object, where: str, select: int | None = None) -> tuple[Option, ...]:
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
    require_distinct(
        [option.id for option in options],
        where,
        "a question names {count} option id more than once. A reader's answer "
        "names the option by its id, so a repeated id is an answer that means "
        "two things. The ids are not reproduced here, since a refusal never quotes a value that "
        "may be personal.",
    )
    require_distinct(
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
        id=read_id(value["id"], "an option's", where),
        text=read_text(value["text"], "an option's 'text' is what the reader chooses", where),
        correct=_correct(value["correct"], where),
        says=read_text(value["says"], "an option's 'says' is why it is right or wrong", where),
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


def require_distinct(values: list[str], where: str, sentence: str) -> None:
    """⛔ Refuse a repeat, saying how many, never which (R7)."""
    repeated = len(values) - len(set(values))
    if repeated:
        raise ExerciseError(f"{where}: {sentence.format(count=repeated)}")


def read_id(value: object, whose: str, where: str) -> str:
    """Refuse an id a reader's stored state could not be filed under."""
    if not isinstance(value, str) or not QUIZ_ID.match(value):
        raise ExerciseError(
            f"{where}: {whose} 'id' must be {QUIZ_ID_PERMITTED}. The value is not "
            f"reproduced here, since a refusal never quotes a value that may be personal."
        )
    return value


def read_text(value: object, whose: str, where: str) -> str:
    """Refuse a blank where a reader is shown a sentence."""
    if not isinstance(value, str) or not value.strip():
        raise ExerciseError(
            f"{where}: {whose}, and it must be text. The value is {describe(value)}."
        )
    return value
