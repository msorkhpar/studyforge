"""The `check` verb's boundaries: no argument becomes a command (§8.3), every line is gated (R7).

⛔ **Spec §8.3, rule 3: nothing the reader types becomes a command.** The argument selects a
practice and nothing else. Each clause is asserted both ways: hostile arguments run nothing,
and every spelling of a practice's file runs exactly that practice's record, with no part of
the argument in the argv.

⛔ **R7:** every line the verb prints is gated, the runner's and its own. ⭐ **Unfiltered:** the
lines between the verb's header and the exit line are exactly the runner's.
"""

from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys

import pytest

from studyforge.archive.scrub import HOME_PATH_PLACEHOLDER
from studyforge.cli import check as check_module
from studyforge.cli.check import FAILED, NOT_A_UNIT_FILE, PASSED, build_parser
from studyforge.execute import Runner
from studyforge.exitcodes import UNUSABLE
from tests.studyforge.cli.checking import PASSING, UNTESTED, check, main_path, record
from tests.studyforge.execute.runnable import (
    FOREIGN_HOME,
    fixture_copy,
    host_environment_clean,
    observed,
)
from tests.support import repository_root

#: A file the argument would create if any part of it ever reached a shell or an argv.
SENTINEL = "pwned"


@pytest.fixture
def root(tmp_path, monkeypatch):
    host_environment_clean(monkeypatch)
    return fixture_copy(tmp_path)


# --------------------------------------------------------------------------
# ⛔ §8.3 rule 3 — the argument selects a file; the command comes from disk
# --------------------------------------------------------------------------


def hostile(root) -> list[str]:
    """Arguments that would run something if anything but a path comparison read them."""
    greet = record(PASSING).main_path
    return [
        f"{greet}; touch {SENTINEL}",
        f"{greet} && touch {SENTINEL}",
        f"$(touch {SENTINEL})",
        f"`touch {SENTINEL}`",
        f"{greet}|touch {SENTINEL}",
        "practice/plants/talk.py",  # a real program no practice names
        record(PASSING).test_path,  # the grader itself
        "python3",
        str(root / ".." / SENTINEL),
    ]


def test_no_hostile_argument_runs_anything(root, monkeypatch):
    monkeypatch.chdir(root)
    for argument in hostile(root):
        checked = check(argument, "--corpus", str(root))
        assert checked.code == UNUSABLE, argument
        assert NOT_A_UNIT_FILE in checked.lines[0], argument
        assert checked.handed.built == [] and checked.handed.started == [], argument
    assert not (root / SENTINEL).exists() and not (root.parent / SENTINEL).exists()


def test_every_spelling_of_a_practices_file_runs_exactly_its_record(root, monkeypatch):
    monkeypatch.chdir(root / "practice")
    greet = record(PASSING).main_path
    spellings = [
        str(root / greet),
        f"passes/{greet.rsplit('/', 1)[1]}",
        f"./passes/../passes/{greet.rsplit('/', 1)[1]}",
        str(root / "kata" / ".." / greet),
    ]
    for spelling in spellings:
        checked = check(spelling)
        assert checked.code == PASSED, spelling
        assert checked.handed.started == [(record(PASSING).test_command,)], spelling


def test_a_practices_file_that_is_a_link_is_selected_by_its_own_spelling(
    root, tmp_path, monkeypatch
):
    # ⭐ Compared as spelled, normalised but before links are resolved: a reader's editor may
    # keep the file elsewhere and link it in. Resolved, it would sit outside the corpus.
    hello = root / record(UNTESTED).main_path
    kept = tmp_path / "kept-elsewhere.py"
    kept.write_text(hello.read_text(encoding="utf-8"), encoding="utf-8")
    hello.unlink()
    hello.symlink_to(kept)
    monkeypatch.chdir(root)
    checked = check("practice/untested/../untested/hello.py")
    assert checked.code == PASSED
    assert checked.handed.started == [(record(UNTESTED).run_command,)]
    # The other way: the file it links to, named directly, is no unit's file.
    assert check(str(kept), "--corpus", str(root)).code == UNUSABLE


def test_a_corpus_named_through_a_link_still_selects_the_file(root, tmp_path):
    # ⭐ And compared with links resolved: the root and the file may be spelled through
    # different links to one directory.
    link = tmp_path / "linked-corpus"
    link.symlink_to(root, target_is_directory=True)
    checked = check(main_path(root, PASSING), "--corpus", str(link))
    assert checked.code == PASSED
    assert checked.handed.started == [(record(PASSING).test_command,)]
    # The other way: through the link, a file no practice names is still refused.
    assert check(str(root / "pytest.ini"), "--corpus", str(link)).code == UNUSABLE


