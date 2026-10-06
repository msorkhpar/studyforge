"""Mirror of `src/studyforge/corpus/manifest/reading.py` (R12).

⭐ Every clause is asserted both ways: each refusal fires by name, and every valid
shape parses. The fixture declares its languages as data, with ids no code knows.
"""

from __future__ import annotations

import copy

import pytest

from studyforge.corpus.manifest import (
    KEY_VERSIONS,
    OUTSIDE_MODES,
    Language,
    ManifestError,
    Mode,
    Reading,
    from_document,
    versions_needed,
)

BASE = {
    "corpus_api": 8,
    "source": "example-corpus",
    "title": "Example Corpus",
    "levels": ["section"],
    "variants": ["java"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["*/README*.md"], "exclude": []},
}

LANGUAGES = [
    {"id": "alpha", "label": "Alpha", "fence_labels": ["alpha", "a"]},
    {"id": "beta", "label": "Beta", "fence_labels": ["beta"]},
]
MODES = [
    {
        "id": "alpha-only",
        "label": "Alpha only",
        "summary": "Alpha prose and code",
        "prose": "alpha",
        "tabs": ["alpha"],
        "practices": ["alpha"],
    },
    {
        "id": "both",
        "label": "Both",
        "summary": "Alpha prose, Beta tab too",
        "prose": "alpha",
        "tabs": ["alpha", "beta"],
        "practices": ["alpha", "beta"],
        "practice_choice": True,
    },
]


def manifest(**keys):
    return {**copy.deepcopy(BASE), **copy.deepcopy(keys)}


def full(**keys):
    return manifest(**{"languages": LANGUAGES, "modes": MODES, **keys})


def refused(document, *words):
    with pytest.raises(ManifestError) as raised:
        from_document(document)
    for word in words:
        assert word in str(raised.value)


def test_a_manifest_with_none_of_the_keys_has_no_reading():
    assert from_document(manifest()).reading is None


def test_languages_alone_are_valid_and_offer_no_mode():
    reading = from_document(manifest(languages=LANGUAGES)).reading
    assert reading == Reading(
        languages=(
            Language("alpha", "Alpha", ("alpha", "a")),
            Language("beta", "Beta", ("beta",)),
        ),
        modes=(),
        default_mode=None,
        outside_mode="open",
    )


def test_fence_labels_are_optional():
    reading = from_document(manifest(languages=[{"id": "alpha", "label": "Alpha"}])).reading
    assert reading.languages[0].fence_labels == ()


def test_modes_parse_in_order_with_the_first_as_the_default():
    reading = from_document(full()).reading
    assert [mode.id for mode in reading.modes] == ["alpha-only", "both"]
    assert reading.default_mode == "alpha-only"
    assert reading.outside_mode == "open"
    assert reading.modes[1] == Mode(
        "both",
        "Both",
        "Alpha prose, Beta tab too",
        "alpha",
        ("alpha", "beta"),
        ("alpha", "beta"),
        True,
    )
    assert reading.modes[0].practice_choice is False


def test_default_mode_and_outside_mode_are_read():
    reading = from_document(full(default_mode="both", outside_mode="locked")).reading
    assert (reading.default_mode, reading.outside_mode) == ("both", "locked")


def test_a_mode_may_list_no_practices():
    document = full()
    document["modes"][0]["practices"] = []
    assert from_document(document).reading.modes[0].practices == ()


def test_modes_without_languages_are_refused():
    refused(manifest(modes=MODES), "'modes'", "without 'languages'")


@pytest.mark.parametrize("key", ["default_mode", "outside_mode"])
def test_default_and_outside_mode_without_modes_are_refused(key):
    value = "open" if key == "outside_mode" else "both"
    refused(manifest(languages=LANGUAGES, **{key: value}), f"'{key}'", "without 'modes'")


@pytest.mark.parametrize("field", ["prose", "tabs", "practices"])
def test_a_mode_naming_an_undeclared_language_is_refused(field):
    document = full()
    document["modes"][1][field] = "gamma" if field == "prose" else ["alpha", "gamma"]
    refused(document, f"modes[1].{field}", "'gamma'", "does not declare")


def test_a_language_in_a_mode_list_twice_is_refused():
    document = full()
    document["modes"][1]["tabs"] = ["alpha", "alpha"]
    refused(document, "modes[1].tabs", "more than once")


def test_a_mode_with_no_tabs_is_refused():
    document = full()
    document["modes"][0]["tabs"] = []
    refused(document, "modes[0].tabs", "non-empty")


