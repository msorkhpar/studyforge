"""Mirror of `src/studyforge/narrate/playable.py` (R12) — the position→filename join.

⛔ **The second direction is the subject of this module, and it is asserted first.**
A happy-path test proves the positional bug is absent today; it does not prove it
cannot return. So every shift case below carries a **refutation control** — the
answer a positional implementation would give, computed by `positional_join` and
asserted to DISAGREE with the answer under test. ⭐ A positional implementation
fails those tests by construction rather than by luck.

⛔ **Every record in this module is written by the shipped writer** (`render_state`
→ `read_state`), so the order the join is tested against is the order a real
corpus's `.studyforge/narration.json` actually has — sorted lexicographically by
id, which is not reading order. ⚠️ Writing the record by hand would have hidden
the very fact the refutation controls turn on.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.narrate.playable import (
    MISFILED,
    NOT_ON_DISK,
    NOT_PLACED,
    NOT_RECORDED,
    WORDS_MOVED,
    Playable,
    playable_of,
    playable_of_units,
)
from studyforge.narrate.speakable import speakable_of
from studyforge.narrate.speakable.naming import digest_of, parse_clip_name
from studyforge.narrate.speakable.records import SpeechUnit
from studyforge.narrate.synth.incremental import wanted_name
from studyforge.narrate.synth.record import (
    Clip,
    Conditions,
    State,
    read_state,
    state_file,
    write_state,
)
from studyforge.render.page import AUDIO_ATTRIBUTE, Narration
from tests.studyforge.render.page.pages import sample_placement

VOICE = "am_liam"
FMT = "mp3"

#: ⛔ Eleven, not three. Ten is where `sorted()` over `…b<n>` ids stops agreeing
#: with reading order (`b10` sorts before `b2`), and that divergence is what the
#: refutation controls need in order to bite. A three-block fixture would let a
#: positional implementation pass every test in this file.
BLOCKS = 11


def conditions() -> Conditions:
    return Conditions(voice=VOICE, fmt=FMT, provides=2, chunk_chars=320)


def document(sentences: list[str]) -> dict:
    """A served unit document with one paragraph per sentence, in order."""
    return {
        "address": ["depth-one", "prose"],
        "unit": 2,
        "sections": [
            {"key": "prose", "blocks": [{"type": "para", "text": text} for text in sentences]}
        ],
    }


def sentences(count: int = BLOCKS) -> list[str]:
    return [f"sentence number {index}" for index in range(1, count + 1)]


def units_of(sentences_said: list[str]) -> tuple[SpeechUnit, ...]:
    return speakable_of(document(sentences_said)).units


def recorded(units: tuple[SpeechUnit, ...], tmp_path: Path, *, merged: dict | None = None) -> State:
    """Write the record the shipped writer would write for `units`, and read it back.

    ⚠️ `merged` is what an earlier build left behind. ⛔ The pass never prunes —
    `synthesise` merges into what it read — so a corpus whose blocks moved really
    does carry entries for units the document no longer has.
    """
    settings = conditions()
    clips = dict(merged or {})
    clips.update(
        {
            unit.id: Clip(
                filename=wanted_name(unit, settings),
                conditions=settings.fingerprint,
                engine="kokoro",
                engine_model="kokoro",
            )
            for unit in units
        }
    )
    file = state_file(tmp_path)
    file.parent.mkdir(parents=True, exist_ok=True)
    write_state(file, clips, settings)
    return read_state(file)


def place(state: State, tmp_path: Path) -> Path:
    """Put a real file on disk for every recorded clip, and return the directory."""
    directory = tmp_path / "audio"
    directory.mkdir(parents=True, exist_ok=True)
    for clip in state.clips.values():
        (directory / clip.filename).write_bytes(b"ID3\x04\x00\x00\x00")
    return directory


def positional_join(units: tuple[SpeechUnit, ...], state: State) -> dict:
    """⛔ What a POSITIONAL implementation returns: the record's entries, zipped in order.

    ⭐ This is the defect, written out once so every shift case can assert the
    answer under test is not it.
    """
    return {
        unit.position: clip.filename
        for unit, clip in zip(units, state.clips.values(), strict=False)
    }


def filed_under(filename: str) -> str:
    """The speech id a clip's own name says it belongs to."""
    return parse_clip_name(Path(filename).stem)[0]


