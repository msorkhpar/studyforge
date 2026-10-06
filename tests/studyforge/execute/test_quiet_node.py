"""Mirror of the `node --test` rules of `src/studyforge/execute/quiet.py` (R12).

⭐ The input is real `node --test` output (`transcripts_node.py` says where it came from).
**What it asserts.** The rules are chosen by the run's command (`node` with `--test`) and never
by being the declared runtime; a corpus declaring no tool with rules is unfiltered as before;
every choice that was made before is unchanged by declaring `node` beside it; and a filtered run
loses only the tally lines, never an assertion, a frame or Node's own load-failure message.
"""

from __future__ import annotations

import pytest

from studyforge.execute import exit_line
from studyforge.execute.quiet import GRADLE, MAVEN, NODE_TEST, PYTEST, TOOLCHAINS, select
from tests.studyforge.execute.test_quiet import GRADLE_RUNS, TWO_TOOLS, run, shown
from tests.studyforge.execute.transcripts_node import NODE_ENUM, NODE_FAILURE, NODE_PASS

CLAUDE_TOOLS = ("gradle", "java", "kotlin", "node", "python")


@pytest.mark.parametrize(
    "argv",
    [
        ["node", "--test", "x.test.ts"],
        ["node", "--test", "--test-reporter=spec", "--test-reporter-destination=stdout", "a.ts"],
        ["/usr/local/bin/node", "--test"],
    ],
)
def test_a_node_test_command_picks_node_in_a_corpus_that_declares_another_tool(argv):
    assert select(CLAUDE_TOOLS, argv) is NODE_TEST


@pytest.mark.parametrize(
    "argv",
    [
        ["node", "run.ts"],
        ["node", "--import", "x.mjs", "run.ts"],
        ["node", "--test-reporter=spec", "run.ts"],
        ["nodemon", "--test"],
        ["python3", "--test"],
    ],
    ids=["script", "import", "reporter-only", "lookalike-word", "other-interpreter"],
)
def test_a_command_that_does_not_run_node_tests_never_picks_it(argv):
    assert select(CLAUDE_TOOLS, argv) is GRADLE


@pytest.mark.parametrize("argv", [None, ["node", "--test"], ["pytest"], ["mvn", "test"]])
def test_a_corpus_declaring_node_and_no_tool_with_rules_is_never_filtered(argv):
    for declared in (("node",), ("python", "node"), ("node", "shell", "sqlite")):
        assert select(declared, argv) is None


@pytest.mark.parametrize("argv", [["gradle", "test"], ["./gradlew", "test"], ["node", "x.ts"]])
def test_declaring_node_beside_one_tool_selects_what_it_selected_before(argv):
    assert select(("gradle", "kotlin", "node"), argv) is GRADLE
    assert select(("java", "maven", "node"), argv) is MAVEN


def test_declaring_node_beside_two_tools_leaves_their_per_run_choice_alone():
    assert select((*TWO_TOOLS, "node"), ["./gradlew", "test"]) is GRADLE
    assert select((*TWO_TOOLS, "node"), ["mvn", "test"]) is MAVEN
    assert select((*TWO_TOOLS, "node"), ["node", "x.ts"]) is None


def test_pytest_is_still_chosen_by_its_own_command_beside_node():
    assert select(CLAUDE_TOOLS, ["python3", "-m", "pytest"]) is PYTEST


@pytest.mark.parametrize("transcript", [NODE_FAILURE, NODE_PASS], ids=["failure", "pass"])
def test_a_node_run_drops_only_the_tallies_nothing_else_says(transcript):
    lines = run(transcript, 1)
    kept = shown(lines, NODE_TEST)
    assert [line for line in kept if line in lines] == kept, "a line was rewritten"
    assert exit_line(1) in kept
    for dropped in ("ℹ suites 0", "ℹ cancelled 0", "ℹ skipped 0", "ℹ todo 0"):
        assert dropped not in kept
    assert not any(line.startswith("ℹ duration_ms") for line in kept)
    assert len(kept) < len(lines)


def test_a_node_failure_keeps_the_assertion_the_frames_and_the_tally():
    lines = run(NODE_FAILURE, 1)
    kept = shown(lines, NODE_TEST)
    must = [
        line
        for line in lines
        if line.startswith(("✖", "✔", "ℹ tests", "ℹ pass", "ℹ fail"))
        or "AssertionError" in line
        or line.lstrip().startswith(("at ", "actual:", "expected:"))
    ]
    assert must and [line for line in kept if line in must] == must
    assert "  AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:" in kept


def test_nodes_own_message_for_an_enum_survives_whole():
    lines = run(NODE_ENUM, 1)
    kept = shown(lines, NODE_TEST)
    message = "TypeScript enum is not supported in strip-only mode"
    assert f"SyntaxError [ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX]: {message}" in kept
    assert "  code: 'ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX'" in kept
    assert [line for line in lines if line.startswith("    at ")] == [
        line for line in kept if line.startswith("    at ")
    ]
    assert "✖ practice/normalise.test.ts (46.257998ms)" in kept


def test_a_programs_own_line_survives_the_node_rules():
    kept = shown(
        run(["a program line", "ℹ this is the program's, not a tally", "ℹ tests 1"]), NODE_TEST
    )
    assert "a program line" in kept and "ℹ this is the program's, not a tally" in kept


def test_a_gradle_or_maven_run_is_unchanged_by_the_node_rules():
    for transcript in GRADLE_RUNS:
        lines = run(transcript, 1)
        assert shown(lines, select(CLAUDE_TOOLS, ["./gradlew", "test"])) == shown(lines, GRADLE)
    assert TOOLCHAINS["gradle"] is GRADLE and TOOLCHAINS["maven"] is MAVEN
    assert TOOLCHAINS["node"] is NODE_TEST and NODE_TEST.only_by_command
