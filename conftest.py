"""The suite's own exit condition: a test run may not change the working tree.

**What it does.** Snapshots `git status` when the session starts and again when
it finishes, and fails the session if any path's status moved in between. The
comparison lives in `tests/harness/treestate.py`; this file is the wiring and
nothing else.

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
`tests.harness.skipped.unreachable_population`, and printed when the count is `0`.
⛔ **It never touches the exit status**: a population out of reach is a
disclosure, not a failure (Ruling 328).

## ⛔ `W364` — under `pytest-xdist`, every reading here is the CONTROLLER's

⭐ With `-n`, each worker is a pytest session of its own and fires these hooks
too. ⛔ **A worker's tree check is a race, never a reading:** workers finish at
different times, so one would snapshot while another's test is mid-write — and
a worker's exit status never reaches the run's anyway. ⭐ So the tree check runs
on the controller only, whose session STARTS before any worker runs a test and
FINISHES after the last one has, which is exactly the serial run's window. The
summary hooks need nothing: the controller's tally is every worker's reports.

⛔ **`SERIAL` names the directories that may not spread across workers**, each
with its reason; its tests go to ONE worker in declaration order, beside the
rest (`--dist loadgroup`, which a bare `-n` is promoted to below). ⭐ A test is
never deleted for being unsafe in parallel: it is fixed, or it is named here.

## ⛔ `W366` — the `reads_tree` marker, and where it comes from

⭐ The merge gate selects tests by what a change can reach; a test that reads the working
tree — a document, a sweep — is reached by ANY change, and carries `reads_tree`. ⛔ The
marker is APPLIED here from `tools.treereaders.TreeReaders`, the very rule the selection uses,
so the two cannot disagree; a test the rule misses is marked by hand with
`pytest.mark.reads_tree`, which that rule reads too. `python3 -m pytest -m reads_tree` is
what a document-only change runs.

## ⛔ `REL-02` — THE PRODUCT SUITE STANDS WITHOUT THE TOOLING

⭐ **Nothing here imports the tooling.** The tree-state exit condition and the unreachable
population are the PRODUCT suite's own, standard library only, under `tests/harness/`: a
stray file a test leaves in the checkout is a defect of the PRODUCT (both measured instances
were a framework writer under test), so the check that catches it must hold wherever the
product's tests run — including a checkout with no tooling in it.

⚠️ **The `reads_tree` rule is NOT the product's** — it exists for the merge gate's selection,
which is tooling. ⛔ So it is reached through ONE seam, `TREE_READERS`, named as data and imported
only when the tooling is present: with it present the marker lands exactly as before, and with
it absent there is no merge gate to select for. `REL-10` deletes the seam with the tooling.

⭐ **The process tests are DECLARED in `tests/harness/process.py`**, and carry the `process`
marker. With the tooling present they run exactly as before; with it absent a declared file is
not collected and a declared test is skipped with its reason, and every run prints which.
"""

from __future__ import annotations

import importlib
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


#: ⛔ The directories whose tests run on ONE worker under `-n`, and why (`W364`).
SERIAL = {
    "tests/visual/": (
        "one headless browser per session: spread across workers it is one browser "
        "PER WORKER, all capturing through the container's one shared-memory mount, "
        "which is the resource a capture once wedged the suite on"
    ),
    "tests/docker/": (
        "with STUDYFORGE_DOCKER_TESTS=1 its checks build and start images through one "
        "daemon under content-named tags; neither gate environment reaches them, so "
        "their parallel safety is unmeasured and they are not spread"
    ),
}


def _root() -> Path:
    return Path(__file__).resolve().parent


def _on_worker(config: pytest.Config) -> bool:
    """Report whether this session is an `xdist` WORKER rather than the run itself."""
    return hasattr(config, "workerinput")


#: ⭐ `W366`: the marker every test that reads the working tree carries, and what it means.
READS_TREE = "reads_tree"
READS_TREE_MEANS = (
    "reads the working tree (a document, a sweep), so the merge gate runs it on ANY change"
)

#: The key the controller hands each worker its distribution mode under (`W364`).
DIST_KEY = "studyforge_dist"

#: ⛔ `REL-02`: the ONE name the product suite gives the tooling, as data — the merge gate's
#: `reads_tree` rule, imported only when the tooling is present (see the module docstring).
TREE_READERS = "tools.treereaders"


def _tree_readers():
    """Return the merge gate's `TreeReaders` over this checkout, or `None` without the tooling.

    ⛔ Absence is read off the tooling DIRECTORY, never off a failed import: with the tooling
    present a broken rule must fail the run, not quietly stop marking.
    """
    from tests.harness import process

    if not process.present(_root()):
        return None
    return importlib.import_module(TREE_READERS).TreeReaders(_root())


