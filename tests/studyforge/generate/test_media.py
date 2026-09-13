"""Mirror of `src/studyforge/generate/media.py` (R12).

⭐ **The clause this module exists for is `SF-37`'s Acceptance** — *"every `src`
and `href` a built page emits resolves to a file the build wrote"* — and it is
asserted over the whole site in `test_site.py`, because that is where the pages
are. ⛔ What is here is the pass's own contract: where it reads, where it puts
what it read, what it refuses, and what it names rather than inventing.

⚠️ **Three shapes neither `FND-04` fixture has are built here from a copy of
one**: a figure nested inside another block, a reference that points off this
machine, and two files that would be placed under one name. Each is a branch
this pass has, and a branch no fixture reaches is a branch no plant can kill.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

import pytest

from studyforge.corpus.placement import UNIT_MEDIA_DIRNAMES
from studyforge.generate import (
    BuildError,
    Reference,
    read_corpus,
    references,
    unit_media,
    write_media,
)
from studyforge.generate.media import MEDIA_BLOCKS
from studyforge.skills.adapter import Layout
from tests.studyforge.generate.corpora import (
    BOTH,
    FIXTURES,
    a_corpus,
    an_output,
    with_a_unit_missing,
)

#: The depth-1 fixture's one media-bearing unit, and the document it is declared in.
LESSON = "archive/depth-one/raw/prose/unit-02/lesson-1.json"
ADDRESS = ["depth-one"]
FIGURE = "media/diagram.svg"


# --------------------------------------------------------------------------
# ⭐ helpers — a fixture copy with one thing changed
# --------------------------------------------------------------------------


def rewritten(root: Path, where: str, blocks: list, video: object = None) -> Path:
    """Replace one archive document's blocks, and optionally file it a deck."""
    path = root / where
    document = json.loads(path.read_text(encoding="utf-8"))
    document["blocks"] = blocks
    if video is not None:
        document["video"] = video
    path.write_text(json.dumps(document, indent=2), encoding="utf-8")
    return root


def filed(root: Path, unit: int, name: str, body: bytes = b"<svg/>") -> Path:
    """Put one file where a unit's `local` references resolve.

    ⭐ **Asked of `Layout`**, so this test is also the behavioural pin on
    `unit_files`: a method that answered a different directory would leave the
    material somewhere the pass cannot see, and every clause below goes red.
    """
    at = Layout(root).unit_files(ADDRESS, unit) / "media" / name
    at.parent.mkdir(parents=True, exist_ok=True)
    at.write_bytes(body)
    return at


def image(src: str) -> dict:
    return {"type": "image", "src": src, "alt": "a figure", "width": None}


def built(tmp_path, root: Path):
    """Run the media pass alone over one corpus, into an output root of its own."""
    out = an_output(tmp_path)
    return unit_media(read_corpus(root), out), out


# --------------------------------------------------------------------------
# ⛔ the directories — the plan's population, not the build's
# --------------------------------------------------------------------------


#: ⛔ W268: the depth1 figure's digest, measured on the output of `e556179`,
#: before this row. A unit WITH media keeps its directory and its bytes.
DIAGRAM = ".studyforge/depth-one/units/unit-02/images/diagram.svg"
DIAGRAM_SHA256 = "ae70ec31fcb3903fb48c24c2db8d19d2097533af10e32bd41129665d8d9ac552"


def declared_directories(corpus):
    """Every media directory the corpus declares, unit by unit."""
    for _, container in corpus.maps:
        for unit in container.units:
            at = corpus.profile.unit(
                container.address, unit.n, unit.title, origin=unit.origin, label=unit.label
            )
            assert len(at.directories) == len(UNIT_MEDIA_DIRNAMES)
            yield from at.directories


