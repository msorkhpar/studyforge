"""A recording narration service, and the disk readings `cli/narrate/`'s tests assert.

⛔ **Every population here is read off the TRANSPORT or the DISK, never off the
run's report.** `SF-17`'s *"0 synthesised"* over 619 stale clips is a report
agreeing with itself; these helpers exist so no test in this package can.

⭐ `speech_ids` derives the expected population from the corpus through the
minter and the builder directly — not through `stage.unit_work` — so a stage
that skipped a unit cannot make the expectation skip it too.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from studyforge.generate.declarations import read_corpus
from studyforge.narrate.client import Received, Sent, ServiceUnavailable
from studyforge.narrate.speakable import parse_clip_name, speakable_of
from studyforge.unit.builder import build_unit

BASE = "http://127.0.0.1:8870"
VOICE = "am_liam"
FMT = "mp3"
HEALTH = ("GET", "/healthz")


class Recording:
    """A transport that records every `Sent` and hands it to `transport`."""

    def __init__(self, transport=None):
        self.sent: list[Sent] = []
        self._transport = transport

    def __call__(self, sent: Sent) -> Received:
        self.sent.append(sent)
        return self.answer(sent)

    def answer(self, sent: Sent) -> Received:
        return self._transport(sent)

    @property
    def requests(self) -> list[tuple[str, str]]:
        """`(method, path)` of every request, in order."""
        return [(sent.method, urlsplit(sent.url).path) for sent in self.sent]

    @property
    def submitted(self) -> list[str]:
        """The id of every segment any job asked the service to synthesise."""
        asked: list[str] = []
        for sent in self.sent:
            if sent.body is not None:
                payload = json.loads(sent.body.decode("utf-8"))
                asked.extend(segment["id"] for segment in payload.get("segments", ()))
        return asked


def audio_for(speech_id: str) -> bytes:
    """The fake service's bytes for one segment — ⭐ distinct per id, so a swap shows."""
    return b"ID3" + speech_id.encode("utf-8")


class FakeService(Recording):
    """Answers `/healthz`, `/v1/jobs` and `/v1/artifacts/<id>` as `narrate-service` does."""

    def __init__(self, *, reachable=True, provides=3, chunk_chars=1800, jobs=None, failing=()):
        super().__init__()
        self.reachable = reachable
        self.provides = provides
        self.chunk_chars = chunk_chars
        self.jobs = jobs
        self.failing = frozenset(failing)
        self._audio: dict[str, bytes] = {}

    def answer(self, sent: Sent) -> Received:
        if not self.reachable:
            raise ServiceUnavailable("the narration service did not answer (ConnectionRefused)")
        path = urlsplit(sent.url).path
        if path == "/healthz":
            health = {"status": "ok", "provides": self.provides, "chunk_chars": self.chunk_chars}
            return as_json(health)
        if path == "/v1/jobs":
            if self.jobs is not None:
                if self.jobs == 0:
                    raise ServiceUnavailable("the narration service went away (ConnectionReset)")
                self.jobs -= 1
            return as_json(self._manifest(json.loads(sent.body.decode("utf-8"))))
        if path.startswith("/v1/artifacts/"):
            return Received(200, "audio/mpeg", self._audio[path.rsplit("/", 1)[1]])
        return Received(404, "application/json", b"{}")

    def _manifest(self, payload: dict) -> dict:
        entries = []
        for segment in payload["segments"]:
            speech_id = segment["id"]
            if speech_id in self.failing:
                entries.append({"id": speech_id, "status": "failed", "reason": "not_synthesisable"})
                continue
            key = hashlib.sha256(f"{speech_id}\0{segment['text']}".encode()).hexdigest()
            self._audio[key] = audio_for(speech_id)
            entries.append(
                {
                    "id": speech_id,
                    "status": "synthesised",
                    "artifact_id": key,
                    "format": payload.get("format", FMT),
                    "engine": "fake",
                    "engine_model": "fake",
                }
            )
        voice, fmt = payload.get("voice"), payload.get("format")
        return {"segments": entries, "voice": voice, "format": fmt, "provides": self.provides}


def as_json(payload: object, status: int = 200) -> Received:
    return Received(status, "application/json", json.dumps(payload).encode("utf-8"))


def speech_ids(root: Path) -> list[str]:
    """Every speech unit the corpus at `root` declares, sorted — ⛔ not via the stage."""
    corpus = read_corpus(root)
    return sorted(
        unit.id
        for source in corpus.units
        for unit in speakable_of(
            build_unit(source.directory, declared_practices=source.declared_practices)
        ).units
    )


def files(root: Path) -> dict[str, tuple[bytes, int]]:
    """Every file under `root`: its bytes and its modification time, by relative path."""
    return {
        path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def new_clips(root: Path, before: dict, suffix: str = FMT) -> list[Path]:
    """⛔ THE DISK READING: every `*.<suffix>` file under `root` that was not there before."""
    return sorted(
        path
        for path in root.rglob(f"*.{suffix}")
        if path.is_file() and path.relative_to(root).as_posix() not in before
    )


def clip_ids(clips: list[Path]) -> list[str]:
    """The speech id each clip file's own NAME files it under, sorted."""
    return sorted(parse_clip_name(clip.stem)[0] for clip in clips)
