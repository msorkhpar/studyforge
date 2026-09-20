"""`W397` — the visual harness closes what it opens, and never waits forever.

⛔ **The defect this module exists for.** The `browser` fixture is session-scoped
and `open_page` is per check, and nothing ever closed a tab. A tab is a set of
operating-system processes, so a session's tabs accumulated until the image
could start no more renderers. ⚠️ **MEASURED by the register on the merged tree
in the pinned image: the whole `tests/visual/` directory hung — 190 processes,
dozens of them Chrome renderers, at 0.1% CPU — while the same modules passed
ALONE in that image in seconds.**

⛔ **The second half is why it HUNG rather than failed.** `Browser.call`
computed a deadline and looped on it, but the loop body blocked in `os.read` on
a live pipe — so a browser that was *up and silent* was waited on forever and
the harness's own `"no answer in 30s"` was unreachable code. ⭐ `docker/dev/check`
named this defect in its own header and routed the deadlined read here, because
`select`-ing on the fd changes the I/O path every reading in this package is
taken against.

## ⛔ What is asserted, and how each clause is made red

⭐ **Clause 1 — a check's tab is closed when the check ends** — is asserted by a
COUNT OF LIVE TARGETS taken from the browser across many opens, never from this
package's own bookkeeping: the row is about processes. ⛔ Its plant is the
leaking form itself, a `close` that closes nothing, and it must go red.

⭐ **Clause 3 — a browser that stops answering FAILS rather than hangs** — is
asserted BOTH WAYS on one instrument: a live browser's call returns, a silent
browser's call raises inside a bound this test names, and the raise is timed so
the claim is about the BOUND and not merely about the error.

⚠️ **The leaking form of clause 3 cannot be planted, and that is the defect
rather than a gap:** a read with no deadline does not fail slowly, it does not
return at all, so a plant of it would hang this module the way it hung the
directory. ⭐ **So the deadline is asserted DIRECTLY instead** — `select` is
wrapped in a recorder and the bounds it was handed are read back — and THAT
check has a plant: the old blocking `_receive`, against a browser that answers
at once, reaches the recorder never.
"""

from __future__ import annotations

import select
import stat
import tempfile
import time
from pathlib import Path

import pytest

from tests.visual import browser as module
from tests.visual import conftest
from tests.visual.browser import Browser, BrowserError
from tests.visual.page import OpenPage

#: How many tabs the counting check opens and closes. ⭐ More than one, because
#: a leak of exactly one tab per check is what this row is about and a single
#: open cannot tell "closed" from "never opened a second".
OPENS = 4

#: Seconds the live-target count may take to settle after a tab is closed.
#: ⚠️ `Target.closeTarget` is answered when the browser has ACCEPTED the close,
#: and the target leaves the listing a moment later.
SETTLE = 5.0

#: The bound the silent-browser checks run under, in seconds. ⛔ Small on
#: purpose: the claim is that the harness gives up at a bound it was told, and
#: a check that took the real 30s to say so would be one nobody runs.
BOUND = 0.5

#: What a failure to give up costs this module before it is called a hang. ⭐ A
#: generous multiple of `BOUND`, because the claim is "bounded", not "prompt".
PATIENCE = 10.0


def _live(browser: Browser, expecting: int) -> int:
    """The count of live page targets, once it has settled or `SETTLE` has passed."""
    deadline = time.monotonic() + SETTLE
    count = len(browser.live_pages())
    while count != expecting and time.monotonic() < deadline:
        time.sleep(0.05)
        count = len(browser.live_pages())
    return count


