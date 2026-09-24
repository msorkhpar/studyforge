"""The `serve` verb as a real process: started as a reader starts it, stopped as a reader stops it.

⛔ **Spec §8.3's runtime arm lives here.** The process is started with `DOCKER_HOST`
naming a real, listening socket called `docker.sock` in a harness-minted directory —
a socket the process CAN reach — and afterwards that socket must have accepted
nothing, and no descriptor the process held may name it.

⛔ **One reader of the process's output**: `tests.support.ProcessOutput`,
from launch to exit. So every line the verb printed is asserted, not only the last.
"""

from __future__ import annotations

import ast
import contextlib
import inspect
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
from dataclasses import dataclass
from urllib.parse import quote

import pytest

from studyforge.cli.serve import STOPPED
from studyforge.generate.declarations import read_corpus
from studyforge.validate.report import OK
from tests.fixture_checks import FIXTURES
from tests.studyforge.cli.serving import (
    LISTENING,
    NAMES,
    Address,
    build,
    pages_of,
    served_page,
)
from tests.studyforge.serve.built import source_of
from tests.studyforge.serve.serving import fetch
from tests.support import ProcessOutput, repository_root, tracked_files

#: One line of the verb's request log: the method, the path and the status.
REQUEST = re.compile(r'^127\.0\.0\.1 "(\w+) (\S+) HTTP/1\.1" (\d{3}) ', re.M)


@dataclass
class Running:
    """A serving process, the address it printed, and the one reader of its output."""

    process: subprocess.Popen
    server: Address
    output: ProcessOutput

    def stopped(self, how: int = signal.SIGINT) -> tuple[int, str, str]:
        """Signal the process; return `(exit code, stdout, stderr)`, each read to its end.

        ⭐ `stdout` is everything the process printed, the listening line included.
        """
        self.process.send_signal(how)
        stdout, stderr = self.output.rest(timeout=30)
        return self.process.wait(timeout=30), stdout, stderr


@contextlib.contextmanager
def launched(root, site, environment=None):
    """`python3 -m studyforge.cli serve …` on port `0`; yield it once it is listening.

    ⭐ `site=None` is the no-configured-path form (`W230`): the root and a port only.
    """
    chosen = [] if site is None else ["--site", str(site)]
    with subprocess.Popen(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.cli", "serve", str(root), *chosen, "--port", "0"],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src", **(environment or {})},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        output = ProcessOutput(process)
        try:
            first = output.line(timeout=30)
            found = LISTENING.match(first)
            if found is None:
                process.kill()
                _, stderr = output.rest(timeout=10)
                pytest.fail(f"the verb did not start listening: {first!r} {stderr[-400:]!r}")
            yield Running(process, Address(int(found.group(1))), output)
        finally:
            if process.poll() is None:
                process.kill()
                output.rest(timeout=10)


def printed(running: Running, stdout: str, requested: list[str]) -> list[str]:
    """Assert the lines around the ones a test reads; return the lines in between.

    ⛔ The listening line FIRST, naming the port a caller read, and `stopped` LAST.
    ⭐ Between them, one request line per path fetched, in order, each answered `200`.
    """
    lines = stdout.splitlines()
    assert lines, "the process printed nothing, so there is no transcript to read"
    found = LISTENING.match(lines[0])
    assert found, f"the first line printed is not the listening line: {lines[0]!r}"
    assert int(found.group(1)) == running.server.server_address[1]
    assert lines[-1] == STOPPED
    assert REQUEST.findall(stdout) == [("GET", path, "200") for path in requested]
    return lines[1:-1]


@pytest.mark.parametrize("name", NAMES)
def test_the_installed_command_serves_each_fixture_and_stops_on_interrupt(name, tmp_path):
    root, site = build(name, tmp_path)
    with launched(root, site) as running:
        index = fetch(running.server, "/index.html")
        toc = fetch(running.server, "/api/v1/content/toc")
        code, stdout, stderr = running.stopped()
    assert (index[0], index[2]) == (200, served_page((site / "index.html").read_bytes()))
    assert toc[0] == 200
    assert code == OK, stderr[-400:]
    printed(running, stdout, ["/index.html", "/api/v1/content/toc"])
    assert "Traceback" not in stdout + stderr


def test_a_terminate_signal_stops_it_cleanly_too(tmp_path):
    root, site = build("depth1", tmp_path)
    with launched(root, site) as running:
        assert fetch(running.server, "/index.html")[0] == 200
        code, stdout, stderr = running.stopped(signal.SIGTERM)
    assert code == OK, stderr[-400:]
    printed(running, stdout, ["/index.html"])
    assert "Traceback" not in stdout + stderr


#: Every test that reads a running child's output. `None` holds the whole module;
#: names hold only those tests, because a neighbour shows a THREAD blocked with an `Event`.
READERS = {
    "tests/studyforge/cli/test_serve_process.py": None,
    "tests/studyforge/skills/buildserve/test_main.py": None,
    "tests/studyforge/progress/test_lock.py": (
        "test_a_second_process_waits_until_the_lock_is_released",
    ),
    "tests/studyforge/progress/test_store.py": (
        "test_a_second_process_writing_during_an_update_loses_nothing",
    ),
}

