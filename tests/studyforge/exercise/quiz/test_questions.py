"""What a question may say, and every way `AX-05`'s Acceptance says it may not.

⭐ **Taken on `depth1`'s own quiz** (`depth1.py`), so every refusal below is a
plant into the material this shape exists for rather than into a shape invented
for the test — ⛔ **and the negative control is the first test in the file: the
unplanted question is ACCEPTED**, which is what makes a refusal a reading of
the plant and not of the fixture.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError, Origin
from studyforge.exercise.quiz import (
    KEYED_OPTIONS,
    MINIMUM_OPTIONS,
    OPTION_KEYS,
    QUESTION_KEYS,
    Option,
    normalised,
    questions_document,
    questions_of,
)
from tests.studyforge.exercise.quiz.depth1 import PAGE, question, section

WHERE = "depth-one/unit-01/practice-1"


def refuse(*questions):
    """The sentence `questions_of` refuses these with, or a failure saying it did not."""
    with pytest.raises(ExerciseError) as raised:
        questions_of(list(questions), WHERE)
    return str(raised.value)


def options(*changes):
    """`depth1`'s question with each option replaced by the mapping beside it.

    ⚠️ A `None` change removes that option; a mapping is merged into it, and a
    key mapped to `None` is removed from the option.
    """
    asked = question()["options"]
    built = []
    padded = list(changes) + [{}] * (len(asked) - len(changes))
    for option, change in zip(asked, padded, strict=True):
        if change is None:
            continue
        merged = {**option, **change}
        built.append({key: value for key, value in merged.items() if value is not None})
    return question(options=built)


# --------------------------------------------------------------------------
# ⭐ the negative control, and the round trip
# --------------------------------------------------------------------------


def test_the_unplanted_question_is_accepted():
    # ⛔ Read FIRST. Every refusal below plants into this exact shape, so a
    # refusal that was really about the fixture would show up here as a green
    # gate over a test that measures nothing.
    asked = questions_of([question()], WHERE)
    assert len(asked) == 1
    assert asked[0].id == "q-1"
    assert asked[0].key.id == "a"
    assert asked[0].origin == Origin(PAGE, section())
    assert [option.id for option in asked[0].options] == ["a", "b", "c"]


def test_a_question_round_trips():
    written = [question()]
    assert questions_document(questions_of(written, WHERE)) == written


def test_the_key_and_every_sentence_are_written_back():
    # ⛔ The key is IN the material and nothing here pretends otherwise (R5's
    # theatre clause, spec §7 §7). Every option's `correct` and `says` survive
    # the round trip, including the key's own.
    written = questions_document(questions_of([question()], WHERE))
    assert [option["correct"] for option in written[0]["options"]] == [True, False, False]
    assert all(option["says"].strip() for option in written[0]["options"])


def test_the_keys_of_a_question_and_an_option_are_what_the_contract_names():
    written = questions_document(questions_of([question()], WHERE))
    assert tuple(written[0]) == QUESTION_KEYS
    assert tuple(written[0]["options"][0]) == OPTION_KEYS


# --------------------------------------------------------------------------
# ⛔ the Acceptance: the four refusals, each named
# --------------------------------------------------------------------------


def test_a_question_with_no_keyed_option_is_refused():
    message = refuse(options({"correct": False}))
    assert "0" in message and str(KEYED_OPTIONS) in message


def test_a_question_with_two_keyed_options_is_refused():
    message = refuse(options({}, {"correct": True}))
    assert "2" in message and str(KEYED_OPTIONS) in message


def test_options_identical_after_normalisation_are_refused():
    # ⚠️ Not identical as bytes: the plant differs by case and by spacing, and
    # those are typography rather than a second answer.
    twin = question()["options"][0]["text"].upper() + "  "
    message = refuse(options({}, {"text": twin}))
    assert "normalisation" in message
    assert twin not in message, "the option's text was reproduced in a refusal (R7)"


def test_an_option_with_no_sentence_is_refused():
    assert "says" in refuse(options({"says": None}))
    assert "text" in refuse(options({}, {"says": "   "}))


# --------------------------------------------------------------------------
# ⛔ and the refusals the shape needs beyond the Acceptance, each argued
# --------------------------------------------------------------------------


def test_normalisation_folds_case_and_spacing_and_nothing_else():
    assert normalised("  A Subject,\tand an Object ") == "a subject, and an object"
    # ⛔ Digits and punctuation are NOT folded: `1,000` and `1000` are two
    # answers, and a normal form that made them one would refuse a real
    # question as a duplicate.
    assert normalised("1,000") != normalised("1000")


def test_a_question_offering_one_option_is_refused():
    message = refuse(options({}, None, None))
    assert str(MINIMUM_OPTIONS) in message


def test_a_question_with_no_origin_is_refused():
    # ⛔ Gate Q5 resolves every question's passage against the source ledger,
    # so a question with none is one nothing can check was built from its page.
    assert "origin" in refuse(question(origin=None))


def test_a_repeated_question_id_is_refused():
    message = refuse(question(), question())
    assert "id" in message
    assert "q-1" not in message, "the ids were reproduced in a refusal (R7)"


def test_a_repeated_option_id_is_refused():
    message = refuse(options({}, {"id": "a"}))
    assert "id" in message


def test_an_option_correct_must_be_a_real_boolean():
    # ⛔ A truthy value would make the key depend on how a reader of the
    # document coerces it, and the key is what the practice is graded against.
    assert "true or false" in refuse(options({"correct": 1}))


@pytest.mark.parametrize("bad", ["q 1", "q/1", "-q1", "q-1\n", "", 7, None])
def test_an_id_outside_the_permitted_set_is_refused(bad):
    # ⚠️ `q-1\n` is `AX-00/1`'s shape: `^…$` with `.match` accepts a trailing
    # newline, and this pattern is anchored `\A…\Z` so that it does not.
    message = refuse(question(id=bad))
    assert "id" in message
    if isinstance(bad, str) and bad.strip():
        assert bad not in message, "the value was reproduced in a refusal (R7)"


def test_an_empty_question_list_is_refused():
    assert "empty" in refuse()


def test_a_question_carrying_an_unknown_key_is_refused():
    assert "hint" in refuse(question(hint="try the second paragraph"))


def test_an_option_carrying_an_unknown_key_is_refused():
    assert "weight" in refuse(options({"weight": 2}))


def test_a_question_missing_a_key_is_refused():
    assert "stem" in refuse(question(stem=None))


def test_the_option_dataclass_is_frozen_and_unvalidated():
    # ⭐ Stated rather than assumed: the refusals live in `questions_of`, and a
    # caller that builds an `Option` by hand has been guaranteed nothing.
    option = Option(id="a", text="x", correct=True, says="because")
    with pytest.raises(AttributeError):
        option.correct = False
