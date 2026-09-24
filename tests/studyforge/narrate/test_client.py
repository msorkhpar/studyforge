"""The framework's narration client (R7, R4, R6, R8).

⛔ **The acceptance clause this file exists for is asserted over the REQUESTS,
not over the output and not over the exception.** `Recorder` collects every
`Sent` the client hands a transport, and the leak tests assert `recorder.sent ==
[]`. ⭐ Each of those has a **positive control** immediately beside it, because
an empty list is also what a recorder nobody wired up returns.

⛔ **A second, wider instrument sits under the first**: `socket.socket` itself is
replaced, so the population becomes *every socket this process would open* and
not merely *every request the seam produced*. Its own positive control is
`test_the_socket_guard_fires_on_a_clean_run` — without that, a guard that could
never fire would prove the same nothing.

⭐ Placing clips is `answers.place` and is tested in `test_answers.py`; reading
an answer's bytes is the wire's and is tested in `test_wire.py`.

⚠️ **The home-path and token material below is assembled at run time**, the same
trick `tests/studyforge/archive/test_scrub.py` uses and for the same reason: this
file is swept by the repository hygiene check like every other tracked file.
⛔ Nothing here came from any real machine, account or person.
"""

import ast
import contextlib
import inspect
import json
import socket
from pathlib import Path

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.narrate import client as client_module
from studyforge.narrate import wire
from studyforge.narrate.client import ARTIFACT_PATH, HEALTH_PATH, JOBS_PATH, NarrateClient
from studyforge.narrate.speakable.records import SpeechUnit
from studyforge.narrate.wire import (
    Received,
    Sent,
    ServiceRefused,
    ServiceUnavailable,
    UnreadableAnswer,
    over_http,
)
from tests.support import imports_module

BASE = "http://127.0.0.1:8870"
SOURCE = Path(inspect.getfile(client_module))

# ⛔ Assembled, never written as a literal — see the module docstring.
HOME = "/" + "home/jane"
BEARER = "Bearer " + "eyJhbGciOiJIUzI1NiJ9"
HOSTNAME = "somebox" + ".local"
EMAIL = "jane.doe@example.invalid"
LEAKS = (HOME, BEARER, HOSTNAME, EMAIL)

ADDRESS_A = "a" * 64
ADDRESS_B = "b" * 64
AUDIO = b"ID3\x04\x00\x00\x00\x00\x00\x00mp3 bytes"

#: What `/healthz` answers here: every field the probe requires.
HEALTHY = {"status": "ok", "provides": 2, "chunk_chars": 1800, "engine_model": "kokoro"}


def unit(identifier: str, said: str) -> SpeechUnit:
    return SpeechUnit(
        id=identifier, speak=said, section="s", block_path=(0,), sub_index=None, kind="paragraph"
    )


class Recorder:
    """A transport that records what it was handed and answers from a script."""

    def __init__(self, *answers):
        self.sent: list[Sent] = []
        self._answers = list(answers)

    def __call__(self, sent: Sent) -> Received:
        self.sent.append(sent)
        if not self._answers:
            raise AssertionError("the recorder was asked for an answer it does not have")
        answer = self._answers.pop(0)
        if isinstance(answer, BaseException):
            raise answer
        return answer


def as_json(payload: object, status: int = 200) -> Received:
    return Received(status, "application/json", json.dumps(payload).encode("utf-8"))


def as_audio(data: bytes = AUDIO) -> Received:
    return Received(200, "audio/mpeg", data)


def entry(identifier: str, address: str, status: str = "synthesised") -> dict:
    return {
        "id": identifier,
        "status": status,
        "artifact_id": address,
        "url": f"{ARTIFACT_PATH}{address}",
        "format": "mp3",
        "media_type": "audio/mpeg",
        "voice": "am_liam",
        "engine": "kokoro",
        "engine_profile": "cpu",
        "engine_model": "kokoro",
        "chunks": 1,
        "bytes": len(AUDIO),
    }


def manifest(*entries: dict) -> dict:
    return {
        "provides": 2,
        "voice": "am_liam",
        "format": "mp3",
        "addressing": {"scheme": "narrate-address-2", "chunk_chars": 1800},
        "counts": {"total": len(entries)},
        "ok": True,
        "segments": list(entries),
    }


