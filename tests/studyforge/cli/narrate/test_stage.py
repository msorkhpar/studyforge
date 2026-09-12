"""Mirror of `src/studyforge/cli/narrate/stage.py` (R12) — `SF-42`'s Acceptance, service-free.

⛔ **Every clause is asserted over the DISK or the TRANSPORT.** The recording
transport's `submitted` is the population *"requests nothing"* is about; the
bytes and modification times of every file under the copied corpus are the
population *"writes nothing"* is about. ⭐ Each emptiness has a positive control
beside it, because an unwired recorder and a snapshot compared with itself are
empty too.

⛔ Every case copies a `FND-04` fixture into `tmp_path`; nothing under
`tests/fixtures/` is ever written.
"""

from __future__ import annotations

import pytest

from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.generate import BuildError
from studyforge.narrate.client import NarrateClient
from studyforge.narrate.synth import StateError, state_file
from tests.studyforge.cli.narrate.service import (
    BASE,
    FMT,
    HEALTH,
    VOICE,
    FakeService,
    audio_for,
    clip_ids,
    files,
    new_clips,
    speech_ids,
)
from tests.studyforge.generate.corpora import BOTH, a_corpus


def run(root, service, *, voice=VOICE, fmt=FMT):
    client = NarrateClient(BASE, voice=voice, fmt=fmt, transport=service)
    return narrate_corpus(root, client, voice=voice, fmt=fmt)


# --------------------------------------------------------------------------
# ⛔ clips exist on disk afterwards — a reading of the disk
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_every_speech_unit_is_a_clip_file_on_disk_afterwards(tmp_path, name):
    root = a_corpus(tmp_path, name)
    before = files(root)
    run(root, FakeService())

    clips = new_clips(root, before)
    expected = speech_ids(root)
    assert expected, f"{name} declares no speech; the reading below would be vacuous"
    assert clip_ids(clips) == expected
    for clip in clips:
        assert clip.read_bytes() == audio_for(clip_ids([clip])[0])


def test_a_clip_deleted_after_the_run_turns_the_disk_reading_red(tmp_path):
    # ⭐ The control: the reading above is the disk's, so a missing file is seen
    # whatever the run reported about it.
    root = a_corpus(tmp_path, "depth1")
    before = files(root)
    narrated = run(root, FakeService())
    new_clips(root, before)[0].unlink()

    assert len(narrated.written) == len(speech_ids(root)), "the report still claims every clip"
    assert clip_ids(new_clips(root, before)) != speech_ids(root)


def test_the_service_is_probed_exactly_once_for_the_whole_corpus(tmp_path):
    root = a_corpus(tmp_path, "depth2")
    service = FakeService()
    narrated = run(root, service)

    assert len(narrated.units) > 1, "a one-unit corpus cannot tell once from once per unit"
    assert service.requests.count(HEALTH) == 1
    assert service.requests[0] == HEALTH


# --------------------------------------------------------------------------
# ⛔ re-running with no content change writes nothing and REQUESTS nothing
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_rerun_with_no_change_requests_nothing_and_writes_nothing(tmp_path, name):
    root = a_corpus(tmp_path, name)
    run(root, FakeService())
    before = files(root)

    again = FakeService()
    run(root, again)

    assert again.submitted == []
    assert again.requests == [HEALTH], "a re-run may probe once and ask for nothing else"
    assert files(root) == before


def test_the_recorder_fires_on_a_run_that_does_work(tmp_path):
    # ⭐ The control for the emptiness above.
    root = a_corpus(tmp_path, "depth1")
    first = FakeService()
    run(root, first)
    assert sorted(first.submitted) == speech_ids(root)


def test_a_provides_bump_asks_for_every_clip_again(tmp_path):
    # ⛔ The relay on the board: a `provides` bump invalidates every recorded
    # address. The record's conditions carry `provides`, so the re-run is not
    # empty — and the no-change re-run above holds only for one deployment.
    root = a_corpus(tmp_path, "depth1")
    run(root, FakeService(provides=3))
    bumped = FakeService(provides=4)
    run(root, bumped)
    assert sorted(bumped.submitted) == speech_ids(root)


# --------------------------------------------------------------------------
# ⛔ refusals: an absent service, an unreadable record, an unreadable corpus
# --------------------------------------------------------------------------


def test_an_absent_service_is_an_answer_and_nothing_is_requested_or_written(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    before = files(root)
    service = FakeService(reachable=False)

    narrated = run(root, service)

    assert narrated.health.reachable is False
    assert service.requests == [HEALTH]
    assert service.submitted == []
    assert files(root) == before


def test_an_unreadable_record_stops_before_a_single_request(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    record = state_file(root)
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("not a record", encoding="utf-8")
    service = FakeService()

    with pytest.raises(StateError):
        run(root, service)
    assert service.sent == []


def test_a_corpus_it_cannot_read_stops_before_a_single_request(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    (root / "corpus.json").write_text("{", encoding="utf-8")
    service = FakeService()

    with pytest.raises(BuildError):
        run(root, service)
    assert service.sent == []


def test_an_unstated_voice_is_refused_before_the_probe(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    service = FakeService()
    with pytest.raises(ValueError, match="voice"):
        narrate_corpus(root, NarrateClient(BASE, transport=service), voice=" ", fmt=FMT)
    assert service.sent == []


# --------------------------------------------------------------------------
# one unit's failure does not cost another its clip
# --------------------------------------------------------------------------


def test_a_service_that_goes_away_mid_corpus_keeps_what_it_placed(tmp_path):
    root = a_corpus(tmp_path, "depth2")
    before = files(root)
    narrated = run(root, FakeService(jobs=1))

    assert narrated.stopped
    kept = clip_ids(new_clips(root, before))
    assert kept and len(kept) < len(speech_ids(root))

    rest = FakeService()
    run(root, rest)
    assert sorted(rest.submitted) == sorted(set(speech_ids(root)) - set(kept))


def test_a_failed_segment_is_reported_and_leaves_no_clip(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    before = files(root)
    lost = speech_ids(root)[0]

    narrated = run(root, FakeService(failing={lost}))

    assert [speech_id for speech_id, _ in narrated.failed] == [lost]
    assert lost not in clip_ids(new_clips(root, before))
