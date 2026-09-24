"""Mirror of `src/studyforge/narrate/synth/location.py` (R12) — where a clip is."""

from __future__ import annotations

import pytest

from studyforge.narrate.synth.location import (
    Superseded,
    checked_where,
    located,
    order,
    root_of,
    where_of,
)
from studyforge.narrate.synth.record import state_file


def test_the_root_is_recovered_from_the_records_own_path(tmp_path):
    assert root_of(state_file(tmp_path)) == tmp_path


@pytest.mark.parametrize("elsewhere", ["narration.json", "corpus/narration.json"])
def test_a_record_outside_a_generated_root_has_no_root(tmp_path, elsewhere):
    with pytest.raises(ValueError):
        root_of(tmp_path / elsewhere)


def test_an_audio_directory_is_spelled_relative_to_the_root(tmp_path):
    assert where_of(tmp_path / "unit-01" / "audio", tmp_path) == "unit-01/audio"


def test_a_relative_root_and_directory_spell_the_same(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert where_of("unit-01/audio", ".") == "unit-01/audio"


def test_an_audio_directory_outside_the_root_is_refused_naming_neither(tmp_path):
    with pytest.raises(ValueError) as refused:
        where_of(tmp_path.parent / "elsewhere", tmp_path)
    assert str(tmp_path) not in str(refused.value)


@pytest.mark.parametrize("value", ["/abs/audio", "../audio", "a/../../b", "a\\b", "", None, 7])
def test_a_recorded_directory_that_leaves_the_root_is_not_one(value):
    assert checked_where(value) is None


def test_a_recorded_clip_is_located_from_the_record_alone(tmp_path):
    assert located(tmp_path, "unit-01/audio", "u1-aaaaaaaa.mp3") == (
        tmp_path / "unit-01" / "audio" / "u1-aaaaaaaa.mp3"
    )
    assert located(tmp_path, None, "u1-aaaaaaaa.mp3") is None


def test_superseded_clips_sort_by_directory_then_name():
    items = [Superseded("b.mp3", "x"), Superseded("a.mp3", "x"), Superseded("c.mp3", None)]
    assert sorted(items, key=order) == [
        Superseded("c.mp3", None),
        Superseded("a.mp3", "x"),
        Superseded("b.mp3", "x"),
    ]