# --- the join, and that it is on the id --------------------------------------


def test_every_unit_addresses_the_clip_filed_under_its_own_id(tmp_path):
    units = units_of(sentences())
    playing = playable_of_units(units, recorded(units, tmp_path))
    assert len(playing.filenames) == len(units)
    for unit in units:
        assert filed_under(playing.filenames[unit.position]) == unit.id


def test_the_key_is_the_units_own_position_and_is_never_spelled_a_second_way(tmp_path):
    # ⛔ The mapping's keys are read off `SpeechUnit.position` — no tuple is
    # written out here, so a join that recomputed a numbering would miss.
    units = units_of(sentences())
    playing = playable_of_units(units, recorded(units, tmp_path))
    assert set(playing.filenames) == {unit.position for unit in units}


def test_a_page_with_no_recorded_clips_is_falsy_and_names_every_silence():
    # ⚠️ A record that is PRESENT and holds no clip for this page. The absent
    # record is a different state and is quiet — see the two tests at the end.
    units = units_of(sentences())
    playing = playable_of_units(units, State(clips={}))
    assert not playing
    assert [gone.reason for gone in playing.silent] == [NOT_RECORDED] * len(units)
    assert [gone.speech_id for gone in playing.silent] == [unit.id for unit in units]


def test_a_page_with_clips_is_truthy(tmp_path):
    # ⭐ The positive control for the emptiness above.
    units = units_of(sentences())
    assert playable_of_units(units, recorded(units, tmp_path))


# --- ⛔ THE SECOND DIRECTION: shifted units, and the control that refutes -------


def test_the_shipped_record_is_not_in_reading_order_which_is_why_position_cannot_join(tmp_path):
    # ⛔ The ground fact every refutation control below stands on, measured
    # against the shipped writer rather than asserted. `render_state` sorts by
    # id, and `…b10` sorts before `…b2`.
    units = units_of(sentences())
    state = recorded(units, tmp_path)
    assert list(state.clips) != [unit.id for unit in units]
    assert list(state.clips) == sorted(unit.id for unit in units)


def test_a_unit_that_gained_a_speakable_element_still_resolves_every_clip(tmp_path):
    # ⛔ THE test. A paragraph is inserted at the front, so every id AND every
    # position after it moves. The record is what the pass leaves behind: the
    # new entries merged over the old, nothing pruned.
    before = units_of(sentences())
    old = dict(recorded(before, tmp_path).clips)
    after = units_of(["a newly written opening", *sentences()])
    state = recorded(after, tmp_path, merged=old)

    playing = playable_of_units(after, state)

    assert playing.silent == ()
    assert playing.stale == ()
    for unit in after:
        filename = playing.filenames[unit.position]
        filed, digest = parse_clip_name(Path(filename).stem)
        assert filed == unit.id
        assert digest == digest_of(unit.speak)


def test_a_positional_join_addresses_the_wrong_audio_for_the_same_shift(tmp_path):
    # ⭐ The refutation control for the test above, and the reason it is not a
    # happy path. A positional implementation passes the previous test only if
    # this assertion fails.
    before = units_of(sentences())
    old = dict(recorded(before, tmp_path).clips)
    after = units_of(["a newly written opening", *sentences()])
    state = recorded(after, tmp_path, merged=old)

    honest = dict(playable_of_units(after, state).filenames)
    positional = positional_join(after, state)

    assert positional != honest
    wrong = [
        unit
        for unit in after
        if unit.position in positional and filed_under(positional[unit.position]) != unit.id
    ]
    assert wrong, "the control did not reproduce the defect it exists to refute"


