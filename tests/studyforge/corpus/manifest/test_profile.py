"""Mirror of the `profile` key of `src/studyforge/corpus/manifest/document.py` (R12).

⭐ An optional top-level key naming the toolchain image profile a corpus's runner and editor are
built on. Absent is the manifest as it was; present, it is a name, it needs runtimes, and it
needs the version that added it. The names below are made up: no code knows a profile.
"""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import KEY_VERSIONS, ManifestError, from_document, versions_needed

BASE = {
    "corpus_api": 8,
    "source": "example-corpus",
    "title": "Example Corpus",
    "levels": ["section"],
    "variants": ["java"],
    "exercises": True,
    "runtimes": ["java"],
    "placement": "tree",
    "content": {"include": ["*/README*.md"], "exclude": []},
}


def manifest(**keys):
    return from_document({**BASE, **keys})


def test_an_absent_profile_is_none_and_the_manifest_reads_as_before():
    assert manifest().profile is None


def test_a_declared_profile_is_its_name():
    assert manifest(profile="example-profile").profile == "example-profile"


BAD = ["", "Upper", "two  words", "-lead", "trail-", "a_b", 3, None, ["x"]]


@pytest.mark.parametrize("bad", BAD)
def test_a_profile_that_is_not_a_hyphenated_name_is_refused_by_key(bad):
    with pytest.raises(ManifestError, match="'profile' must be a profile name"):
        manifest(profile=bad)


def test_a_profile_needs_the_runtimes_it_is_built_on():
    without = {k: v for k, v in BASE.items() if k != "runtimes"}
    with pytest.raises(ManifestError, match="declares a 'profile' and no 'runtimes'"):
        from_document({**without, "exercises": False, "profile": "example-profile"})


def test_the_key_is_gated_at_the_version_this_build_already_writes():
    assert KEY_VERSIONS[(None, "profile")] == 8
    needed = versions_needed({**BASE, "profile": "example-profile"})
    assert needed == [("runtimes", 4), ("profile", 8)]
    with pytest.raises(ManifestError, match="uses 'profile', which corpus_api 8 added"):
        manifest(corpus_api=7, profile="example-profile")
