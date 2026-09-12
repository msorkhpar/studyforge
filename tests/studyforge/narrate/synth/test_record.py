"""`.studyforge/narration.json` — the R9 contract, R10's bytes and R7's gate.

⚠️ **The leak material below is assembled at run time**, like
`tests/studyforge/narrate/test_client.py`'s and for the same reason: this file is
swept by the repository hygiene check. ⛔ Nothing here came from any real
machine, account or person.
"""

import json

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.placement.profile import GENERATED_ROOT
from studyforge.narrate.client import Health, NarrationError
from studyforge.narrate.synth.record import (
    NARRATION_API,
    NARRATION_STATE_FILENAME,
    Clip,
    Conditions,
    StateError,
    read_state,
    render_state,
    state_file,
    write_state,
)

VOICE = "am_liam"
FMT = "mp3"

# ⛔ Assembled, never written as a literal — see the module docstring.
HOME = "/" + "home/jane"


def conditions(**moved) -> Conditions:
    settings = {"voice": VOICE, "fmt": FMT, "provides": 2, "chunk_chars": 320}
    settings.update(moved)
    return Conditions(**settings)


def one_clip() -> dict[str, Clip]:
    return {"u1": Clip("u1-aaaaaaaa.mp3", conditions().fingerprint, "kokoro", "kokoro")}


# --------------------------------------------------------------------------
# R9: refuse rather than rebuild
# --------------------------------------------------------------------------


def test_an_absent_record_is_a_state_and_not_a_failure(tmp_path):
    absent = read_state(state_file(tmp_path))
    assert absent.present is False
    assert dict(absent.clips) == {}


@pytest.mark.parametrize(
    "written",
    [
        pytest.param("not json at all", id="not-json"),
        pytest.param("[]", id="not-an-object"),
        pytest.param('{"narration_api": 1, "clips": []}', id="clips-not-an-object"),
        pytest.param('{"narration_api": true}', id="a-bool-is-not-a-version"),
        pytest.param('{"narration_api": 2}', id="a-version-this-build-cannot-speak"),
        pytest.param('{"narration_api": 1, "clips": {"u1": {"filename": "u1-a.mp3"}}}',
                     id="a-clip-with-no-conditions"),
        pytest.param('{"narration_api": 1, "clips": {"u1": 7}}', id="a-clip-that-is-not-an-object"),
    ],
)
def test_a_record_this_build_cannot_read_raises_rather_than_guessing(tmp_path, written):
    path = state_file(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(written, encoding="utf-8")
    with pytest.raises(StateError):
        read_state(path)


def test_the_refusal_is_in_the_narration_family_and_names_the_file(tmp_path):
    path = state_file(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text('{"narration_api": 2}', encoding="utf-8")
    with pytest.raises(NarrationError) as refusal:
        read_state(path)
    assert NARRATION_STATE_FILENAME in str(refusal.value)
    # ⛔ R7: the message names the contract's own filename, never a path from
    # this machine.
    assert str(tmp_path) not in str(refusal.value)


def test_a_record_this_build_does_speak_round_trips(tmp_path):
    path = state_file(tmp_path)
    write_state(path, one_clip(), conditions())
    read_back = read_state(path)
    assert read_back.present is True
    assert read_back.clips["u1"] == one_clip()["u1"]


# --------------------------------------------------------------------------
# R10 and R7
# --------------------------------------------------------------------------


def test_the_record_renders_identically_for_an_unchanged_corpus():
    assert render_state(one_clip(), conditions()) == render_state(one_clip(), conditions())


def test_the_record_carries_no_clock_and_exactly_the_fields_the_office_chose():
    document = json.loads(render_state(one_clip(), conditions()))
    assert list(document) == ["narration_api", "conditions", "clips"]
    assert document["narration_api"] == NARRATION_API
    assert list(document["conditions"]) == ["voice", "format", "provides", "chunk_chars"]
    assert list(document["clips"]["u1"]) == ["filename", "conditions", "engine", "engine_model"]


def test_the_clips_are_ordered_by_id_so_two_runs_agree():
    scrambled = {
        "u2": Clip("u2-bbbbbbbb.mp3", conditions().fingerprint),
        "u1": Clip("u1-aaaaaaaa.mp3", conditions().fingerprint),
    }
    assert list(json.loads(render_state(scrambled, conditions()))["clips"]) == ["u1", "u2"]


def test_identical_bytes_are_not_rewritten(tmp_path):
    path = state_file(tmp_path)
    assert write_state(path, one_clip(), conditions()) is True
    assert write_state(path, one_clip(), conditions()) is False
    assert not list(path.parent.glob("*.writing"))


def test_a_leak_in_the_record_refuses_before_it_reaches_disk(tmp_path):
    path = state_file(tmp_path)
    leaking = {"u1": Clip(f"{HOME}/u1-aaaaaaaa.mp3", conditions().fingerprint)}
    with pytest.raises(PersonalDataLeak):
        write_state(path, leaking, conditions())
    assert not path.exists()


def test_the_same_write_without_the_leak_lands(tmp_path):
    # ⭐ The positive control: a gate that refused everything would pass above.
    path = state_file(tmp_path)
    assert write_state(path, one_clip(), conditions()) is True
    assert path.is_file()


# --------------------------------------------------------------------------
# The conditions themselves
# --------------------------------------------------------------------------


def test_the_fingerprint_moves_with_every_recorded_condition_and_with_nothing_else():
    base = conditions().fingerprint
    assert conditions(voice="af_heart").fingerprint != base
    assert conditions(fmt="opus").fingerprint != base
    assert conditions(provides=3).fingerprint != base
    assert conditions(chunk_chars=512).fingerprint != base
    assert conditions().fingerprint == base


@pytest.mark.parametrize("missing", [{"voice": ""}, {"fmt": "  "}, {"voice": None}, {"fmt": 7}])
def test_a_record_that_cannot_say_what_a_clip_was_made_under_is_refused(missing):
    with pytest.raises(ValueError):
        conditions(**missing)


def test_conditions_are_read_off_a_probe_and_not_from_a_constant():
    # ⛔ `chunk_chars` is a deployment setting and part of the content address
    # (`NS-02`), so it is read from health rather than assumed.
    health = Health(reachable=True, detail="up", provides=2, chunk_chars=777)
    read = Conditions.of(health, voice=VOICE, fmt=FMT)
    assert (read.chunk_chars, read.provides) == (777, 2)
    with pytest.raises(TypeError):
        Conditions.of({"chunk_chars": 777}, voice=VOICE, fmt=FMT)


def test_the_record_lives_beside_the_discovery_cache_under_the_generated_root(tmp_path):
    assert state_file(tmp_path) == tmp_path / GENERATED_ROOT / NARRATION_STATE_FILENAME
