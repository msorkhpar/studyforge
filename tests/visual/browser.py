"""A browser, driven over the DevTools protocol, with no dependency to install.

**What it does.** Launches a Chromium-family browser headless and speaks the
Chrome DevTools Protocol to it over `--remote-debugging-pipe` — two file
descriptors carrying NUL-delimited JSON. `Browser.page()` attaches to a fresh
tab and returns the session id every later call is addressed with.

**How you use it.** `with Browser(binary) as browser:` then
`session = browser.page()`, then `browser.call("Page.navigate", {...}, session)`.
`browser.events` accumulates everything the browser volunteered; `browser.wait`
blocks for one.

**Depends on.** `json`, `os`, `shutil`, `subprocess`, `tempfile`, `time`,
`pathlib` — the standard library, and nothing else.

## ⛔ `W312` — a launch leaves nothing behind, and its last words outlive it

⛔ **Every launch makes a fresh profile under the system temp directory, and
until `W312` nothing ever removed one.** A profile carries the browser's own
caches, the temp filesystem is quota-limited, and when it filled every shell on
the host exited `1` with no output. ⭐ **`close()` now removes the profile, and
so does a launch that fails part-way** — `__init__` hands whatever it had
already opened to `close()` before re-raising.

⭐ **The diagnostics are read BEFORE the directory goes.** `browser.log` lives
inside the profile, so `close()` reads its tail once the browser has stopped
writing, keeps it, and `diagnostics()` answers from that copy afterwards. ⛔ A
cleanup that deleted the only evidence of why a launch failed would trade one
silent failure for another.

## ⛔ `W397` — a tab is closed by whoever opened it, and a silent browser fails

⛔ **Two defects, one symptom.** `page()` opened a tab per check and nothing ever
closed one, so a session's tabs accumulated as operating-system processes until
the image could start no more renderers. ⚠️ **MEASURED by the register in the
pinned image: 190 processes, dozens of them Chrome renderers, at 0.1% CPU.**
⭐ `page()` now records the target behind each session and `close_page()` closes
it; `live_pages()` is how a check counts what is still open.

⛔ **And the wait had no floor under it.** `call` computed a deadline and looped
on it, but the loop body blocked in `os.read` on a live pipe — so a browser that
was UP AND SILENT was never given up on, and `"no answer in 30s"` was
unreachable. ⭐ `_receive` now waits with `select` until the SAME deadline, so a
browser that stops answering FAILS the check instead of hanging the suite.
⚠️ `docker/dev/check`'s outer bound stays where it is: it catches a hang
anywhere, and this catches this one with a verdict attached.

## ⛔ Why the pipe and not a WebSocket, and why no driver library

⭐ **The transport is the whole reason this file is short.** `--remote-debugging-port`
answers on a WebSocket, and a WebSocket needs framing that the standard library
does not implement — so that road ends at a third-party client. The pipe carries
the *same protocol* as NUL-delimited JSON on fds 3 and 4, which `os.read` and
`os.write` already do.

⚠️ **Putting the pipe ends on fds 3 and 4 is the fiddly part**, and the first
version of it worked by hand and failed under `pytest`. `_place_pipe_on_three_and_four`
carries the whole story.

⛔ **No `pip install`, deliberately.** `tests/` may take a test-only dependency
(the framework may not), but the two candidates both fail the same way: they
would be absent in the pinned image *and* absent on a fresh host, and a harness
that quietly does nothing when its dependency is missing is worse than no
harness. What is missing here is a *browser*, which is a fact about the machine
that `discovery.py` states out loud rather than a package a resolver could hide.
"""

from __future__ import annotations

import json
import os
import select
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

#: Flags every launch carries. ⛔ `--headless=new` so there is no display
#: requirement, `--force-color-profile=srgb` and `--force-device-scale-factor=1`
#: so a colour read back through `getComputedStyle` is the colour the stylesheet
#: wrote rather than one a profile transformed, and the three `--disable-*`
#: network flags so a page that issues no request cannot be *reported* as
#: issuing one by the browser's own background traffic (R8's check depends on
#: that being true).
LAUNCH_FLAGS = (
    "--headless=new",
    "--remote-debugging-pipe",
    "--no-sandbox",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-extensions",
    "--disable-component-extensions-with-background-pages",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-sync",
    "--no-pings",
    "--metrics-recording-only",
    "--hide-scrollbars",
    "--force-color-profile=srgb",
    "--force-device-scale-factor=1",
)

