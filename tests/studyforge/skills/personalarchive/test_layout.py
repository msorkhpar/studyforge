"""Mirror of `src/studyforge/skills/personalarchive/layout.py` (R12): the manifest, paths and R7."""

from __future__ import annotations

import io
import json

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.skills.personalarchive.layout import (
    OWNER,
    PERSONAL_ARCHIVE_API,
    SHARING,
    ArchiveError,
    Material,
    gate,
    manifest_document,
    read_manifest,
    refused_path,
    render,
    speaker,
)
from studyforge.version import CONTRACT_FIELDS
from tests.studyforge.skills.personalarchive.archiving import planted_identity

STORE = ".studyforge/progress"
FILE = Material("corpus.json", b"{}\n", False)


def valid(**fields) -> str:
    return render({**manifest_document(OWNER, "demo", [FILE], progress=True), **fields})


def test_the_version_key_is_registered_where_r9_reads_it():
    assert "personal_archive_api" in CONTRACT_FIELDS
    assert read_manifest(valid())["personal_archive_api"] == PERSONAL_ARCHIVE_API


@pytest.mark.parametrize(
    ("fields", "names"),
    [
        ({"personal_archive_api": 2}, "personal_archive_api"),
        ({"personal_archive_api": True}, "personal_archive_api"),
        ({"kind": "everyone"}, "kind"),
        ({"source": ""}, "source"),
        ({"progress": "yes"}, "progress"),
        ({"kind": SHARING, "progress": True}, "sharing"),
        ({"material": {}}, "material"),
        ({"material": [{"path": "a"}]}, "file #1"),
        ({"material": [{**FILE.described(), "sha256": "x"}]}, "sha256"),
        ({"material": [{**FILE.described(), "bytes": -1}]}, "bytes"),
        ({"material": [FILE.described(), FILE.described()]}, "twice"),
        ({"extra": 1}, "exactly the keys"),
    ],
)
def test_a_manifest_that_is_not_exactly_one_this_build_speaks_is_refused(fields, names):
    with pytest.raises(ArchiveError, match=names):
        read_manifest(valid(**fields))


def test_a_manifest_that_is_not_json_or_not_an_object_is_refused():
    for text in ("{", "[]"):
        with pytest.raises(ArchiveError):
            read_manifest(text)


def test_a_manifest_carrying_an_identity_is_refused_by_the_gate():
    with pytest.raises(PersonalDataLeak):
        read_manifest(valid(source=planted_identity()))
    with pytest.raises(PersonalDataLeak):
        manifest_document(SHARING, planted_identity(), [FILE], progress=False)


def test_a_sharing_manifest_can_never_be_built_with_progress_and_the_kind_is_never_assumed():
    with pytest.raises(ArchiveError, match="never carries progress"):
        manifest_document(SHARING, "demo", [FILE], progress=True)
    with pytest.raises(ArchiveError, match="none is assumed"):
        manifest_document("", "demo", [FILE], progress=False)


@pytest.mark.parametrize(
    ("path", "why"),
    [
        ("", "plain relative"),
        ("/etc/passwd", "plain relative"),
        ("a//b", "plain relative"),
        ("a/./b", "plain relative"),
        ("a\\b", "plain relative"),
        ("../x", "climbs out"),
        ("a/../../x", "climbs out"),
        (".git/config", "version-control"),
        ("pkg/__pycache__/m.pyc", "bytecode"),
        (STORE, "progress store"),
        (f"{STORE}/progress.json", "progress store"),
    ],
)
def test_a_path_the_archive_may_not_carry_is_named_with_why(path, why):
    assert why in (refused_path(path, STORE) or "")


@pytest.mark.parametrize("path", ["corpus.json", "archive/a/b.json", ".studyforge/assets/x.css"])
def test_a_plain_path_outside_the_store_may_be_carried(path):
    assert refused_path(path, STORE) is None


def test_the_gate_reads_names_and_utf8_text_and_says_when_it_could_not_read():
    assert gate("notes.md", b"plain\n") is True
    assert gate("clip.bin", b"\xff\xfe\x00") is False
    with pytest.raises(PersonalDataLeak):
        gate("notes.md", f"at {planted_identity()}\n".encode())
    with pytest.raises(PersonalDataLeak):
        gate("jane.doe" + "@" + "mailhost.org.md", b"")


def test_render_is_stable_and_the_speaker_scrubs_every_line():
    assert render({"b": 1, "a": [2]}) == json.dumps({"a": [2], "b": 1}, indent=2) + "\n"
    out = io.StringIO()
    speaker(out)(f"refused {planted_identity()}")
    assert planted_identity() not in out.getvalue() and out.getvalue().startswith("refused ")
