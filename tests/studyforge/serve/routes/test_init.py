"""Mirror of `src/studyforge/serve/routes/__init__.py` (R12)."""

from __future__ import annotations

from studyforge.serve import routes
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(routes, "studyforge.serve.routes")