def pytest_configure(config: pytest.Config) -> None:
    """Promote a bare `-n`'s `load` to `loadgroup`, so `SERIAL` is honoured (`W364`).

    ⭐ `loadgroup` distributes every unmarked test exactly as `load` does, so this
    moves nothing but the groups; an explicit `--dist` of any other kind is kept.

    ⚠️ **MEASURED in the pinned image, `pytest-xdist` 3.8.0:** a worker RE-PARSES the
    run's own argv and derives `loadgroup` from it before any conftest configures,
    so a promotion on the controller alone never reaches the workers that must
    suffix each grouped id. ⭐ The controller therefore hands its mode to every
    worker (`pytest_configure_node`), and a worker promotes itself from that.
    """
    from tests.harness import process

    # ⭐ `W366`, on the controller AND every worker: `--strict-markers` refuses an unregistered one.
    config.addinivalue_line("markers", f"{READS_TREE}: {READS_TREE_MEANS}")
    config.addinivalue_line("markers", f"{process.MARKER}: {process.MARKER_MEANS}")
    if _on_worker(config):
        if config.workerinput.get(DIST_KEY) == "loadgroup":
            config.option.loadgroup = True
        return
    if getattr(config.option, "dist", "no") == "load":
        config.option.dist = "loadgroup"


@pytest.hookimpl(optionalhook=True)
def pytest_configure_node(node) -> None:
    """Hand the controller's distribution mode to a worker as it starts (`W364`)."""
    node.workerinput[DIST_KEY] = getattr(node.config.option, "dist", "no")


# ⛔ `tryfirst`: `xdist`'s worker suffixes each GROUPED id in this same hook and is
#    registered after this file, so without it the marks would land after that reading.
@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark the tree readers (`W366`) and the process (`REL-02`); group each `SERIAL` directory."""
    from tests.harness import process

    readers = _tree_readers()
    present = process.present(_root())
    for item in items:
        relative, _, rest = item.nodeid.partition("::")
        if readers is not None and readers.reads(relative, rest.split("::", 1)[0].split("[", 1)[0]):
            item.add_marker(getattr(pytest.mark, READS_TREE))
        reason = process.declared(item.nodeid)
        if reason is not None:
            item.add_marker(getattr(pytest.mark, process.MARKER))
            if not present:
                item.add_marker(pytest.mark.skip(reason=f"{ABSENT_REASON}: {reason}"))
    if not config.pluginmanager.hasplugin("xdist"):
        return
    for item in items:
        for prefix in SERIAL:
            if item.nodeid.startswith(prefix):
                item.add_marker(pytest.mark.xdist_group(name=prefix.strip("/").replace("/", "-")))


#: What a declared process test says when the tooling is absent (`REL-02`).
ABSENT_REASON = "a process test, not run because the tooling is absent from this checkout"


def pytest_ignore_collect(collection_path: Path, config: pytest.Config) -> bool | None:
    """Leave a declared process FILE uncollected when the tooling is absent (`REL-02`).

    ⭐ A whole file, because it imports the tooling at its top and would fail at import. ⛔
    `None`, never `False`, for everything else, so no other plugin's answer is overridden.
    """
    from tests.harness import process

    if process.present(_root()):
        return None
    try:
        relative = collection_path.resolve().relative_to(_root()).as_posix()
    except ValueError:
        return None
    return True if relative in process.files() else None


def pytest_sessionstart(session: pytest.Session) -> None:
    """Record what git says about the tree before a single test runs."""
    from tests.harness import treestate

    if _on_worker(session.config):
        return
    _BEFORE.append(treestate.snapshot(_root()))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Compare, and fail the session if the run left the checkout changed."""
    from tests.harness import treestate

    if _on_worker(session.config):
        return
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


#: The one directory whose OWN conftest prints a summary line (`tests/visual/conftest.py`).
VISUAL = "tests/visual/"


def _forward_visual(terminalreporter, exitstatus: int, config: pytest.Config) -> None:
    """Print the visual harness's line on an `xdist` CONTROLLER, as a serial run does (`W364`).

    ⚠️ **MEASURED in the pinned image:** under `-n` the line VANISHED. The controller
    never collects, so `tests/visual/conftest.py` — not an initial conftest — is never
    loaded there, and its summary hook never fires. ⭐ Its `report_line` reads only the
    environment, so the controller's reading is the one a serial run prints; it is
    forwarded whenever this run reached a test in that directory.
    """
    if not config.pluginmanager.hasplugin("dsession"):
        return
    # ⚠️ MEASURED: a run whose ARGUMENT lies inside that directory loads its conftest on the
    #    controller as an INITIAL one, and then the line was printed twice.
    own = (_root() / VISUAL / "conftest.py").resolve()
    for plugin in config.pluginmanager.get_plugins():
        if Path(getattr(plugin, "__file__", None) or ".").resolve() == own:
            return
    reached = any(
        str(getattr(report, "nodeid", "")).startswith(VISUAL)
        for reports in terminalreporter.stats.values()
        for report in reports
    )
    if reached:
        from tests.visual import conftest as visual

        visual.pytest_terminal_summary(terminalreporter, exitstatus, config)


def pytest_terminal_summary(terminalreporter, exitstatus: int, config: pytest.Config) -> None:
    """Print what this run could not reach, on every run, empty or not (`W158`, `REL-02`)."""
    from tests.harness import process
    from tests.harness.skipped import unreachable_population

    _forward_visual(terminalreporter, exitstatus, config)
    terminalreporter.write_line("")
    for line in unreachable_population(terminalreporter.stats):
        terminalreporter.write_line(line)
    terminalreporter.write_line(process.population_line(process.present(_root())))
