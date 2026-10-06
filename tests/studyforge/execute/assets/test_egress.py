"""Mirror of `src/studyforge/execute/assets/egress.py.txt` (R12): the allow-list proxy, in process.

⭐ The shipped file is loaded as a script would be and driven over local sockets: which CONNECT
lines it refuses and which it tunnels. The container proof against stand-in hosts, on an internal
network, is `test_live_proxy_image.py`'s. ⛔ Names here are made up; the guard that refuses
non-public addresses is swapped only in the one test that needs a loopback upstream.
"""

from __future__ import annotations

import asyncio
import importlib.machinery
import importlib.util
from pathlib import Path

import pytest

import studyforge.execute as execute

SCRIPT = Path(execute.__file__).parent / "assets" / "egress.py.txt"


def load(monkeypatch, host="allowed.example.test", port="443"):
    monkeypatch.setenv("EGRESS_ALLOW_HOST", host)
    monkeypatch.setenv("EGRESS_ALLOW_PORT", port)
    loader = importlib.machinery.SourceFileLoader("egress_under_test", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("address", "ok"),
    [
        ("8.8.8.8", True),
        ("1.1.1.1", True),
        ("2606:4700::1111", True),
        ("127.0.0.1", False),
        ("10.1.2.3", False),
        ("172.16.0.1", False),
        ("192.168.1.1", False),
        ("169.254.169.254", False),
        ("100.64.0.1", False),
        ("0.0.0.0", False),
        ("::1", False),
        ("fe80::1", False),
        ("fd00::1", False),
        ("::ffff:127.0.0.1", False),
        ("not an address", False),
        ("", False),
    ],
)
def test_only_a_global_address_is_public(monkeypatch, address, ok):
    assert load(monkeypatch).public(address) is ok


@pytest.mark.parametrize(
    "host", ["", "upper", "a", "a..b", "1.2.3.4:443", "a b.test", "a.test/", "-a.test", "a.test."]
)
def test_it_refuses_to_start_without_one_bare_host(monkeypatch, host):
    with pytest.raises(SystemExit):
        load(monkeypatch, host=host).run()


async def ask(module, line: bytes, upstream=None):
    """Send one request line to the proxy's handler over a socket; return what came back."""
    limit = asyncio.Semaphore(2)

    async def one(reader, writer):
        await module.handle(reader, writer, limit)

    server = await asyncio.start_server(one, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    try:
        reader, writer = await asyncio.open_connection("127.0.0.1", port)
        writer.write(line)
        await writer.drain()
        head = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 5)
        if upstream and b" 200 " in head:
            writer.write(b"ping\n")
            await writer.drain()
            return head, await asyncio.wait_for(reader.read(100), 5)
        writer.close()
        return head, b""
    finally:
        server.close()
        await server.wait_closed()


def connect(target: str, verb: str = "CONNECT") -> bytes:
    return f"{verb} {target} HTTP/1.1\r\nHost: {target}\r\n\r\n".encode()


@pytest.mark.parametrize(
    ("line", "status"),
    [
        (connect("denied.example.test:443"), b"403"),
        (connect("allowed.example.test:80"), b"403"),
        (connect("allowed.example.test:8443"), b"403"),
        (connect("127.0.0.1:443"), b"403"),
        (connect("allowed.example.test"), b"403"),
        (connect("allowed.example.test:443", "GET"), b"405"),
        (connect("allowed.example.test:443", "POST"), b"405"),
        (b"CONNECT allowed.example.test:443\r\n\r\n", b"405"),
    ],
)
def test_every_other_verb_host_or_port_is_refused(monkeypatch, line, status):
    module = load(monkeypatch)
    head, _ = asyncio.run(ask(module, line))
    assert status in head.split(b"\r\n")[0]


def test_an_address_that_is_not_public_is_refused_even_for_the_allowed_host(monkeypatch):
    module = load(monkeypatch, host="localhost", port="443")
    head, _ = asyncio.run(ask(module, connect("localhost:443")))
    assert b"403" in head.split(b"\r\n")[0] and b"not public" in head


def test_an_allowed_public_name_becomes_a_tunnel_to_the_resolved_address(monkeypatch):
    async def run():
        async def echo(reader, writer):
            data = await reader.readline()
            writer.write(b"echo:" + data)
            await writer.drain()
            writer.close()

        upstream = await asyncio.start_server(echo, "127.0.0.1", 0)
        port = upstream.sockets[0].getsockname()[1]
        module = load(monkeypatch, host="localhost", port=str(port))
        module.public = lambda address: True  # ⚠️ the one swap: the stand-in is on loopback
        try:
            return await ask(module, connect(f"localhost:{port}"), upstream=True)
        finally:
            upstream.close()
            await upstream.wait_closed()

    head, body = asyncio.run(run())
    assert b"200 Connection established" in head and body == b"echo:ping\n"