def test_the_argument_never_appears_in_what_the_runner_is_handed(root, monkeypatch):
    monkeypatch.chdir(root)
    spelling = "./practice/passes/../passes/greet.py"
    handed = check(spelling).handed.started
    assert handed == [(record(PASSING).test_command,)]
    assert all(spelling not in argument for command in handed[0] for argument in command)


def test_the_verb_takes_one_file_and_no_other_input(root):
    parser = build_parser()
    assert {action.dest for action in parser._actions} == {"help", "file", "corpus"}
    for argv in (
        [record(PASSING).main_path, "rm", "-rf", "."],
        [record(PASSING).main_path, "--", "-c", "print(1)"],
        [record(PASSING).main_path, "--command", "true"],
    ):
        with pytest.raises(SystemExit) as refused:
            parser.parse_args(argv)
        assert refused.value.code == UNUSABLE


def test_no_option_offers_the_docker_socket_or_a_mount():
    # ⛔ §8.3: not behind a flag. The runner reaches the container from outside.
    text = build_parser().format_help().lower()
    for word in ("socket", "docker.sock", "mount", "--docker", "--container"):
        assert word not in text


def test_the_verb_starts_no_process_of_its_own():
    # ⛔ `execute` is the only package that starts one: this module imports no way to.
    tree = ast.parse(inspect.getsource(check_module))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not imported & {"subprocess", "socket", "pty", "multiprocessing"}
    assert "system" not in {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }


# --------------------------------------------------------------------------
# ⛔ R7 — every line is gated, the runner's and the verb's own
# --------------------------------------------------------------------------


def test_every_line_of_the_programs_output_is_gated(root):
    hello = root / record(UNTESTED).main_path
    hello.write_text(
        f"import os\nprint('home', '{FOREIGN_HOME}/secret.txt')\nprint('here', os.getcwd())\n",
        encoding="utf-8",
    )
    # The other way: the program itself prints both, so a pass-through would leak them.
    raw = subprocess.run(
        [sys.executable, str(hello)], cwd=root, capture_output=True, text=True, check=True
    ).stdout
    assert FOREIGN_HOME in raw and str(root) in raw
    checked = check(str(hello))
    assert checked.code == PASSED
    assert FOREIGN_HOME not in checked.text and str(root) not in checked.text
    assert f"home {HOME_PATH_PLACEHOLDER}/secret.txt" in checked.lines
    assert "here ." in checked.lines


def test_the_verbs_own_lines_are_gated_including_the_argument_it_echoes(root):
    typed = f"{FOREIGN_HOME}/practice/passes/greet.py"
    checked = check(typed, "--corpus", str(root))
    assert checked.code == UNUSABLE
    assert FOREIGN_HOME not in checked.text
    refused = f"{HOME_PATH_PLACEHOLDER}/practice/passes/greet.py: {NOT_A_UNIT_FILE}"
    assert checked.lines[0] == refused


def test_the_output_is_the_runners_unfiltered(root):
    for unit in (PASSING, UNTESTED):
        exercise = record(unit)
        command = exercise.test_command if exercise.graded else exercise.run_command
        direct = list(Runner(root, None).start([command]).lines())
        checked = check(main_path(root, unit))
        header = 1
        streamed = checked.lines[header : header + len(direct)]
        assert observed(streamed) == observed(direct), unit
        assert checked.lines[0].startswith(f"check {exercise.main_path}  ")


# --------------------------------------------------------------------------
# the installed command, as a reader runs it
# --------------------------------------------------------------------------


def test_the_reader_runs_it_from_the_corpus_root_as_the_installed_command(root):
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in ("PYTHONUNBUFFERED", "PYTHONDONTWRITEBYTECODE")
    }
    environment["PYTHONPATH"] = str(repository_root() / "src")
    codes = {}
    for path in (record(PASSING).main_path, "practice/fails/total.py", "pytest.ini"):
        ran = subprocess.run(
            [sys.executable, "-m", "studyforge.cli", "check", path],
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )
        codes[path] = ran.returncode
        assert str(root) not in ran.stdout + ran.stderr
    assert codes == {
        record(PASSING).main_path: PASSED,
        "practice/fails/total.py": FAILED,
        "pytest.ini": UNUSABLE,
    }