@pytest.mark.parametrize("name", BOTH)
def test_a_unit_gets_a_media_directory_only_for_a_kind_it_has_files_of(tmp_path, name):
    # ⛔ W268, both ways over the population the plan declares: a directory a
    # copy filled exists, and one nothing filled was never minted.
    written, out = built(tmp_path, FIXTURES / name)
    filled = {path.parent for path in written.media}
    declared = list(declared_directories(read_corpus(FIXTURES / name)))

    assert filled <= set(declared), "a copy landed outside every declared directory"
    for directory in declared:
        assert (out / directory).is_dir() == (directory in filled), directory
    assert written.refused == ()


def test_the_media_bearing_unit_keeps_its_directory_and_its_bytes(tmp_path):
    written, out = built(tmp_path, FIXTURES / "depth1")

    assert [path.as_posix() for path in written.media] == [DIAGRAM]
    assert hashlib.sha256((out / DIAGRAM).read_bytes()).hexdigest() == DIAGRAM_SHA256


def test_a_unit_the_corpus_declares_and_nobody_built_gets_no_directories(tmp_path):
    """⛔ W268: a declared unit with no material has no file to copy, so nothing is minted.

    ⭐ It was the case `with_a_unit_missing` exposed for the old rule, when every
    declared unit got four; it now shows the opposite.
    """
    root = with_a_unit_missing(tmp_path / "in", "depth1", "archive/depth-one/raw/prose/unit-02")
    corpus = read_corpus(root)
    assert "depth-one/unit-02" in corpus.absent, "the premise: this unit has no material"

    _, out = built(tmp_path, root)

    at = corpus.profile.unit(corpus.maps[0][1].address, 2, "Reading a small graph")
    assert [directory for directory in at.directories if (out / directory).exists()] == []


def test_a_rebuild_over_an_old_output_removes_no_directory_already_there(tmp_path):
    # ⛔ R3: the empty directories an earlier build minted stay exactly as they are.
    out = an_output(tmp_path)
    corpus = read_corpus(FIXTURES / "depth1")
    declared = list(declared_directories(corpus))
    for directory in declared:
        (out / directory).mkdir(parents=True, exist_ok=True)

    written = unit_media(corpus, out)

    assert all((out / directory).is_dir() for directory in declared)
    assert written.refused == ()
    assert hashlib.sha256((out / DIAGRAM).read_bytes()).hexdigest() == DIAGRAM_SHA256


def test_a_readers_file_where_a_filled_directory_belongs_is_named_and_nothing_copied(tmp_path):
    out = an_output(tmp_path)
    corpus = read_corpus(FIXTURES / "depth1")
    at = corpus.profile.unit(corpus.maps[0][1].address, 2, "Reading a small graph")
    (out / at.images).parent.mkdir(parents=True, exist_ok=True)
    (out / at.images).write_bytes(b"a reader's own file")

    written = unit_media(corpus, out)

    assert at.images in written.refused
    assert written.media == ()
    assert (out / at.images).read_bytes() == b"a reader's own file"


def test_a_readers_own_file_where_a_media_directory_belongs_is_named_not_crashed_into(tmp_path):
    """⛔ R3 for a directory: `mkdir` on a file raises, and a build must not."""
    out = an_output(tmp_path)
    corpus = read_corpus(FIXTURES / "depth1")
    at = corpus.profile.unit(corpus.maps[0][1].address, 1, "What a triple is")
    (out / at.images).parent.mkdir(parents=True, exist_ok=True)
    (out / at.images).write_bytes(b"a reader's own file")

    written = unit_media(corpus, out)

    assert at.images in written.refused
    assert (out / at.images).read_bytes() == b"a reader's own file"


# --------------------------------------------------------------------------
# ⭐ the copy
# --------------------------------------------------------------------------


def test_the_media_bearing_fixture_has_its_figure_copied_byte_for_byte(tmp_path):
    written, out = built(tmp_path, FIXTURES / "depth1")

    origin = FIXTURES / "depth1/archive/depth-one/units/unit-02/media/diagram.svg"
    assert [path.name for path in written.media] == ["diagram.svg"]
    assert (out / written.media[0]).read_bytes() == origin.read_bytes()


