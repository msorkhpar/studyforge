"""Mirror of `src/studyforge/serve/sending.py` (R12): a file's span, held to its version."""

from __future__ import annotations

import socket
import threading

from studyforge.serve.response import Response
from studyforge.serve.sending import opened, send_span
from studyforge.serve.versions import version_of


def test_a_body_answer_opens_nothing():
    assert opened(Response(200, (), b"body")) == (None, False)


def test_an_empty_file_answer_opens_nothing(tmp_path):
    path = tmp_path / "empty.js"
    path.write_bytes(b"")
    assert opened(Response(200, (), file=path, span=None)) == (None, False)


def test_a_file_at_its_judged_version_is_opened(tmp_path):
    path = tmp_path / "index.js"
    path.write_bytes(b"judged")
    handle, moved = opened(
        Response(200, (), file=path, span=(0, 5), version=version_of(path.stat()))
    )
    try:
        assert not moved and handle.read() == b"judged"
    finally:
        handle.close()


def test_a_file_that_moved_since_its_judgement_is_not_opened(tmp_path):
    path = tmp_path / "index.js"
    path.write_bytes(b"judged")
    held = version_of(path.stat())
    path.write_bytes(b"replaced, and longer")
    assert opened(Response(200, (), file=path, span=(0, 5), version=held)) == (None, True)


def test_a_file_that_vanished_is_moved(tmp_path):
    path = tmp_path / "gone.js"
    assert opened(Response(200, (), file=path, span=(0, 5))) == (None, True)


def test_a_span_is_sent_byte_for_byte(tmp_path):
    payload = bytes(range(256)) * 4096
    path = tmp_path / "large.bin"
    path.write_bytes(payload)
    ours, theirs = socket.socketpair()
    received = bytearray()

    def drain():
        while chunk := theirs.recv(1 << 16):
            received.extend(chunk)

    reader = threading.Thread(target=drain)
    reader.start()
    with path.open("rb") as handle:
        short = send_span(ours, handle, 100, len(payload) - 200)
    ours.close()
    reader.join(timeout=10)
    theirs.close()
    assert short == 0
    assert bytes(received) == payload[100:-100]


def test_a_span_past_the_end_of_the_file_reports_what_it_could_not_send(tmp_path):
    path = tmp_path / "short.bin"
    path.write_bytes(b"0123456789")
    ours, theirs = socket.socketpair()
    with path.open("rb") as handle:
        assert send_span(ours, handle, 0, 20) == 10
    ours.close()
    assert theirs.recv(64) == b"0123456789"
    theirs.close()