def test_duplicate_language_ids_are_refused():
    refused(
        manifest(languages=[LANGUAGES[0], {**LANGUAGES[1], "id": "alpha"}]),
        "languages",
        "'alpha'",
        "twice",
    )


def test_duplicate_mode_ids_are_refused():
    document = full()
    document["modes"][1]["id"] = "alpha-only"
    refused(document, "modes", "'alpha-only'", "twice")


def test_a_fence_label_claimed_by_two_languages_is_refused():
    document = manifest(languages=LANGUAGES)
    document["languages"][1]["fence_labels"] = ["beta", "a"]
    refused(document, "fence label", "'a'", "alpha", "beta")


def test_a_fence_label_repeated_in_one_language_is_refused():
    document = manifest(languages=[{"id": "alpha", "label": "A", "fence_labels": ["x", "x"]}])
    refused(document, "fence_labels", "'x'", "twice")


@pytest.mark.parametrize("label", ["", "two words", 3, "`"])
def test_a_malformed_fence_label_is_refused(label):
    refused(
        manifest(languages=[{"id": "alpha", "label": "A", "fence_labels": [label]}]), "fence_labels"
    )


def test_a_default_mode_that_is_not_a_mode_is_refused():
    refused(full(default_mode="gamma"), "default_mode", "declared mode", "'gamma'")


@pytest.mark.parametrize("value", ["closed", "OPEN", None, True, ["open"]])
def test_an_outside_mode_other_than_open_or_locked_is_refused(value):
    refused(full(outside_mode=value), "outside_mode", "open", "locked")


def test_the_outside_modes_are_open_and_locked():
    assert OUTSIDE_MODES == ("open", "locked")


@pytest.mark.parametrize("value", ["yes", 1, None, "true"])
def test_a_practice_choice_that_is_not_a_boolean_is_refused(value):
    document = full()
    document["modes"][1]["practice_choice"] = value
    refused(document, "modes[1].practice_choice", "true or false")


@pytest.mark.parametrize("key", ["id", "label", "summary", "prose", "tabs", "practices"])
def test_a_mode_missing_a_required_key_is_refused(key):
    document = full()
    del document["modes"][0][key]
    refused(document, "modes[0]", "missing", key)


@pytest.mark.parametrize("key", ["id", "label"])
def test_a_language_missing_a_required_key_is_refused(key):
    document = manifest(languages=copy.deepcopy(LANGUAGES))
    del document["languages"][0][key]
    refused(document, "languages[0]", key)


def test_an_unknown_key_in_a_language_or_mode_is_refused():
    document = full()
    document["languages"][0]["colour"] = "red"
    refused(document, "languages[0]", "unknown", "colour")
    document = full()
    document["modes"][0]["colour"] = "red"
    refused(document, "modes[0]", "unknown", "colour")


@pytest.mark.parametrize("bad", ["Upper", "", "has space", 4, None])
def test_a_malformed_id_is_refused(bad):
    refused(manifest(languages=[{"id": bad, "label": "A"}]), "languages[0].id")


@pytest.mark.parametrize("key", ["languages", "modes"])
@pytest.mark.parametrize("value", [[], "alpha", None, {}, [3]])
def test_an_empty_or_malformed_list_is_refused(key, value):
    refused(full(**{key: value}), f"'{key}")


def test_a_non_string_label_is_refused():
    document = full()
    document["modes"][0]["summary"] = 3
    refused(document, "modes[0].summary", "non-empty string")


@pytest.mark.parametrize("key", ["languages", "modes", "default_mode", "outside_mode"])
def test_each_key_is_gated_by_the_version_table_at_the_current_version(key):
    assert KEY_VERSIONS[(None, key)] == 8
    document = full(default_mode="both", outside_mode="locked", corpus_api=7)
    refused(document, "corpus_api 7", "corpus_api 8")
    used = versions_needed(full(default_mode="both", outside_mode="open"))
    assert key in {name for name, _ in used}


def test_a_manifest_at_the_current_version_with_every_key_parses():
    assert from_document(full(default_mode="both", outside_mode="locked")).corpus_api == 8


def test_no_new_key_is_required_and_the_version_is_not_raised():
    from studyforge.corpus.manifest import CORPUS_API, KNOWN_CORPUS_API, REQUIRED_KEYS

    assert CORPUS_API == 8 and max(KNOWN_CORPUS_API) == 8
    assert not {"languages", "modes", "default_mode", "outside_mode"} & set(REQUIRED_KEYS)
