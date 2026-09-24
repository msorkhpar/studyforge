"""Mirror of `src/studyforge/corpus/manifest/fields.py` (R12).

⭐ The field rules are exercised through the document in `test_document.py`,
which is where a corpus meets them. What lives here is each rule read on its
own, both ways, so a change to one names the rule rather than the document.
"""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import ManifestError
from studyforge.corpus.manifest.fields import (
    exercises_of,
    levels_of,
    narration_of,
    slug_of,
    title_of,
    variants_of,
)


def test_a_title_is_free_text_and_an_empty_one_is_refused():
    assert title_of("Senior Java, 2nd ed.", "corpus.json") == "Senior Java, 2nd ed."
    with pytest.raises(ManifestError, match="'title'"):
        title_of("   ", "corpus.json")


def test_labels_are_not_slugs_and_an_empty_label_is_refused_by_position():
    assert levels_of(["Section", "Module"], "corpus.json") == ("Section", "Module")
    with pytest.raises(ManifestError, match=r"'levels\[1\]'"):
        levels_of(["Section", ""], "corpus.json")


def test_an_empty_list_is_refused_naming_the_key():
    with pytest.raises(ManifestError, match="'variants' must be a non-empty list"):
        variants_of([], "corpus.json")


def test_slugs_are_the_address_package_s_and_a_refusal_arrives_as_this_package_s_error():
    assert variants_of(["java", "2nd"], "corpus.json") == ("java", "2nd")
    assert slug_of("demo", "source") == "demo"
    with pytest.raises(ManifestError):
        slug_of("Not A Slug", "source")


@pytest.mark.parametrize("value", [1, "true", None])
def test_exercises_is_a_real_bool_and_nothing_that_looks_like_one(value):
    assert exercises_of(False, "corpus.json") is False
    with pytest.raises(ManifestError, match="'exercises' must be true or false"):
        exercises_of(value, "corpus.json")


@pytest.mark.parametrize("value", [0, "off", "false", None])
def test_narration_is_a_real_bool_and_nothing_that_looks_like_one(value):
    # ⭐ The author's answer, recorded as they gave it.
    assert narration_of(False, "corpus.json") is False
    assert narration_of(True, "corpus.json") is True
    with pytest.raises(ManifestError, match="'narration' must be true or false"):
        narration_of(value, "corpus.json")
