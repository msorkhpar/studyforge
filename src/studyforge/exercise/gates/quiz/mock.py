"""The `mock` family — `P1` — and what it asks of a mock exam that `Q1`–`Q5` do not.

**What it does.** Declares one gate, `P1`, and registers it, so a gate record that names
the `mock` family is complete only when it carries `P1` as well as `Q1`–`Q5`. `P1` holds
when every question names a domain, every domain a question names is one the exam declares,
and every declared domain has at least one question.

**How you use it.**

    from studyforge.exercise.gates.quiz.mock import check_mock

    verdicts = (*check_quiz(exercise, judgements, origins, ledger, where),
                check_mock(exercise, where))

**Depends on.** `family` for how a verdict is spelt, `gates.families` for the registry,
`gates.record` for `Verdict`, `checks.require_quiz` for what a quiz is, and
`studyforge.exercise.quiz` for the questions and the `mock` key.

## ⛔ `Q1`–`Q5` ARE NOT RE-DECLARED, AND NOTHING THEY SAY IS WEAKENED

⭐ **A mock exam is a quiz**, so `check_quiz` answers `Q1`–`Q5` over every one of its
questions unchanged: `Q4` and `Q5` are mechanical and name the question that fails; `Q1`–`Q3`
are taken per question at authoring and recorded per question. ⛔ This family declares a
gate of its own rather than a second claim on one of theirs, because a gate id belongs to
exactly one family and a second claim on one is how a gate is weakened.

## ⭐ `P1` ANSWERS FOR EVERY QUESTION AND EVERY DOMAIN AT ONCE

The record refuses what is wrong in one value (`quiz.mock`); `P1` states what is wrong with
the SET, in one verdict, so an author fixing three questions is told about three. ⛔ A
question is named by its stem, never by its id, as `Q4` names one.
⚠️ **`P1` is mechanical**: it reads only the exercise, so whoever holds the bundle can re-run it.
"""

from __future__ import annotations

import re

from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.gates.families import Family, register
from studyforge.exercise.gates.quiz.checks import require_quiz
from studyforge.exercise.gates.quiz.family import QUIZ
from studyforge.exercise.gates.record import Verdict
from studyforge.exercise.quiz import SCENARIO_SENTENCES
from studyforge.exercise.record import Exercise

#: The one gate a mock exam clears beyond a quiz's five.
P1 = "P1"

#: ⭐ Registered at import: a record naming this family is complete only with `P1`.
MOCK = register(Family("mock", (P1,)))


def check_mock(exercise: Exercise, where: str) -> Verdict:
    """Answer `P1` over one mock exam — ⛔ refusing an exercise that is not one."""
    questions = require_quiz(exercise, where)
    mock = exercise.mock
    if mock is None:
        raise ExerciseError(
            f"{where}: the mock gate reads a quiz that declares a 'mock' and this one "
            f"declares none. A quiz is gated by {list(QUIZ.gates)} alone."
        )
    declared = {domain.id for domain in mock.domains}
    findings: list[str] = []
    for question in questions:
        named = f"the question {question.stem!r}"
        if question.domain is None:
            findings.append(f"{named} names no domain, so no score can be reported for it")
        elif question.domain not in declared:
            findings.append(
                f"{named} names a domain this exam does not declare, so its score "
                f"is reported under nothing"
            )
    findings += _scenario_findings(mock, questions)
    findings += _difficulty_findings(mock, questions)
    used = {question.domain for question in questions}
    for domain in mock.domains:
        if domain.id not in used:
            findings.append(
                f"the domain {domain.title!r} has no question, so a score reported "
                f"for it would be 0 of 0"
            )
    if findings:
        return Verdict(
            id=P1,
            family=MOCK.name,
            held=False,
            says=f"{len(findings)} finding(s) in this mock exam's domains: " + "; ".join(findings),
        )
    return Verdict(
        id=P1,
        family=MOCK.name,
        held=True,
        says=f"each of the {len(questions)} questions names one of the "
        f"{len(declared)} declared domains, and every domain has a question",
    )


def _sentences(text: str) -> int:
    """How many sentences a text holds: its stops (full stop, question or exclamation mark)."""
    return len(re.findall(r"[.!?](?=\s|$)", text.strip()))


def _scenario_findings(mock, questions) -> list[str]:
    """Return what is wrong with the scenarios: one undeclared, one unused, a context too long."""
    declared = {one.id for one in mock.scenarios}
    findings: list[str] = []
    for question in questions:
        if question.scenario is not None and question.scenario not in declared:
            findings.append(
                f"the question {question.stem!r} names a scenario this exam does not declare, "
                f"so the page has no card to show with it"
            )
    asked = {question.scenario for question in questions}
    low, high = SCENARIO_SENTENCES
    for scenario in mock.scenarios:
        if scenario.id not in asked:
            findings.append(
                f"the scenario {scenario.title!r} has no question, so a card would be shown "
                f"with nothing to answer"
            )
        count = _sentences(scenario.context)
        if not low <= count <= high:
            findings.append(
                f"the scenario {scenario.title!r} sets its context in {count} sentence(s) and a "
                f"scenario card is {low} to {high}"
            )
    return findings


def _difficulty_findings(mock, questions) -> list[str]:
    """Return what is wrong with the difficulty labels: one nobody declared, one nobody carries."""
    declared = {one.id for one in mock.difficulties}
    findings = [
        f"the question {question.stem!r} names a difficulty this exam does not declare"
        for question in questions
        if question.difficulty is not None and question.difficulty not in declared
    ]
    findings += [
        f"the difficulty {one.title!r} labels no question, so its score would be 0 of 0"
        for one in mock.difficulties
        if all(question.difficulty != one.id for question in questions)
    ]
    return findings
