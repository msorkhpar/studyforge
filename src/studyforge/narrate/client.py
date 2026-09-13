r"""The framework's client for the narration service, and the R7 gate in front of it.

**What it does.** Submits speech units to the narration service as one job,
fetches the artifacts the manifest names, and returns them unplaced. ⛔ Every
segment passes the gate **before the first request is built**, so a leak stops
the run instead of being narrated aloud into a file nobody can grep for.

**How you use it.** `NarrateClient(base_url).narrate(units)` returns a
`Narration`; `answers.place(narration, into)` writes it, `into` being the
directory the caller got from `corpus.placement`. `probe()` says whether the
service is there and never raises for absence: a corpus with no narration reads
fine (R6, R8).

**Depends on.** `json`, `re` (standard library), `archive.scrub` for the gate,
`narrate.speakable` for the records and the one clip minter, `narrate.wire` for
the request, the answer and reading it, and `narrate.answers` for the values.
⛔ **Not on `corpus.placement`** — asserted, see R4.

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

## ⛔ THE SERVICE'S OWN URL IS NOT FOLLOWED, AND ITS MODEL IS READ, NOT GUESSED

⛔ A manifest entry's `url` is ignored: the path is rebuilt from `artifact_id`,
checked against `ARTIFACT_ID`, against the configured base, so the service cannot
redirect a fetch elsewhere. ⭐ **`probe` reads `engine_model` off `/healthz`**
(`W223`): the service's cache key is the service's, and this client reports what
the deployment says rather than composing a key of its own.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence

from studyforge.archive.scrub import assert_clean, scrub
from studyforge.describe import describe
from studyforge.narrate.answers import Artifact, Health, Narration
from studyforge.narrate.speakable.naming import clip_name
from studyforge.narrate.speakable.records import SpeechUnit
from studyforge.narrate.wire import (
    AUDIO_ACCEPT,
    ENCODING,
    HTTP_OK,
    JSON_MEDIA_TYPE,
    Received,
    Sent,
    ServiceRefused,
    ServiceUnavailable,
    Transport,
    UnreadableAnswer,
    decoded,
    field_of,
    object_of,
    over_http,
)

HEALTH_PATH = "/healthz"
JOBS_PATH = "/v1/jobs"
ARTIFACT_PATH = "/v1/artifacts/"

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
        """Report whether the service is there. ⛔ Never raises for its absence (R6, R8).

        ⛔ `chunk_chars` and `engine_model` are both in the service's content
        address and both deployment settings (`NS-02`, `W223`), so an answer
        without either is unreadable rather than a guess.
        """
        try:
            answer = self._send("GET", HEALTH_PATH, accept=JSON_MEDIA_TYPE)
            if answer.status != HTTP_OK:
                return Health(False, scrub(f"{HEALTH_PATH} answered {answer.status}"))
            payload = decoded(answer, HEALTH_PATH)
            chunk_chars = field_of(payload, "chunk_chars", HEALTH_PATH)
            engine_model = field_of(payload, "engine_model", HEALTH_PATH)
        except ServiceUnavailable as absent:
            return Health(reachable=False, detail=str(absent))
        except UnreadableAnswer as unreadable:
            return Health(reachable=False, detail=scrub(str(unreadable)))
        return Health(
            reachable=True,
            detail=scrub(f"the narration service answered at {self._base}{HEALTH_PATH}"),
            provides=payload.get("provides"),
            chunk_chars=chunk_chars if isinstance(chunk_chars, int) else None,
            engine_model=engine_model if isinstance(engine_model, str) else None,
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
        return self._collect(units, decoded(answer, JOBS_PATH))

    def _collect(self, units: Sequence[SpeechUnit], manifest: dict[str, object]) -> Narration:
        """Fetch every produced segment and sort the rest into failed and retryable."""
        entries = field_of(manifest, "segments", JOBS_PATH)
        if not isinstance(entries, list):
            raise UnreadableAnswer(f"{JOBS_PATH} answered with segments that are not a list")
        by_id = {unit.id: unit for unit in units}
        artifacts: list[Artifact] = []
        failed: list[tuple[str, str]] = []
        retryable: list[str] = []
        for entry in (object_of(raw, JOBS_PATH) for raw in entries):
            speech_id = str(field_of(entry, "id", JOBS_PATH))
            status = str(field_of(entry, "status", JOBS_PATH))
            if speech_id not in by_id:
                raise UnreadableAnswer(f"{JOBS_PATH} answered about a segment nobody submitted")
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
        artifact_id = str(field_of(entry, "artifact_id", JOBS_PATH))
        fmt = str(field_of(entry, "format", JOBS_PATH))
        if not ARTIFACT_ID.match(artifact_id):
            raise UnreadableAnswer(f"the artifact id for {unit.id} is not the published shape")
        if not FORMAT_NAME.match(fmt):
            raise UnreadableAnswer(f"the format for {unit.id} is not a usable filename suffix")
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
