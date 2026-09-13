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

import json
import re
import shutil
from pathlib import Path

import pytest

from studyforge.cli.narrate.prune import prune_corpus
from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.generate import BuildError, write_site
from studyforge.generate.declarations import read_corpus, unit_location
from studyforge.narrate.client import NarrateClient
from studyforge.narrate.synth import StateError, audio_dir, read_state, state_file
from studyforge.render.page import AUDIO_ATTRIBUTE
from tests.studyforge.cli.narrate.plant import narrated, plant_dead_entry, reword
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


# --------------------------------------------------------------------------
# ⛔ W193 answer 4: the disclosure — a PLANTED entry, and the count that moves
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_planted_dead_entry_moves_the_disclosed_count_from_zero_to_one(tmp_path, name):
    root = narrated(tmp_path, name)
    assert run(root, FakeService()).dead == (), "the control: a clean corpus discloses none"
    dead, _ = plant_dead_entry(root)

    assert run(root, FakeService()).dead == (dead,)


def test_a_reworded_passage_moves_the_superseded_count_from_zero_to_one(tmp_path):
    # ⛔ W226: the kept clip is disclosed, read off the record when the run returns.
    root = narrated(tmp_path)
    assert run(root, FakeService()).superseded == (), "the control: a clean corpus discloses none"
    reword(root)

    assert len(run(root, FakeService()).superseded) == 1


def test_the_disclosure_is_owed_when_the_service_is_absent_too(tmp_path):
    root = narrated(tmp_path)
    dead, _ = plant_dead_entry(root)
    assert run(root, FakeService(reachable=False)).dead == (dead,)


def test_a_walk_that_missed_a_declared_unit_names_it_and_deletes_nothing(tmp_path):
    root = narrated(tmp_path)
    missing = read_corpus(root).units[0]
    shutil.rmtree(missing.directory)
    before = files(root)

    done = run(root, FakeService())

    assert done.unwalked == (missing.key,)
    assert done.dead, "every entry of the unit it missed looks dead to this walk"
    assert files(root) == before


# --------------------------------------------------------------------------
# ⛔ W222: ONE derivation of a unit's audio directory, its label included
# --------------------------------------------------------------------------

LABEL = "lab"
HREF = re.compile(AUDIO_ATTRIBUTE + r'="([^"]*)"')


def label_first_unit(root: Path) -> None:
    """Give the sibling fixture's first declared unit a label, which moves its stem."""
    path = sorted((root / "archive").rglob("container.json"))[0]
    record = json.loads(path.read_text("utf-8"))
    record["units"][0]["label"] = LABEL
    path.write_text(json.dumps(record), "utf-8")


def moved(root: Path) -> tuple[Path, Path, Path]:
    """The labelled unit's audio directory without and with its label, and its page."""
    corpus = read_corpus(root)
    source = next(item for item in corpus.units if item.label == LABEL)
    at = {
        label: unit_location(
            corpus,
            source.container.address,
            source.ordinal,
            source.title,
            origin=source.origin,
            label=label,
        )
        for label in (None, LABEL)
    }
    assert at[None].audio != at[LABEL].audio, "the label moved nothing; this would be vacuous"
    return audio_dir(root, at[None]), audio_dir(root, at[LABEL]), root / Path(str(at[LABEL].page))


def test_a_labelled_sibling_units_page_links_the_clips_narrate_placed(tmp_path):
    root = a_corpus(tmp_path, "depth2")
    label_first_unit(root)
    unlabelled, labelled, page = moved(root)

    run(root, FakeService())

    assert sorted(labelled.glob(f"*.{FMT}")) and not unlabelled.exists()
    assert write_site(root, root).refused == ()
    hrefs = {
        path: [href for href in HREF.findall(path.read_text("utf-8")) if href]
        for path in sorted(root.rglob("*.unit.html"))
    }
    assert hrefs.get(page), "the labelled unit's page plays nothing"
    for path, found in hrefs.items():
        for href in found:
            assert (path.parent / href).is_file(), f"{path.name} links a clip it cannot reach"


def test_clips_left_in_a_units_old_directory_are_superseded_and_only_a_prune_deletes_them(
    tmp_path,
):
    root = a_corpus(tmp_path, "depth2")
    run(root, FakeService())
    label_first_unit(root)
    old, new, _ = moved(root)
    stranded = sorted(old.glob(f"*.{FMT}"))
    assert stranded, "nothing was narrated in the old directory; this would be vacuous"
    record = state_file(root).relative_to(root).as_posix()
    before = files(root)
    service = FakeService()

    run(root, service)

    after = files(root)
    assert {path: after.get(path) for path in before if path != record} == {
        path: value for path, value in before.items() if path != record
    }, "narrate deleted or rewrote a file other than the record"
    assert sorted(service.submitted) == clip_ids(stranded), "an unlabelled unit was re-requested"
    superseded = {
        root / item.where / item.filename
        for clip in read_state(state_file(root)).clips.values()
        for item in clip.superseded
    }
    assert superseded == set(stranded), "a clip in the old directory is orphaned"
    assert [path.name for path in sorted(new.glob(f"*.{FMT}"))] == [p.name for p in stranded]

    pruned = prune_corpus(root)

    assert sorted(pruned.deleted) == stranded
    assert not any(path.exists() for path in stranded)
    assert all((new / path.name).is_file() for path in stranded)
    assert not any(clip.superseded for clip in read_state(state_file(root)).clips.values())
