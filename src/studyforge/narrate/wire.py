r"""The wire to the narration service: bytes out, bytes in, and what can go wrong between.

**What it does.** Defines one outbound request (`Sent`), one answer (`Received`),
the transport shape between them, and `over_http`, the only place this framework
opens a socket. It also defines the refusals a service answer can raise:
`ServiceUnavailable`, `ServiceRefused` and the decode error `UnreadableAnswer`.

**How you use it.** `narrate.client` builds a `Sent` and hands it to a transport.
A test hands in a recording transport instead. A reader of an answer's bytes
raises `UnreadableAnswer` for one it cannot read.

**Depends on.** `urllib`, `dataclasses`, `collections.abc` (standard library
only), plus `archive.scrub` for the absence sentence and `narrate.answers` for
the error family. ⛔ **Nothing on the build's side imports this module**,
asserted over `sys.modules` in a fresh interpreter.

## ⛔ THE DECODE ERROR IS THE WIRE'S

⭐ **Reading bytes as JSON is the same act for `/healthz` and for a job**, so the
refusal is one class, and it is defined here. ⚠️ A health answer is not a
manifest, so no arm around one catches another package's error family. ⛔ **Every
arm around a service answer names this module's classes.** ⭐ The JSON readers themselves are
`narrate.client`'s:
the module that decodes an answer is the one that calls the R7 gate.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

from studyforge.archive.scrub import scrub
from studyforge.narrate.answers import NarrationError

JSON_MEDIA_TYPE = "application/json"
AUDIO_ACCEPT = "audio/*"
ENCODING = "utf-8"
HTTP_OK = 200


class ServiceUnavailable(NarrationError):
    """The service is not there. ⭐ A known state, not a crash (R6, R8)."""


class ServiceRefused(NarrationError):
    """The service answered and the answer was a refusal."""


class UnreadableAnswer(NarrationError):
    """The service answered with something this client cannot read."""


@dataclass(frozen=True, slots=True)
class Sent:
    """One outbound request as it leaves the client — ⭐ the acceptance's unit."""

    method: str
    url: str
    body: bytes | None
    accept: str
    timeout: float


@dataclass(frozen=True, slots=True)
class Received:
    """What came back: the status, the media type, and the undecoded bytes."""

    status: int
    media_type: str
    body: bytes


Transport = Callable[[Sent], Received]


def over_http(sent: Sent) -> Received:
    """Perform `sent` with `urllib`. ⛔ The only place this framework opens a socket.

    A refusal returns its status, because a job's status is data; an absent
    service raises `ServiceUnavailable`.
    """
    request = urllib.request.Request(sent.url, data=sent.body, method=sent.method)
    request.add_header("Accept", sent.accept)
    if sent.body is not None:
        request.add_header("Content-Type", JSON_MEDIA_TYPE)
    try:
        with urllib.request.urlopen(request, timeout=sent.timeout) as answer:
            return Received(answer.status, answer.headers.get_content_type(), answer.read())
    except urllib.error.HTTPError as refusal:
        media_type = refusal.headers.get_content_type() if refusal.headers else ""
        return Received(refusal.code, media_type, refusal.read())
    except (urllib.error.URLError, TimeoutError, OSError) as absent:
        raise ServiceUnavailable(_absent(sent.url, type(absent).__name__)) from None


def _absent(url: str, kind: str) -> str:
    """Say the service did not answer, ⛔ naming the failure's type and never it."""
    ending = "A corpus with no narration still reads (R6, R8); nothing was written."
    return scrub(f"the narration service did not answer at {url} ({kind}). {ending}")
