"""Mirror of `src/studyforge/corpus/media/recorded.py` (R12) — what the record locates.

The footprint weighs every clip the narration record locates, so this
module's answer is the population the widening adds. Records are fabricated
through `narrate.synth`'s own writer, never typed as JSON by hand.
"""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.corpus.media import MediaError
from studyforge.corpus.media.recorded import Unlocated, recorded_clips
from studyforge.narrate.synth import Clip, Conditions, Superseded, state_file, write_state

SETTINGS = Conditions(voice="voice-a", fmt="mp3", provides=3, chunk_chars=320)
GONE = ".studyforge/units/a-unit-no-longer-declared/audio"
HERE = ".studyforge/units/basics/01-intro/audio"


def record(root, clips):
    """Write a narration record holding `clips` under `root`."""
    stamped = {
        key: Clip(
            filename=clip.filename,
            conditions=SETTINGS.fingerprint,
            where=clip.where,
            superseded=clip.superseded,
        )
        for key, clip in clips.items()
    }
    write_state(state_file(root), stamped, SETTINGS)


def test_an_absent_record_locates_nothing_and_is_not_a_refusal(tmp_path):
    assert recorded_clips(tmp_path) == ((), ())


def test_every_current_and_superseded_clip_is_located_relative_to_the_root(tmp_path):
    # ⭐ Clips need not be on disk: whether something is there is the footprint's question.
    record(
        tmp_path,
        {
            "u1-s2": Clip("u1-s2-bbbb.mp3", "", where=GONE),
            "u1-s1": Clip(
                "u1-s1-aaaa.mp3", "", where=HERE, superseded=(Superseded("u1-s1-old.mp3", GONE),)
            ),
        },
    )
    located, unlocated = recorded_clips(tmp_path)
    # ⛔ R10: ordered by the posix string, whatever order the record holds them in.
    assert located == (
        PurePosixPath(f"{GONE}/u1-s1-old.mp3"),
        PurePosixPath(f"{GONE}/u1-s2-bbbb.mp3"),
        PurePosixPath(f"{HERE}/u1-s1-aaaa.mp3"),
    )
    assert unlocated == ()
    assert not any(path.is_absolute() for path in located)


def test_a_clip_with_no_recorded_directory_is_named_not_dropped(tmp_path):
    record(
        tmp_path,
        {"u1-s1": Clip("u1-s1-aaaa.mp3", "", superseded=(Superseded("u1-s1-old.mp3"),))},
    )
    located, unlocated = recorded_clips(tmp_path)
    assert located == ()
    assert unlocated == (Unlocated("u1-s1", "u1-s1-aaaa.mp3"), Unlocated("u1-s1", "u1-s1-old.mp3"))
    assert "u1-s1's clip u1-s1-aaaa.mp3" in unlocated[0].sentence()


def test_a_filename_that_is_not_one_file_name_is_named_by_id_and_never_echoed(tmp_path):
    # ⛔ R7: the recorded value would leave its directory, so it is not quoted.
    record(tmp_path, {"u1-s1": Clip("../../elsewhere.mp3", "", where=HERE)})
    located, unlocated = recorded_clips(tmp_path)
    assert located == ()
    assert unlocated == (Unlocated("u1-s1", None),)
    assert "u1-s1" in unlocated[0].sentence()
    assert "elsewhere" not in unlocated[0].sentence()


def test_a_blank_filename_records_no_clip_and_names_nothing(tmp_path):
    record(tmp_path, {"u1-s1": Clip(" ", "", where=HERE)})
    assert recorded_clips(tmp_path) == ((), ())


def test_an_unreadable_record_refuses_and_quotes_no_path(tmp_path):
    # ⛔ An empty answer here would be a silent under-count.
    state_file(tmp_path).parent.mkdir(parents=True)
    state_file(tmp_path).write_text("not a record", encoding="utf-8")
    with pytest.raises(MediaError) as raised:
        recorded_clips(tmp_path)
    assert "narration record cannot be read" in str(raised.value)
    assert str(tmp_path) not in str(raised.value)


def test_the_record_is_the_only_file_opened(tmp_path, monkeypatch):
    # ⛔ The footprint stats clips; it never opens one.
    from pathlib import Path

    record(tmp_path, {"u1-s1": Clip("u1-s1-aaaa.mp3", "", where=HERE)})
    clip = tmp_path / HERE / "u1-s1-aaaa.mp3"
    clip.parent.mkdir(parents=True)
    clip.write_bytes(b"x")
    opened = []
    original = Path.open

    def spy(self, *args, **kwargs):
        opened.append(self.name)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", spy)
    recorded_clips(tmp_path)
    assert opened == [state_file(tmp_path).name]
