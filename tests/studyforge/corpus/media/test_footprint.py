"""Mirror of `src/studyforge/corpus/media/footprint.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.address import Address
from studyforge.corpus.manifest import MediaPolicy
from studyforge.corpus.media import (
    MediaError,
    MediaFile,
    MediaFootprint,
    measure,
    measure_directories,
    verdict_for,
)
from studyforge.corpus.placement import UNIT_MEDIA_DIRNAMES, profile_for
from studyforge.narrate.synth import Clip, Conditions, Superseded, state_file, write_state

ADDRESS = Address.of("basics", "01-getting-started")


def write(root, relative, size):
    """Put `size` bytes at `relative` under `root`, making the parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)
    return path


# --------------------------------------------------------------------------
# The reading comes off the disk
# --------------------------------------------------------------------------


def test_the_footprint_is_read_from_the_files_that_are_actually_there(tmp_path):
    # ⛔ the media policy's acceptance: *the verdict is derived from the files actually on
    # disk, not from a prediction.* No rate, no unit count, no multiplication.
    write(tmp_path, "unit-01.audio/u-1-s1-abcd1234.mp3", 300)
    write(tmp_path, "unit-01.audio/u-1-s2-abcd5678.mp3", 700)
    footprint = measure_directories(tmp_path, ["unit-01.audio"])
    assert footprint.total_bytes == 1000
    assert footprint.count == 2


def test_a_corpus_that_has_generated_nothing_weighs_nothing_and_is_not_a_refusal(tmp_path):
    # ⚠️ The honest zero. ⛔ Refusing on an absent media directory would make
    # the first build of every corpus fail on the absence of the thing it was
    # about to create.
    footprint = measure_directories(tmp_path, ["unit-01.audio", "unit-01.video"])
    assert footprint.total_bytes == 0
    assert footprint.count == 0
    assert footprint.largest is None
    assert footprint.files == ()


def test_a_root_that_is_not_a_directory_is_a_different_mistake_and_is_refused(tmp_path):
    # ⛔ An absent media directory is an honest zero; a root that is not a
    # corpus at all is a caller error, and the two are not the same answer.
    with pytest.raises(MediaError):
        measure_directories(tmp_path / "no-such-root", ["unit-01.audio"])


def test_nothing_outside_the_named_directories_is_weighed(tmp_path):
    # ⭐ The population is the media directories placement minted, so a
    # corpus's own material and this framework's own pages are not in it.
    write(tmp_path, "unit-01.audio/clip.mp3", 100)
    write(tmp_path, "README.md", 5000)
    write(tmp_path, "unit-01.unit.html", 4000)
    assert measure_directories(tmp_path, ["unit-01.audio"]).total_bytes == 100


def test_files_nested_below_a_media_directory_are_weighed_too(tmp_path):
    # ⚠️ The walk is recursive: a profile or a synthesis pass that groups
    # clips into a subdirectory must not fall out of the measurement.
    write(tmp_path, "unit-01.audio/en/clip.mp3", 42)
    assert measure_directories(tmp_path, ["unit-01.audio"]).total_bytes == 42


# --------------------------------------------------------------------------
# R10 — the same reading on two machines
# --------------------------------------------------------------------------


def test_the_records_are_ordered_by_relative_posix_path(tmp_path):
    # ⛔ R10. `rglob` answers in whatever order the filesystem chooses.
    for name in ("z.mp3", "a.mp3", "m.mp3"):
        write(tmp_path, f"unit-01.audio/{name}", 1)
    paths = [
        found.path.as_posix() for found in measure_directories(tmp_path, ["unit-01.audio"]).files
    ]
    assert paths == sorted(paths)


def test_a_recorded_path_is_relative_to_the_corpus_root(tmp_path):
    # ⛔ R7. The recorded path is printed in a refusal and carried into a
    # report, so it must never begin with somebody's home directory.
    write(tmp_path, "unit-01.audio/clip.mp3", 1)
    (found,) = measure_directories(tmp_path, ["unit-01.audio"]).files
    assert found.path == PurePosixPath("unit-01.audio/clip.mp3")
    assert not found.path.is_absolute()


def test_a_directory_named_twice_is_counted_once(tmp_path):
    # ⛔ Otherwise a caller with overlapping directories inflates a total and
    # crosses a limit that was never crossed.
    write(tmp_path, "unit-01.audio/clip.mp3", 500)
    twice = measure_directories(tmp_path, ["unit-01.audio", "unit-01.audio", "."])
    assert twice.total_bytes == 500
    assert twice.count == 1


def test_a_media_directory_outside_the_corpus_root_is_refused():
    # ⛔ R7 again, from the other side: weighing an absolute directory would
    # measure something outside the corpus and record a path from this machine.
    with pytest.raises(MediaError):
        measure_directories(".", ["/" + "srv/build-artifacts/audio"])


