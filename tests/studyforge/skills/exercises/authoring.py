"""A small corpus, a deterministic author, a judge and a runner — the loop's fixtures, once.

⭐ **The author is a stand-in and that is the point**: in
real use a model authors at ingestion, and here a SCRIPT does, so what is under
test is the loop, the budget and the reporting — never a model's taste.
⛔ **The runner is NOT a stand-in**: every gate reading comes out of a real
`pytest` process over real files, so a plant's effect is observed rather than
typed into a verdict (the gates' workspace makes the same choice).

⚠️ **Why a corpus of its own rather than `tests/fixtures/`.** Each page here
is a real page with the case its section says, and each carries the aspects an
author would read off it: the exercise that checks each one is named
in `ASPECTS`, so the plan is read, never typed. `depth1/`, the prose fixture,
carries no source material on disk, so no ledger can be taken over it.
⚠️ **The shared reading section** is the kind of prose that teaches no
checkable aspect of its own, so no aspect names it.

⛔ Nothing here asserts: a helper that asserted would be an instrument nobody
names.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

from studyforge.address import Address
from studyforge.exercise import CODE, EDGE, MAIN, QUIZ, Case, Origin
from studyforge.exercise.gates.quiz import Q1, Q2, Q3, WHOLE_QUESTION, Judgement, question_digest
from studyforge.exercise.quiz import Option, Question
from studyforge.skills.exercises import (
    CORE,
    Aspect,
    Brief,
    CodeDraft,
    Page,
    QuizDraft,
    Ran,
)
from tests.support import run

#: A written reason, as the stand-in author gives one.
BECAUSE = "carried by the reading floor; the page's exercise is built from its prose"

#: ⭐ The reading every page shares: prose that teaches no checkable aspect of its own.
NOTES = """## Reading notes

Practice is what turns a page you have read into a skill you can use. Read the
page once for its shape, then once more for its detail, and only then open the
exercise beside it. The exercise asks for one thing the page taught and names
the edges of that thing, one by one, so that a reader who handles the main ask
and forgets an edge is told exactly which edge was forgotten. That is the whole
reason an exercise names its cases: a verdict that only says pass or fail tells
a reader that something is wrong without saying where to look.

Every exercise on this site was written for it and proven before it shipped. A
worked solution exists for each one, and the tests were run against that
solution twice, against the empty starting file once, and against one planted
solution per edge case that solves the ask and ignores exactly that edge. A
test that passed on the starting file would be a test that checks nothing, and
a test that never failed on its planted solution would be an edge nobody
checks. Neither kind ships.

You may read the worked solution whenever you like. Reading it is not a
failure and nothing records it. The page is still the teacher; the exercise is
only the place where you find out whether the page has taught you. Take your
time with it, run it as often as you want, and come back to the page whenever
the exercise surprises you, because a surprise is usually the page saying
something you read past the first time. When every case passes, the practice
is complete, and the next page is waiting.
"""

GREETING_SOURCE = """def greet(who):
    return f"Hello, {who}"
"""

GREETING_TEST = """from greet import greet


def test_the_greeting_names_who_it_greets():
    assert greet("Ada") == "Hello, Ada"
"""

SHOUT_EXAMPLE = """def shout(text):
    return text.upper() + "!"
"""

PAGES = {
    "lessons/greeting.md": f"""# Greeting

A greeting names somebody. This page's function does, and its test says so.

## The function

```python
{GREETING_SOURCE}```

{NOTES}""",
    "lessons/shout.md": f"""# Shouting

## How to shout

To shout a word is to write it in capitals and end it with a mark.

```python
{SHOUT_EXAMPLE}```

{NOTES}""",
    "lessons/basket.md": f"""# A basket of prices

A basket is a list of prices, and its total is their sum. An empty basket
totals nothing, and a negative price is not a price at all and is refused.

{NOTES}""",
    "lessons/extra.md": f"""# An aside

```python
print("an example nobody builds an exercise from")
```

{NOTES}""",
    "notes/gauge.md": f"""# Field notes

## Taking a reading

Read the gauge at the same hour every day, and write the hour down beside the
number. A reading taken at a different hour cannot be compared with the rest.

## Writing it down

Copy the reading into the book on the same day. A reading nobody wrote down is
a reading nobody has.

