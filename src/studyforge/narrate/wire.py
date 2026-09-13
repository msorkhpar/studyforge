r"""The wire to the narration service: bytes out, bytes in, and reading what came back.

**What it does.** Defines one outbound request (`Sent`), one answer (`Received`),
the transport shape between them, and `over_http`, the only place this framework
opens a socket. It also reads an answer's body as a JSON object and refuses one
it cannot read, with `UnreadableAnswer`.

**How you use it.** `narrate.client` builds a `Sent` and hands it to a transport.
A test hands in a recording transport instead. `decoded(answer, where)`,
`object_of` and `field_of` read a body and raise `UnreadableAnswer`.

**Depends on.** `json`, `urllib`, `dataclasses`, `collections.abc` (standard
library only), plus `archive.scrub` for the absence sentence, `describe`, and
`narrate.answers` for the error family. ⛔ **Nothing on the build's side imports
this module**, asserted over `sys.modules` in a fresh interpreter (`W223`).

## ⛔ THE DECODE ERROR IS THE WIRE'S (`W212/3`)

⭐ **Reading bytes as JSON is the same act for `/healthz` and for a job**, so the
refusal is one class, raised here. ⚠️ `probe` used to catch a `ManifestError`
around a health answer, which is not a manifest, and the name was another
package's error family. ⛔ **Every arm around a service answer now names this
module's classes.**
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

from studyforge.archive.scrub import scrub
from studyforge.describe import describe
from studyforge.narrate.answers import NarrationError

ENCODING = "utf-8"
JSON_MEDIA_TYPE = "application/json"
AUDIO_ACCEPT = "audio/*"
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


def decoded(answer: Received, where: str) -> dict[str, object]:
    """Return `answer`'s body as a decoded JSON object, or raise `UnreadableAnswer`."""
    try:
        payload = json.loads(answer.body.decode(ENCODING))
    except ValueError, UnicodeDecodeError:
        raise UnreadableAnswer(f"{where} answered with a body that is not JSON") from None
    return object_of(payload, where)


def object_of(value: object, where: str) -> dict[str, object]:
    """Return `value` as a decoded JSON object, or raise `UnreadableAnswer`."""
    if not isinstance(value, dict):
        raise UnreadableAnswer(f"{where} answered with {describe(value)}, not an object")
    return value


def field_of(payload: dict[str, object], what: str, where: str) -> object:
    """Return the `what` key of a decoded object, or raise `UnreadableAnswer`."""
    if what not in payload:
        raise UnreadableAnswer(f"{where} answered without a '{what}' field")
    return payload[what]
