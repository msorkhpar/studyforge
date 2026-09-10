"""A browser, driven over the DevTools protocol, with no dependency to install.

**What it does.** Launches a Chromium-family browser headless and speaks the
Chrome DevTools Protocol to it over `--remote-debugging-pipe` — two file
descriptors carrying NUL-delimited JSON. `Browser.page()` attaches to a fresh
tab and returns the session id every later call is addressed with.

**How you use it.** `with Browser(binary) as browser:` then
`session = browser.page()`, then `browser.call("Page.navigate", {...}, session)`.
`browser.events` accumulates everything the browser volunteered; `browser.wait`
blocks for one.

**Depends on.** `json`, `os`, `subprocess`, `tempfile`, `time`, `pathlib` — the
standard library, and nothing else.

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


class BrowserError(RuntimeError):
    """The browser refused a call, died, or never answered."""


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
        """Launch `binary` headless with a throwaway profile."""
        self.binary = binary
        self._reader, writer_end = os.pipe()
        reader_end, self._writer = os.pipe()
        os.set_inheritable(reader_end, True)
        os.set_inheritable(writer_end, True)
        # ⛔ A fresh profile per launch, under the system temp directory: a
        # shared profile carries state between runs, which is the failure R10
        # is about wearing a different hat.
        self._profile = tempfile.mkdtemp(prefix="studyforge-visual-")
        argv = [
            binary,
            *LAUNCH_FLAGS,
            f"--window-size={VIEWPORT[0]},{VIEWPORT[1]}",
            f"--user-data-dir={self._profile}",
            "about:blank",
        ]
        # ⛔ The browser's own diagnostics are kept, not discarded. A protocol
        # pipe that closes says only "the browser went away"; the reason is on
        # its stderr, and a harness that threw that away would report every
        # launch failure with the same unhelpful sentence. ⭐ It is also how the
        # `dash` defect above was found in one run instead of an afternoon.
        self._log = open(Path(self._profile) / "browser.log", "w+b")  # noqa: SIM115
        self._process = subprocess.Popen(  # noqa: S603 - fixed argv, no user input
            argv,
            close_fds=False,
            preexec_fn=_place_pipe_on_three_and_four(reader_end, writer_end),  # noqa: PLW1509
            stdout=subprocess.DEVNULL,
            stderr=self._log,
        )
        os.close(reader_end)
        os.close(writer_end)
        self._buffer = b""
        self._next_id = 0
        #: Every event the browser volunteered, oldest first. Callers clear it.
        self.events: list[dict] = []

    # --- the protocol ------------------------------------------------------

    def call(self, method: str, params: dict | None = None, session: str | None = None) -> dict:
        """Send one command and return its result, queueing any event that arrives first."""
        self._next_id += 1
        wanted = self._next_id
        message: dict = {"id": wanted, "method": method, "params": params or {}}
        if session is not None:
            message["sessionId"] = session
        os.write(self._writer, json.dumps(message).encode("utf-8") + b"\0")
        deadline = time.monotonic() + CALL_TIMEOUT
        while time.monotonic() < deadline:
            received = self._receive()
            if received.get("id") == wanted:
                if "error" in received:
                    raise BrowserError(f"{method}: {received['error']}")
                return received.get("result", {})
            if "method" in received:
                self.events.append(received)
        raise BrowserError(f"{method}: no answer in {CALL_TIMEOUT:.0f}s")

    def wait(self, method: str, timeout: float = CALL_TIMEOUT) -> dict:
        """Return the first queued or incoming event named `method`."""
        for event in self.events:
            if event.get("method") == method:
                return event
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            received = self._receive()
            if "method" not in received:
                continue
            self.events.append(received)
            if received["method"] == method:
                return received
        raise BrowserError(f"no {method} in {timeout:.0f}s")

    def page(self) -> str:
        """Open a tab, attach to it, and return the session id calls are addressed with."""
        target = self.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        attached = self.call("Target.attachToTarget", {"targetId": target, "flatten": True})
        return attached["sessionId"]

    def _receive(self) -> dict:
        """Read one NUL-delimited message, blocking until the browser sends it."""
        while b"\0" not in self._buffer:
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
        """The tail of whatever the browser wrote to its standard error."""
        try:
            self._log.flush()
            self._log.seek(0)
            return self._log.read().decode("utf-8", "replace").strip()[-2000:]
        except OSError, ValueError:  # pragma: no cover - the log is already gone
            return ""

    # --- lifetime ----------------------------------------------------------

    def close(self) -> None:
        """Stop the browser, whatever state it is in."""
        for closing in (self._writer, self._reader):
            try:
                os.close(closing)
            except OSError:  # pragma: no cover - already closed
                pass
        self._log.close()
        self._process.terminate()
        try:
            self._process.wait(timeout=10)
        except subprocess.TimeoutExpired:  # pragma: no cover - a wedged browser
            self._process.kill()
            self._process.wait(timeout=10)

    def __enter__(self) -> Browser:
        """Return self, so a caller can use `with Browser(...) as browser:`."""
        return self

    def __exit__(self, *_exception: object) -> None:
        """Stop the browser on the way out, including on failure."""
        self.close()
