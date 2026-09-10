"""Mirror of `src/studyforge/cli/plan/__init__.py` (R12)."""

from __future__ import annotations

from studyforge.cli import plan
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(plan, "studyforge.cli.plan")


def test_the_public_surface_is_what_a_consumer_needs_and_no_more():
    # ⛔ `derive` and `report` are not on it: a consumer that has to import
    # `studyforge.cli.plan.derive` is a consumer this contract failed.
    for name in plan.__all__:
        assert hasattr(plan, name), name


def test_the_three_consumers_can_reach_what_they_were_promised():
    # SK-07 renders ignore rules and the edits; OPS-05 asserts against paths;
    # a person reads the lines. All three arrive through this module.
    for name in ("plan_for", "Plan", "main"):
        assert name in plan.__all__
