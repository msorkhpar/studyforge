"""Mirror of `src/studyforge/corpus/manifest/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.corpus.manifest import (
    ManifestError,
    from_document,
    parse_content,
    parse_edits,
    parse_media,
)

#: Every public entry point, with an argument each one refuses. ⛔ One
#: exception type or a caller writes an `except` clause per module.
REFUSALS = [
    (parse_content, ({"include": []},)),
    (parse_media, ({"commit": "sometimes"},)),
    (parse_edits, ("not a list", parse_content({"include": ["*.md"]}))),
    (from_document, ({"corpus_api": 99},)),
]


def test_a_manifest_error_is_a_value_error():
    # ⚠️ SF-01's proposed precedent, and this line is the whole of SF-02's
    # exposure to it: a *value* error subclasses `ValueError`. If the CTO
    # overrules the split, this is what changes.
    assert issubclass(ManifestError, ValueError)


@pytest.mark.parametrize("function,arguments", REFUSALS)
def test_every_public_entry_point_raises_this_one_type(function, arguments):
    with pytest.raises(ManifestError):
        function(*arguments)


@pytest.mark.parametrize("function,arguments", REFUSALS)
def test_nothing_repairs_a_value_quietly(function, arguments):
    # ⛔ R6. The alternative to raising is a manifest that means something
    # nobody wrote, and a corpus built from it that nobody can explain.
    try:
        function(*arguments)
    except ManifestError as error:
        assert str(error).strip(), f"{function.__name__} raised with no message"
    else:
        pytest.fail(f"{function.__name__} accepted a value it should refuse")


def test_a_refusal_names_the_field_and_the_permitted_class_but_not_the_value():
    # ⭐ A manifest is the first file an integrator writes by hand, so its
    # refusals are the first thing this framework ever says to them.
    # ⛔ Which is also why the value is not repeated back: any string in a
    # hand-written file can be an absolute path (R7, Ruling 14). The field and
    # the permitted set are what the reader cannot see; the value is in the
    # file in front of them.
    with pytest.raises(ManifestError) as raised:
        parse_media({"commit": "sometimes"})
    message = str(raised.value)
    assert "media.commit" in message
    assert "sometimes" not in message
    assert "always" in message


def test_a_refusal_over_a_closed_set_says_what_the_set_is():
    with pytest.raises(ManifestError) as raised:
        from_document({"corpus_api": 99})
    assert "[1]" in str(raised.value)


def test_it_can_be_caught_as_a_value_error_by_a_caller_that_does_not_import_it():
    # A CLI that catches `ValueError` around "read this corpus" gets this for
    # free, which is what the shared base is for.
    with pytest.raises(ValueError, match="content"):
        parse_content(None)
