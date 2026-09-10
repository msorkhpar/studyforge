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


def test_no_module_here_names_a_corpus_even_in_a_docstring():
    # ⛔ §7c, and R1 behind it: the framework knows nothing about any source.
    # ⚠️ **"Even in a comment" is what makes this check work** — the first
    # version of this package put 21 corpus names in docstrings, zero in live
    # code, and a second copy of one measurement table had already drifted from
    # `SKILL.md` inside a single commit.
    #
    # ⭐ The skill document is exempt **because it is the far end of the
    # pointer**: a skill names the material it was measured on, and that is the
    # one place a name belongs. Modules point at it and hold nothing.
    #
    # ⚠️ Scoped to this package deliberately. A repository-wide version of this
    # check is the CTO's to rule on, not a test to add on the way past.
    corpora = ("ISO-8583", "jPOS", "SPARQL", "Java-senior", "CodeSignal", "Claude-senior")
    where = repository_root() / "src/studyforge/skills/reconnaissance"
    for module in sorted(where.glob("*.py")):
        text = module.read_text(encoding="utf-8")
        for name in corpora:
            assert name not in text, (
                f"{module.name} names {name!r}. ⛔ The measurement belongs in "
                f"SKILL.md; the module points at it."
            )
