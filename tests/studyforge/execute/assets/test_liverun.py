"""Mirror of `src/studyforge/execute/assets/liverun.pl` (R12): the live runner, run for real.

⭐ The shipped Perl script is started on this machine, listening on an ephemeral loopback port, with
a corpus directory it runs the declared programs from, and driven over its own wire by
`execute.live`. What is read is what it does with a FAKE key (`sk-test-` and random hex): where the
key is and is not while a run lasts and after it, and how a run ends. ⛔ No real key, no API.

The container-level readings (hardening, the networks, the graded runner beside it) are
`test_live_compose_image.py`'s.
"""

from __future__ import annotations

import base64
import os
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
from pathlib import Path

import pytest

import studyforge.execute as execute
from studyforge.execute import Service, start_live, write_allowed
from studyforge.execute.remote import NUL, request
from tests.studyforge.execute import leakscan

SCRIPT = Path(execute.__file__).parent / "assets" / "liverun.pl"
NAME = "EXAMPLE_API_KEY"
PYTHON = sys.executable

PROGRAMS = {
    "check_env.py": (
        "import os\nvalue = os.environ.get('EXAMPLE_API_KEY', '')\n"
        "print('has key:', bool(value), 'length', len(value))\n"
        "print('token marked:', any(k == 'STUDYFORGE_RUN' for k in os.environ))\n"
    ),
    "echo_key.py": (
        "import base64, os, sys, urllib.parse\nkey = os.environ['EXAMPLE_API_KEY']\n"
        "print('raw ' + key)\nprint('url ' + urllib.parse.quote(key, safe=''))\n"
        "print('b64 ' + base64.b64encode(key.encode()).decode())\n"
        "print('basic ' + base64.b64encode(('user:' + key).encode()).decode())\n"
        "print('hdr Authorization: Bearer ' + key)\nsys.stderr.write('err ' + key + '\\n')\n"
    ),
    "split_key.py": (
        "import os, sys, time\nkey = os.environ['EXAMPLE_API_KEY']\n"
        "for part in (key[:5], key[5:11], key[11:]):\n"
        "    sys.stdout.write(part); sys.stdout.flush(); time.sleep(0.15)\n"
        "print()\n"
    ),
    "sleep.py": "import time\nprint('started', flush=True)\ntime.sleep(60)\n",
    "spam.py": "import sys\nwhile True:\n    sys.stdout.write('x' * 500 + '\\n'); sys.stdout.flush()\n",
    "writes.py": (
        "import os, pathlib\nkey = os.environ['EXAMPLE_API_KEY']\n"
        "for target in ('probe.txt', '.studyforge/execution/probe.txt'):\n"
        "    try:\n        pathlib.Path(target).write_text(key)\n        print('wrote', target)\n"
        "    except OSError as error:\n        print('refused', target)\n"
    ),
    "crash.py": "import os\nkey = os.environ['EXAMPLE_API_KEY']\nraise RuntimeError('boom')\n",
}


def fake() -> str:
    return "sk-test-" + secrets.token_hex(12)


class Live:
    """The running service, the corpus it works from, and what it said on stderr."""

    def __init__(self, tmp: Path, **environment: str) -> None:
        self.work = tmp / "work"
        self.scratch = tmp / "scratch"
        self.work.mkdir()
        self.scratch.mkdir()
        for name, text in PROGRAMS.items():
            (self.work / name).write_text(text, encoding="utf-8")
        self.entries = [(".", [PYTHON, name]) for name in PROGRAMS]
        write_allowed(self.work, self.entries, "live")
        # ⛔ The service's own environment has no key: it holds the variable's NAME only.
        env = {
            "PATH": os.environ["PATH"], "STUDYFORGE_RUN_WORK": str(self.work),
            "STUDYFORGE_LIVE_BIND": "127.0.0.1", "STUDYFORGE_LIVE_PORT": "0",
            "STUDYFORGE_LIVE_KEY_NAME": NAME, "STUDYFORGE_LIVE_LOCK": str(self.scratch / "lock"),
            "HOME": str(self.scratch), "TMPDIR": str(self.scratch), **environment,
        }
        self.log = tmp / "service.log"
        self.process = subprocess.Popen(  # noqa: S603 - the shipped script, a fixed argv
            ["perl", str(SCRIPT)], env=env, stdin=subprocess.DEVNULL,
            stdout=self.log.open("wb"), stderr=subprocess.STDOUT,
        )
        self.port = self._port()
        self.service = Service("127.0.0.1", self.port)

    def _port(self) -> int:
        for _ in range(100):
            text = self.log.read_text(encoding="utf-8", errors="replace")
            if "listening on" in text:
                return int(text.rsplit("listening on", 1)[1].split()[0])
            time.sleep(0.05)
        raise AssertionError(f"the live runner did not start: {text}")

    def run(self, program: str, key: str, **options) -> list[str]:
        return list(start_live(self.service, [PYTHON, program], key, **options).lines())

    def stop(self) -> None:
        self.process.kill()
        self.process.wait()


