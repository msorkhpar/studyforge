"""A spaced-review bank: the section a quiz declaring `review` draws, and the files it links.

**What it does.** Renders a bank's questions as the quiz's own (stems, options), plus the schedule,
inside one section the shared review script turns into a session: it shows the questions that are
due, grades them from the key the page carries, and files each item's streak and last-right day in
the reader's own browser (`studyforge.review.v1`, behind a guard that tolerates a refused store).
No request, no server, no clock but the reader's.

**How you use it.** `page.practice.render` calls `render(...)` for a quiz whose record carries
`review`; `files()` is what a corpus with a bank writes beside the shared bundle.

**Depends on.** `exercise.quiz`, `render.page.quiz` (the key block's safe writer and the option
markup), `render.templates`, `render.markup`, `render.pageassets.source`.

## Absent means today, byte for byte

A quiz with no `review` key is rendered by `page.quiz` with its own template, unchanged. The two
files are written only for a corpus holding a bank.
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

STYLESHEET_NAME = "review.css"
SCRIPT_NAME = "review.js"
PARTS = (STYLESHEET_NAME, SCRIPT_NAME)

REVIEW_TEMPLATE = "practice-review.html"
QUESTION_TEMPLATE = "practice-review-question.html"


def render(
    exercise: Exercise,
    *,
    key: str,
    corpus: str,
    grader: str,
    assets: Callable[[str], str],
) -> str:
    """Return one review bank's section; `assets` turns a shared file's name into its link."""
    review = exercise.review
    questions = exercise.questions
    if review is None or not questions:
        return ""
    return templates.fill(
        REVIEW_TEMPLATE,
        key=escape_attribute(key),
        corpus=escape_attribute(corpus),
        steps=str(len(review.intervals_days)),
        total=str(len(questions)),
        grader=grader,
        questions="".join(_question(one, key) + quiz.JOIN for one in questions),
        answers=quiz.answers(questions),
        plan=_plan(exercise),
        stylesheet=escape_attribute(assets(STYLESHEET_NAME)),
        script=escape_attribute(assets(SCRIPT_NAME)),
    )


def files() -> dict[str, str]:
    """`filename -> content` of what a corpus with a review bank writes beside the bundle."""
    return {STYLESHEET_NAME: text(STYLESHEET_NAME), SCRIPT_NAME: text(SCRIPT_NAME)}


def _question(asked: Question, key: str) -> str:
    """One bank item: the quiz's own options, and the line its verdict lands in."""
    return templates.fill(
        QUESTION_TEMPLATE,
        id=escape_attribute(asked.id),
        stem=inline(asked.stem),
        options="".join(quiz.option(one, f"{key}:{asked.id}") + quiz.JOIN for one in asked.options),
    )


def _plan(exercise: Exercise) -> str:
    """Return the schedule, as the text of a data block no sentence can close."""
    written = json.dumps(
        {"intervals_days": list(exercise.review.intervals_days)},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return "".join(quiz.SCRIPT_SAFE.get(char, char) for char in written)