#: The viewport every capture is taken at. Fixed, because a screenshot compared
#: across runs at a size the window manager chose is not a comparison.
VIEWPORT = (1280, 900)

#: Seconds a single protocol call may take before the harness gives up. A
#: browser that has wedged must fail the test rather than hang the suite.
CALL_TIMEOUT = 30.0


#: The highest descriptor the child is allowed to inherit. Everything above the
#: protocol pipe is closed on the way in, which is what `close_fds=True` would
#: have done for us if it did not also close the pipe.
LAST_INHERITED_FD = 4


#: Attempts `_remove_profile` makes before it reports the profile as left behind.
#: ⚠️ A browser's helper processes can still be writing into the profile for a
#: moment after the main process has exited, so one pass can race them.
REMOVAL_ATTEMPTS = 20


class BrowserError(RuntimeError):
    """The browser refused a call, died, or never answered."""


def _remove_profile(profile: str) -> None:
    """Remove one launch's profile, retrying past a helper that is still writing.

    ⛔ Raises `BrowserError` when the directory survives every attempt, so a
    profile left behind is a failure somebody reads rather than a quota that
    fills in silence (`W312`).
    """
    for _attempt in range(REMOVAL_ATTEMPTS):
        shutil.rmtree(profile, ignore_errors=True)
        if not os.path.lexists(profile):
            return
        time.sleep(0.05)
    raise BrowserError(f"the browser profile survived {REMOVAL_ATTEMPTS} removals: {profile}")


def _place_pipe_on_three_and_four(reader: int, writer: int):
    """Return a child-side hook putting the pipe ends on fds 3 and 4 and closing the rest.

    ⛔ **Why this is not a one-line shell redirection, which is what it was.**
    `--remote-debugging-pipe` reads fd 3 and writes fd 4, and the obvious way to
    arrange that is `sh -c 'exec 3<&N 4>&M; exec chrome …'`. ⚠️ **`dash` — which
    is `/bin/sh` on Debian, and therefore inside this project's own image —
    accepts only a single digit** in `n<&word`. Under `pytest` the pipe ends
    land above fd 9 because the session already has files open, so the wrapper
    failed with `Bad fd number` **only when run from the suite** and worked
    every time it was tried by hand. ⭐ Doing it in Python removes both the
    shell and the digit.

    ⚠️ `close_fds=False` is required and is why the hook closes the rest itself:
    `subprocess` runs this hook *before* its own descriptor sweep, so anything
    duplicated here would be swept away again before `exec`.
    """

    def place() -> None:  # pragma: no cover - runs in the forked child
        ends = []
        for end in (reader, writer):
            while end <= LAST_INHERITED_FD:
                end = os.dup(end)
            ends.append(end)
        os.dup2(ends[0], 3)
        os.dup2(ends[1], 4)
        os.closerange(LAST_INHERITED_FD + 1, os.sysconf("SC_OPEN_MAX"))

    return place


