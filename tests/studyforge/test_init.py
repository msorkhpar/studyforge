"""Mirror of `src/studyforge/__init__.py` (R12)."""

from __future__ import annotations

import studyforge
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(studyforge, "studyforge")


def test_names_the_rule_it_exists_under():
    # R1 is the ruling a reader of the top-level package most needs to meet
    # first: every source-specific fact arrives as data.
    assert "R1" in (studyforge.__doc__ or "")
