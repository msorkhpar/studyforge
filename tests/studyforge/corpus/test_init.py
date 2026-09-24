"""Mirror of `src/studyforge/corpus/__init__.py` (R12).

⚠️ The `RAISES` sweep is `tests/test_raises_convention.py`, not this package's:
its population is DERIVED from every package that exports a tuple, so it
reaches `generate`, `progress` and `serve` as well, and a tree-wide
instrument living in one package's mirror would range over `corpus.*` alone.
"""

from __future__ import annotations

from studyforge import corpus
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(corpus, "studyforge.corpus")
