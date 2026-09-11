"""Fixtures for the visual harness, and the line it prints whether it ran or not.

⛔ **`pytest_terminal_summary` is the loud half of this task** and is not
decoration. `SF-01` was approved on a host run whose two skips nobody read, and
this wave the container's eight skips and the host's eight were measured to be
disjoint sets. A skip behind `-rs` is a skip nobody reads, so this harness says
what it did — or did not do, and how many checks that was — in the summary of
**every** run of the whole suite, in `-q` as well.

## ⛔ `W128` — this module is the ONE ambient reader, and the licence is stated

⛔ **`browser` hands the HOST's environment to a verdict function**
(`discovery.require_browser`), and that is LICENSED rather than overlooked.
⭐ **Why it is admissible:** the verdict it can reach is a SKIP or a FAILURE that
NAMES ITSELF and its remedy (Ruling 204), the number of checks it silenced is
counted and printed by `pytest_terminal_summary`, and the environment in force
is printed beside it by `discovery.environment_declaration()`. ⛔ **Nothing here
can turn a silent non-run into a green reading.**

⭐ **Every OTHER function in this package that reaches a verdict pins the
environment instead, by requesting `pinned_environment`** — and
`test_host_environment.py` enforces exactly that, with this module named as the
single licensed exception. ⚠️ **The exception is a NAMED module with a STATED
licence and never a pattern** (Ruling 185).
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

    ⛔ **`W128`, and it is the fixture arm of the remedy.** ⭐ A test that
    asserts what `require_browser`, `state`, `evidence_state`, `report_line` or
    `environment_declaration` ANSWERS must decide the environment itself; one
    that inherits the host's is a committed verdict depending on the host
    (Ruling 225's environment half).

    ⚠️ **This is not a hypothetical.** At `270296d`, MEASURED in the pinned
    container, `STUDYFORGE_VISUAL=required docker/dev/check` read
    `1 failed, 5560 passed` against `5561 passed` with it unset, and the one
    failure was `test_a_missing_browser_skips_with_a_reason_that_names_the_remedy`
    — a test that fakes the browser's absence and then let the HOST decide
    whether absence skips or fails (`W124/5`, `W115/4`).

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
#: ⚠️ **`error` is here because of `W128/4`**, and it is the SAME defect this row
#: exists to close arriving in the COUNT rather than in a test: with
#: `$STUDYFORGE_VISUAL` unset, 123 browser checks SKIP and the line said *"123
#: visual check(s) DID NOT RUN"*; with `=required` the same 123 become fixture
#: ERRORS, and the line said **`0`**. ⛔ **MEASURED at `270296d` in the pinned
#: container: `50 passed, 123 errors` beside `visual harness: NO BROWSER — 0
#: visual check(s) DID NOT RUN`.** ⭐ A count that reads `0` when nothing ran is
#: the loudness mechanism reporting the opposite of the truth.
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


@pytest.fixture
def open_page(browser: Browser) -> Iterator[OpenPage]:
    """A fresh tab per test, closed with the browser at the end of the session."""
    yield OpenPage(browser)


@pytest.fixture(scope="session")
def capture_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Where this run writes its PNGs — a named directory, or a temporary one."""
    named = os.environ.get(CAPTURE_VARIABLE, "").strip()
    if named:
        directory = Path(named)
        directory.mkdir(parents=True, exist_ok=True)
        return directory
    return tmp_path_factory.mktemp("visual-captures")
