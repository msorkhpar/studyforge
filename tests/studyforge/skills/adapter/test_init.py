"""Mirror of `src/studyforge/skills/adapter/__init__.py` (R12)."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys

import studyforge.validate as validate_package
from studyforge.cli import PROGRAM, VERBS
from studyforge.skills import adapter
from studyforge.skills.adapter import PARTS
from studyforge.validate import CHECKS
from tests.support import assert_package_contract, repository_root

#: How far past a dated figure its dating must appear, in characters.
DATED_WITHIN = 400

#: The verb the skill's fence gives. ⛔ Checked against the registered table
#: rather than assumed, so retiring the verb fails here and not in a reader's
#: shell.
VERB = "validate"

SKILL = "src/studyforge/skills/adapter/SKILL.md"
WHERE = "src/studyforge/skills/adapter"

#: ⛔ **The package's whole public surface, spelled out.** ⚠️ Duplicated from
#: `__all__` on purpose, following SF-01 and the pin `corpus.placement` already
#: has: a check that walks `__all__` to test `__all__` agrees with itself, so a
#: name silently LEAVING this surface was invisible to it.
#: ⭐ `W298`'s clause 3 is why it exists — `UNITS_DIR` survives here as a
#: BINDING of placement's spelling (`W199`'s rider: an adapter's whole
#: vocabulary arrives through this package, R19), and a surviving name owes a
#: CLOSED check rather than a spot assertion.
PUBLIC_SURFACE = frozenset(
    {
        "ARCHIVE_DIR",
        "BYTECODE_RULES",
        "FILLED_IN",
        "IGNORE_FILE",
        "PACKAGE",
        "PARTS",
        "RAW_DIR",
        "SOURCE_LINE_CEILING",
        "TREE_ROOT",
        "UNITS_DIR",
        "Layout",
        "LayoutError",
        "Part",
        "Plan",
        "PlanError",
        "Scaffold",
        "ScaffoldRefused",
        "Written",
        "archive_tree",
        "bytecode_ignore",
        "bytecode_ignores",
        "document_name",
        "ignore_files",
        "plan_for",
        "scaffold",
        "write_files",
    }
)


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
    # ⛔ W61 / Ruling 138: the command is DERIVED from what runs it, never
    # pinned as a literal. ⭐ SF-40 registered the console script, so the fence
    # is now the installed spelling and the derivation moves with it: the verb
    # comes from `cli.VERBS` and the program name from `cli.PROGRAM`, both
    # reached from `[project.scripts]`. Pinning the string here would let the
    # skill outlive the verb.
    text = skill_text()
    module = validate_package.__name__
    assert importlib.util.find_spec(f"{module}.__main__") is not None, f"{module} is not runnable"
    assert VERB in VERBS, f"{VERB!r} is not a registered verb; the skill's fence would not run"
    assert f"{PROGRAM} {VERB} <corpus-root>" in text
    assert "Done is a machine's answer, not a person's" in text


def test_the_skill_carries_the_measurements_rather_than_asserting_shape():
    # ⛔ R19: anything a second source would have to re-derive is a hole in the
    # skill. Each number below was counted in the pinned image, not inherited.
    # ⚠️ W257 (rider W248/3): the check and rule-id counts went stale after
    # `f816454`. They are DATED IN PLACE (Ruling 106), not rewritten, so the
    # date beside each is pinned with it.
    text = skill_text()
    for measured in ("**12 checks**", "**23 distinct rule ids**", "**11\ntypes**", "12.2%"):
        assert measured in text, f"the skill no longer carries the measurement {measured!r}"
    for stale in ("**12 checks**", "| checks | **12** |"):
        following = text[text.index(stale) : text.index(stale) + DATED_WITHIN]
        assert "⚠️ **Dated, and stale**" in following, (
            f"{stale!r} reads as current; it is a reading at f816454 and must say so"
        )


def test_the_skill_prints_the_check_count_rather_than_carrying_it():
    # ⭐ Ruling 163: a pointer resolves at read time, and an agent executes a
    # fence, so the fence is run here rather than read.
    fences = [line for line in skill_text().splitlines() if "len(v.CHECKS)" in line]
    assert len(fences) == 1, fences
    assert fences[0].startswith('python3 -c "') and fences[0].endswith('"'), fences[0]
    env = {**os.environ, "PYTHONPATH": str(repository_root() / "src")}
    result = subprocess.run(
        [sys.executable, "-c", fences[0][len('python3 -c "') : -1]],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )
    assert result.stdout.strip() == f"{len(CHECKS)} checks", result.stdout + result.stderr


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


def test_the_public_surface_is_exactly_what_the_contract_says():
    # ⛔ `W298` clause 3. ⚠️ The arm above walks `__all__`, so it answers
    # "does every declared name resolve" and CANNOT answer "is every name that
    # belongs here still declared" — dropping `UNITS_DIR` from `__all__` passes
    # it. ⭐ This one is closed over a population declared outside `__all__`.
    assert set(adapter.__all__) == PUBLIC_SURFACE
    missing = sorted(name for name in PUBLIC_SURFACE if not hasattr(adapter, name))
    assert missing == [], "exported but absent: " + ", ".join(missing)
