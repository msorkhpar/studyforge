"""Mirror of `src/studyforge/skills/exercises/__init__.py` (R12).

⭐ **What goes RED, each planted:** a package that stops stating its contract, a
name that leaves the surface, a surface that stops being the two modules' own
names, and a run-time import appearing in either module — the door
`tests/harness/test_isolation.py` closes for the framework and `AX-03` lost a
design to.
"""

from __future__ import annotations

import ast
from pathlib import Path

from studyforge.skills import exercises
from tests.support import assert_package_contract, repository_root

#: This package, as an importer spells it.
PACKAGE = "studyforge.skills.exercises"

#: ⛔ The whole public surface, spelled out. ⚠️ Duplicated from `__all__` on
#: purpose: a name leaving the contract is a decision, and this is what makes
#: it one rather than a quiet deletion.
PUBLIC_SURFACE = frozenset(
    {
        "ACCOUNTED_KEYS",
        "ADVANCED",
        "BANDS",
        "CORE",
        "ENTRY_KEYS",
        "ENTRY_KINDS",
        "EXAMPLE",
        "INTRODUCTORY",
        "LEDGER_API",
        "LEDGER_KEYS",
        "PLAN_API",
        "PLAN_KEYS",
        "REASON_DESCRIBED",
        "REASON_KEYS",
        "SHORTFALL_KEYS",
        "SOURCE_KEYS",
        "TESTS",
        "TIERS",
        "TIER_MOVES",
        "Accounted",
        "Band",
        "Entry",
        "Fence",
        "Ledger",
        "LedgerError",
        "Plan",
        "PlanError",
        "Reason",
        "Refusal",
        "Scan",
        "Source",
        "account",
        "accounts_for",
        "band_for",
        "digests",
        "key_of",
        "ledger_document",
        "plan_document",
        "plan_for",
        "scan",
        "shortfall",
        "shortfall_document",
        "take",
    }
)

#: ⛔ The names a run-time import is spelled with. A registry populated by one
#: is a registry only a run can answer for, and the harness refuses it framework
#: wide; this asserts the property for the two modules rather than inheriting it.
NEVER_IMPORTED = ("importlib", "pkgutil", "subprocess", "shutil", "socket", "urllib")


def modules() -> list[Path]:
    """Every module of this package, read from disk rather than from `__file__`."""
    directory = repository_root() / "src" / "studyforge" / "skills" / "exercises"
    return sorted(directory.glob("*.py"))


def test_states_its_contract():
    assert_package_contract(exercises, PACKAGE)


def test_the_surface_is_what_the_contract_says_it_is():
    assert set(exercises.__all__) == PUBLIC_SURFACE, "the surface moved without a decision"
    assert len(exercises.__all__) == len(PUBLIC_SURFACE), "a name is exported twice"


def test_every_exported_name_resolves():
    for name in exercises.__all__:
        assert hasattr(exercises, name), f"{name!r} is exported and is not there"


def test_nothing_here_discovers_anything_at_run_time():
    found = [path for path in modules() if path.name != "__init__.py"]
    assert found, "the package has no modules, so this asserts nothing"
    for path in found:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported = {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        } | {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        for name in NEVER_IMPORTED:
            assert name not in imported, f"{path.name} imports {name!r}; see the contract"