def test_the_copy_lands_exactly_where_the_unit_page_addresses_it(tmp_path):
    """⭐ The pin on the three rules this module re-derives from `render.page`.

    ⛔ The href is asked of **placement**, which is what the renderer asks, and
    resolved from the page's own directory — so a copy that landed anywhere else
    is red here without any HTML being read.
    """
    _, out = built(tmp_path, FIXTURES / "depth1")
    corpus = read_corpus(FIXTURES / "depth1")

    at = corpus.profile.unit(corpus.maps[0][1].address, 2, "Reading a small graph")
    landing = (out / at.page).parent / at.href("images", "diagram.svg")
    assert landing.is_file()


def test_only_the_basename_survives_and_the_archive_directory_does_not(tmp_path):
    """⛔ `media/diagram.svg` is a fact about the archive; the page never echoes it."""
    written, out = built(tmp_path, FIXTURES / "depth1")

    assert all("media" not in path.parts for path in written.media)
    assert not (out / ".studyforge/depth-one/units/unit-02/images/media").exists()


def test_the_pass_runs_alone_over_a_corpus_root_and_writes_no_page(tmp_path):
    """⭐ Independently invocable — a reader replacing one image rebuilds no HTML."""
    out = an_output(tmp_path)

    written = write_media(FIXTURES / "depth1", out)

    assert written.media and written.pages == ()
    assert list(out.rglob("*.html")) == []


# --------------------------------------------------------------------------
# ⛔ R3, over the media pass
# --------------------------------------------------------------------------


def test_a_second_pass_over_its_own_output_recopies_every_file_it_declared(tmp_path):
    out = an_output(tmp_path)
    corpus = read_corpus(FIXTURES / "depth1")
    first = unit_media(corpus, out)
    stamps = {path: (out / path).read_bytes() for path in first.media}

    second = unit_media(corpus, out)

    assert sorted(second.media) == sorted(first.media)
    assert second.refused == ()
    assert sorted(second.replaced) == sorted(first.media)
    assert {path: (out / path).read_bytes() for path in first.media} == stamps


def test_a_readers_own_file_INSIDE_a_declared_media_directory_is_REPLACED(tmp_path):
    """⛔ **The by-path rule, pinned at the media pass too.**

    ⚠️ The plan enumerates a unit's media as a DIRECTORY, so every file the
    archive puts in one is named by the enumeration — including one a reader
    put there first, on a run where no prior output exists to be theirs.
    ⭐ Asserted so nobody has to discover it; `generate/writing.py`'s contract
    is where the rule and its price are argued.
    """
    out = an_output(tmp_path)
    corpus = read_corpus(FIXTURES / "depth1")
    at = corpus.profile.unit(corpus.maps[0][1].address, 2, "Reading a small graph")
    target = at.images / "diagram.svg"
    (out / target).parent.mkdir(parents=True, exist_ok=True)
    (out / target).write_bytes(b"a reader's own file")

    written = unit_media(corpus, out)

    assert target in written.replaced
    assert written.refused == ()
    assert (out / target).read_bytes() != b"a reader's own file"


def test_a_readers_own_file_BESIDE_a_declared_media_directory_survives(tmp_path):
    """⭐ The half that does hold: outside the footprint, R3 is absolute."""
    out = an_output(tmp_path)
    corpus = read_corpus(FIXTURES / "depth1")
    at = corpus.profile.unit(corpus.maps[0][1].address, 2, "Reading a small graph")
    beside = at.images.parent / "images-of-mine"
    (out / beside).mkdir(parents=True)
    (out / beside / "diagram.svg").write_bytes(b"a reader's own file")

    unit_media(corpus, out)
    unit_media(corpus, out)

    assert (out / beside / "diagram.svg").read_bytes() == b"a reader's own file"


# --------------------------------------------------------------------------
# ⭐ the population — what a page will actually reach for
# --------------------------------------------------------------------------


