"""`SF-20`'s acceptance, every clause in BOTH modes — host, and a REAL runner container.

⭐ **Each test is parametrized over the two modes.** Host mode always runs.
Container mode runs when `STUDYFORGE_RUNNER_IMAGE` names the runner image and
Docker is reachable (`container.py`), against a container started with
`code-server-toolchain`'s documented run line over a copy of
`tests/fixtures/runnable/` — ⛔ never a mock. Where it cannot run it SKIPS and
says why.

⭐ **Both modes run over the SAME copy**, the container mounting exactly the
directory the host mode runs in — so *"identical observable behaviour on the
same practice"* compares one tree, not two.

⭐ **Each clause is asserted both ways**: the negative half is either a second
unit of the fixture that must behave the other way, or the runner's own
decision removed in a plant (the environment's two variables).
"""

from __future__ import annotations

import shutil
import time

import pytest

from studyforge.execute import CONTAINER, EXIT_STOPPED, EXIT_TIMEOUT, HOST, Runner, exit_line
from tests.studyforge.execute import container
from tests.studyforge.execute.runnable import (
    FOREIGN_HOME,
    alive,
    fixture_copy,
    gone,
    host_environment_clean,
    observed,
    pids_from,
    plant,
    snapshot,
    unbuffered_removed,
    unit_commands,
)


@pytest.fixture(scope="module")
def stage(tmp_path_factory):
    """One copy of the corpus, and — when the image is named — the reader's container over it."""
    root = fixture_copy(tmp_path_factory.mktemp("sf20"))
    reason = container.skip_reason()
    name = None if reason else container.start(root)
    try:
        yield root, name, reason
    finally:
        if name is not None:
            container.remove(name)


@pytest.fixture(params=[HOST, CONTAINER])
def mode(request, stage, monkeypatch):
    """The mode under test; container mode skips, naming why, when it cannot run."""
    _, name, reason = stage
    if request.param == CONTAINER and name is None:
        pytest.skip(reason)
    host_environment_clean(monkeypatch)
    return request.param


def runner_for(stage, mode: str, **settings) -> Runner:
    """A runner over the stage's root that WILL take `mode` — asserted, not assumed."""
    root, name, _ = stage
    runner = Runner(root, name if mode == CONTAINER else None, **settings)
    assert runner.mode() == mode
    return runner


def run(stage, mode: str, commands, **settings) -> list[str]:
    return list(runner_for(stage, mode, **settings).start(commands).lines())


def exit_lines(lines: list[str]) -> list[str]:
    return [line for line in lines if line.startswith("--- exit ")]


# --- a failing compile stops before tests; the first failure ends the run ----------------


def test_a_file_that_does_not_compile_never_reaches_its_tests(stage, mode):
    lines = run(stage, mode, unit_commands(4))
    assert any("SyntaxError" in line for line in lines)
    assert not any("check_area" in line for line in lines), (
        "the grader ran after the compile failed"
    )
    assert lines[-1] == exit_line(1)


def test_a_file_that_compiles_does_reach_its_tests(stage, mode):
    """The other way: unit 2's run succeeds, so its failing test DOES run."""
    lines = run(stage, mode, unit_commands(2))
    assert any("check_total" in line for line in lines)
    assert lines[-1] == exit_line(1)


def test_a_passing_unit_runs_both_commands_and_exits_zero(stage, mode):
    lines = run(stage, mode, unit_commands(1))
    assert lines[0] == "Hello, reader"
    assert any(line.startswith("1 passed") for line in lines)
    assert lines[-1] == exit_line(0)


def test_a_file_with_no_test_runs_and_is_not_a_failure(stage, mode):
    lines = run(stage, mode, unit_commands(3))
    assert lines == ["Hello from a file with no test", exit_line(0)]


# --- exactly one exit line per run ------------------------------------------------------


@pytest.mark.parametrize("unit", [1, 2, 3, 4])
def test_every_run_ends_in_exactly_one_exit_line(stage, mode, unit):
    lines = run(stage, mode, unit_commands(unit))
    assert len(exit_lines(lines)) == 1
    assert lines[-1] == exit_lines(lines)[0]


# --- a timeout kills the process GROUP and emits the timeout line ------------------------


def test_a_timeout_kills_the_whole_tree_and_says_timeout(stage, mode):
    root, name, _ = stage
    started = time.monotonic()
    lines = run(stage, mode, plant("nap.py"), timeout=2.0, grace=0.5)
    assert time.monotonic() - started < 30
    assert lines[-1] == exit_line(EXIT_TIMEOUT)
    assert len(exit_lines(lines)) == 1
    check = alive if mode == HOST else container.alive_in(name)
    parent, child = pids_from(lines)
    assert gone(check, parent, child), "a process of the run outlived its timeout"


