"""Mirror of `src/studyforge/corpus/manifest/curriculum.py` (R12).

⭐ The declaration is asserted both ways: each shape the contract admits parses to
the value it states, and each refusal fires. ⛔ Whether a TREE agrees with it is
the adapter skill's, and is asserted in `tests/studyforge/skills/adapter/test_curriculum.py`.
"""

from __future__ import annotations

import pytest

from studyforge.address import Address
from studyforge.corpus.manifest import (
    KEY_VERSIONS,
    MANIFEST_KEYS,
    ManifestError,
    from_document,
    prefix_of,
)

#: A manifest at the version that added the key, declaring nothing about it yet.
BASE = {
    "corpus_api": 7,
    "source": "example-corpus",
    "title": "Example Corpus",
    "levels": ["group"],
    "variants": ["prose"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["src/*.md"]},
}

#: A second corpus's shape: its prefixes are words, and one group has none.
DECLARED = {
    "record": "SUMMARY.md",
    "containers": [
        {"label": "The Basics", "address": "basics", "prefix": "basics-"},
        {"label": "Going Deeper", "address": "deeper", "prefix": "deep_"},
        {"label": "Appendix", "address": "appendix"},
    ],
}


def parsed(curriculum: object, **overrides):
    """The `Manifest` a document carrying `curriculum` becomes."""
    return from_document({**BASE, **overrides, "curriculum": curriculum})


def refusal(curriculum: object, **overrides) -> str:
    """The message a document carrying `curriculum` is refused with."""
    with pytest.raises(ManifestError) as raised:
        parsed(curriculum, **overrides)
    return str(raised.value)


# --- clause 3: a corpus that declares nothing still works --------------------


@pytest.mark.parametrize("api", [1, 6, 7])
def test_a_manifest_without_the_key_has_no_curriculum_at_any_version(api):
    assert from_document({**BASE, "corpus_api": api}).curriculum is None


# --- the version the key needs (R9) ------------------------------------------


def test_the_key_is_corpus_api_7s_and_a_top_level_one():
    assert KEY_VERSIONS[(None, "curriculum")] == 7
    assert "curriculum" in MANIFEST_KEYS


def test_an_older_version_using_the_key_is_refused_naming_both_numbers():
    message = refusal(DECLARED, corpus_api=6)
    assert "corpus_api 6" in message
    assert "corpus_api 7" in message
    assert "curriculum" in message


# --- the shapes it admits -----------------------------------------------------


def test_a_declaration_reads_back_as_the_record_its_groups_and_their_prefixes():
    curriculum = parsed(DECLARED).curriculum
    assert curriculum.record == "SUMMARY.md"
    assert [each.label for each in curriculum.containers] == [
        "The Basics",
        "Going Deeper",
        "Appendix",
    ]
    assert [each.address for each in curriculum.containers] == [
        Address.of("basics"),
        Address.of("deeper"),
        Address.of("appendix"),
    ]
    assert [each.prefix for each in curriculum.containers] == ["basics-", "deep_", None]
    assert set(curriculum.prefixes) == {"basics-", "deep_"}


def test_the_record_alone_is_a_declaration_and_files_nothing():
    curriculum = parsed({"record": "docs/README.md"}).curriculum
    assert curriculum.record == "docs/README.md"
    assert curriculum.containers == ()


def test_the_empty_prefix_is_a_prefix():
    # ⭐ The first corpus's fundamentals are `1.md` … `16.md`: no text before the number.
    curriculum = parsed(
        {"record": "README.md", "containers": [{"label": "L", "address": "a", "prefix": ""}]}
    ).curriculum
    assert curriculum.prefixes[""].address == Address.of("a")


def test_an_address_is_checked_against_this_corpus_s_depth():
    two = {"record": "README.md", "containers": [{"label": "L", "address": "part/chapter"}]}
    assert parsed(two, levels=["part", "chapter"]).curriculum.containers[0].address.depth == 2
    assert "address" in refusal(two)


@pytest.mark.parametrize(
    ("path", "prefix"),
    [
        ("src/s10.md", "s"),
        ("src/10.md", ""),
        ("lessons/basics-3.md", "basics-"),
        ("src/Server.md", None),
        ("src/1a.md", None),
        ("src/s10-notes.md", None),
    ],
)
def test_a_name_carries_the_text_before_its_number_or_nothing(path, prefix):
    assert prefix_of(path) == prefix


# --- the refusals -------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "README.md",
        [],
        {},
        {"record": "README.md", "curriculum": 1},
        {"record": "README.md", "containers": {}},
        {"record": "README.md", "containers": ["L"]},
    ],
    ids=["a string", "a list", "no record", "an unknown key", "a map", "a bare label"],
)
def test_a_declaration_not_shaped_as_the_contract_says_is_refused(value):
    assert "curriculum" in refusal(value)


@pytest.mark.parametrize(
    "record",
    ["/abs/README.md", "../README.md", "./README.md", "docs/*.md", "README.txt", ".md", "", 7],
)
def test_a_record_that_is_not_a_markdown_file_inside_the_corpus_is_refused(record):
    message = refusal({"record": record})
    assert "curriculum.record" in message
    # ⛔ R7: a path that is not a corpus path is usually somebody's home directory.
    if isinstance(record, str) and record.startswith("/"):
        assert record not in message


@pytest.mark.parametrize("prefix", ["s1", "a/b", "a b", "s*", 3])
def test_a_prefix_that_could_not_partition_the_names_is_refused(prefix):
    group = {"label": "L", "address": "a", "prefix": prefix}
    assert "prefix" in refusal({"record": "README.md", "containers": [group]})


@pytest.mark.parametrize("field", ["label", "address", "prefix"])
def test_a_repeated_label_address_or_prefix_is_refused(field):
    first = {"label": "One", "address": "one", "prefix": "o"}
    second = {"label": "Two", "address": "two", "prefix": "t", field: first[field]}
    message = refusal({"record": "README.md", "containers": [first, second]})
    assert f"repeats a {field}" in message


@pytest.mark.parametrize(
    "group",
    [
        {"address": "a"},
        {"label": " ", "address": "a"},
        {"label": "L"},
        {"label": "L", "address": "Not A Slug"},
        {"label": "L", "address": "a", "title": "x"},
    ],
    ids=["no label", "a blank label", "no address", "a non-slug address", "an unknown key"],
)
def test_a_group_missing_or_mis_stating_a_field_is_refused(group):
    assert "curriculum.containers[0]" in refusal({"record": "README.md", "containers": [group]})
