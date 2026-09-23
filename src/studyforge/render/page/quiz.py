r"""The quiz panel: the questions and what may be answered — and never which answer is right.

**What it does.** Renders the reader-facing surface of an exercise whose `kind`
is `quiz` — the stem, the options, the control that sends the reader's choices
to be graded, and the sentence saying a page opened as a file cannot have them
checked. ⛔ **No editor, no Run and no Submit, and not disabled ones either**: a
quiz has no file to open, no command to run and no grader to submit to, so every
one of those would be a dead control (`SF-24`'s standing rule, `W429`, `W431`).

**How you use it.** `quiz.render(exercise, key=…, corpus=…, grader=…)` returns
the section's markup; `page.practice.render` calls it for a quiz and emits its
own panel for everything else.

**Depends on.** `studyforge.exercise.quiz` for what a question IS — the record's
own `Question` and `Option`, never a second reading of the shape — plus
`render.templates` and `render.markup`. ⛔ **Not on `serve`**: a page that
needed a server to RENDER would fail the `file://` floor (R8). The page renders
there; it simply cannot have its answers checked there, and says so.

## ⛔ THE KEY IS NOT IN THE PAGE — THE USER'S RULING, 2026-09-23 (`W451`)

> *"the quiz itself again should not require an online or agent check for the
> answer user provided. It will be just a test with the correct answer residing
> on the server side. When user answers it will get validated and result will be
> returned to the user with explanation if needed"*

⛔ **An option is emitted as its id and its words, and NOTHING ELSE.** Until
`W451` each option carried `data-practice-correct` and its own sentence in
`data-practice-says`, and the page graded itself; ⚠️ that stance — *"an offline
page cannot hide the answer it grades with"* — is **superseded**, not argued
with: the page no longer grades. ⭐ The local study server does
(`serve.routes.quiz`), reading the key from the unit's own document on disk, and
answers each choice with the chosen option's sentence.
`tests/studyforge/render/page/test_quiz.py` reads every key and every sentence
out of the rendered bytes and requires none of them there.

⭐ **Over `file://` the questions and options still show** and a reader can
still choose; the Check control ships `hidden` and the `offline` sentence ships
showing — the mechanism the code panel's Run and Submit already use — and
`practice-quiz.js` swaps the two only where the served client says an origin can
answer.

## ⛔ R5's VOCABULARY IS NOT HERE EITHER

⚠️ `provenance` and `trust` are the framework's internal words and a reader is
never shown one (spec §7 §9). ⭐ The label this section carries arrives already
rendered, from `page.practice`'s one mapping over the record's own predicates —
so there is no second place a token of that vocabulary could reach the page.

## ⭐ The words a reader reads are the CORPUS's; the words about them are OURS

⛔ A stem and an option come out of the document and are escaped as text (R1).
⚠️ *Right.*, *Not this one.*, the counting sentence and the offline sentence are
this framework's own words about its own control, and they live in the
**templates** — the same two-sided spelling every hook on this page has, because
markup and script cannot import one another and the Python side is the single
source for what is emitted (`W431`).
"""

from __future__ import annotations

from studyforge.exercise import Exercise
from studyforge.exercise.quiz import Option, Question
from studyforge.render import templates
from studyforge.render.markup import escape, escape_attribute

#: The whole section: the questions, the control that grades them and the line
#: that says what it made of them — one element with attributes, so a file (R13).
QUIZ_TEMPLATE = "practice-quiz.html"

#: One question, and one answer it offers.
QUESTION_TEMPLATE = "practice-question.html"
OPTION_TEMPLATE = "practice-option.html"

#: What separates two rendered rows. ⚠️ The same shape `page.practice._region`
#: uses: a row is exactly its markup plus one newline, never a conditional
#: newline somewhere else (R10).
JOIN = "\n"


def render(exercise: Exercise, *, key: str, corpus: str, grader: str) -> str:
    """Return one quiz's section, or `''` for an exercise that is not one.

    ⛔ **`''` is the honest answer for a code exercise**, the same way
    `page.practice.render` answers `''` for a unit that sets no work: the two
    shapes share one surface and each renders the other as an absence rather
    than as controls a reader may not use.
    """
    if not exercise.is_quiz or not exercise.questions:
        return ""
    return templates.fill(
        QUIZ_TEMPLATE,
        key=escape_attribute(key),
        corpus=escape_attribute(corpus),
        grader=grader,
        questions=questions(exercise.questions, key),
    )


def questions(asked: tuple[Question, ...], key: str) -> str:
    """Return every question, in the order the corpus wrote them.

    ⛔ **The order is the record's and is never sorted here.** A quiz reads as a
    sequence built from one passage, and re-ordering it would be this framework
    editing the material (R1).
    """
    return "".join(question(one, key) + JOIN for one in asked)


def question(asked: Question, key: str) -> str:
    """Return one question: its stem, its options, and the empty line its answer lands in.

    ⭐ **The radio group's name joins the PRACTICE KEY to the question's id**, so
    two quizzes on one page — or one quiz rendered twice — cannot share a group
    and silently unselect each other. ⚠️ Nothing is composed out of thin air:
    both halves arrive already minted, and this module neither parses nor
    re-spells either.
    """
    return templates.fill(
        QUESTION_TEMPLATE,
        id=escape_attribute(asked.id),
        stem=escape(asked.stem),
        options="".join(option(one, f"{key}:{asked.id}") + JOIN for one in asked.options),
    )


def option(offered: Option, name: str) -> str:
    """Return one answer: its id and its words, and nothing that says whether it is right.

    ⛔ **`offered.correct` and `offered.says` are never read here** (`W451`): the
    first IS the key and the second tells a reader which option it is, so either
    one in the markup is the key in the page. ⭐ Both reach a reader only from
    the server's verdict, and only for the option they chose.
    """
    return templates.fill(
        OPTION_TEMPLATE,
        id=escape_attribute(offered.id),
        name=escape_attribute(name),
        text=escape(offered.text),
    )
