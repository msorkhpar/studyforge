"""Mirror of `src/studyforge/skills/onboarding/__init__.py` (R12)."""

from __future__ import annotations

from studyforge.skills import onboarding
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(onboarding, "studyforge.skills.onboarding")


def test_a_consumer_needs_only_the_package():
    # ⭐ A consumer that has to import a submodule directly is a consumer this
    # contract failed. `onboard`, `uninstall` and the refusals are the whole of
    # what a skill's reader touches.
    assert {"onboard", "uninstall", "OnboardingRefused"} <= set(onboarding.__all__)
    assert all(hasattr(onboarding, name) for name in onboarding.__all__)


def test_the_surface_names_each_thing_once():
    # ⚠️ Order is ruff's to enforce (RUF022 groups constants, classes and
    # functions); what a test can say that a linter cannot is that no name is
    # exported twice and every one of them resolves.
    assert len(onboarding.__all__) == len(set(onboarding.__all__))


def test_the_procedure_ships_beside_the_package():
    # ⛔ §9: the document is the deliverable and this package is what it calls.
    from pathlib import Path

    assert (Path(onboarding.__file__).parent / "SKILL.md").exists()
