"""A real prose page, a real quiz written from it, and every plant as a real edit to one of them.

⛔ **`AX-06`'s Acceptance is *`Q4` and `Q5` refuse their planted defects
mechanically*, and a plant is not a plant until its effect is OBSERVED.** ⭐ So
nothing here is a value typed into a verdict: every reading a gate is given
comes out of a page whose bytes exist, a quiz built from that page, and a
ledger digested from those same bytes — and each plant is a real edit to one of
the three.

## ⛔ THE THREE `Q4` PLANTS ARE REAL AT TWO HEIGHTS, AND BOTH ARE READ

⚠️ **`quiz.questions_of` already refuses two keyed options, a duplicate option
and an option with no sentence** — so a planted *document* never reaches a
gate. ⭐ **That is not `Q4` being redundant; it is `Q4` reading the other
height.** `Question` and `Option` are frozen and **not validated** (their own
contract says so), and an authoring pass builds them before any document
exists. ⛔ So each plant is applied to the built questions, where `Q4` is the
only thing standing between it and a bundle — and the same plant is put to
`questions_of` in the same test, so the plant is proved a real defect rather
than merely a shape this module made up.

## ⚠️ THE PAGE IS PROSE, DELIBERATELY

⭐ **A quiz is the practice for material that admits no coding task** (spec §7
§7), so the page here is a page, the ledger is a mapping of one path to one
digest, and nothing in this module runs, compiles or fetches anything.
⛔ The framework knows nothing about it (R1): it is material in the test tree
and the gates read it as data.

⛔ Mirrors no source module (R12 is one-way): it is material, not a test.
"""

from __future__ import annotations

import dataclasses

from studyforge.exercise import Exercise, of, origin_in
from studyforge.exercise.gates import digest_of_bytes
from studyforge.exercise.gates.quiz import (
    Q1,
    Q2,
    Q3,
    WHOLE_QUESTION,
    Judgement,
    question_digest,
)
from studyforge.exercise.quiz import Option, Question

WHERE = "corpus/message-shapes/unit-01/practice-1"

#: The page the quiz is written from, and where the ledger files it.
PAGE_PATH = "lessons/what-a-header-carries.md"
PAGE_SECTION = "What a message header carries"

#: ⭐ Real bytes, because the ledger's digest is taken over them and `Q5`'s
#: whole claim is that those bytes have not moved.
PAGE = b"""# What a message header carries

A header is read before anything else in the message. It states how long the
body is, which version wrote it, and nothing at all about what the body means.

A reader that trusts the length and ignores the version still parses a message
an older writer sent, and parses it wrongly.
"""

#: ⛔ The plants, each named by what it BREAKS and never by the gate it is
#: expected to break: a plant named after its gate is a plant nobody checked
#: the effect of. ⭐ `AX-03`'s rule, kept.
NONE = "no plant"
TWO_KEYS = "a second option is keyed correct"
DUPLICATE_OPTION = "two options say the same thing after normalisation"
SILENT_OPTION = "an option carries no sentence for the reader who picks it"
TOO_FEW_OPTIONS = "a question offers one option and nothing to rule out"
DRIFTED_PAGE = "the page has changed in the source since the quiz was written from it"
RE_AUTHORED_QUESTION = "the question has been rewritten since its judgements were taken"


def questions_document() -> list[dict]:
    """The quiz's two questions, as the practice document writes them."""
    return [
        {
            "id": "q-1",
            "stem": "What does a message header state about the body?",
            "options": [
                {
                    "id": "a",
                    "text": "How long it is, and nothing about what it means",
                    "correct": True,
                    "says": "The page says the header states the body's length and "
                    "nothing at all about what the body means.",
                },
                {
                    "id": "b",
                    "text": "What the body means, field by field",
                    "correct": False,
                    "says": "The page says the header states nothing about what the body means.",
                },
                {
                    "id": "c",
                    "text": "Which reader is allowed to open it",
                    "correct": False,
                    "says": "The page never says who may open a message.",
                },
            ],
            "origin": {"path": PAGE_PATH, "section": PAGE_SECTION},
        },
        {
            "id": "q-2",
            "stem": "What happens to a reader that ignores the version?",
            "options": [
                {
                    "id": "a",
                    "text": "It refuses the message",
                    "correct": False,
                    "says": "The page says such a reader still parses the message "
                    "rather than refusing it.",
                },
                {
                    "id": "b",
                    "text": "It parses an older writer's message wrongly",
                    "correct": True,
                    "says": "The page says exactly this: it still parses, and parses wrongly.",
                },
            ],
            "origin": {"path": PAGE_PATH, "section": PAGE_SECTION},
        },
    ]


