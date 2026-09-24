"""Mirror of `src/studyforge/generate/narration.py` (R12).

The narration states, THROUGH the build: the three states over
both framework fixture corpora, each page read off disk after `write_site` or the
`build` command. The renderer's own tests are the other half and do not
discharge this one.

No narration service is involved. `narrate` below writes what `studyforge
narrate` writes, through the same `narrate.synth` calls, with planted bytes as
clips. The build is pointed at the corpus root itself, because that is the
root every plan golden and every clip path is relative to.
"""

from __future__ import annotations

import io
import json
import os
import re
from dataclasses import replace
from pathlib import Path

import pytest

from studyforge.cli.site.cli import main
from studyforge.generate import BuildError, write_narration, write_site
from studyforge.generate.declarations import read_corpus, unit_location
from studyforge.generate.narration import UNKEPT, gaps
from studyforge.narrate.playable import (
    MISFILED,
    NOT_ON_DISK,
    NOT_PLACED,
    NOT_RECORDED,
    Playable,
    Unmatched,
)
from studyforge.narrate.speakable import speakable_of
from studyforge.narrate.synth import (
    Clip,
    Conditions,
    audio_dir,
    state_file,
    wanted_name,
    write_state,
)
from studyforge.render.page import AUDIO_ATTRIBUTE
from studyforge.unit.builder import build_unit
from studyforge.validate.cli import UNUSABLE
from tests.studyforge.generate.corpora import BOTH, a_corpus, an_output

HREF = re.compile(AUDIO_ATTRIBUTE + r'="([^"]*)"')
PLAYER = '<footer id="player"'
GAP = 'data-section="narration-gap"'

#: Old enough that any write this run makes moves it.
LONG_AGO = 1_000_000_000


def narrate(root: Path, *, only: set[str] | None = None) -> list[Path]:
    """Write the record and one clip per speech unit, as `studyforge narrate` would."""
    corpus = read_corpus(root)
    settings = Conditions(voice="voice-a", fmt="mp3", provides=3, chunk_chars=320)
    clips: dict[str, Clip] = {}
    placed: list[Path] = []
    for source in corpus.units:
        if only is not None and source.key not in only:
            continue
        document = build_unit(source.directory, declared_practices=source.declared_practices)
        into = audio_dir(root, unit_location(corpus, source))
        into.mkdir(parents=True, exist_ok=True)
        for unit in speakable_of(document).units:
            name = wanted_name(unit, settings)
            clips[unit.id] = Clip(name, settings.fingerprint, "engine", "model")
            (into / name).write_bytes(b"ID3\x04\x00\x00\x00")
            placed.append(into / name)
    file = state_file(root)
    file.parent.mkdir(parents=True, exist_ok=True)
    write_state(file, clips, settings)
    return placed


def unit_pages(out: Path) -> dict[Path, str]:
    pages = {path: path.read_text(encoding="utf-8") for path in sorted(out.rglob("*.unit.html"))}
    assert pages, "no unit page was built, so every assertion below would pass over nothing"
    return pages


def not_quiet(body: str) -> list[str]:
    """What a never-narrated page must not carry. Empty is the pass condition."""
    marks = {"a narrated passage": AUDIO_ATTRIBUTE, "a player": PLAYER, "a gap notice": GAP}
    return [what for what, mark in marks.items() if mark in body]


def build(root: Path, into: Path | None = None) -> None:
    written = write_site(root, root if into is None else into)
    assert written.refused == (), "the build refused a path, so it did not build what it planned"


# --------------------------------------------------------------------------
# state 1: no record at all -> no player AND no notice
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_corpus_with_no_record_builds_pages_with_no_player_and_no_notice(tmp_path, name):
    root = a_corpus(tmp_path, name)
    assert not state_file(root).exists()

    build(root)

    for path, body in unit_pages(root).items():
        assert not_quiet(body) == [], f"{path.name} is not a clean prose page"


