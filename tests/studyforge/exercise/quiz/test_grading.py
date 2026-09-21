"""The grading rule: all-correct completes, one wrong does not, and nothing is fetched.

⛔ **`AX-05`'s Acceptance, on `depth1`'s own quiz.** The two readings that are
easy to fake are taken by OBSERVATION rather than by assertion: the "no
compiler, no container, no network, no model" clause is read with the
filesystem, the network and `subprocess` made unusable, and the closed import
set is read out of the package's own AST.
"""

from __future__ import annotations

import ast
import builtins
import io
import json
import os
import socket
import subprocess
from pathlib import Path

import pytest

from studyforge.exercise import GRADED, NONE, RUN, TEST, UNGRADED, completes_practice, of, state_of
from studyforge.exercise.quiz import NO_ANSWERS, completes, grade
from tests.studyforge.exercise.quiz.depth1 import on_disk, practice_document, question
from tests.support import repository_root

WHERE = "depth-one/unit-01/practice-1"

#: ⛔ What `exercise.quiz` may import, whole. A name outside it could reach a
#: file, a process, a socket or a clock — and the moment one does, grading is
#: no longer a function of the document a reader already holds.
PERMITTED_IMPORTS = {
    "__future__",
    "collections.abc",
    "dataclasses",
    "re",
    "unicodedata",
    "studyforge.describe",
    "studyforge.exercise.cases",
    "studyforge.exercise.errors",
    "studyforge.exercise.quiz.grading",
    "studyforge.exercise.quiz.questions",
    "studyforge.exercise.quiz.shape",
    "studyforge.unit.errors",
    "studyforge.unit.trust",
}


def asked():
    """`depth1`'s quiz, read back off the bytes a build would have written."""
    return of(on_disk(), WHERE).questions


def right(questions):
    """The answers a reader gives who has read the page: every key, by id."""
    return {question.id: question.key.id for question in questions}


class Unreachable(AssertionError):
    """Raised by anything grading is not allowed to touch."""


