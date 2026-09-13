"""The suite's own exit condition: a test run may not change the working tree.

**What it does.** Snapshots `git status` when the session starts and again when
it finishes, and fails the session if any path's status moved in between. The
comparison lives in `tools/treestate.py`; this file is the wiring and nothing
else.

**Why here.** ⛔ `pytest_sessionstart` and `pytest_sessionfinish` fire once per
session and only for an **initial** conftest, so a conftest deeper in the tree
would answer for `pytest tests/` and be silent for `pytest tools/tests/`. The
repository root is the only place that holds for every invocation, including
the bare `python3 -m pytest` that `docker/dev/check` runs.

## ⛔ The two instances this exists for

⚠️ **`SF-17/11`.** A writer under test wrote a file named `alpha` into the
repository root, and that stray file changed what an *unrelated* module's probe
refused — a RED in a module nobody had touched. ⚠️ **`SF-28/2`.** An untracked
`alpha/alpha` appeared after a full suite run and **nothing failed and nothing
reported it**.

⭐ Both were found by a person noticing. Neither instrument that could have
found them was looking, and neither needed to know what a writer is — which is
why this check knows nothing about writers either.

## ⛔ It reports even when the suite is already red, and only *sets* the code
when it is green

⚠️ A dirtied tree during a failing run is the more interesting case, not the
less: the stray file may be *why* the run failed. So the report always prints.
⛔ But the exit status is only taken over from `0`, because overwriting a real
failure's code with this one would hide which gate spoke.

## ⛔ `W158` — every run PRINTS the population it could not reach

⚠️ **The two routine environments are not supersets of each other** (Ruling 326):
the pinned container mounts only the checkout and skips every sibling assertion,
the host skips the in-image ones, and both print `passed`. ⭐ So the summary says
how many tests this run skipped and why — derived from the run's own tally by
`tools.quality.report.unreachable_population`, and printed when the count is `0`.
⛔ **It never touches the exit status**: a population out of reach is a
disclosure, not a failure (Ruling 328).
"""

from __future__ import annotations

from pathlib import Path

import pytest

#: Where the snapshot taken at session start is kept. ⚠️ A module global rather
#: than the session stash: `pytest_sessionfinish` receives the session, but a
#: stash key defined here would have to survive the same import either way, and
#: this is one value for one session.
_BEFORE: list[dict[str, str] | None] = []

#: What a dirtied tree exits with. ⛔ Deliberately inside pytest's own range: a
#: tree dirtied by the run is a failing suite, not an infrastructure fault, and
#: `docker/dev/check` reserves the codes outside that range for a wedged run.
DIRTY_EXIT = 1


def _root() -> Path:
    return Path(__file__).resolve().parent


def pytest_sessionstart(session: pytest.Session) -> None:
    """Record what git says about the tree before a single test runs."""
    from tools import treestate

    _BEFORE.append(treestate.snapshot(_root()))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Compare, and fail the session if the run left the checkout changed."""
    from tools import treestate

    root = _root()
    before = _BEFORE[0] if _BEFORE else None
    moved = treestate.changes(before, treestate.snapshot(root), treestate.exempt_prefixes(root))
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    if moved is None:
        if reporter is not None:
            # ⛔ Loud, never silent: a check over nothing must not read as a
            # pass (Ruling 191).
            reporter.write_line(
                "tree state: NOT CHECKED — git could not answer, so whether this run "
                "dirtied the checkout is unknown",
                yellow=True,
            )
        return
    if not moved:
        if reporter is not None:
            reporter.write_line(
                f"tree state: unchanged by this run ({len(before or {})} path(s) already "
                f"differed from HEAD before it started, and still do)",
                green=True,
            )
        return
    if reporter is not None:
        reporter.write_line(treestate.report(moved), red=True)
    if exitstatus == 0:
        session.exitstatus = DIRTY_EXIT


def pytest_terminal_summary(terminalreporter) -> None:
    """Print what this run could not reach, on every run, empty or not (`W158`)."""
    from tools.quality.report import unreachable_population

    terminalreporter.write_line("")
    for line in unreachable_population(terminalreporter.stats):
        terminalreporter.write_line(line)
