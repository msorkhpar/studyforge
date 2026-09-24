"""A fixture corpus whose units RUN — the input the runner and the terminal command need.

**What it asserts.** That `tests/fixtures/runnable/` is a valid corpus, that it
carries by construction every shape a runner must tell apart, and that each
shape BEHAVES as it is named when its own declared commands are run:

| Unit | Shape | Its run command | Its test command |
|---|---|---|---|
| 1 | a file and a test that passes | succeeds | passes |
| 2 | a file and a test that fails | succeeds | fails |
| 3 | a file and NO test — ungraded, its record names the file | succeeds | none declared |
| 4 | a file that does not compile | fails | errors at collection |
| 5 | no practice at all — reading only | — | — |

⭐ **Why unit 4's run command matters as much as its test.** *"The first
failure ends the run"*: a runner that stops at the failed run never
reaches the grader, and the grader it did not reach is asserted to be one that
could not have been run against anything.

⛔ **Every command runs in a temp COPY, never in the tree**, with bytecode off:
the fixture tree is un-ignored by the repository (`!tests/fixtures/**`), so a
`__pycache__` written into it would be an untracked file, and the suite's own
tree-state check would red on it.

⭐ **Why the graders are `check_*.py` and not `test_*.py`.** This suite's
`testpaths` include `tests/`, so a grader under the default pattern is
collected by the repository's OWN run — and unit 2 fails and unit 4 errors on
purpose. The corpus's own `pytest.ini` declares the pattern its graders use;
both halves are asserted below.

**Depends on.** `tests.fixture_checks` for the declaration, and the framework's
own readers — `studyforge.exercise` for the record and its state,
`studyforge.validate` for the verdict. ⛔ It imports nothing from `execute/`:
the runner is `studyforge.execute`'s, and this is the fixture it is measured on.
"""

from __future__ import annotations

import ast
import configparser
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

import pytest

from studyforge.corpus.manifest import MANIFEST_KEYS
from studyforge.exercise import of, state_of
from studyforge.exercise.states import GRADED, NONE, UNGRADED
from studyforge.validate.run import validate
from tests.fixture_checks import FIXTURES, RUNNABLE, VALID, violations

ROOT = FIXTURES / RUNNABLE
RAW = ROOT / "archive" / "kata" / "raw" / "python"

#: Each unit's state, and — for a unit with a file — the directory it lives in.
SHAPES = {
    1: (GRADED, "passes"),
    2: (GRADED, "fails"),
    3: (UNGRADED, "untested"),
    4: (GRADED, "broken"),
    5: (NONE, None),
}

#: pytest's exit codes, named by what they mean here.
PASSED, FAILED, ERRORED, COLLECTED_NOTHING = 0, 1, 2, 5

#: What each graded unit's two commands must do: (run exit, test exit).
BEHAVES = {1: (PASSED, PASSED), 2: (PASSED, FAILED), 4: (FAILED, ERRORED)}


def practice(unit: int) -> dict | None:
    """The unit's decoded practice document, or `None` when it sets no work."""
    path = RAW / f"unit-{unit:02d}" / "practice-1.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def exercise(unit: int):
    """The unit's exercise, read through the framework's own reader."""
    return of(practice(unit), f"unit {unit}")


@pytest.fixture
def copy(tmp_path) -> Path:
    """The corpus, copied somewhere a run may write."""
    return Path(shutil.copytree(ROOT, tmp_path / RUNNABLE))


