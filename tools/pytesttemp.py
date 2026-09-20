"""`W398`: clearing stale pytest temp roots by a test a LIVE run cannot fail.

**What it does.** Sweeps the numbered run directories pytest leaves under the
system temp directory and removes only the ones no live process owns. Every
candidate is asked two questions, in this order: *does a live process hold this
directory's lock*, and *is it older than the grace*. The first is the liveness
test; the second is a belt, and never the safety property.

**How you use it.**

    python3 -m tools.pytesttemp            # sweep, then print counts
    python3 -m tools.pytesttemp --dry-run  # the same verdicts, nothing removed

`sweep(root, ...)` is the same pass in Python and returns a `Sweep`, whose
`report()` is what the command prints.

**Depends on.** `os`, `shutil`, `pathlib`, `dataclasses`, `argparse`, `time`
and `tempfile` — the standard library. ⛔ Deliberately **not** on
`_pytest.pathlib`, whose cleanup helpers are private API: the rule this file
implements is four lines long and is written out here, where it can be read and
tested, rather than borrowed from a module that may rename it.

## ⛔ Why an age test alone is not obeyable, which is the whole row

⚠️ **Measured by the register, 2026-09-19:** a guarded merge was REFUSED when a
worker's temp directory vanished under a live run, because an office had cleared
*stale* pytest temp directories by age while a gate was using one. ⭐ The office
rule already said *never one in use* — ⛔ **and an age test cannot see a live
run.** A suite that runs for forty minutes owns a directory that has been older
than any plausible threshold for twenty-five of them, so by-eye obedience was
not carelessness; it was the only reading the instrument allowed.

⭐ **What a live run does leave is a lock.** pytest writes `.lock` into each
numbered directory it creates and removes it at process exit, and the file's
contents are the **pid** of the process that made it. So the liveness test is
exact and costs one `os.kill(pid, 0)`: a lock whose pid is alive is a run in
flight, whatever the directory's age says.

## ⛔ What this deliberately does NOT do, and why

⛔ **It does not give each run a private temp root.** ⚠️ That was the other
candidate and it is measured to break this suite: `W375/3` recorded three tests
in the serve CLI going RED under a private `--basetemp`, because those tests
bind a Unix socket inside the temp root and the longer path exceeded what
`sun_path` can hold. ⭐ A liveness test costs nothing and moves no path.

⛔ **It never prints a path.** The run directories live under `pytest-of-<user>`
— the name carries the host account, which is personal data (R7) — so the report
is counts and reasons, and the caller that wants a path already has the root.

## ⚠️ The blind spot, recorded rather than discovered later

⛔ **A run started with `tmp_path_retention_policy=none` writes NO lock**, so no
instrument here can see it and only the grace stands between it and this sweep.
⭐ That is what the grace is for, and it is why it is not zero by default; an
office that sets that policy has taken the liveness test away and the office
rules say not to.
"""

from __future__ import annotations

import argparse
import os
import shutil
import tempfile
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

#: The directory name pytest gives the per-run lock, and the prefix of a run directory.
LOCK_NAME = ".lock"
RUN_PREFIX = "pytest-"

#: The temp-root directories pytest makes, one per account. ⭐ Matched by prefix and then
#: filtered by owner, so another account's root is never a candidate in the first place.
ROOT_PREFIX = "pytest-of-"

#: ⚠️ Fifteen minutes, the figure the office rules already carried. ⛔ It is NOT the safety
#: property — see the module docstring — it is the cover for a run that wrote no lock.
DEFAULT_GRACE_SECONDS = 900.0

#: The verdicts a candidate can take, and what each one means in the report.
IN_USE = "in use"
TOO_YOUNG = "younger than the grace"
REMOVABLE = "removable"
UNREADABLE = "unreadable"

#: ⭐ The order the report lists the verdicts it KEPT a directory under, so two runs'
#: reports compare line by line. ⛔ `REMOVABLE` is not among them: its count is the
#: headline figure, and printing it twice invites the two copies to disagree.
KEPT_VERDICTS = (IN_USE, TOO_YOUNG, UNREADABLE)


def _pid_alive(pid: int) -> bool:
    """Report whether `pid` names a live process on this host.

    ⛔ `EPERM` answers YES, not no: a pid we may not signal is a pid that exists,
    and the conservative reading is the only safe one here.
    """
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def lock_holder(run: Path) -> int | None:
    """Return the pid written in `run`'s lock file, or `None` when there is no lock.

    ⚠️ A lock whose contents are not a pid answers `0`, which `_pid_alive` reads as
    dead — the file is pytest's and pytest writes a pid; anything else is a corpse.
    """
    lock = run / LOCK_NAME
    try:
        text = lock.read_text(encoding="utf-8", errors="replace").strip()
    except FileNotFoundError:
        return None
    except OSError:
        # ⛔ A lock we cannot read is a lock we must assume is held.
        return -1
    try:
        return int(text)
    except ValueError:
        return 0


@dataclass(frozen=True)
class Candidate:
    """One numbered run directory and the two readings taken of it."""

    path: Path
    verdict: str
    holder: int | None = None


