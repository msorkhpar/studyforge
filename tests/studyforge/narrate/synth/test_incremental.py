"""The incremental pass (R4, R6).

⛔ **The headline clause is *"re-running with no content change writes nothing
AND REQUESTS NOTHING"*, so it is asserted over two populations at once** — the
`Sent` list the transport was handed, and the bytes of every file under the
corpus root. ⭐ Neither is the run's own report: a report saying *"0 synthesised"*
over stale clips is the exact failure asserted against.

⭐ **Every emptiness assertion has a positive control beside it.** An empty
request list is also what an unwired recorder returns, and an unchanged tree is
also what a snapshot compared against itself returns.

⛔ **The conditions tests are the ones a content address cannot pass.** A voice
change, a `provides` bump and a `chunk_chars` change each leave every filename
byte-identical, so each is asserted with the filenames pinned equal first.

⚠️ **The page half of *"every `<audio>` source resolves to a file on disk, both
directions"* is NOT asserted here.** The page renderer emits an audio source onto a
page. What is asserted here is the synthesis half — record ↔ disk, both ways — plus the round-trip
through `parse_clip_name`
that the renderer reads the href back through.
"""

import json
from pathlib import Path

import pytest

from studyforge.address.address import Address
from studyforge.corpus.placement.names import AUDIO_DIRNAME
from studyforge.corpus.placement.profile import profile_for
from studyforge.narrate.answers import NarrationError
from studyforge.narrate.client import NarrateClient
from studyforge.narrate.recorded.location import Superseded, audio_dir, located
from studyforge.narrate.recorded.record import (
    Clip,
    Conditions,
    State,
    StateError,
    read_state,
    state_file,
)
from studyforge.narrate.speakable.naming import digest_of, parse_clip_name
from studyforge.narrate.speakable.records import SpeechUnit
from studyforge.narrate.synth.incremental import (
    CLIP_ABSENT,
    CONDITIONS_MOVED,
    NO_RECORD,
    WORDS_MOVED,
    batches,
    plan,
    synthesise,
    wanted_name,
)
from studyforge.narrate.wire import Received, Sent

BASE = "http://127.0.0.1:8870"
VOICE = "am_liam"
FMT = "mp3"
AUDIO = b"ID3\x04\x00\x00\x00\x00\x00\x00mp3 bytes"
ARTIFACT = "c" * 64


def unit(identifier: str, said: str) -> SpeechUnit:
    return SpeechUnit(
        id=identifier, speak=said, section="s", block_path=(0,), sub_index=None, kind="paragraph"
    )


UNITS = (unit("u1", "the first sentence"), unit("u2", "the second sentence"))


def conditions(**moved) -> Conditions:
    settings = {
        "voice": VOICE,
        "fmt": FMT,
        "provides": 2,
        "chunk_chars": 320,
        "engine_model": "kokoro",
    }
    settings.update(moved)
    return Conditions(**settings)


class Recorder:
    """A transport that records what it was handed and answers from a script."""

    def __init__(self, *answers):
        self.sent: list[Sent] = []
        self._answers = list(answers)

    def __call__(self, sent: Sent) -> Received:
        self.sent.append(sent)
        if not self._answers:
            raise AssertionError("the recorder was asked for an answer it does not have")
        answer = self._answers.pop(0)
        if isinstance(answer, BaseException):
            raise answer
        return answer

    @property
    def submitted(self) -> list[str]:
        """The ids of every segment this transport was asked to synthesise."""
        asked = []
        for sent in self.sent:
            if sent.body is None:
                continue
            payload = json.loads(sent.body.decode("utf-8"))
            asked.extend(segment["id"] for segment in payload.get("segments", ()))
        return asked


def as_json(payload: object, status: int = 200) -> Received:
    return Received(status, "application/json", json.dumps(payload).encode("utf-8"))


def entry(identifier: str, status: str = "synthesised", fmt: str = FMT) -> dict:
    return {
        "id": identifier,
        "status": status,
        "artifact_id": ARTIFACT,
        "format": fmt,
        "engine": "kokoro",
        "engine_model": "kokoro",
    }


def job(*identifiers: str, fmt: str = FMT) -> list[Received]:
    """One `POST /v1/jobs` answer plus one artifact fetch per produced segment."""
    manifest = {
        "segments": [entry(identifier, fmt=fmt) for identifier in identifiers],
        "voice": VOICE,
        "format": fmt,
        "provides": 2,
    }
    return [as_json(manifest), *(Received(200, "audio/mpeg", AUDIO) for _ in identifiers)]


