"""Mirror of `src/studyforge/execute/runner.py` (R12): the two launchers and what they are handed.

⭐ Container-mode COMPOSITION is read off a fake `docker` that answers the probe
and logs every argv it is given — no daemon, no lock. The real container is
`test_acceptance.py`'s. The kill-by-token program is run for real, on the host,
against real processes, because `/proc` is the same interface in both.
"""

from __future__ import annotations

import ast
import inspect
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from studyforge import execute
from studyforge.execute import (
    CONTAINER,
    HOST,
    RUN_ENVIRONMENT,
    RUNNER_DOWN,
    Runner,
    RunRefused,
    exit_line,
)
from studyforge.execute import runner as runner_module
from studyforge.execute.handle import KILL, STOP
from studyforge.execute.runner import KILL_BY_TOKEN, MERGE_STDERR, RUN_TOKEN
from tests.studyforge.execute.runnable import alive, gone
from tests.studyforge.execute.test_mode import answer, calls, fake_docker, up

NAME = "studyforge-runner-kata"


@pytest.fixture
def root(tmp_path) -> Path:
    corpus = tmp_path / "corpus"
    (corpus / "practice").mkdir(parents=True)
    return corpus


def container_runner(tmp_path, root, **settings) -> Runner:
    docker = fake_docker(tmp_path, up(root))
    runner = Runner(root, NAME, docker=str(docker), **settings)
    assert runner.mode() == CONTAINER
    return runner


def execs(tmp_path) -> list[list[str]]:
    return [call.split(" ") for call in calls(tmp_path) if call.startswith("exec ")]


def test_container_mode_is_docker_exec_with_the_argv_verbatim_and_last(tmp_path, root):
    list(
        container_runner(tmp_path, root)
        .start([["python3", "-m", "pytest", "-q"]], "practice")
        .lines()
    )
    (argv,) = execs(tmp_path)
    assert argv[:3] == ["exec", "-w", "/work/practice"]
    at = argv.index(NAME)
    assert argv[at + 1 : at + 3] == ["sh", "-c"]
    assert argv[at + 3 + len(MERGE_STDERR.split(" ")) :] == ["sh", "python3", "-m", "pytest", "-q"]
    for key, value in RUN_ENVIRONMENT.items():
        assert f"{key}={value}" in argv
    assert any(part.startswith(f"{RUN_TOKEN}=") for part in argv)


def test_the_root_directory_is_work_itself(tmp_path, root):
    list(container_runner(tmp_path, root).start([["python3", "x.py"]]).lines())
    assert execs(tmp_path)[0][:3] == ["exec", "-w", "/work"]


def test_container_mode_never_runs_start_stop_build_or_a_mount(tmp_path, root):
    runner = container_runner(tmp_path, root)
    list(runner.start([["python3", "x.py"]]).lines())
    verbs = {call.split(" ")[0] for call in calls(tmp_path)}
    assert verbs == {"inspect", "exec"}
    assert not any("docker.sock" in call or " -v " in call for call in calls(tmp_path))


def test_a_stop_reaches_into_the_container_by_its_token(tmp_path, root):
    runner = container_runner(tmp_path, root, grace=0.2)
    handle = runner.start([["python3", "x.py"]])
    deadline = time.monotonic() + 10
    while not execs(tmp_path) and time.monotonic() < deadline:
        time.sleep(0.05)
    token = next(part for part in execs(tmp_path)[0] if part.startswith(f"{RUN_TOKEN}="))
    handle.stop()
    list(handle.lines())
    kills = [argv for argv in execs(tmp_path) if argv[1] == NAME]
    assert kills, "a stop did not reach into the container"
    assert all(argv[1:4] == [NAME, "sh", "-c"] and token in argv for argv in kills)
    assert {argv[-1] for argv in kills} <= {"TERM", "KILL"}


def test_host_mode_runs_in_the_directory_named_relative_to_the_root(root):
    (root / "practice" / "where.py").write_text("import os; print(os.getcwd())\n", encoding="utf-8")
    lines = list(Runner(root).start([["python3", "where.py"]], "practice").lines())
    assert lines == ["practice", exit_line(0)]


