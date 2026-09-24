"""Mirror of `src/studyforge/render/page/errors.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.render.page.errors import PageError
from studyforge.render.templates import TemplateError


def test_a_page_error_is_its_own_family_and_not_a_value_error():
    # ⚠️ Following `AssetError` and `ContentError`: a document error, not a
    # caller's-argument error.
    assert issubclass(PageError, Exception)
    assert not issubclass(PageError, ValueError)


def test_a_personal_data_leak_is_not_caught_as_a_page_error():
    # ⛔ R7: a caller rendering a site catches `PageError` per unit and
    # carries on; an R7 refusal inside that family would be logged as one more
    # page that did not render, and the leak would be the thing nobody looked at.
    assert not issubclass(PersonalDataLeak, PageError)
    with pytest.raises(PersonalDataLeak):
        try:
            raise PersonalDataLeak("a leak")
        except PageError:  # pragma: no cover - the point is that this never fires
            pytest.fail("a personal-data refusal was caught as a page error")


def test_a_broken_template_is_not_a_page_error():
    # ⚠️ A missing template is true of every page this build would render, not
    # of the one document in hand. Folded into `PageError` it would report a
    # thousand unrenderable units where the answer is one broken file.
    assert not issubclass(TemplateError, PageError)
