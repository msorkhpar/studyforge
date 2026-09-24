"""Mirror of `src/studyforge/generate/footprint.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.cli.plan.report import CREATION_VERBS
from studyforge.corpus.placement import ARCHIVE_DIRNAME, AUDIO_DIRNAME
from studyforge.generate import Footprint, declared_location, footprint_for, read_corpus
from studyforge.generate.footprint import of
from tests.studyforge.generate.corpora import BOTH, GOLDEN, a_corpus

ARCHIVE = PurePosixPath(ARCHIVE_DIRNAME)


def plan_lines(name: str) -> list[str]:
    """Every `create` path the committed golden names, `/` and all.

    ⛔ **Read from the golden, never retyped** — `corpora.planned` drops the
    directory lines by filtering on a suffix, and the directories are half of
    what a footprint is made of.
    """
    lines = (GOLDEN / f"{name}.plan.txt").read_text(encoding="utf-8").splitlines()
    # ⭐ Every path line, whatever its verb, which is the whole of `Plan.paths`.
    return [line.split()[1] for line in lines if line.split(" ", 1)[0] in CREATION_VERBS]


# --------------------------------------------------------------------------
# ⛔ of — the plan's own file/directory distinction, and the one exclusion
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_every_file_the_golden_plan_names_is_owned(name):
    footprint = of(plan_lines(name), excluding=ARCHIVE)

    for path in plan_lines(name):
        if not path.endswith("/"):
            assert footprint.owns(PurePosixPath(path)), path


@pytest.mark.parametrize("name", BOTH)
def test_a_file_inside_a_directory_the_golden_plan_names_is_owned(name):
    """⭐ The plan enumerates a unit's media as a directory; a build copies
    files into it, and those files are named in no plan line."""
    footprint = of(plan_lines(name), excluding=ARCHIVE)
    directories = [path for path in plan_lines(name) if path.endswith("/")]

    for directory in directories:
        if directory.startswith(f"{ARCHIVE}/"):
            continue
        assert footprint.owns(PurePosixPath(f"{directory}anything.svg")), directory


@pytest.mark.parametrize("name", BOTH)
def test_the_archive_is_the_one_planned_directory_the_build_never_owns(name):
    """⛔ An adapter writes it (R2). Its prefix covers the source material, so
    owning it would make *"the build's own output"* mean *"everything"*."""
    footprint = of(plan_lines(name), excluding=ARCHIVE)

    assert not footprint.owns(ARCHIVE / "depth-one/unit-01/lesson.json")
    assert ARCHIVE not in footprint.directories


@pytest.mark.parametrize("name", BOTH)
def test_nothing_a_reader_owns_beside_the_output_is_claimed(name):
    footprint = of(plan_lines(name), excluding=ARCHIVE)

    for path in ("README.md", "notes.txt", "pom.xml", ".git/config", "src/Main.java"):
        assert not footprint.owns(PurePosixPath(path)), path


def test_a_sibling_directory_sharing_a_prefix_is_not_inside_it():
    """⛔ Planted: `startswith` on the string form claims `images-of-mine`."""
    footprint = of(["units/unit-01/images/"], excluding=ARCHIVE)

    assert footprint.owns(PurePosixPath("units/unit-01/images/a.svg"))
    assert not footprint.owns(PurePosixPath("units/unit-01/images-of-mine/a.svg"))


def test_a_default_footprint_owns_nothing():
    assert not Footprint().owns(PurePosixPath("index.html"))
    assert not Footprint().owns(PurePosixPath("anything/at/all"))


# --------------------------------------------------------------------------
# ⛔ footprint_for — the derivation, against a corpus on disk
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_the_derived_footprint_is_the_committed_plans_own_enumeration(tmp_path, name):
    """⭐ The acceptance that matters: one enumeration, and it is `plan`'s.

    ⛔ Compared against the GOLDEN rather than against a second `plan_for` call
    — two derivations from the same code would agree for the reason the code
    agrees with itself.
    """
    root = a_corpus(tmp_path, name)
    corpus = read_corpus(root)

    # ⭐ Which golden lines are a unit's audio directory is asked of placement
    # here, by a route of its own, against the plan's `narration` marking.
    audio = [declared_location(corpus, c, u) for _, c in corpus.maps for u in c.units]
    audio = [f"{at.media_dir(AUDIO_DIRNAME)}/" for at in audio]
    assert audio and set(audio) <= set(plan_lines(name))
    expected = of(plan_lines(name), excluding=corpus.shared.archive, narration=audio)

    assert corpus.footprint == expected
    assert corpus.footprint == footprint_for(root, corpus.profile)


@pytest.mark.parametrize("name", BOTH)
def test_every_path_a_build_writes_is_inside_the_footprint_it_derived(tmp_path, name):
    """⛔ The plan-and-build agreement from the other side: a path the build writes that the plan
    never declared would be refused on the next run and never rebuilt."""
    from studyforge.generate import write_site

    root = a_corpus(tmp_path, name)
    out = tmp_path / "out"
    out.mkdir()
    corpus = read_corpus(root)

    written = write_site(root, out)

    assert written.paths
    for path in written.paths:
        assert corpus.footprint.owns(path), path


def test_a_corpus_whose_plan_refuses_yields_a_footprint_that_owns_nothing(tmp_path):
    """⛔ An incomplete enumeration is not a footprint: the fallback is R3's
    floor, so a bad plan makes a build do too little rather than too much.

    ⛔ **The corpus is broken at a CONTAINER MAP and not at the manifest**, and
    that is what makes the clause discriminate. ⭐ Found by planting: a manifest
    broken instead leaves `plan_for` with no creations at all, so an
    implementation with the fallback deleted still returned an empty footprint
    and the plant survived a green run.
    """
    from studyforge.cli.plan import plan_for
    from studyforge.corpus.placement import profile_for

    root = a_corpus(tmp_path, "depth1")
    (root / "archive/depth-one/container.json").write_text("{ not json", encoding="utf-8")
    plan = plan_for(root)

    # ⚠️ The premise, asserted rather than assumed: this plan REFUSED and still
    # named paths, which is the only state in which the fallback does anything.
    assert plan.refusals and plan.paths

    assert footprint_for(root, profile_for("tree")) == Footprint()


# --------------------------------------------------------------------------
# ⛔ narration: an audio directory is no prefix, a clip copy is owned one by one
# --------------------------------------------------------------------------

AUDIO = "units/unit-01/audio/"
CLIP = "units/unit-01/audio/u.intro.b1-0123abcd.mp3"


def test_a_marked_audio_directory_is_no_prefix_and_a_marked_clip_is_owned_by_path():
    footprint = of(
        [AUDIO, CLIP, "units/unit-01/images/"], excluding=ARCHIVE, narration=[AUDIO, CLIP]
    )

    assert footprint.owns(PurePosixPath(CLIP))
    assert not footprint.owns(PurePosixPath(f"{AUDIO}narrates-own-0000abcd.mp3"))
    assert footprint.owns(PurePosixPath("units/unit-01/images/a.svg"))
    assert footprint.clips == {PurePosixPath(CLIP)}


def test_without_clips_owns_no_clip_and_everything_else_it_did():
    footprint = of([AUDIO, CLIP, "index.html"], excluding=ARCHIVE, narration=[AUDIO, CLIP])

    beside = footprint.without_clips()

    assert not beside.owns(PurePosixPath(CLIP))
    assert beside.owns(PurePosixPath("index.html"))
    assert beside.files == footprint.files and beside.directories == footprint.directories
