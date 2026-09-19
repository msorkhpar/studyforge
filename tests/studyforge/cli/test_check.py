"""`SF-44`'s acceptance and its two decisions, on the runnable fixture, each clause both ways.

⭐ **The corpus has every shape the acceptance names**: units 1, 2 and 4 are graded (a test
that passes, one that fails, a file that does not compile), unit 3 is a file with no test,
and unit 5 is reading only. Each run is in a temp copy (`checking.py`).

⭐ **Host mode here, both modes in `test_check_modes.py`.** The mode is `SF-20`'s, and the
verb only hands it a command.
"""

from __future__ import annotations

import pytest

from studyforge.address import Address
from studyforge.cli import VERBS
from studyforge.cli.check import FAILED, NO_TEST, NOT_A_UNIT_FILE, PASSED, main
from studyforge.execute import EXIT_STOPPED, exit_line
from studyforge.exitcodes import UNUSABLE
from studyforge.progress import Progress
from tests.studyforge.cli.checking import (
    BROKEN,
    FAILING,
    GRADED_UNITS,
    PASSING,
    UNTESTED,
    check,
    entries,
    main_path,
    record,
)
from tests.studyforge.execute.runnable import fixture_copy, host_environment_clean

SECTION = "practice-python"


@pytest.fixture
def root(tmp_path, monkeypatch):
    """A fresh copy of the runnable corpus, and the host's own Python settings kept out."""
    host_environment_clean(monkeypatch)
    return fixture_copy(tmp_path)


def practice_entry(root, unit: int) -> dict | None:
    """The unit's entry, read back by the key the page reads (`progress.practice_key`)."""
    return Progress(root, depth=1).entry(Address(["kata"]), unit, SECTION)


# --------------------------------------------------------------------------
# the verb is registered
# --------------------------------------------------------------------------


def test_the_verb_is_registered_in_the_one_table_after_serve():
    assert VERBS["check"].run is main
    names = list(VERBS)
    assert names.index("serve") < names.index("check")


# --------------------------------------------------------------------------
# a file with a test runs it, and the exit code is its verdict
# --------------------------------------------------------------------------


def test_a_file_with_a_passing_test_runs_that_test_and_exits_zero(root):
    checked = check(main_path(root, PASSING))
    assert checked.code == PASSED == 0
    assert checked.handed.started == [(record(PASSING).test_command,)]
    assert checked.exit_lines() == [exit_line(0)]
    assert "1 passed" in checked.text


@pytest.mark.parametrize("unit", [FAILING, BROKEN])
def test_a_file_whose_test_does_not_pass_exits_non_zero(root, unit):
    checked = check(main_path(root, unit))
    assert checked.code == FAILED != 0
    assert checked.handed.started == [(record(unit).test_command,)]
    assert checked.exit_lines() != [exit_line(0)]


def test_a_graded_file_is_handed_its_test_and_never_its_program(root):
    for unit in GRADED_UNITS:
        started = check(main_path(root, unit)).handed.started
        assert started == [(record(unit).test_command,)]
        assert record(unit).run_command not in started[0]


# --------------------------------------------------------------------------
# decision (a): a file with no test runs its program, says so, and exits 0
# --------------------------------------------------------------------------


def test_a_file_with_no_test_runs_its_program_says_so_and_exits_zero(root):
    checked = check(main_path(root, UNTESTED))
    assert checked.code == PASSED == 0
    assert record(UNTESTED).test_command is None
    assert checked.handed.started == [(record(UNTESTED).run_command,)]
    assert "Hello from a file with no test" in checked.lines
    assert checked.lines[-1] == NO_TEST
    # The other way: a graded file never says it.
    assert NO_TEST not in check(main_path(root, PASSING)).lines


def test_a_file_with_no_test_exits_zero_even_when_its_program_fails(root):
    # ⭐ C5: no test, no failure. The program's own status is in the exit line.
    (root / record(UNTESTED).main_path).write_text("raise SystemExit(3)\n", encoding="utf-8")
    checked = check(main_path(root, UNTESTED))
    assert checked.code == PASSED
    assert checked.exit_lines() == [exit_line(3)]
    assert checked.lines[-1] == NO_TEST


def test_a_graded_file_whose_program_would_fail_is_still_judged_by_its_test(root):
    # The other way round: with a grader, the verdict is the test's, not the program's.
    greet = root / record(PASSING).main_path
    greet.write_text(greet.read_text(encoding="utf-8") + "\nraise SystemExit(3)\n", "utf-8")
    assert check(main_path(root, PASSING)).code == FAILED


# --------------------------------------------------------------------------
# decision (b): a graded file's test run is recorded; only a pass passes
# --------------------------------------------------------------------------


def test_a_passing_test_run_records_a_practice_pass_under_the_pages_key(root):
    assert practice_entry(root, PASSING) is None
    check(main_path(root, PASSING))
    entry = practice_entry(root, PASSING)
    assert entry is not None and entry["first_passed_at"] is not None
    assert entry["last"]["mode"] == "test" and entry["last"]["passed"] is True
    assert entry["last"]["commands"] == [" ".join(record(PASSING).test_command)]


@pytest.mark.parametrize("unit", [FAILING, BROKEN])
def test_a_test_run_that_does_not_pass_is_recorded_and_passes_nothing(root, unit):
    check(main_path(root, unit))
    entry = practice_entry(root, unit)
    assert entry is not None and entry["runs"] == 1
    assert entry["first_passed_at"] is None and entry["last"]["passed"] is False
    assert entry["last"]["exit"] != 0