{NOTES}""",
}

GRADERS = {"checks/test_greeting.py": GREETING_TEST}


def write_corpus(root: Path) -> tuple[list[str], list[str], list[Page]]:
    """Write the corpus under `root` and return its material, its graders and its pages."""
    for path, text in {**PAGES, **GRADERS}.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text, encoding="utf-8")
    return sorted(PAGES), sorted(GRADERS), list(pages())


def pages() -> tuple[Page, ...]:
    """One page per case: code with tests, code without, neither — and one quiz."""
    kata = Address(["kata"])
    return (
        page("lessons/greeting.md", kata, 1, graders=("checks/test_greeting.py",)),
        page("lessons/shout.md", kata, 2),
        page("lessons/basket.md", kata, 3),
        page("notes/gauge.md", Address(["notes"]), 1, kind=QUIZ, variant="prose"),
    )


#: ⭐ The aspects an author reads off each page, and the exercise that
#: checks each. ⚠️ The basket's two aspects are ONE exercise's, and so are the
#: gauge's two: coverage is counted by aspects, and one exercise may check many.
ASPECTS = {
    "lessons/greeting.md": (
        Aspect(
            "greets-by-name",
            "the greeting names who it greets",
            ("example:lessons/greeting.md:1", "tests:checks/test_greeting.py"),
            exercise="greet",
        ),
    ),
    "lessons/shout.md": (
        Aspect(
            "shouts",
            "a shouted word is in capitals and ends with a mark",
            ("example:lessons/shout.md:1",),
            exercise="shout",
        ),
    ),
    "lessons/basket.md": (
        Aspect(
            "totals",
            "a basket totals the sum of its prices",
            ("section:A basket of prices",),
            exercise="total",
        ),
        Aspect(
            "refuses-negative",
            "a negative price is refused",
            ("section:A basket of prices",),
            exercise="total",
        ),
    ),
    "notes/gauge.md": (
        Aspect("hour", "the gauge is read at one hour", ("section:Taking a reading",), "notes"),
        Aspect("book", "a reading is copied the same day", ("section:Writing it down",), "notes"),
    ),
}


def page(path, address, unit, *, kind=CODE, variant="python", graders=()) -> Page:
    """A page, with the aspects an author read off it."""
    return Page(
        path=path,
        address=address,
        variant=variant,
        unit=unit,
        kind=kind,
        aspects=ASPECTS[path],
        tier=CORE,
        graders=graders,
    )


def _code(brief: Brief, name: str, **parts) -> CodeDraft:
    """A code draft with commands spelled from the brief's own workspace."""
    ws = brief.places.workspace
    return CodeDraft(
        title=parts.pop("title"),
        lang="python",
        main_file=f"{name}.py",
        test_file=f"test_{name}.py",
        run_command=("python3", f"{ws}/{name}.py"),
        test_command=(
            "python3",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--junit-xml",
            f"{ws}/target/report.xml",
            f"{ws}/test_{name}.py",
        ),
        report="target/report.xml",
        starter=f"def {name}(*args):\n    raise NotImplementedError('write me')\n",
        **parts,
    )


BLANK = Case("test_a_blank_name_is_refused", EDGE, "a blank name is refused")
GREETS = Case("test_the_greeting_names_who_it_greets", MAIN, "the greeting names who it greets")
GREETING_REFERENCE = """def greet(who):
    if not who.strip():
        raise ValueError("a greeting names somebody")
    return f"Hello, {who}"
"""
GREETING_TESTS = (
    GREETING_TEST
    + """

def test_a_blank_name_is_refused():
    try:
        greet("  ")
    except ValueError:
        return
    raise AssertionError("a blank name should have been refused")
"""
)


def greeting(brief: Brief) -> CodeDraft:
    """Case (a): the source's own test is the main ask, and one edge is authored on top."""
    return _code(
        brief,
        "greet",
        title="Greet somebody by name",
        cases=(GREETS, BLANK),
        origin=Origin("lessons/greeting.md", None),
        statement="Write `greet(who)`: the greeting for `who`, refusing a blank name.\n",
        reference=GREETING_REFERENCE,
        tests=GREETING_TESTS,
        plants={BLANK.id: GREETING_SOURCE},
    )


def greeting_whose_plant_handles_its_edge(brief: Brief) -> CodeDraft:
    """⛔ A planted defect: the edge's plant IS the reference, so `G3` cannot hold."""
    return replace(greeting(brief), plants={BLANK.id: GREETING_REFERENCE})


def greeting_with_a_vacuous_ask(brief: Brief) -> CodeDraft:
    """⛔ A plant that cannot clear: the main ask's test passes on anything, so `G2` refuses."""
    tests = GREETING_TESTS.replace('assert greet("Ada") == "Hello, Ada"', "assert True")
    return replace(greeting(brief), tests=tests)


def greeting_that_drops_its_edge(brief: Brief) -> CodeDraft:
    """⛔ The retreat a retry may never make: the refused edge case simply disappears."""
    return replace(greeting(brief), cases=(GREETS,), plants={})


EMPTY = Case("test_an_empty_text_is_only_the_mark", EDGE, "an empty text is only the mark")


def shout(brief: Brief) -> CodeDraft:
    """Case (b): the page's own example is the reference solution, unchanged."""
    return _code(
        brief,
        "shout",
        title="Shout a word",
        cases=(Case("test_shouts_a_word", MAIN, "a word is shouted"), EMPTY),
        origin=Origin("lessons/shout.md", "How to shout"),
        statement="Write `shout(text)`: the text in capitals, ending in a mark.\n",
        reference=SHOUT_EXAMPLE,
        tests=(
            "from shout import shout\n\n\ndef test_shouts_a_word():\n"
            '    assert shout("hi") == "HI!"\n\n\n'
            "def test_an_empty_text_is_only_the_mark():\n"
            '    assert shout("") == "!"\n'
        ),
        plants={EMPTY.id: 'def shout(text):\n    return text.upper() + "!" if text else ""\n'},
    )


