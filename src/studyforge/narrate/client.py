r"""The framework's client for the narration service, and the R7 gate in front of it.

**What it does.** Submits speech units to the narration service as one job,
fetches the artifacts the manifest names, and hands them to a directory the
placement policy chose. ⛔ Every segment passes the gate **before the first
request is built**, so a leak stops the run instead of being narrated aloud into
a file nobody can grep for.

**How you use it.** `NarrateClient(base_url).narrate(units)` returns a
`Narration`; `place(narration, into)` writes it, `into` being the directory the
caller got from `corpus.placement`. `probe()` says whether the service is there
and never raises for absence: a corpus with no narration reads fine (R6, R8).

**Depends on.** `json`, `re`, `urllib`, `pathlib`, `dataclasses` — standard library
only — plus `archive.scrub` for the gate and `narrate.speakable` for the records
and the one clip minter. ⛔ **Not on `corpus.placement`** — asserted, see R4.

## ⛔ THE POPULATION IS THE REQUESTS, AND EXACTLY ONE SEAM PRODUCES IT

⭐ **Every byte this module sends leaves through `NarrateClient._send`, which builds
a `Sent` and hands it to the transport.** ⛔ That is what makes *"a leaking segment
stops the run before any request is made"* an assertion about **what was sent**, not
what was written or which exception came back: substitute a recording transport, and
the acceptance is that its list is **empty**.

⚠️ **A gate that only ran in `narrate()` would be a discipline, not a property**, so
the seam gates too: `_send` runs `assert_clean` over the decoded payload and the URL,
and the body is **encoded after that call and nowhere else**. ⭐ The inner layer is
news, not redundancy (SF-08's argument): the per-segment gate names the speech id and
is actionable; the seam gate cannot, so a match there means an upstream stage failed.

## ⛔ `scrub` THEN `assert_clean`, AND THEY READ DIFFERENT WORDS

⭐ **The order is the archive writer's and so is the division** (SF-08 *Decisions* 1):
`scrub` rewrites text **this framework wrote** — the `where` label and every message
raised here — and `assert_clean` **refuses** text a source wrote, because rewriting a
record corrupts it. ⛔ Scrubbing a segment then asserting it would swap the leak for a
placeholder and pass: a gate that cannot fire. Never done here.

## ⛔ R4, AND THE SERVICE'S OWN URL IS NOT FOLLOWED EITHER

⛔ `place` takes its directory as an argument: no default, no `"audio"`, no join
against a profile, no import of `corpus.placement` — the caller asks the policy and
passes the answer in. ⛔ And a manifest entry's `url` is ignored: the path is rebuilt
from `artifact_id`, checked against `ARTIFACT_ID`, against the configured base, so
the service cannot redirect a fetch elsewhere.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.scrub import assert_clean, scrub
from studyforge.describe import describe
from studyforge.narrate.speakable.naming import clip_name
from studyforge.narrate.speakable.records import SpeechUnit

ENCODING = "utf-8"
JSON_MEDIA_TYPE = "application/json"
AUDIO_ACCEPT = "audio/*"
HEALTH_PATH = "/healthz"
JOBS_PATH = "/v1/jobs"
ARTIFACT_PATH = "/v1/artifacts/"
HTTP_OK = 200

#: ⚠️ Ten minutes: the service's default is sized for the slow CPU profile.
DEFAULT_TIMEOUT_SECONDS = 600.0

#: Produced an artifact. ⛔ `cached` counts: the engine did not run, and that is
#: the cache working rather than a failure.
PRODUCED = ("synthesised", "cached")

#: Worth resubmitting unchanged — the job stopped early and what finished is
#: already cached, so the second attempt pays only for the remainder.
RETRYABLE = ("skipped",)

#: What an artifact id may be, ⛔ checked before it is put in a URL.
ARTIFACT_ID = re.compile(r"\A[0-9a-f]{16,128}\Z")

#: What a clip's suffix may be, so a format from the wire cannot become a path.
FORMAT_NAME = re.compile(r"\A[a-z0-9]{1,8}\Z")

#: Written while an artifact is being placed, then renamed over the target.
PARTIAL_SUFFIX = ".partial"


class NarrationError(Exception):
    """Synthesis did not happen.

    ⛔ **`PersonalDataLeak` is deliberately outside this family and is never
    translated into it** (Ruling 58): a caller catching this reports and carries
    on, and an R7 refusal must stop the run. ⭐ Two exceptions travel through
    unconverted, deliberately — `PersonalDataLeak` and `SpeakableError`.
    """


class ServiceUnavailable(NarrationError):
    """The service is not there. ⭐ A known state, not a crash (R6, R8)."""


class ServiceRefused(NarrationError):
    """The service answered and the answer was a refusal."""


class ManifestError(NarrationError):
    """The service answered with something this client cannot read as a manifest."""


@dataclass(frozen=True, slots=True)
class Sent:
    """One outbound request as it leaves this module — ⭐ the acceptance's unit."""

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