def practice_document() -> dict:
    """The whole practice document a build would write for this quiz."""
    return {
        "kind": "practice",
        "exercise": {"kind": "quiz", "questions": questions_document()},
    }


def exercise() -> Exercise:
    """The quiz as the framework reads it back — ⭐ through `of`, never hand-built."""
    read = of(practice_document(), WHERE)
    assert read is not None, "the practice document carries no exercise"
    return read


def built(documents: list[dict]) -> tuple[Question, ...]:
    """Build the questions the way an AUTHORING PASS does: dataclasses, nothing validated.

    ⛔ **This is the height `Q4` guards.** `questions_of` is the document
    reader; an authoring pass has no document yet, so what it hands a gate
    suite is exactly this — frozen values whose own contract says they are not
    validated.

    ⚠️ **`origin` is read through `cases.origin_in` and never subscripted**:
    `W109` holds that key to one reader across `src/` and `tests/`, and a
    second site reading it is what that instrument exists to refuse.
    """
    return tuple(
        Question(
            id=entry["id"],
            stem=entry["stem"],
            options=tuple(
                Option(
                    id=option["id"],
                    text=option["text"],
                    correct=option["correct"],
                    says=option["says"],
                )
                for option in entry["options"]
            ),
            origin=origin_in(entry, WHERE),
        )
        for entry in documents
    )


def planted(plant: str) -> list[dict]:
    """The question documents with one real edit applied — ⛔ the edit, never a flag."""
    documents = questions_document()
    if plant == NONE:
        return documents
    if plant == TWO_KEYS:
        documents[0]["options"][1]["correct"] = True
        return documents
    if plant == DUPLICATE_OPTION:
        documents[0]["options"][2]["text"] = "  HOW LONG IT IS, and nothing about what it means "
        return documents
    if plant == SILENT_OPTION:
        documents[0]["options"][1]["says"] = "   "
        return documents
    if plant == TOO_FEW_OPTIONS:
        documents[1]["options"] = documents[1]["options"][1:]
        return documents
    if plant == RE_AUTHORED_QUESTION:
        documents[0]["stem"] = "What does a message header say about the body it precedes?"
        return documents
    raise AssertionError(f"no such plant: {plant}")


def page(plant: str) -> bytes:
    """The page's bytes, with `DRIFTED_PAGE` a real edit to them."""
    if plant == DRIFTED_PAGE:
        return PAGE.replace(b"parses it wrongly", b"parses it correctly")
    return PAGE


def ledger(plant: str = NONE) -> dict[str, str]:
    """What the source ledger says this page digests to NOW (`AX-07`'s one question)."""
    return {PAGE_PATH: digest_of_bytes(page(plant))}


def judgements(questions: tuple[Question, ...]) -> tuple[Judgement, ...]:
    """Every `Q1`–`Q3` judgement this quiz owes, each taken over the question in hand.

    ⚠️ **`Q3` is one per WRONG OPTION**, for the reason `G3` is one per edge
    case: a judgement covering every distractor at once would let the one
    nobody can rule out ride along with the obvious ones.
    """
    taken: list[Judgement] = []
    for question in questions:
        over = question_digest(question)
        taken.append(
            Judgement(
                gate=Q1,
                question=question.id,
                option=WHOLE_QUESTION,
                prompt="given this page and this question alone, which option is keyed?",
                taken_by="an independent pass over the page, read twice",
                outcome="picked the keyed option on both readings",
                held=True,
                over=over,
            )
        )
        taken.append(
            Judgement(
                gate=Q2,
                question=question.id,
                option=WHOLE_QUESTION,
                prompt="given this question and its options but NOT the page, which is keyed?",
                taken_by="the same pass, with the page withheld",
                outcome="did not pick the keyed option",
                held=True,
                over=over,
            )
        )
        taken += [
            Judgement(
                gate=Q3,
                question=question.id,
                option=option.id,
                prompt="which passage of the page rules this option out?",
                taken_by="an independent pass over the page",
                outcome="named the passage that refutes it",
                held=True,
                over=over,
            )
            for option in question.options
            if not option.correct
        ]
    return tuple(taken)


def quiz_with(questions: tuple[Question, ...]) -> Exercise:
    """The read exercise carrying these questions instead of its own.

    ⚠️ **`dataclasses.replace` is the hand-built path, and it is used on
    purpose**: it is how an authoring pass reaches a gate suite, and it is the
    reason `checks.require_quiz` re-checks what `of` already checked.
    """
    return dataclasses.replace(exercise(), questions=questions)