def build(tmp_path: Path, *answers) -> tuple[NarrateClient, Recorder, Path, Path]:
    """A client wired to a recorder, plus the two paths a pass is given."""
    recorder = Recorder(*answers)
    client = NarrateClient(BASE, voice=VOICE, fmt=FMT, transport=recorder)
    return client, recorder, tmp_path / "audio", state_file(tmp_path)


def snapshot(root: Path) -> dict[str, bytes]:
    """Every file under `root`, by relative path — the population *writes nothing* is over."""
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def first_pass(tmp_path: Path, units=UNITS) -> tuple[Path, Path]:
    """Synthesise `units` from nothing, and return the two paths."""
    client, _recorder, into, state = build(tmp_path, *job(*(item.id for item in units)))
    outcome = synthesise(units, client=client, conditions=conditions(), into=into, state=state)
    assert len(outcome.written) == len(units)
    return into, state


class Broken(NarrationError):
    """A service that went away mid-corpus."""


# --------------------------------------------------------------------------
# ⛔ The headline: nothing changed, so nothing is written and nothing is asked
# --------------------------------------------------------------------------


def test_a_rerun_with_no_change_requests_nothing_and_writes_nothing(tmp_path):
    into, state = first_pass(tmp_path)
    before = snapshot(tmp_path)

    client, recorder, _into, _state = build(tmp_path)
    outcome = synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state)

    assert recorder.sent == []
    assert snapshot(tmp_path) == before
    assert outcome.written == ()
    assert outcome.recorded is False
    assert sorted(outcome.fresh) == ["u1", "u2"]


def test_the_recorder_and_the_snapshot_both_fire_on_a_run_that_does_work(tmp_path):
    # ⭐ The positive control. An empty request list is also what an unwired
    # transport returns, and an unchanged snapshot is also what a comparison
    # against itself returns.
    before = snapshot(tmp_path)
    into, _state = first_pass(tmp_path)
    assert snapshot(tmp_path) != before
    assert len(list(into.glob(f"*.{FMT}"))) == 2


# --------------------------------------------------------------------------
# ⛔ Exactly the changed segments, over the files AND over the requests
# --------------------------------------------------------------------------


def test_a_wording_change_synthesises_exactly_the_changed_segment(tmp_path):
    into, state = first_pass(tmp_path)
    edited = (UNITS[0], unit("u2", "the second sentence, reworded"))

    client, recorder, _into, _state = build(tmp_path, *job("u2"))
    outcome = synthesise(edited, client=client, conditions=conditions(), into=into, state=state)

    assert recorder.submitted == ["u2"]
    assert [path.name for path in outcome.written] == [wanted_name(edited[1], conditions())]
    assert outcome.fresh == ("u1",)
    assert outcome.reasons == {"u2": WORDS_MOVED}


def named_by_record(root: Path, state: Path) -> set:
    """Every clip the record names — entries and superseded — located from the record alone."""
    named = set()
    for clip in read_state(state).clips.values():
        named.add(located(root, clip.where, clip.filename))
        named.update(located(root, item.where, item.filename) for item in clip.superseded)
    return named


def test_a_rewording_keeps_the_old_clip_and_the_record_still_names_every_clip(tmp_path):
    # ⛔ Nothing is deleted, and the record names every clip on disk: all 3.
    into, state = first_pass(tmp_path)
    edited = (UNITS[0], unit("u2", "the second sentence, reworded"))
    client, _recorder, _into, _state = build(tmp_path, *job("u2"))
    synthesise(edited, client=client, conditions=conditions(), into=into, state=state)

    on_disk = set(into.glob(f"*.{FMT}"))
    assert len(on_disk) == 3
    assert on_disk == named_by_record(tmp_path, state)
    assert read_state(state).clips["u2"].superseded == (
        Superseded(wanted_name(UNITS[1], conditions()), "audio"),
    )


def test_every_recorded_clip_is_a_file_located_from_the_record_alone(tmp_path):
    # ⛔ No placement is asked; the record says where.
    _into, state = first_pass(tmp_path)
    named = named_by_record(tmp_path, state)
    assert len(named) == len(UNITS)
    assert all(path is not None and path.is_file() for path in named)


