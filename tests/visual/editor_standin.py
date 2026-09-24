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
polls either.

**Depends on.** `http.server`, `threading`, `urllib.parse`, `time`,
`contextlib`. ⛔ Nothing under `src/`: this is a stand-in for somebody else's
program, and the page under test must not be able to tell it from one.

## ⛔ Why ANOTHER origin, and not `served.WINDOW_URLS`

⚠️ `about:blank` has no script of its own, and the defect is the framed
document's OWN script taking focus. ⭐ A second loopback port is the same site
and a different origin — exactly the relation between a study page and the
editor on a reader's machine — so the browser treats its `focus()` the way it
treats the workbench's.
"""

from __future__ import annotations

import contextlib
import threading
import time
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

#: How many times the stand-in focuses its input as it starts, and when.
#: ⭐ Two, after the document has loaded — the workbench's two calls.
FOCUS_AT_MS = (300, 900)

#: The window's document. ⛔ `focus()` with no options, which is what scrolls
#: every ancestor frame; the reports are fire-and-forget to this same origin.
PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>stand-in editor</title></head>
<body style="margin:0"><textarea id="input" style="width:95%;height:180px"></textarea>
<script>
  var input = document.getElementById('input');
  function say(what) { fetch(what, { cache: 'no-store' }); }
  __TIMERS__
  input.addEventListener('input', function () {
    say('/typed?v=' + encodeURIComponent(input.value));
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
        self.lock = threading.Lock()

    def wait_for(self, done: Callable[[StandIn], bool], timeout: float = 20.0) -> None:
        """Poll until `done(self)` holds, or fail naming what was reported."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self.lock:
                if done(self):
                    return
            time.sleep(0.05)
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
            with state.lock:
                if where.path == "/focused":
                    state.focused += 1
                elif where.path == "/typed":
                    state.typed = parse_qs(where.query).get("v", [""])[0]
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
