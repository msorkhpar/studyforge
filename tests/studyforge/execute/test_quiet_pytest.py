"""Mirror of the pytest rules of `src/studyforge/execute/quiet.py` (R12).

⭐ The input is real pytest output (`transcripts_pytest.py` says where it came from).
**What it asserts.** pytest's rules are chosen by the run's command and never by being the
declared runtime; a corpus declaring `python` and no other tool with rules is unfiltered as
before; a Gradle or Maven choice is unchanged by declaring `python` beside them; and a
filtered pytest run loses only what pytest says about itself.
"""

from __future__ import annotations

import pytest

from studyforge.execute import exit_line
from studyforge.execute.quiet import GRADLE, MAVEN, PYTEST, TOOLCHAINS, select
from tests.studyforge.execute.test_quiet import GRADLE_RUNS, TWO_TOOLS, run, shown
from tests.studyforge.execute.transcripts_pytest import (
    PYTEST_FAILURE,
    PYTEST_PASS,
    PYTEST_QUIET_FAILURE,
    PYTEST_QUIET_PASS,
)

# --- pytest: chosen by the command, never by being the declared runtime ----------------------

CLAUDE_TOOLS = ("gradle", "java", "kotlin", "node", "python")
PYTEST_ARGVS = [
    ["pytest", "-q"],
    ["python3", "-m", "pytest", "-q", "x.py"],
    ["python", "-m", "pytest"],
    ["/usr/bin/python3.14", "-m", "pytest"],
    ["py.test"],
]
PYTEST_RUNS = [PYTEST_FAILURE, PYTEST_QUIET_FAILURE, PYTEST_PASS, PYTEST_QUIET_PASS]


@pytest.mark.parametrize("argv", PYTEST_ARGVS)
def test_a_pytest_command_picks_pytest_in_a_corpus_that_declares_another_tool(argv):
    assert select(CLAUDE_TOOLS, argv) is PYTEST


@pytest.mark.parametrize(
    "argv",
    [
        ["python3", "run.py"],
        ["python3", "-m", "unittest"],
        ["python3", "-c", "pytest"],
        ["pytestx"],
    ],
    ids=["script", "other-module", "lookalike-arg", "lookalike-word"],
)
def test_a_command_that_does_not_run_pytest_never_picks_it(argv):
    assert select(CLAUDE_TOOLS, argv) is GRADLE


@pytest.mark.parametrize("argv", [None, ["python3", "-m", "pytest"], ["pytest"], ["mvn", "test"]])
def test_a_corpus_declaring_python_and_no_tool_with_rules_is_never_filtered(argv):
    for declared in (("python",), ("python", "node"), ("python", "shell", "sqlite")):
        assert select(declared, argv) is None


@pytest.mark.parametrize("argv", [["gradle", "test"], ["./gradlew", "test"], ["python3", "x.py"]])
def test_declaring_python_beside_one_tool_selects_what_it_selected_before(argv):
    assert select(("gradle", "kotlin", "python"), argv) is GRADLE
    assert select(("java", "maven", "python"), argv) is MAVEN


def test_declaring_python_beside_two_tools_leaves_their_per_run_choice_alone():
    assert select((*TWO_TOOLS, "python"), ["./gradlew", "test"]) is GRADLE
    assert select((*TWO_TOOLS, "python"), ["mvn", "test"]) is MAVEN
    assert select((*TWO_TOOLS, "python"), ["python3", "x.py"]) is None


@pytest.mark.parametrize("transcript", PYTEST_RUNS, ids=["failure", "q-failure", "pass", "q-pass"])
def test_a_pytest_run_drops_only_what_pytest_says_about_itself(transcript):
    lines = run(transcript, 1)
    kept = shown(lines, PYTEST)
    assert [line for line in kept if line in lines] == kept, "a line was rewritten"
    assert exit_line(1) in kept
    for dropped in (
        "============================= test session starts ==============================",
        "rootdir: .",
        "collected 4 items",
        "....                                                                     [100%]",
    ):
        assert dropped not in kept
    assert len(kept) < len(lines)


@pytest.mark.parametrize("transcript", [PYTEST_FAILURE, PYTEST_QUIET_FAILURE])
def test_a_pytest_failure_keeps_the_assertion_the_frame_the_names_and_the_tally(transcript):
    lines = run(transcript, 1)
    kept = shown(lines, PYTEST)
    must = [
        line
        for line in lines
        if line.startswith(("E ", "FAILED ", ">", "_"))
        or line.endswith(": AssertionError")
        or "failed, 1 passed" in line
    ]
    assert must and [line for line in kept if line in must] == must
    assert "practice/test_normalise.py:6: AssertionError" in kept
    assert "E       AssertionError: assert ' one two' == 'one two'" in kept


def test_a_pytest_pass_keeps_the_tally_and_nothing_else_of_pytests():
    assert shown(run(PYTEST_QUIET_PASS), PYTEST) == ["4 passed in 0.01s", exit_line(0)]
    assert shown(run(PYTEST_PASS), PYTEST) == [
        "",
        "",
        "============================== 4 passed in 0.00s ===============================",
        exit_line(0),
    ]


def test_a_programs_own_line_survives_the_pytest_rules():
    lines = run([*PYTEST_QUIET_PASS[:1], "a program line", "[100%] is not progress", "4 passed"])
    kept = shown(lines, PYTEST)
    assert "a program line" in kept and "[100%] is not progress" in kept


def test_a_gradle_or_maven_run_is_unchanged_by_the_pytest_rules():
    for transcript in GRADLE_RUNS:
        lines = run(transcript, 1)
        assert shown(lines, select(CLAUDE_TOOLS, ["./gradlew", "test"])) == shown(lines, GRADLE)
    assert TOOLCHAINS["gradle"] is GRADLE and TOOLCHAINS["maven"] is MAVEN
    assert TOOLCHAINS["python"] is PYTEST and PYTEST.only_by_command
