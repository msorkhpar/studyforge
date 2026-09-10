"""The loudness mechanism, tested where it matters — on the machine it is not on.

⛔ **This is the module that stops `QA-03` repeating `SF-01`'s defect.** A
harness whose absent-browser branch has never been executed is a harness whose
skips are a guess, and the machine that most needs that branch to work — the
pinned image, which has no browser — is the one where nobody is watching.

⭐ **Runs everywhere**, browser or not: it fakes the state rather than the
machine.
"""

from __future__ import annotations

import pytest

from tests.visual import discovery

ABSENT = discovery.State(binary=None, version=None, searched=discovery.CANDIDATES)
PRESENT = discovery.State(binary="/some/browser", version="Some Browser 1.2", searched=())


@pytest.fixture
def as_state(monkeypatch: pytest.MonkeyPatch):
    """Answer `discovery.state()` with a state this machine may not be in."""

    def use(state: discovery.State) -> None:
        monkeypatch.setattr(discovery, "state", lambda: state)

    return use


def test_a_missing_browser_skips_with_a_reason_that_names_the_remedy(as_state) -> None:
    as_state(ABSENT)
    with pytest.raises(pytest.skip.Exception) as raised:
        discovery.require_browser()
    assert "no browser" in str(raised.value)
    assert "QA-03/1" in str(raised.value)


def test_a_missing_browser_FAILS_when_the_run_demanded_one(
    as_state, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ One word turns every skip below into a failure, and it is checked here.

    ⚠️ Otherwise `STUDYFORGE_VISUAL=required` is a promise in a docstring. A
    reviewer who set it and saw a green run would read that as *"the visual
    checks ran"*, which is the most expensive way this could be wrong.
    """
    as_state(ABSENT)
    monkeypatch.setenv(discovery.DEMAND_VARIABLE, discovery.DEMAND_VALUE)
    with pytest.raises(pytest.fail.Exception) as raised:
        discovery.require_browser()
    assert discovery.DEMAND_VALUE in str(raised.value)
    assert "Install a Chromium-family browser" in str(raised.value)


def test_the_demand_is_exact_and_not_merely_truthy(
    as_state, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⭐ The control: any other value must still skip.

    ⚠️ A check written as `if os.environ.get(VAR)` would make
    `STUDYFORGE_VISUAL=0` — which reads as *off* — turn every skip into a
    failure, and the person who set it would have meant the opposite.
    """
    as_state(ABSENT)
    for value in ("", "0", "no", "yes", "true", "REQUIRE"):
        monkeypatch.setenv(discovery.DEMAND_VARIABLE, value)
        with pytest.raises(pytest.skip.Exception):
            discovery.require_browser()
    monkeypatch.setenv(discovery.DEMAND_VARIABLE, "REQUIRED")
    with pytest.raises(pytest.fail.Exception):
        discovery.require_browser()


def test_a_present_browser_is_returned_and_neither_skips_nor_fails(
    as_state, monkeypatch: pytest.MonkeyPatch
) -> None:
    as_state(PRESENT)
    monkeypatch.setenv(discovery.DEMAND_VARIABLE, discovery.DEMAND_VALUE)
    assert discovery.require_browser() == "/some/browser"


def test_the_summary_line_counts_what_did_not_run(as_state) -> None:
    """⛔ The count is the half a reader acts on: *nothing ran* looks like *all passed*."""
    as_state(ABSENT)
    assert "17 visual check(s) DID NOT RUN" in discovery.report_line(17)
    assert "DID NOT RUN" not in discovery.report_line(None)
    as_state(PRESENT)
    assert "RAN on Some Browser 1.2" in discovery.report_line(0)