def test_rewording_back_makes_the_earlier_clip_current_again(tmp_path):
    into, state = first_pass(tmp_path)
    edited = (UNITS[0], unit("u2", "the second sentence, reworded"))
    for words in (edited, UNITS):
        client, _recorder, _into, _state = build(tmp_path, *job("u2"))
        synthesise(words, client=client, conditions=conditions(), into=into, state=state)

    assert read_state(state).clips["u2"].superseded == (
        Superseded(wanted_name(edited[1], conditions()), "audio"),
    )
    assert set(into.glob(f"*.{FMT}")) == named_by_record(tmp_path, state)


def test_a_unit_whose_directory_moved_supersedes_its_clips_in_the_old_one(tmp_path):
    # ⛔ At the pass: a renumbered or renamed unit's old clips stay named.
    into, state = first_pass(tmp_path)
    moved = tmp_path / "renamed" / "audio"
    client, _recorder, _into, _state = build(tmp_path, *job("u1", "u2"))
    synthesise(UNITS, client=client, conditions=conditions(), into=moved, state=state)

    after = read_state(state)
    assert {clip.where for clip in after.clips.values()} == {"renamed/audio"}
    assert {item.where for clip in after.clips.values() for item in clip.superseded} == {"audio"}
    assert set(into.glob(f"*.{FMT}")) | set(moved.glob(f"*.{FMT}")) == named_by_record(
        tmp_path, state
    )


def as_version_1(state: Path) -> None:
    """Rewrite the record as a version-1 writer left it: no directories."""
    document = json.loads(state.read_text(encoding="utf-8"))
    document["narration_api"] = 1
    for entry in document["clips"].values():
        entry.pop("where", None)
    state.write_text(json.dumps(document), encoding="utf-8")


def test_a_version_1_record_gains_its_directories_and_nothing_is_requested(tmp_path):
    into, state = first_pass(tmp_path)
    as_version_1(state)

    client, recorder, _into, _state = build(tmp_path)
    synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state)

    assert recorder.sent == []
    after = read_state(state)
    assert sorted(after.clips) == ["u1", "u2"]
    assert {clip.where for clip in after.clips.values()} == {"audio"}
    assert json.loads(state.read_text(encoding="utf-8"))["narration_api"] == 2


def test_a_version_1_entry_no_run_can_place_is_kept_and_not_dropped(tmp_path):
    # ⛔ The MUST-NOT: an entry the run cannot place stays, unlocated, by name.
    into, state = first_pass(tmp_path)
    as_version_1(state)

    client, _recorder, _into, _state = build(tmp_path)
    synthesise(UNITS[:1], client=client, conditions=conditions(), into=into, state=state)

    after = read_state(state)
    assert sorted(after.clips) == ["u1", "u2"]
    assert (after.clips["u1"].where, after.clips["u2"].where) == ("audio", None)


def test_a_record_from_before_the_model_was_a_condition_is_stale_and_drops_nothing(tmp_path):
    # ⛔ An older record reads, never as current, and loses no
    # entry. Its fingerprints are rewritten exactly as the writer before `engine_model`
    # took them: over the conditions document with no `engine_model` key.
    third = unit("u3", "a third sentence")
    into, state = first_pass(tmp_path, units=(*UNITS, third))
    document = json.loads(state.read_text(encoding="utf-8"))
    older = {key: value for key, value in document["conditions"].items() if key != "engine_model"}
    document["conditions"] = older
    for entry_of in document["clips"].values():
        entry_of["conditions"] = digest_of(json.dumps(older, sort_keys=True, ensure_ascii=False))
    state.write_text(json.dumps(document), encoding="utf-8")

    client, recorder, _into, _state = build(tmp_path, *job("u1", "u2"))
    outcome = synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state)

    assert recorder.submitted == ["u1", "u2"]
    assert outcome.reasons == {"u1": CONDITIONS_MOVED, "u2": CONDITIONS_MOVED}
    assert sorted(read_state(state).clips) == ["u1", "u2", "u3"]


def test_an_audio_directory_outside_the_corpus_root_is_refused_before_any_request(tmp_path):
    client, recorder, _into, state = build(tmp_path / "corpus", *job("u1", "u2"))

    with pytest.raises(StateError):
        synthesise(
            UNITS, client=client, conditions=conditions(), into=tmp_path / "elsewhere", state=state
        )

    assert recorder.sent == []


def test_a_unit_added_to_a_synthesised_corpus_is_the_only_one_asked_for(tmp_path):
    into, state = first_pass(tmp_path)
    grown = (*UNITS, unit("u3", "a third sentence"))
    client, recorder, _into, _state = build(tmp_path, *job("u3"))
    outcome = synthesise(grown, client=client, conditions=conditions(), into=into, state=state)
    assert recorder.submitted == ["u3"]
    assert outcome.reasons == {"u3": NO_RECORD}