# --------------------------------------------------------------------------
# The measured population is placement's population
# --------------------------------------------------------------------------


def test_measure_weighs_every_media_kind_placement_mints(tmp_path):
    # ⛔ The property that makes the verdict mean anything: the measured
    # population and the population `Profile.media_ignore_lines` covers are the
    # same population. A fifth kind must not leave this walk weighing four.
    unit = profile_for("sibling").unit(ADDRESS, 1, "Getting started", origin="basics/a.md")
    for kind in UNIT_MEDIA_DIRNAMES:
        write(tmp_path, unit.media_dir(kind) / "artifact.bin", 10)
    footprint = measure(tmp_path, [unit])
    assert footprint.count == len(UNIT_MEDIA_DIRNAMES)
    assert footprint.total_bytes == 10 * len(UNIT_MEDIA_DIRNAMES)


@pytest.mark.parametrize("profile", ["tree", "sibling"])
def test_the_walk_is_the_same_walk_under_either_profile(tmp_path, profile):
    # ⭐ This module has no opinion about where a profile puts media; it takes
    # the locations placement already answered with.
    unit = profile_for(profile).unit(ADDRESS, 1, "Getting started", origin="basics/a.md")
    write(tmp_path, unit.audio / "u-1-s1-abcd1234.mp3", 250)
    assert measure(tmp_path, [unit]).total_bytes == 250


def test_two_units_are_weighed_together(tmp_path):
    sibling = profile_for("sibling")
    units = [
        sibling.unit(ADDRESS, 1, "One", origin="basics/a.md"),
        sibling.unit(ADDRESS, 2, "Two", origin="basics/b.md"),
    ]
    for ordinal, unit in enumerate(units, start=1):
        write(tmp_path, unit.audio / "clip.mp3", 100 * ordinal)
    assert measure(tmp_path, units).total_bytes == 300


# --------------------------------------------------------------------------
# What a refusal will name
# --------------------------------------------------------------------------


def test_the_largest_file_is_named_and_ties_break_on_the_path():
    # ⛔ R10: the file a refusal names is the same file on two machines.
    footprint = MediaFootprint(
        (
            MediaFile(PurePosixPath("a/clip.mp3"), 900),
            MediaFile(PurePosixPath("b/clip.mp3"), 900),
            MediaFile(PurePosixPath("c/clip.mp3"), 100),
        )
    )
    assert footprint.largest.path == PurePosixPath("b/clip.mp3")


def test_every_file_over_a_limit_is_reported_and_not_only_the_first():
    # ⚠️ A corpus one file over and a corpus two hundred files over are
    # different situations, and naming only the heaviest would let the second
    # be discovered one file at a time.
    footprint = MediaFootprint(
        (
            MediaFile(PurePosixPath("a.mp3"), 50),
            MediaFile(PurePosixPath("b.mp3"), 150),
            MediaFile(PurePosixPath("c.mp3"), 250),
        )
    )
    assert [found.path.as_posix() for found in footprint.over(100)] == ["b.mp3", "c.mp3"]
    assert footprint.over(1000) == ()


def test_a_file_exactly_at_a_limit_is_not_over_it():
    # ⭐ The limit is a ceiling that may be reached. Stated, because "over"
    # and "at least" differ by exactly one file at the boundary.
    footprint = MediaFootprint((MediaFile(PurePosixPath("a.mp3"), 100),))
    assert footprint.over(100) == ()


# --------------------------------------------------------------------------
# ⛔ Every clip the narration record locates is weighed
# --------------------------------------------------------------------------

TREE = profile_for("tree")
DECLARED = TREE.unit(ADDRESS, 1, "Getting started")
#: A unit the corpus does not declare whose directory is still on disk.
REMOVED = TREE.unit(Address.of("basics", "02-removed"), 2, "Removed")
SETTINGS = Conditions(voice="voice-a", fmt="mp3", provides=3, chunk_chars=320)


def narrated(root, clips):
    """Record `clips` (speech id -> (filename, where, superseded)) as `narrate` would."""
    write_state(
        state_file(root),
        {
            speech_id: Clip(name, SETTINGS.fingerprint, where=where, superseded=older)
            for speech_id, (name, where, older) in clips.items()
        },
        SETTINGS,
    )


def a_corpus(root, *, with_removed_unit):
    """A declared unit's 100-byte clip, and optionally a removed unit's 900-byte one."""
    clips = {"u1-s1": ("u1-s1-aaaa.mp3", DECLARED.audio.as_posix(), ())}
    write(root, DECLARED.audio / "u1-s1-aaaa.mp3", 100)
    if with_removed_unit:
        clips["u2-s1"] = ("u2-s1-bbbb.mp3", REMOVED.audio.as_posix(), ())
        write(root, REMOVED.audio / "u2-s1-bbbb.mp3", 900)
    narrated(root, clips)
    return root