def one_clean_job(*units: SpeechUnit) -> Recorder:
    """A recorder scripted to answer a job for `units` and then every fetch."""
    entries = [entry(item.id, ADDRESS_A[:-1] + str(index)) for index, item in enumerate(units)]
    return Recorder(as_json(manifest(*entries)), *(as_audio() for _ in units))


# --------------------------------------------------------------------------
# ⛔ The clause: a leaking segment stops the run BEFORE ANY REQUEST IS MADE,
#    asserted by inspecting what was SENT.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("leak", LEAKS)
def test_a_leaking_segment_sends_nothing_at_all(leak):
    """⛔ THE CLAUSE. The population is the requests and the assertion is that it is empty.

    ⭐ The refusal is SUPPRESSED rather than required here, deliberately: with
    `pytest.raises` the test would go red on the missing exception before it ever
    read the population, and *"the run raised"* is not the acceptance. The
    recorder is scripted to answer a whole successful job, so a client with no
    gate completes and this assertion — and only this assertion — fires.
    """
    units = [unit("s1", "A clean sentence."), unit("s2", f"see {leak} for more")]
    recorder = one_clean_job(*units)
    with contextlib.suppress(PersonalDataLeak):
        NarrateClient(BASE, transport=recorder).narrate(units)
    assert recorder.sent == []


@pytest.mark.parametrize("leak", LEAKS)
def test_a_leaking_segment_is_also_refused(leak):
    """⚠️ The companion, and NOT the acceptance — that a run raised says nothing
    about whether a request went out before it did.
    """
    units = [unit("s1", "A clean sentence."), unit("s2", f"see {leak} for more")]
    with pytest.raises(PersonalDataLeak):
        NarrateClient(BASE, transport=one_clean_job(*units)).narrate(units)


def test_the_recorder_would_have_seen_a_request_the_positive_control():
    """⭐ Without this, every `sent == []` above passes on a recorder nobody wired."""
    spoken = unit("s1", "A clean sentence.")
    recorder = one_clean_job(spoken)
    NarrateClient(BASE, transport=recorder).narrate([spoken])
    assert [item.method for item in recorder.sent] == ["POST", "GET"]
    assert b"A clean sentence." in recorder.sent[0].body


def test_a_leak_in_the_last_segment_still_sends_nothing():
    """⛔ The gate runs over EVERY unit before a body exists, not lazily."""
    many = [unit(f"s{index}", "Clean.") for index in range(40)]
    many.append(unit("s40", f"the capture ran from {HOME}/work"))
    recorder = one_clean_job(*many)
    with contextlib.suppress(PersonalDataLeak):
        NarrateClient(BASE, transport=recorder).narrate(many)
    assert recorder.sent == []


def test_a_leak_in_a_speech_id_sends_nothing():
    leaking = [unit(EMAIL, "Clean.")]
    recorder = one_clean_job(*leaking)
    with contextlib.suppress(PersonalDataLeak):
        NarrateClient(BASE, transport=recorder).narrate(leaking)
    assert recorder.sent == []


def test_a_leaking_base_url_sends_nothing():
    clean = [unit("s1", "Clean.")]
    recorder = one_clean_job(*clean)
    with contextlib.suppress(PersonalDataLeak):
        NarrateClient(f"http://{HOSTNAME}:8870", transport=recorder).narrate(clean)
    assert recorder.sent == []


def test_the_seam_gates_too_so_bypassing_narrate_sends_nothing():
    """⛔ The inner layer: a caller reaching past `narrate` still cannot send."""
    recorder = Recorder(as_json(manifest()))
    client = NarrateClient(BASE, transport=recorder)
    payload = {"segments": [{"id": "s1", "text": f"see {HOME}/work"}]}
    with contextlib.suppress(PersonalDataLeak):
        client._send("POST", JOBS_PATH, payload=payload, accept="application/json")
    assert recorder.sent == []


def test_the_seam_is_the_only_exit_and_every_route_uses_it():
    """⭐ The population is complete only if no route sidesteps `_send`."""
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and "_transport" in ast.unparse(node.func)
    ]
    assert len(calls) == 1, "more than one call site hands work to a transport"
    holder = next(
        function
        for function in ast.walk(tree)
        if isinstance(function, ast.FunctionDef) and calls[0] in ast.walk(function)
    )
    assert holder.name == "_send"


