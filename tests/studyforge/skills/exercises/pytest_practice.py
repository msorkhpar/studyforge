"""A Python practice graded with pytest through the JUnit report, in the shape a course ships it.

⭐ **The fixture, once.** One page of `authoring.py`'s corpus, one draft: a starter that
returns a wrong value, a reference, one planted wrong solution per edge case, the tests, and
the command `python3 -m pytest --junitxml=<report>` (argv, no shell). The variant a run
grades is chosen by which solution the staging puts at the main file, which is the one place
the framework selects it.

⚠️ **Two cases carry a space in their id** (`test_collapses[inner spaces]`), because that is
how pytest spells a parametrised test given readable ids.
⛔ Nothing here asserts.
"""

from __future__ import annotations

from dataclasses import replace

from studyforge.exercise import EDGE, MAIN, Case, Origin
from studyforge.skills.exercises import Brief, CodeDraft

MAIN_CASE = Case("test_one_space_between_words", MAIN, "words are separated by one space")
BLANK = Case("test_blank_text_is_refused", EDGE, "blank text is refused")
INNER = Case("test_collapses[inner spaces]", EDGE, "a run of spaces inside is one space")
TABS = Case("test_collapses[tabs and newlines]", EDGE, "tabs and newlines count as spaces")

REFERENCE = '''def normalise(text):
    if not text.strip():
        raise ValueError("there is nothing to normalise")
    return " ".join(text.split())
'''

#: Returns a wrong value, so every test fails on an assertion and none on an error.
STARTER = "def normalise(text):\n    return text\n"

#: What an author writes first and a pass of these gates must not let through.
RAISING_STARTER = (
    "def normalise(text):\n    raise NotImplementedError('write normalise')\n"
)

PLANTS = {
    BLANK.id: 'def normalise(text):\n    return " ".join(text.split())\n',
    INNER.id: (
        "def normalise(text):\n"
        "    if not text.strip():\n"
        '        raise ValueError("there is nothing to normalise")\n'
        "    return text.strip()\n"
    ),
    TABS.id: (
        "import re\n\n\ndef normalise(text):\n"
        "    if not text.strip():\n"
        '        raise ValueError("there is nothing to normalise")\n'
        '    return " ".join(re.split(" +", text.strip()))\n'
    ),
}

TESTS = '''import pytest

from normalise import normalise


def test_one_space_between_words():
    assert normalise(" one two") == "one two"


def test_blank_text_is_refused():
    try:
        normalise("   ")
    except ValueError:
        return
    raise AssertionError("blank text should have been refused")


@pytest.mark.parametrize(
    "raw,want",
    [("a   b", "a b"), ("a\\tb\\nc", "a b c")],
    ids=["inner spaces", "tabs and newlines"],
)
def test_collapses(raw, want):
    assert normalise(raw) == want
'''

REPORT = "target/report.xml"


def draft(brief: Brief, *, report: str = REPORT, written: str = REPORT, **parts) -> CodeDraft:
    """The practice as a draft; `written` is where the command says the report lands.

    ⭐ `report` is where the record says it is. Making the two differ is the planted
    wrong report path.
    """
    ws = brief.places.workspace
    made = CodeDraft(
        title="Normalise whitespace",
        lang="python",
        main_file="normalise.py",
        test_file="test_normalise.py",
        run_command=("python3", f"{ws}/normalise.py"),
        test_command=(
            "python3",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            f"--junitxml={ws}/{written}",
            f"{ws}/test_normalise.py",
        ),
        cases=(MAIN_CASE, BLANK, INNER, TABS),
        report=report,
        origin=Origin("lessons/basket.md", None),
        statement="Write `normalise(text)`: one space between words, refusing blank text.\n",
        starter=STARTER,
        reference=REFERENCE,
        tests=TESTS,
        plants=dict(PLANTS),
        assertions_only=True,
    )
    return replace(made, **parts)