@pytest.mark.parametrize(
    ("with_removed_unit", "total", "refuses"), [(True, 1000, True), (False, 100, False)]
)
def test_W311_a_clip_in_a_removed_units_directory_is_weighed_both_ways(
    tmp_path, with_removed_unit, total, refuses
):
    # ⛔ The settling clause, both ways (R12): the removed unit's clip is on disk and
    # committed, so it counts; without it, nothing is invented.
    footprint = measure(a_corpus(tmp_path, with_removed_unit=with_removed_unit), [DECLARED])
    assert footprint.total_bytes == total
    assert footprint.unweighed == ()
    policy = MediaPolicy(commit="auto", max_total_bytes=500, max_file_bytes=10_000)
    assert verdict_for(policy, footprint).refuses is refuses


def test_W311_a_superseded_clip_outside_every_declared_directory_is_weighed(tmp_path):
    write(tmp_path, DECLARED.audio / "u1-s1-aaaa.mp3", 100)
    write(tmp_path, REMOVED.audio / "u1-s1-old.mp3", 40)
    older = (Superseded("u1-s1-old.mp3", REMOVED.audio.as_posix()),)
    narrated(tmp_path, {"u1-s1": ("u1-s1-aaaa.mp3", DECLARED.audio.as_posix(), older)})
    footprint = measure(tmp_path, [DECLARED])
    assert [found.path for found in footprint.files] == [
        DECLARED.audio / "u1-s1-aaaa.mp3",
        REMOVED.audio / "u1-s1-old.mp3",
    ]
    assert footprint.count == 2  # ⛔ the declared clip both paths reach is counted once


def test_W311_only_what_the_record_locates_is_added_and_an_absent_clip_weighs_nothing(tmp_path):
    # ⭐ The record locates; the walk is not widened to guess. An unrecorded file in a
    # removed unit's directory is not reached, and a recorded clip not on disk is not
    # an under-count, so it is not named either.
    write(tmp_path, REMOVED.audio / "unrecorded.mp3", 900)
    narrated(tmp_path, {"u2-s1": ("u2-s1-gone.mp3", REMOVED.audio.as_posix(), ())})
    footprint = measure(tmp_path, [DECLARED])
    assert (footprint.total_bytes, footprint.unweighed) == (0, ())


def test_W311_a_clip_the_record_cannot_locate_is_named_unless_a_weighed_directory_holds_it(
    tmp_path,
):
    # ⛔ Never a silent under-count: a version-1 entry carries no directory.
    write(tmp_path, DECLARED.audio / "u1-s1-aaaa.mp3", 100)
    narrated(
        tmp_path,
        {"u1-s1": ("u1-s1-aaaa.mp3", None, ()), "u2-s1": ("u2-s1-bbbb.mp3", None, ())},
    )
    footprint = measure(tmp_path, [DECLARED])
    assert footprint.total_bytes == 100
    (said,) = footprint.unweighed
    assert said.startswith("u2-s1's clip u2-s1-bbbb.mp3")


def test_W311_an_unreadable_record_refuses_the_reading(tmp_path):
    write(tmp_path, DECLARED.audio / "u1-s1-aaaa.mp3", 100)
    state_file(tmp_path).write_text("{", encoding="utf-8")
    with pytest.raises(MediaError, match="narration record cannot be read"):
        measure(tmp_path, [DECLARED])


def test_W311_plan_reads_the_widened_footprint_without_a_measurement_of_its_own(tmp_path):
    # ⭐ `plan` goes through `measure`, so the widening reaches it untouched.
    import json
    import shutil

    from studyforge.cli.plan import plan_for
    from studyforge.corpus.manifest import MANIFEST_FILENAME
    from tests.fixture_checks import FIXTURES

    root = tmp_path / "depth1"
    shutil.copytree(FIXTURES / "depth1", root)
    manifest = json.loads((root / MANIFEST_FILENAME).read_text("utf-8"))
    manifest["media"] = {"commit": "auto", "max_total_bytes": 500}
    (root / MANIFEST_FILENAME).write_text(json.dumps(manifest), encoding="utf-8")
    gone = ".studyforge/units/a-unit-no-longer-declared/audio"
    write(root, f"{gone}/u9-s1-cccc.mp3", 900)
    narrated(root, {"u9-s1": ("u9-s1-cccc.mp3", gone, ())})
    (said,) = footprint_lines(plan_for(root))
    assert said.startswith("media footprint  EXCEEDS — measured 900 byte(s) in 1 file(s)"), said
    narrated(root, {})
    (said,) = footprint_lines(plan_for(root))
    assert said.startswith("media footprint  measured — 0 byte(s) in 0 file(s)"), said


def footprint_lines(plan):
    """The plan's printed footprint lines."""
    return [line for line in plan.lines() if line.startswith("media footprint")]
