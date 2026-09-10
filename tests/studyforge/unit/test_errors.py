"""Mirror of `src/studyforge/unit/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.unit import (
    ContentError,
    check_test_record,
    derived_section_key,
    from_document,
    section_key,
)


def test_a_content_error_is_a_value_error():
    # ⚠️ SF-01's split as `corpus.manifest` reads it: an overlay is a value
    # read from a document, so both halves fail the same way.
    assert issubclass(ContentError, ValueError)


@pytest.mark.parametrize(
    "call",
    [
        lambda: section_key("lesson"),
        lambda: section_key("lang", "Java"),
        lambda: derived_section_key("java", "heading", 0),
        lambda: check_test_record("borrowed"),
        lambda: from_document({"content_api": 99}, 1),
        lambda: from_document("not an object", 1),
    ],
)
def test_every_way_it_can_fail_raises_this_one_type(call):
    with pytest.raises(ContentError):
        call()


def test_a_refusal_names_the_file_the_section_and_the_field():
    # ⛔ This is the only file in the contract a person edits by hand, so a
    # typo must name itself rather than produce a page that is quietly wrong.
    with pytest.raises(ContentError) as raised:
        from_document(
            {
                "content_api": 1,
                "address": ["depth-one"],
                "unit": 1,
                "title": "T",
                "sections": [{"kind": "lang", "heading": "H", "blocks": []}],
            },
            1,
            "content.json",
        )
    message = str(raised.value)
    assert "content.json" in message and "section 0" in message and "lang" in message