def test_a_figure_inside_another_block_is_copied_too(tmp_path):
    """⛔ `archive.blocks.walk` is the one recursion — *"a consumer that names
    `quote` itself is the next `disclosure` waiting to be forgotten"*. Neither
    fixture nests a figure, so this builds one that does."""
    root = a_corpus(tmp_path / "in", "depth1")
    rewritten(
        root,
        LESSON,
        [{"type": "disclosure", "summary": "Look", "open": False, "blocks": [image(FIGURE)]}],
    )

    written, _ = built(tmp_path, root)

    assert [path.name for path in written.media] == ["diagram.svg"]


def test_a_reference_that_points_off_this_machine_is_neither_copied_nor_named_missing(tmp_path):
    """⭐ R8: a remote file is a link the reader chooses to follow, so there is
    nothing on disk to place — and nothing absent either."""
    root = a_corpus(tmp_path / "in", "depth1")
    rewritten(root, LESSON, [image("https://example.invalid/remote.svg")])

    written, _ = built(tmp_path, root)

    assert written.media == ()
    assert written.missing == ()


def test_a_deck_and_its_poster_are_both_placed_among_the_units_video(tmp_path):
    """⚠️ The poster is a `poster=` attribute, not a `src=`, and it is a file."""
    root = a_corpus(tmp_path / "in", "depth1")
    rewritten(
        root,
        LESSON,
        [image(FIGURE)],
        video={
            "src": "media/lesson.mp4",
            "poster": "media/lesson.png",
            "mime": "video/mp4",
            "remote": None,
            "poster_remote": None,
        },
    )
    filed(root, 2, "lesson.mp4", b"mp4")
    filed(root, 2, "lesson.png", b"png")

    written, out = built(tmp_path, root)

    corpus = read_corpus(root)
    at = corpus.profile.unit(corpus.maps[0][1].address, 2, "Reading a small graph")
    assert (out / at.video / "lesson.mp4").read_bytes() == b"mp4"
    assert (out / at.video / "lesson.png").read_bytes() == b"png"
    assert sorted(path.name for path in written.media) == [
        "diagram.svg",
        "lesson.mp4",
        "lesson.png",
    ]


def test_a_poster_with_no_video_is_not_placed_because_no_page_reaches_for_it(tmp_path):
    """⛔ `render.page.section` renders the deck only when it has a `src`."""
    root = a_corpus(tmp_path / "in", "depth1")
    rewritten(
        root,
        LESSON,
        [image(FIGURE)],
        video={
            "src": None,
            "poster": "media/lesson.png",
            "mime": None,
            "remote": None,
            "poster_remote": None,
        },
    )
    filed(root, 2, "lesson.png", b"png")

    written, _ = built(tmp_path, root)

    assert [path.name for path in written.media] == ["diagram.svg"]


def test_one_file_named_twice_is_copied_once_and_is_not_its_own_refusal(tmp_path):
    """⭐ A deck and a `video` block are usually the same file, and depth2 is."""
    root = a_corpus(tmp_path / "in", "depth1")
    rewritten(
        root,
        LESSON,
        [{"type": "video", "src": "media/lesson.mp4", "title": "Once"}],
        video={
            "src": "media/lesson.mp4",
            "poster": None,
            "mime": "video/mp4",
            "remote": None,
            "poster_remote": None,
        },
    )
    filed(root, 2, "lesson.mp4", b"mp4")

    written, _ = built(tmp_path, root)

    assert [path.name for path in written.media] == ["lesson.mp4"]
    assert written.refused == ()


def test_a_file_the_archive_does_not_hold_is_NAMED_and_the_build_carries_on(tmp_path):
    """⛔ `media_skipped` is legal, and `depth2`'s third unit is exactly it.

    ⭐ The build does not stop and does not invent a file: the destination goes
    into `missing`, and `test_site.py` asserts that set is precisely the set of
    references a reader would find broken.
    """
    written, out = built(tmp_path, FIXTURES / "depth2")

    assert sorted(path.name for path in written.missing) == [
        "lifecycle.png",
        "watching-it-run.mp4",
        "watching-it-run.png",
    ]
    assert written.media == ()
    for path in written.missing:
        assert not (out / path).exists(), "a named absence is not a written file"