NEGATIVE = Case("test_a_negative_price_is_refused", EDGE, "a negative price is refused")


def basket(brief: Brief) -> CodeDraft:
    """Case (c): nothing in the source to start from — all of it authored from the prose."""
    return _code(
        brief,
        "total",
        title="Total a basket",
        cases=(Case("test_totals_a_basket", MAIN, "a basket adds up"), NEGATIVE),
        origin=Origin("lessons/basket.md", None),
        statement="Write `total(prices)`: the sum of a basket, refusing a negative price.\n",
        reference=(
            "def total(prices):\n    if any(price < 0 for price in prices):\n"
            '        raise ValueError("a price is never negative")\n    return sum(prices)\n'
        ),
        tests=(
            "from total import total\n\n\ndef test_totals_a_basket():\n"
            "    assert total([2, 3, 5]) == 10\n\n\n"
            "def test_a_negative_price_is_refused():\n    try:\n        total([2, -1])\n"
            "    except ValueError:\n        return\n"
            '    raise AssertionError("a negative price should have been refused")\n'
        ),
        plants={NEGATIVE.id: "def total(prices):\n    return sum(prices)\n"},
    )


def _option(id, text, correct, says):
    return Option(id=id, text=text, correct=correct, says=says)


def gauge_questions() -> tuple[Question, ...]:
    """Two questions, each written from one passage of the prose page."""
    return (
        Question(
            id="q-hour",
            stem="When is the gauge read?",
            options=(
                _option("a", "At the same hour every day", True, "The page says so."),
                _option("b", "Whenever it rains", False, "The page names an hour, not weather."),
            ),
            origin=Origin("notes/gauge.md", "Taking a reading"),
        ),
        Question(
            id="q-book",
            stem="When is a reading copied into the book?",
            options=(
                _option("a", "At the end of the month", False, "The page says the same day."),
                _option("b", "On the same day", True, "The page says so."),
            ),
            origin=Origin("notes/gauge.md", "Writing it down"),
        ),
    )


def gauge(brief: Brief) -> QuizDraft:
    """The quiz case: a prose page, its questions written from its passages."""
    return QuizDraft(title="Field notes", questions=gauge_questions())


def gauge_keyed_twice(brief: Brief) -> QuizDraft:
    """⛔ A planted `Q4` defect: the first question keys both of its options."""
    first, second = gauge_questions()
    doubled = replace(first, options=tuple(replace(o, correct=True) for o in first.options))
    return QuizDraft(title="Field notes", questions=(doubled, second))


def gauge_that_deletes_a_question(brief: Brief) -> QuizDraft:
    """⛔ The retreat a retry may never make: the refused question is deleted."""
    return QuizDraft(title="Field notes", questions=gauge_questions()[1:])


#: The whole corpus, authored cleanly on the first attempt.
CLEAN = {
    "lessons/greeting.md": [greeting],
    "lessons/shout.md": [shout],
    "lessons/basket.md": [basket],
    "notes/gauge.md": [gauge],
}


class Scripted:
    """The deterministic author: per page, one draft-maker per attempt, the last repeated."""

    def __init__(self, script: dict) -> None:
        self.script = script
        self.briefs: list[Brief] = []
        self.excused: list = []

    def draft(self, brief: Brief):
        """Answer from the script, recording the brief it was handed."""
        self.briefs.append(brief)
        makers = self.script[brief.page.path]
        return makers[min(brief.attempt, len(makers)) - 1](brief)

    def excuse(self, entry) -> str:
        """Give the one written reason, recording which entry asked for it."""
        self.excused.append(entry)
        return BECAUSE


class Judging:
    """The independent pass's stand-in: every judgement taken, held, over the question as asked."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, brief: Brief, questions: tuple[Question, ...]) -> tuple[Judgement, ...]:
        """One `Q1` and `Q2` per question, one `Q3` per wrong option."""
        self.calls += 1
        taken = []
        for question in questions:
            over = question_digest(question)
            for gate in (Q1, Q2):
                taken.append(_judged(gate, question.id, WHOLE_QUESTION, over))
            for option in question.options:
                if not option.correct:
                    taken.append(_judged(Q3, question.id, option.id, over))
        return tuple(taken)


def _judged(gate: str, question: str, option: str, over: str) -> Judgement:
    return Judgement(
        gate=gate,
        question=question,
        option=option,
        prompt="the page and the question, and nothing else",
        taken_by="a scripted stand-in for the independent pass",
        outcome="the pass answered as the gate needs",
        held=True,
        over=over,
    )


class Running:
    """A REAL runner on the host, counting its runs. ⛔ Nothing about a run is stubbed."""

    def __init__(self) -> None:
        self.runs = 0

    def __call__(self, root: Path, command: tuple[str, ...]) -> Ran:
        """Run the command from `root`, with this interpreter standing in for `python3`."""
        self.runs += 1
        argv = [sys.executable if command[0] == "python3" else command[0], *command[1:]]
        done = run(argv, root)
        return Ran(done.returncode, done.stdout + done.stderr)


def snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    """Every file under `root`, by relative path, with its bytes and its modification time."""
    return {
        path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
