"""Mirror of `src/studyforge/execute/commands.py` (R12): what the runner will start."""

from __future__ import annotations

import json
import re

import pytest

from studyforge.corpus.manifest import parse
from studyforge.execute import (
    CONTAINER_PREFIX,
    ROOT_DIR,
    RunRefused,
    container_for,
    editor_container_for,
    require_commands,
    require_container,
    require_workdir,
)
from studyforge.skills.execution import onboard
from tests.studyforge.skills.execution.contracts import (
    corpus,
    editor_text,
    manifest_document,
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


def test_the_editor_container_is_the_one_the_generated_compose_file_brings_up(tmp_path):
    """⭐ The convention and the file that realises it, read together (`W416`).

    ⚠️ Compose derives a container's name as `<project>-<service>-<index>`, and
    what this asserts is the two halves this repository owns — the project
    `skills.execution` names and the one service it renders — against the one
    name the framework looks a running editor up by. ⛔ **The derivation itself
    is Compose's and cannot be read in this gate**, which has no Docker: it is a
    host reading, in `W416`'s handoff, and taken against this same spelling.
    """
    document = manifest_document()
    generated = onboard.generate(
        parse(json.dumps(document)), editor_text=editor_text(), root=corpus(tmp_path)
    )
    text = dict(generated.files)[onboard.COMPOSE_FILE]
    project = re.search(r"^name: (\S+)$", text, flags=re.MULTILINE)
    services = re.findall(r"^  (\S+):$", text.split("services:", 1)[1], flags=re.MULTILINE)
    assert project is not None and services
    assert editor_container_for(document["source"]) == f"{project.group(1)}-{services[0]}-1"


@pytest.mark.parametrize("name", ["two words", "-flag", "a;b", "", None, "a/b"])
def test_a_container_name_that_is_not_one_word_is_refused(name):
    with pytest.raises(RunRefused):
        require_container(name)


@pytest.mark.parametrize("ending", ["\n", "\r\n", "\r"])
def test_a_trailing_line_ending_is_refused_by_every_check_here(ending):
    # ⛔ W434. `require_container` reads `SAFE_SEGMENT` directly and never
    # re-checks, so the pattern's anchor is this module's whole defence. Each
    # value is legal without its ending — the negative control is asserted.
    assert require_container("runner") == "runner"
    with pytest.raises(RunRefused):
        require_container("runner" + ending)
    assert require_workdir("practice") == "practice"
    with pytest.raises(RunRefused):
        require_workdir("practice" + ending)
    with pytest.raises(RunRefused):
        require_commands([["python3", "greet.py" + ending]])