@pytest.fixture
def silent_binary(tmp_path: Path) -> str:
    """A 'browser' that starts, holds the protocol pipe open, and never speaks."""
    script = tmp_path / "silent-browser"
    script.write_text("#!/bin/sh\nexec sleep 60\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return str(script)


@pytest.fixture
def launch_under(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Put every launch profile made here under `tmp_path`, never the shared root."""
    root = tmp_path / "launches"
    root.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(root))
    return root


# --- clause 1: a check's tab is closed when the check ends -------------------


def _check_opening_and_closing_many_tabs_leaves_the_count_where_it_started(
    browser: Browser,
) -> None:
    """Open `OPENS` tabs one at a time, closing each — the live count must not grow."""
    before = len(browser.live_pages())
    for _each in range(OPENS):
        with OpenPage(browser):
            pass
    after = _live(browser, expecting=before)
    assert after == before, f"{after - before} tab(s) outlived the checks that opened them"


def test_a_tab_opened_and_closed_leaves_no_target_behind(browser: Browser) -> None:
    _check_opening_and_closing_many_tabs_leaves_the_count_where_it_started(browser)


def test_PLANT_a_close_that_closes_nothing_reddens_the_check(
    browser: Browser, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ The leaking form — the shape this row found in the tree — must go red."""
    opened: list[str] = []

    def _leak(page: OpenPage) -> None:
        opened.append(page.session)

    monkeypatch.setattr(OpenPage, "close", _leak)
    try:
        with pytest.raises(AssertionError, match="outlived the checks"):
            _check_opening_and_closing_many_tabs_leaves_the_count_where_it_started(browser)
    finally:
        monkeypatch.undo()
        for session in opened:
            browser.close_page(session)


def test_a_tab_is_closed_even_when_the_check_that_held_it_raised(browser: Browser) -> None:
    """⛔ The run whose tab must not leak is exactly the run that failed."""
    before = len(browser.live_pages())
    with pytest.raises(RuntimeError, match="the check failed"), OpenPage(browser):
        raise RuntimeError("the check failed")
    assert _live(browser, expecting=before) == before, "a failed check left its tab open"


def test_closing_a_tab_twice_is_harmless(browser: Browser) -> None:
    before = len(browser.live_pages())
    page = OpenPage(browser)
    page.close()
    page.close()
    assert _live(browser, expecting=before) == before, "closing twice left the count wrong"


# --- clause 1, at the seam a check actually meets: the fixture ---------------


def test_the_open_page_fixture_closes_the_tab_it_opened(browser: Browser) -> None:
    """⭐ The fixture's own generator, driven here, so its teardown is measured."""
    before = len(browser.live_pages())
    handing_over = conftest.one_tab_per_check(browser)
    page = next(handing_over)
    assert isinstance(page, OpenPage)
    assert _live(browser, expecting=before + 1) == before + 1, "the fixture opened no tab"
    with pytest.raises(StopIteration):
        next(handing_over)
    assert _live(browser, expecting=before) == before, "the fixture left its tab open"


def test_the_open_page_fixture_closes_the_tab_when_the_check_raised(browser: Browser) -> None:
    """⛔ A check that raises is torn down THROUGH the fixture, and still pays."""
    before = len(browser.live_pages())
    handing_over = conftest.one_tab_per_check(browser)
    next(handing_over)
    with pytest.raises(RuntimeError, match="the check failed"):
        handing_over.throw(RuntimeError("the check failed"))
    assert _live(browser, expecting=before) == before, "a raising check left the fixture's tab"


# --- clause 3: a browser that stops answering fails, inside a named bound -----


def _check_a_silent_browser_fails_inside_the_bound(binary: str) -> float:
    """A browser that is up and never speaks must raise, and must raise quickly."""
    running = Browser(binary)
    try:
        started = time.monotonic()
        with pytest.raises(BrowserError, match="running and silent") as raised:
            running.call("Browser.getVersion")
        spent = time.monotonic() - started
        assert "no answer" in str(raised.value), "the failure did not name what it waited for"
        assert spent < PATIENCE, f"the harness took {spent:.1f}s to give up on a silent browser"
        return spent
    finally:
        running.close()


def test_a_browser_that_is_up_and_silent_fails_instead_of_hanging(
    silent_binary: str, launch_under: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(module, "CALL_TIMEOUT", BOUND)
    spent = _check_a_silent_browser_fails_inside_the_bound(silent_binary)
    assert spent >= BOUND, f"the harness gave up in {spent:.2f}s, before the {BOUND}s it was told"
    left = sorted(launch_under.glob("studyforge-visual-*"))
    assert left == [], f"the silent browser's profile outlived it: {[p.name for p in left]}"


def test_a_browser_that_answers_still_answers_under_the_same_bound(
    browser: Browser, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⭐ The other way: the deadlined read must not break the ordinary path."""
    monkeypatch.setattr(module, "CALL_TIMEOUT", BOUND)
    assert browser.call("Browser.getVersion").get("product"), "a live browser gave no version"


# --- clause 3's instrument: the READ itself carries the deadline -------------


def _check_the_read_waits_on_a_deadline(browser: Browser, seen: list[float | None]) -> None:
    """Any reading at all must have been taken through a bounded wait."""
    browser.call("Browser.getVersion")
    assert seen, "the protocol read waited with no deadline at all"
    assert all(bound is not None and 0 < bound <= module.CALL_TIMEOUT for bound in seen), (
        f"the read waited past the bound it was given: {seen}"
    )


@pytest.fixture
def recorded_waits(monkeypatch: pytest.MonkeyPatch) -> list[float | None]:
    """Record every bound `_receive` hands `select`, while still really selecting."""
    seen: list[float | None] = []
    # ⛔ Held BEFORE the patch: `select` here and `module.select` are one module
    # object, so a wrapper that looked the name up again would call itself.
    really_select = select.select

    def _remember(
        readable: list, writable: list, erroring: list, timeout: float | None = None
    ) -> tuple:
        seen.append(timeout)
        return really_select(readable, writable, erroring, timeout)

    monkeypatch.setattr(module.select, "select", _remember)
    return seen


def test_the_protocol_read_waits_on_the_callers_deadline(
    browser: Browser, recorded_waits: list[float | None]
) -> None:
    _check_the_read_waits_on_a_deadline(browser, recorded_waits)


def test_PLANT_a_read_with_no_deadline_reddens_the_check(
    browser: Browser, recorded_waits: list[float | None], monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ The form this row replaced, against a browser that answers at once.

    ⚠️ Safe to plant only because the browser here is live and prompt: the same
    code against a SILENT browser is the hang, which is the whole defect.
    """

    def _blocking_receive(self: Browser, _deadline: float, _complaint: str) -> dict:
        while b"\0" not in self._buffer:
            self._buffer += module.os.read(self._reader, 1 << 16)
        line, self._buffer = self._buffer.split(b"\0", 1)
        return module.json.loads(line)

    monkeypatch.setattr(Browser, "_receive", _blocking_receive)
    with pytest.raises(AssertionError, match="no deadline at all"):
        _check_the_read_waits_on_a_deadline(browser, recorded_waits)
