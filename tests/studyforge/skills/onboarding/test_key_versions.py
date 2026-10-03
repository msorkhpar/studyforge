"""`promote` writes the version every key it carries needs.

⭐ The version is read from the manifest package's own `KEY_VERSIONS`, so a key a version
adds is written under that version the day it is added. ⛔ Each case asks the manifest's
own reader, never a literal: the promoted document parses, and one version lower does not.
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import KEY_VERSIONS, ManifestError, parse
from studyforge.corpus.manifest.content import EACH_DIRECTORY_API
from studyforge.skills.onboarding import artifacts, hand_edited, onboard, reonboard
from studyforge.skills.onboarding.manifest import promote, render
from tests.studyforge.skills.onboarding import corpora

READING_MODE = {
    "id": "only",
    "label": "Only",
    "summary": "One language",
    "prose": "alpha",
    "tabs": ["alpha"],
    "practices": ["alpha"],
}

#: One draft per key a version added after `1`, each carrying only that key.
DRAFTS = {
    ("media", "max_files"): {**corpora.DRAFT, "media": {"max_files": 4000}},
    (None, "runtimes"): {**corpora.DRAFT, "exercises": True, "runtimes": ["java", "maven"]},
    (None, "narration"): {**corpora.DRAFT, "narration": False},
    (None, "onboarding_doc"): {**corpora.DRAFT, "onboarding_doc": "docs/reader.md"},
    (None, "curriculum"): {**corpora.DRAFT, "curriculum": {"record": "README.md"}},
    (None, "languages"): {
        **corpora.DRAFT,
        "languages": [{"id": "alpha", "label": "Alpha", "fence_labels": ["alpha"]}],
    },
    (None, "modes"): {
        **corpora.DRAFT,
        "languages": [{"id": "alpha", "label": "Alpha"}],
        "modes": [READING_MODE],
    },
    (None, "default_mode"): {
        **corpora.DRAFT,
        "languages": [{"id": "alpha", "label": "Alpha"}],
        "modes": [READING_MODE],
        "default_mode": "only",
    },
    (None, "outside_mode"): {
        **corpora.DRAFT,
        "languages": [{"id": "alpha", "label": "Alpha"}],
        "modes": [READING_MODE],
        "outside_mode": "locked",
    },
    (None, "profile"): {
        **corpora.DRAFT,
        "exercises": True,
        "runtimes": ["java"],
        "profile": "example-profile",
    },
    ("curriculum", "linked"): {
        **corpora.DRAFT,
        "levels": ["section", "module"],
        "curriculum": {
            "record": "README.md",
            "containers": [{"label": "Basics", "address": "basics"}],
            "linked": "module",
        },
    },
}


def test_every_key_a_version_added_has_a_case_here():
    # ⭐ A key added to the map without a case fails here, not in a stranger's corpus.
    assert set(DRAFTS) | {("content", "not_material")} == set(KEY_VERSIONS)


@pytest.mark.parametrize("key", sorted(DRAFTS, key=str))
def test_a_draft_carrying_a_key_is_written_under_the_version_that_key_needs(key):
    document = promote(DRAFTS[key])

    assert document["corpus_api"] == KEY_VERSIONS[key]
    assert parse(render(document)).corpus_api == KEY_VERSIONS[key]
    with pytest.raises(ManifestError):
        parse(render({**document, "corpus_api": KEY_VERSIONS[key] - 1}))


def test_the_highest_key_wins_and_no_key_lowers_a_drafted_version():
    both = {**DRAFTS[(None, "runtimes")], "narration": True}

    assert promote(both)["corpus_api"] == KEY_VERSIONS[(None, "narration")]
    assert promote({**both, "corpus_api": 6})["corpus_api"] == 6


def test_an_empty_runtimes_list_is_dropped_and_raises_nothing():
    document = promote({**corpora.DRAFT, "exercises": True, "runtimes": []})

    assert "runtimes" not in document
    assert document["corpus_api"] == corpora.DRAFT["corpus_api"]


@pytest.mark.parametrize(
    ("settle", "key"),
    [
        ({"exercises": True, "runtimes": ["python"]}, (None, "runtimes")),
        ({"media": {"max_files": 4000}}, ("media", "max_files")),
    ],
    ids=["runtimes", "media.max_files"],
)
def test_a_settle_that_needs_a_newer_version_is_written_under_it(tmp_path, settle, key):
    # ⛔ Each of these is refused by the version check under too low a `corpus_api`.
    root = corpora.material(tmp_path / "corpus")
    onboard(corpora.DRAFT, framework_commit=corpora.COMMIT).write(root)

    reonboard(root, settle=settle).write(root, regenerate=True)

    written = json.loads((root / artifacts.MANIFEST).read_text(encoding="utf-8"))
    assert {name: written[name] for name in settle} == settle
    assert written["corpus_api"] == KEY_VERSIONS[key]
    assert hand_edited(root) == []


def test_a_glob_in_every_root_directory_is_written_under_the_version_that_admits_it():
    # ⭐ A form, not a key: `*/name` under `content.not_material`, which a build
    # before `corpus_api` 8 refuses as a loose glob and blames on the corpus.
    reason = "each module's build file, written once for every module"
    drafted = {
        **corpora.DRAFT,
        "content": {
            **corpora.DRAFT["content"],
            "not_material": [{"glob": "*/pom.xml", "why": reason}],
        },
    }
    document = promote(drafted)

    assert document["corpus_api"] == EACH_DIRECTORY_API == 8
    with pytest.raises(ManifestError, match="corpus_api 8"):
        parse(render({**document, "corpus_api": 7}))
