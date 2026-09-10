"""Fixtures for the visual harness, and the line it prints whether it ran or not.

⛔ **`pytest_terminal_summary` is the loud half of this task** and is not
decoration. `SF-01` was approved on a host run whose two skips nobody read, and
this wave the container's eight skips and the host's eight were measured to be
disjoint sets. A skip behind `-rs` is a skip nobody reads, so this harness says
what it did — or did not do, and how many checks that was — in the summary of
**every** run of the whole suite, in `-q` as well.
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


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:  # noqa: ARG001
    """Say what the visual harness did, at the end of every run, unconditionally."""
    skipped = sum(
        1
        for report in terminalreporter.stats.get("skipped", [])
        if str(getattr(report, "nodeid", "")).startswith("tests/visual/")
    )
    terminalreporter.write_line("")
    terminalreporter.write_line(discovery.report_line(skipped))


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
