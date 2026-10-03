r"""The mock exam's exam form: timer, navigator, flags, scenarios, multiple response, sittings.

**What it does.** Renders the section of a mock exam that opts into any of them (`Mock.opts_in`,
or a question that asks the reader to choose more than one option). It carries every question of
the pool, each with its scenario card, its difficulty label and its inputs, the key block, the plan
block and the words, and the empty places the page's script fills: the start panel, the navigator,
the pager, the result and the review.

**How you use it.** `page.mock.render` calls `render(...)` for an opted-in mock and renders every
other mock as it always did. `wanted_for(exercise)` says which. `files()` is the four files an
opted-in corpus writes beside the bundle.

**Depends on.** `exercise.quiz`, `render.page.quiz` (the key block's safe writer),
`render.templates`, `render.markup`, `pageassets.source`.

## Absent means today, byte for byte

A mock with none of the opt-in keys is rendered by `page.mock` with its own templates and script,
unchanged. This part's four files are written only for a corpus holding an opted-in mock.

## Everything is graded in the page

No request, no server, no model. The key block lists, per question, the ids of every keyed option
and every option's sentence; the page grades from it, so the reading is the same over `file://`
and served. All state (answers, flags, start time, seed, drawn set, seen questions) lives in the
reader's own browser, behind a guard that tolerates a refused store.
"""

from __future__ import annotations

import json
from collections.abc import Callable

from studyforge.exercise import Exercise
from studyforge.exercise.quiz import Question
from studyforge.render import templates
from studyforge.render.markup import escape, escape_attribute, inline
from studyforge.render.page import quiz
from studyforge.render.pageassets.source import text

STYLESHEET_NAME = "mock-form.css"
SCRIPT_NAME = "mock-form.js"
#: The scripts, in the order the page runs them: the shared parts, the panels, then the exam.
CORE_NAME = "mock-form-core.js"
PANELS_NAME = "mock-form-panels.js"
PARTS = (STYLESHEET_NAME, CORE_NAME, PANELS_NAME, SCRIPT_NAME)

FORM_TEMPLATE = "practice-mockform.html"
QUESTION_TEMPLATE = "practice-mockform-question.html"
OPTION_TEMPLATE = "practice-mockform-option.html"

#: The words about the exam are this framework's own; the script reads them from this block.
WORDS = {
    "choose": "Choose a sitting",
    "begin": "Begin",
    "beginOnly": "Begin the exam",
    "questions": "{n} questions",
    "scenarios": "{n} scenarios",
    "allQuestions": "All {n} questions",
    "minutes": "{n} minutes",
    "noTime": "No time limit",
    "count": "{answered} of {asked} answered",
    "position": "Question {n} of {total}",
    "flag": "Flag for review",
    "flagged": "Flagged for review",
    "previous": "Previous",
    "next": "Next",
    "answered": "answered",
    "open": "not answered",
    "flaggedState": "flagged",
    "navQuestion": "Question {n}, {state}",
    "allDomains": "All domains",
    "domainFilter": "Domain",
    "flaggedOnly": "Flagged only",
    "choose_n": "Choose {n}.",
    "confirm": "Not answered yet: {list}. Choose Submit exam again to submit anyway.",
    "timeUp": "Time is up. The exam was submitted.",
    "minutesLeft": "{n} minutes remaining.",
    "oneMinuteLeft": "One minute remaining.",
    "reached": "You scored {right} of {asked} ({percent}%). The pass mark is {pass}%, "
    "and you reached it.",
    "short": "You scored {right} of {asked} ({percent}%). The pass mark is {pass}%, "
    "and you did not reach it.",
    "scaled": "Scaled score: {score} on a scale of {min} to {max}, where the scale's pass is "
    "{line}. This is a linear illustration of your score and not the exam's own scaling.",
    "scoreWords": "{right} of {asked} ({percent}%)",
    "right": "Right.",
    "wrong": "Not this one.",
    "unanswered": "Not answered.",
    "key": "Correct answer",
    "yours": "Your choice",
    "reviewAll": "All questions",
    "reviewMissed": "Missed only",
    "reviewFlagged": "Flagged only",
    "reviewNone": "No question matches this filter.",
    "unitSingular": "question",
    "domain": "Domain",
    "difficulty": "Difficulty",
}


def wanted_for(exercise: Exercise) -> bool:
    """Does this mock exam use the exam form? ⭐ Only when it opts in; else it is the page of old."""
    mock = exercise.mock
    if mock is None:
        return False
    return mock.opts_in or any(one.select is not None for one in exercise.questions or ())


