"""Mirror of `src/studyforge/skills/reconnaissance/__init__.py` (R12)."""

from __future__ import annotations

from studyforge.skills import reconnaissance
from tests.support import assert_package_contract, repository_root


def test_states_its_contract():
    assert_package_contract(reconnaissance, "studyforge.skills.reconnaissance")


def test_the_skill_document_sits_beside_the_code_it_calls():
    # ⭐ §9: a skill is a document with a procedure, and this package is what it
    # *calls*. They ship in one directory so a consumer copies one thing —
    # R20's point, that what a consumer needs is carried here.
    skill = repository_root() / "src/studyforge/skills/reconnaissance/SKILL.md"
    assert skill.is_file(), "the skill document is missing; the package is not the skill"
    assert "# Skill — source reconnaissance" in skill.read_text(encoding="utf-8")


def test_the_skill_document_carries_the_measurements_rather_than_asserting_shape():
    # ⛔ R19: anything a second source would have to re-derive is a hole in the
    # skill. The traps are written down with their numbers, so the next
    # integrator starts further along than the last.
    text = (repository_root() / "src/studyforge/skills/reconnaissance/SKILL.md").read_text("utf-8")
    for measured in (
        "37 of 38",
        "50.2%",
        "53.7%",
        "21 containers for a 3-container corpus",
        "39.5%",
    ):
        assert measured in text, f"the skill no longer carries the measurement {measured!r}"