# --------------------------------------------------------------------------
# ⛔ The wider instrument: no SOCKET is opened either, and it can fire.
# --------------------------------------------------------------------------


def socket_guard(monkeypatch) -> list:
    """Replace `socket.socket` with a recorder that refuses to open anything."""
    opened: list = []

    def guard(*arguments, **keywords):
        opened.append(arguments)
        raise OSError("this test opens no socket")

    monkeypatch.setattr(socket, "socket", guard)
    return opened


def test_a_leaking_segment_opens_no_socket(monkeypatch):
    """⛔ Measured over the real transport, so no substitution can be the reason."""
    opened = socket_guard(monkeypatch)
    client = NarrateClient(BASE)
    assert client._transport is over_http
    with contextlib.suppress(PersonalDataLeak, ServiceUnavailable):
        client.narrate([unit("s1", "Clean."), unit("s2", f"see {HOME}/work")])
    assert opened == []


def test_the_socket_guard_fires_on_a_clean_run(monkeypatch):
    """⭐ The control for the test above: the guard is able to see an attempt."""
    opened = socket_guard(monkeypatch)
    with pytest.raises(ServiceUnavailable):
        NarrateClient(BASE).narrate([unit("s1", "Clean.")])
    assert opened, "the guard saw nothing here, so its silence above proves nothing"


def test_the_real_transport_reports_absence_in_a_scrubbed_printable_sentence(monkeypatch):
    """⛔ The message names the failure's TYPE, and the URL it prints is scrubbed."""
    socket_guard(monkeypatch)
    leaking = Sent("GET", f"{BASE}/x{HOME}/y", None, "application/json", 1.0)
    with pytest.raises(ServiceUnavailable) as absent:
        over_http(leaking)
    assert "still reads" in str(absent.value)
    assert "jane" not in str(absent.value)


# --------------------------------------------------------------------------
# ⛔ R7, and the refusal's own words
# --------------------------------------------------------------------------


def except_arms(function: ast.AST) -> list[str]:
    """Every `except` arm's type under `function`, as written."""
    return [
        "bare" if handler.type is None else ast.unparse(handler.type)
        for handler in ast.walk(function)
        if isinstance(handler, ast.ExceptHandler)
    ]


def test_no_arm_of_this_module_catches_a_leak_or_swallows_everything():
    """⛔ R7's own instrument, run over this module rather than the tree."""
    caught = except_arms(ast.parse(SOURCE.read_text(encoding="utf-8")))
    assert caught, "the scan found no arm, so the checks below read nothing"
    assert "bare" not in caught
    for arm in caught:
        assert "PersonalDataLeak" not in arm
        assert arm not in {"Exception", "BaseException"}


def test_the_refusal_names_the_speech_id_and_never_the_words():
    leaking = f"the capture ran from {HOME}/work"
    with pytest.raises(PersonalDataLeak) as refusal:
        NarrateClient(BASE, transport=Recorder()).narrate([unit("unit-01.1.b3", leaking)])
    assert "unit-01.1.b3" in str(refusal.value)
    assert "jane" not in str(refusal.value)


def test_a_clean_segment_is_sent_verbatim_and_is_never_rewritten():
    """⛔ The gate refuses; it does not scrub the source's words into a placeholder."""
    said = "Consider the path in the lesson, and read it aloud."
    recorder = one_clean_job(unit("s1", said))
    NarrateClient(BASE, transport=recorder).narrate([unit("s1", said)])
    body = json.loads(recorder.sent[0].body.decode("utf-8"))
    assert body["segments"] == [{"id": "s1", "text": said}]


# --------------------------------------------------------------------------
# ⛔ Standard library only, and R4 asserted rather than intended
# --------------------------------------------------------------------------


def test_the_module_imports_only_the_standard_library_and_the_framework_modules_it_names():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert imported == {
        "__future__",
        "collections.abc",
        "json",
        "re",
        "studyforge.archive.scrub",
        "studyforge.describe",
        "studyforge.narrate.answers",
        "studyforge.narrate.speakable.naming",
        "studyforge.narrate.speakable.records",
        "studyforge.narrate.wire",
    }