#: A wait on a clock, in each spelling a stand-in takes, and the second reader.
AROUND_THE_READER = frozenset({"sleep", "monotonic", "perf_counter", "Event", "communicate"})

#: The one home of the listening line and the address: a copy keeps passing alone.
HOME = "tests/studyforge/cli/serving.py"
DEFINED = re.compile(r"^(?:LISTENING\b|class Address\b)", re.M)


def called(node: ast.AST) -> set[str]:
    """The name of every call under `node`, as its last dotted part."""
    calls = [each.func for each in ast.walk(node) if isinstance(each, ast.Call)]
    return {getattr(func, "attr", getattr(func, "id", "")) for func in calls}


def scopes() -> dict[str, ast.AST]:
    """Each module or named test in `READERS`, parsed; a named test that is absent fails."""
    found = {}
    for relative, names in READERS.items():
        tree = ast.parse((repository_root() / relative).read_text(encoding="utf-8"))
        tests = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        for name in names or [None]:
            assert name is None or name in tests, f"{relative} has no {name}; nothing was read"
            found[relative if name is None else f"{relative}::{name}"] = tests.get(name, tree)
    return found


def test_the_reader_waits_on_the_stream_and_never_on_a_clock():
    # ⛔ A sleep standing in for the read passes whenever the machine is fast.
    assert "sleep" not in called(ast.parse(inspect.getsource(ProcessOutput))), "the reader sleeps"
    found = scopes()
    assert len(found) == 4, f"the population is {sorted(found)}, not the four `W237` names"
    for where, node in found.items():
        named = called(node)
        assert named, f"{where} parsed to no calls, so the check read nothing"
        assert not named & AROUND_THE_READER, f"{where} calls {sorted(named & AROUND_THE_READER)}"
        pipes = {each.attr for each in ast.walk(node) if isinstance(each, ast.Attribute)}
        assert not pipes & {"stdout", "stderr"}, f"{where} touches a pipe around the reader"


def test_the_listening_line_and_the_address_have_one_home():
    modules = tracked_files(("tests/*.py",))
    root = repository_root()
    defined = [name for name in modules if DEFINED.search((root / name).read_text("utf-8"))]
    assert defined == [HOME], f"defined in {defined} of {len(modules)} modules, not only {HOME}"


def decoy(tmp_path_factory) -> tuple[socket.socket, str]:
    """A listening Unix socket named `docker.sock`, in a directory the harness mints."""
    path = str(tmp_path_factory.mktemp("dk") / "docker.sock")
    assert len(path) < 100, "the socket path is too long to bind, so the arm could not run"
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(path)
    listener.listen()
    listener.setblocking(False)
    return listener, path


def accepted(listener: socket.socket) -> int:
    """How many connections are waiting on the decoy."""
    count = 0
    while True:
        try:
            connection, _ = listener.accept()
        except BlockingIOError:
            return count
        connection.close()
        count += 1


def targets(descriptors: str) -> list[str]:
    """What each descriptor a live process holds points at.

    ⚠️ A handler thread can close one between the listing and the read, so a
    descriptor that vanished is skipped rather than failing the reading.
    """
    found = []
    for fd in os.listdir(descriptors):
        with contextlib.suppress(FileNotFoundError):
            found.append(os.readlink(os.path.join(descriptors, fd)))
    return found


def test_the_decoy_counts_a_connection_when_one_is_made(tmp_path_factory):
    # ⭐ The control: the arm below reads 0, and this is the same instrument reading 1.
    listener, path = decoy(tmp_path_factory)
    with listener, socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(path)
        assert accepted(listener) == 1


@pytest.mark.parametrize("form", ["site", "root"])
def test_the_serving_process_never_reaches_a_docker_socket_its_environment_names(
    form, tmp_path, tmp_path_factory
):
    root, site = build("depth2", tmp_path, into=tmp_path / "root" / "depth2")
    prefix, corpus = "", root
    if form == "root":
        shutil.copytree(root, site, dirs_exist_ok=True)
        root, site, prefix = tmp_path / "root", None, "/depth2"
    unit = [page for page in pages_of(FIXTURES / "depth2") if page != "index.html"][0]
    requested = [f"{prefix}/index.html", "/api/v1/content/toc", f"{prefix}/" + quote(unit)]
    listener, path = decoy(tmp_path_factory)
    with listener, launched(root, site, {"DOCKER_HOST": f"unix://{path}"}) as running:
        for each in requested:
            assert fetch(running.server, each)[0] == 200
        descriptors = f"/proc/{running.process.pid}/fd"
        assert os.path.isdir(descriptors), "no descriptor table to read, so the arm did not run"
        held = targets(descriptors)
        code, stdout, stderr = running.stopped()
        assert any(target.startswith("socket:") for target in held), "not even its listener"
        assert [target for target in held if "docker" in target] == []
        assert accepted(listener) == 0, "the serving process connected to the Docker socket"
    assert code == OK, stderr[-400:]
    between = printed(running, stdout, requested)
    if form == "root":
        # ⭐ Printed straight after the listening line, so a reader that read ahead loses it.
        port, index = running.server.server_address[1], read_corpus(corpus).shared.root_index
        assert between[0] == f"corpus {source_of(corpus)} http://127.0.0.1:{port}{prefix}/{index}"
