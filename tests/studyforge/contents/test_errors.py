"""Mirror of `src/studyforge/contents/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.contents import ContentsError, from_document, parse
from studyforge.version import VersionError


def test_a_contents_error_is_a_value_error():
    assert issubclass(ContentsError, ValueError)


def test_a_contents_error_is_not_a_version_error():
    # ⛔ Each contract keeps its own front door: a consumer catching this one
    # wants "the contents are wrong", never "something disagreed about a
    # version".
    assert not issubclass(ContentsError, VersionError)


def test_a_version_refusal_arrives_as_this_packages_own_type():
    with pytest.raises(ContentsError):
        from_document({"toc_api": 99})


def test_a_personal_data_leak_is_not_in_this_family():
    # ⛔ Ruling 58. A caller rendering a whole site catches `ContentsError` per
    # corpus and carries on; an R7 refusal folded into that family would be
    # logged as one more corpus that did not build.
    assert not issubclass(PersonalDataLeak, ContentsError)


def test_every_ordinary_refusal_in_this_package_is_one_type():
    for text in ("{not json", "[]", '{"toc_api": 1}'):
        with pytest.raises(ContentsError):
            parse(text)