def test_the_tree_check_sees_a_live_tree(stage, mode):
    """The other way: before any timeout, the same instrument reads both pids ALIVE."""
    _, name, _ = stage
    handle = runner_for(stage, mode, timeout=60.0, grace=0.5).start(plant("nap.py"))
    stream = handle.lines()
    parent, child = pids_from([next(stream)])
    check = alive if mode == HOST else container.alive_in(name)
    try:
        assert check(parent) and check(child)
    finally:
        assert handle.stop()
        rest = list(stream)
    assert rest[-1] == exit_line(EXIT_STOPPED)
    assert gone(check, parent, child), "a stopped run left a process behind"


# --- output streams line by line, stdout and stderr merged -------------------------------


def test_output_streams_as_it_is_written(stage, mode):
    stream = runner_for(stage, mode).start(plant("slow.py")).lines()
    started = time.monotonic()
    assert next(stream) == "first"
    assert time.monotonic() - started < 2.5, "the first line waited for the process to end"
    assert list(stream) == ["second", exit_line(0)]


def test_without_the_runners_environment_output_arrives_in_one_lump(stage, mode, monkeypatch):
    unbuffered_removed(monkeypatch)
    stream = runner_for(stage, mode).start(plant("slow.py")).lines()
    started = time.monotonic()
    assert next(stream) == "first"
    assert time.monotonic() - started >= 2.5


def test_stdout_and_stderr_arrive_merged_in_the_order_written(stage, mode):
    lines = run(stage, mode, plant("talk.py"))
    assert lines[:3] == ["out one", "err two", "out three"]


# --- a home path in output is gated; output is relative to the source root ------------


def test_a_home_path_is_gated_and_the_root_prints_relative(stage, mode):
    root, _, _ = stage
    lines = run(stage, mode, plant("talk.py"))
    assert "home /path/to/project/secret.txt" in lines
    assert not any(FOREIGN_HOME in line for line in lines)
    assert "here ." in lines
    assert not any(str(root) in line or "/work" in line for line in lines)


def test_the_argv_arrives_verbatim(stage, mode):
    lines = run(stage, mode, plant("talk.py", "--flag=a:b@c+d", "key=value"))
    assert "argv --flag=a:b@c+d key=value" in lines


# --- both modes identical on the same unit -------------------------------------------


@pytest.mark.parametrize("unit", [1, 2, 3, 4])
def test_both_modes_produce_identical_observable_behaviour(stage, unit, monkeypatch):
    _, name, reason = stage
    if name is None:
        pytest.skip(reason)
    host_environment_clean(monkeypatch)
    host = observed(run(stage, HOST, unit_commands(unit)))
    inside = observed(run(stage, CONTAINER, unit_commands(unit)))
    assert host == inside


def test_the_comparison_can_tell_two_units_apart(stage, mode):
    """The other way: the instrument above is not blind — units 1 and 2 differ."""
    assert observed(run(stage, mode, unit_commands(1))) != observed(
        run(stage, mode, unit_commands(2))
    )


# --- a run leaves the tree as it found it (`W352/3`) ---------------------------------


def test_a_run_writes_no_bytecode_into_the_tree(stage, mode):
    root, _, _ = stage
    before = snapshot(root)
    for unit in (1, 2, 3, 4):
        run(stage, mode, unit_commands(unit))
    assert snapshot(root) == before


def test_without_the_runners_environment_a_grader_run_writes_bytecode(stage, mode, monkeypatch):
    root, _, _ = stage
    monkeypatch.setattr("studyforge.execute.runner.RUN_ENVIRONMENT", {"PYTHONUNBUFFERED": "1"})
    try:
        run(stage, mode, unit_commands(1))
        written = sorted(path.relative_to(root).as_posix() for path in root.rglob("__pycache__"))
        assert written, "the plant did not write bytecode, so the clause above proves nothing"
    finally:
        for path in list(root.rglob("__pycache__")):
            shutil.rmtree(path)


# --- the container is the reader's, and the runner reached it from outside ------------


def test_the_container_is_the_documented_one_offline_and_socketless(stage):
    _, name, reason = stage
    if name is None:
        pytest.skip(reason)
    reported = container.settings(name)
    assert reported.startswith("none "), "the runner container is not --network none"
    assert "docker.sock" not in reported
    assert '"Destination":"/work"' in reported
