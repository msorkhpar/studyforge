"""The `serve` verb as a real process: started as a reader starts it, stopped as a reader stops it.

⛔ **Spec §8.3's runtime arm lives here.** The process is started with `DOCKER_HOST`
naming a real, listening socket called `docker.sock` in a harness-minted directory —
a socket the process CAN reach — and afterwards that socket must have accepted
nothing, and no descriptor the process held may name it.
"""

from __future__ import annotations

import contextlib
import os
import re
import selectors
import signal
import socket
import subprocess
import sys
from urllib.parse import quote

import pytest

from studyforge.cli.serve import STOPPED
from studyforge.validate.report import OK
from tests.studyforge.cli.serving import NAMES, build, pages_of
from tests.studyforge.serve.serving import fetch
from tests.support import repository_root

LISTENING = re.compile(r"^serve http://127\.0\.0\.1:(\d+)/")


class Address:
    """What `fetch` reads off a server, for a server that lives in another process."""

    def __init__(self, port: int) -> None:
        self.server_address = ("127.0.0.1", port)


@contextlib.contextmanager
def launched(root, site, environment=None):
    """`python3 -m studyforge.cli serve …` on port `0`; yield it once it is listening."""
    process = subprocess.Popen(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.cli", "serve", str(root), "--site", str(site)]
        + ["--port", "0"],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src", **(environment or {})},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            ready = selector.select(timeout=30)
        first = process.stdout.readline() if ready else ""
        found = LISTENING.match(first)
        if found is None:
            process.kill()
            _, stderr = process.communicate(timeout=10)
            pytest.fail(f"the verb did not start listening: {first!r} {stderr[-400:]!r}")
        yield process, Address(int(found.group(1)))
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=10)


def stopped(process, how=signal.SIGINT):
    """Signal the process and return `(exit code, stdout, stderr)`."""
    process.send_signal(how)
    stdout, stderr = process.communicate(timeout=30)
    return process.returncode, stdout, stderr


@pytest.mark.parametrize("name", NAMES)
def test_the_installed_command_serves_each_fixture_and_stops_on_interrupt(name, tmp_path):
    root, site = build(name, tmp_path)
    with launched(root, site) as (process, server):
        index = fetch(server, "/index.html")
        toc = fetch(server, "/api/v1/content/toc")
        code, stdout, stderr = stopped(process)
    assert (index[0], index[2]) == (200, (site / "index.html").read_bytes())
    assert toc[0] == 200
    assert code == OK, stderr[-400:]
    assert stdout.splitlines()[-1] == STOPPED
    assert "Traceback" not in stdout + stderr


def test_a_terminate_signal_stops_it_cleanly_too(tmp_path):
    root, site = build("depth1", tmp_path)
    with launched(root, site) as (process, server):
        assert fetch(server, "/index.html")[0] == 200
        code, stdout, stderr = stopped(process, signal.SIGTERM)
    assert code == OK, stderr[-400:]
    assert "Traceback" not in stdout + stderr


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


def test_the_serving_process_never_reaches_a_docker_socket_its_environment_names(
    tmp_path, tmp_path_factory
):
    root, site = build("depth2", tmp_path)
    unit = [page for page in pages_of(root) if page != "index.html"][0]
    listener, path = decoy(tmp_path_factory)
    with listener, launched(root, site, {"DOCKER_HOST": f"unix://{path}"}) as (process, server):
        assert fetch(server, "/index.html")[0] == 200
        assert fetch(server, "/api/v1/content/toc")[0] == 200
        assert fetch(server, "/" + quote(unit))[0] == 200
        descriptors = f"/proc/{process.pid}/fd"
        assert os.path.isdir(descriptors), "no descriptor table to read, so the arm did not run"
        held = targets(descriptors)
        code, _, stderr = stopped(process)
        assert any(target.startswith("socket:") for target in held), "not even its listener"
        assert [target for target in held if "docker" in target] == []
        assert accepted(listener) == 0, "the serving process connected to the Docker socket"
    assert code == OK, stderr[-400:]
