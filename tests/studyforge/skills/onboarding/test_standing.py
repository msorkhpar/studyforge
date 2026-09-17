"""Mirror of `src/studyforge/skills/onboarding/standing.py` (R12).

⭐ Every figure is asserted against a corpus whose state the test MADE — ingested,
narrated through the recording fake, a clip removed, a practice declared — and
each clause both ways, so a reader that answered a constant would fail one side.
"""

from __future__ import annotations

import shutil

from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.generate import read_corpus, unit_location
from studyforge.generate.narration import recorded
from studyforge.narrate.client import NarrateClient
from studyforge.narrate.synth import audio_dir, state_file
from studyforge.skills.onboarding.standing import Standing, standing_of
from tests.studyforge.cli.narrate.service import BASE, FMT, VOICE, FakeService
from tests.studyforge.generate.corpora import a_corpus


def _narrate(root):
    client = NarrateClient(BASE, voice=VOICE, fmt=FMT, transport=FakeService())
    narrate_corpus(root, client, voice=VOICE, fmt=FMT)


def test_no_root_and_a_root_with_no_manifest_read_nothing(tmp_path):
    assert standing_of(None) == Standing()
    assert standing_of(tmp_path) == Standing()


def test_a_manifest_with_no_archive_is_not_yet_ingested(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    shutil.rmtree(root / "archive")

    assert standing_of(root) == Standing()


def test_an_ingested_corpus_with_no_record_reads_its_units_and_narrates_none(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    corpus = read_corpus(root)

    found = standing_of(root)

    assert found.read and not found.recorded
    assert found.units == len(corpus.units) > 0
    assert found.declared == sum(len(container.units) for _, container in corpus.maps)
    assert found.narrated == 0


def test_a_narrated_corpus_counts_every_unit_whose_page_plays_a_clip(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    _narrate(root)

    found = standing_of(root)

    assert found.recorded
    assert found.narrated == found.units


def test_a_unit_whose_clips_are_gone_from_disk_is_not_counted_as_narrated(tmp_path):
    # ⛔ The other way: the record still names the clips, the page plays none.
    root = a_corpus(tmp_path, "depth1")
    _narrate(root)
    corpus = read_corpus(root)
    shutil.rmtree(audio_dir(root, unit_location(corpus, corpus.units[0])))

    found = standing_of(root)

    assert recorded(root).present
    assert found.narrated == found.units - 1


def test_a_declared_unit_with_no_material_is_declared_but_not_counted(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    corpus = read_corpus(root)
    shutil.rmtree(corpus.units[0].directory)

    found = standing_of(root)

    assert found.declared == found.units + 1


def test_a_prose_corpus_needs_no_container_and_a_practice_declaring_one_does(tmp_path):
    prose = standing_of(a_corpus(tmp_path, "depth1"))
    practised = standing_of(a_corpus(tmp_path, "depth2"))

    assert prose.reading_only == prose.units and not prose.container
    assert practised.reading_only < practised.units and practised.container


def test_an_unreadable_record_is_a_refusal_carrying_no_path(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    state_file(root).parent.mkdir(parents=True, exist_ok=True)
    state_file(root).write_text("{not json", encoding="utf-8")

    found = standing_of(root)

    assert not found.read and "narration record" in found.refused
    assert str(tmp_path) not in found.refused


def test_a_container_map_the_build_refuses_is_a_refusal_not_an_exception(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    next((root / "archive").rglob("container.json")).write_text("[]", encoding="utf-8")

    found = standing_of(root)

    assert not found.read and found.refused
    assert str(tmp_path) not in found.refused
