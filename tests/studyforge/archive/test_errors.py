"""The archive's one exception type (SF-06)."""

import json

import pytest

from studyforge.archive.blocks import read_layout
from studyforge.archive.document import build, load, parse
from studyforge.archive.errors import ArchiveError
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.manifest import ManifestError
from studyforge.version import VersionError

HOME = "/" + "home/jane"

BASE = {
    "source": "demo",
    "address": ["solo"],
    "variant": "prose",
    "unit": 1,
    "kind": "lesson",
    "ordinal": 1,
    "ingested": "2026-01-05",
    "title": "Unit 1",
    "blocks": [{"type": "para", "text": "One."}],
}


def test_an_archive_error_is_a_value_error():
    # ⚠️ Following the manifest's precedent: somebody handed us something we
    # cannot accept.
    assert issubclass(ArchiveError, ValueError)


@pytest.mark.parametrize(
    "call",
    [
        lambda: parse("not json", "lesson-1.json"),
        lambda: parse("[]", "lesson-1.json"),
        lambda: parse(json.dumps({**build(**BASE), "raw_api": 99}), "lesson-1.json"),
        lambda: build(**{**BASE, "kind": "quiz"}),
        lambda: build(**{**BASE, "ingested": "yesterday"}),
        lambda: read_layout({"kind": "practice", "blocks": []}, "practice-1.json"),
    ],
)
def test_every_way_the_archive_says_no_is_the_same_type(call):
    # ⛔ One front door. A caller reading a file wants one answer to "can I
    # use this?", not five.
    with pytest.raises(ArchiveError):
        call()


def test_a_leak_is_not_an_archive_error():
    # ⛔ **The deliberate exception**, and the one worth a test of its own. R7's
    # refusal is louder than a format error, and a caller writing
    # `except ArchiveError: skip_this_file()` must not silently swallow one.
    assert not issubclass(PersonalDataLeak, ArchiveError)
    with pytest.raises(PersonalDataLeak):
        build(**{**BASE, "source": f"from {HOME}/corpus"})


def test_a_version_refusal_arrives_as_an_archive_error_not_a_version_error():
    # ⭐ Each contract keeps its own front door: SF-33's guard is handed
    # `error=ArchiveError`, so the shared check does not leak a shared type.
    assert not issubclass(ArchiveError, VersionError)
    with pytest.raises(ArchiveError):
        parse(json.dumps({**build(**BASE), "raw_api": 99}), "lesson-1.json")


def test_the_archive_and_the_manifest_do_not_share_an_error_type():
    # ⚠️ Two documents, two contracts, two answers. A caller reading a corpus
    # catches both deliberately rather than one by accident.
    assert not issubclass(ArchiveError, ManifestError)
    assert not issubclass(ManifestError, ArchiveError)


def test_a_missing_file_is_an_archive_error_and_not_an_os_error(tmp_path):
    with pytest.raises(ArchiveError):
        load(tmp_path / "absent.json")