def test_a_later_failure_never_takes_back_a_pass(root):
    check(main_path(root, PASSING))
    first = practice_entry(root, PASSING)["first_passed_at"]
    greet = root / record(PASSING).main_path
    greet.write_text("def greet(who):\n    return who\n", encoding="utf-8")
    assert check(main_path(root, PASSING)).code == FAILED
    entry = practice_entry(root, PASSING)
    assert entry["runs"] == 2 and entry["last"]["passed"] is False
    assert entry["first_passed_at"] == first


def test_a_file_with_no_test_records_nothing(root):
    check(main_path(root, UNTESTED))
    assert practice_entry(root, UNTESTED) is None
    assert entries(root) == {}
    # The other way: a graded run on the same copy does record.
    check(main_path(root, PASSING))
    assert list(entries(root)) == [f"kata/unit-{PASSING:02d}/{SECTION}"]


def test_a_store_that_cannot_be_written_leaves_the_verdict_standing(root):
    store = Progress(root, depth=1).path
    store.parent.mkdir(parents=True)
    store.write_text("not json", encoding="utf-8")
    checked = check(main_path(root, PASSING))
    assert checked.code == PASSED
    assert any(line.startswith("the run was not recorded: ") for line in checked.lines)
    assert store.read_text(encoding="utf-8") == "not json"
    # The other way: a failing test still fails, recorded or not.
    assert check(main_path(root, FAILING)).code == FAILED


def test_an_interrupted_run_ends_in_the_stopped_line_and_is_recorded_stopped(root):
    class Interrupted:
        returncode = None
        stopped = False

        def lines(self):
            yield "a line before the reader pressed Ctrl-C"
            raise KeyboardInterrupt

        def stop(self):
            Interrupted.stopped = True
            return True

    class Runner:
        def __init__(self, *_):
            pass

        def mode(self):
            return "host"

        def start(self, commands, cwd="."):
            return Interrupted()

    checked = check(main_path(root, PASSING), runner_for=Runner)
    assert Interrupted.stopped is True
    assert checked.code == FAILED
    assert checked.exit_lines() == [exit_line(EXIT_STOPPED)]
    entry = practice_entry(root, PASSING)
    assert entry["last"]["exit"] == EXIT_STOPPED and entry["first_passed_at"] is None


# --------------------------------------------------------------------------
# an argument that is no unit's file is refused by name, and nothing runs
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "practice/passes/check_greet.py",  # a grader, not the file a practice names
        "kata/05-reading.md",  # the reading-only unit's material
        "practice/nowhere.py",  # no file at all
        "pytest.ini",
    ],
)
def test_a_path_that_is_no_units_file_is_refused_by_name_and_nothing_runs(root, path):
    checked = check(str(root / path))
    assert checked.code == UNUSABLE
    assert checked.lines[0].endswith(f"{path}: {NOT_A_UNIT_FILE}")
    assert checked.handed.built == [] and checked.handed.started == []


def test_the_refusal_lists_exactly_the_files_the_corpus_checks(root):
    checked = check(str(root / "pytest.ini"))
    listed = [line.split("checked: ", 1)[1] for line in checked.lines[1:]]
    assert listed == sorted(record(unit).main_path for unit in (*GRADED_UNITS, UNTESTED))


def test_a_file_outside_the_corpus_is_refused(root, tmp_path):
    outside = tmp_path / "elsewhere.py"
    outside.write_text("print('not a unit')\n", encoding="utf-8")
    checked = check(str(outside), "--corpus", str(root))
    assert checked.code == UNUSABLE and NOT_A_UNIT_FILE in checked.lines[0]
    assert checked.handed.started == []


# --------------------------------------------------------------------------
# which corpus
# --------------------------------------------------------------------------


def test_the_corpus_is_found_above_the_file_or_named(root, monkeypatch, tmp_path):
    assert check(main_path(root, PASSING)).handed.built[0][0] == root
    monkeypatch.chdir(root)
    named = check(record(PASSING).main_path, "--corpus", ".")
    assert named.code == PASSED
    assert named.handed.built[0][1] == "studyforge-runner-runnable-demo"


def test_no_corpus_above_the_file_or_at_the_named_root_is_unusable(root, tmp_path):
    stray = tmp_path / "stray"
    stray.mkdir()
    (stray / "x.py").write_text("print(1)\n", encoding="utf-8")
    for argv in ((str(stray / "x.py"),), (main_path(root, PASSING), "--corpus", str(stray))):
        checked = check(*argv)
        assert checked.code == UNUSABLE and "no corpus.json found" in checked.text
        assert checked.handed.started == []
    # The other way: the same file, the right root.
    assert check(main_path(root, PASSING), "--corpus", str(root)).code == PASSED


def test_two_practices_naming_one_file_run_neither(root):
    practice = root / "archive/kata/raw/python/unit-02/practice-1.json"
    text = practice.read_text(encoding="utf-8")
    practice.write_text(
        text.replace(
            '"main_path": "practice/fails/total.py"', f'"main_path": "{record(PASSING).main_path}"'
        ),
        encoding="utf-8",
    )
    checked = check(main_path(root, PASSING))
    assert checked.code == UNUSABLE and "more than one practice" in checked.lines[0]
    assert "kata/unit-01/practice-python" in checked.lines[0]
    assert "kata/unit-02/practice-python" in checked.lines[0]
    assert checked.handed.started == []
    # The other way: a file exactly one practice names is still run.
    assert check(str(root / "practice/broken/area.py")).code == FAILED


def test_a_unit_that_cannot_be_read_is_unusable_and_nothing_runs(root):
    practice = root / "archive/kata/raw/python/unit-02/practice-1.json"
    practice.write_text(
        practice.read_text(encoding="utf-8").replace('"run_command"', '"run_commandd"'),
        encoding="utf-8",
    )
    checked = check(main_path(root, PASSING))
    assert checked.code == UNUSABLE
    assert checked.handed.built == [] and checked.handed.started == []
    assert str(root) not in checked.text