def close_every_way_out(monkeypatch):
    """The `file://` floor, ENFORCED: no file, no socket, no process, from here on.

    ⛔ Not a promise and not a reading of the imports — those are asserted
    separately. This is the observation: grading takes the same reading with
    every way out of the process closed.

    ⚠️ **Called AFTER the document is loaded**, never as a fixture: the
    questions come off a file like any corpus's, and closing the filesystem
    before reading them would refuse the setup rather than the reading.
    """

    def refuse(*_args, **_kwargs):
        raise Unreachable("grading reached outside the document it was given")

    # ⚠️ THREE names, and the third is why: `builtins.open` alone left
    # `Path.read_text` working, because `pathlib` reaches `io.open` through the
    # module and `os.open` below it. The control below is what found that.
    monkeypatch.setattr(builtins, "open", refuse)
    monkeypatch.setattr(io, "open", refuse)
    monkeypatch.setattr(os, "open", refuse)
    monkeypatch.setattr(socket, "socket", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(subprocess, "run", refuse)
    return refuse


# --------------------------------------------------------------------------
# ⭐ the Acceptance: all-correct completes, one wrong does not
# --------------------------------------------------------------------------


def test_every_question_answered_correctly_completes_the_quiz():
    questions = asked()
    verdict = grade(questions, right(questions))
    assert verdict.complete is True
    assert (verdict.right, verdict.asked) == (len(questions), len(questions))
    assert completes(questions, right(questions)) is True


def test_one_wrong_answer_does_not_complete_it():
    questions = asked()
    answers = right(questions)
    wrong = next(option for option in questions[0].options if not option.correct)
    answers[questions[0].id] = wrong.id
    verdict = grade(questions, answers)
    assert verdict.complete is False
    assert completes(questions, answers) is False
    assert verdict.answered[0].correct is False
    assert verdict.answered[0].says == wrong.says, "the reader is not told why"


def test_a_quiz_of_several_questions_needs_every_one_of_them():
    # ⛔ Not most of them: there is no pass mark, because a pass mark is a
    # number somebody chooses and a corpus then wants to configure.
    written = practice_document()
    written["exercise"]["questions"] = [question(), question(id="q-2")]
    questions = of(written, WHERE).questions
    answers = right(questions)
    answers.pop(questions[1].id)
    assert grade(questions, answers).right == 1
    assert completes(questions, answers) is False
    assert completes(questions, right(questions)) is True


def test_an_unanswered_question_completes_nothing_and_says_nothing():
    questions = asked()
    verdict = grade(questions, NO_ANSWERS)
    assert verdict.complete is False
    assert verdict.answered[0].answered is False
    assert verdict.answered[0].chosen is None
    assert verdict.answered[0].says == ""


# --------------------------------------------------------------------------
# ⛔ the reading is identical over `file://` and over a served origin
# --------------------------------------------------------------------------


def verdict_document(verdict):
    """The verdict as bytes, so two readings are compared as bytes and not as objects."""
    return json.dumps(
        [
            {
                "question": row.question.id,
                "chosen": None if row.chosen is None else row.chosen.id,
                "correct": row.correct,
                "says": row.says,
            }
            for row in verdict.answered
        ],
        ensure_ascii=False,
    )


def test_the_reading_is_byte_identical_with_every_way_out_of_the_process_closed(monkeypatch):
    # ⭐ The served reading is taken first, ordinarily. The `file://` one is
    # taken with `open`, `socket` and `subprocess` refusing — which is what an
    # offline page has — and the two are compared as BYTES.
    questions = asked()
    answers = right(questions)
    served = verdict_document(grade(questions, answers))
    close_every_way_out(monkeypatch)
    offline_reading = verdict_document(grade(questions, answers))
    assert offline_reading == served
    assert completes(questions, answers) is True


def test_the_offline_plant_is_not_a_no_op(monkeypatch):
    # ⛔ A PLANT IS NOT A PLANT UNTIL ITS EFFECT IS OBSERVED. If the three
    # patches above did nothing, the reading beside them would measure nothing
    # and read exactly like success.
    here = Path(__file__)
    close_every_way_out(monkeypatch)
    with pytest.raises(Unreachable):
        here.read_text(encoding="utf-8")
    with pytest.raises(Unreachable):
        builtins.open(here, encoding="utf-8")
    with pytest.raises(Unreachable):
        socket.socket()
    with pytest.raises(Unreachable):
        subprocess.run(["true"], check=False)


def test_the_package_imports_nothing_that_could_reach_out_of_the_process():
    # ⛔ The standing property behind the reading above: grading is a function
    # of its arguments, and a name outside this set is how that stops being
    # true without anybody noticing.
    root = repository_root() / "src/studyforge/exercise/quiz"
    modules = sorted(root.glob("*.py"))
    assert len(modules) >= 4, [path.name for path in modules]
    found = set()
    for path in modules:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                found.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                found.add(node.module)
    assert found <= PERMITTED_IMPORTS, sorted(found - PERMITTED_IMPORTS)


def test_the_permitted_set_is_not_wider_than_what_is_imported():
    # ⚠️ Ruling 48's other half: a permitted set carrying names nothing imports
    # is a set that would go on passing after the module that needed them left.
    root = repository_root() / "src/studyforge/exercise/quiz"
    text = "\n".join(path.read_text(encoding="utf-8") for path in sorted(root.glob("*.py")))
    assert all(name in text for name in PERMITTED_IMPORTS), "a permitted name nothing imports"


# --------------------------------------------------------------------------
# ⛔ a quiz produces no run, and no run verdict completes one
# --------------------------------------------------------------------------


@pytest.mark.parametrize("command", [RUN, TEST])
@pytest.mark.parametrize("passed", [True, False])
def test_no_run_verdict_completes_a_quiz(command, passed):
    # ⛔ Spec §7 §7, asserted over every combination rather than argued: a quiz
    # names no `test_path`, so the run-based rule reads it as ungraded and
    # answers `False` — which is the correct answer to the question it asks.
    document = on_disk()
    assert state_of(document) == UNGRADED
    assert completes_practice(state_of(document), command, passed=passed) is False


def test_the_run_rule_is_untouched_for_the_shapes_that_do_produce_runs():
    # ⭐ The negative control: `states` still answers what it always did, so
    # the reading above is about the quiz and not about a broken rule.
    assert state_of(None) == NONE
    assert completes_practice(GRADED, TEST, passed=True) is True
    assert completes_practice(GRADED, RUN, passed=True) is False


# --------------------------------------------------------------------------
# ⛔ nothing here raises, whatever the reader's state holds
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "answers",
    [None, "q-1", 7, [], {"q-1": "z"}, {"q-1": None}, {"q-9": "a"}, {7: 7}],
    ids=repr,
)
def test_anything_unrecognised_is_not_a_correct_answer_and_is_not_an_error(answers):
    # ⭐ `states.completes_practice`'s rule, applied here: a caller that had to
    # catch an exception to learn "no" is a caller that will eventually not
    # catch it and complete a practice on an error.
    questions = asked()
    verdict = grade(questions, answers)
    assert verdict.asked == len(questions)
    assert verdict.complete is False
    assert completes(questions, answers) is False


def test_the_verdict_has_one_row_per_question_and_never_one_per_answer():
    questions = asked()
    verdict = grade(questions, {**right(questions), "q-9": "a"})
    assert [row.question.id for row in verdict.answered] == [q.id for q in questions]
    assert verdict.complete is True