def test_a_unit_that_lost_a_speakable_element_still_resolves_every_clip(tmp_path):
    # ⚠️ The other half of "shifted": a paragraph is removed, so the record keeps
    # an entry for a unit the document no longer has and carries MORE clips than
    # there are units.
    before = units_of(sentences())
    old = dict(recorded(before, tmp_path).clips)
    after = units_of(sentences()[1:])
    state = recorded(after, tmp_path, merged=old)

    playing = playable_of_units(after, state)

    assert len(state.clips) > len(after)
    assert playing.silent == ()
    for unit in after:
        assert filed_under(playing.filenames[unit.position]) == unit.id
    assert positional_join(after, state) != dict(playing.filenames)


# --- ⭐ a clip that cannot be played is a NAMED STATE, never a KeyError ---------


def test_a_unit_with_no_recorded_clip_is_named_rather_than_missing(tmp_path):
    units = units_of(sentences())
    state = recorded(units[1:], tmp_path)
    playing = playable_of_units(units, state)
    assert units[0].position not in playing.filenames
    assert [(gone.speech_id, gone.reason) for gone in playing.silent] == [
        (units[0].id, NOT_RECORDED)
    ]


def test_asking_for_an_unnarrated_position_is_not_a_key_error():
    # ⛔ The clause stated as the caller experiences it: a lookup that finds
    # nothing must be answerable, because the renderer asks for every element.
    playing = playable_of_units(units_of(sentences()), State(clips={}, present=False))
    assert playing.filenames.get(("prose", (0,), None)) is None


def test_a_record_that_names_no_file_is_its_own_state():
    units = units_of(sentences()[:1])
    state = State(clips={units[0].id: Clip(filename="   ", conditions="x" * 8)})
    playing = playable_of_units(units, state)
    assert playing.filenames == {}
    assert [gone.reason for gone in playing.silent] == [NOT_PLACED]


@pytest.mark.parametrize(
    "filename",
    ["not-a-clip-name.mp3", "somebody-else-11111111.mp3", "trailing-dash-.mp3"],
    ids=["unparseable", "another units id", "no digest"],
)
def test_a_clip_whose_name_disagrees_with_its_key_is_refused_rather_than_played(filename):
    # ⛔ The corroboration, and the worst failure shape this module removes: the
    # entry is filed under this unit but the file it names belongs to another.
    # Playing it would be a valid filename, a present file, and the wrong words.
    units = units_of(sentences()[:1])
    state = State(clips={units[0].id: Clip(filename=filename, conditions="x" * 8)})
    playing = playable_of_units(units, state)
    assert playing.filenames == {}
    assert [(gone.reason, gone.filename) for gone in playing.silent] == [(MISFILED, filename)]


def test_a_recorded_clip_that_is_not_on_disk_is_named_when_the_directory_is_given(tmp_path):
    units = units_of(sentences())
    state = recorded(units, tmp_path)
    directory = place(state, tmp_path)
    (directory / state.clips[units[3].id].filename).unlink()

    playing = playable_of_units(units, state, audio=directory)

    assert units[3].position not in playing.filenames
    assert [(gone.speech_id, gone.reason) for gone in playing.silent] == [
        (units[3].id, NOT_ON_DISK)
    ]
    assert len(playing.filenames) == len(units) - 1


def test_the_disk_is_not_consulted_when_no_directory_is_given(tmp_path):
    # ⭐ The control for the test above: the same record, no `audio`, nothing on
    # disk at all, and every clip still resolves. Otherwise the previous test
    # would pass against an implementation that always reports NOT_ON_DISK.
    units = units_of(sentences())
    playing = playable_of_units(units, recorded(units, tmp_path))
    assert len(playing.filenames) == len(units)
    assert playing.silent == ()


