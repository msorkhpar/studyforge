"""Mirror of `src/studyforge/skills/execution/standalone/preflight.py` (R12).

⭐ The fixtures are `test_write`'s and `test_profile_export`'s: a git checkout of a corpus,
a synthetic toolchain that answers as the real one does, and a lock. ⛔ Every refusal here is
asked for with the others beside it, because the point of the module is that one run names
them all.
"""

from __future__ import annotations

import pytest

from studyforge.skills.delivery import LOG
from studyforge.skills.delivery.finding import Claim, Finding
from studyforge.skills.delivery.findings_log import Disposition, Entry
from studyforge.skills.delivery.refusal import PREAMBLE
from studyforge.skills.execution.standalone import preflight, write
from tests.studyforge.skills.execution.standalone import test_profile_export as profiled
from tests.studyforge.skills.execution.standalone.test_bases import lock, parsed
from tests.studyforge.skills.execution.standalone.test_vendor import findings
from tests.studyforge.skills.execution.standalone.test_write import (
    answered,
    checkout,
    thin_answered,
    thin_toolchain,
    toolchain,
)

GAP = Finding("EXAMPLE-1/2", "local", "a gap", (Claim("a check", measured="this run"),))


def asked(root, out, **kwargs):
    """The preflight over `root`, against the synthetic toolchain, with `kwargs` passed on."""
    kwargs.setdefault("toolchain", toolchain(out.parent / f"{out.name}-tc"))
    kwargs.setdefault("run", answered())
    return preflight.preflight(root, out, platform="linux/amd64", **kwargs)


def test_a_course_ready_to_release_is_clear_and_nothing_is_written(tmp_path):
    out = tmp_path / "learner"
    assert asked(checkout(tmp_path), out) == []
    assert not out.exists()


def test_a_course_with_no_findings_log_is_refused_and_told_where_to_write_and_sort_it(tmp_path):
    root = checkout(tmp_path)
    (root / LOG).unlink()
    reasons = asked(root, tmp_path / "learner")
    assert len(reasons) == 1
    assert LOG in reasons[0]
    assert "onboarding skill's step 7" in reasons[0] and "delivery skill's step 9" in reasons[0]
    with pytest.raises(write.ReleaseRefused, match="no findings log"):
        write.release(
            root,
            tmp_path / "learner",
            toolchain=toolchain(tmp_path / "tc"),
            platform="linux/amd64",
            run=answered(),
        )
    assert not (tmp_path / "learner").exists()


def test_a_findings_log_with_an_open_entry_is_refused_with_its_count(tmp_path):
    root = checkout(tmp_path)
    findings(root, Entry(GAP))
    (reason,) = asked(root, tmp_path / "learner")
    assert "open: 1" in reason and "delivery skill's step 9" in reason


def test_a_findings_log_whose_every_entry_is_sorted_is_clear(tmp_path):
    root = checkout(tmp_path)
    findings(root, Entry(GAP, Disposition("no", "no generator could know this course's gap")))
    assert asked(root, tmp_path / "learner") == []


def test_text_at_the_log_s_place_that_is_not_a_log_is_refused(tmp_path):
    root = checkout(tmp_path)
    (root / LOG).write_text("notes\n", encoding="utf-8")
    (reason,) = asked(root, tmp_path / "learner")
    assert "does not open with" in reason and "onboarding skill's step 7" in reason


def test_every_refusal_it_can_decide_is_named_in_one_run(tmp_path):
    """A full target, a bad account, no log and a stale lock: four rounds before, one now."""
    root = checkout(tmp_path / "src")
    (root / LOG).unlink()
    out = tmp_path / "learner"
    out.mkdir()
    (out / "left.txt").write_text("x", encoding="utf-8")
    stale = parsed(lock(runner=dict(lock()["runner"], tag="stale")))
    reasons = preflight.preflight(
        root,
        out,
        toolchain=thin_toolchain(tmp_path / "tc"),
        platform="linux/amd64",
        bases=stale,
        published_account="Not-An-Account",
        run=thin_answered(),
    )
    assert len(reasons) == 4, reasons
    for part in ("published_account", "not empty", "no findings log", "locked at tag stale"):
        assert sum(part in one for one in reasons) == 1, (part, reasons)
    with pytest.raises(write.ReleaseRefused) as refused:
        write.release(
            root,
            out,
            toolchain=thin_toolchain(tmp_path / "tc2"),
            platform="linux/amd64",
            bases=stale,
            published_account="Not-An-Account",
            run=thin_answered(),
        )
    assert str(refused.value).startswith(PREAMBLE.format(count=4))
    assert sorted(p.name for p in out.iterdir()) == ["left.txt"]


def test_a_profiled_course_whose_lock_names_no_profile_and_has_no_log_hears_both(tmp_path):
    """The publish that hit its refusals one at a time: here the lock's and the log's at once."""
    root = profiled.checkout(tmp_path)
    (root / LOG).unlink()
    reasons = preflight.preflight(
        root,
        tmp_path / "out",
        toolchain=thin_toolchain(tmp_path / "tc"),
        platform="linux/amd64",
        bases=parsed(lock()),
        run=profiled.answered(),
    )
    assert len(reasons) == 2, reasons
    assert any("names no profile" in one for one in reasons)
    assert any("no findings log" in one for one in reasons)


def test_a_profiled_course_with_no_lock_is_told_to_export_thin_beside_its_other_refusals(
    tmp_path,
):
    root = profiled.checkout(tmp_path)
    findings(root, Entry(GAP))
    reasons = preflight.preflight(
        root,
        tmp_path / "out",
        toolchain=thin_toolchain(tmp_path / "tc"),
        platform="linux/amd64",
        run=profiled.answered(),
    )
    assert len(reasons) == 2, reasons
    assert any("export it thin" in one for one in reasons)
    assert any("open: 1" in one for one in reasons)


def test_a_root_that_is_no_corpus_is_named_and_what_needs_one_is_not_asked(tmp_path):
    seen: list[list[str]] = []

    def run(argv, cwd):
        seen.append(list(argv))
        return 1, ""

    reasons = preflight.preflight(
        tmp_path, tmp_path / "out", toolchain=tmp_path, platform="linux/amd64", run=run
    )
    assert any("corpus.json" in one for one in reasons)
    assert any("no findings log" in one for one in reasons)
    assert seen == []


def test_pictures_are_judged_before_anything_is_written_and_every_bad_one_is_named(tmp_path):
    shots = tmp_path / "shots"
    shots.mkdir()
    (shots / "index.png").write_bytes(b"x" * 2048)
    (shots / "unknown.png").write_bytes(b"x" * 2048)
    (shots / "lesson.gif").write_bytes(b"x" * 2048)
    reasons = asked(checkout(tmp_path / "src"), tmp_path / "learner", screenshots=shots)
    assert len(reasons) == 2, reasons
    assert any("unknown.png" in one for one in reasons)
    assert any("lesson.gif" in one for one in reasons)
    assert not (tmp_path / "learner").exists()
