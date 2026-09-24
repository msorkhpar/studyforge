"""Mirror of `src/studyforge/cli/plan/media.py` (R12), and of what a plan decides with it.

⛔ **A SPLIT AT A SEAM, not a trim** (R11), and one seam serves the source
and its tests alike: everything a plan
says about **media** — the `MediaProjection` rendering, the ignore lines the
policy requires, the footprint it projects and measures, and the verdict it
refuses on — is here, while `test_report.py` and `test_derive.py` keep what a
plan says about **paths, edits and declarations**. The halves share only the
fixture copier, imported from the mirror that owns it.

⭐ **The clauses that live here:** the ignore file, the footprint is measured, what
the reading covers and what it could not weigh, and a crossed limit is a refusal
and the plan exits non-zero.
"""

from __future__ import annotations

import json
import re
from pathlib import PurePosixPath

import pytest

from studyforge.cli.plan import UNPROJECTED, plan_for
from studyforge.cli.plan.media import MEASURED_OVER, NOTHING_ON_DISK, MediaProjection
from studyforge.corpus.manifest import COMMIT_MODES, DEFAULT_MEDIA, MANIFEST_FILENAME, MediaPolicy
from studyforge.corpus.media import MediaFile, MediaFootprint
from studyforge.corpus.placement import ARCHIVE_DIRNAME as ARCHIVE_DIR
from studyforge.corpus.placement import (
    AUDIO_DIRNAME,
    GENERATED_ROOT,
    SITE_CACHE_FILENAME,
    UNIT_MEDIA_DIRNAMES,
)
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES, VALID
from tests.studyforge.cli.plan.test_derive import copy_fixture
from tests.support import init_repository, is_ignored

# --------------------------------------------------------------------------
# ⛔ the ignore file the profile requires
# --------------------------------------------------------------------------


