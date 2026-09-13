"""Mirror of `src/studyforge/serve/caching.py` (R12)."""

from __future__ import annotations

import os

import pytest

from studyforge.serve.caching import (
    UNSATISFIABLE,
    WHOLE,
    not_modified,
    parse_range,
    strong_etag,
    weak_etag,
)


def test_a_strong_tag_is_quoted_unweakened_and_moves_with_the_bytes():
    first = strong_etag(b"one")
    assert first == strong_etag(b"one")
    assert first.startswith('"') and first.endswith('"')
    assert not first.startswith("W/")
    assert strong_etag(b"two") != first


def test_a_weak_tag_is_marked_weak_and_moves_with_size_and_mtime(tmp_path):
    path = tmp_path / "clip.bin"
    path.write_bytes(b"12345")
    first = weak_etag(path.stat())
    assert first.startswith('W/"')
    os.utime(path, ns=(10**18, 10**18))
    assert weak_etag(path.stat()) != first
    moved = weak_etag(path.stat())
    path.write_bytes(b"123456")
    os.utime(path, ns=(10**18, 10**18))
    assert weak_etag(path.stat()) != moved


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        (None, False),
        ("", False),
        ('"abc"', True),
        ('"zzz", "abc"', True),
        ("*", True),
        ('W/"abc"', True),
        ('"abcd"', False),
    ],
)
def test_if_none_match_uses_the_weak_comparison(header, expected):
    assert not_modified(header, '"abc"') is expected


def test_a_weak_tag_matches_its_own_opaque_value():
    assert not_modified('"1-2"', 'W/"1-2"')


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("bytes=0-9", (0, 9)),
        ("bytes=1-1", (1, 1)),
        ("bytes=90-", (90, 99)),
        ("bytes=-10", (90, 99)),
        ("bytes=-200", (0, 99)),
        ("bytes=95-200", (95, 99)),
        ("BYTES = 0-0", (0, 0)),
        ("bytes=100-", UNSATISFIABLE),
        ("bytes=100-150", UNSATISFIABLE),
        ("bytes=10-5", UNSATISFIABLE),
        ("bytes=abc", UNSATISFIABLE),
        ("bytes=-", UNSATISFIABLE),
        ("bytes=-0", UNSATISFIABLE),
        ("bytes=²-", UNSATISFIABLE),
        ("bytes=0-1,5-6", WHOLE),
        ("items=0-1", WHOLE),
        ("bytes", WHOLE),
        (None, WHOLE),
    ],
)
def test_a_range_is_read_against_a_hundred_byte_file(header, expected):
    assert parse_range(header, 100) == expected


@pytest.mark.parametrize("header", ["bytes=0-", "bytes=-5", "bytes=0-0"])
def test_every_range_over_an_empty_file_is_unsatisfiable(header):
    assert parse_range(header, 0) == UNSATISFIABLE
