"""Mirror of `src/studyforge/execute/live.py` (R12): one live run, started with a key.

⛔ Every key here is FAKE (`sk-test-` and random hex). The wire is read against a local socket that
records what it was sent, so the claim is about the bytes the launcher puts on it.
"""

from __future__ import annotations

import base64
import secrets
import socket
import threading
import urllib.parse

import pytest

from studyforge.execute import RunRefused, Service, redactions, start_live, valid_key
from studyforge.execute.live import LIVE_PORT, LiveLauncher
from studyforge.execute.remote import NUL, request


def fake() -> str:
    return "sk-test-" + secrets.token_hex(12)


@pytest.mark.parametrize("good", ["a" * 8, "sk-test-" + "a" * 20, "A_b-9" * 40, "x" * 256])
def test_a_key_of_the_accepted_shape_is_valid(good):
    assert valid_key(good)


@pytest.mark.parametrize(
    "bad",
    [
        "", "short", "x" * 257, "a b" + "c" * 8, "a" * 8 + "\n", "a" * 8 + "\x00",
        "k;" + "a" * 8, "k$(" + "a" * 8, "k'" + "a" * 8, "k`" + "a" * 8, "k é" + "a" * 8,
        None, 5, b"a" * 9,
    ],
)
def test_a_key_of_any_other_shape_is_not(bad):
    assert not valid_key(bad)


def test_the_key_pattern_refuses_a_trailing_newline_which_a_dollar_would_admit():
    assert not valid_key("sk-test-abcdef\n")


def test_the_forms_hold_the_key_its_url_encoding_and_its_base64_at_every_alignment():
    key = fake()
    forms = redactions(key)
    assert key in forms and forms == tuple(sorted(forms, key=len, reverse=True))
    assert urllib.parse.quote(key, safe="") in forms
    for before in range(6):
        for after in range(6):
            text = base64.b64encode(("a" * before + key + "b" * after).encode()).decode()
            assert any(form in text for form in forms), (before, after)
            safe = text.replace("+", "-").replace("/", "_")
            assert any(form in safe for form in forms), (before, after)


def test_the_whole_encoding_of_the_key_alone_is_a_form_with_and_without_its_padding():
    key = "sk-test-" + "ab"  # 10 bytes: an encoding that pads
    whole = base64.b64encode(key.encode()).decode()
    assert whole.endswith("=") and whole in redactions(key) and whole.rstrip("=") in redactions(key)


def serving(answer: bytes):
    """A local socket that records one request and answers `answer`; its address and the record."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    got: list[bytes] = []

    def accept() -> None:
        connection, _ = listener.accept()
        data = b""
        while not data.endswith(NUL + NUL):
            data += connection.recv(4096)
        got.append(data)
        connection.sendall(answer)
        connection.close()
        listener.close()

    threading.Thread(target=accept, daemon=True).start()
    return Service("127.0.0.1", listener.getsockname()[1]), got


def test_the_key_is_one_framed_field_after_the_directory_and_before_the_argv():
    secret = fake()
    service, got = serving(b"O3\nhi\nX0\n")
    handle = start_live(service, ["python3", "examples/a/run.py"], secret, cwd=".")
    lines = list(handle.lines())
    fields = got[0].split(NUL)[:-2]
    assert [f.decode() for f in fields[:1]] == ["live"]
    assert fields[1].startswith(b"STUDYFORGE_RUN=") and fields[2] == b"."
    assert fields[3] == secret.encode() and fields[4:] == [b"python3", b"examples/a/run.py"]
    assert lines[-1] == "--- exit 0 ---" and "hi" in lines[0]


def test_a_launcher_refuses_a_key_of_the_wrong_shape_without_saying_it():
    bad = "has a space" + "x" * 9
    with pytest.raises(RunRefused) as refused:
        LiveLauncher(Service("127.0.0.1", 1), ".", bad)
    assert bad not in str(refused.value) and "accepts" in str(refused.value)


def test_a_launcher_never_prints_the_key_it_holds():
    secret = fake()
    launcher = LiveLauncher(Service("127.0.0.1", 1), ".", secret)
    assert secret not in repr(launcher) and secret not in str(launcher)


def test_a_graded_run_request_and_a_live_one_are_different_verbs():
    secret = fake()
    assert request("run", "t", ".", "x").split(NUL)[0] == b"run"
    assert secret.encode() not in request("run", "t", ".", "x")
    assert request("live", "t", ".", secret, "x").split(NUL)[0] == b"live"
