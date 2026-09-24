"""Mirror of `src/studyforge/validate/source/__init__.py` (R12).

⛔ **The guard the whole package rests on lives here, and that is the point of
the split rather than an accident of it.** A guard that names one file in a
package of three is a guard the next submodule walks straight past, so it is
derived from the package directory instead — and the derivation asserts its own
inhabitation, because a sweep over an empty set passes.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.validate import source
from studyforge.validate.source import classification, completeness, enumeration, membership
from tests.support import assert_package_contract, repository_root

#: The package on disk, as the guard below walks it.
PACKAGE = "src/studyforge/validate/source"


#: ⭐ The survey is the importer the surface guard below was written over.
SURVEY = "src/studyforge/skills/reconnaissance/inventory.py"


def modules() -> dict[str, str]:
    """Every module of the package, by relative path, with its text."""
    root = repository_root() / PACKAGE
    return {
        path.relative_to(repository_root()).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(root.glob("*.py"))
    }


def test_states_its_contract():
    assert_package_contract(source, "studyforge.validate.source")


def test_the_public_surface_is_what_a_consumer_needs_and_no_more():
    # ⛔ A consumer that has to import `studyforge.validate.source.completeness`
    # is a consumer this contract failed.
    for name in source.__all__:
        assert hasattr(source, name), name


def test_both_checks_are_reachable_through_the_package():
    for name in (
        "CHECKS",
        "check_archive_members",
        "check_declared_files",
        "check_unclassified",
        "check_completeness",
        "source_files",
    ):
        assert name in source.__all__


def test_the_checks_run_in_the_order_the_report_reads_best():
    # ⛔ The order, not the membership: what the files *are* is reported before
    # what one of them *contains*, and `validate.run` splices this tuple in as
    # it stands.
    # ⭐ The archive root first: a stray there is not material beside it,
    # and what the archive DECLARES and does not hold is the same question from
    # the other end, so the two sit together and before the material.
    assert source.CHECKS == (
        source.check_archive_members,
        source.check_declared_files,
        source.check_unclassified,
        source.check_completeness,
    )


def test_every_rule_id_the_package_can_emit_is_on_its_surface():
    # ⚠️ A script filters a report by rule id and needs the constant rather
    # than the string. ⛔ **Derived from the two halves rather than re-typed**,
    # so the next rule id added to either one is exported or this fails —
    # which is the failure mode for a rule such as `ignore-declaration` or
    # `contested`, each its own rather than folded into `unclassified`.
    declared = {
        name
        for module in (classification, completeness, enumeration, membership)
        for name in vars(module)
        if name.startswith("RULE_")
    }
    assert declared, "the derivation found no rule ids at all"
    assert {name for name in source.__all__ if name.startswith("RULE_")} == declared


def test_the_seam_holds_and_neither_half_imports_the_other():
    # ⛔ **The claim the package docstring makes, asserted rather than stated.**
    # If one half ever reaches for the other the seam has moved and the two
    # test modules stop naming what they cover.
    # ⭐ `classification` reads `enumeration`, the walk it judges, and that is the
    # ONE edge inside the package. Nothing reads `classification`; `enumeration` reads none.
    edges = {
        classification: {enumeration},
        completeness: set(),
        enumeration: set(),
        membership: set(),
    }
    for module, reads in edges.items():
        imported = {
            node.module
            for node in ast.walk(ast.parse(Path(module.__file__).read_text(encoding="utf-8")))
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert {other for other in edges if other.__name__ in imported} == reads, module.__name__


def test_no_module_in_this_package_reaches_for_the_markdown_reader():
    # ⛔ **The assertion the whole completeness check rests on.** Two readings
    # from the same parser are not two readings, and the only way to keep that
    # true is to forbid the import outright — a later hand could otherwise
    # "simplify" a submodule by reusing the reader and the suite would stay
    # green.
    found = modules()
    # ⭐ Inhabitation first: a sweep over an empty set passes, and a package
    # renamed out from under this test would do exactly that.
    assert set(found) == {
        f"{PACKAGE}/__init__.py",
        f"{PACKAGE}/classification.py",
        f"{PACKAGE}/completeness.py",
        f"{PACKAGE}/enumeration.py",
        f"{PACKAGE}/membership.py",
    }
    for where, text in found.items():
        imported = {
            node.module
            for node in ast.walk(ast.parse(text))
            if isinstance(node, ast.ImportFrom) and node.module and "markdown" in node.module
        }
        assert imported == set(), f"{where} imports the reader: {imported}"


def test_the_guard_above_would_notice(tmp_path):
    # ⛔ **The negative control, and it is run negatively.** The sweep is only
    # worth anything if the same expression flags a module that does import the
    # reader; without this row a broken `ast` walk would pass on every file.
    text = "from studyforge.archive.markdown import read\n"
    imported = {
        node.module
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.ImportFrom) and node.module and "markdown" in node.module
    }
    assert imported == {"studyforge.archive.markdown"}


def past_the_surface(text: str) -> set[str]:
    """Each import in `text` past this package's `__all__`: a submodule, or a name off it."""
    package = source.__name__
    past: set[str] = set()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Import):
            past |= {alias.name for alias in node.names if alias.name.startswith(f"{package}.")}
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(package):
            if node.module != package:
                past.add(node.module)
            else:
                past |= {
                    f"{package}.{alias.name}"
                    for alias in node.names
                    if alias.name not in source.__all__
                }
    return past


def test_W280_no_module_outside_the_package_imports_past_its_surface():
    # ⛔ The split's second clause: a consumer under `src/` reads `__all__`, never a
    # submodule. ⚠️ Tests
    # are not swept: they name a submodule to monkeypatch a private, and say so.
    root = repository_root()
    found = {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted((root / "src").rglob("*.py"))
        if not path.relative_to(root).as_posix().startswith(f"{PACKAGE}/")
    }
    importers = {where for where, text in found.items() if source.__name__ in text}
    # ⭐ Inhabitation first: a sweep that found no importer would pass on nothing.
    assert SURVEY in importers, sorted(importers)
    assert {where: past_the_surface(found[where]) for where in importers} == dict.fromkeys(
        importers, set()
    )


@pytest.mark.parametrize(
    "planted",
    [
        "from studyforge.validate.source.classification import REPOSITORY_STORE\n",
        "from studyforge.validate.source.enumeration import source_files\n",
        "import studyforge.validate.source.enumeration\n",
        "from studyforge.validate.source import enumeration\n",
    ],
)
def test_W280_a_planted_import_past_all_is_named(planted):
    # ⛔ The split's third clause, run negatively: the same expression that reads the
    # tree clean names these.
    assert past_the_surface(planted), planted


def test_W280_the_store_name_imported_through_the_surface_reads_clean():
    # ⭐ The control for the plants above: the import the survey now makes.
    assert "REPOSITORY_STORE" in source.__all__
    assert past_the_surface("from studyforge.validate.source import REPOSITORY_STORE\n") == set()
