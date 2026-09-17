"""`W312` — a launched browser leaves nothing behind, and its last words survive.

⛔ **The defect this module exists for.** `Browser.__init__` made a fresh profile
under the system temp directory and `close()` never removed it. Each profile
carries the browser's own caches, the temp filesystem is quota-limited, and
when it filled every shell on the host exited `1` with no output.

⭐ **Two arms, and the real one is the one that counts.** The REAL-browser arm
takes its binary from the session `browser` fixture — the one licensed ambient
reader (`conftest.py`) — so it RUNS in the pinned image, which carries a browser
(`W36`), and skips loudly where there is none. ⚠️ The FAKE arm is additional,
never a substitute: it reaches the failures a real browser will not produce on
demand — a browser that dies at once, a binary that is not there, and a launch
that fails after the profile exists.

⛔ **Every settling clause is asserted both ways (R12).** Each check is a helper
that a test calls plainly, and a plant test calls again under
`monkeypatch` with the removal or the kept log switched off — where it must
raise `AssertionError`. ⭐ A check that cannot be made red by removing the thing
it checks is not a check.

⭐ **Every launch here is redirected under `tmp_path`** by pointing
`tempfile.tempdir` at it, so a plant that leaves a profile behind leaves it where
this test removes it, never in the shared temp directory `W312` is about.
"""

from __future__ import annotations

import shutil
import stat
import tempfile
from pathlib import Path

import pytest

from tests.visual import browser as module
from tests.visual.browser import Browser, BrowserError

#: What the fake browser says on its way out, so its survival is recognisable.
LAST_WORDS = "fake browser: refusing to start"


def _profiles(root: Path) -> list[Path]:
    """Every launch profile under `root`."""
    return sorted(root.glob("studyforge-visual-*"))


