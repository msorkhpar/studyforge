"""Mirror of `src/studyforge/generate/clips.py` (R12) — `W224`'s settlement, through the build.

Every corpus here is narrated by `studyforge narrate`'s own stage against the
recording fake service in `tests/studyforge/cli/narrate/service.py` (no
network), then built and planned through the commands, and every assertion
reads pages and clips off disk.
"""

from __future__ import annotations

import io
import json
import os
import re
from pathlib import Path, PurePosixPath

import pytest

from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.cli.plan import main as plan_main
from studyforge.cli.plan import plan_for
from studyforge.cli.site.cli import main as build_main
from studyforge.corpus.placement import AUDIO_DIRNAME
from studyforge.generate import (
    BuildError,
    for_output,
    read_corpus,
    unit_clips,
    unit_location,
    write_clips,
    write_narration,
    write_site,
)
from studyforge.narrate.client import NarrateClient
from studyforge.narrate.speakable import unit_token
from studyforge.narrate.synth import forget, read_state, state_file
from studyforge.render.page import AUDIO_ATTRIBUTE
from tests.studyforge.cli.narrate.service import BASE, FMT, VOICE, FakeService
from tests.studyforge.generate.corpora import BOTH, a_corpus, an_output

HREF = re.compile(AUDIO_ATTRIBUTE + r'="([^"]*)"')
GAP = 'data-section="narration-gap"'
PLAYER = '<footer id="player"'
CLIP = f".{FMT}"

#: Old enough that any write this run makes moves it.
LONG_AGO = 1_000_000_000


def narrated(tmp_path: Path, name: str) -> tuple[Path, list[Path]]:
    """A fixture copy narrated by the real stage through the recording fake."""
    root = a_corpus(tmp_path, name)
    client = NarrateClient(BASE, voice=VOICE, fmt=FMT, transport=FakeService())
    narrate_corpus(root, client, voice=VOICE, fmt=FMT)
    clips = clip_files(root)
    assert clips, "the fake narrated nothing, so every clause below would pass over nothing"
    return root, clips


def clip_files(tree: Path) -> list[Path]:
    return sorted(path for path in tree.rglob(f"*{CLIP}") if path.is_file())


def build(root: Path, out: Path | str) -> str:
    stream = io.StringIO()
    code = build_main([str(root), "--out", str(out)], out=stream)
    assert code == 0, stream.getvalue()
    return stream.getvalue()


def addressed(out: Path) -> list[Path]:
    """Every file a built unit page's audio hrefs land on, gaps excluded."""
    pages = sorted(out.rglob("*.unit.html"))
    assert pages, "no unit page was built"
    return sorted(
        (page.parent / href).resolve()
        for page in pages
        for href in HREF.findall(page.read_text(encoding="utf-8"))
        if href
    )


def clips_of(paths) -> list[str]:
    return sorted(str(path) for path in paths if PurePosixPath(path).suffix == CLIP)


# --------------------------------------------------------------------------
# 1 — every audio href resolves under --out, and none climbs out of it
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_every_audio_href_a_page_built_elsewhere_emits_resolves_to_a_file_under_out(tmp_path, name):
    root, clips = narrated(tmp_path, name)
    out = an_output(tmp_path)

    build(root, out)

    landed = addressed(out)
    assert len(landed) == len(clips)
    for target in landed:
        assert target.is_relative_to(out.resolve()), "an href climbs out of --out"
        assert target.is_file(), "an href lands on nothing under --out"
        source = root / target.relative_to(out.resolve())
        assert target.read_bytes() == source.read_bytes()
    assert landed == [path.resolve() for path in clip_files(out)]


@pytest.mark.parametrize("name", BOTH)
def test_each_copy_lands_in_the_audio_directory_placement_names_for_its_unit(tmp_path, name):
    root, _ = narrated(tmp_path, name)
    corpus = read_corpus(root)
    asked = {
        unit_location(
            corpus,
            source.container.address,
            source.ordinal,
            source.title,
            origin=source.origin,
            label=source.label,
        ).media_dir(AUDIO_DIRNAME)
        for source in corpus.units
    }

    written = unit_clips(corpus, an_output(tmp_path))

    assert written.media and written.refused == ()
    assert {path.parent for path in written.media} <= asked


# --------------------------------------------------------------------------
# 3 — the plan enumerates the copies and the build agrees path for path
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_plan_enumerates_every_copy_and_the_build_agrees_path_for_path(tmp_path, name):
    root, clips = narrated(tmp_path, name)
    clips[0].unlink()
    stream = io.StringIO()
    assert plan_main([str(root)], out=stream) == 0
    plan = plan_for(root)
    planned = sorted(c.path for c in plan.creations if c.narration and not c.path.endswith("/"))
    printed = sorted(
        line.split()[1]
        for line in stream.getvalue().splitlines()
        if line.startswith("create ") and line.split()[1] in planned
    )

    written = write_site(root, an_output(tmp_path))
    wrote = sorted(
        line.split()[1]
        for line in build(root, an_output(tmp_path, "again")).splitlines()
        if line.startswith("wrote ") and line.endswith(CLIP)
    )

    assert printed == planned and len(planned) == len(clips)
    assert state_file(root).relative_to(root).as_posix() in plan.read_files
    assert len(clips_of(written.missing)) == 1
    assert planned == sorted(clips_of(written.media) + clips_of(written.missing))
    assert wrote == clips_of(written.media)