def test_the_no_record_arm_turns_red_on_a_planted_player(tmp_path):
    # R12's other direction: the arm above must be able to fail on a REAL page,
    # or "silently identical to a failed narration" passes it.
    root = a_corpus(tmp_path, "depth1")
    build(root)
    body = next(iter(unit_pages(root).values()))
    assert not_quiet(body) == []

    for plant, what in (
        ('<footer id="player" hidden></footer>', "a player"),
        (f'<p {AUDIO_ATTRIBUTE}="">x</p>', "a narrated passage"),
        (f"<section {GAP}></section>", "a gap notice"),
    ):
        planted = body.replace("</body>", plant + "</body>")
        assert planted != body
        assert what in not_quiet(planted)


# --------------------------------------------------------------------------
# state 2: every promised clip on disk -> a player whose sources resolve
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_every_clip_on_disk_builds_a_player_whose_sources_resolve(tmp_path, name):
    root = a_corpus(tmp_path, name)
    placed = narrate(root)
    assert placed

    build(root)

    linked = []
    for path, body in unit_pages(root).items():
        hrefs = HREF.findall(body)
        if not hrefs:
            continue
        assert PLAYER in body and GAP not in body
        for href in hrefs:
            assert href, f"{path.name} names a gap with every clip on disk"
            assert (path.parent / href).is_file(), f"{path.name} links a clip that is not there"
        linked += [(path.parent / href).resolve() for href in hrefs]
    assert sorted(linked) == sorted(clip.resolve() for clip in placed)


# --------------------------------------------------------------------------
# state 3: a promised clip absent -> the page names the gap
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_promised_clip_that_is_absent_builds_a_page_that_names_the_gap(tmp_path, name):
    root = a_corpus(tmp_path, name)
    lost = narrate(root)[0]
    lost.unlink()

    build(root)

    broken = {path: body for path, body in unit_pages(root).items() if GAP in body}
    assert len(broken) == 1, "exactly the page that lost a clip names a gap"
    ((path, body),) = broken.items()
    assert PLAYER in body
    assert HREF.findall(body).count("") == 1
    assert lost.name not in body


def test_a_unit_the_record_never_mentioned_is_quiet_rather_than_a_gap(tmp_path):
    # NOT_RECORDED is never a gap: a half-narrated corpus carries no notice.
    root = a_corpus(tmp_path, "depth1")
    first = read_corpus(root).units[0].key
    narrate(root, only={first})

    build(root)

    pages = list(unit_pages(root).values())
    assert PLAYER in pages[0] and GAP not in pages[0]
    for body in pages[1:]:
        assert not_quiet(body) == []


def test_the_gap_partition_is_the_three_unkept_states_and_never_not_recorded():
    assert UNKEPT == {NOT_PLACED, MISFILED, NOT_ON_DISK}
    reasons = (NOT_RECORDED, NOT_PLACED, MISFILED, NOT_ON_DISK)
    silent = tuple(
        Unmatched(("prose", (index,), None), f"u{index}", why) for index, why in enumerate(reasons)
    )
    playing = Playable(filenames={}, silent=silent, stale=())
    assert gaps(playing) == (("prose", (1,), None), ("prose", (2,), None), ("prose", (3,), None))


def test_a_labelled_sibling_unit_plays_from_the_directory_its_page_links(tmp_path):
    # One derivation, so the writer, the build's read and the page
    # agree on a labelled unit's audio directory, and its page links clips on disk.
    root = a_corpus(tmp_path, "depth2")
    path = sorted((root / "archive").rglob("container.json"))[0]
    record = json.loads(path.read_text("utf-8"))
    record["units"][0]["label"] = "lab"
    path.write_text(json.dumps(record), "utf-8")
    corpus = read_corpus(root)
    labelled = next(source for source in corpus.units if source.label)
    at = {
        label: unit_location(corpus, replace(labelled, label=label))
        for label in (None, labelled.label)
    }
    assert at[None].audio != at["lab"].audio, "the label moved nothing; this would be vacuous"
    narrate(root)

    build(root)

    pages = unit_pages(root)
    body = pages[root / Path(str(at["lab"].page))]
    assert [href for href in HREF.findall(body) if href], "the labelled unit's page plays nothing"
    assert GAP not in body, "the labelled unit's page names a gap over clips that are on disk"
    for page, text in pages.items():
        for href in HREF.findall(text):
            reachable = href == "" or (page.parent / href).is_file()
            assert reachable, f"{page.name} links a clip it cannot reach"


