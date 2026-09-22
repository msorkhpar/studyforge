r"""The quiz panel: the questions, what may be answered, and why each answer is what it is.

**What it does.** Renders the reader-facing surface of an exercise whose `kind`
is `quiz` — the stem, the options, the sentence behind each one, and the control
that grades them. ⛔ **No editor, no Run and no Submit, and not disabled ones
either**: a quiz has no file to open, no command to run and no grader to submit
to, so every one of those would be a dead control (`SF-24`'s standing rule,
`W429`, `W431`).

**How you use it.** `quiz.render(exercise, key=…, corpus=…, grader=…)` returns
the section's markup; `page.practice.render` calls it for a quiz and emits its
own panel for everything else.

**Depends on.** `studyforge.exercise.quiz` for what a question IS — the record's
own `Question` and `Option`, never a second reading of the shape — plus
`render.templates` and `render.markup`. ⛔ **Not on `serve`**: a quiz is graded
with no compiler, no container, no network and no model, so this renders and
grades identically over `file://` and over a served origin (spec §7 §7, R8).

## ⛔ THE KEY IS IN THE PAGE, AND PRETENDING OTHERWISE IS THE THEATRE R5 REFUSES

⚠️ Every option carries `data-practice-correct` and its own sentence. ⛔ **That
is deliberate and it is not a leak**: the site is offline and `file://`-
addressable, so a page that graded without carrying its key could not grade at
all — exactly as an offline workspace cannot hide its test file. ⭐ Claiming to
hide either is the pretence R5 exists to prevent, and `exercise.quiz` says so
first.

## ⛔ R5's VOCABULARY IS NOT HERE EITHER

⚠️ `provenance` and `trust` are the framework's internal words and a reader is
never shown one (spec §7 §9). ⭐ The label this section carries arrives already
rendered, from `page.practice`'s one mapping over the record's own predicates —
so there is no second place a token of that vocabulary could reach the page.

## ⭐ The words a reader reads are the CORPUS's; the words about them are OURS

⛔ A stem, an option and its sentence come out of the document and are escaped
as text (R1). ⚠️ *Right.*, *Not this one.* and the counting sentence are this
framework's own words about its own control, and they live in the **templates**
— the same two-sided spelling every hook on this page has, because markup and
script cannot import one another and the Python side is the single source for
what is emitted (`W431`).
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

#: How a boolean is spelled in an attribute. ⛔ HTML's own words and not
#: Python's, because the script reads the string back.
SPELLED = {True: "true", False: "false"}


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
    """Return one answer: what it says, whether it is the key, and why it is what it is."""
    return templates.fill(
        OPTION_TEMPLATE,
        id=escape_attribute(offered.id),
        name=escape_attribute(name),
        correct=SPELLED[offered.correct],
        says=escape_attribute(offered.says),
        text=escape(offered.text),
    )
