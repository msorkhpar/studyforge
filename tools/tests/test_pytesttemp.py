"""`W398`: the sweep is asserted against a REAL live run, not only against a fake pid.

⛔ Every clause here is asserted both ways — a held directory is kept **and** the same
directory is removed once nothing holds it — because a cleanup that removes nothing is
as wrong as one that removes a live run, and an assertion in one direction cannot tell
the two apart.

⭐ The last test in this file runs an actual `pytest` in a subprocess and sweeps while
it is mid-run: that is the negative control for the instrument the register's refused
merge was missing, and it is itself run negatively (the same directory, after exit).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

from tools import pytesttemp

# ---------------------------------------------------------------------------
# Plants: a temp root shaped the way pytest shapes one
# ---------------------------------------------------------------------------

#: ⭐ A fabricated account name, never this host's (R7): the sweep filters by uid, not by name.
ACCOUNT = "pytest-of-example"

#: How much older than the grace a planted directory is made, so age is never the question.
WELL_PAST_GRACE = 10_000.0


def plant(root, name, *, lock=None, age=0.0):
    """Make one numbered run directory under a `pytest-of-…` root, optionally locked."""
    owner = root / ACCOUNT
    owner.mkdir(exist_ok=True)
    run = owner / name
    run.mkdir()
    (run / "test_something0").mkdir()
    if lock is not None:
        (run / pytesttemp.LOCK_NAME).write_text(str(lock), encoding="utf-8")
    if age:
        when = time.time() - age
        os.utime(run, (when, when))
    return run


def dead_pid():
    """A pid that is certainly not running: a child we started, waited for, and buried."""
    finished = subprocess.Popen(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-c", ""],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    finished.wait(timeout=60)
    return finished.pid


# ---------------------------------------------------------------------------
# The liveness test comes FIRST, and age never overrides it
# ---------------------------------------------------------------------------


def test_a_live_lock_holder_keeps_a_directory_however_old_it_is(tmp_path):
    # ⛔ The refused merge in one assertion: forty minutes old AND in use.
    run = plant(tmp_path, "pytest-1", lock=os.getpid(), age=WELL_PAST_GRACE)
    verdict = pytesttemp.judge(run, now=time.time(), grace=pytesttemp.DEFAULT_GRACE_SECONDS)
    assert verdict.verdict == pytesttemp.IN_USE


def test_the_same_directory_is_removable_once_its_holder_is_gone(tmp_path):
    run = plant(tmp_path, "pytest-1", lock=dead_pid(), age=WELL_PAST_GRACE)
    verdict = pytesttemp.judge(run, now=time.time(), grace=pytesttemp.DEFAULT_GRACE_SECONDS)
    assert verdict.verdict == pytesttemp.REMOVABLE


def test_an_unlocked_directory_past_the_grace_is_removable(tmp_path):
    run = plant(tmp_path, "pytest-2", age=WELL_PAST_GRACE)
    assert pytesttemp.judge(run, now=time.time(), grace=60.0).verdict == pytesttemp.REMOVABLE


def test_an_unlocked_directory_inside_the_grace_is_not(tmp_path):
    # ⭐ The belt for a run that wrote no lock at all — not a liveness test, and said so.
    run = plant(tmp_path, "pytest-2")
    assert pytesttemp.judge(run, now=time.time(), grace=60.0).verdict == pytesttemp.TOO_YOUNG


def test_a_lock_that_cannot_be_read_is_assumed_held(tmp_path):
    run = plant(tmp_path, "pytest-3", age=WELL_PAST_GRACE)
    (run / pytesttemp.LOCK_NAME).mkdir()
    assert pytesttemp.judge(run, now=time.time(), grace=60.0).verdict == pytesttemp.UNREADABLE


def test_a_lock_holding_something_that_is_not_a_pid_does_not_hold_the_directory(tmp_path):
    run = plant(tmp_path, "pytest-4", lock="not-a-pid", age=WELL_PAST_GRACE)
    assert pytesttemp.judge(run, now=time.time(), grace=60.0).verdict == pytesttemp.REMOVABLE


# ---------------------------------------------------------------------------
# What is a candidate at all
# ---------------------------------------------------------------------------


def test_only_numbered_run_directories_under_a_pytest_of_root_are_candidates(tmp_path):
    plant(tmp_path, "pytest-1")
    (tmp_path / ACCOUNT / "garbage-abc").mkdir()
    (tmp_path / "some-other-thing").mkdir()
    (tmp_path / "some-other-thing" / "pytest-9").mkdir()
    found = {run.name for run in pytesttemp.run_directories(tmp_path)}
    assert found == {"pytest-1"}


def test_a_symlink_is_never_a_candidate(tmp_path):
    run = plant(tmp_path, "pytest-1")
    (tmp_path / ACCOUNT / "pytest-current").symlink_to(run, target_is_directory=True)
    found = [candidate.name for candidate in pytesttemp.run_directories(tmp_path)]
    assert found == ["pytest-1"]


def test_a_root_owned_by_another_account_is_not_swept(tmp_path):
    plant(tmp_path, "pytest-1")
    # ⛔ Asserted by asking as somebody else: the uid is the filter, and it is the only one.
    assert list(pytesttemp.run_directories(tmp_path, uid=os.getuid() + 1)) == []
    assert [run.name for run in pytesttemp.run_directories(tmp_path)] == ["pytest-1"]


def test_a_missing_root_sweeps_nothing_rather_than_raising(tmp_path):
    assert pytesttemp.sweep(tmp_path / "never-made").counts == {}


# ---------------------------------------------------------------------------
# The sweep, and what it reports
# ---------------------------------------------------------------------------


def test_a_sweep_removes_the_dead_and_keeps_the_live_in_one_pass(tmp_path):
    held = plant(tmp_path, "pytest-1", lock=os.getpid(), age=WELL_PAST_GRACE)
    dead = plant(tmp_path, "pytest-2", lock=dead_pid(), age=WELL_PAST_GRACE)
    result = pytesttemp.sweep(tmp_path, grace=60.0)
    assert held.exists()
    assert not dead.exists()
    assert result.removed == 1
    assert result.counts[pytesttemp.IN_USE] == 1


def test_a_dry_run_judges_the_same_and_removes_nothing(tmp_path):
    dead = plant(tmp_path, "pytest-2", lock=dead_pid(), age=WELL_PAST_GRACE)
    result = pytesttemp.sweep(tmp_path, grace=60.0, dry_run=True)
    assert dead.exists()
    assert result.removed == 0
    assert result.counts[pytesttemp.REMOVABLE] == 1


def test_the_report_names_counts_and_never_a_path(tmp_path):
    plant(tmp_path, "pytest-1", lock=os.getpid(), age=WELL_PAST_GRACE)
    plant(tmp_path, "pytest-2", lock=dead_pid(), age=WELL_PAST_GRACE)
    report = pytesttemp.sweep(tmp_path, grace=60.0).report()
    assert str(tmp_path) not in report
    assert ACCOUNT not in report
    assert pytesttemp.IN_USE in report and "removed 1" in report


def test_the_command_sweeps_the_root_it_is_given_and_exits_zero(tmp_path, capsys):
    dead = plant(tmp_path, "pytest-2", lock=dead_pid(), age=WELL_PAST_GRACE)
    assert pytesttemp.main(["--root", str(tmp_path), "--grace", "60"]) == 0
    assert not dead.exists()
    assert "pytest temp roots:" in capsys.readouterr().out


def test_the_command_honours_dry_run(tmp_path, capsys):
    dead = plant(tmp_path, "pytest-2", lock=dead_pid(), age=WELL_PAST_GRACE)
    assert pytesttemp.main(["--root", str(tmp_path), "--grace", "60", "--dry-run"]) == 0
    assert dead.exists()
    assert "would remove 1" in capsys.readouterr().out


def test_the_temp_root_follows_pytests_own_override(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTEST_DEBUG_TEMPROOT", str(tmp_path))
    assert pytesttemp.temp_root() == tmp_path


# ---------------------------------------------------------------------------
# ⭐ The negative control, run against a REAL pytest and then run negatively
# ---------------------------------------------------------------------------

#: The child suite: it blocks until the test that started it drops a file, so the
#: sweep happens while the child genuinely holds its own temp directory.
CHILD_SUITE = """
import pathlib, time