# --------------------------------------------------------------------------
# through the build command, and what a build does not do
# --------------------------------------------------------------------------


def invoke(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    return main(list(argv), out=out), out.getvalue()


def test_the_build_command_builds_a_corpus_with_no_record_exit_zero(tmp_path):
    root = a_corpus(tmp_path, "depth2")

    code, _ = invoke(str(root), "--out", str(root))

    assert code == 0
    for body in unit_pages(root).values():
        assert not_quiet(body) == []


def test_the_build_command_names_a_gap_after_narrate_lost_a_clip(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    narrate(root)[-1].unlink()

    code, _ = invoke(str(root), "--out", str(root))

    assert code == 0
    assert sum(GAP in body for body in unit_pages(root).values()) == 1


def test_an_unreadable_record_stops_the_build_before_a_page_is_written(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    state_file(root).parent.mkdir(parents=True)
    state_file(root).write_text("not a record", "utf-8")
    out = an_output(tmp_path)

    with pytest.raises(BuildError, match="narration record") as raised:
        write_site(root, out)
    assert str(tmp_path) not in str(raised.value)
    assert list(out.rglob("*.html")) == []

    code, printed = invoke(str(root), "--out", str(out))
    assert code == UNUSABLE and "Traceback" not in printed


def test_a_build_writes_no_clip_beside_the_material_and_none_under_its_output_no_page_addresses(
    tmp_path,
):
    """A build copies each clip a page addresses into its output, and no other.

    The deletion rule is about the originals beside the material, which a build
    never touches.
    """
    root = a_corpus(tmp_path, "depth1")
    placed = narrate(root)
    orphan = placed[0].parent / "an-orphan-0000abcd.mp3"
    orphan.write_bytes(b"ID3")
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
    out = an_output(tmp_path)

    build(root, out)

    assert {path: path.read_bytes() for path in root.rglob("*") if path.is_file()} == before
    copies = sorted(path.resolve() for path in out.rglob("*.mp3"))
    pages = unit_pages(out)
    hrefs = {
        (page.parent / h).resolve() for page, body in pages.items() for h in HREF.findall(body)
    }
    assert copies and copies == sorted(hrefs - {page.parent.resolve() for page in pages})
    assert list(out.rglob(orphan.name)) == []


# --------------------------------------------------------------------------
# the pass invoked alone: moved pages rewritten, unmoved pages untouched
# --------------------------------------------------------------------------


def test_rerunning_narration_rewrites_only_the_page_whose_narration_moved(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    placed = narrate(root)
    build(root)
    pages = sorted(unit_pages(root))
    for page in pages:
        os.utime(page, ns=(LONG_AGO, LONG_AGO))

    again = write_narration(root, root)

    assert again.written.pages == () and len(again.unchanged) == len(pages)
    assert all(page.stat().st_mtime_ns == LONG_AGO for page in pages)

    placed[0].unlink()
    moved = write_narration(root, root)

    assert len(moved.written.pages) == 1 and moved.written.replaced == moved.written.pages
    assert len(moved.unchanged) == len(pages) - 1
    touched = [page for page in pages if page.stat().st_mtime_ns != LONG_AGO]
    assert touched == [root / moved.written.pages[0]]
    assert GAP in touched[0].read_text(encoding="utf-8")


def test_the_pass_alone_into_an_empty_root_writes_every_unit_page(tmp_path):
    root = a_corpus(tmp_path, "depth2")
    out = an_output(tmp_path)

    alone = write_narration(root, out)

    assert alone.unchanged == () and alone.written.refused == ()
    assert len(alone.written.pages) == len(read_corpus(root).units)