def test_every_placed_clip_resolves_when_the_directory_is_given(tmp_path):
    # ⭐ The second control: the disk check passes when the files are there.
    units = units_of(sentences())
    state = recorded(units, tmp_path)
    playing = playable_of_units(units, state, audio=place(state, tmp_path))
    assert len(playing.filenames) == len(units)
    assert playing.silent == ()


# --- ⚠️ the one state that still plays ----------------------------------------


def test_a_clip_made_from_other_words_still_plays_and_is_reported(tmp_path):
    # ⚠️ The record has not caught up with the text. The file is real, so the
    # reader gets audio rather than unexplained silence, and the disagreement is
    # surfaced instead of being thrown away — `SF-17`'s `unsettled` argument.
    before = units_of(sentences())
    state = recorded(before, tmp_path)
    after = units_of([*sentences()[:-1], "sentence number eleven, rewritten"])

    playing = playable_of_units(after, state)

    assert len(playing.filenames) == len(after)
    assert playing.silent == ()
    assert [(entry.speech_id, entry.reason) for entry in playing.stale] == [
        (after[-1].id, WORDS_MOVED)
    ]
    assert playing.reasons() == {after[-1].id: WORDS_MOVED}
    assert after[-1].position in playing.filenames


def test_nothing_is_reported_when_the_record_matches_every_unit(tmp_path):
    # ⭐ The control: `stale` and `reasons()` are empty for an up-to-date record,
    # so the test above cannot pass against an implementation that reports
    # everything.
    units = units_of(sentences())
    playing = playable_of_units(units, recorded(units, tmp_path))
    assert playing.stale == ()
    assert playing.reasons() == {}


def test_every_silence_is_named_in_the_reasons(tmp_path):
    # ⭐ The one place a long run prints at the end covers silences too.
    units = units_of(sentences())
    playing = playable_of_units(units, State(clips={}))
    assert playing.reasons() == {unit.id: NOT_RECORDED for unit in units}


# --- refusals ----------------------------------------------------------------


def test_two_units_at_one_position_are_refused_rather_than_one_being_dropped():
    # ⛔ The later would silently replace the earlier in the mapping: one clip
    # gone, nothing raised.
    twin = SpeechUnit(
        id="a", speak="one", section="s", block_path=(0,), sub_index=None, kind="para"
    )
    other = SpeechUnit(
        id="b", speak="two", section="s", block_path=(0,), sub_index=None, kind="para"
    )
    with pytest.raises(ValueError, match="one position"):
        playable_of_units((twin, other), State(clips={}, present=False))


def test_a_segment_that_is_not_a_speech_unit_is_refused():
    with pytest.raises(TypeError, match="not a SpeechUnit"):
        playable_of_units(("not a unit",), State(clips={}, present=False))


def test_the_recorded_clips_arrive_as_a_state():
    with pytest.raises(TypeError, match="State"):
        playable_of_units(units_of(sentences()[:1]), {"clips": {}})


# --- the seam this module exists to close -------------------------------------


def test_the_mapping_is_what_the_renderer_takes_unchanged(tmp_path):
    # ⛔ `SF-18/4`'s hole, closed end to end: record → this join → the href on
    # the element. Nothing between them composes a name or a path.
    units = units_of(sentences())
    state = recorded(units, tmp_path)
    playing = playable_of_units(units, state)

    narration = Narration.of(playing.filenames, sample_placement())

    for unit in units:
        section, path, sub = unit.position
        expected = f"audio/{state.clips[unit.id].filename}"
        assert narration.attribute(section, path, sub) == f' {AUDIO_ATTRIBUTE}="{expected}"'


def test_the_join_hands_out_filenames_and_never_a_path(tmp_path):
    # ⛔ R4. A path here would be right under one placement profile and silently
    # wrong under the other, with the page rendering identically both ways.
    units = units_of(sentences())
    playing = playable_of_units(units, recorded(units, tmp_path))
    assert all("/" not in filename for filename in playing.filenames.values())


