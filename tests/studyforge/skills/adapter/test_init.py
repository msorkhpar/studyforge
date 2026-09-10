"""Mirror of `src/studyforge/skills/adapter/__init__.py` (R12)."""

from __future__ import annotations

from studyforge.skills import adapter
from studyforge.skills.adapter import PARTS
from tests.support import assert_package_contract, repository_root

SKILL = "src/studyforge/skills/adapter/SKILL.md"
WHERE = "src/studyforge/skills/adapter"


def skill_text():
    """The skill document, which is the far end of every pointer in this package."""
    return (repository_root() / SKILL).read_text(encoding="utf-8")


def test_states_its_contract():
    assert_package_contract(adapter, "studyforge.skills.adapter")


def test_the_skill_document_sits_beside_the_code_it_calls():
    # ⭐ §9: a skill is a document with a procedure and this package is what it
    # *calls*. They ship in one directory so a consumer copies one thing.
    assert (repository_root() / SKILL).is_file(), "the skill document is missing"
    assert "# Skill — adapter authoring" in skill_text()


def test_the_skill_names_validate_as_its_definition_of_done():
    # ⛔ R2: an adapter's whole obligation is an archive `validate` accepts, and
    # a skill that described a shape instead would be checkable by opinion.
    text = skill_text()
    assert "studyforge validate <corpus-root>" in text
    assert "Done is a machine's answer, not a person's" in text


def test_the_skill_carries_the_measurements_rather_than_asserting_shape():
    # ⛔ R19: anything a second source would have to re-derive is a hole in the
    # skill. Each number below was counted in the pinned image, not inherited.
    text = skill_text()
    for measured in ("**12 checks**", "**22 distinct rule ids**", "**11\ntypes**", "12.2%"):
        assert measured in text, f"the skill no longer carries the measurement {measured!r}"


def test_every_part_is_produced_by_a_step_the_skill_document_writes_down():
    # ⛔ A file the procedure never mentions is a file nobody is told to look
    # at — and the scaffold would still write it.
    text = skill_text()
    for part in PARTS:
        assert f"### {part.step}." in text, (
            f"{part.where} claims step {part.step}, which SKILL.md does not have"
        )


def test_no_module_here_names_a_corpus_even_in_a_docstring():
    # ⛔ §7c, and R1 behind it: the framework knows nothing about any source.
    # ⭐ The skill document is exempt because it is the far end of the pointer.
    corpora = ("ISO-8583", "jPOS", "SPARQL", "Java-senior", "CodeSignal", "Claude-senior")
    for module in sorted((repository_root() / WHERE).rglob("*.py")):
        text = module.read_text(encoding="utf-8")
        for name in corpora:
            assert name not in text, (
                f"{module.name} names {name!r}. ⛔ The measurement belongs in SKILL.md."
            )


def test_the_surface_is_exactly_what_it_declares():
    # ⛔ Ruling 101's producer half: a name a second package needs is on this
    # `__all__`, or the two packages do not share it.
    for name in adapter.__all__:
        assert hasattr(adapter, name), f"__all__ names {name!r}, which is not exported"
    assert len(set(adapter.__all__)) == len(adapter.__all__), "a name is exported twice"
