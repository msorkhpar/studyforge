"""Mirror of `src/studyforge/unit/__init__.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge import unit
from tests.support import assert_package_contract

PUBLIC_SURFACE = frozenset(
    {
        "CONTENT_API",
        "CONTENT_FILENAME",
        "DEFAULT_TRUST",
        "DERIVED_FIELDS",
        "FORBIDDEN",
        "KINDS_WITH_A_LANG",
        "KIND_OF",
        "KNOWN_CONTENT_API",
        "OVERLAY_KEYS",
        "PRACTICE_PREFIX",
        "PROVENANCE",
        "SECTION_FIELDS",
        "SECTION_KINDS",
        "SHARED_KEY",
        "TRUST",
        "ContentError",
        "Overlay",
        "Section",
        "check_test_record",
        "derived_section_key",
        "from_document",
        "load",
        "parse",
        "section_key",
    }
)


def package_modules():
    return sorted(Path(unit.__file__).parent.glob("*.py"))


def imported_names(path):
    tree = ast.parse(path.read_text("utf-8"), filename=path.name)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module)
    return names


def test_states_its_contract():
    assert_package_contract(unit, "studyforge.unit")


def test_the_public_surface_is_exactly_what_the_contract_says():
    assert set(unit.__all__) == PUBLIC_SURFACE
    missing = sorted(name for name in PUBLIC_SURFACE if not hasattr(unit, name))
    assert missing == [], "exported but absent: " + ", ".join(missing)


@pytest.mark.parametrize("name", sorted(PUBLIC_SURFACE))
def test_every_exported_name_is_reachable_from_the_package(name):
    assert getattr(unit, name) is not None


def test_the_package_imports_nothing_outside_the_standard_library_and_itself():
    allowed = {"studyforge", "dataclasses", "json", "pathlib", "__future__"}
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        for name in sorted(imported_names(path))
        if name.split(".")[0] not in allowed
    ]
    assert offenders == [], "unexpected import: " + ", ".join(offenders)


def test_the_package_does_not_reach_for_a_renderer():
    # ⛔ This package decides WHAT a unit is; the renderer decides what it
    # looks like. That split is what lets one unit document serve a page, a
    # contents entry and a narration script without three ideas of the content.
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        for name in sorted(imported_names(path))
        if name.startswith(("studyforge.render", "studyforge.serve", "studyforge.narrate"))
    ]
    assert offenders == [], "the unit package reached for a view: " + ", ".join(offenders)


def test_the_block_vocabulary_is_imported_and_never_restated():
    # ⭐ SF-06 consolidated four copies of the block-type list into one table.
    # This package is a fifth consumer and imports it.
    body = (Path(unit.__file__).parent / "content.py").read_text("utf-8")
    assert "from studyforge.archive.blocks import BLOCK_FIELDS" in body


def test_the_version_gate_is_imported_and_never_reimplemented():
    # ⚠️ SF-33 ships a tree test that fails any module rolling its own
    # membership check; this states the same expectation locally.
    body = (Path(unit.__file__).parent / "content.py").read_text("utf-8")
    assert "from studyforge.version import check" in body


def test_the_contract_names_the_three_things_r21_requires():
    # ⛔ R21: a document states the file it lives in, the key that versions it,
    # and the one producer that writes it — before any task builds against it.
    contract = unit.__doc__ or ""
    assert "content.json" in contract
    assert "content_api" in contract
    assert "person" in contract
