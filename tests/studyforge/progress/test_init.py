"""Mirror of `src/studyforge/progress/__init__.py` (R12)."""

from __future__ import annotations

from studyforge import progress
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(progress, "studyforge.progress")
