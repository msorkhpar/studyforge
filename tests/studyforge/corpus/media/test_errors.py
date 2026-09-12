"""Mirror of `src/studyforge/corpus/media/errors.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.corpus.manifest import MediaPolicy
from studyforge.corpus.media import (
    MediaError,
    MediaFile,
    MediaFootprint,
    measure_directories,
    require_committable,
    verdict_for,
)

OVER = MediaFootprint((MediaFile(PurePosixPath("u.audio/a.mp3"), 900),))


def test_a_media_error_is_a_value_error():
    # ⚠️ The split `placement.errors` states: every failure here is "what you
    # handed me cannot be weighed against this policy", never "this document
    # cannot be read" — ⛔ this package reads no `corpus.json` at all.
    assert issubclass(MediaError, ValueError)


@pytest.mark.parametrize(
    "call",
    [
        # a root that is not a directory
        lambda: measure_directories("no-such-corpus-root", ["u.audio"]),
        # a media directory that escapes the corpus root
        lambda: measure_directories(".", ["/" + "srv/elsewhere/audio"]),
        # `auto` with nothing to compare against
        lambda: verdict_for(MediaPolicy(commit="auto")),
        # a crossed limit, which is the refusal this package exists to raise
        lambda: require_committable(
            verdict_for(MediaPolicy(commit="auto", max_total_bytes=1, max_file_bytes=1), OVER)
        ),
    ],
)
def test_every_way_it_can_fail_raises_this_one_type(call):
    with pytest.raises(MediaError):
        call()


def test_a_refusal_carries_no_absolute_path():
    # ⛔ R7. The corpus root is an absolute path on somebody's machine and a
    # build's refusal is read in a log. ⚠️ Assembled so the repository's own
    # R7 sweep is not asked for an exception.
    with pytest.raises(MediaError) as raised:
        measure_directories("/" + "home/example/corpus", ["u.audio"])
    assert "/home/" not in str(raised.value)
    assert "example" not in str(raised.value)


def test_a_refusal_says_what_arrived_by_type_rather_than_by_value():
    # ⭐ `studyforge.describe` is how a refusal says what it was handed.
    with pytest.raises(MediaError) as raised:
        measure_directories(None, ["u.audio"])
    assert "nothing" in str(raised.value)