# --------------------------------------------------------------------------
# ⛔ the refusals
# --------------------------------------------------------------------------


def test_two_different_files_that_would_be_placed_under_one_name_are_refused(tmp_path):
    """⛔ The one media defect that is otherwise silent.

    ⚠️ Only the basename survives placement, so `media/a/plan.svg` and
    `media/b/plan.svg` render as the *same* href — whichever was copied second
    would be shown for both, on a page that renders perfectly.
    """
    root = a_corpus(tmp_path / "in", "depth1")
    rewritten(root, LESSON, [image("media/a/plan.svg"), image("media/b/plan.svg")])
    filed(root, 2, "a/plan.svg", b"first")
    filed(root, 2, "b/plan.svg", b"second")

    with pytest.raises(BuildError) as raised:
        built(tmp_path, root)

    assert "plan.svg" in str(raised.value)


def test_a_reference_leaving_the_source_root_is_refused_without_being_quoted(tmp_path):
    """⛔ R7: every value refused here is, by construction, a candidate home path."""
    root = a_corpus(tmp_path / "in", "depth1")
    rewritten(root, LESSON, [image("../../../../secrets/diagram.svg")])

    with pytest.raises(BuildError) as raised:
        built(tmp_path, root)

    assert "secrets" not in str(raised.value)
    assert "a path leaving the source root" in str(raised.value)


def test_a_figure_that_names_nothing_is_refused_rather_than_placed_as_an_empty_box(tmp_path):
    root = a_corpus(tmp_path / "in", "depth1")
    rewritten(root, LESSON, [image("   ")])

    with pytest.raises(BuildError):
        built(tmp_path, root)


# --------------------------------------------------------------------------
# ⭐ references — a reading of a document, and of no disk at all
# --------------------------------------------------------------------------


def test_references_answers_from_the_document_and_touches_nothing(tmp_path):
    document = {
        "sections": [
            {
                "blocks": [image(FIGURE), {"type": "para", "text": "no file here"}],
                "video": {"src": "media/deck.mp4", "poster": "media/deck.png"},
            }
        ]
    }

    found = list(references(document))

    assert [(one.kind, one.source) for one in found] == [
        ("images", FIGURE),
        ("video", "media/deck.mp4"),
        ("video", "media/deck.png"),
    ]


def test_a_section_that_is_not_an_object_is_skipped_rather_than_crashed_on():
    assert list(references({"sections": [None, {"blocks": [image(FIGURE)]}]})) == [
        Reference("images", FIGURE)
    ]


def test_every_block_type_the_vocabulary_gives_a_file_has_a_directory_to_go_in():
    """⭐ The clause that makes the derivation worth having, and it is forward-looking.

    ⛔ A twelfth block type carrying a `src` is a file a page will show, and
    `archive.blocks` is where one would arrive. This is red the day one does and
    no unit media directory holds it — which is a decision, not an oversight to
    be discovered by a reader meeting a broken image.

    ⚠️ **It does not distinguish the derivation from a hardcoded pair today**,
    because the two agree at this ref — see the survivor recorded in this row's
    handoff.
    """
    for name in MEDIA_BLOCKS:
        found = list(references({"sections": [{"blocks": [{"type": name, "src": FIGURE}]}]}))
        assert [one.source for one in found] == [FIGURE]
        assert found[0].kind in UNIT_MEDIA_DIRNAMES


def test_a_document_with_no_sections_reaches_for_nothing():
    assert list(references({})) == []


def test_the_pass_writes_relative_paths_a_caller_can_diff_against_the_plan(tmp_path):
    written, _ = built(tmp_path, FIXTURES / "depth1")

    assert all(isinstance(path, PurePosixPath) and not path.is_absolute() for path in written.media)
