"""One page, open in a real browser, and the five questions a test asks it.

**What it does.** Wraps a protocol session in the vocabulary the acceptance
clauses are written in: open a `file://` URL under a chosen colour scheme with
scripts on or off, evaluate an expression, capture a PNG, press a key, and read
back every request the page issued.

**How you use it.** `page = OpenPage(browser)`, then `page.open(url)`, then any
of `page.evaluate(...)`, `page.capture(path)`, `page.tab()`, `page.requests()`.
One `OpenPage` per test; the fixtures in `conftest.py` build it.

**Depends on.** `browser.Browser` and `browser.VIEWPORT`, `base64`, `pathlib`,
`time`. ⛔ The two named widths here are stated, never read out of a
stylesheet — see `WIDE`. Nothing under
`src/` — ⛔ a harness that imported the renderer to decide what a page should
look like would be asserting the code against itself.

## ⚠️ Why the scheme and the script switch are arguments to `open`

Both are set on the session **before** navigation and both survive it, so a test
that set them afterwards would measure the page it did not mean to. Making them
parameters of `open` is what stops that being a thing a caller can get wrong.
"""

from __future__ import annotations

import base64
import time
from pathlib import Path

from tests.visual.browser import VIEWPORT, Browser, BrowserError

#: The two viewports every LAYOUT clause in this package is judged at, as
#: `(width, height)`. ⛔ **Both are stated here and neither is "whatever the
#: window opened at"**: a reading about a breakpoint, taken at a width nobody
#: named, is not a reading about a breakpoint. ⭐ `WIDE` is the launch viewport,
#: so a check that sets no width runs at the wide one and this harness's default
#: population is the two-column page (`W325`). ⚠️ Which side of `chrome.css`'s
#: own threshold each falls on is asserted in `test_rail.py`, against the
#: stylesheet, so a breakpoint moved there is a red check rather than two
#: readings of one layout.
WIDE = VIEWPORT
NARROW = (720, VIEWPORT[1])

#: The two colour schemes `palette.css` defines, named as the media feature
#: spells them. ⛔ Both, always: the stylesheet's own docstring says *"a token
#: defined once is a token that is wrong in one of them — invisible to whoever
#: authored it, because they only ever looked at the theme they use"*.
SCHEMES = ("light", "dark")

#: How long a page may take to reach `readyState === "complete"`.
LOAD_TIMEOUT = 30.0

#: Seconds to let script-driven decoration settle after load — syntax
#: highlighting and the copy buttons are added by `page.js` after parsing.
#: ⚠️ Polled rather than slept through; this is only the ceiling.
SETTLE_TIMEOUT = 10.0