def test_the_returned_mapping_cannot_be_edited_by_a_caller(tmp_path):
    units = units_of(sentences())
    playing = playable_of_units(units, recorded(units, tmp_path))
    assert isinstance(playing, Playable)
    with pytest.raises(TypeError):
        playing.filenames[("prose", (99,), None)] = "smuggled.mp3"


# --- ⭐ the door a build uses, and the ordinary case of never having narrated --


def test_the_document_door_joins_the_minters_own_units(tmp_path):
    # ⛔ `playable_of(document, state)` must be `speakable_of`'s mirror and
    # nothing more: the same answer as walking the document by hand, so no build
    # derives a second set of units.
    said = sentences()
    units = units_of(said)
    state = recorded(units, tmp_path)
    assert playable_of(document(said), state) == playable_of_units(units, state)


def test_a_corpus_that_has_never_been_narrated_is_quiet(tmp_path):
    # ⛔ THE ordinary case: no `.studyforge/narration.json` anywhere. It must be
    # correct and SILENT, not one complaint per paragraph.
    fresh = tmp_path / "never-narrated"
    fresh.mkdir()
    absent = read_state(state_file(fresh))

    playing = playable_of(document(sentences()), absent)

    assert absent.present is False
    assert playing.narrated is False
    assert not playing
    assert playing.filenames == {}
    assert playing.silent == ()
    assert playing.stale == ()
    assert playing.reasons() == {}


def test_a_record_that_exists_and_records_nothing_reports_every_unit(tmp_path):
    # ⭐ THE control for the test above, and the whole reason `narrated` is not
    # `bool(filenames)`. A record that is PRESENT and empty is a real problem —
    # synthesis ran and produced nothing — so every unit is named. An
    # implementation that keyed the quiet on emptiness instead of on presence
    # passes the previous test and fails this one.
    write_state(state_file(tmp_path), {}, conditions())
    empty = read_state(state_file(tmp_path))

    playing = playable_of(document(sentences()), empty)

    assert empty.present is True
    assert playing.narrated is True
    assert not playing
    assert [gone.reason for gone in playing.silent] == [NOT_RECORDED] * BLOCKS
    assert len(playing.reasons()) == BLOCKS


def test_an_unnarrated_page_renders_exactly_as_it_did_before_narration_existed(tmp_path):
    # ⭐ `SF-18`'s reading floor, reached through this module: no transport, no
    # attribute, no branch anywhere on whether narration exists.
    fresh = tmp_path / "never-narrated"
    fresh.mkdir()
    playing = playable_of(document(sentences()), read_state(state_file(fresh)))

    narration = Narration.of(playing.filenames, sample_placement())

    assert not narration
    assert narration.attribute("prose", (0,)) == ""


def test_the_record_on_disk_reaches_the_href_on_the_element(tmp_path):
    # ⛔ The wiring, end to end and in the direction a build runs it: a record
    # written under a corpus root, read back by its own reader, joined, and
    # resolved onto the element. Nothing between them composes a name or a path.
    said = sentences()
    units = units_of(said)
    recorded(units, tmp_path)

    playing = playable_of(document(said), read_state(state_file(tmp_path)))
    narration = Narration.of(playing.filenames, sample_placement())

    assert playing.narrated is True
    assert playing.silent == ()
    for unit in units:
        section, path, sub = unit.position
        attribute = narration.attribute(section, path, sub)
        href = attribute.split('"')[1]
        assert filed_under(Path(href).name) == unit.id


def test_the_other_direction_every_recorded_clip_is_addressed_by_exactly_one_element(tmp_path):
    # ⚠️ R12's second direction for the wiring itself: not merely that every
    # element finds a clip, but that every clip the record holds is spoken for,
    # once. A join that dropped a unit would pass the direction above.
    said = sentences()
    units = units_of(said)
    state = recorded(units, tmp_path)

    playing = playable_of(document(said), state)

    addressed = sorted(playing.filenames.values())
    assert addressed == sorted(clip.filename for clip in state.clips.values())
    assert len(addressed) == len(set(addressed))
