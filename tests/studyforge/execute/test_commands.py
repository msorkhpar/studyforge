"""Mirror of `src/studyforge/execute/commands.py` (R12): what the runner will start."""

from __future__ import annotations

import pytest

from studyforge.execute import (
    CONTAINER_PREFIX,
    ROOT_DIR,
    RunRefused,
    container_for,
    require_commands,
    require_container,
    require_workdir,
)

PERMITTED = [
    ["python3", "-m", "pytest", "-q", "practice/passes/check_greet.py"],
    ["mvn", "-o", "test"],
]


def test_argv_lists_are_returned_unchanged_as_tuples():
    assert require_commands(PERMITTED) == tuple(tuple(command) for command in PERMITTED)


@pytest.mark.parametrize(
    "commands",
    [
        "python3 practice/passes/greet.py",  # a shell line: never split
        b"python3",
        [],
        ["python3", "greet.py"],  # one command given as a flat list of strings
        [[]],
        [["python3", "greet.py; rm -rf ."]],
        [["python3", "$(id)"]],
        [["/usr/bin/python3", "greet.py"]],
        [["python3", "../outside.py"]],
        [["python3", "greet.py"], "pytest"],
        {"run": ["python3"]},
    ],
)
def test_anything_else_is_refused_before_a_process_exists(commands):
    with pytest.raises(RunRefused):
        require_commands(commands)


def test_the_directory_is_the_root_or_a_relative_path_inside_it():
    assert require_workdir(ROOT_DIR) == ROOT_DIR
    assert require_workdir("practice/passes") == "practice/passes"


@pytest.mark.parametrize("cwd", ["/work", "..", "practice/../..", "-rf", "", None, "a\\b"])
def test_a_directory_outside_the_root_is_refused(cwd):
    with pytest.raises(RunRefused):
        require_workdir(cwd)


def test_the_container_is_named_for_its_corpus_as_the_readers_run_line_names_it():
    assert container_for("runnable-demo") == CONTAINER_PREFIX + "runnable-demo"
    assert container_for("runnable-demo") == "studyforge-runner-runnable-demo"


@pytest.mark.parametrize("name", ["two words", "-flag", "a;b", "", None, "a/b"])
def test_a_container_name_that_is_not_one_word_is_refused(name):
    with pytest.raises(RunRefused):
        require_container(name)
