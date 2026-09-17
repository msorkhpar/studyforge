"""Mirror of `src/studyforge/corpus/media/verdict.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.corpus.manifest import DEFAULT_MEDIA, MediaPolicy
from studyforge.corpus.media import (
    LIMIT_COUNT,
    LIMIT_FILE,
    LIMIT_TOTAL,
    MOST_NAMED,
    WAYS_FORWARD,
    Crossing,
    MediaError,
    MediaFile,
    MediaFootprint,
    MediaVerdict,
    ignore_lines,
    require_committable,
    verdict_for,
)
from studyforge.corpus.placement import profile_for

SIBLING = profile_for("sibling")


def footprint(*sizes):
    """A footprint of one file per size, named so the order is stated."""
    return MediaFootprint(
        tuple(
            MediaFile(PurePosixPath(f"unit-{index:02d}.audio/clip.mp3"), size)
            for index, size in enumerate(sizes, start=1)
        )
    )


# --------------------------------------------------------------------------
# Under the limits, media is committed
# --------------------------------------------------------------------------


def test_a_corpus_under_the_limits_commits_its_media(tmp_path):
    # ⭐ SF-32's first acceptance clause, in the half this module can assert:
    # the verdict is *commit*, and the ignore rules do not cover the media —
    # so a clone carries the clips and plays them with nothing running (R8).
    verdict = verdict_for(DEFAULT_MEDIA, footprint(1000, 2000))
    assert verdict.commits is True
    assert verdict.refuses is False
    assert verdict.ignore_media is False
    assert not [line for line in ignore_lines(SIBLING, verdict) if line.startswith("*.audio")]


def test_auto_is_the_default_and_auto_commits():
    # ⚠️ `auto` is not "decide later". A reader treating it as undecided
    # produces the silent clone the whole policy exists to prevent.
    assert verdict_for(DEFAULT_MEDIA, footprint()).commits is True


# --------------------------------------------------------------------------
# Over a limit, it fails — naming the limit, the value and what is responsible
# --------------------------------------------------------------------------


def test_a_corpus_over_the_total_limit_fails_naming_the_limit_and_the_measured_value():
    policy = MediaPolicy(commit="auto", max_total_bytes=1000, max_file_bytes=10_000)
    verdict = verdict_for(policy, footprint(600, 700))
    assert verdict.refuses is True
    (crossing,) = verdict.crossings
    assert crossing.limit == LIMIT_TOTAL
    assert (crossing.allowed, crossing.measured) == (1000, 1300)
    assert "1300" in crossing.sentence() and "1000" in crossing.sentence()
    assert LIMIT_TOTAL in crossing.sentence()


def test_a_corpus_over_the_per_file_limit_names_the_file_responsible():
    policy = MediaPolicy(commit="auto", max_total_bytes=10_000, max_file_bytes=500)
    verdict = verdict_for(policy, footprint(100, 900))
    (crossing,) = verdict.crossings
    assert crossing.limit == LIMIT_FILE
    assert crossing.responsible == (PurePosixPath("unit-02.audio/clip.mp3"),)
    assert "unit-02.audio/clip.mp3" in crossing.sentence()


def test_crossing_two_limits_reports_both():
    # ⛔ *over any one limit* — and a corpus over both is told about both, in
    # one reading, rather than discovering the second after fixing the first.
    policy = MediaPolicy(commit="auto", max_total_bytes=1000, max_file_bytes=500)
    verdict = verdict_for(policy, footprint(600, 700))
    assert [crossing.limit for crossing in verdict.crossings] == [LIMIT_TOTAL, LIMIT_FILE]


def test_a_sentence_names_a_bounded_number_of_files_and_counts_the_rest():
    # ⚠️ A bound on the SENTENCE and never on the record.
    over = tuple(PurePosixPath(f"u{index}.audio/clip.mp3") for index in range(MOST_NAMED + 2))
    crossing = Crossing(LIMIT_FILE, 1, 9, over)
    assert f"{len(over)} file(s) over it" in crossing.sentence()
    assert "and 2 more" in crossing.sentence()
    assert crossing.responsible == over


def test_the_refusal_carries_the_number_the_limit_and_the_two_ways_forward():
    # ⭐ Crossing the ceiling is a decision, and a refusal with no way forward
    # is a wall. This is the moment the extraction source never had.
    policy = MediaPolicy(commit="auto", max_total_bytes=1, max_file_bytes=1)
    verdict = verdict_for(policy, footprint(900))
    with pytest.raises(MediaError) as raised:
        require_committable(verdict)
    message = str(raised.value)
    assert "900" in message and LIMIT_TOTAL in message
    for way in WAYS_FORWARD:
        assert way in message
    assert len(WAYS_FORWARD) == 2


def test_a_verdict_that_does_not_refuse_lets_the_build_through():
    require_committable(verdict_for(DEFAULT_MEDIA, footprint(10)))


# --------------------------------------------------------------------------
# ⛔ `auto` never silently switches
# --------------------------------------------------------------------------


def test_a_crossed_limit_does_not_change_what_is_ignored():
    # ⛔ The whole of the "never silently switches" clause, asserted as an
    # equality rather than promised in prose: a generator that quietly started
    # ignoring media would produce clones that are silent with no error.
    policy = MediaPolicy(commit="auto", max_total_bytes=1, max_file_bytes=1)
    over = verdict_for(policy, footprint(900))
    under = verdict_for(policy, footprint())
    assert over.refuses is True and under.refuses is False
    assert over.ignore_media is under.ignore_media is False
    assert ignore_lines(SIBLING, over) == ignore_lines(SIBLING, under)


def test_a_crossed_limit_does_not_flip_the_commit_answer():
    policy = MediaPolicy(commit="auto", max_total_bytes=1, max_file_bytes=1)
    assert verdict_for(policy, footprint(900)).commits is True


# --------------------------------------------------------------------------
# `always` and `never` are honoured without measurement
# --------------------------------------------------------------------------


@pytest.mark.parametrize("mode,commits", [("always", True), ("never", False)])
def test_always_and_never_are_honoured_with_no_footprint_at_all(mode, commits):
    verdict = verdict_for(MediaPolicy(commit=mode))
    assert verdict.commits is commits
    assert verdict.refuses is False
    assert verdict.footprint is None
    assert "not weighed" in verdict.report()


def test_always_is_not_second_guessed_by_a_measurement():
    # ⭐ The corpus owner's call, already taken. Even a footprint far over the
    # limits does not turn `always` into a refusal.
    policy = MediaPolicy(commit="always", max_total_bytes=1, max_file_bytes=1)
    assert verdict_for(policy, footprint(10**9)).refuses is False


def test_never_produces_the_ignore_rules_that_cover_the_media():
    verdict = verdict_for(MediaPolicy(commit="never"))
    assert verdict.ignore_media is True
    lines = ignore_lines(SIBLING, verdict)
    assert set(SIBLING.media_ignore_lines()) <= set(lines)


def test_auto_with_no_measurement_is_refused():
    # ⛔ A mode whose entire content is a comparison cannot answer with
    # nothing to compare — that would be `always` wearing another name.
    with pytest.raises(MediaError):
        verdict_for(MediaPolicy(commit="auto"))


# --------------------------------------------------------------------------
# The limits are data (R1)
# --------------------------------------------------------------------------


def test_changing_a_limit_changes_the_verdict_and_nothing_else():
    # ⭐ SF-32's last acceptance clause. One field moves; the commit answer,
    # the ignore rules and the measurement do not.
    measured = footprint(900)
    tight = MediaPolicy(commit="auto", max_total_bytes=100, max_file_bytes=100)
    loose = MediaPolicy(commit="auto", max_total_bytes=10_000, max_file_bytes=10_000)
    tight = verdict_for(tight, measured)
    loose = verdict_for(loose, measured)
    assert tight.refuses is True and loose.refuses is False
    assert tight.commits is loose.commits is True
    assert ignore_lines(SIBLING, tight) == ignore_lines(SIBLING, loose)
    assert tight.footprint is loose.footprint is measured


def test_this_module_names_no_host_and_no_forge():
    # ⛔ R1. The limits are the corpus's declaration; nothing here knows which
    # service a corpus is pushed to, or that any such service exists.
    from studyforge.corpus.media import verdict as module

    # ⚠️ This framework's own name contains the word, so it comes out first —
    # otherwise the assertion would be measuring its own package name.
    text = ((module.__doc__ or "") + "\n".join(WAYS_FORWARD)).lower().replace("studyforge", "")
    for named in ("github", "gitlab", "bitbucket", "codeberg", "sourcehut", "forge"):
        assert named not in text


def test_the_frozen_field_names_are_the_manifest_field_names():
    # ⛔ Ruling 104: the two names are frozen, and a crossing reports against
    # the field a person edits. Read off the policy rather than retyped.
    for limit in (LIMIT_TOTAL, LIMIT_FILE):
        assert hasattr(DEFAULT_MEDIA, limit)


def test_a_verdict_reports_what_was_measured():
    verdict = MediaVerdict(DEFAULT_MEDIA, footprint(100, 200))
    assert "300 byte(s) in 2 file(s)" in verdict.report()


def test_W311_what_the_reading_could_not_weigh_is_reported_by_name_and_only_then():
    # ⛔ Both ways: a footprint that names an unweighed clip says so beside the
    # total, and one that weighed everything prints no such line.
    said = "u2-s1's clip u2-s1-bbbb.mp3: the narration record carries no directory for it"
    named = MediaFootprint(footprint(100).files, (said,))
    lines = MediaVerdict(DEFAULT_MEDIA, named).lines()
    assert lines[1:] == ["media measured  100 byte(s) in 1 file(s)", f"media unweighed  {said}"]
    weighed = MediaVerdict(DEFAULT_MEDIA, footprint(100)).lines()
    assert not any("unweighed" in line for line in weighed)


# --------------------------------------------------------------------------
# The count limit — the one a corpus crosses while both byte limits are under
# --------------------------------------------------------------------------


#: Twenty-one clips of 20 KB. ⭐ 420 000 bytes against a 2 GiB total and a
#: 100 MiB per-file block: **both byte limits are comfortably under**, which is
#: the whole case for weighing the count at all.
MANY_SMALL = 21 * [20_000]

#: The byte limits a corpus of that shape would declare, chosen so that neither
#: of them can be what refuses. ⛔ Without this the count test would pass on a
#: byte crossing and prove nothing.
ROOMY_BYTES = {"max_total_bytes": 2 * 1024**3, "max_file_bytes": 100 * 1024**2}


def test_a_corpus_under_the_count_ceiling_commits_and_does_not_refuse():
    policy = MediaPolicy(commit="auto", max_files=21, **ROOMY_BYTES)
    verdict = verdict_for(policy, footprint(*MANY_SMALL))
    # ⚠️ Exactly at the ceiling is UNDER it, like both byte limits: `>` and not
    # `>=`. A corpus told it may have 21 files may have 21 files.
    assert verdict.refuses is False
    assert verdict.commits is True
    assert verdict.crossings == ()


def test_a_corpus_over_the_count_ceiling_refuses_naming_the_count():
    # ⛔ **The half of SF-32's acceptance that could not happen**: *"the file
    # **or count** responsible"*. There was no count limit to cross.
    policy = MediaPolicy(commit="auto", max_files=20, **ROOMY_BYTES)
    verdict = verdict_for(policy, footprint(*MANY_SMALL))
    (crossing,) = verdict.crossings
    assert crossing.limit == LIMIT_COUNT
    assert (crossing.allowed, crossing.measured) == (20, 21)
    assert "21 file(s)" in crossing.sentence()
    assert LIMIT_COUNT in crossing.sentence()


def test_the_count_crossing_is_the_only_one_and_neither_byte_limit_fired():
    # ⭐ The control that makes the test above mean something: with the same
    # footprint and no count ceiling, the verdict fits.
    loose = MediaPolicy(commit="auto", **ROOMY_BYTES)
    assert verdict_for(loose, footprint(*MANY_SMALL)).refuses is False


def test_a_count_crossing_is_reported_in_files_and_never_in_bytes():
    # ⛔ `21 byte(s)` for a corpus whose problem is 21 files is a right number
    # in a wrong sentence, and it sends a person looking for a size.
    policy = MediaPolicy(commit="auto", max_files=20, **ROOMY_BYTES)
    (crossing,) = verdict_for(policy, footprint(*MANY_SMALL)).crossings
    assert "byte" not in crossing.sentence()


def test_a_byte_crossing_is_still_reported_in_bytes():
    # ⭐ The control for the case above: the unit is per-crossing, not removed.
    policy = MediaPolicy(commit="auto", max_total_bytes=1000, max_file_bytes=10_000)
    (crossing,) = verdict_for(policy, footprint(600, 700)).crossings
    assert "1300 byte(s)" in crossing.sentence()


def test_an_undeclared_count_ceiling_never_refuses_however_many_files_there_are():
    # ⛔ Unstated is UNBOUNDED, not zero. This is the branch that would refuse
    # the first clip of every corpus if `None` were read as a limit.
    policy = MediaPolicy(commit="auto", **ROOMY_BYTES)
    assert policy.max_files is None
    assert verdict_for(policy, footprint(*(500 * [10]))).refuses is False
    assert verdict_for(policy, footprint(10)).refuses is False


def test_the_count_crossing_names_no_file_because_no_one_file_is_responsible():
    # ⚠️ `responsible` is empty for a limit whose subject is the whole
    # footprint — the same shape as the total-bytes crossing. Naming three of
    # twenty-one clips would point at files that are individually fine.
    policy = MediaPolicy(commit="auto", max_files=20, **ROOMY_BYTES)
    (crossing,) = verdict_for(policy, footprint(*MANY_SMALL)).crossings
    assert crossing.responsible == ()
    assert "file(s) over it" not in crossing.sentence()


def test_all_three_limits_crossed_are_reported_in_the_order_the_manifest_declares_them():
    policy = MediaPolicy(commit="auto", max_total_bytes=1000, max_file_bytes=500, max_files=1)
    verdict = verdict_for(policy, footprint(600, 700))
    assert [crossing.limit for crossing in verdict.crossings] == [
        LIMIT_TOTAL,
        LIMIT_FILE,
        LIMIT_COUNT,
    ]


def test_a_count_crossing_refuses_the_build_with_the_whole_report():
    policy = MediaPolicy(commit="auto", max_files=20, **ROOMY_BYTES)
    verdict = verdict_for(policy, footprint(*MANY_SMALL))
    with pytest.raises(MediaError) as raised:
        require_committable(verdict)
    message = str(raised.value)
    assert LIMIT_COUNT in message
    # ⭐ A refusal with no way forward is a wall; both ways are still offered
    # for the limit that has no byte in it.
    for way in WAYS_FORWARD:
        assert way in message


@pytest.mark.parametrize("mode", ["always", "never"])
def test_a_declared_mode_is_not_weighed_against_the_count_either(mode):
    # ⛔ Only `auto` consults the limits, and the third limit did not change
    # that. A `never` corpus with a million clips is a decision already taken.
    verdict = verdict_for(MediaPolicy(commit=mode, max_files=1))
    assert verdict.refuses is False
    assert verdict.footprint is None


def test_a_crossed_count_does_not_change_what_is_ignored():
    # ⛔ `auto` never silently switches — asserted as an EQUALITY, so the third
    # limit cannot become the one crossing that flips the policy.
    crossed = MediaPolicy(commit="auto", max_files=1, **ROOMY_BYTES)
    fitting = MediaPolicy(commit="auto", max_files=1000, **ROOMY_BYTES)
    measured = footprint(*MANY_SMALL)
    assert verdict_for(crossed, measured).refuses is True
    assert ignore_lines(SIBLING, verdict_for(crossed, measured)) == ignore_lines(
        SIBLING, verdict_for(fitting, measured)
    )