def _age(path: Path, now: float) -> float | None:
    try:
        return now - path.stat().st_mtime
    except OSError:
        return None


def judge(
    run: Path,
    *,
    now: float,
    grace: float,
    alive: Callable[[int], bool] = _pid_alive,
) -> Candidate:
    """Decide what may be done with one run directory, liveness FIRST.

    ⭐ The order is the point: a directory whose lock is held is `IN_USE` however old
    it is, and the grace is only ever consulted for one that no live process holds.
    """
    holder = lock_holder(run)
    if holder is not None:
        if holder < 0:
            return Candidate(run, UNREADABLE, holder)
        if alive(holder):
            return Candidate(run, IN_USE, holder)
    age = _age(run, now)
    if age is None:
        return Candidate(run, UNREADABLE, holder)
    if age < grace:
        return Candidate(run, TOO_YOUNG, holder)
    return Candidate(run, REMOVABLE, holder)


def run_directories(root: Path, *, uid: int | None = None) -> Iterator[Path]:
    """Yield every numbered run directory under the temp `root` this account owns.

    ⛔ Symlinks are skipped: `pytest-current` and its siblings point AT a run directory,
    and following one would delete the target through a name that is not the target's.
    """
    owner = os.getuid() if uid is None else uid
    try:
        roots = sorted(root.iterdir())
    except OSError:
        return
    for pytest_of in roots:
        if not pytest_of.name.startswith(ROOT_PREFIX) or pytest_of.is_symlink():
            continue
        try:
            if pytest_of.stat().st_uid != owner or not pytest_of.is_dir():
                continue
            runs = sorted(pytest_of.iterdir())
        except OSError:
            continue
        for run in runs:
            if run.is_symlink() or not run.name.startswith(RUN_PREFIX):
                continue
            try:
                if run.is_dir():
                    yield run
            except OSError:
                continue


@dataclass
class Sweep:
    """What one pass saw and what it did, in counts — ⛔ never in paths."""

    counts: dict[str, int] = field(default_factory=dict)
    removed: int = 0
    failed: int = 0
    dry_run: bool = False

    def record(self, candidate: Candidate) -> None:
        self.counts[candidate.verdict] = self.counts.get(candidate.verdict, 0) + 1

    def report(self) -> str:
        """One line per verdict, in a fixed order, with no path and no account name."""
        seen = sum(self.counts.values())
        head = "would remove" if self.dry_run else "removed"
        # ⛔ A dry run removed nothing, so the headline is what it JUDGED removable.
        figure = self.counts.get(REMOVABLE, 0) if self.dry_run else self.removed
        lines = [
            f"pytest temp roots: {seen} run director{'y' if seen == 1 else 'ies'} seen, "
            f"{head} {figure}"
        ]
        for verdict in KEPT_VERDICTS:
            count = self.counts.get(verdict, 0)
            if count:
                lines.append(f"  {count} {verdict}")
        if self.failed:
            lines.append(f"  {self.failed} could not be removed")
        return "\n".join(lines)


def _remove(run: Path) -> bool:
    """Delete one run directory, reporting whether it is gone — ⛔ never raising."""
    try:
        shutil.rmtree(run)
    except OSError:
        pass
    return not run.exists()


def sweep(
    root: Path,
    *,
    grace: float = DEFAULT_GRACE_SECONDS,
    now: float | None = None,
    alive: Callable[[int], bool] = _pid_alive,
    dry_run: bool = False,
    uid: int | None = None,
) -> Sweep:
    """Judge every run directory under `root` and remove the ones nothing holds."""
    moment = time.time() if now is None else now
    result = Sweep(dry_run=dry_run)
    for run in run_directories(root, uid=uid):
        candidate = judge(run, now=moment, grace=grace, alive=alive)
        result.record(candidate)
        if candidate.verdict != REMOVABLE or dry_run:
            continue
        if _remove(run):
            result.removed += 1
        else:
            result.failed += 1
    return result


def temp_root() -> Path:
    """The directory pytest puts its per-account root in, honouring its own override."""
    return Path(os.environ.get("PYTEST_DEBUG_TEMPROOT") or tempfile.gettempdir())


def main(argv: list[str] | None = None) -> int:
    """Sweep and print.

    ⭐ Exit `0` whether or not anything was removed: a cleanup is housekeeping and
    never a verdict, and an office reads its counts, not its status.
    """
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.pytesttemp",
        description=(
            "Remove the pytest run directories no live process holds. "
            "A directory whose lock is held by a live pid is never touched."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="judge, print, remove nothing")
    parser.add_argument(
        "--grace",
        type=float,
        default=DEFAULT_GRACE_SECONDS,
        metavar="SECONDS",
        help="cover for a run that wrote no lock; not the liveness test (default: %(default)s)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        metavar="DIR",
        help="the temp directory to sweep (default: pytest's own)",
    )
    args = parser.parse_args(argv)
    result = sweep(
        args.root or temp_root(),
        grace=args.grace,
        dry_run=args.dry_run,
    )
    print(result.report())
    return 0


if __name__ == "__main__":  # pragma: no cover - the entry point itself
    raise SystemExit(main())
