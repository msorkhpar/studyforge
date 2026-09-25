"""One page, open in a real browser, and the five questions a test asks it.

**What it does.** Wraps a protocol session in the vocabulary the acceptance
clauses are written in: open a `file://` URL under a chosen colour scheme with
scripts on or off, evaluate an expression, capture a PNG, press a key, and read
back every request the page issued.

**How you use it.** `with OpenPage(browser) as page:`, then `page.open(url)`,
then any of `page.evaluate(...)`, `page.capture(path)`, `page.tab()`,
`page.requests()`. One `OpenPage` per test; the fixtures in `conftest.py` build
it, and close it.

## ⛔ The object that opened the tab closes it

⛔ **A tab is a set of operating-system processes**; the `browser` fixture is
session-scoped and this one is per check, so a tab that outlived its check would
accumulate until the pinned image could start no more renderers and the whole
directory hung. ⭐ **`close()` closes
the target, `__exit__` calls it, and `conftest.py`'s fixture is the wrapper that
makes every check pay it.** ⛔ A caller that builds one outside the fixture —
`test_contrast.py`'s module-scoped reading does — owns the same closing.

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
#: population is the two-column page. ⚠️ Which side of `chrome.css`'s
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

#: The keys `press` knows, as `(code, virtual key code, the text it types)`.
#: ⛔ A named table rather than a caller passing raw protocol fields: a key
#: dispatched with the wrong `code` is delivered and ignored, which reads in a
#: check as the PAGE refusing the keyboard.
KEYS = {
    "Enter": ("Enter", 13, "\r"),
    " ": ("Space", 32, " "),
    "Escape": ("Escape", 27, None),
    #: ⭐ How a TABLIST is traversed, and the only way to reach its second tab:
    #: a roving `tabindex` puts exactly one tab in the focus ring, so Tab
    #: reaches the selected one and an arrow moves between them.
    "ArrowRight": ("ArrowRight", 39, None),
}

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
        self._open = True
        try:
            for domain in ("Page", "Runtime", "Network", "DOM"):
                browser.call(f"{domain}.enable", session=self.session)
        except BaseException:
            # ⛔ A tab that fails half-way through setup is still a tab.
            self.close()
            raise
        self._scripts = True

    # --- lifetime ----------------------------------------------------------

    def close(self) -> None:
        """Close this tab. Safe twice, and safe once the browser itself has gone.

        ⛔ Closing the TARGET and not merely detaching the session:
        a detached tab keeps its renderer, so a harness that only detached would
        accumulate exactly what this closes.
        """
        if not self._open:
            return
        self._open = False
        self.browser.close_page(self.session)

    def __enter__(self) -> OpenPage:
        """Return self, so a caller can use `with OpenPage(browser) as page:`."""
        return self

    def __exit__(self, *_exception: object) -> None:
        """Close the tab on the way out, including on failure."""
        self.close()

    # --- opening -----------------------------------------------------------

    def open(self, url: str, *, scheme: str = "light", scripts: bool = True) -> None:
        """Navigate to `url` under `scheme`, with page scripts on or off.

        ⭐ **`url` is a `file://` URL for every clause but one, and that is the
        default rather than a rule this method enforces.** R8's floor is a page
        opened by double-clicking it, so a harness that only ever served the
        tree would be testing a configuration no reader has.

        ⛔ **The one exception is the served practice panel, and it is an
        ADDITION to that floor and never a retreat from it.** The practice panel's controls exist
        only
        where `window.studyforge.run.available()` is true — which
        `run-client.js` answers from `location.protocol` — so the panel's
        keyboard behaviour is unreadable over `file://`. ⚠️ `served.py` opens the SAME built bytes
        over a loopback origin for that one reading; every other clause in this
        package still opens the file.
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

        ⛔ **Not a wait for any particular element.** A wait for a copy button or
        a syntax token spends the full ceiling on a prose page with no code
        block, waiting for something that never comes, and then passes. ⚠️ **A
        timeout that expires and lets the test proceed is a slow check that
        still says yes.**

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

    def press(self, key: str) -> None:
        """Press and release one named key where focus is, as a reader would.

        ⛔ **A real key event, for the reason `test_keyboard`'s docstring gives
        about focus**: activating a control by calling `element.click()` proves
        nothing about whether a keyboard can reach or fire it, and a panel whose
        buttons were `<div>`s would pass such a check.

        ⚠️ **Enter carries `text`, and that is not decoration.** Chromium fires
        a button's activation from the *character* event for Enter, so a
        `rawKeyDown` alone lands on the control and does nothing — which reads
        as *"the keyboard cannot press this button"* and would have been
        reported as a defect in the page.
        """
        if key not in KEYS:
            raise ValueError(f"unknown key {key!r}; this harness presses {sorted(KEYS)}")
        code, number, text = KEYS[key]
        event = {
            "key": key,
            "code": code,
            "windowsVirtualKeyCode": number,
            "nativeVirtualKeyCode": number,
            "modifiers": 0,
        }
        down = {**event, "type": "keyDown"}
        if text is not None:
            down["text"] = text
        for message in (down, {**event, "type": "keyUp"}):
            self.browser.call("Input.dispatchKeyEvent", message, session=self.session)

    def focus_body(self) -> None:
        """Put focus at the top of the document, so a traversal starts where a reader's does."""
        self.evaluate("document.body.focus(); document.body.blur();")

    def focused(self) -> dict:
        """What has focus now: its tag, its href or class, its focus outline, and where it is.

        ⚠️ `at` is the element's position in document order, because a label is
        not an identity: two links to one page carry one href.
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

        ⛔ **The wrap is the SAME ELEMENT coming round, never the same href**:
        a unit page's trail and its between-units bar both link the index, and
        a mark of tag and href would end the walk at the second one.
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

    def open_practice(self, index: int = 0) -> None:
        """Open the page's practice card number `index` in its workspace, and wait for it.

        ⭐ **A practice is worked in the page's workspace** (the user's ruling):
        its statement and panel are hidden under the *Practice (n)* list until
        a card opens them, so a reading of the panel opens one first. ⚠️ The
        card's link is followed with `click()` — opening is not what these
        readings are about, and `test_practice_workspace.py` opens by keyboard.
        """
        opened = self.evaluate(
            "(() => { const links = document.querySelectorAll("
            "'a[data-practices-part=\"open\"]');"
            f" const link = links[{int(index)}]; if (!link) return false;"
            " link.click();"
            " return document.documentElement.hasAttribute('data-workspace-open'); })()"
        )
        if opened is not True:
            raise AssertionError(f"practice card {index} did not open the workspace")
