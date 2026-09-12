"""Mirror of `src/studyforge/corpus/media/verdict.py` (R12)."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.corpus.manifest import DEFAULT_MEDIA, MediaPolicy
from studyforge.corpus.media import (
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