def test_the_client_does_not_import_the_placement_policy():
    """⛔ R4: the caller asks the policy; a client that imported it would decide."""
    for module in (
        "studyforge.corpus.placement",
        "studyforge.corpus.placement.names",
        "studyforge.corpus.placement.profile",
    ):
        assert not imports_module(SOURCE, module)


# --------------------------------------------------------------------------
# ⛔ The service being absent is a KNOWN STATE, and there is no partial state
# --------------------------------------------------------------------------


def test_probe_reports_an_absent_service_without_raising():
    absent = Recorder(ServiceUnavailable("nothing answered"))
    health = NarrateClient(BASE, transport=absent).probe()
    assert health.reachable is False
    assert "nothing answered" in health.detail


def test_probe_reports_a_reachable_service_and_its_deployment_settings():
    answer = as_json({**HEALTHY, "formats": ["mp3"]})
    health = NarrateClient(BASE, transport=Recorder(answer)).probe()
    assert (health.reachable, health.provides, health.chunk_chars) == (True, 2, 1800)


@pytest.mark.parametrize("model", ["kokoro", "kokoro-v1.1"])
def test_probe_reads_the_deployments_model_off_healthz_and_composes_none(model):
    # ⛔ `engine_model` is what `/healthz` reports, read verbatim.
    health = NarrateClient(BASE, transport=Recorder(as_json({**HEALTHY, "engine_model": model})))
    assert health.probe().engine_model == model


@pytest.mark.parametrize("missing", ["chunk_chars", "engine_model"])
def test_a_health_answer_without_a_content_address_setting_is_unreadable(missing):
    # ⛔ Not a guess: an answer that cannot say what clips are made under is not
    # a deployment this run may record conditions from.
    partial = {key: value for key, value in HEALTHY.items() if key != missing}
    health = NarrateClient(BASE, transport=Recorder(as_json(partial))).probe()
    assert health.reachable is False
    assert missing in health.detail


def test_probe_reads_health_and_asks_for_nothing_else():
    recorder = Recorder(as_json(HEALTHY))
    NarrateClient(BASE, transport=recorder).probe()
    assert [(item.method, item.url) for item in recorder.sent] == [("GET", BASE + HEALTH_PATH)]


def test_an_unreadable_health_answer_is_still_not_a_crash():
    health = NarrateClient(BASE, transport=Recorder(Received(200, "text/html", b"<p>"))).probe()
    assert health.reachable is False


def test_probe_catches_only_the_wires_own_refusals():
    # ⛔ A health answer is not a manifest, and the decode error is the
    # wire's. Every arm `probe` holds names a class `narrate.wire` defines.
    method = next(
        node
        for node in ast.walk(ast.parse(SOURCE.read_text(encoding="utf-8")))
        if isinstance(node, ast.FunctionDef) and node.name == "probe"
    )
    arms = except_arms(method)
    assert sorted(arms) == ["ServiceUnavailable", "UnreadableAnswer"]
    assert all(getattr(wire, arm).__module__ == wire.__name__ for arm in arms)
    assert not hasattr(client_module, "ManifestError")


def test_a_service_that_dies_mid_batch_writes_nothing(tmp_path):
    """⛔ No partial state: the artifacts are in memory and `place` is never reached."""
    units = [unit("s1", "First."), unit("s2", "Second.")]
    recorder = Recorder(
        as_json(manifest(entry("s1", ADDRESS_A), entry("s2", ADDRESS_B))),
        as_audio(),
        ServiceUnavailable("the engine went away"),
    )
    with pytest.raises(ServiceUnavailable):
        NarrateClient(BASE, transport=recorder).narrate(units)
    assert len(recorder.sent) == 3, "the run did reach the second fetch"
    assert list(tmp_path.iterdir()) == []


# --------------------------------------------------------------------------
# ⛔ Reading the manifest: counts, not the status code
# --------------------------------------------------------------------------