def _with_media(name, commit, tmp_path):
    """The plan for a copy of one fixture under a stated media policy."""
    root = copy_fixture(name, tmp_path / commit)
    manifest = json.loads((root / MANIFEST_FILENAME).read_text("utf-8"))
    manifest["media"] = {"commit": commit}
    (root / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return plan_for(root)


def _clips(plan):
    """One clip in every audio directory the plan claims, whatever shape the profile gives it.

    ⛔ **Asked by SEGMENT, never by the last one**. `tree` ends an
    audio directory at `audio/`; `sibling` continues below it with the unit's
    stem, so a predicate on the final segment found every clip under one
    profile and none under the other — and *found none* reads as *nothing to
    ignore*, which is the one answer these two cases must never get for free.
    """
    return [
        f"{path}clip.mp3"
        for path in plan.paths
        if path.endswith("/") and AUDIO_DIRNAME in PurePosixPath(path).parts
    ]


def _homed(plan, repository):
    """Write the plan's lines into the file the plan names, and return the repository.

    ⛔ **Where the plan says, never the root.** The tests this replaced wrote
    the lines into a root `.gitignore`, which is the edit R3 forbids.
    """
    if plan.ignore_home is not None:
        home = repository / plan.ignore_home
        home.parent.mkdir(parents=True, exist_ok=True)
        home.write_text("\n".join(plan.ignore) + "\n", encoding="utf-8")
    return repository


@pytest.mark.parametrize("commit", COMMIT_MODES)
@pytest.mark.parametrize("name", VALID)
def test_git_ignores_no_page_no_json_and_no_archive_under_any_media_policy(name, commit, tmp_path):
    """Asked of git: no generated rule matches `*.html` or `*.json`.

    ⛔ **Pages are what a clone reads** (§5), so this holds under every
    policy, not only the default. ⚠️ The archive is the ingested record an
    adapter wrote (R2); a clone without it rebuilds nothing.

    ⚠️ **The discovery cache is not in this population**: nothing reads it
    back, so it is the one generated file a corpus does not commit — and the
    other direction is asserted below.
    """
    plan = _with_media(name, commit, tmp_path)
    repository = _homed(plan, init_repository(tmp_path / f"{name}-repo"))
    archive = next(p for p in plan.paths if p.rstrip("/").endswith(ARCHIVE_DIR))
    kept = [p for p in plan.paths if p.endswith((".html", ".json"))]
    kept = [p for p in kept if p != f"{GENERATED_ROOT}/{SITE_CACHE_FILENAME}"]
    kept += [f"{archive}some/container.json"]
    assert [p for p in kept if p.endswith(".unit.html")], "no page was asked about"
    assert [p for p in kept if is_ignored(p, cwd=repository)] == []
    # ⭐ The control, in the other direction: wherever the plan has a file
    # to put rules in, they DO cover the cache — so the clean answer above is a
    # measurement and not an empty ignore file. ⚠️ A policy whose media rules
    # have no home is refused whole (`plan.ignore_home is None`), and then the
    # corpus is not onboarded at all; `discovery.cache` is what covers a corpus
    # that reaches a serve anyway.
    covered = is_ignored(f"{GENERATED_ROOT}/{SITE_CACHE_FILENAME}", cwd=repository)
    assert covered == (plan.ignore_home is not None)


@pytest.mark.parametrize("name", VALID)
def test_committed_media_is_not_ignored_and_the_only_rules_are_the_frameworks(name, tmp_path):
    # ⭐ Generated media is committed by default (§5), and every fixture takes
    # that default. Ignoring it would produce clones that are silent with no
    # error, which is the outcome the whole media policy refuses.
    # ⭐ What the plan does print is the framework's own cache rules,
    # which no corpus adds by hand.
    plan = plan_for(FIXTURES / name)
    assert plan.ignore == (SITE_CACHE_FILENAME, f"{SITE_CACHE_FILENAME}.writing", ".gitignore")
    assert plan.ignore_home == f"{GENERATED_ROOT}/.gitignore"
    repository = _homed(plan, init_repository(tmp_path / name))
    clips = _clips(plan)
    assert clips
    assert [c for c in clips if is_ignored(c, cwd=repository)] == []


@pytest.mark.parametrize("name", VALID)
def test_media_that_is_not_committed_is_ignored_from_its_home_or_refused(name, tmp_path):
    plan = _with_media(name, "never", tmp_path)
    clips = _clips(plan)
    assert clips
    if plan.ignore_home is None:
        # ⛔ No SINGLE generated directory encloses this profile's media, and
        # the root ignore file is R3's: refused, never printed homeless.
        assert plan.ignore == ()
        refused = [refusal for refusal in plan.refusals if "never edited" in refusal.why]
        assert refused, plan.refusals
        assert plan.exit_code == INVALID
        return
    assert plan.exit_code == OK
    repository = _homed(plan, init_repository(tmp_path / f"{name}-repo"))
    assert [c for c in clips if not is_ignored(c, cwd=repository)] == []


def test_both_outcomes_are_reached_across_the_fixtures(tmp_path):
    # ⛔ And `plan` reaches them without naming either profile: it asks.
    homeless = {_with_media(name, "never", tmp_path / name).ignore_home is None for name in VALID}
    assert homeless == {True, False}


def test_no_plan_names_anything_but_a_file_inside_the_generated_root(tmp_path):
    homes = {
        _with_media(name, commit, tmp_path / name).ignore_home
        for name in VALID
        for commit in COMMIT_MODES
    }
    assert None in homes and len(homes) > 1
    outside = [h for h in homes if h is not None and PurePosixPath(h).parts[0] != GENERATED_ROOT]
    assert outside == []


def test_every_ignore_line_names_the_file_that_holds_it(tmp_path):
    # ⛔ Plan printed lines and named no file to hold them.
    plans = [_with_media(name, "never", tmp_path / name) for name in VALID]
    lines = [line for plan in plans for line in plan.lines() if line.startswith("ignore ")]
    assert lines
    assert [line for line in lines if not line.endswith(f"  in {GENERATED_ROOT}/.gitignore")] == []


# --------------------------------------------------------------------------
# the projection's rate is a parameter a person supplies
# --------------------------------------------------------------------------


def test_a_rate_turns_the_footprint_into_a_verdict():
    plan = plan_for(FIXTURES / "depth2", bytes_per_unit=2_000_000_000)
    footprint = [line for line in plan.lines() if line.startswith("media footprint")][0]
    assert "EXCEEDS max_total_bytes" in footprint


# --------------------------------------------------------------------------
# ⛔ The footprint is measured on disk, and no closed task is named as future
# --------------------------------------------------------------------------

#: A task or milestone id, which the plan must never print (`AB-32`, `M3`).
TASK_ID = re.compile(r"\b(?:[A-Z]{1,4}-\d+|M\d+)\b")


def _footprints(plan) -> list[str]:
    return [line for line in plan.lines() if line.startswith("media footprint")]


def _with_clips(tmp_path, sizes, **limits):
    """A depth1 copy holding clip files of `sizes` bytes in its first unit's audio directory."""
    from studyforge.corpus.placement import AUDIO_DIRNAME
    from studyforge.generate import read_corpus, unit_location

    root = copy_fixture("depth1", tmp_path)
    if limits:
        manifest = json.loads((root / MANIFEST_FILENAME).read_text("utf-8"))
        manifest["media"] = {"commit": "auto", **limits}
        if "max_files" in limits:
            # ⛔ R9: `media.max_files` is `corpus_api` 3's key, and the version
            # is declared rather than inferred from the keys present.
            manifest["corpus_api"] = 3
        (root / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    corpus = read_corpus(root)
    audio = root / str(unit_location(corpus, corpus.units[0]).media_dir(AUDIO_DIRNAME))
    audio.mkdir(parents=True)
    for n, size in enumerate(sizes):
        (audio / f"clip-{n}.mp3").write_bytes(b"x" * size)
    return root


def test_a_corpus_with_clips_on_disk_measures_them_and_names_no_task_as_future(tmp_path):
    plan = plan_for(_with_clips(tmp_path, (10, 20, 30)))

    assert plan.exit_code == OK
    [footprint] = _footprints(plan)
    assert footprint.startswith("media footprint  fits — measured 60 byte(s) in 3 file(s)")
    assert not TASK_ID.search(footprint), footprint


def test_a_measured_crossing_is_reported_with_the_limit_it_crossed(tmp_path):
    root = _with_clips(tmp_path, (10, 20, 30), max_total_bytes=50, max_file_bytes=25)
    [footprint] = _footprints(plan_for(root))
    assert footprint.startswith("media footprint  EXCEEDS — measured 60 byte(s) in 3 file(s)")
    assert "max_total_bytes crossed: 60 byte(s) against a limit of 50" in footprint
    assert "max_file_bytes crossed" in footprint


@pytest.mark.parametrize("name", VALID)
def test_a_corpus_with_no_media_says_so_and_names_no_task_as_future(name):
    [footprint] = _footprints(plan_for(FIXTURES / name))
    assert footprint.startswith("media footprint  measured — 0 byte(s) in 0 file(s)")
    assert "nothing is there yet" in footprint and UNPROJECTED not in footprint
    assert not TASK_ID.search(footprint), footprint


def test_a_rate_never_hides_what_is_on_disk(tmp_path):
    plan = plan_for(_with_clips(tmp_path, (40, 40), max_total_bytes=50), bytes_per_unit=1)
    projected, measured = _footprints(plan)
    assert projected.startswith("media footprint  fits — 3 byte(s) projected")
    assert measured.startswith("media footprint  EXCEEDS — measured 80 byte(s) in 2 file(s)")


@pytest.mark.parametrize("commit", ["always", "never"])
def test_a_policy_that_does_not_weigh_its_media_walks_no_disk(commit, tmp_path, monkeypatch):
    import studyforge.cli.plan.derive as derive

    def refuse(*_):
        raise AssertionError("measured a policy that weighs nothing")

    monkeypatch.setattr(derive, "measure", refuse)
    plan = _with_media("depth1", commit, tmp_path)
    assert plan.exit_code == OK
    assert plan.media is not None and plan.media.measured is None


# --------------------------------------------------------------------------
# ⛔ A crossed limit stops the plan and says so (§5), both ways
# --------------------------------------------------------------------------


def _planted(tmp_path, sizes, **limits):
    """The plan for a depth1 copy holding clips of `sizes` bytes, under its declared limits."""
    return plan_for(_with_clips(tmp_path, sizes, **limits))


def _refused(plan) -> list[str]:
    return [refusal.line() for refusal in plan.refusals]


def test_a_corpus_inside_every_limit_plans_cleanly_and_exits_zero(tmp_path):
    # ⭐ The other way round (R12): the stop is a stop and not a new floor.
    plan = _planted(tmp_path, (10, 20, 30), max_total_bytes=500, max_file_bytes=100)
    assert (plan.exit_code, plan.refusals) == (OK, ())
    assert "media footprint  fits" in "\n".join(plan.lines())


def test_a_crossed_total_exits_one_naming_the_number_and_the_limit(tmp_path):
    plan = _planted(tmp_path, (10, 20, 30), max_total_bytes=50, max_file_bytes=100)
    assert plan.exit_code == INVALID
    [refused] = _refused(plan)
    assert refused.startswith(f"refuse {MANIFEST_FILENAME}  ")
    assert "max_total_bytes crossed: 60 byte(s) against a limit of 50" in refused
    assert "a build stops here" in refused


def test_a_crossed_per_file_limit_exits_one_naming_the_file_over_it(tmp_path):
    plan = _planted(tmp_path, (10, 30), max_total_bytes=500, max_file_bytes=25)
    assert plan.exit_code == INVALID
    [refused] = _refused(plan)
    assert "max_file_bytes crossed: 30 byte(s) against a limit of 25" in refused
    assert "clip-1.mp3" in refused


def test_a_crossed_file_count_exits_one_and_is_reported_in_files(tmp_path):
    # ⛔ The third limit is not a bigger version of the first two: both byte
    # ceilings are comfortably under here, and the corpus still stops.
    plan = _planted(tmp_path, (10, 10, 10), max_total_bytes=500, max_file_bytes=100, max_files=2)
    assert plan.exit_code == INVALID
    [refused] = _refused(plan)
    assert "max_files crossed: 3 file(s) against a limit of 2" in refused


def test_every_limit_crossed_at_once_is_refused_once_each(tmp_path):
    plan = _planted(tmp_path, (10, 30, 30), max_total_bytes=50, max_file_bytes=25, max_files=2)
    assert plan.exit_code == INVALID
    assert len(plan.refusals) == 3
    assert plan.summary().endswith("3 refusal(s)")


def test_a_projection_that_crosses_is_not_a_refusal(tmp_path):
    # ⛔ A projection is a question asked at a rate, not a reading, and only a
    # measurement may decide a commit (§5). The line still says EXCEEDS.
    plan = plan_for(FIXTURES / "depth2", bytes_per_unit=2_000_000_000)
    assert (plan.exit_code, plan.refusals) == (OK, ())
    assert "EXCEEDS max_total_bytes" in _footprints(plan)[0]


@pytest.mark.parametrize("commit", ["always", "never"])
def test_a_policy_whose_limits_are_inapplicable_is_never_refused(commit, tmp_path):
    # ⛔ `verdict_for` weighs nothing for a decision already taken, and this
    # must not become a refusal invented one layer up.
    root = _with_clips(tmp_path, (10, 20, 30), max_total_bytes=1, max_file_bytes=1)
    manifest = json.loads((root / MANIFEST_FILENAME).read_text("utf-8"))
    manifest["media"] = {**manifest["media"], "commit": commit}
    (root / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    plan = plan_for(root)
    assert (plan.exit_code, plan.refusals) == (OK, ())


def test_a_reading_that_could_not_be_taken_refuses_nothing_about_the_limits(tmp_path):
    # ⭐ The record's own refusal already exits 1; an unweighed corpus must not
    # also be reported as having crossed a limit nobody measured.
    root = _with_clips(tmp_path, (10,), max_total_bytes=1, max_file_bytes=1)
    (root / ".studyforge").mkdir(exist_ok=True)
    (root / ".studyforge" / "narration.json").write_text("{not json", encoding="utf-8")
    plan = plan_for(root)
    assert plan.exit_code == INVALID
    assert [r.where for r in plan.refusals] == [".studyforge/narration.json"]


# --------------------------------------------------------------------------
# ⛔ The measured line says what it covered, and names
# what it could not weigh
# --------------------------------------------------------------------------


def _version_one_record(root, speech_id, filename):
    """A record entry that locates no directory, as version 1's entries do."""
    from studyforge.narrate.synth import Clip, Conditions, state_file, write_state

    settings = Conditions(voice="voice-a", fmt="mp3", provides=3, chunk_chars=320)
    state_file(root).parent.mkdir(parents=True, exist_ok=True)
    write_state(state_file(root), {speech_id: Clip(filename, settings.fingerprint)}, settings)


def test_the_measured_line_says_the_reading_covers_the_located_clips_too(tmp_path):
    # ⛔ The sentence was narrower than the figure beside it.
    [footprint] = _footprints(plan_for(_with_clips(tmp_path, (10,))))
    assert "under the declared units' media directories" in footprint
    assert "wherever the narration record locates a clip" in footprint


def test_a_clip_the_reading_could_not_weigh_is_named_on_its_own_line(tmp_path):
    # ⛔ A fitting total is never read as the whole corpus.
    root = _with_clips(tmp_path, (10,))
    _version_one_record(root, "u1-s1", "u1-s1-nowhere.mp3")
    lines = plan_for(root).lines()
    [said] = [line for line in lines if line.startswith("media unweighed")]
    assert "u1-s1" in said
    assert [line for line in lines if line.startswith("media footprint  fits")]


def test_a_corpus_whose_clips_are_all_weighed_says_nothing_about_unweighed(tmp_path):
    lines = plan_for(_with_clips(tmp_path, (10,))).lines()
    assert [line for line in lines if line.startswith("media unweighed")] == []


# --------------------------------------------------------------------------
# ⛔ the media projection, and whether it fits
# --------------------------------------------------------------------------


def test_with_no_rate_the_footprint_says_it_is_unprojected_and_why():
    lines = MediaProjection(DEFAULT_MEDIA, 5).lines()
    assert any(UNPROJECTED in line for line in lines)


#: A task or milestone id, which the plan must never print as a future owner.
TASK_ID = re.compile(r"\b(?:[A-Z]{1,4}-\d+|M\d+)\b")


def weighing(*sizes: int) -> MediaFootprint:
    """A measured footprint of `sizes`, as `corpus.media.measure` would return one."""
    return MediaFootprint(
        tuple(MediaFile(PurePosixPath(f"u/audio/c{n}.mp3"), size) for n, size in enumerate(sizes))
    )


def test_no_footprint_sentence_names_a_task_as_the_owner_of_the_measurement():
    # ⛔ The sentence must never name a task as the future owner on a corpus
    # with clips on disk. Every form the line can take is read, not only the
    # constant.
    policy = MediaPolicy("auto", 50, 25)
    projections = (
        MediaProjection(policy, 5),
        MediaProjection(policy, 5, measured=weighing()),
        MediaProjection(policy, 5, measured=weighing(10)),
        MediaProjection(policy, 5, measured=weighing(40, 40)),
        MediaProjection(policy, 5, bytes_per_unit=1, measured=weighing(10)),
        MediaProjection(policy, 5, unmeasured="the corpus root is not a directory"),
    )
    said = [line for p in projections for line in p.lines() if line.startswith("media footprint")]
    assert len(said) == len(projections) + 1
    assert [line for line in said if TASK_ID.search(line)] == []
    assert not TASK_ID.search(UNPROJECTED) and not TASK_ID.search(NOTHING_ON_DISK)


def test_a_measurement_is_printed_with_its_verdict_in_both_directions():
    policy = MediaPolicy("auto", 50, 25)
    fits = MediaProjection(policy, 1, measured=weighing(10, 20)).lines()[-1]
    exceeds = MediaProjection(policy, 1, measured=weighing(10, 30, 20)).lines()[-1]
    empty = MediaProjection(policy, 1, measured=weighing()).lines()[-1]
    assert fits.startswith("media footprint  fits — measured 30 byte(s) in 2 file(s)")
    assert exceeds.startswith("media footprint  EXCEEDS — measured 60 byte(s) in 3 file(s)")
    assert "max_total_bytes crossed" in exceeds and "u/audio/c1.mp3" in exceeds
    assert empty.endswith(f"measured — 0 byte(s) in 0 file(s) {MEASURED_OVER}; {NOTHING_ON_DISK}")


def test_a_refused_reading_says_why_and_is_never_printed_as_zero():
    line = MediaProjection(DEFAULT_MEDIA, 1, unmeasured="no root").lines()[-1]
    assert line == "media footprint  not measured — no root"


def test_a_rate_that_fits_says_so_with_both_numbers():
    projection = MediaProjection(MediaPolicy("auto", 1000, 100), units=4, bytes_per_unit=200)
    footprint = [line for line in projection.lines() if line.startswith("media footprint")][0]
    assert projection.total == 800
    assert "fits" in footprint and "800" in footprint and "1000" in footprint


def test_a_rate_that_does_not_fit_names_the_number_and_the_limit_it_crossed():
    projection = MediaProjection(MediaPolicy("auto", 1000, 100), units=4, bytes_per_unit=400)
    footprint = [line for line in projection.lines() if line.startswith("media footprint")][0]
    assert "EXCEEDS max_total_bytes" in footprint
    assert "1600" in footprint and "1000" in footprint


def test_the_unit_count_is_reported_even_when_the_footprint_is_not():
    # ⭐ "Will this corpus's audio fit in git?" has a knowable half before the
    # gigabytes exist, and it is printed rather than withheld with the rest.
    lines = MediaProjection(DEFAULT_MEDIA, 17).lines()
    assert any(line.startswith("media units 17") for line in lines)


def test_the_media_kinds_come_from_placements_own_tuple():
    # ⛔ Never retyped: a fifth kind must not leave this sentence listing four.
    units = [line for line in MediaProjection(DEFAULT_MEDIA, 1).lines() if "units" in line][0]
    for kind in UNIT_MEDIA_DIRNAMES:
        assert kind in units


@pytest.mark.parametrize("commit", ["always", "never"])
def test_only_auto_consults_the_limits_and_the_others_say_so(commit):
    lines = MediaProjection(MediaPolicy(commit, 1, 1), 3).lines()
    assert any("not consulted" in line for line in lines)
    assert not any(line.startswith("media limit ") for line in lines)


def test_media_is_ignored_only_when_the_policy_does_not_commit_it():
    # ⛔ Generated media is committed by DEFAULT (§5). A framework that ignored
    # a corpus's narration by reflex produces clones that are silent with no
    # error, which is the outcome the whole policy exists to refuse.
    assert MediaProjection(DEFAULT_MEDIA, 1).ignored is False
    assert MediaProjection(MediaPolicy("always", 1, 1), 1).ignored is False
    assert MediaProjection(MediaPolicy("never", 1, 1), 1).ignored is True


def test_the_media_units_line_says_a_directory_is_made_only_when_filled():
    units = [line for line in MediaProjection(DEFAULT_MEDIA, 1).lines() if "units" in line][0]
    assert "made only when a build copies a file into it" in units