def test_host_mode_carries_the_run_environment(root, monkeypatch):
    for key in RUN_ENVIRONMENT:
        monkeypatch.delenv(key, raising=False)
    (root / "env.py").write_text(
        "import os\n"
        + "".join(f"print(os.environ.get({key!r}))\n" for key in sorted(RUN_ENVIRONMENT)),
        encoding="utf-8",
    )
    lines = list(Runner(root).start([["python3", "env.py"]]).lines())
    assert lines[:-1] == [RUN_ENVIRONMENT[key] for key in sorted(RUN_ENVIRONMENT)]


def test_a_required_runner_that_is_down_refuses_and_never_runs_on_the_host(tmp_path, root):
    # ⛔ A corpus that declares its runner: its code runs there or nowhere.
    docker = fake_docker(tmp_path, answer("false"))
    planted = root / "planted"
    runner = Runner(root, NAME, docker=str(docker), required=True)
    with pytest.raises(RunRefused) as refused:
        runner.mode()
    assert str(refused.value) == RUNNER_DOWN
    with pytest.raises(RunRefused):
        runner.start([["touch", "planted"]])
    assert not planted.exists(), "a declared runner's run fell back to the host"


def test_a_required_runner_that_is_up_runs_in_it(tmp_path, root):
    docker = fake_docker(tmp_path, up(root))
    assert Runner(root, NAME, docker=str(docker), required=True).mode() == CONTAINER


def test_a_runner_not_required_still_falls_back_to_the_host(tmp_path, root):
    # ⭐ Only a corpus that declares no runner: the host is its one place to run.
    docker = fake_docker(tmp_path, answer("false"))
    assert Runner(root, NAME, docker=str(docker)).mode() == HOST


def test_no_container_named_is_host_mode(root):
    assert Runner(root).mode() == HOST


@pytest.mark.parametrize(
    ("commands", "cwd"),
    [("python3 x.py", "."), ([["python3", "x.py;id"]], "."), ([["python3", "x.py"]], "/tmp")],
)
def test_a_refused_run_starts_nothing_and_asks_nothing(tmp_path, root, commands, cwd):
    docker = fake_docker(tmp_path, up(root))
    with pytest.raises(RunRefused):
        Runner(root, NAME, docker=str(docker)).start(commands, cwd)
    assert calls(tmp_path) == []


def test_a_container_name_that_is_not_one_word_is_refused_at_construction(root):
    with pytest.raises(RunRefused):
        Runner(root, "a; docker run")


def test_start_takes_commands_and_a_directory_and_nothing_else():
    assert list(inspect.signature(Runner.start).parameters) == ["self", "commands", "cwd"]


def test_no_module_of_the_package_starts_anything_through_a_shell():
    for path in Path(execute.__file__).parent.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.keyword) and node.arg == "shell":
                pytest.fail(f"{path.name} passes shell=")
            if isinstance(node, ast.Attribute) and node.attr in {"system", "popen"}:
                pytest.fail(f"{path.name} calls os.{node.attr}")


def test_the_shell_detector_is_not_blind():
    planted = ast.parse("import subprocess\nsubprocess.run('x', shell=True)\n")
    assert any(isinstance(node, ast.keyword) and node.arg == "shell" for node in ast.walk(planted))


def _marked(marker: str | None) -> subprocess.Popen:
    env = {**os.environ}
    if marker:
        env[RUN_TOKEN] = marker
    return subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], env=env)


def test_the_kill_program_signals_every_process_carrying_the_token_and_no_other():
    ours, theirs = _marked("abc123"), _marked("zzz999")
    try:
        subprocess.run(
            ["sh", "-c", KILL_BY_TOKEN, "sh", f"{RUN_TOKEN}=abc123", "KILL"], check=True, timeout=10
        )
        assert ours.wait(timeout=10) != 0
        assert not gone(alive, theirs.pid, within=0.5)
    finally:
        theirs.kill()
        theirs.wait()