# --------------------------------------------------------------------------
# ⛔ What a content address CANNOT see, with the filenames pinned equal
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "moved",
    [
        pytest.param({"voice": "af_heart"}, id="voice"),
        pytest.param({"provides": 3}, id="provides"),
        pytest.param({"chunk_chars": 512}, id="chunk_chars"),
        pytest.param({"engine_model": "kokoro-v1.1"}, id="engine_model"),
    ],
)
def test_a_condition_moving_makes_every_clip_stale_though_no_filename_moves(tmp_path, moved):
    into, state = first_pass(tmp_path)
    now = conditions(**moved)

    # ⛔ The premise of the test: the address is unchanged in every case.
    assert [wanted_name(item, now) for item in UNITS] == [
        wanted_name(item, conditions()) for item in UNITS
    ]

    client, recorder, _into, _state = build(tmp_path, *job("u1", "u2"))
    outcome = synthesise(UNITS, client=client, conditions=now, into=into, state=state)

    assert recorder.submitted == ["u1", "u2"]
    assert outcome.fresh == ()
    assert set(outcome.reasons.values()) == {CONDITIONS_MOVED}


def test_a_format_change_moves_the_filename_and_is_caught_as_a_wording_move(tmp_path):
    into, state = first_pass(tmp_path)
    now = conditions(fmt="opus")
    client, recorder, _into, _state = build(tmp_path, *job("u1", "u2", fmt="opus"))
    outcome = synthesise(UNITS, client=client, conditions=now, into=into, state=state)
    assert recorder.submitted == ["u1", "u2"]
    assert set(outcome.reasons.values()) == {WORDS_MOVED}
    assert all(path.suffix == ".opus" for path in outcome.written)


def test_a_clip_missing_from_disk_is_stale_even_though_the_record_agrees(tmp_path):
    # ⛔ The clause a record agreeing with itself cannot supply, and the shape of
    # the "0 synthesised over stale clips" failure the Acceptance names.
    into, state = first_pass(tmp_path)
    (into / wanted_name(UNITS[0], conditions())).unlink()
    client, recorder, _into, _state = build(tmp_path, *job("u1"))
    outcome = synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state)
    assert recorder.submitted == ["u1"]
    assert outcome.reasons == {"u1": CLIP_ABSENT}


# --------------------------------------------------------------------------
# ⛔ Both directions synthesis owns, and the round-trip the renderer reads
# --------------------------------------------------------------------------


def test_the_record_and_the_disk_agree_in_both_directions(tmp_path):
    into, state = first_pass(tmp_path)
    recorded = read_state(state)
    assert {clip.filename for clip in recorded.clips.values()} == {
        path.name for path in into.glob(f"*.{FMT}")
    }
    assert set(recorded.clips) == {item.id for item in UNITS}
    for path in into.glob(f"*.{FMT}"):
        assert path.is_file()


def test_every_recorded_filename_parses_back_to_the_speech_id_it_is_filed_under(tmp_path):
    # ⭐ The page emits the href onto the page and reads it back through
    # `parse_clip_name`. This is that round-trip asserted at the record, which
    # is the half of it synthesis owns.
    _into, state = first_pass(tmp_path)
    for speech_id, clip in read_state(state).clips.items():
        parsed, _fingerprint = parse_clip_name(Path(clip.filename).stem)
        assert parsed == speech_id


def test_the_recorded_format_is_one_bare_suffix_for_the_whole_build(tmp_path):
    # ⛔ `conditions.format` is what a pure renderer reads (R10) — it cannot stat
    # a disk and must not become a second authority on the extension.
    _into, state = first_pass(tmp_path)
    document = json.loads(state.read_text(encoding="utf-8"))
    assert document["conditions"]["format"] == FMT
    assert not document["conditions"]["format"].startswith(".")
    for clip in document["clips"].values():
        assert clip["filename"].endswith(f".{document['conditions']['format']}")


# --------------------------------------------------------------------------
# ⛔ One unit's failure does not cost another its clip
# --------------------------------------------------------------------------


def test_a_batch_that_fails_leaves_the_earlier_batch_placed_and_recorded(tmp_path):
    client, recorder, into, state = build(tmp_path, *job("u1"), Broken("the service went away"))
    with pytest.raises(Broken):
        synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state, budget=1)

    assert recorder.submitted == ["u1", "u2"]
    assert list(read_state(state).clips) == ["u1"]
    assert (into / wanted_name(UNITS[0], conditions())).is_file()
    assert not (into / wanted_name(UNITS[1], conditions())).is_file()