# --------------------------------------------------------------------------
# 4 — at --out = the corpus root nothing is copied and no clip is owned
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_at_the_corpus_root_nothing_is_copied_and_a_rebuild_leaves_narrates_clips_untouched(
    tmp_path, name
):
    root, clips = narrated(tmp_path, name)
    before = {clip: clip.read_bytes() for clip in clips}
    for clip in clips:
        os.utime(clip, ns=(LONG_AGO, LONG_AGO))

    build(root, root)
    build(root, f"{root}/../{root.name}")
    again = write_site(root, root)

    assert clips_of(again.media) == [] and again.refused == ()
    assert {clip: clip.read_bytes() for clip in clip_files(root)} == before
    assert all(clip.stat().st_mtime_ns == LONG_AGO for clip in clips)
    relative = [PurePosixPath(clip.relative_to(root).as_posix()) for clip in clips]
    corpus = read_corpus(root)
    assert all(corpus.footprint.owns(path) for path in relative), "no clip was ever owned"
    assert not any(for_output(corpus, root).footprint.owns(path) for path in relative)


# --------------------------------------------------------------------------
# 5 — a clip absent at its source is a gap; a unit never narrated is not
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_clip_absent_at_its_source_is_not_copied_and_its_page_names_the_gap(tmp_path, name):
    root, clips = narrated(tmp_path, name)
    lost = clips[-1]
    lost.unlink()
    out = an_output(tmp_path)

    build(root, out)

    assert list(out.rglob(lost.name)) == []
    assert len(clip_files(out)) == len(clips) - 1
    broken = [page for page in out.rglob("*.unit.html") if GAP in page.read_text("utf-8")]
    assert len(broken) == 1


def test_a_unit_the_record_never_mentions_is_no_gap_and_nothing_is_missing(tmp_path):
    root, clips = narrated(tmp_path, "depth1")
    corpus = read_corpus(root)
    token = unit_token(corpus.units[1].key)
    state = read_state(state_file(root))
    forgotten = [speech_id for speech_id in state.clips if speech_id.startswith(f"{token}.")]
    assert forgotten and forget(state_file(root), forgotten)
    out = an_output(tmp_path)

    written = write_clips(root, out)
    build(root, out)

    assert written.missing == ()
    assert len(clips_of(written.media)) == len(clips) - len(forgotten)
    quiet = [page for page in out.rglob("*.unit.html") if PLAYER not in page.read_text("utf-8")]
    assert len(quiet) == 1 and GAP not in quiet[0].read_text("utf-8")


# --------------------------------------------------------------------------
# must not: delete a copy on rebuild, or copy outside a unit's directory
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_rebuild_replaces_its_own_copies_and_deletes_none_the_record_stopped_naming(
    tmp_path, name
):
    root, clips = narrated(tmp_path, name)
    out = an_output(tmp_path)
    build(root, out)
    copies = sorted(clip.relative_to(out).as_posix() for clip in clip_files(out))

    again = write_site(root, out)

    assert again.refused == () and clips_of(again.replaced) == copies
    state = read_state(state_file(root))
    speech_id = sorted(state.clips)[0]
    dropped = state.clips[speech_id].filename
    forget(state_file(root), [speech_id])
    build(root, out)
    assert [path for path in clip_files(out) if path.name == dropped], "a rebuild deleted a copy"


def test_a_record_naming_a_clip_outside_its_directory_is_refused_by_plan_and_build(tmp_path):
    root, _ = narrated(tmp_path, "depth1")
    record = json.loads(state_file(root).read_text(encoding="utf-8"))
    entry = record["clips"][sorted(record["clips"])[0]]
    entry["filename"] = f"../{entry['filename']}"
    state_file(root).write_text(json.dumps(record), encoding="utf-8")

    plan = plan_for(root)
    assert [r for r in plan.refusals if r.where == ".studyforge/narration.json"]
    with pytest.raises(BuildError, match="not one file name") as raised:
        write_site(root, an_output(tmp_path))
    assert str(tmp_path) not in str(raised.value)


def test_the_narration_pass_alone_into_another_output_copies_the_clips_its_pages_address(tmp_path):
    root, clips = narrated(tmp_path, "depth2")
    out = an_output(tmp_path)

    alone = write_narration(root, out)

    assert alone.written.refused == ()
    landed = addressed(out)
    assert len(landed) == len(clips) and all(target.is_file() for target in landed)
