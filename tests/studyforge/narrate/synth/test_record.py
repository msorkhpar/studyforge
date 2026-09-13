"""`.studyforge/narration.json` — the R9 contract, R10's bytes and R7's gate.

⚠️ **The leak material below is assembled at run time**, like
`tests/studyforge/narrate/test_client.py`'s and for the same reason: this file is
swept by the repository hygiene check. ⛔ Nothing here came from any real
machine, account or person.
"""

import json
from pathlib import Path

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.placement.profile import GENERATED_ROOT
from studyforge.narrate.client import Health, NarrationError
from studyforge.narrate.speakable.naming import digest_of
from studyforge.narrate.synth import record as record_module
from studyforge.narrate.synth.location import Superseded
from studyforge.narrate.synth.record import (
    NARRATION_API,
    NARRATION_STATE_FILENAME,
    Clip,
    Conditions,
    StateError,
    forget,
    forget_superseded,
    read_state,
    render_state,
    state_file,
    the_one_file,
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
        # ⛔ Both carry a VALID `clips`, so the version is the only thing wrong.
        # Without it they passed on the clips check instead and a plant that
        # accepted every version left them green.
        pytest.param('{"narration_api": true, "clips": {}}', id="a-bool-is-not-a-version"),
        pytest.param('{"narration_api": 3, "clips": {}}', id="a-version-this-build-cannot-speak"),
        pytest.param(
            '{"narration_api": 1, "clips": {"u1": {"filename": "u1-a.mp3"}}}',
            id="a-clip-with-no-conditions",
        ),
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
    path.write_text('{"narration_api": 3, "clips": {}}', encoding="utf-8")
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
    assert list(document["clips"]["u1"]) == [
        "filename",
        "where",
        "conditions",
        "engine",
        "engine_model",
    ]


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


# --------------------------------------------------------------------------
# ⛔ One file and one writer, enforced — and it is not a stylistic gate
# --------------------------------------------------------------------------


@pytest.mark.parametrize("named", ["alpha", "narration.jsonl", "state.json", ".narration.json"])
def test_the_writer_refuses_any_path_that_is_not_this_contracts_one_file(tmp_path, named):
    # ⛔ MEASURED: without this, `tests/test_emission.py`'s probe — which fills
    # unprobed parameters with the word `alpha` — made `write_state` drop a file
    # called `alpha` into the repository root, and that stray file changed what
    # an UNRELATED module's scan refused. A writer pointed anywhere is a
    # contract nobody can find and a suite whose colour depends on run order.
    target = tmp_path / named
    with pytest.raises(StateError):
        write_state(target, one_clip(), conditions())
    with pytest.raises(StateError):
        read_state(target)
    assert list(tmp_path.iterdir()) == []


def test_the_one_file_itself_is_accepted_and_written(tmp_path):
    # ⭐ The positive control: a gate that refused every path would pass above.
    path = state_file(tmp_path)
    assert the_one_file(path) == path
    assert write_state(path, one_clip(), conditions()) is True
    assert path.is_file()


def test_the_refusal_says_how_to_obtain_the_right_path(tmp_path):
    with pytest.raises(StateError) as refusal:
        the_one_file(tmp_path / "alpha")
    assert "state_file" in str(refusal.value)
    assert NARRATION_STATE_FILENAME in str(refusal.value)


def test_the_fingerprint_comes_from_the_one_minter_and_is_not_a_second_truncation():
    # ⛔ `test_exactly_one_module_in_the_whole_framework_truncates_a_digest`
    # failed on this file's first draft, which computed its own. The fingerprint
    # is `speakable.naming.digest_of` over the canonical conditions.
    canonical = json.dumps(conditions().document(), sort_keys=True, ensure_ascii=False)
    assert conditions().fingerprint == digest_of(canonical)
    assert "hexdigest" not in (Path(record_module.__file__)).read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# ⛔ W218: `forget` — the smallest removal, and the record keeps one writer
# --------------------------------------------------------------------------


def two_clips() -> dict[str, Clip]:
    return {**one_clip(), "u2": Clip("u2-bbbbbbbb.mp3", conditions().fingerprint, "k", "k")}


def test_forget_removes_only_the_named_entries_and_keeps_the_conditions(tmp_path):
    record = state_file(tmp_path)
    write_state(record, two_clips(), conditions(voice="other"))

    assert forget(record, ["u2", "never-recorded"]) == ("u2",)

    assert render_state(one_clip(), conditions(voice="other")) == record.read_text("utf-8")


def test_forget_with_nothing_to_remove_writes_nothing(tmp_path):
    record = state_file(tmp_path)
    write_state(record, one_clip(), conditions())
    before = (record.read_bytes(), record.stat().st_mtime_ns)

    assert forget(record, ["absent"]) == ()
    assert (record.read_bytes(), record.stat().st_mtime_ns) == before
    assert forget(state_file(tmp_path / "none"), ["u1"]) == ()
    assert not state_file(tmp_path / "none").exists()


@pytest.mark.parametrize(
    "broken", [[], {"voice": "", "format": FMT}, {"voice": VOICE, "format": FMT, "provides": "2"}]
)
def test_forget_refuses_a_record_whose_conditions_it_cannot_carry_over(tmp_path, broken):
    record = state_file(tmp_path)
    write_state(record, two_clips(), conditions())
    payload = json.loads(record.read_text("utf-8"))
    payload["conditions"] = broken
    record.write_text(json.dumps(payload), encoding="utf-8")
    before = record.read_bytes()

    with pytest.raises(StateError):
        forget(record, ["u2"])
    assert record.read_bytes() == before


def test_forget_refuses_any_file_but_the_one_record(tmp_path):
    with pytest.raises(StateError):
        forget(tmp_path / "alpha", ["u1"])


# --------------------------------------------------------------------------
# ⛔ W226: version 2 locates every clip, and version 1 still reads
# --------------------------------------------------------------------------


def _written(tmp_path, document) -> Path:
    path = state_file(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_a_version_1_record_still_reads_and_its_entries_are_unlocated(tmp_path):
    # ⛔ The MUST-NOT: an existing record reads rather than being refused or dropped.
    entry = {"filename": "u1-aaaaaaaa.mp3", "conditions": conditions().fingerprint}
    path = _written(tmp_path, {"narration_api": 1, "clips": {"u1": entry}})

    clip = read_state(path).clips["u1"]

    assert (clip.filename, clip.where, clip.superseded) == ("u1-aaaaaaaa.mp3", None, ())


@pytest.mark.parametrize("where", ["/abs/audio", "../audio", "a/../../b"])
@pytest.mark.parametrize("place", ["entry", "superseded"])
def test_a_recorded_directory_outside_the_root_is_refused_and_not_quoted(tmp_path, where, place):
    entry = {"filename": "u1-aaaaaaaa.mp3", "where": "audio", "conditions": "f"}
    if place == "entry":
        entry["where"] = where
    else:
        entry["superseded"] = [{"filename": "u1-bbbbbbbb.mp3", "where": where}]
    path = _written(tmp_path, {"narration_api": 2, "clips": {"u1": entry}})

    with pytest.raises(StateError) as refused:
        read_state(path)

    assert where not in str(refused.value)


def test_a_superseded_clip_round_trips_and_is_written_only_when_there_is_one(tmp_path):
    fingerprint = conditions().fingerprint
    old = Superseded("u1-aaaaaaaa.mp3", "audio")
    clip = Clip("u1-bbbbbbbb.mp3", fingerprint, where="audio", superseded=(old,))
    path = state_file(tmp_path)

    write_state(path, {"u1": clip}, conditions())

    assert read_state(path).clips["u1"] == clip
    assert "superseded" not in json.loads(render_state(one_clip(), conditions()))["clips"]["u1"]
    assert list(json.loads(render_state({"u1": clip}, conditions()))["clips"]["u1"])[-1] == (
        "superseded"
    )


def test_forget_superseded_removes_only_the_named_clip_and_otherwise_writes_nothing(tmp_path):
    fingerprint = conditions().fingerprint
    first, second = Superseded("u1-aaaaaaaa.mp3", "audio"), Superseded("u1-cccccccc.mp3", "audio")
    clip = Clip("u1-bbbbbbbb.mp3", fingerprint, where="audio", superseded=(first, second))
    path = state_file(tmp_path)
    write_state(path, {"u1": clip}, conditions())

    assert forget_superseded(path, [("u1", first), ("u9", first)]) == (("u1", first),)
    assert read_state(path).clips["u1"].superseded == (second,)
    before = path.read_bytes()
    assert forget_superseded(path, [("u1", first)]) == ()
    assert path.read_bytes() == before
