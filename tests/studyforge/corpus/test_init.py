"""Mirror of `src/studyforge/corpus/__init__.py` (R12).

⚠️ The `RAISES` sweep that stood here is now `tests/test_raises_convention.py`.
⛔ It was never this package's to hold: its population is now DERIVED from every
package that exports a tuple, so it reaches `generate`, `progress` and `serve`
as well, and a tree-wide instrument living in one package's mirror is how it
came to range over `corpus.*` alone.
"""

from __future__ import annotations

from studyforge import corpus
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(corpus, "studyforge.corpus")