def test_the_next_run_after_a_failure_asks_only_for_the_remainder(tmp_path):
    client, _recorder, into, state = build(tmp_path, *job("u1"), Broken("gone"))
    with pytest.raises(Broken):
        synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state, budget=1)

    client, recorder, _into, _state = build(tmp_path, *job("u2"))
    synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state, budget=1)
    assert recorder.submitted == ["u2"]


def test_a_reported_failure_leaves_the_unit_unrecorded_so_the_next_run_retries(tmp_path):
    manifest = {"segments": [entry("u1"), {"id": "u2", "status": "failed", "reason": "no voice"}]}
    client, _recorder, into, state = build(
        tmp_path, as_json(manifest), Received(200, "audio/mpeg", AUDIO)
    )
    outcome = synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state)
    assert outcome.failed == (("u2", "no voice"),)
    assert list(read_state(state).clips) == ["u1"]

    client, recorder, _into, _state = build(tmp_path, *job("u2"))
    synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state)
    assert recorder.submitted == ["u2"]


def test_a_service_answering_in_another_format_is_reported_rather_than_hidden(tmp_path):
    client, _recorder, into, state = build(tmp_path, *job("u1", "u2", fmt="opus"))
    outcome = synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state)
    assert sorted(outcome.unsettled) == ["u1", "u2"]


def test_an_unreadable_record_stops_before_a_single_request(tmp_path):
    into, state = first_pass(tmp_path)
    document = json.loads(state.read_text(encoding="utf-8"))
    document["narration_api"] = 99
    state.write_text(json.dumps(document), encoding="utf-8")
    before = snapshot(tmp_path)

    client, recorder, _into, _state = build(tmp_path)
    with pytest.raises(NarrationError):
        synthesise(UNITS, client=client, conditions=conditions(), into=into, state=state)
    assert recorder.sent == []
    assert snapshot(tmp_path) == before


# --------------------------------------------------------------------------
# ⛔ The engine is provenance, batching, and R4
# --------------------------------------------------------------------------


def test_the_engine_is_recorded_and_is_not_compared(tmp_path):
    # ⚠️ On a cache hit `engine` is the FIRST synthesis's, not what is deployed,
    # so comparing it would re-synthesise a corpus against a fact no
    # probe reports.
    into, state = first_pass(tmp_path)
    recorded = dict(read_state(state).clips)
    assert recorded["u1"].engine == "kokoro"
    recorded["u1"] = Clip(recorded["u1"].filename, recorded["u1"].conditions, "other", "other")
    assert plan(UNITS, into=into, state=State(recorded), conditions=conditions()).stale == ()


def test_batches_respect_the_budget_and_never_split_a_unit():
    units = tuple(unit(f"u{index}", "x" * 40) for index in range(5))
    made = list(batches(units, budget=100))
    assert [len(batch) for batch in made] == [2, 2, 1]
    assert [item.id for batch in made for item in batch] == [item.id for item in units]


def test_a_unit_larger_than_the_whole_budget_travels_alone():
    units = (unit("u1", "x" * 500), unit("u2", "y"))
    assert [[item.id for item in batch] for batch in batches(units, budget=10)] == [["u1"], ["u2"]]


@pytest.mark.parametrize("budget", [0, -1, True, "40"])
def test_a_budget_that_is_not_a_positive_int_is_refused(budget):
    with pytest.raises(ValueError):
        list(batches(UNITS, budget=budget))


def test_an_empty_plan_reaches_no_batch_at_all():
    assert list(batches(())) == []


def test_the_media_directory_is_the_placement_answer_rooted_and_differs_between_profiles(tmp_path):
    # `audio_dir` roots the unit's one placement answer and composes nothing.
    address = Address(("course", "module"))
    for label in (None, "7b"):
        asked = {}
        for name in ("tree", "sibling"):
            located = profile_for(name).unit(address, 1, "A unit", origin="src", label=label)
            asked[name] = audio_dir(tmp_path, located)
            assert asked[name] == tmp_path / Path(str(located.media_dir(AUDIO_DIRNAME)))
        assert asked["tree"] != asked["sibling"]


def test_a_plan_refuses_something_that_is_not_a_speech_unit(tmp_path):
    with pytest.raises(TypeError):
        plan(["u1"], into=tmp_path, state=State({}), conditions=conditions())