def run(argv, cwd: Path) -> subprocess.CompletedProcess:
    """Run one declared command in `cwd`, with bytecode off and none of this suite's paths."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTEST", "PYTHONPATH"))}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    argv = [sys.executable if argv[0] == "python3" else argv[0], *argv[1:]]
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)


# --------------------------------------------------------------------------
# it is a corpus, and a valid one
# --------------------------------------------------------------------------


def test_the_corpus_is_declared_valid_so_every_contract_test_sees_it():
    # ⚠️ A corpus outside `VALID` is a directory no parametrized check opens.
    assert RUNNABLE in VALID
    assert violations(ROOT) == []


def test_validate_passes_it_with_nothing_unchecked():
    # ⭐ Its source material is committed beside its archive, so the heading
    # count and the classification checks actually run rather than report
    # `Unchecked`.
    report = validate(ROOT)
    assert report.findings == ()
    assert report.unchecked == ()


def test_validate_would_refuse_a_file_the_manifest_does_not_classify(copy):
    # ⛔ The other direction: the verdict above is a real one on this corpus.
    (copy / "stray.py").write_text("print('unclassified')\n", encoding="utf-8")
    assert "unclassified" in validate(copy).rules


# --------------------------------------------------------------------------
# every shape is present, by construction
# --------------------------------------------------------------------------


def test_every_unit_is_in_the_state_it_is_named_for():
    assert {n: state_of(practice(n)) for n in SHAPES} == {n: s for n, (s, _d) in SHAPES.items()}
    assert set(state for state, _d in SHAPES.values()) == {GRADED, UNGRADED, NONE}


@pytest.mark.parametrize("unit", sorted(BEHAVES))
def test_a_graded_unit_names_files_that_are_on_disk_in_its_own_directory(unit):
    record = exercise(unit)
    folder = PurePosixPath("practice", SHAPES[unit][1])
    for named in (record.main_path, record.test_path):
        assert PurePosixPath(named).parent == folder, named
        assert (ROOT / named).is_file(), named


def test_the_ungraded_unit_has_a_file_and_no_grader():
    # ⭐ *A file with no test is not a failure* (spec §7) — so the
    # file must be there for a runner to be handed, and nothing may grade it.
    folder = ROOT / "practice" / SHAPES[3][1]
    assert [p.name for p in folder.iterdir()] == ["hello.py"]
    # ⭐ The record names that file and how it runs, and no grader.
    record = exercise(3)
    assert record.main_path == "practice/untested/hello.py"
    assert (ROOT / record.main_path).is_file()
    assert record.graded is False
    assert (record.test_path, record.test_command, record.provenance) == (None, None, None)


def test_every_unit_with_a_file_names_it_and_only_the_graded_ones_name_a_grader():
    # ⭐ What `studyforge check` resolves a reader's file through: every unit whose
    # practice has a file carries a record naming it, graded or not. ⛔ The
    # other way: the record's `graded` is exactly the unit's state.
    named = {unit: exercise(unit) for unit, (_s, folder) in SHAPES.items() if folder}
    assert all(record is not None for record in named.values())
    assert {unit: record.graded for unit, record in named.items()} == {
        unit: SHAPES[unit][0] == GRADED for unit in named
    }
    assert exercise(5) is None


def test_one_runtime_and_it_is_python():
    for unit in BEHAVES:
        record = exercise(unit)
        assert record.run_command[0] == record.test_command[0] == "python3", unit
    assert exercise(3).run_command[0] == "python3"


def test_the_runtimes_key_is_not_invented_before_w350_lands():
    # ⛔ The framework owns the key: absent from the framework, it is absent
    # here, and present there it must be declared here.
    manifest = json.loads((ROOT / "corpus.json").read_text(encoding="utf-8"))
    if "runtimes" in MANIFEST_KEYS:
        assert manifest.get("runtimes") == ["python"]
    else:
        assert "runtimes" not in manifest


# --------------------------------------------------------------------------
# each shape behaves as named — in a temp copy
# --------------------------------------------------------------------------


@pytest.mark.parametrize("unit", sorted(BEHAVES))
def test_a_graded_units_commands_exit_as_its_shape_says(unit, copy):
    record = exercise(unit)
    ran, tested = run(record.run_command, copy), run(record.test_command, copy)
    assert (ran.returncode, tested.returncode) == BEHAVES[unit], ran.stderr + tested.stdout


def test_the_file_that_does_not_compile_fails_as_a_syntax_error(copy):
    ran = run(exercise(4).run_command, copy)
    tested = run(exercise(4).test_command, copy)
    assert "SyntaxError" in ran.stderr
    assert "SyntaxError" in tested.stdout
    assert " passed" not in tested.stdout


def test_the_file_parses_and_only_the_compiler_refuses_it():
    # ⛔ A PARSE error would break every walker in this suite that `ast.parse`s
    # each `.py` under `tests/`. ⭐ `'break' outside loop` is raised
    # by the compiler, not the parser — still a `SyntaxError`, and still a file
    # that never runs — so both halves are pinned, and "simplifying" it to a
    # missing colon reds here rather than in five unrelated modules.
    text = (ROOT / exercise(4).main_path).read_text(encoding="utf-8")
    assert isinstance(ast.parse(text), ast.Module)
    with pytest.raises(SyntaxError, match="outside loop"):
        compile(text, exercise(4).main_path, "exec")
    # ⭐ And the other graded files compile, so the instrument can tell them apart.
    for unit in (1, 2):
        path = exercise(unit).main_path
        compile((ROOT / path).read_text(encoding="utf-8"), path, "exec")


def test_every_practice_starts_from_the_file_as_shipped():
    # ⭐ The starting code a page shows is the file the reader edits.
    for unit, (_state, folder) in SHAPES.items():
        if folder is None:
            continue
        shipped = (ROOT / "practice" / folder).iterdir()
        (main,) = [p for p in shipped if not p.name.startswith("check_")]
        assert practice(unit)["starting_code"] == main.read_text(encoding="utf-8"), unit


def test_the_unit_with_no_test_runs_and_collects_nothing(copy):
    folder = f"practice/{SHAPES[3][1]}"
    # ⭐ Its OWN declared run command, read from its record.
    ran = run(exercise(3).run_command, copy)
    assert ran.returncode == PASSED, ran.stderr
    assert "Hello from a file with no test" in ran.stdout
    assert run(["python3", "-m", "pytest", "-q", folder], copy).returncode == COLLECTED_NOTHING
    # ⛔ Not vacuous: the same command over a graded unit's folder DOES collect.
    passes = f"practice/{SHAPES[1][1]}"
    assert run(["python3", "-m", "pytest", "-q", passes], copy).returncode == PASSED


def test_a_run_writes_bytecode_so_it_is_never_run_in_the_tree(copy):
    # ⛔ Why every run above is in a copy: with bytecode ON, one grader run
    # writes a cache beside the file it imported — which in the tree would be
    # an untracked file under the un-ignored fixture directory.
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTEST", "PYTHONPATH"))}
    # ⚠️ Both halves: the pinned image sets a cache PREFIX too, which would
    # redirect the cache out of the copy and make this plant read nothing.
    env.pop("PYTHONDONTWRITEBYTECODE", None)
    env.pop("PYTHONPYCACHEPREFIX", None)
    argv = [sys.executable, *exercise(1).test_command[1:]]
    subprocess.run(argv, cwd=copy, env=env, capture_output=True, timeout=120, check=True)
    assert list(copy.rglob("__pycache__"))
    assert [p for p in ROOT.rglob("*") if p.name in ("__pycache__", ".pytest_cache")] == []


# --------------------------------------------------------------------------
# ⛔ this suite never collects the graders; the corpus's own runner does
# --------------------------------------------------------------------------


def graders() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.py") if p.name.startswith("check_"))


def test_no_file_in_the_corpus_matches_this_suites_collection_pattern(pytestconfig):
    patterns = pytestconfig.getini("python_files")
    matched = [
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*.py")
        if any(PurePosixPath(p.name).full_match(pattern) for pattern in patterns)
    ]
    assert matched == []


def test_the_corpus_declares_the_pattern_its_graders_use():
    ini = configparser.ConfigParser()
    ini.read(ROOT / "pytest.ini", encoding="utf-8")
    pattern = ini["pytest"]["python_files"]
    assert graders(), "no grader to match"
    assert all(PurePosixPath(p.name).full_match(pattern) for p in graders())
    assert {exercise(unit).test_path for unit in BEHAVES} == {
        p.relative_to(ROOT).as_posix() for p in graders()
    }


def test_the_corpus_runner_writes_no_cache_and_would_without_its_ini(copy):
    # ⭐ The `pytest.ini` also turns pytest's cache off, so a grader run leaves
    # nothing at the corpus root but what the interpreter itself writes.
    run(exercise(1).test_command, copy)
    assert not (copy / ".pytest_cache").exists()
    # ⛔ The other way: the same run, with the ini's `addopts` removed.
    ini = copy / "pytest.ini"
    ini.write_text(ini.read_text(encoding="utf-8").replace("addopts", "# addopts"), "utf-8")
    run(exercise(1).test_command, copy)
    assert (copy / ".pytest_cache").is_dir()
