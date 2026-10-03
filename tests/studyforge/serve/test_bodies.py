"""Mirror of `src/studyforge/serve/bodies.py` (R12): a `POST` body, read to a limit."""

from __future__ import annotations

import io

import pytest

from studyforge.serve.bodies import read


def test_the_declared_length_is_read_and_nothing_past_it():
    stream = io.BytesIO(b"abcdefgh")
    assert read({"Content-Length": "3"}, stream, 10) == b"abc"
    assert stream.read() == b"defgh"


@pytest.mark.parametrize("declared", [None, "", "0"])
def test_no_declared_length_is_no_body_and_reads_nothing(declared):
    stream = io.BytesIO(b"abc")
    headers = {} if declared is None else {"Content-Length": declared}
    assert read(headers, stream, 10) == b"" and stream.tell() == 0


@pytest.mark.parametrize("declared", ["abc", "-1", "11", "1.5", "0x3"])
def test_a_bad_or_over_limit_length_is_refused_and_reads_nothing(declared):
    stream = io.BytesIO(b"abc")
    assert read({"Content-Length": declared}, stream, 10) is None and stream.tell() == 0


def test_the_limit_is_inclusive():
    assert read({"Content-Length": "10"}, io.BytesIO(b"0123456789"), 10) == b"0123456789"
