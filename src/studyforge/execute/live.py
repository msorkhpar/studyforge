r"""A live run: one process in the live runner, started with the reader's key in ITS environment.

**What it does.** Speaks the live runner's service (`assets/liverun.pl`) from the serving
process: `LiveLauncher` sends one `live` request, whose key is a framed FIELD, and streams the
run's output as a process would; `start` makes the run's handle; `valid_key` is the one shape a
key may have; `redactions` spells the forms a stream must never carry.

**How you use it.**

    handle = start(service, ("python3", "examples/a/run.py"), "sk-test-...", cwd=".")
    for line in handle.lines(): ...

**Depends on.** `remote` for the wire's frames and `handle` for the run. ⛔ No process and no
socket but the one request: a live run is a message, and the answer is the run's bytes.

## ⛔ WHERE THE KEY GOES, AND WHERE IT NEVER DOES

⭐ **One reader of the request's key (`routes.live`) and one place it is put on the wire
(`LiveLauncher.spawn`)**; the live runner sets it, in the child only, as the corpus's declared
variable. ⛔ It is never an argument (an argv holds the corpus's own command), never a file, never a
log line and never part of an error text: this module's refusals name the shape, not the value.
⭐ **The graded runner has no `live` verb** (`assets/runservice.pl` is unchanged), so it cannot
accept a key even if one reached it.

## ⭐ THE KEY'S SHAPE IS CHECKED, AND THEN IT IS ONLY DATA

Letters, digits, `-` and `_`, 8 to 256 of them. A newline, NUL, space or shell metacharacter is
refused before anything is built, with a sentence that does not echo the value. ⛔ The live runner
`exec`s an argv list with no shell, so a key could never be parsed as a command either way.
"""

from __future__ import annotations

import base64
import re
import urllib.parse
from collections.abc import Sequence

from studyforge.execute.errors import RunRefused
from studyforge.execute.handle import RunHandle
from studyforge.execute.output import LineGate
from studyforge.execute.remote import (
    CONNECT_TIMEOUT,
    RemoteLauncher,
    RemoteProcess,
    Service,
    _connect,
    fresh_token,
    request,
)

#: The port the live runner listens on, inside the compose network only.
LIVE_PORT = 7124

#: What a key may be. ⛔ Anchored `\A…\Z`: `$` would admit a trailing newline.
KEY = re.compile(r"\A[A-Za-z0-9_-]{8,256}\Z")

#: The longest a live run may take, and the work directory it runs in.
LIVE_TIMEOUT = 300.0
WORKDIR_IN_LIVE = "/work"

#: What replaces a key found in output.
MARKER = "[redacted]"

#: The refusal's sentence. ⛔ It carries no part of the value.
BAD_KEY = "the key is not in the form a live run accepts: 8 to 256 letters, digits, '-' and '_'"


def valid_key(value: object) -> bool:
    """Whether `value` is a key shape a live run accepts."""
    return isinstance(value, str) and KEY.match(value) is not None


def redactions(key: str) -> tuple[str, ...]:
    """Return the forms of `key` a stream must not carry: raw, URL-encoded, base64 at each offset.

    ⭐ The whole base64 encoding of the key (with and without its padding) is a form of its own, so
    a key encoded alone is replaced in full. ⚠️ A key inside a longer encoded text can only be found
    by the characters no neighbour changes, so a character or two at either end of such a run may
    remain: the live runner's net and this one share that limit, and it is stated.

    ⭐ The base64 forms are the encodings of the key at the three alignments it can sit in a longer
    text, trimmed to the characters that do not depend on a neighbour, so a key inside a
    credential header or a basic-auth string is still found.
    """
    forms = {key, urllib.parse.quote(key, safe=""), urllib.parse.quote_plus(key)}
    data = key.encode("ascii")
    whole = base64.b64encode(data).decode("ascii")
    for spelling in (whole, whole.rstrip("=")):
        forms.add(spelling)
        forms.add(spelling.replace("+", "-").replace("/", "_"))
    for pad in range(3):
        encoded = base64.b64encode(b"\x00" * pad + data).decode("ascii")
        # Drop the characters touched by the padding bytes and by a following neighbour.
        head = {0: 0, 1: 2, 2: 3}[pad]
        tail = (len(data) + pad) % 3
        body = encoded.rstrip("=")
        body = body[head : len(body) - (1 if tail else 0)] if tail else body[head:]
        if len(body) >= 8:
            forms.add(body)
            forms.add(body.replace("+", "-").replace("/", "_"))
    return tuple(sorted(forms, key=len, reverse=True))


class LiveLauncher(RemoteLauncher):
    """Start the argv in the live runner: the key is one framed field, never part of the argv."""

    def __init__(self, service: Service, cwd: str, key: str) -> None:
        """Hold the key for this one run; refuse a value that is not a key's shape."""
        if not valid_key(key):
            raise RunRefused(BAD_KEY)
        super().__init__(service, cwd)
        self._key = key

    def spawn(self, argv: Sequence[str]) -> RemoteProcess:
        """Send one `live` request: token, directory, key, then the argv, verbatim."""
        payload = request("live", self.marker, self.cwd, self._key, *argv)
        connection = _connect(self.service)
        connection.settimeout(CONNECT_TIMEOUT)
        connection.sendall(payload)
        connection.settimeout(None)
        return RemoteProcess(connection)

    def __repr__(self) -> str:
        """Say what this is, never what it holds."""
        return "LiveLauncher(<run>)"


def start(
    service: Service,
    argv: Sequence[str],
    key: str,
    *,
    cwd: str = ".",
    timeout: float = LIVE_TIMEOUT,
    grace: float = 2.0,
) -> RunHandle:
    """Return the live run's handle; the first command is started before this returns."""
    launcher = LiveLauncher(service, cwd, key)
    return RunHandle(
        [list(argv)],
        launcher,
        LineGate((WORKDIR_IN_LIVE,)),
        mode="live",
        timeout=timeout,
        grace=grace,
    )


def new_token() -> str:
    """Return a fresh run token (kept here so a caller names no private of `remote`)."""
    return fresh_token()