@pytest.fixture
def live(tmp_path):
    made = Live(tmp_path)
    yield made
    made.stop()


def exchange(service: Service, *fields: str, kind: str = "live") -> bytes:
    """Send one raw request and read the whole answer."""
    with socket.create_connection((service.host, service.port), 5) as connection:
        connection.sendall(request(kind, *fields))
        data = b""
        while chunk := connection.recv(4096):
            data += chunk
    return data


def texts(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def test_the_key_is_in_the_environment_of_the_one_process_it_was_given_to(live):
    secret = fake()
    out = texts(live.run("check_env.py", secret))
    assert f"has key: True length {len(secret)}" in out and "token marked: True" in out
    assert out.endswith("--- exit 0 ---\n")


def test_the_service_itself_holds_no_key_and_no_file_or_log_holds_one_after_a_run(live, tmp_path):
    secret = fake()
    live.run("check_env.py", secret)
    live.run("echo_key.py", secret)
    # ⭐ The service's environment names the variable (a value of `STUDYFORGE_LIVE_KEY_NAME`) and
    # never holds it: no entry of it is `EXAMPLE_API_KEY=`.
    assert f"{NAME}=" not in Path(f"/proc/{live.process.pid}/environ").read_bytes().decode()
    assert leakscan.in_tree(tmp_path, secret) == []
    assert not leakscan.in_bytes(live.log.read_bytes(), secret)


def test_while_a_run_lasts_the_key_is_in_one_process_environment_and_no_command_line(live):
    secret = fake()
    seen: list = []

    def during():
        time.sleep(1.0)
        seen.append(leakscan.in_processes(secret))
        live_stop = request("stop", token[0], "KILL")
        with socket.create_connection((live.service.host, live.service.port), 5) as c:
            c.sendall(live_stop)
            c.recv(16)

    handle = start_live(live.service, [PYTHON, "sleep.py"], secret)
    token = [handle._launcher.marker]
    threading.Thread(target=during, daemon=True).start()
    out = texts(list(handle.lines()))
    assert "started" in out
    (found,) = seen
    assert [what for _, what in found] == ["environ"], found
    assert not any(what == "cmdline" for _, what in found)


@pytest.mark.parametrize("program", ["echo_key.py", "split_key.py"])
def test_what_the_program_prints_of_its_key_is_replaced_before_it_leaves(live, program):
    secret = fake()
    out = texts(live.run(program, secret))
    assert not leakscan.in_bytes(out.encode(), secret) or all(
        # a character or two at the ends of a key inside a longer encoding may remain (stated)
        form not in out.encode() for form in (secret.encode(), urllib.parse.quote(secret).encode())
    )
    assert secret not in out and base64.b64encode(secret.encode()).decode() not in out
    assert "[redacted]" in out


def test_a_key_printed_in_chunks_that_split_it_is_still_replaced(live):
    secret = fake()
    out = texts(live.run("split_key.py", secret))
    assert secret not in out and out.startswith("[redacted]")


def test_every_encoding_the_program_prints_of_the_whole_key_is_gone(live):
    secret = fake()
    out = texts(live.run("echo_key.py", secret))
    lines = dict(line.split(" ", 1) for line in out.splitlines() if " " in line)
    assert lines["raw"] == "[redacted]" and lines["url"] == "[redacted]" and lines["b64"] == "[redacted]"
    assert secret not in out and "Bearer " + secret not in out
    # ⭐ Judged by the scan helper's own spelling of the forms, not the runner's: a key inside a
    # longer base64 text (`basic`) is found and replaced too.
    assert leakscan.in_bytes(out.encode(), secret) == []
    assert lines["basic"].startswith("dXNlcjp") and "[redacted]" in lines["basic"]


def test_the_run_writes_where_the_corpus_allows_and_the_key_is_in_no_file(live, tmp_path):
    secret = fake()
    live.run("writes.py", secret)
    # the host stand-in does not mount read-only (the container proof does); the key is in no file
    # the service itself made, and none of the service's own paths
    assert not leakscan.in_bytes(live.log.read_bytes(), secret)
    assert not [one for one in leakscan.in_tree(live.scratch, secret)]


def test_a_program_that_cannot_be_started_says_so_without_the_key(live):
    missing = "/no/such/program"
    write_allowed(live.work, [*live.entries, (".", [missing])], "live")
    secret = fake()
    out = texts(list(start_live(live.service, [missing], secret).lines()))
    assert "could not be started" in out and not leakscan.in_bytes(out.encode(), secret)
    with open(live.log, "rb") as log:
        assert not leakscan.in_bytes(log.read(), secret)


def test_a_crash_prints_a_trace_that_carries_no_key(live):
    secret = fake()
    out = texts(live.run("crash.py", secret))
    assert "RuntimeError: boom" in out and secret not in out and out.endswith("--- exit 1 ---\n")


@pytest.mark.parametrize("kind", ["run", "ping2", "exec", ""])
def test_a_verb_other_than_live_stop_and_ping_is_refused(live, kind):
    answer = exchange(live.service, "STUDYFORGE_RUN=" + "0" * 32, ".", PYTHON, "check_env.py", kind=kind)
    assert b"X126" in answer and b"live requests only" in answer


def test_the_graded_verb_is_never_accepted_and_ping_answers(live):
    assert exchange(live.service, kind="ping").startswith(b"pong")
    answer = exchange(live.service, "STUDYFORGE_RUN=" + "1" * 32, ".", PYTHON, "check_env.py", kind="run")
    assert b"X126" in answer


@pytest.mark.parametrize(
    "key",
    ["", "short", "x" * 300, "has space" + "a" * 9, "nl\n" + "a" * 9, "q'uote" + "a" * 9, "$(x)" + "a" * 9],
)
def test_a_key_of_the_wrong_shape_is_refused_and_never_echoed_by_the_service(live, key):
    token = "STUDYFORGE_RUN=" + "2" * 32
    fields = [token, ".", key, PYTHON, "check_env.py"]
    if "\x00" in key:
        pytest.skip("a NUL cannot be framed")
    answer = exchange(live.service, *fields)
    assert b"X126" in answer and b"does not accept" not in answer or b"form a live run accepts" in answer
    assert key == "" or key.encode() not in answer


def test_an_argv_the_corpus_did_not_declare_live_is_refused(live):
    secret = fake()
    answer = exchange(
        live.service, "STUDYFORGE_RUN=" + "3" * 32, ".", secret, PYTHON, "-c", "print(1)"
    )
    assert b"X126" in answer and b"not one the corpus" in answer and secret.encode() not in answer


@pytest.mark.parametrize("cwd", ["/etc", "..", "a/../..", "a//b", "./x"])
def test_a_directory_that_climbs_or_is_not_clean_is_refused(live, cwd):
    answer = exchange(live.service, "STUDYFORGE_RUN=" + "4" * 32, cwd, fake(), PYTHON, "check_env.py")
    assert b"X126" in answer


def test_a_second_live_run_while_one_goes_is_refused(live):
    handle = start_live(live.service, [PYTHON, "sleep.py"], fake())
    iterator = handle.lines()
    next(iterator)
    second = texts(live.run("check_env.py", fake()))
    handle.stop()
    list(iterator)
    assert "already going" in second


def test_a_run_past_its_time_limit_is_killed_and_nothing_of_it_remains(tmp_path):
    service = Live(tmp_path, STUDYFORGE_LIVE_TIMEOUT="2")
    try:
        out = texts(service.run("sleep.py", fake()))
        assert "time limit" in out and out.endswith("--- exit 124 ---\n")
        time.sleep(0.5)
        assert not leftover("sleep.py")
    finally:
        service.stop()


def test_a_run_that_prints_past_its_output_limit_is_stopped(tmp_path):
    service = Live(tmp_path, STUDYFORGE_LIVE_MAX_OUTPUT="5000")
    try:
        out = texts(service.run("spam.py", fake()))
        assert "output limit" in out and len(out) < 200_000
        time.sleep(0.5)
        assert not leftover("spam.py")
    finally:
        service.stop()


def test_a_client_that_hangs_up_ends_the_run_and_its_process_group(live):
    handle = start_live(live.service, [PYTHON, "sleep.py"], fake())
    iterator = handle.lines()
    next(iterator)
    assert leftover("sleep.py")
    handle._launcher.signal(handle._process, 9)
    for _ in range(40):
        if not leftover("sleep.py"):
            break
        time.sleep(0.1)
    assert not leftover("sleep.py")
    list(iterator)


def test_a_normal_end_leaves_no_process_of_the_run(live):
    live.run("check_env.py", fake())
    time.sleep(0.3)
    assert not leftover("check_env.py")


def test_the_shipped_script_reads_the_key_variable_name_and_never_a_key_from_its_environment():
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.count("$ENV{$NAME} = $key") == 1
    assert "$ENV{STUDYFORGE_LIVE_KEY_NAME}" in text
    assert "ANTHROPIC" not in text and "sk-" not in text
    assert text.count("print STDERR") == 2  # its listening line, and a program that cannot start
    assert shutil.which("perl")


def leftover(program: str) -> list[int]:
    """The pids of live processes running `program` of this test's corpus."""
    found = []
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                line = (entry / "cmdline").read_bytes().split(NUL)
            except OSError:
                continue
            if PYTHON.encode() in line[:1] and program.encode() in line[1:2]:
                found.append(int(entry.name))
    return found
