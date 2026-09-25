"""Mirror of `src/studyforge/unit/prose.py` (R12): every run of words, walked as a copy."""

from __future__ import annotations

from studyforge.exercise.quiz import shape
from studyforge.exercise.quiz.questions import OPTION_KEYS, QUESTION_KEYS
from studyforge.unit.prose import OPTION_WORDS, OPTIONS, QUESTION_WORDS, QUESTIONS, quiz, walk


def shout(value: object) -> object:
    return value.upper() if isinstance(value, str) else value


def test_every_run_of_words_at_any_depth_is_walked_and_code_is_not():
    blocks = [
        {"type": "heading", "level": 2, "text": "a"},
        {"type": "code", "lang": "java", "text": "b"},
        {"type": "list", "ordered": False, "items": ["c", ["d", {"type": "para", "text": "e"}]]},
        {"type": "table", "headers": ["f"], "rows": [["g"]]},
        {
            "type": "disclosure",
            "summary": "h",
            "open": False,
            "blocks": [{"type": "para", "text": "i"}],
        },
    ]
    assert walk(blocks, shout) == [
        {"type": "heading", "level": 2, "text": "A"},
        {"type": "code", "lang": "java", "text": "b"},
        {"type": "list", "ordered": False, "items": ["C", ["D", {"type": "para", "text": "E"}]]},
        {"type": "table", "headers": ["F"], "rows": [["G"]]},
        {
            "type": "disclosure",
            "summary": "H",
            "open": False,
            "blocks": [{"type": "para", "text": "I"}],
        },
    ]
    assert blocks[0]["text"] == "a"


def test_a_quiz_s_words_are_walked_and_nothing_else_is():
    workspace = {
        "kind": "quiz",
        QUESTIONS: [
            {
                "id": "q",
                "stem": "stem",
                OPTIONS: [{"id": "a", "text": "text", "correct": True, "says": "says"}],
                "origin": {"path": "p", "section": "s"},
            }
        ],
    }
    assert quiz(workspace, shout) == {
        "kind": "quiz",
        QUESTIONS: [
            {
                "id": "q",
                "stem": "STEM",
                OPTIONS: [{"id": "a", "text": "TEXT", "correct": True, "says": "SAYS"}],
                "origin": {"path": "p", "section": "s"},
            }
        ],
    }
    # ⭐ A copy: the record handed in is unchanged.
    assert workspace[QUESTIONS][0]["stem"] == "stem"


def test_a_workspace_that_is_not_a_quiz_comes_back_as_it_came():
    for workspace in (None, {"kind": "code", "tests": []}, {QUESTIONS: "none"}):
        assert quiz(workspace, shout) is workspace


def test_the_quiz_s_keys_are_the_record_s_own():
    # ⛔ Spelled here, held to `exercise.quiz.questions`, which writes the record.
    assert set(QUESTION_WORDS) | {OPTIONS} <= set(QUESTION_KEYS)
    assert set(OPTION_WORDS) <= set(OPTION_KEYS)
    assert shape.QUESTIONS == QUESTIONS
