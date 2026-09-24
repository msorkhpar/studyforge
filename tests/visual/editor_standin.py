"""A stand-in editor on its own loopback origin that takes focus as it starts, as a workbench does.

**What it does.** Serves `/main` and `/test`: each is one `<textarea>` whose
page script calls `focus()` on it twice as the document starts, with no
`preventScroll` — ⭐ the shape measured in code-server 4.137.0, where
`restoreParts()` focuses the editor group and the editor that opens the window's
file then focuses its input. Each `focus()` it makes and every value
typed into it is reported back to this server, so a check can read what
happened INSIDE a frame of another origin without reaching into it.

**How you use it.** `with editor_standin.running() as editor:` then
`served.serving(built, editor=editor.origin)`; `editor.focused` counts the
focus calls made, `editor.typed` is the last value typed, and `editor.wait_for`
blocks until either reaches what a check awaits.

**Depends on.** `http.server`, `threading`, `urllib.parse`, `contextlib`.
⛔ Nothing under `src/`: this is a stand-in for somebody else's
program, and the page under test must not be able to tell it from one.

## ⛔ Why ANOTHER origin, and not `served.WINDOW_URLS`

⚠️ `about:blank` has no script of its own, and the defect is the framed
document's OWN script taking focus. ⭐ A second loopback port is the same site
and a different origin — exactly the relation between a study page and the
editor on a reader's machine — so the browser treats its `focus()` the way it
treats the workbench's.

## ⛔ `W458` — a report is ordered by its NUMBER, never by when it arrived

⚠️ **Each report is a separate `fetch`, and this server answers each on its own
thread**, so under load the reports of four keystrokes can land in any order.
⛔ **Measured, not supposed:** with the last arrival winning, `typed` settled on
`'w44'` and on `'w4'` after `'w449'` had been typed, and a check waiting for
`'w449'` timed out on a frame that had done everything right. ⭐ So the page
numbers every report and `typed` is the value of the HIGHEST number seen,
which is the value the textarea holds last whatever order the reports took.

⭐ **And a wait is a wait on the report itself.** Every report notifies
`changed`, so `wait_for` wakes on the report that satisfies it rather than on
a polling tick.
"""

from __future__ import annotations

import contextlib
import threading
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

#: How many times the stand-in focuses its input as it starts, and when.
#: ⭐ Two, after the document has loaded — the workbench's two calls.
FOCUS_AT_MS = (300, 900)

#: The window's document. ⛔ `focus()` with no options, which is what scrolls
#: every ancestor frame; the reports are fire-and-forget to this same origin,
#: and each value typed carries its number (`W458`, above).
PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>stand-in editor</title></head>
<body style="margin:0"><textarea id="input" style="width:95%;height:180px"></textarea>
<script>
  var input = document.getElementById('input');
  function say(what) { fetch(what, { cache: 'no-store' }); }
  __TIMERS__
  var sent = 0;
  input.addEventListener('input', function () {
    sent += 1;
    say('/typed?n=' + sent + '&v=' + encodeURIComponent(input.value));
  });
</script></body></html>
"""

TIMER = "setTimeout(function () { input.focus(); say('/focused'); }, %d);"


class StandIn:
    """The running stand-in: its origin, and what its windows have reported."""

    def __init__(self) -> None:
        """Nothing reported yet."""
        self.origin = ""
        self.focused = 0
        self.typed = ""
        self.numbered = 0
        self.lock = threading.Lock()
        self.changed = threading.Condition(self.lock)

    def wait_for(self, done: Callable[[StandIn], bool], timeout: float = 20.0) -> None:
        """Block until a report makes `done(self)` hold, or fail naming what was reported."""
        with self.changed:
            if self.changed.wait_for(lambda: done(self), timeout=timeout):
                return
        raise AssertionError(
            f"the stand-in editor never reached the awaited state: "
            f"focused={self.focused} typed={self.typed!r}"
        )


def _handler(state: StandIn) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - the name is http.server's
            where = urlsplit(self.path)
            if where.path in ("/main", "/test"):
                timers = "\n  ".join(TIMER % at for at in FOCUS_AT_MS)
                self._answer(200, PAGE.replace("__TIMERS__", timers).encode("utf-8"))
                return
            with state.changed:
                if where.path == "/focused":
                    state.focused += 1
                elif where.path == "/typed":
                    _typed(state, parse_qs(where.query))
                state.changed.notify_all()
            self._answer(204, b"")

        def _answer(self, status: int, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args: object) -> None:
            """Say nothing: a check reads the state, not a log."""

    return Handler


def _typed(state: StandIn, query: dict[str, list[str]]) -> None:
    """Keep the value of the highest-numbered report, whatever order they arrived in."""
    number = int(query.get("n", ["0"])[0])
    if number > state.numbered:
        state.numbered = number
        state.typed = query.get("v", [""])[0]


@contextlib.contextmanager
def running() -> Iterator[StandIn]:
    """Serve the stand-in on a free loopback port for the length of the block."""
    state = StandIn()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _handler(state))
    state.origin = f"http://127.0.0.1:{server.server_address[1]}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=20)
