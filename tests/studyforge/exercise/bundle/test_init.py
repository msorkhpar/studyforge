"""The bundle package's contract, its public surface, and what it may not reach for."""

from __future__ import annotations

import ast
from pathlib import Path

from studyforge import exercise
from studyforge.exercise import bundle
from tests.support import assert_package_contract, repository_root


def package_modules() -> list[Path]:
    root = repository_root() / "src" / "studyforge" / "exercise" / "bundle"
    return sorted(path for path in root.glob("*.py"))


def test_the_package_states_its_contract():
    assert_package_contract(bundle, "studyforge.exercise.bundle")


def test_the_public_surface_is_declared_and_complete():
    assert set(bundle.__all__) == {
        "BUILD",
        "BUNDLES_DIRNAME",
        "BUNDLE_API",
        "BUNDLE_DIRNAMES",
        "BUNDLE_FILENAME",
        "BUNDLE_FILENAMES",
        "BUNDLE_KEYS",
        "Bundle",
        "Emission",
        "GATES_FILENAME",
        "OPTIONAL_KEYS",
        "PLANTS_DIRNAME",
        "PLANT_DIRNAME",
        "Places",
        "REFERENCE_SUMMARY",
        "ROLE_DIRNAMES",
        "RUN_OUTPUT_DIRNAME",
        "RUN_OUTPUT_IGNORE",
        "SHIPPED_ROLES",
        "STATEMENT",
        "STATEMENT_FILENAME",
        "TESTS",
        "bundle_document",
        "bundle_of",
        "edges_of",
        "emit",
        "emit_page",
        "is_run_output",
        "ordinals",
        "plant_dirname",
        "plant_positions",
        "require_inside",
        "require_no_gap",
        "unpermitted",
        "write",
    }
    assert all(hasattr(bundle, name) for name in bundle.__all__)


def test_the_parent_contract_says_this_sub_package_exists():
    # ⛔ R17: a parent contract is where a reader finds out a sub-package is
    # there. `gates` and `quiz` are named for the same reason.
    assert "`bundle`" in (exercise.__doc__ or "")


def test_no_module_here_runs_anything_or_reaches_a_module_by_name():
    # ⛔ There is no legal discovery mechanism in `src/` (`AX-03`'s first
    # surprise), and a bundle is read off disk rather than executed.
    forbidden = {"subprocess", "importlib", "shutil", "socket", "urllib"}
    for path in package_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {(node.module or "").split(".")[0]}
            else:
                continue
            assert not (names & forbidden), f"{path.name} imports {names & forbidden}"


def test_nothing_here_knows_any_source(tmp_path):
    # ⛔ R1: the framework knows nothing about any source. Every module is read
    # for the names of the repositories this workspace pins.
    sources = ("codesignal", "iso-8583", "jpos", "sparql", "java-engineer")
    for path in package_modules():
        text = path.read_text(encoding="utf-8").lower()
        for name in sources:
            assert name not in text, f"{path.name} names {name}"


def test_the_package_depends_only_on_studyforge_and_the_standard_library():
    allowed = {"studyforge", "dataclasses", "pathlib", "json", "re", "__future__"}
    for path in package_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level == 0:
                assert (node.module or "").split(".")[0] in allowed, node.module
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] in allowed, alias.name
