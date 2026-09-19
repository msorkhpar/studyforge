"""`W364` clause 6: `tools.mergegate` holds the shared container lock ITSELF, image gates only.

⭐ **Asserted both ways (R12)** with a fake runner and a lock file under `tmp_path`: with
`STUDYFORGE_CONTAINER_LOCK` set, every pinned-image gate runs while the lock is HELD and
every host gate runs with it RELEASED; unset, nothing is ever locked. ⛔ No test calls docker.

⭐ **"Held" is PROBED, never inferred:** the runner opens the lock file a second time and
asks for it without blocking. An `flock` belongs to an open file description, so a second
open in this same process is refused exactly while the gate holds it.
"""

from __future__ import annotations

import fcntl
from pathlib import Path

import pytest

import tools.gates as gates_module
from tests.support import git, init_repository, run
from tools.gates import GATES, HOST, IMAGE
from tools.mergegate import LOCK_VARIABLE, MERGED, REFUSED, Gate, stage_and_read

_IDENTITY = ("-c", "user.name=test", "-c", "user.email=test@example.invalid")


def _git(cwd: Path, *arguments: str) -> None:
    result = run([git(), *_IDENTITY, "-c", "commit.gpgsign=false", *arguments], cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture
def release(tmp_path: Path) -> Path:
    """A release checkout with an unmerged `branch`; a placeholder identity in ITS OWN config."""
    root = init_repository(tmp_path / "release")
    _git(root, "config", "user.name", "test")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "symbolic-ref", "HEAD", "refs/heads/release")
    for name, branch in (("base.txt", None), ("branch.txt", "branch")):
        if branch:
            _git(root, "checkout", "-q", "-b", branch)
        (root / name).write_text(f"{name}\n", encoding="utf-8")
        _git(root, "add", name)
        _git(root, "commit", "-q", "-m", name)
    _git(root, "checkout", "-q", "release")
    return root


def _held(lock: Path) -> bool:
    """Report whether somebody holds `lock`, by asking for it WITHOUT blocking."""
    with lock.open("a", encoding="utf-8") as probe:
        try:
            fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(probe, fcntl.LOCK_UN)
        return False


def _probing(lock: Path, seen: list[tuple[str, bool]], red: str = ""):
    def runner(gate: Gate, root: Path) -> int:
        seen.append((gate.environment, _held(lock)))
        return 1 if gate.environment == red else 0

    return runner


def test_SET_every_IMAGE_gate_runs_HELD_and_every_HOST_gate_RELEASED(
    release, tmp_path, monkeypatch
):
    lock = tmp_path / "container.lock"
    monkeypatch.setenv(LOCK_VARIABLE, str(lock))
    seen: list[tuple[str, bool]] = []
    outcome = stage_and_read(release, "branch", _probing(lock, seen), GATES)
    assert outcome.verdict == MERGED
    assert {environment for environment, _ in seen} == {IMAGE, HOST}, seen
    assert seen == [(environment, environment == IMAGE) for environment, _ in seen], seen
    assert not _held(lock), "the lock outlived the run"


def test_SET_a_RED_image_gate_still_RELEASES_the_lock(release, tmp_path, monkeypatch):
    lock = tmp_path / "container.lock"
    monkeypatch.setenv(LOCK_VARIABLE, str(lock))
    seen: list[tuple[str, bool]] = []
    outcome = stage_and_read(release, "branch", _probing(lock, seen, red=IMAGE), GATES)
    assert outcome.verdict == REFUSED
    assert seen == [(IMAGE, True)], seen
    assert not _held(lock), "a red reading left the lock held"


def test_UNSET_nothing_is_ever_locked(release, tmp_path, monkeypatch):
    monkeypatch.delenv(LOCK_VARIABLE, raising=False)
    # ⚠️ The spy replaces `fcntl.flock` for the whole process, so this runner does not probe.
    calls: list[object] = []
    monkeypatch.setattr(gates_module.fcntl, "flock", lambda *a: calls.append(a))
    taken: list[str] = []
    outcome = stage_and_read(release, "branch", lambda g, r: taken.append(g.environment) or 0)
    assert outcome.verdict == MERGED
    assert IMAGE in taken and HOST in taken, taken
    assert calls == [], "a lock was taken with the variable unset"


def test_the_CONTROL_the_same_spy_SEES_the_lock_when_the_variable_is_set(
    release, tmp_path, monkeypatch
):
    # ⛔ Ruling 191: the spy above reads `[]` for free unless it can read a lock at all.
    monkeypatch.setenv(LOCK_VARIABLE, str(tmp_path / "container.lock"))
    calls: list[object] = []
    monkeypatch.setattr(gates_module.fcntl, "flock", lambda *a: calls.append(a))
    stage_and_read(release, "branch", lambda gate, root: 0)
    assert calls, "no lock was taken with the variable set"
