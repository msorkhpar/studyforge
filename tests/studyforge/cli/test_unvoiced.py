"""Mirror of `src/studyforge/cli/unvoiced.py` (R12): narration off, as the verbs read it."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

import pytest

from studyforge.cli.unvoiced import (
    NARRATED_MARK,
    is_clip,
    speaks,
    unvoiced_clips,
    voiced_pages,
)
from studyforge.generate import read_corpus, write_site
from tests.studyforge.generate.corpora import a_corpus
from tests.studyforge.generate.test_narration import narrate

CLIP = "u.b1-0123abcd.mp3"


@pytest.mark.parametrize(
    ("declared", "asked", "voiced"),
    [(True, None, True), (False, None, False), (True, False, False), (False, True, True)],
)
def test_the_run_s_answer_overrides_the_corpus_s_and_none_keeps_it(declared, asked, voiced):
    assert speaks(declared, asked) is voiced


@pytest.mark.parametrize(
    ("path", "clip"),
    [
        (f"a/audio/{CLIP}", True),
        (f"a/audio/stem/{CLIP}", True),
        ("a/audio/lecture.mp3", False),  # material a source keeps under `audio/`
        (f"a/images/{CLIP}", False),
        (CLIP, False),
    ],
)
def test_a_clip_is_a_clip_name_inside_an_audio_directory(path, clip):
    assert is_clip(PurePosixPath(path)) is clip


def test_the_predicate_withholds_clips_under_its_roots_only(tmp_path):
    inside, outside = tmp_path / "served", tmp_path / "other"
    private = unvoiced_clips([inside])
    assert private(inside / "u" / "audio" / CLIP)
    assert not private(outside / "u" / "audio" / CLIP)
    assert not private(inside / "u" / "page.html")
    assert not unvoiced_clips([])(inside / "u" / "audio" / CLIP)


def test_voiced_pages_names_every_page_that_carries_narration(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    narrate(root)
    write_site(root, root)
    corpus = read_corpus(root)
    loud = voiced_pages(corpus, root)
    assert loud and all(NARRATED_MARK in (root / page).read_text("utf-8") for page in loud)

    write_site(root, root, narration=False)
    assert voiced_pages(corpus, root) == []


def test_an_absent_page_is_not_this_refusal_s_to_name(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    assert voiced_pages(read_corpus(root), Path(tmp_path / "nothing-built")) == []
