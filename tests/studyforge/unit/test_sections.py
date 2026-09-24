"""Mirror of `src/studyforge/unit/sections.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.unit import (
    KIND_OF,
    KINDS_WITH_A_LANG,
    SECTION_KINDS,
    ContentError,
    derived_section_key,
    section_key,
)

# --- a key never comes from a heading ---------------------------------------


def test_a_retitled_section_keeps_its_key_and_therefore_its_audio_filenames():
    # ⛔ The unit content's headline acceptance. Those ids name audio files on disk, so a
    # content-derived key would make a copy-edit silently orphan a unit's
    # narration: the page asks for clips that no longer exist, the clips that
    # do exist belong to nothing, and neither half fails.
    before = section_key("lang", "java")
    after = section_key("lang", "java")
    assert before == after == "java"


def test_the_heading_is_not_an_argument_at_all():
    # ⭐ Stronger than "the key does not change when the heading does": the
    # function cannot see a heading, so it cannot come to depend on one.
    import inspect

    assert "heading" not in inspect.signature(section_key).parameters


@pytest.mark.parametrize(
    "kind,variant,expected",
    [
        ("shared", None, "shared"),
        ("lang", "java", "java"),
        ("lang", "python-3", "python-3"),
        ("practice", "java", "practice-java"),
        ("practice", "sparql", "practice-sparql"),
    ],
)
def test_the_vocabulary_is_kind_and_variant(kind, variant, expected):
    assert section_key(kind, variant) == expected


def test_an_explicit_key_is_the_authors_escape_hatch_and_wins():
    assert section_key("lang", "java", "extra-reading") == "extra-reading"


# --- the ASCII-collision question, answered by refusing to slugify ----------


@pytest.mark.parametrize("key", ["Extra Reading", "café", "Java", "a_b", "", "  "])
def test_an_explicit_key_must_already_be_a_slug_and_is_never_made_into_one(key):
    # ⛔ `require_slug`, never `slugify`. A component which slugifies owes
    # itself a collision check the framework cannot make;
    # the answer here is to remove the slugification instead. A title passed
    # where a slug is required raises — it is not repaired.
    with pytest.raises(ContentError, match="slug|non-empty str"):
        section_key("lang", "java", key)


@pytest.mark.parametrize("variant", ["Java", "café", "java script", ""])
def test_a_variant_that_is_not_a_slug_is_refused_rather_than_slugified(variant):
    # ⭐ It costs nothing to refuse: `corpus.manifest` already validates every
    # declared variant as a slug, so deriving `<variant>` is the identity
    # function and cannot collide however the corpus spells its variants.
    with pytest.raises(ContentError, match="slug|non-empty str"):
        section_key("lang", variant)


def test_two_variants_that_would_collide_under_slugification_cannot_both_arrive():
    # The collision the question is about, shown to be unreachable: neither
    # spelling is a legal variant, so no pair of them can be keyed at all.
    for spelling in ("café", "cafe "):
        with pytest.raises(ContentError):
            section_key("lang", spelling)
    assert section_key("lang", "cafe") == "cafe"


# --- what it refuses --------------------------------------------------------


@pytest.mark.parametrize("kind", ["lesson", "", None, "Shared", "practice-java"])
def test_an_unknown_section_kind_is_refused_naming_the_ones_there_are(kind):
    with pytest.raises(ContentError) as raised:
        section_key(kind, "java")
    for name in SECTION_KINDS:
        assert name in str(raised.value)


@pytest.mark.parametrize("kind", KINDS_WITH_A_LANG)
def test_a_kind_that_names_a_variant_must_have_one(kind):
    with pytest.raises(ContentError):
        section_key(kind, None)


# --- the derived shape, for a unit with no overlay --------------------------


@pytest.mark.parametrize(
    "variant,kind,index,expected",
    [
        ("java", "lesson", 0, "java"),
        ("java", "lesson", 1, "java-2"),
        ("java", "practice", 0, "practice-java"),
        ("java", "practice", 2, "practice-java-3"),
        ("prose", "lesson", 0, "prose"),
    ],
)
def test_the_first_file_of_a_kind_keys_on_the_plain_name(variant, kind, index, expected):
    # ⭐ So the common case — one lesson and one practice — reads as it did
    # before a second one existed.
    assert derived_section_key(variant, kind, index) == expected


def test_the_position_is_among_its_own_kind_and_not_the_file_ordinal():
    # ⚠️ A capture that skips `lesson-2` must not leave a hole in the speech
    # ids, so the caller passes a position, not an ordinal.
    assert derived_section_key("java", "lesson", 1) == "java-2"


@pytest.mark.parametrize("archive_kind", ["heading", "", None, "shared", "lang"])
def test_a_section_derives_only_from_an_archive_kind(archive_kind):
    with pytest.raises(ContentError) as raised:
        derived_section_key("java", archive_kind, 0)
    for name in KIND_OF:
        assert name in str(raised.value)


@pytest.mark.parametrize("index", [-1, 1.0, True, None, "0"])
def test_a_position_that_is_not_one_is_refused(index):
    with pytest.raises(ContentError, match="0 or more"):
        derived_section_key("java", "lesson", index)


def test_a_derived_key_and_an_authored_one_agree_for_the_same_section():
    # ⛔ Two answers to "what is this section called" is how a page and its
    # media come to disagree; the derived form routes through the authored one.
    assert derived_section_key("java", "lesson", 0) == section_key("lang", "java")
    assert derived_section_key("java", "practice", 0) == section_key("practice", "java")
