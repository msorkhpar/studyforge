"""Mirror of `src/studyforge/exercise/gates/quiz/giveaway.py` (R12): `Q2` is read off the rule.

**What it asserts.** A page-free reading holds when its reader said *none* or
picked a wrong option, and does not hold when it picked the key. ⛔ A reading
that picked no option the question offers, or that gives no reason, is
refused. ⭐ The judgement it writes is taken under `Q2_PROMPT` and carries the
reader's cue, which a refused `Q2` verdict quotes.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates.quiz import (
    PICKED_NONE,
    Q2,
    Q2_PROMPT,
    judged_gate,
    page_free,
    question_digest,
    require_judgements,
)
from tests.studyforge.exercise.gates.quiz import material
from tests.studyforge.exercise.gates.quiz.material import WHERE

#: The cue a reader names when the wording betrays the key.
CUE = "the keyed option is the longest and restates the stem"


def questions():
    """The unplanted quiz of `material`: two questions, each with its key."""
    return material.built(material.planted(material.NONE))


def key_of(question) -> str:
    return next(option.id for option in question.options if option.correct)


def wrong_of(question) -> str:
    return next(option.id for option in question.options if not option.correct)


def readings(picks):
    """One `Q2` reading per question, picking what `picks` names for it."""
    return tuple(
        page_free(question, pick(question), CUE, "an independent reader")
        for question, pick in zip(questions(), picks, strict=True)
    )


def test_none_or_a_wrong_option_holds_and_the_key_does_not():
    asked = questions()
    for picks, held in (
        ((lambda q: PICKED_NONE, lambda q: PICKED_NONE), True),
        ((wrong_of, lambda q: PICKED_NONE), True),
        ((key_of, lambda q: PICKED_NONE), False),
    ):
        taken = readings(picks)
        print([(entry.question, entry.held, entry.outcome) for entry in taken])
        read = judged_gate(Q2, asked, require_judgements(taken, WHERE))
        print(read.held, read.says)
        assert read.held is held, read.says


def test_a_giveaway_is_refused_and_its_verdict_quotes_the_reader_s_cue():
    asked = questions()
    taken = readings((key_of, lambda q: PICKED_NONE))
    # ⭐ The plant, OBSERVED: the first reading really picked the key.
    assert "picked 'a'; the key is 'a'" in taken[0].outcome and taken[0].held is False
    read = judged_gate(Q2, asked, taken)
    print(read.says)
    assert read.held is False
    assert CUE in read.says


def test_the_judgement_is_taken_under_the_rule_s_prompt_over_the_question():
    (first, _) = asked = questions()
    (entry, _) = readings((lambda q: PICKED_NONE, lambda q: PICKED_NONE))
    assert (entry.gate, entry.prompt, entry.because) == (Q2, Q2_PROMPT, CUE)
    assert entry.over == question_digest(first) and entry.question == asked[0].id
    assert "picked none" in entry.outcome


@pytest.mark.parametrize("picked", ["z", "", "A"])
def test_a_pick_the_question_does_not_offer_is_refused(picked):
    with pytest.raises(ExerciseError, match="none of its"):
        page_free(questions()[0], picked, CUE, "an independent reader")


@pytest.mark.parametrize("because", ["", "   ", None])
def test_a_reading_that_gives_no_reason_is_refused(because):
    with pytest.raises(ExerciseError, match="gives no reason"):
        page_free(questions()[0], PICKED_NONE, because, "an independent reader")


@pytest.mark.parametrize("word", ["none", "None", " NONE "])
def test_the_reader_s_word_none_is_read_as_picking_none(word):
    # ⭐ Measured on a Java course: the word the prompt asks for is `PICKED_NONE`, not a refusal.
    question = questions()[0]
    entry = page_free(question, word, CUE, "an independent reader")
    print(entry.outcome)
    assert entry.held is True and "picked none" in entry.outcome


def test_an_option_whose_id_is_none_is_still_that_option():
    question = questions()[0]
    renamed = tuple(
        replace(option, id="none") if option.correct else option for option in question.options
    )
    entry = page_free(replace(question, options=renamed), "none", CUE, "an independent reader")
    assert entry.held is False and "picked 'none'" in entry.outcome