def test_waits(tmp_path):
    marker = pathlib.Path(__file__).parent / "release-me"
    (pathlib.Path(__file__).parent / "holding").write_text(str(tmp_path))
    deadline = time.time() + 60
    while not marker.exists() and time.time() < deadline:
        time.sleep(0.05)
"""

#: How long the control waits for the child to reach its temp directory before giving up.
CHILD_DEADLINE = 60.0


def _wait_for(predicate, deadline=CHILD_DEADLINE):
    limit = time.time() + deadline
    while time.time() < limit:
        value = predicate()
        if value:
            return value
        time.sleep(0.05)
    return None


def test_a_real_running_pytest_survives_a_sweep_and_is_swept_once_it_exits(tmp_path):
    work = tmp_path / "child"
    work.mkdir()
    (work / "test_child.py").write_text(CHILD_SUITE, encoding="utf-8")
    temproot = tmp_path / "temproot"
    temproot.mkdir()
    environment = dict(os.environ, PYTEST_DEBUG_TEMPROOT=str(temproot))
    child = subprocess.Popen(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_child.py"],
        cwd=work,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        held = _wait_for(lambda: next(iter(pytesttemp.run_directories(temproot)), None))
        assert held is not None, "the child never reached a pytest temp directory"
        assert _wait_for(lambda: (held / pytesttemp.LOCK_NAME).exists())
        # ⛔ Grace ZERO: nothing but the liveness test stands between the sweep and a
        #    directory a live run owns, which is exactly the reading the row is about.
        kept = pytesttemp.sweep(temproot, grace=0.0)
        assert held.exists()
        assert kept.counts.get(pytesttemp.IN_USE) == 1
        assert kept.removed == 0
    finally:
        (work / "release-me").write_text("go", encoding="utf-8")
        child.wait(timeout=CHILD_DEADLINE)
    # ⭐ Run negatively: the SAME directory, once its holder is gone.
    assert _wait_for(lambda: not (held / pytesttemp.LOCK_NAME).exists())
    after = pytesttemp.sweep(temproot, grace=0.0)
    assert not held.exists()
    assert after.removed == 1