def render(
    exercise: Exercise,
    *,
    key: str,
    corpus: str,
    grader: str,
    assets: Callable[[str], str],
) -> str:
    """Return one opted-in mock exam's section."""
    mock = exercise.mock
    questions = exercise.questions
    scenarios = {one.id: one for one in mock.scenarios}
    difficulties = {one.id: one.title for one in mock.difficulties}
    return templates.fill(
        FORM_TEMPLATE,
        key=escape_attribute(key),
        passmark=str(mock.pass_mark),
        layout=escape_attribute(mock.layout or "page"),
        corpus=escape_attribute(corpus),
        asked=str(len(questions)),
        grader=grader,
        questions="".join(
            _question(one, key, scenarios, difficulties) + quiz.JOIN for one in questions
        ),
        answers=_key_block(questions),
        plan=_safe(_plan(exercise)),
        words=_safe(WORDS),
        stylesheet=escape_attribute(assets(STYLESHEET_NAME)),
        core=escape_attribute(assets(CORE_NAME)),
        panels=escape_attribute(assets(PANELS_NAME)),
        script=escape_attribute(assets(SCRIPT_NAME)),
    )


def files() -> dict[str, str]:
    """`filename -> content` of what a corpus with an opted-in mock writes beside the bundle."""
    return {name: text(name) for name in PARTS}


def _question(asked: Question, key: str, scenarios: dict, difficulties: dict) -> str:
    attributes = f' data-mock-domain="{escape_attribute(asked.domain or "")}"'
    if asked.scenario:
        attributes += f' data-mock-scenario="{escape_attribute(asked.scenario)}"'
    if asked.select:
        attributes += f' data-mock-select="{asked.select}"'
    if asked.shuffle is False:
        attributes += ' data-mock-shuffle="false"'
    if asked.difficulty:
        attributes += f' data-mock-difficulty="{escape_attribute(asked.difficulty)}"'
    card = ""
    if asked.scenario:
        one = scenarios[asked.scenario]
        card = (
            f'<aside data-form-part="scenario" data-scenario="{escape_attribute(one.id)}" '
            f'aria-label="Scenario"><h3>{inline(one.title)}</h3><p>{inline(one.context)}</p>'
            f"</aside>\n"
        )
    meta = ""
    parts = []
    if asked.difficulty:
        parts.append(
            f'<span data-form-part="difficulty">{escape(difficulties[asked.difficulty])}</span>'
        )
    if asked.select:
        parts.append(f'<span data-form-part="choose">Choose {asked.select}.</span>')
    if parts:
        meta = f'<p data-form-part="meta">{" ".join(parts)}</p>\n'
    kind = "checkbox" if asked.select else "radio"
    return templates.fill(
        QUESTION_TEMPLATE,
        id=escape_attribute(asked.id),
        attributes=attributes,
        scenario=card,
        stem=inline(asked.stem),
        meta=meta,
        options="".join(
            templates.fill(
                OPTION_TEMPLATE,
                id=escape_attribute(one.id),
                type=kind,
                name=escape_attribute(f"{key}:{asked.id}"),
                text=inline(one.text),
            )
            + quiz.JOIN
            for one in asked.options
        ),
    )


def _safe(document: object) -> str:
    written = json.dumps(document, ensure_ascii=False, separators=(",", ":"))
    return "".join(quiz.SCRIPT_SAFE.get(char, char) for char in written)


def _key_block(questions: tuple[Question, ...]) -> str:
    return _safe(
        {
            one.id: {
                "keys": [option.id for option in one.options if option.correct],
                "says": {option.id: inline(option.says) for option in one.options},
            }
            for one in questions
        }
    )


def _plan(exercise: Exercise) -> dict:
    mock = exercise.mock
    plan: dict = {
        "pass_mark": mock.pass_mark,
        "domains": [
            {"id": one.id, "title": one.title, **({"weight": one.weight} if one.weight else {})}
            for one in mock.domains
        ],
        "layout": mock.layout or "page",
    }
    if mock.minutes is not None:
        plan["minutes"] = mock.minutes
    if mock.difficulties:
        plan["difficulties"] = [{"id": one.id, "title": one.title} for one in mock.difficulties]
    if mock.sittings:
        plan["sittings"] = [
            {
                "id": one.id,
                "title": one.title,
                **({"questions": one.questions} if one.questions else {}),
                **({"scenarios": one.scenarios} if one.scenarios else {}),
                **({"minutes": one.minutes} if one.minutes else {}),
            }
            for one in mock.sittings
        ]
    if mock.scale is not None:
        plan["scale"] = {"min": mock.scale.min, "max": mock.scale.max, "pass": mock.scale.pass_}
    return plan
