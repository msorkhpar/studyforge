"""Mirror of `src/studyforge/execute/remote.py` (R12), and of the run service it speaks to.

⭐ The service is the real one (`assets/runservice.pl`), run on the host under
`perl` against a scratch work directory on a loopback port, because the wire,
the allowlist and the kill-by-token are the same code in the runner. ⭐ A
`Runner` given that service is then read end to end: its runs, its refusals,
its stop, and that it never falls back to the host.
"""

from __future__ import annotations

import os
import re
import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from studyforge.execute import (
    ALLOWED_FILE,
    SERVICE,
    Runner,
    RunRefused,
    Service,
    exit_line,
    write_allowed,
)
from studyforge.execute.remote import RemoteProcess, ServiceProbe, fresh_token, request
from tests.studyforge.execute.runservice import NEEDS_PERL, run_service

pytestmark = NEEDS_PERL

#: A program that writes to both streams and exits with a status of its own.
TALK = "echo out\necho err >&2\nexit 3\n"


@pytest.fixture
def work(tmp_path) -> Path:
    root = tmp_path / "work"
    root.mkdir()
    (root / "talk.sh").write_text(TALK, encoding="utf-8")
    (root / "sub").mkdir()
    (root / "sub" / "here.sh").write_text("pwd\n", encoding="utf-8")
    return root


@pytest.fixture
def service(work) -> Iterator[Service]:
    with run_service(work) as started:
        yield started


def allow(work: Path, *argv: list[str], cwd: str = ".") -> None:
    write_allowed(work, [(cwd, one) for one in argv])


def lines(runner: Runner, argv: list[str], cwd: str = ".") -> list[str]:
    return [line.rstrip("\n") for line in runner.start([argv], cwd).lines()]


def test_a_request_is_nul_framed_and_a_nul_in_a_field_is_refused():
    assert request("run", "t", ".", "sh", "a b") == b"run\x00t\x00.\x00sh\x00a b\x00\x00"
    with pytest.raises(RunRefused):
        request("run", "t", ".", "sh\x00-c")


def test_a_token_is_the_run_variable_and_32_hex():
    assert re.fullmatch(r"STUDYFORGE_RUN=[0-9a-f]{32}", fresh_token())


def test_frames_decode_to_lines_and_the_status_is_the_last_frame():
    ours, theirs = socket.socketpair()
    theirs.sendall(b"O9\nfirst\nsec" + b"O4\nond\n" + b"X7\n")
    theirs.close()
    process = RemoteProcess(ours)
    assert [process.readline(), process.readline(), process.readline()] == [
        "first\n",
        "second\n",
        "",
    ]
    assert process.wait(0) == 7


def test_a_service_that_hangs_up_mid_run_is_a_lost_run_not_a_hang():
    ours, theirs = socket.socketpair()
    theirs.sendall(b"O3\nhi\n")
    theirs.close()
    process = RemoteProcess(ours)
    assert process.readline() == "hi\n"
    assert process.readline() == ""
    assert process.wait(0) == 255


def test_waiting_on_a_live_run_times_out_as_a_process_does():
    ours, theirs = socket.socketpair()
    with pytest.raises(subprocess.TimeoutExpired):
        RemoteProcess(ours).wait(0.05)
    theirs.close()


def test_an_allowed_argv_runs_in_the_service_with_both_streams_and_its_status(work, service):
    allow(work, ["sh", "talk.sh"])
    runner = Runner(work, service=service)
    assert runner.mode() == SERVICE
    assert lines(runner, ["sh", "talk.sh"]) == ["out", "err", exit_line(3)]


def test_the_directory_is_relative_to_the_work_root(work, service):
    allow(work, ["sh", "here.sh"], cwd="sub")
    assert lines(Runner(work, service=service), ["sh", "here.sh"], "sub") == [
        str(work / "sub"),
        exit_line(0),
    ]


def test_an_argv_the_records_do_not_name_is_refused_and_nothing_runs(work, service):
    allow(work, ["sh", "talk.sh"])
    planted = work / "planted"
    got = lines(Runner(work, service=service), ["touch", "planted"])
    assert got == ["run service: this argv is not one the corpus's records name", exit_line(126)]
    assert not planted.exists()


def test_an_allowed_argv_in_another_directory_is_refused(work, service):
    allow(work, ["sh", "here.sh"], cwd="sub")
    got = lines(Runner(work, service=service), ["sh", "here.sh"])
    assert got[-1] == exit_line(126)


def test_no_allowlist_at_all_runs_nothing(work, service):
    assert not (work / ALLOWED_FILE).exists()
    assert lines(Runner(work, service=service), ["sh", "talk.sh"])[-1] == exit_line(126)


def test_a_directory_that_climbs_out_is_refused_by_the_service(work, service):
    allow(work, ["sh", "talk.sh"], cwd="..")
    with socket.create_connection((service.host, service.port)) as raw:
        raw.sendall(request("run", fresh_token(), "..", "sh", "talk.sh"))
        answer = raw.makefile("rb").read()
    assert answer.endswith(b"X126\n") and b"never climbs out" in answer


def test_a_stop_ends_the_run_and_every_process_it_started(work, service):
    (work / "long.sh").write_text("sleep 30 & sleep 30\n", encoding="utf-8")
    allow(work, ["sh", "long.sh"])
    handle = Runner(work, service=service, grace=2).start([["sh", "long.sh"]])
    time.sleep(0.5)
    began = time.monotonic()
    assert handle.stop()
    assert list(handle.lines())[-1] == exit_line("stopped")
    assert time.monotonic() - began < 5
    mine = [pid for pid in _sleeping() if _in(work, pid)]
    assert mine == [], "a stopped run left a process behind"


def test_a_service_that_is_not_answering_refuses_the_run_and_never_runs_on_the_host(work):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    runner = Runner(work, service=Service("127.0.0.1", port))
    with pytest.raises(RunRefused, match="not answering"):
        runner.mode()
    with pytest.raises(RunRefused):
        runner.start([["sh", "talk.sh"]])


def test_the_probe_is_believed_for_its_ttl(work, service):
    probe = ServiceProbe(service, ttl=60)
    assert probe.up()
    probe.service = Service("127.0.0.1", 1)
    assert probe.up(), "an answer inside its TTL is believed, not asked again"


def _sleeping() -> list[str]:
    """Every process whose command line is `sleep 30`, read off `/proc` (no `pgrep` needed)."""
    found = []
    for entry in Path("/proc").iterdir():
        try:
            if entry.name.isdigit() and (entry / "cmdline").read_bytes() == b"sleep\x0030\x00":
                found.append(entry.name)
        except OSError:
            continue
    return found


def _in(work: Path, pid: str) -> bool:
    try:
        return os.readlink(f"/proc/{pid}/cwd").startswith(str(work))
    except OSError:
        return False