@dataclass(frozen=True, slots=True)
class Health:
    """Whether the service is there, and what it says about itself.

    ⛔ `reachable=False` is an answer, not an error: `detail` is a sentence a
    build prints before carrying on without narration (R6, R8).
    """

    reachable: bool
    detail: str
    provides: int | None = None
    #: ⛔ In the content address AND a deployment setting: read it here, never
    #: from a constant.
    chunk_chars: int | None = None


@dataclass(frozen=True, slots=True)
class Artifact:
    """One placeable clip: what it is called, and what made it.

    `filename` comes from the one minter, `clip_name`, which takes the whole unit
    so an id cannot be paired with words that are not its own. ⚠️ `engine` and
    `engine_model` are *what made this file* — on a cache hit, the FIRST
    synthesis's, not necessarily the one deployed.
    """

    speech_id: str
    filename: str
    media_type: str
    audio: bytes
    engine: str
    engine_model: str
    status: str


@dataclass(frozen=True, slots=True)
class Narration:
    """One job's whole outcome, in memory and not yet on disk.

    ⭐ **Nothing is written until `place` is called** — *"no partial state"* as a
    property of the shape rather than a promise about error handling.
    """

    artifacts: tuple[Artifact, ...]
    failed: tuple[tuple[str, str], ...]
    retryable: tuple[str, ...]
    voice: str
    fmt: str
    provides: int | None


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


def _decoded(answer: Received, where: str) -> dict[str, object]:
    """Return `answer`'s body as a decoded JSON object, or raise `ManifestError`."""
    try:
        payload = json.loads(answer.body.decode(ENCODING))
    except ValueError, UnicodeDecodeError:
        raise ManifestError(f"{where} answered with a body that is not JSON") from None
    return _object(payload, where)


def _object(value: object, where: str) -> dict[str, object]:
    """Return `value` as a decoded JSON object, or raise `ManifestError`."""
    if not isinstance(value, dict):
        raise ManifestError(f"{where} answered with {describe(value)}, not an object")
    return value


def _field(payload: dict[str, object], key: str, where: str) -> object:
    """Return one key of a decoded object, or raise `ManifestError`."""
    if key not in payload:
        raise ManifestError(f"{where} answered without a '{key}' field")
    return payload[key]


