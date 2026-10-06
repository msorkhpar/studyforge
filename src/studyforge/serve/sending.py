r"""A file's span on the wire: opened before the headers, held to its version, sent by the kernel.

**What it does.** `opened(response)` opens a file answer's file before a header is
written and says whether the open handle is still the version the route judged.
`send_span(connection, handle, first, length)` sends the inclusive span with
`socket.sendfile` — the kernel copies, and no Python thread holds the interpreter
while it does — and returns how many bytes it could not send.

**How you use it.**

    handle, moved = opened(response)            # before `send_response`
    if moved: ... answer `MOVED` instead
    short = send_span(connection, handle, first, response.length)

**Depends on.** `os`, `socket`, `serve.response` and `serve.versions`.

⛔ **A file whose open handle names another version is not sent**: the route judged one
version's bytes (`serve.versions`), and the bytes on the wire are those or none. A file that
moved, or vanished, between the route and the wire is answered `MOVED` — headers are not
yet out, so the client is told plainly rather than handed a short body.

⚠️ `socket.sendfile` falls back to reads and writes where the platform has no
`sendfile`, so the span is sent either way; a span cut short — the file shrank, the client
hung up — is reported, and `serve.app` closes the connection, the only honest signal left.
"""

from __future__ import annotations

import os
import socket
from typing import BinaryIO

from studyforge.serve.response import Response
from studyforge.serve.versions import version_of

#: Status and message for a file that moved between its judgement and the wire.
MOVED_STATUS = 503
MOVED = "the file changed while it was being answered; ask again"


def opened(response: Response) -> tuple[BinaryIO | None, bool]:
    """Return the open file of a file answer and whether it moved; `(None, False)` for none."""
    if response.file is None or response.span is None:
        return None, False
    try:
        handle = response.file.open("rb")
    except OSError:
        return None, True
    try:
        moved = response.version is not None and (
            version_of(os.fstat(handle.fileno())) != response.version
        )
    except OSError:
        moved = True
    if moved:
        handle.close()
        return None, True
    return handle, False


def send_span(connection: socket.socket, handle: BinaryIO, first: int, length: int) -> int:
    """Send `length` bytes of `handle` from `first`; return how many could not be sent."""
    try:
        sent = connection.sendfile(handle, first, length)
    except OSError:
        return length
    return length - sent
