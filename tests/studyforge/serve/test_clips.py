"""Mirror of `src/studyforge/serve/clips.py` (R12).

Served, the clip signal is the disk's answer NOW: a clip put back after the file
was written is heard, a clip taken away is not, and the file is never rewritten.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.corpus.placement import profile_for, registered
from studyforge.render.pageassets import ABSENT, CLIPS_NAME, PRESENT, RELEASED, clips_script
from studyforge.serve.clips import holds_a_clip, is_signal, told
from studyforge.serve.response import NO_STORE, Request
from studyforge.serve.routes.assets import serve

#: A clip's name as narration mints it: a speech id, a dash, eight hex digits.
CLIP = "basics--unit-01.prose.b1-0123abcd.mp3"

SIGNAL = f"/.studyforge/assets/{CLIPS_NAME}"

ADDRESS = Address.of("basics", "01-getting-started")


def placed_audio(profile: str) -> Path:
    """Where `profile` puts a unit's clips, relative to the served root (TREE and FLAT alike)."""
    origin = "01-getting-started/README.md" if profile == "sibling" else None
    return Path(profile_for(profile).unit(ADDRESS, 1, "Your first class", origin=origin).audio)


def nothing_private(path: Path) -> bool:
    return False


def a_site(tmp_path: Path, told_state: str = RELEASED) -> Path:
    """A served root holding the signal and an empty audio directory under `sibling`'s shape."""
    root = tmp_path / "site"
    (root / ".studyforge" / "assets").mkdir(parents=True)
    (root / ".studyforge" / "assets" / CLIPS_NAME).write_bytes(clips_script(told_state))
    (root / "src" / "study" / "audio" / "basics.unit-01").mkdir(parents=True)
    return root


def get(root: Path, path: str = SIGNAL, private=nothing_private):
    return serve(root, Request("GET", path, {}), path, private)


def test_the_signal_is_recognised_by_where_it_sits_and_nothing_else(tmp_path):
    assert is_signal(tmp_path / ".studyforge" / "assets" / CLIPS_NAME)
    assert not is_signal(tmp_path / "assets" / CLIPS_NAME)
    assert not is_signal(tmp_path / ".studyforge" / CLIPS_NAME)
    assert not is_signal(tmp_path / ".studyforge" / "assets" / "page.js")


@pytest.mark.parametrize("where", ["src/study/audio/basics.unit-01", "basics/unit-01/audio"])
def test_a_clip_in_an_audio_directory_anywhere_in_the_source_is_found(tmp_path, where):
    directory = tmp_path / where
    directory.mkdir(parents=True)
    assert not holds_a_clip(tmp_path, nothing_private)
    (directory / CLIP).write_bytes(b"x")
    assert holds_a_clip(tmp_path, nothing_private)


@pytest.mark.parametrize("profile", registered())
def test_a_clip_where_each_placement_puts_it_is_found(tmp_path, profile):
    # ⭐ `tree` puts every clip under `.studyforge/`, a dot-directory: the look must
    # still reach it, or a served tree-placed course hides its own narration.
    root = a_site(tmp_path)
    directory = root / placed_audio(profile)
    directory.mkdir(parents=True, exist_ok=True)
    assert get(root).body == clips_script(ABSENT)
    (directory / CLIP).write_bytes(b"x")
    assert holds_a_clip(root, nothing_private)
    assert get(root).body == clips_script(PRESENT), f"a clip placed by {profile!r} was not heard"


@pytest.mark.parametrize("profile", registered())
def test_a_withheld_clip_where_each_placement_puts_it_does_not_count(tmp_path, profile):
    root = a_site(tmp_path)
    directory = root / placed_audio(profile)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / CLIP).write_bytes(b"x")
    assert get(root, private=lambda path: path.suffix == ".mp3").body == clips_script(ABSENT)


@pytest.mark.parametrize(
    "where",
    [
        "src/study/audio/basics.unit-01/notes.mp3",  # not a clip's name
        "src/study/media/" + CLIP,  # not an audio directory
        ".git/audio/" + CLIP,  # under a dot-directory
        ".sdkman/candidates/audio/" + CLIP,  # under a dot-directory no placement writes
        "src/.studyforge/audio/" + CLIP,  # a generated root's name, but not the site's own
    ],
)
def test_nothing_but_a_clip_in_an_audio_directory_counts(tmp_path, where):
    path = tmp_path / where
    path.parent.mkdir(parents=True)
    path.write_bytes(b"x")
    assert not holds_a_clip(tmp_path, nothing_private)


def test_a_clip_the_server_withholds_does_not_count(tmp_path):
    # ⛔ A serve with narration off withholds every clip, and must not tell a page
    # its clips are there.
    (tmp_path / "audio").mkdir()
    (tmp_path / "audio" / CLIP).write_bytes(b"x")
    assert not holds_a_clip(tmp_path, lambda path: True)


def test_the_answer_follows_the_disk_and_the_file_is_left_as_it_was(tmp_path):
    root = a_site(tmp_path, RELEASED)
    signal = root / ".studyforge" / "assets" / CLIPS_NAME
    first = get(root)
    assert first.status == 200 and first.body == clips_script(ABSENT)
    (root / "src" / "study" / "audio" / "basics.unit-01" / CLIP).write_bytes(b"x")
    second = get(root)
    assert second.body == clips_script(PRESENT), "a clip put back was not heard"
    assert signal.read_bytes() == clips_script(RELEASED), "the server rewrote the file"
    assert told(signal, nothing_private) == clips_script(PRESENT)


def test_the_answer_is_script_and_is_never_stored(tmp_path):
    answer = get(a_site(tmp_path))
    assert answer.header("Content-Type").startswith("text/javascript")
    assert answer.header("Cache-Control") == NO_STORE
    assert answer.header("ETag") is None


def test_a_site_with_no_signal_file_still_answers_404(tmp_path):
    # ⭐ Only a signal the site HAS is answered, so an older build is unchanged.
    root = a_site(tmp_path)
    (root / ".studyforge" / "assets" / CLIPS_NAME).unlink()
    assert get(root).status == 404
