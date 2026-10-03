"""`require_lang`: what an archive document's `lang` may be."""

from __future__ import annotations

import pytest

from studyforge.archive.errors import ArchiveError
from studyforge.archive.language import LANG_ID, languages_of, require_lang


@pytest.mark.parametrize("good", ["a", "kotlin", "x-1", "a_b", "9z"])
def test_an_id_is_returned_as_given(good):
    assert require_lang(good, "lesson-1") == good


@pytest.mark.parametrize("bad", ["", " a", "A", "-a", "a.b", "a/b", None, 1, ("a",)])
def test_anything_else_is_refused_naming_the_field_and_the_document(bad):
    with pytest.raises(ArchiveError) as refused:
        require_lang(bad, "lesson-1")
    assert "lesson-1 has an invalid 'lang'" in str(refused.value)


def test_a_refused_string_is_never_quoted():
    with pytest.raises(ArchiveError) as refused:
        require_lang("/" + "home/someone", "lesson-1")
    assert "someone" not in str(refused.value)


def test_the_pattern_is_the_one_a_manifest_spells_its_ids_with():
    from studyforge.corpus.manifest.reading import ID

    assert LANG_ID.pattern == ID.pattern


@pytest.mark.parametrize("several", ["a b", "aa bb cc dd", "x-1 a_b 9z"])
def test_several_ids_joined_by_single_spaces_are_returned_as_given(several):
    assert require_lang(several, "lesson-1") == several
    assert languages_of(several) == tuple(several.split(" "))


@pytest.mark.parametrize("bad", ["a  b", "a b ", "a,b", "a a", "a B", "a\tb", " "])
def test_a_list_that_repeats_an_id_or_is_spaced_oddly_is_refused(bad):
    with pytest.raises(ArchiveError) as refused:
        require_lang(bad, "lesson-1")
    assert "lesson-1 has an invalid 'lang'" in str(refused.value)
