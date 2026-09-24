"""The container map's one exception type."""

import json

import pytest

from studyforge.address import AddressError
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.container import ContainerError, from_document, load, parse
from studyforge.corpus.manifest import ManifestError
from studyforge.corpus.manifest import from_document as manifest_from_document
from studyforge.version import VersionError

HOME = "/" + "home/jane"

MANIFEST = {
    "corpus_api": 1,
    "source": "demo",
    "title": "Demo",
    "levels": ["section"],
    "variants": ["prose"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["**/*.md"]},
}

BASE = {
    "container_api": 1,
    "address": ["depth-one"],
    "titles": ["Depth One"],
    "variant": "prose",
    "ingested": "2026-01-05",
    "units": [{"n": 1, "title": "One", "practices": 0}],
}


def manifest():
    return manifest_from_document(MANIFEST, "corpus.json")


def built(**overrides):
    return from_document({**BASE, **overrides}, "container.json", manifest())


def test_a_container_error_is_a_value_error():
    assert issubclass(ContainerError, ValueError)


@pytest.mark.parametrize(
    "call",
    [
        lambda: parse("not json", "container.json", manifest()),
        lambda: parse("[]", "container.json", manifest()),
        lambda: built(container_api=99),
        lambda: built(variant="java"),
        lambda: built(units=[]),
        lambda: built(titles=[]),
        lambda: built(chapters=[]),
        lambda: built(units=[{"n": 2, "title": "b", "practices": 0}]),
        lambda: built(origin="/etc/passwd"),
        lambda: built(units=[{"n": 1, "title": "a", "practices": 0, "url_slug": "Not A Slug"}]),
    ],
)
def test_every_way_the_container_map_says_no_is_the_same_type(call):
    # ⛔ One front door. A caller reading a corpus wants one answer to "can I
    # use this?", not eight.
    with pytest.raises(ContainerError):
        call()


def test_the_arity_comparison_is_the_one_deliberate_exception():
    # ⚠️ The manifest's precedent exactly: the arity *comparison* is `address`'s and it
    # owns it outright — this document only supplies the address it declared.
    with pytest.raises(AddressError):
        built(address=["a", "b"])


def test_but_every_other_rule_of_sf_01_s_is_converted():
    # ⛔ What a slug is and what an ordinal is are the address package's rules; the *document*
    # is this contract's. ⭐ And converting them is not only consistency —
    # The address package's messages format the offending value with `!r`, and these values
    # are read straight out of a file somebody else wrote (R7).
    for broken in (
        {"n": 0, "title": "a", "practices": 0},
        {"n": 1, "title": "a", "practices": 0, "url_slug": "Not A Slug"},
    ):
        with pytest.raises(ContainerError):
            built(units=[broken])


def test_a_leak_is_not_a_container_error():
    # ⛔ R7's refusal is louder than a format error, and a caller writing
    # `except ContainerError: skip_this_file()` must not swallow one.
    assert not issubclass(PersonalDataLeak, ContainerError)
    with pytest.raises(PersonalDataLeak):
        built(note=f"ingested from {HOME}/corpus")


def test_a_version_refusal_arrives_as_a_container_error():
    # ⭐ Each contract keeps its own front door: the version guard is handed
    # `error=ContainerError`, so the shared check does not leak a shared type.
    assert not issubclass(ContainerError, VersionError)
    with pytest.raises(ContainerError):
        parse(json.dumps({**BASE, "container_api": 99}), "container.json", manifest())


def test_the_container_map_and_the_manifest_do_not_share_an_error_type():
    assert not issubclass(ContainerError, ManifestError)
    assert not issubclass(ManifestError, ContainerError)


def test_a_missing_file_is_a_container_error_and_not_an_os_error(tmp_path):
    with pytest.raises(ContainerError):
        load(tmp_path / "absent.json", manifest())