class OpenPage:
    """A browser tab a test drives, and the readings it takes from it."""

    def __init__(self, browser: Browser) -> None:
        """Attach a fresh tab and enable the domains every reading needs."""
        self.browser = browser
        self.session = browser.page()
        for domain in ("Page", "Runtime", "Network", "DOM"):
            browser.call(f"{domain}.enable", session=self.session)
        self._scripts = True

    # --- opening -----------------------------------------------------------

    def open(self, url: str, *, scheme: str = "light", scripts: bool = True) -> None:
        """Navigate to `url` under `scheme`, with page scripts on or off.

        ⛔ `url` is a `file://` URL. R8's floor is a page opened by
        double-clicking it, and a harness that served the tree over HTTP would
        be testing a configuration no reader has.
        """
        if scheme not in SCHEMES:
            raise ValueError(f"unknown colour scheme {scheme!r}; expected one of {SCHEMES}")
        self._set_scripts(scripts)
        self.browser.call(
            "Emulation.setEmulatedMedia",
            {"features": [{"name": "prefers-color-scheme", "value": scheme}]},
            session=self.session,
        )
        self.browser.events.clear()
        self.browser.call("Page.navigate", {"url": url}, session=self.session)
        self.browser.wait("Page.loadEventFired", timeout=LOAD_TIMEOUT)
        self._settle()

    def resize(self, width: int, height: int) -> None:
        """Set this tab's viewport, for every later navigation in it.

        ⛔ **Called BEFORE `open`, for the reason the colour scheme is an
        argument to it** (this module's docstring): a media query re-evaluated
        after the page has already been read is a reading about the page nobody
        asked about. ⭐ The override rides the session, so one call covers every
        open that follows — and each test gets a fresh tab, so nothing leaks
        into the check after it.
        """
        self.browser.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False},
            session=self.session,
        )

    def _set_scripts(self, enabled: bool) -> None:
        """Turn page scripts on or off for every later navigation in this tab."""
        self.browser.call(
            "Emulation.setScriptExecutionDisabled",
            {"value": not enabled},
            session=self.session,
        )
        self._scripts = enabled

    def _settle(self) -> None:
        """Wait for the document to finish and for one frame to have been painted.

        ⛔ **Not a wait for any particular element.** The first version of this
        polled for a copy button or a syntax token — and `depth1-unit-02` has no
        code block, so every open of the prose page spent the full ceiling
        waiting for something that was never coming, and passed. ⚠️ **A timeout
        that expires and lets the test proceed is a slow check that still says
        yes**; it cost 10 seconds per page and nothing noticed.

        ⭐ The correct wait is shorter and does not need a list: `page.js` is
        `defer`red, so it has already run by `load`, and two animation frames
        after that is a painted document.
        """
        deadline = time.monotonic() + SETTLE_TIMEOUT
        while time.monotonic() < deadline:
            if self.evaluate("document.readyState") == "complete":
                break
            time.sleep(0.02)
        if self._scripts:
            self.evaluate(
                "new Promise(done => requestAnimationFrame("
                "() => requestAnimationFrame(() => done(true))))"
            )

    # --- reading -----------------------------------------------------------

    def evaluate(self, expression: str) -> object:
        """Run `expression` in the page and return its value.

        ⛔ Raises rather than returning `None` when the page throws: a harness
        that swallowed a `ReferenceError` would report every later reading as
        `None` and every assertion about it as a pass.
        """
        result = self.browser.call(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": True},
            session=self.session,
        )
        if result.get("exceptionDetails"):
            raise BrowserError(
                f"page threw evaluating {expression!r}: {result['exceptionDetails']}"
            )
        return result.get("result", {}).get("value")

    def html(self) -> str:
        """The document as the browser now holds it, after any script has run."""
        root = self.browser.call("DOM.getDocument", {"depth": -1}, session=self.session)["root"]
        outer = self.browser.call(
            "DOM.getOuterHTML", {"nodeId": root["nodeId"]}, session=self.session
        )
        return str(outer["outerHTML"])

    def requests(self) -> list[str]:
        """Every URL the page asked for while loading, in the order it asked."""
        return [
            event["params"]["request"]["url"]
            for event in self.browser.events
            if event.get("method") == "Network.requestWillBeSent"
        ]

    def capture(self, destination: Path) -> Path:
        """Write a full-page PNG to `destination` and return it.

        ⛔ `destination` is chosen by the caller and is never inside the
        repository: a capture is an artefact of one run on one machine, and the
        path it was taken at is a home directory (R7).
        """
        shot = self.browser.call(
            "Page.captureScreenshot",
            {"format": "png", "captureBeyondViewport": True},
            session=self.session,
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(base64.b64decode(shot["data"]))
        return destination

    # --- driving -----------------------------------------------------------

    def tab(self, *, backwards: bool = False) -> None:
        """Press Tab (or Shift+Tab), moving focus the way a keyboard reader does."""
        event = {
            "key": "Tab",
            "code": "Tab",
            "windowsVirtualKeyCode": 9,
            "nativeVirtualKeyCode": 9,
            "modifiers": 8 if backwards else 0,
        }
        for kind in ("rawKeyDown", "keyUp"):
            self.browser.call(
                "Input.dispatchKeyEvent", {**event, "type": kind}, session=self.session
            )

    def focus_body(self) -> None:
        """Put focus at the top of the document, so a traversal starts where a reader's does."""
        self.evaluate("document.body.focus(); document.body.blur();")

    def focused(self) -> dict:
        """What has focus now: its tag, its href or class, its focus outline, and where it is.

        ⚠️ `at` is the element's position in document order, because a label is
        not an identity: two links to one page carry one href (`W105`).
        """
        return dict(
            self.evaluate(
                "(() => { const e = document.activeElement;"
                " if (!e || e === document.body)"
                "  return {tag: 'BODY', label: '', outline: '', at: -1};"
                " const s = getComputedStyle(e);"
                " return {tag: e.tagName,"
                "  label: e.getAttribute('href') || e.className"
                "    || e.textContent.trim().slice(0, 40),"
                "  outline: s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.outlineColor,"
                "  at: Array.prototype.indexOf.call(document.querySelectorAll('*'), e)};"
                "})()"
            )  # type: ignore[arg-type]
        )

    def trail(self, steps: int) -> list[dict]:
        """Press Tab from the top until focus comes round again, or `steps` times.

        ⛔ **Stopping at the wrap is not a convenience.** Chromium's focus ring
        is a cycle, so a fixed number of presses larger than the page's control
        count walks it two or three times — and an order compared against a list
        that has been traversed twice fails for a reason that has nothing to do
        with the order.

        ⛔ **The wrap is the SAME ELEMENT coming round, never the same href**
        (`W105`): a unit page's trail and its between-units bar both link the
        index, and a mark of tag and href ended the walk at the second one.
        """
        self.focus_body()
        seen: list[dict] = []
        first: str | None = None
        for index in range(steps):
            self.tab()
            here = self.focused()
            mark = f"{here['tag']}|{here['label']}|{here['at']}"
            if index == 0:
                first = mark
            elif mark == first:
                break
            seen.append(here)
        return seen
