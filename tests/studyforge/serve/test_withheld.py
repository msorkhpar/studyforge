"""Mirror of `src/studyforge/serve/withheld.py` (R12): what of a quiz the site never serves.

⭐ Every needle is read off `quizzing.QUESTIONS`, the record that reaches disk.
⛔ The readings over a real served instance, in every form of the verb, are
`tests/studyforge/cli/test_serve_keyless.py`'s; these are the module's own rules.
"""

from __future__ import annotations

import html
import json

import pytest

from studyforge.serve.withheld import (
    MIN_WORDS,
    carries,
    redacted,
    refused_by,
    sentences_in,
    sentences_of,
)
from tests.studyforge.serve.routes.quizzing import QUESTIONS, sentences


def unit_document(workspace: dict | None) -> dict:
    """A unit document carrying one lesson and one practice with `workspace`."""
    return {
        "sections": [
            {"key": "prose", "kind": "lesson", "workspace": None},
            {"key": "practice-prose", "kind": "practice", "workspace": workspace},
        ]
    }


QUIZ = {"kind": "quiz", "questions": QUESTIONS}
CODE = {"main_path": "greet.py", "run_command": ["python3", "greet.py"], "correct": "kept"}


def test_redacted_cuts_every_option_to_its_id_and_its_words_and_changes_nothing_else() -> None:
    document = unit_document(QUIZ)
    before = json.dumps(document, sort_keys=True)
    answered = redacted(document)
    assert json.dumps(document, sort_keys=True) == before, "the caller's document was changed"
    questions = answered["sections"][1]["workspace"]["questions"]
    assert [q["stem"] for q in questions] == [q["stem"] for q in QUESTIONS]
    for asked, cut in zip(QUESTIONS, questions, strict=True):
        assert cut["options"] == [{"id": o["id"], "text": o["text"]} for o in asked["options"]]


def test_a_code_practice_document_is_answered_unchanged() -> None:
    """⭐ Spec §7 §8: a workspace with no questions is not a quiz, whatever it holds."""
    document = unit_document(CODE)
    assert redacted(document) == document
    assert sentences_in(document) == frozenset()


def test_sentences_in_reads_every_sentence_of_every_quiz_even_an_invalid_one() -> None:
    assert sentences_in(unit_document(QUIZ)) == frozenset(sentences())
    broken = {"questions": [{"options": [{"says": "Read although the record is not valid."}]}]}
    assert sentences_in(unit_document(broken)) == {"Read although the record is not valid."}
    assert sentences_in({"sections": "not a list"}) == frozenset()


@pytest.mark.parametrize(
    "text",
    [
        '{"options": [{"id": "a", "correct": true}]}',
        '{"correct":false}',
        '<li data-practice-correct="true">a</li>',
    ],
)
def test_the_key_is_carried_by_its_structure_with_no_sentence_known(text: str) -> None:
    assert carries(text.encode(), ())


@pytest.mark.parametrize(
    "text",
    [
        'section[data-practice-quiz] li[data-practice-verdict="correct"] { color: green }',
        "The correct answer is found on the page.",
        '{"right": 1, "complete": false}',
    ],
)
def test_the_word_correct_alone_is_not_the_key(text: str) -> None:
    assert not carries(text.encode(), ())


@pytest.mark.parametrize("spell", [str, lambda s: json.dumps(s), html.escape])
def test_a_sentence_is_found_in_every_spelling_it_can_be_served_in(spell) -> None:
    for sentence in sentences():
        assert carries(f"prefix {spell(sentence)} suffix".encode(), sentences()), sentence


def test_a_hard_wrapped_sentence_is_still_found() -> None:
    sentence = sentences()[1]
    words = sentence.split()
    wrapped = " ".join(words[:3]) + "\n   " + " ".join(words[3:])
    assert carries(wrapped.encode(), [sentence])


def test_a_sentence_shorter_than_the_floor_is_not_searched_for() -> None:
    short = " ".join(["Right"] * (MIN_WORDS - 1)) + "."
    assert not carries(f"<p>{short}</p>".encode(), [short])
    long = " ".join(["Right"] * MIN_WORDS) + "."
    assert carries(f"<p>{long}</p>".encode(), [long])


class Source:
    """A content source whose sentences a test changes between two asks."""

    def __init__(self) -> None:
        self.found: frozenset[str] = frozenset()

    def withheld(self) -> frozenset[str]:
        return self.found


def test_refused_by_asks_the_source_on_every_file_and_never_captures_it() -> None:
    source = Source()
    refused = refused_by(source)
    body = f"<p>{sentences()[0]}</p>".encode()
    assert not refused(body)
    source.found = frozenset(sentences())
    assert refused(body)


def test_a_source_that_cannot_say_withholds_the_key_structure_only() -> None:
    assert sentences_of(object()) == frozenset()
    assert refused_by(object())(b'{"correct": true}')