def test_the_merge_program_keeps_the_order_written_and_the_argv_verbatim():
    program = (
        "import sys; print('a', flush=True); print('b', file=sys.stderr, flush=True); print('c')"
    )
    merged = subprocess.run(
        ["sh", "-c", MERGE_STDERR, "sh", sys.executable, "-c", program],
        capture_output=True,
        text=True,
        check=True,
    )
    assert merged.stdout.splitlines() == ["a", "b", "c"]
    assert merged.stderr == ""


def test_without_the_merge_program_stderr_takes_its_own_stream():
    program = "import sys; print('b', file=sys.stderr)"
    apart = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True)
    assert apart.stdout == "" and apart.stderr == "b\n"


# ---------------------------------------------------------------------------
# ⭐ Windows has no `killpg`, no session and no `SIGKILL`. These read the Windows
# path on any host by setting `os.name`, with fake processes: nothing is started.


class Leader:
    """A started command's stand-in: records what it is sent."""

    pid = 4242

    def __init__(self, alive: bool = True) -> None:
        self.alive = alive
        self.sent: list[object] = []

    def poll(self):
        return None if self.alive else 0

    def send_signal(self, signum) -> None:
        self.sent.append(("signal", signum))

    def kill(self) -> None:
        self.sent.append(("kill", None))


@pytest.fixture
def windows(monkeypatch):
    """This host as Windows: `os.name` is `nt`, and there is no `killpg` to call."""
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.delattr(os, "killpg", raising=False)
    ran: list[list[str]] = []
    monkeypatch.setattr(
        runner_module.subprocess,
        "run",
        lambda argv, **_: ran.append(list(argv)) or subprocess.CompletedProcess(argv, 0),
    )
    return ran


def test_on_windows_a_command_leads_a_new_process_group_not_a_session(windows):
    assert runner_module._own_group() == {"creationflags": 0x00000200}


def test_on_posix_a_command_leads_a_new_session():
    assert runner_module._own_group() == {"start_new_session": True}


def test_on_windows_a_stop_is_a_console_break_to_the_group(windows):
    leader = Leader()
    runner_module._signal_group(leader, STOP)
    assert leader.sent == [("signal", runner_module.CTRL_BREAK)]
    assert windows == []


def test_on_windows_a_kill_ends_the_whole_tree_then_the_leader(windows):
    leader = Leader()
    runner_module._signal_group(leader, KILL)
    assert windows == [["taskkill", "/T", "/F", "/PID", str(Leader.pid)]]
    assert leader.sent == [("kill", None)]


def test_on_windows_a_leader_already_gone_is_sent_no_break(windows):
    leader = Leader(alive=False)
    runner_module._signal_group(leader, STOP)
    assert leader.sent == []


def test_the_container_stop_names_its_signal_without_posix_names(tmp_path, root, monkeypatch):
    """⛔ `signal.Signals(9)` does not exist on Windows; the name is the launcher's own."""
    launcher = runner_module.ContainerLauncher(NAME, ".", docker=str(fake_docker(tmp_path, "")))
    monkeypatch.setattr(runner_module, "_signal_group", lambda *_: None)
    monkeypatch.delattr(runner_module.signal, "Signals")
    launcher.signal(Leader(), KILL)
    launcher.signal(Leader(), STOP)
    stops = [call.split(" ")[-1] for call in calls(tmp_path) if call.startswith("exec ")]
    assert stops == ["KILL", "TERM"]


def test_a_stop_sends_stop_then_kill_on_a_host_with_no_sigkill(tmp_path, monkeypatch):
    """⛔ Windows' `signal` has no `SIGKILL`: a stop must not reach for it."""
    monkeypatch.delattr(runner_module.signal, "SIGKILL")
    sent: list[int] = []

    class Recording(execute.runner.HostLauncher):
        def signal(self, process, signum):
            sent.append(signum)
            super().signal(process, signum)

    handle = execute.RunHandle(
        [[sys.executable, "-c", "import time; time.sleep(60)"]],
        Recording(tmp_path, "."),
        execute.LineGate([]),
        mode=HOST,
        timeout=30.0,
        grace=0.2,
    )
    lines = handle.lines()
    time.sleep(0.3)
    assert handle.stop()
    assert list(lines)[-1] == exit_line("stopped")
    assert sent[:2] == [STOP, KILL]
