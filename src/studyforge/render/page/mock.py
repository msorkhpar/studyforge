r"""The mock exam panel: a quiz's questions with a progress line, a submit, and a score per domain.

**What it does.** Renders the reader-facing surface of a quiz whose record declares `mock`:
the questions (each tagged with its domain), the progress line, the controls, the empty result
the page's script fills, and the two links to the files that script and its look live in.
Returns those two files' text for the site build to write beside the shared bundle.

**How you use it.** `page.practice.render` calls `render(exercise, key=…, corpus=…, grader=…,
assets=…)` for a quiz that declares a mock exam and `quiz.render` for every other; the site build
calls `files()` only for a corpus that has a mock exam.

**Depends on.** `studyforge.exercise.quiz` for what a question and a mock exam ARE,
`render.page.quiz` for the option, the key block and the join, `render.templates`,
`render.markup` and `pageassets.source`. ⛔ **Not on `serve`**: nothing about a mock exam is a
server function.

## ⛔ Absent means today, byte for byte

⭐ A quiz with no `mock` is rendered by `render.page.quiz` exactly as it always was, and the
two files this part writes are written only for a corpus that has a mock exam, so a corpus
with none carries no byte of it. ⛔ The shared `page.css` and `page.js` never carry a rule or
a line of it: it sits in two files of its own, as `modes.css` and `modes.js` do.

## ⭐ The section is a quiz section, and its own script is the only one that acts on it

The section wears `data-practice-quiz`, so the workspace opens it, the card above it reads its
pass, and `practice-quiz.css` styles its questions. ⛔ It has no `practice` part named `key`,
`check` or `controls`, so the shared `practice-quiz.js` finds nothing to wire and does nothing to
it: `mock-exam.js` grades it, from the key block `data-mock-part="key"` that has the quiz key's
own shape.

## ⭐ The words a reader reads are the corpus's; the words about them are OURS

A stem, an option and a sentence go through the prose's inline renderer, as in `quiz`. The
progress, missing, result and no-script sentences are this framework's own words and live in the
**template**, where `mock-exam.js` reads them off the attributes.
"""

from __future__ import annotations

import json
from collections.abc import Callable

from studyforge.exercise import Exercise
from studyforge.exercise.quiz import Question
from studyforge.render import templates
from studyforge.render.markup import escape_attribute, inline
from studyforge.render.page import quiz
from studyforge.render.pageassets.source import text

#: What the two files are written as, beside `page.css` and `page.js`.
STYLESHEET_NAME = "mock-exam.css"
SCRIPT_NAME = "mock-exam.js"

#: The two files, as `pageassets` finds them on disk.
PARTS = (STYLESHEET_NAME, SCRIPT_NAME)

#: The section, and one question of it.
MOCK_TEMPLATE = "practice-mock.html"
QUESTION_TEMPLATE = "practice-mock-question.html"


def render(
    exercise: Exercise,
    *,
    key: str,
    corpus: str,
    grader: str,
    assets: Callable[[str], str],
) -> str:
    """Return one mock exam's section; `assets` turns a shared file's name into this page's link."""
    mock = exercise.mock
    questions = exercise.questions
    if mock is None or not questions:
        return ""
    return templates.fill(
        MOCK_TEMPLATE,
        key=escape_attribute(key),
        passmark=str(mock.pass_mark),
        corpus=escape_attribute(corpus),
        asked=str(len(questions)),
        grader=grader,
        questions="".join(_question(one, key) + quiz.JOIN for one in questions),
        answers=quiz.answers(questions),
        plan=_plan(exercise),
        stylesheet=escape_attribute(assets(STYLESHEET_NAME)),
        script=escape_attribute(assets(SCRIPT_NAME)),
    )


def files() -> dict[str, str]:
    """`filename -> content` of what a corpus with a mock exam writes beside the bundle."""
    return {STYLESHEET_NAME: text(STYLESHEET_NAME), SCRIPT_NAME: text(SCRIPT_NAME)}


def _question(asked: Question, key: str) -> str:
    """One question with its domain: the quiz's own options, and an attribute for the score."""
    return templates.fill(
        QUESTION_TEMPLATE,
        id=escape_attribute(asked.id),
        domain=escape_attribute(asked.domain or ""),
        stem=inline(asked.stem),
        options="".join(
            quiz.option(one, f"{key}:{asked.id}") + quiz.JOIN for one in asked.options
        ),
    )


def _plan(exercise: Exercise) -> str:
    """The pass mark and the domains, as the text of a data block no sentence can close."""
    mock = exercise.mock
    document = {
        "pass_mark": mock.pass_mark,
        "domains": [{"id": one.id, "title": one.title} for one in mock.domains],
    }
    written = json.dumps(document, ensure_ascii=False, separators=(",", ":"))
    return "".join(quiz.SCRIPT_SAFE.get(char, char) for char in written)