class Browser:
    """One headless browser process and the protocol connection to it."""

    def __init__(self, binary: str) -> None:
        """Launch `binary` headless with a throwaway profile.

        ⛔ **A launch that fails part-way leaves nothing behind** (`W312`): the
        profile exists from the first line, so every later step runs under a
        handler that gives what was opened to `close()` and re-raises.
        """
        self.binary = binary
        # ⛔ A fresh profile per launch, under the system temp directory: a
        # shared profile carries state between runs, which is the failure R10
        # is about wearing a different hat.
        self._profile = tempfile.mkdtemp(prefix="studyforge-visual-")
        self._reader: int | None = None
        self._writer: int | None = None
        self._log = None
        self._process: subprocess.Popen | None = None
        #: The log's tail, kept by `close()` before the profile holding it goes.
        self._last_words = ""
        self._closed = False
        self._buffer = b""
        self._next_id = 0
        #: The target behind each attached session, so `close_page` can close it.
        self._targets: dict[str, str] = {}
        #: Whether the browser has been asked to announce target lifetimes.
        self._discovering = False
        #: Every event the browser volunteered, oldest first. Callers clear it.
        self.events: list[dict] = []
        try:
            self._launch(binary)
        except BaseException:
            self.close()
            raise

    def _launch(self, binary: str) -> None:
        """Open the pipe and the log, and start the browser on them."""
        self._reader, writer_end = os.pipe()
        try:
            reader_end, self._writer = os.pipe()
        except BaseException:
            os.close(writer_end)
            raise
        try:
            os.set_inheritable(reader_end, True)
            os.set_inheritable(writer_end, True)
            argv = [
                binary,
                *LAUNCH_FLAGS,
                f"--window-size={VIEWPORT[0]},{VIEWPORT[1]}",
                f"--user-data-dir={self._profile}",
                "about:blank",
            ]
            # ⛔ The browser's own diagnostics are kept, not discarded. A
            # protocol pipe that closes says only "the browser went away"; the
            # reason is on its stderr, and a harness that threw that away would
            # report every launch failure with the same unhelpful sentence.
            # ⭐ It is also how the `dash` defect above was found in one run
            # instead of an afternoon.
            self._log = open(Path(self._profile) / "browser.log", "w+b")  # noqa: SIM115
            self._process = subprocess.Popen(  # noqa: S603 - fixed argv, no user input
                argv,
                close_fds=False,
                preexec_fn=_place_pipe_on_three_and_four(reader_end, writer_end),  # noqa: PLW1509
                stdout=subprocess.DEVNULL,
                stderr=self._log,
            )
        finally:
            os.close(reader_end)
            os.close(writer_end)

    # --- the protocol ------------------------------------------------------

    def call(self, method: str, params: dict | None = None, session: str | None = None) -> dict:
        """Send one command and return its result, queueing any event that arrives first."""
        self._next_id += 1
        wanted = self._next_id
        message: dict = {"id": wanted, "method": method, "params": params or {}}
        if session is not None:
            message["sessionId"] = session
        os.write(self._writer, json.dumps(message).encode("utf-8") + b"\0")
        complaint = f"{method}: no answer in {CALL_TIMEOUT:.0f}s"
        deadline = time.monotonic() + CALL_TIMEOUT
        while time.monotonic() < deadline:
            received = self._receive(deadline, complaint)
            if received.get("id") == wanted:
                if "error" in received:
                    raise BrowserError(f"{method}: {received['error']}")
                return received.get("result", {})
            if "method" in received:
                self.events.append(received)
        raise BrowserError(complaint)

    def wait(self, method: str, timeout: float = CALL_TIMEOUT) -> dict:
        """Return the first queued or incoming event named `method`."""
        for event in self.events:
            if event.get("method") == method:
                return event
        complaint = f"no {method} in {timeout:.0f}s"
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            received = self._receive(deadline, complaint)
            if "method" not in received:
                continue
            self.events.append(received)
            if received["method"] == method:
                return received
        raise BrowserError(complaint)

    # --- tabs --------------------------------------------------------------

    def page(self) -> str:
        """Open a tab, attach to it, and return the session id calls are addressed with.

        ⛔ **Whoever calls this owns `close_page`** (`W397`). A tab is a set of
        operating-system processes, not a handle, and a session that opens one
        per check and closes none ends where the register found this one.
        """
        self._discover_targets()
        target = self.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        attached = self.call("Target.attachToTarget", {"targetId": target, "flatten": True})
        session = attached["sessionId"]
        self._targets[session] = target
        return session

    def close_page(self, session: str) -> None:
        """Close the tab `session` addresses, and RETURN ONLY ONCE IT IS GONE.

        ⛔ **Waiting is the whole of `W397/3`, and it is not tidiness.**
        `Target.closeTarget` is answered when the browser has ACCEPTED the
        close, not when the tab is destroyed — ⚠️ **MEASURED in the pinned
        image: the target is still listed for 10-13 ms on an idle machine and
        for 26-100 ms under 24 competing processes.** ⛔ So a caller that read
        `Target.getTargets` after this returned read a count that included tabs
        the browser was still destroying, and the number it got depended on how
        busy the machine was. ⭐ Waiting for the browser's OWN
        `Target.targetDestroyed` makes every count taken afterwards correct by
        construction, rather than correct when the machine happens to be quiet.

        ⭐ Safe twice, and safe after `close()`.
        """
        if self._closed:
            return
        target = self._targets.pop(session, None)
        if target is not None:
            self.call("Target.closeTarget", {"targetId": target})
            self._await_destroyed(target)

    def _discover_targets(self) -> None:
        """Ask the browser to announce target lifetimes. Once per browser.

        ⛔ `Target.targetDestroyed` is not emitted until discovery is on, so
        this is what makes `close_page`'s wait possible at all.
        """
        if not self._discovering:
            self.call("Target.setDiscoverTargets", {"discover": True})
            self._discovering = True

    @staticmethod
    def _destroys(event: dict, target: str) -> bool:
        """Report whether `event` is the browser saying `target` is gone."""
        return (
            event.get("method") == "Target.targetDestroyed"
            and event.get("params", {}).get("targetId") == target
        )

    def _await_destroyed(self, target: str) -> None:
        """Block until the browser reports `target` destroyed, or give up at the bound."""
        if any(self._destroys(event, target) for event in self.events):
            return
        complaint = f"the closed tab was not destroyed in {CALL_TIMEOUT:.0f}s"
        deadline = time.monotonic() + CALL_TIMEOUT
        while time.monotonic() < deadline:
            received = self._receive(deadline, complaint)
            if "method" not in received:
                continue
            self.events.append(received)
            if self._destroys(received, target):
                return
        raise BrowserError(complaint)

    def live_pages(self) -> list[str]:
        """The id of every page target the browser still holds open.

        ⭐ Asked of the BROWSER rather than of this object's bookkeeping, so a
        count taken over many checks measures the processes and not the
        intention (`W397`).
        """
        targets = self.call("Target.getTargets")["targetInfos"]
        return [info["targetId"] for info in targets if info.get("type") == "page"]

    def _receive(self, deadline: float, complaint: str) -> dict:
        """Read one NUL-delimited message, giving up at `deadline`.

        ⛔ **The bound is on the READ, not only on the loop around it** (`W397`).
        This blocked in `os.read` on a live pipe, so a browser that was up and
        silent was waited on forever and every caller's deadline was dead code.
        ⭐ `select` waits until the same instant the caller named, and `complaint`
        is the caller's own sentence so the failure says what was waited for.
        """
        while b"\0" not in self._buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self._reader], [], [], remaining)[0]:
                raise BrowserError(
                    f"{complaint} — {self.binary} is running and silent. "
                    f"Its own last words: {self.diagnostics()!r}"
                )
            chunk = os.read(self._reader, 1 << 16)
            if not chunk:
                raise BrowserError(
                    f"{self.binary} closed the protocol pipe (exit {self._process.poll()}). "
                    f"Its own last words: {self.diagnostics()!r}"
                )
            self._buffer += chunk
        line, self._buffer = self._buffer.split(b"\0", 1)
        return json.loads(line)

    def diagnostics(self) -> str:
        """The tail of whatever the browser wrote to its standard error.

        ⭐ Once closed, the tail `close()` read before removing the profile.
        """
        if self._log is None or self._log.closed:
            return self._last_words
        return self._read_log()

    def _read_log(self) -> str:
        """Read the tail of the open log."""
        try:
            self._log.flush()
            self._log.seek(0)
            return self._log.read().decode("utf-8", "replace").strip()[-2000:]
        except OSError, ValueError:  # pragma: no cover - the log is already gone
            return ""

    def _keep_last_words(self) -> None:
        """Copy the log's tail out of the profile, so removing it loses nothing."""
        self._last_words = self._read_log()

    # --- lifetime ----------------------------------------------------------

    def close(self) -> None:
        """Stop the browser, whatever state it is in, and remove its profile.

        ⛔ **Order is the point** (`W312`): the browser is stopped first so its
        last words are written, they are read second, and only then does the
        directory holding them go. ⭐ Safe on a half-made launch and safe twice.
        """
        if self._closed:
            return
        self._closed = True
        self._targets.clear()
        try:
            for closing in (self._writer, self._reader):
                if closing is None:
                    continue
                try:
                    os.close(closing)
                except OSError:  # pragma: no cover - already closed
                    pass
            if self._process is not None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=10)
                except subprocess.TimeoutExpired:  # pragma: no cover - a wedged browser
                    self._process.kill()
                    self._process.wait(timeout=10)
            if self._log is not None:
                self._keep_last_words()
                self._log.close()
        finally:
            _remove_profile(self._profile)

    def __enter__(self) -> Browser:
        """Return self, so a caller can use `with Browser(...) as browser:`."""
        return self

    def __exit__(self, *_exception: object) -> None:
        """Stop the browser on the way out, including on failure."""
        self.close()
