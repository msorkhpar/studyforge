"""Mirror of `src/studyforge/contents/__init__.py` (R12)."""

from __future__ import annotations

from studyforge import contents
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(contents, "studyforge.contents")
