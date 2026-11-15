"""Mirror of `src/studyforge/__init__.py` (R12)."""

from __future__ import annotations

import studyforge
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(studyforge, "studyforge")
