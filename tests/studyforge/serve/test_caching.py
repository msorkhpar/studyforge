"""Mirror of `src/studyforge/serve/caching.py` (R12)."""

from __future__ import annotations

import gzip
import os

import pytest

from studyforge.serve.caching import (
    UNSATISFIABLE,
    WHOLE,
    accepts_gzip,
    gzip_etag,
    gzipped,
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


def test_a_weak_tag_folds_in_the_build_digest_and_keeps_its_shape_without_one(tmp_path):
    path = tmp_path / "page.css"
    path.write_bytes(b"a{}")
    plain = weak_etag(path.stat())
    built = weak_etag(path.stat(), "ab" * 32)
    assert plain == weak_etag(path.stat(), None)
    assert built.startswith(plain[:-1]) and built.endswith("ab" * 32 + '"')
    assert built != weak_etag(path.stat(), "cd" * 32)


@pytest.mark.parametrize(
    ("header", "accepted"),
    [
        (None, False),
        ("", False),
        ("identity", False),
        ("gzip", True),
        ("GZIP", True),
        ("deflate, gzip;q=0.5", True),
        ("x-gzip", True),
        ("*", True),
        ("gzip;q=0", False),
        ("gzip;q=0, *", False),
        ("br, *;q=0", False),
        ("gzip;q=nope", False),
    ],
)
def test_accept_encoding_is_read_by_its_weights(header, accepted):
    assert accepts_gzip(header) is accepted


def test_the_gzip_representation_has_its_own_validator():
    assert gzip_etag('W/"1-2"') == 'W/"1-2+gzip"'
    assert not not_modified('W/"1-2"', gzip_etag('W/"1-2"'))
    assert gzip_etag("W/bare") == "W/bare+gzip"


def test_gzipped_bytes_round_trip_and_are_the_same_every_time():
    body = b"window.studyforge = {};\n" * 100
    assert gzip.decompress(gzipped(body)) == body
    assert gzipped(body) == gzipped(body)
