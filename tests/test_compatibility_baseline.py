"""The compatibility baseline: today's behaviour, recorded, so a later change that moves it fails.

Mirrors no source module. It adds no behaviour: every expectation below was written
from the code as it stood before any change that adds a language, and none was
copied from output a later change produced. `tests/baseline/__init__.py` says how each
recording was made and the one command that rewrites them, on purpose and never to
make a red run green.

## What each clause pins, and what already pinned part of it

- builds: the sha256 of every file `write_site` writes for each valid fixture corpus
  (`sites.json`). Already pinned: page and plan goldens (`tests/harness/goldens.py`),
  which cover pages and paths and not the whole output tree.
- exports: the sha256 of every file of the thin and the self-contained export of the
  runnable fixture, less what the checkout alone decides (`exports.json`). Already
  pinned: `standalone/test_write.py` holds structure and agreement between the modes,
  not bytes.
- locks: literal lock documents that no helper builds, accepted and refused as today.
  Already pinned: `standalone/test_bases.py`, which builds locks with helpers and is kept.
- manifests: the parsed value of every fixture manifest and of manifests using every key,
  the key tables and the accepted versions. Already pinned: `test_spec_manifest_keys.py`
  holds the spec against the key list.
- narration: the promise number, the three routes, and the request and answer shapes the
  client uses. Already pinned: `buildserve/test_narration.py` reads the sibling's own file
  when it is on disk.

The toolchain's tags are pinned in that repository's own suite, which is where they
are computed.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import document as manifest_document
from studyforge.corpus.manifest import runtimes as manifest_runtimes
from studyforge.narrate import answers
from studyforge.narrate.client import NarrateClient
from studyforge.narrate.speakable.records import SpeechUnit
from studyforge.narrate.wire import Received, Sent
from studyforge.skills.execution.standalone import bases
from tests import baseline


def moved(live: dict[str, str], kept: dict[str, str]) -> list[str]:
    """One sentence per file whose bytes, presence or absence differs from the recording."""
    found = [f"{path} is no longer written" for path in sorted(kept.keys() - live.keys())]
    found += [f"{path} is newly written" for path in sorted(live.keys() - kept.keys())]
    found += [
        f"{path} has other bytes"
        for path in sorted(kept.keys() & live.keys())
        if live[path] != kept[path]
    ]
    return found


# ---------------------------------------------------------------- builds


@pytest.mark.parametrize("name", baseline.SITE_CORPORA)
def test_a_fixture_corpus_builds_to_the_recorded_bytes(name):
    assert moved(baseline.sites()[name], baseline.recorded("sites.json")[name]) == []


def test_every_valid_fixture_corpus_is_recorded():
    assert sorted(baseline.recorded("sites.json")) == sorted(baseline.SITE_CORPORA)
    assert all(baseline.recorded("sites.json").values()), (
        "a recording with no files would pin nothing"
    )


# ---------------------------------------------------------------- exports


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    return baseline.exports(tmp_path_factory.mktemp("baseline"))


@pytest.mark.parametrize("mode", ["thin", "self-contained"])
def test_an_export_of_the_runnable_fixture_is_the_recorded_bytes(exported, mode):
    assert moved(exported[mode], baseline.recorded("exports.json")[mode]) == []


def test_the_normalising_takes_out_only_what_the_checkout_decides(exported):
    kept = baseline.recorded("exports.json")
    assert not any(path.startswith(baseline.SERVE_TREE) for path in kept["self-contained"])
    assert baseline.RELEASE in kept["thin"] and baseline.RELEASE in kept["self-contained"]
    assert {
        "README.md",
        "compose.yaml",
        "course.env",
        ".studyforge/images/site/Dockerfile",
    } <= kept["thin"].keys()


# ---------------------------------------------------------------- locks

SERVE_TAG = "0.1.0-" + "a" * 64
#: A lock as the published bases have it, written out. ⛔ Made-up hex digests, no account.
TODAYS_LOCK = {
    "bases_api": 1,
    "serve": {"image": "studyforge-serve", "tag": SERVE_TAG, "digest": "sha256:" + "3" * 64},
    "runner": {
        "image": "studyforge-code-toolchain-runner",
        "tag": "java-maven-node-python-amd64-f8f1db0be48a",
        "digest": "sha256:" + "4" * 64,
    },
    "editor": {
        "image": "studyforge-code-toolchain-editor",
        "tag": "java-maven-node-python-amd64-14e3f747ce03",
        "digest": "sha256:" + "5" * 64,
    },
}
#: What the pinned toolchain computes for each recorded runtime set (the toolchain's own baseline).
TOOLCHAIN = {
    ("java", "maven"): {
        "runner": "java-maven-amd64-f8f1db0be48a",
        "editor": "java-maven-amd64-14e3f747ce03",
    },
    ("java", "maven", "node", "python"): {
        "runner": "java-maven-node-python-amd64-f8f1db0be48a",
        "editor": "java-maven-node-python-amd64-14e3f747ce03",
    },
}


def tags_for(runtimes):
    return TOOLCHAIN[tuple(sorted(runtimes))] if tuple(sorted(runtimes)) in TOOLCHAIN else _refuse()


def _refuse():
    raise ValueError("not a recorded set")


def lock_text(**changes) -> str:
    document = json.loads(json.dumps(TODAYS_LOCK))
    for key, value in changes.items():
        document[key] = {**document[key], **value} if isinstance(value, dict) else value
    return json.dumps(document)


def accepts(text: str, declared=("java", "maven")) -> None:
    locked = bases.from_text(text)
    bases.check(
        locked,
        version="0.1.0",
        toolchain=TOOLCHAIN[declared if declared in TOOLCHAIN else ("java", "maven")],
        serve_tag=SERVE_TAG,
        declared=declared,
        tags_for=tags_for,
    )


def test_a_lock_of_the_published_shape_is_read_as_it_always_was():
    locked = bases.from_text(lock_text())
    assert locked.serve.reference == f"studyforge-serve:{SERVE_TAG}@sha256:{'3' * 64}"
    assert locked.runner.reference == (
        "studyforge-code-toolchain-runner:java-maven-node-python-amd64-f8f1db0be48a"
        f"@sha256:{'4' * 64}"
    )
    assert locked.editor.reference.startswith(
        "studyforge-code-toolchain-editor:java-maven-node-python-amd64-"
    )
    assert (bases.key(locked.runner), bases.key(locked.editor)) == ("4" * 12, "5" * 12)
    assert dict(bases.PUBLISHED) == {
        "serve": "studyforge-serve",
        "runner": "studyforge-code-toolchain-runner",
        "editor": "studyforge-code-toolchain-editor",
    }


def test_a_published_lock_passes_the_check_for_the_exact_set_and_for_a_declared_subset():
    accepts(lock_text(), declared=("java", "maven", "node", "python"))
    accepts(lock_text(), declared=("java", "maven"))  # built on a superset of the declared set
    exact = {
        "runner": {"tag": "java-maven-amd64-f8f1db0be48a"},
        "editor": {"tag": "java-maven-amd64-14e3f747ce03"},
    }
    accepts(lock_text(**exact), declared=("java", "maven"))


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("not json", "not JSON"),
        (lock_text(bases_api=2), "bases_api"),
        (json.dumps({**TODAYS_LOCK, "extra": 1}), "keys it does not read"),
        (lock_text(runner={"image": "runner"}), "no longer publishes"),
        (lock_text(editor={"image": "acct/editor"}), "not a bare name"),
        (lock_text(editor={"digest": "sha256:abc"}), "digest"),
        (lock_text(serve={"digest": bases.PLACEHOLDER}), "placeholder"),
    ],
)
def test_a_lock_the_reader_refused_is_still_refused(text, message):
    with pytest.raises(bases.BasesRefused, match=message):
        bases.from_text(text)


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"runner": {"tag": "java-maven-node-python-amd64-000000000000"}}, "computes"),
        ({"editor": {"tag": "python-node-maven-java-amd64-14e3f747ce03"}}, "computes"),
        ({"runner": {"tag": "java-cobol-amd64-f8f1db0be48a"}}, "does not know"),
        ({"serve": {"tag": "0.1.0-" + "b" * 64}}, "checkout computes"),
    ],
)
def test_a_lock_the_check_refused_is_still_refused(changes, message):
    with pytest.raises(bases.BasesRefused, match=message):
        accepts(lock_text(**changes))


def test_a_base_that_lacks_a_declared_runtime_is_refused_by_name():
    exact = {
        "runner": {"tag": "java-maven-amd64-f8f1db0be48a"},
        "editor": {"tag": "java-maven-amd64-14e3f747ce03"},
    }
    with pytest.raises(bases.BasesRefused, match=r"lacks .*\['node'\]"):
        bases.check(
            bases.from_text(lock_text(**exact)),
            version="0.1.0",
            toolchain=TOOLCHAIN[("java", "maven", "node", "python")],
            serve_tag=SERVE_TAG,
            declared=("java", "node"),
            tags_for=tags_for,
        )


# ---------------------------------------------------------------- manifests


def test_every_recorded_manifest_parses_to_the_recorded_declarations():
    live, kept = baseline.manifests(), baseline.recorded("manifests.json")
    assert sorted(live) == sorted(kept)
    assert [name for name in kept if live[name] != kept[name]] == []


def test_the_manifest_keys_of_today_all_stay_and_none_becomes_required():
    today = (
        "corpus_api source title levels variants curriculum exercises runtimes narration "
        "onboarding_doc placement content media permitted_edits"
    ).split()
    required = "corpus_api source title levels variants exercises placement content".split()
    assert set(today) <= set(manifest_document.MANIFEST_KEYS), "an existing key was removed"
    assert set(manifest_document.REQUIRED_KEYS) == set(required), (
        "a key became required, or stopped being"
    )
    assert set(manifest_document.KNOWN_CORPUS_API) >= set(range(1, 9)), "a version was dropped"
    assert manifest_document.PLACEMENT_PROFILES[:2] == ("tree", "sibling")


def test_the_version_each_existing_key_needs_is_unchanged():
    today = {
        ("content", "not_material"): 2,
        ("media", "max_files"): 3,
        (None, "runtimes"): 4,
        (None, "narration"): 5,
        (None, "onboarding_doc"): 6,
        (None, "curriculum"): 7,
        ("curriculum", "linked"): 8,
    }
    assert {key: manifest_document.KEY_VERSIONS[key] for key in today} == today


def test_the_runtime_vocabulary_only_grows_and_keeps_what_each_writes():
    today = ("gradle", "java", "kotlin", "maven", "node", "python", "shell", "sqlite")
    assert set(today) <= set(manifest_runtimes.RUNTIMES)
    assert {
        name: manifest_runtimes.SOURCE_SUFFIXES[name]
        for name in manifest_runtimes.SOURCE_SUFFIXES
        if name in today
    } == {
        "java": (".java",),
        "kotlin": (".kt",),
        "node": (".js", ".mjs", ".cjs", ".ts"),
        "python": (".py",),
        "shell": (".sh", ".bash"),
        "sqlite": (".sql",),
    }
    assert {"gradle", "kotlin", "maven"} <= set(manifest_runtimes.REQUIRES_JAVA)


# ---------------------------------------------------------------- narration

AUDIO = b"ID3\x04mp3 bytes"
ADDRESS = "ab" * 32


class Wire:
    """A transport that records each request and answers from a script."""

    def __init__(self, *answers):
        self.sent: list[Sent] = []
        self._answers = list(answers)

    def __call__(self, sent: Sent) -> Received:
        self.sent.append(sent)
        return self._answers.pop(0)


def json_answer(payload) -> Received:
    return Received(200, "application/json", json.dumps(payload).encode("utf-8"))


#: What the service answers today, as its API document shows it.
HEALTH = {
    "status": "ok",
    "version": "0.1.0",
    "provides": 3,
    "chunk_chars": 1800,
    "default_voice": "am_liam",
    "voices": 68,
    "engine_reachable": True,
    "formats": ["mp3"],
    "engine": "kokoro",
    "engine_profile": "cpu",
    "engine_model": "kokoro",
}
JOB = {
    "provides": 3,
    "voice": "am_liam",
    "format": "mp3",
    "addressing": {"scheme": "narrate-address-2", "chunk_chars": 1800},
    "counts": {"total": 1},
    "ok": True,
    "segments": [
        {
            "id": "s1",
            "status": "synthesised",
            "artifact_id": ADDRESS,
            "url": f"/v1/artifacts/{ADDRESS}",
            "format": "mp3",
            "media_type": "audio/mpeg",
            "voice": "am_liam",
            "engine": "kokoro",
            "engine_profile": "cpu",
            "engine_model": "kokoro",
            "chunks": 1,
            "bytes": len(AUDIO),
        }
    ],
}


def test_the_framework_was_written_against_promise_three_and_three_routes():
    assert answers.PROMISE == 3
    from studyforge.skills.buildserve import narration

    assert narration.PROMISE == 3
    from studyforge.narrate import client

    assert (client.HEALTH_PATH, client.JOBS_PATH, client.ARTIFACT_PATH) == (
        "/healthz",
        "/v1/jobs",
        "/v1/artifacts/",
    )


def test_the_client_asks_exactly_what_it_asked_and_reads_the_answers_of_today():
    wire = Wire(json_answer(HEALTH), json_answer(JOB), Received(200, "audio/mpeg", AUDIO))
    narrator = NarrateClient("http://127.0.0.1:8870", voice="am_liam", fmt="mp3", transport=wire)
    health = narrator.probe()
    unit = SpeechUnit(
        id="s1", speak="Say this.", section="s", block_path=(0,), sub_index=None, kind="paragraph"
    )
    done = narrator.narrate([unit])
    asked = [
        (one.method, one.url, one.accept, None if one.body is None else json.loads(one.body))
        for one in wire.sent
    ]
    assert asked == [
        ("GET", "http://127.0.0.1:8870/healthz", "application/json", None),
        (
            "POST",
            "http://127.0.0.1:8870/v1/jobs",
            "application/json",
            {"segments": [{"id": "s1", "text": "Say this."}], "voice": "am_liam", "format": "mp3"},
        ),
        ("GET", f"http://127.0.0.1:8870/v1/artifacts/{ADDRESS}", "audio/*", None),
    ]
    assert (health.reachable, health.provides, health.chunk_chars, health.engine_model) == (
        True,
        3,
        1800,
        "kokoro",
    )
    assert [a.audio for a in done.artifacts] == [AUDIO] and done.provides == 3 and done.failed == ()