class NarrateClient:
    """A thin batch client for the narration service. ⛔ It places nothing itself.

    Standard library only, one transport seam, and no knowledge of where a study
    site keeps its audio (R4).
    """

    def __init__(
        self,
        base_url: str,
        *,
        voice: str | None = None,
        fmt: str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        transport: Transport = over_http,
    ) -> None:
        """Configure where the service is, what to ask it for, and how to reach it."""
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError(f"a base URL is a non-empty str, got {describe(base_url)}")
        self._base = base_url.strip().rstrip("/")
        self._voice = voice
        self._fmt = fmt
        self._timeout = float(timeout)
        self._transport = transport

    def _send(self, method: str, path: str, *, payload: object = None, accept: str) -> Received:
        """Gate, encode and hand ONE request to the transport. ⛔ The only exit.

        `assert_clean` runs over the decoded payload and the URL, and the body is
        encoded **after** it — so nothing reaches a transport unpassed.
        """
        url = f"{self._base}{path}"
        where = scrub(f"{method} {path}")
        assert_clean({"url": url, "payload": payload}, where)
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode(ENCODING)
        return self._transport(Sent(method, url, body, accept, self._timeout))

    @staticmethod
    def gate(units: Sequence[SpeechUnit]) -> None:
        """Refuse the whole batch if any unit carries personal data (R7).

        ⛔ Makes no request and builds no body, and runs over **every** unit before
        anything is submitted: one leaking segment in three thousand stops the run
        rather than becoming the clip nobody can search for.
        """
        for index, unit in enumerate(units):
            if not isinstance(unit, SpeechUnit):
                raise TypeError(f"segment {index} is {describe(unit)}, not a SpeechUnit")
            assert_clean(unit.id, f"the id of segment {index}")
            assert_clean(unit.speak, f"the speech of {unit.id}")

    def probe(self) -> Health:
        """Report whether the service is there. ⛔ Never raises for its absence (R6, R8)."""
        try:
            answer = self._send("GET", HEALTH_PATH, accept=JSON_MEDIA_TYPE)
            if answer.status != HTTP_OK:
                return Health(False, scrub(f"{HEALTH_PATH} answered {answer.status}"))
            payload = _decoded(answer, HEALTH_PATH)
            chunk_chars = _field(payload, "chunk_chars", HEALTH_PATH)
        except ServiceUnavailable as absent:
            return Health(reachable=False, detail=str(absent))
        except ManifestError as unreadable:
            return Health(reachable=False, detail=scrub(str(unreadable)))
        return Health(
            reachable=True,
            detail=scrub(f"the narration service answered at {self._base}{HEALTH_PATH}"),
            provides=payload.get("provides"),
            chunk_chars=chunk_chars if isinstance(chunk_chars, int) else None,
        )

    def narrate(self, units: Sequence[SpeechUnit]) -> Narration:
        """Synthesise `units` as one job and return their artifacts, unplaced.

        ⛔ The gate runs first and over everything; only then is a body built.
        Every artifact is held in memory and nothing touches a tree, so a service
        that goes away part-way leaves no partial state to clean up.
        """
        self.gate(units)
        payload: dict[str, object] = {
            "segments": [{"id": unit.id, "text": unit.speak} for unit in units]
        }
        if self._voice is not None:
            payload["voice"] = self._voice
        if self._fmt is not None:
            payload["format"] = self._fmt
        answer = self._send("POST", JOBS_PATH, payload=payload, accept=JSON_MEDIA_TYPE)
        if answer.status != HTTP_OK:
            raise ServiceRefused(f"{JOBS_PATH} answered {answer.status}, not {HTTP_OK}")
        return self._collect(units, _decoded(answer, JOBS_PATH))

    def _collect(self, units: Sequence[SpeechUnit], manifest: dict[str, object]) -> Narration:
        """Fetch every produced segment and sort the rest into failed and retryable."""
        entries = _field(manifest, "segments", JOBS_PATH)
        if not isinstance(entries, list):
            raise ManifestError(f"{JOBS_PATH} answered with segments that are not a list")
        by_id = {unit.id: unit for unit in units}
        artifacts: list[Artifact] = []
        failed: list[tuple[str, str]] = []
        retryable: list[str] = []
        for entry in (_object(raw, JOBS_PATH) for raw in entries):
            speech_id = str(_field(entry, "id", JOBS_PATH))
            status = str(_field(entry, "status", JOBS_PATH))
            if speech_id not in by_id:
                raise ManifestError(f"{JOBS_PATH} answered about a segment nobody submitted")
            if status in PRODUCED:
                artifacts.append(self._artifact(by_id[speech_id], entry))
            elif status in RETRYABLE:
                retryable.append(speech_id)
            else:
                failed.append((speech_id, str(entry.get("reason", status))))
        return Narration(
            artifacts=tuple(artifacts),
            failed=tuple(failed),
            retryable=tuple(retryable),
            voice=str(manifest.get("voice", "")),
            fmt=str(manifest.get("format", "")),
            provides=manifest.get("provides"),
        )

    def _artifact(self, unit: SpeechUnit, entry: dict[str, object]) -> Artifact:
        """Fetch one produced segment's audio and name it with the one minter."""
        artifact_id = str(_field(entry, "artifact_id", JOBS_PATH))
        fmt = str(_field(entry, "format", JOBS_PATH))
        if not ARTIFACT_ID.match(artifact_id):
            raise ManifestError(f"the artifact id for {unit.id} is not the published shape")
        if not FORMAT_NAME.match(fmt):
            raise ManifestError(f"the format for {unit.id} is not a usable filename suffix")
        answer = self._send("GET", f"{ARTIFACT_PATH}{artifact_id}", accept=AUDIO_ACCEPT)
        if answer.status != HTTP_OK:
            raise ServiceRefused(f"fetching {unit.id}'s artifact answered {answer.status}")
        return Artifact(
            speech_id=unit.id,
            filename=f"{clip_name(unit)}.{fmt}",
            media_type=answer.media_type,
            audio=answer.body,
            engine=str(entry.get("engine", "")),
            engine_model=str(entry.get("engine_model", "")),
            status=str(entry["status"]),
        )


def place(narration: Narration, into: Path) -> tuple[Path, ...]:
    """Write every artifact into `into` — ⛔ the directory the POLICY named.

    ⭐ `into` is an argument and never a default: this module holds no opinion about
    where a study site keeps its audio (R4). Each file lands in a temporary sibling
    and is renamed over its target, so an interrupted run leaves no truncated clip
    that looks finished — `NS-01`'s property, at this end.
    """
    destination = Path(into)
    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for artifact in narration.artifacts:
        target = destination / artifact.filename
        partial = target.with_name(f".{target.name}{PARTIAL_SUFFIX}")
        partial.write_bytes(artifact.audio)
        partial.replace(target)
        written.append(target)
    return tuple(written)
