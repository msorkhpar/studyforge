"""Fixtures for the visual harness, and the line it prints whether it ran or not.

⛔ **`pytest_terminal_summary` is the loud half of this harness** and is not
decoration. A host and the container can skip disjoint sets, and a skip behind
`-rs` is a skip nobody reads, so this harness says
what it did — or did not do, and how many checks that was — in the summary of
**every** run of the whole suite, in `-q` as well.

## ⛔ This module is the ONE ambient reader, and the licence is stated

⛔ **`browser` hands the HOST's environment to a verdict function**
(`discovery.require_browser`), and that is LICENSED rather than overlooked.
⭐ **Why it is admissible:** the verdict it can reach is a SKIP or a FAILURE that
NAMES ITSELF and its remedy, the number of checks it silenced is
counted and printed by `pytest_terminal_summary`, and the environment in force
is printed beside it by `discovery.environment_declaration()`. ⛔ **Nothing here
can turn a silent non-run into a green reading.**

⭐ **Every OTHER function in this package that reaches a verdict pins the
environment instead, by requesting `pinned_environment`** — and
`test_host_environment.py` enforces exactly that, with this module named as the
single licensed exception. ⚠️ **The exception is a NAMED module with a STATED
licence and never a pattern**.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.visual import discovery, site
from tests.visual.browser import Browser
from tests.visual.page import OpenPage

#: Where captures are written when a run wants to keep them. ⛔ Unset by
#: default, so captures land in pytest's own temporary directory and **nothing
#: is written into the repository**: a screenshot is an artefact of one machine,
#: and the path it was taken at is a home directory (R7).
CAPTURE_VARIABLE = "STUDYFORGE_VISUAL_CAPTURES"


@pytest.fixture
def pinned_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Pin the three verdict-reaching variables OFF, so this test reads no host.

    ⛔ **The fixture arm.** ⭐ A test that
    asserts what `require_browser`, `state`, `evidence_state`, `report_line` or
    `environment_declaration` ANSWERS must decide the environment itself; one
    that inherits the host's is a committed verdict depending on the host
    (R15): a test that fakes the browser's absence and then lets the HOST decide
    whether absence skips or fails passes or fails by the host's setting.

    ⭐ **The `@cache` on `state()` is cleared on the way in and on the way out**,
    so a test may exercise the discovery path under a faked `PATH` without
    leaving the session's real answer poisoned for the checks that follow.
    """
    cached = discovery.state
    cached.cache_clear()
    for variable in (
        discovery.DEMAND_VARIABLE,
        discovery.BINARY_VARIABLE,
        discovery.CONTAINER_VARIABLE,
    ):
        monkeypatch.delenv(variable, raising=False)
    yield
    # ⛔ The CACHED callable is held from setup, never re-read from the module:
    # a test that replaces `discovery.state` with a lambda is torn down AFTER
    # this fixture, so `discovery.state.cache_clear` would not exist here.
    cached.cache_clear()


#: ⛔ The outcomes that mean *this check reached no verdict on its subject*.
#: ⚠️ **`error` is here** because with `$STUDYFORGE_VISUAL` unset the browser
#: checks SKIP, and with `=required` the same checks become fixture ERRORS. ⭐ A
#: count of skips alone would then read `0` when nothing ran, which is the
#: loudness mechanism reporting the opposite of the truth.
DID_NOT_RUN = ("skipped", "error")


def checks_that_did_not_run(stats: dict) -> int:
    """How many checks in THIS package produced no verdict on their subject.

    ⭐ A pure function of pytest's own tally, so the count is asserted over a
    fixture in `test_host_environment.py` rather than only observed in a run.
    """
    return sum(
        1
        for outcome in DID_NOT_RUN
        for report in stats.get(outcome, [])
        if str(getattr(report, "nodeid", "")).startswith("tests/visual/")
    )


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:  # noqa: ARG001
    """Say what the visual harness did, at the end of every run, unconditionally."""
    terminalreporter.write_line("")
    terminalreporter.write_line(
        discovery.report_line(checks_that_did_not_run(terminalreporter.stats))
    )


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    """One headless browser for the whole session, or a named skip."""
    binary = discovery.require_browser()
    with Browser(binary) as running:
        yield running


@pytest.fixture(scope="session")
def built_site(tmp_path_factory: pytest.TempPathFactory) -> site.Site:
    """The two fixture units, built into a temporary tree the way a build would."""
    return site.build(tmp_path_factory.mktemp("visual-site"))


@pytest.fixture(scope="session")
def damaged_sites(tmp_path_factory: pytest.TempPathFactory) -> dict[str, site.Site]:
    """One tree per declared damage, for the negative control each clause runs."""
    root = tmp_path_factory.mktemp("visual-damaged")
    return {name: site.build(root / name, damage=name) for name in site.DAMAGE}


def one_tab_per_check(browser: Browser) -> Iterator[OpenPage]:
    """Open one tab, hand it to a check, and close it when the check ends.

    ⛔ **The closing is the point.** A tab left open is an operating-system
    process, and a session's worth of them hangs the whole directory.

    ⭐ **It is a NAMED generator and the fixture below is one line over it**, so
    `test_page_lifetime.py` can drive the teardown and assert the tab is gone.
    ⛔ A fixture body reachable only through pytest is a teardown asserted by
    reading it.

    ⚠️ `finally` and not a plain call after the `yield`: a check that fails
    raises through here, and that is precisely the run whose tab must not leak.
    """
    page = OpenPage(browser)
    try:
        yield page
    finally:
        page.close()


#: A fresh tab per test, closed when that test ends.
open_page = pytest.fixture(name="open_page")(one_tab_per_check)


@pytest.fixture(scope="session")
def capture_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Where this run writes its PNGs — a named directory, or a temporary one."""
    named = os.environ.get(CAPTURE_VARIABLE, "").strip()
    if named:
        directory = Path(named)
        directory.mkdir(parents=True, exist_ok=True)
        return directory
    return tmp_path_factory.mktemp("visual-captures")
