r"""The part of a learner's README that says what the course is and what it gives.

**What it does.** Writes, as lines of Markdown, the three sections a visitor reads
before any command: what the course holds (its counts), what a learner gets (each
feature, with its screenshot where the export has one), and the comparison of the
two ways to use it, the read-only preview and the full course run with Docker.

**How you use it.** `sections(title, facts, shots, ...)` returns the lines; `learner`
puts them between the introduction and the first command.

**Depends on.** `facts.Facts` for the numbers. ⛔ It names no account, no host and
no path, and it states only what the pages do today: a feature a course does not
have (no quizzes, no code examples, no narration) is not described.

## ⭐ A number that was not read is not printed

⛔ Every count arrives as `None` when it could not be read, and a sentence that needs
one is left out whole, so the README never shows a guess.
"""

from __future__ import annotations

from collections.abc import Mapping

from studyforge.skills.execution.standalone.facts import Facts

#: The README section every note in the preview points to, and its heading.
RUN_HEADING = "Run it locally with Docker"
RUN_ANCHOR = "run-it-locally-with-docker"

#: The screenshots the export accepts, in the order the README shows them: the role, then its
#: alternative text. ⭐ The file for a role is `<role>.png` or `<role>.webp`.
ROLES = (
    ("index", "The course index, with the reading progress, the next unit and a filter"),
    ("lesson", "A lesson page, with the course contents and the outline beside the text"),
    (
        "practice",
        "A practice open in its workspace: the statement on the left, the editor on the right",
    ),
    ("quiz", "A quiz answered in the page, with the explanation of the chosen answer"),
    ("example", "A code example opened in the editor in place, beside the lesson"),
    ("narration", "A lesson with the narration player at the foot of the page"),
)


def plural(count: int, word: str, many: str | None = None) -> str:
    """`1 unit`, `2 units`; `many` names an irregular plural."""
    return f"{count} {word if count == 1 else many or word + 's'}"


def _shot(shots: Mapping[str, str], role: str) -> list[str]:
    if role not in shots:
        return []
    alt = dict(ROLES)[role]
    return ["", f"![{alt}]({shots[role]})"]


def join_and(words: list[str]) -> str:
    """Join with commas and a last `and`: `a`, `a and b`, `a, b and c`."""
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


def holds(facts: Facts) -> list[str]:
    """Return the sentences of the course's size, each left out where its number is unknown."""
    lines: list[str] = []
    if facts.modules and facts.units:
        size = f"It has {plural(facts.modules, 'module')} and {plural(facts.units, 'unit')}"
        if facts.areas:
            size = (
                f"It has {plural(facts.units, 'unit')} in {plural(facts.modules, 'module')}, "
                f"grouped in {plural(len(facts.areas), 'topic area')}: "
                f"{join_and(list(facts.areas))}"
            )
        lines += [size + ".", ""]
    elif facts.units:
        lines += [f"It has {plural(facts.units, 'unit')}.", ""]
    if facts.practices:
        counts = [f"It holds {plural(facts.practices, 'practice')}"]
        if facts.coded and facts.quizzes:
            counts = [
                f"It holds {plural(facts.practices, 'practice')}: {facts.coded} to write in code, "
                "graded by a real runner, and "
                f"{plural(facts.quizzes, 'short quiz', 'short quizzes')}, graded in the page"
            ]
        lines += [counts[0] + ".", ""]
    return lines


def features(facts: Facts, shots: Mapping[str, str], *, narrated: bool) -> list[str]:
    """Return what a learner gets, one paragraph each, its screenshot beside its feature."""
    lines = [
        "## What you get",
        "",
        "**Lessons.** Each unit is a page of text and code, with the course contents, an "
        "outline of the page and links to the previous and next unit. The index shows "
        "what you have read and what comes next, and filters the contents as you type.",
        *_shot(shots, "index"),
        *_shot(shots, "lesson"),
        "",
    ]
    if facts.coded:
        lines += [
            "**Practices graded by a real runner.** A code practice gives you a statement, "
            "starting code and tests. You write your answer in an editor, and **Submit** "
            "runs the practice's tests in a runner that has no network. The report says "
            "whether the main ask is done and how many edge cases pass, and a practice "
            "counts as passed when its tests pass.",
            "",
            "**The practice workspace.** Opening a practice fills the window: the "
            "statement on the left, the editor on the right, and a report bar below. "
            "Drag the dividers to resize the panes. A worked solution is one click away "
            "when you are stuck. **Run** tries your code, **Submit** runs the tests.",
            *_shot(shots, "practice"),
            "",
        ]
    if facts.quizzes:
        lines += [
            "**Quizzes graded in the page.** A short quiz has a few questions with one "
            "answer each. Choose, press **Check answers**, and each choice is explained "
            "right or wrong. Nothing is sent anywhere: the page grades it.",
            *_shot(shots, "quiz"),
            "",
        ]
    if facts.examples:
        lines += [
            "**Code examples that open in an editor.** A lesson's example expands in "
            "place into the editor, with its source and its test beside the text and a "
            "button that runs the test. The editor shows a copy, so the course's own "
            "files stay as they are.",
            *_shot(shots, "example"),
            "",
        ]
    lines += [
        "**Reading marks and progress.** Mark a unit as read and the index counts it. "
        "Your marks and quiz passes are kept in your browser; your practice results are "
        "kept on your machine, in a Docker volume.",
        "",
    ]
    if narrated:
        lines += [
            "**Optional narration.** Lessons can be read aloud, the passage being read "
            "highlighted, with play and pause, previous and next passage, and speed. "
            "Practices and code are not narrated. See [Narration](#narration-optional).",
            *_shot(shots, "narration"),
            "",
        ]
    return lines


def ways(facts: Facts, *, narrated: bool) -> list[str]:
    """Return the comparison of the two ways to use the course."""
    rows = [
        (
            "Set-up",
            "None: open the website link at the top of this repository",
            f"Docker, and one command: [{RUN_HEADING}](#{RUN_ANCHOR})",
        ),
        ("Lessons, the index and its filter", "Yes", "Yes"),
        ("Reading marks and progress", "Yes, kept in your browser", "Yes, kept in your browser"),
    ]
    if facts.quizzes:
        rows.append(("Quizzes, graded in the page", "Yes", "Yes"))
    if facts.coded:
        rows += [
            ("Run and Submit, graded by the runner", "No", "Yes"),
            ("The editor beside the statement", "No", "Yes"),
        ]
    if facts.examples:
        rows.append(
            ("Code examples opened in the editor", "No: the files open in the source viewer", "Yes")
        )
    if narrated:
        rows.append(("Narration", "No", "Optional"))
    rows.append(("Works offline", "No", "Yes"))
    return [
        "## Two ways to use it",
        "",
        "The **read-only preview** is a copy of the lessons on a website: you read, answer "
        "the quizzes and keep your reading marks, and everything that needs a server on "
        "your machine says so and points here. The **full course** runs on your machine "
        "with Docker.",
        "",
        "| | Read-only preview | Full course, with Docker |",
        "|---|---|---|",
        *(f"| {a} | {b} | {c} |" for a, b, c in rows),
        "",
    ]


def sections(facts: Facts, shots: Mapping[str, str], *, title: str, narrated: bool) -> list[str]:
    """Return the three sections, in reading order."""
    return [
        "## The course",
        "",
        f"{title} is a self-study course: you read its lessons in a browser and work "
        "its practices in an editor, on your own machine. A read-only preview of the "
        "lessons is online: see the website link at the top of this repository.",
        "",
        *holds(facts),
        *features(facts, shots, narrated=narrated),
        *ways(facts, narrated=narrated),
    ]
