"""Mirror of `src/studyforge/corpus/__init__.py` (R12)."""

from __future__ import annotations

from studyforge import corpus
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(corpus, "studyforge.corpus")