@pytest.fixture
def launch_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A temp directory every launch in this test makes its profile under."""
    root = tmp_path / "launches"
    root.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(root))
    return root


@pytest.fixture
def dying_binary(tmp_path: Path) -> str:
    """A 'browser' that prints its last words to stderr and exits at once."""
    script = tmp_path / "dying-browser"
    script.write_text(f"#!/bin/sh\necho '{LAST_WORDS}' >&2\nexit 3\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return str(script)


def _sweep(root: Path) -> None:
    """Remove what a planted run left behind, so a plant never fills a disk."""
    for profile in _profiles(root):
        shutil.rmtree(profile, ignore_errors=True)


# --- the checks, each called plainly and again under a plant -----------------


def _check_a_used_browser_leaves_nothing(binary: str, root: Path) -> None:
    """Ordinary path: launch, drive one call, close — no profile remains."""
    with Browser(binary) as running:
        assert _profiles(root) == [Path(running._profile)], "the launch made no profile here"
        running.page()
    assert _profiles(root) == [], f"a closed browser left its profile: {_profiles(root)}"


def _check_a_failing_test_leaves_nothing(binary: str, root: Path) -> None:
    """A test that raises inside the `with` still removes the profile."""
    with pytest.raises(RuntimeError, match="the test failed"), Browser(binary):
        raise RuntimeError("the test failed")
    assert _profiles(root) == [], f"a failed test left its profile: {_profiles(root)}"


def _check_a_browser_that_never_starts_leaves_nothing_and_keeps_its_words(
    binary: str, root: Path
) -> None:
    """The browser dies at launch: its words are reported, then kept, then the profile goes."""
    running = Browser(binary)
    with pytest.raises(BrowserError) as raised:
        running.call("Browser.getVersion")
    assert LAST_WORDS in str(raised.value), "the failure did not report the browser's words"
    running.close()
    assert _profiles(root) == [], f"a browser that never started left: {_profiles(root)}"
    assert LAST_WORDS in running.diagnostics(), "the diagnostics were lost with the profile"


def _check_a_launch_failing_after_the_profile_exists_leaves_nothing(root: Path) -> None:
    """`__init__` raising after `mkdtemp` still removes what it made."""
    with pytest.raises(OSError, match="planted launch failure"):
        Browser("/path/to/any-browser")
    assert _profiles(root) == [], f"a failed launch left its profile: {_profiles(root)}"


def _check_a_missing_binary_leaves_nothing(root: Path) -> None:
    """A binary that does not exist never starts — and still leaves nothing.

    ⚠️ It does NOT raise at launch: the child-side hook closes every descriptor
    above the pipe, `subprocess`'s own exec-error pipe included, so the failure
    arrives at the first call as a closed pipe (`W312/1`).
    """
    running = Browser(str(root / "no-such-browser"))
    with pytest.raises(BrowserError, match="closed the protocol pipe"):
        running.call("Browser.getVersion")
    running.close()
    assert _profiles(root) == [], f"a missing binary left its profile: {_profiles(root)}"


def _refuse_popen(*_args: object, **_kwargs: object) -> None:
    raise OSError("planted launch failure")


def _keep_nothing(_profile: str) -> None:
    """The plant: a removal that removes nothing."""


# --- the real browser --------------------------------------------------------


def test_a_real_browser_closed_on_the_ordinary_path_leaves_no_profile(
    browser: Browser, launch_root: Path
) -> None:
    _check_a_used_browser_leaves_nothing(browser.binary, launch_root)


def test_a_real_browser_closed_by_a_failing_test_leaves_no_profile(
    browser: Browser, launch_root: Path
) -> None:
    _check_a_failing_test_leaves_nothing(browser.binary, launch_root)


def test_PLANT_a_real_browser_whose_removal_is_skipped_reddens_the_check(
    browser: Browser, launch_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(module, "_remove_profile", _keep_nothing)
    try:
        with pytest.raises(AssertionError, match="left its profile"):
            _check_a_used_browser_leaves_nothing(browser.binary, launch_root)
    finally:
        _sweep(launch_root)


# --- a fake browser, for the failures a real one will not produce on demand ---


def test_a_browser_that_never_starts_leaves_no_profile_and_its_words_survive(
    dying_binary: str, launch_root: Path
) -> None:
    _check_a_browser_that_never_starts_leaves_nothing_and_keeps_its_words(
        dying_binary, launch_root
    )


def test_PLANT_a_browser_that_never_starts_whose_removal_is_skipped_reddens_the_check(
    dying_binary: str, launch_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(module, "_remove_profile", _keep_nothing)
    try:
        with pytest.raises(AssertionError, match="never started left"):
            _check_a_browser_that_never_starts_leaves_nothing_and_keeps_its_words(
                dying_binary, launch_root
            )
    finally:
        _sweep(launch_root)


def test_PLANT_diagnostics_not_kept_before_removal_reddens_the_check(
    dying_binary: str, launch_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Browser, "_keep_last_words", lambda _self: None)
    with pytest.raises(AssertionError, match="diagnostics were lost"):
        _check_a_browser_that_never_starts_leaves_nothing_and_keeps_its_words(
            dying_binary, launch_root
        )


def test_a_fake_browser_closed_by_a_failing_test_leaves_no_profile(
    dying_binary: str, launch_root: Path
) -> None:
    _check_a_failing_test_leaves_nothing(dying_binary, launch_root)


def test_PLANT_a_failing_test_whose_removal_is_skipped_reddens_the_check(
    dying_binary: str, launch_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(module, "_remove_profile", _keep_nothing)
    with pytest.raises(AssertionError, match="failed test left"):
        _check_a_failing_test_leaves_nothing(dying_binary, launch_root)


def test_a_launch_failing_after_the_profile_exists_leaves_no_profile(
    launch_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(module.subprocess, "Popen", _refuse_popen)
    _check_a_launch_failing_after_the_profile_exists_leaves_nothing(launch_root)


def test_PLANT_a_failed_launch_whose_removal_is_skipped_reddens_the_check(
    launch_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(module.subprocess, "Popen", _refuse_popen)
    monkeypatch.setattr(module, "_remove_profile", _keep_nothing)
    with pytest.raises(AssertionError, match="failed launch left"):
        _check_a_launch_failing_after_the_profile_exists_leaves_nothing(launch_root)


def test_a_missing_binary_leaves_no_profile(launch_root: Path) -> None:
    _check_a_missing_binary_leaves_nothing(launch_root)


def test_PLANT_a_missing_binary_whose_removal_is_skipped_reddens_the_check(
    launch_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(module, "_remove_profile", _keep_nothing)
    with pytest.raises(AssertionError, match="missing binary left"):
        _check_a_missing_binary_leaves_nothing(launch_root)


def test_closing_twice_is_harmless_and_keeps_the_words(
    dying_binary: str, launch_root: Path
) -> None:
    running = Browser(dying_binary)
    running.close()
    words = running.diagnostics()
    running.close()
    assert running.diagnostics() == words
    assert _profiles(launch_root) == []


def test_a_profile_that_survives_every_removal_is_a_failure_and_not_silence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ Both ways: a removable profile goes quietly; an unremovable one is named."""
    removable = tmp_path / "removable"
    removable.mkdir()
    module._remove_profile(str(removable))
    assert not removable.exists()

    stubborn = tmp_path / "stubborn"
    stubborn.mkdir()
    monkeypatch.setattr(module.shutil, "rmtree", lambda *_a, **_k: None)
    monkeypatch.setattr(module.time, "sleep", lambda _s: None)
    with pytest.raises(BrowserError, match="survived"):
        module._remove_profile(str(stubborn))