def test_a_partially_failing_job_keeps_the_work_that_finished():
    units = [unit("s1", "First."), unit("s2", "Second."), unit("s3", "Third.")]
    failed = {"id": "s2", "status": "failed", "reason": "engine_failed", "error": "no"}
    skipped = {"id": "s3", "status": "skipped", "reason": "engine_unavailable"}
    recorder = Recorder(as_json(manifest(entry("s1", ADDRESS_A), failed, skipped)), as_audio())
    narration = NarrateClient(BASE, transport=recorder).narrate(units)
    assert [item.speech_id for item in narration.artifacts] == ["s1"]
    assert narration.failed == (("s2", "engine_failed"),)
    assert narration.retryable == ("s3",)


def test_a_cached_segment_is_a_produced_segment():
    spoken = unit("s1", "First.")
    cached = entry("s1", ADDRESS_A, status="cached")
    recorder = Recorder(as_json(manifest(cached)), as_audio())
    narration = NarrateClient(BASE, transport=recorder).narrate([spoken])
    assert narration.artifacts[0].status == "cached"
    assert narration.artifacts[0].engine == "kokoro"


def test_the_manifests_own_url_is_never_followed():
    """⛔ The fetch is rebuilt against the configured base, not taken from the answer."""
    spoken = unit("s1", "First.")
    hostile = entry("s1", ADDRESS_A)
    hostile["url"] = "http://elsewhere.example/steal"
    recorder = Recorder(as_json(manifest(hostile)), as_audio())
    NarrateClient(BASE, transport=recorder).narrate([spoken])
    assert recorder.sent[1].url == f"{BASE}{ARTIFACT_PATH}{ADDRESS_A}"


@pytest.mark.parametrize("artifact_id", ["../../etc/passwd", "NOTHEX", "", "a" * 8])
def test_an_artifact_id_that_is_not_the_published_shape_is_refused(artifact_id):
    spoken = unit("s1", "First.")
    recorder = Recorder(as_json(manifest(entry("s1", artifact_id))))
    with pytest.raises(UnreadableAnswer):
        NarrateClient(BASE, transport=recorder).narrate([spoken])
    assert len(recorder.sent) == 1


def test_a_format_that_is_not_a_usable_suffix_is_refused():
    spoken = unit("s1", "First.")
    bad = entry("s1", ADDRESS_A)
    bad["format"] = "../mp3"
    with pytest.raises(UnreadableAnswer):
        NarrateClient(BASE, transport=Recorder(as_json(manifest(bad)))).narrate([spoken])


def test_a_manifest_about_a_segment_nobody_submitted_is_refused():
    recorder = Recorder(as_json(manifest(entry("s9", ADDRESS_A))))
    with pytest.raises(UnreadableAnswer):
        NarrateClient(BASE, transport=recorder).narrate([unit("s1", "First.")])


def test_a_job_that_is_not_two_hundred_is_a_refusal_and_not_an_unreadable_answer():
    recorder = Recorder(as_json({"error": "body must be JSON"}, status=400))
    with pytest.raises(ServiceRefused):
        NarrateClient(BASE, transport=recorder).narrate([unit("s1", "First.")])


def test_a_job_body_that_is_not_json_is_unreadable():
    recorder = Recorder(Received(200, "text/html", b"<html>"))
    with pytest.raises(UnreadableAnswer):
        NarrateClient(BASE, transport=recorder).narrate([unit("s1", "First.")])


def test_a_segment_that_is_not_a_speech_unit_is_refused_before_any_request():
    recorder = Recorder()
    with pytest.raises(TypeError):
        NarrateClient(BASE, transport=recorder).narrate([{"id": "s1", "text": "First."}])
    assert recorder.sent == []


def test_the_voice_and_format_reach_the_job_only_when_they_are_chosen():
    spoken = unit("s1", "First.")
    plain = one_clean_job(spoken)
    NarrateClient(BASE, transport=plain).narrate([spoken])
    assert set(json.loads(plain.sent[0].body)) == {"segments"}
    chosen = one_clean_job(spoken)
    NarrateClient(BASE, voice="af_bella", fmt="mp3", transport=chosen).narrate([spoken])
    assert json.loads(chosen.sent[0].body)["voice"] == "af_bella"


def test_a_base_url_that_is_not_a_string_is_refused():
    with pytest.raises(ValueError, match="base URL"):
        NarrateClient(None)
