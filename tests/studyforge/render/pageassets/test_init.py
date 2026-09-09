"""Mirror of `src/studyforge/render/pageassets/__init__.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.render import pageassets
from tests.support import assert_package_contract

#: The whole public surface, spelled out. ⚠️ Duplicated from `__all__` on
#: purpose, following SF-01: a test that read `__all__` and then asserted the
#: names in it exist would pass whatever the module happened to export.
PUBLIC_SURFACE = frozenset(
    {
        "ASSET_DIR",
        "HEADER_CHARS",
        "HEADER_MARKERS",
        "JOIN",
        "LICENCE_SUFFIX",
        "PART_SUFFIXES",
        "SCRIPT_NAME",
        "SCRIPT_PARTS",
        "SPRITE_PART",
        "SPRITE_PLACEHOLDER",
        "STYLESHEET_NAME",
        "STYLE_PARTS",
        "SURFACE_CLASSES",
        "SURFACE_HOOKS",
        "VENDORED",
        "AssetError",
        "class_for",
        "compose",
        "header_of",
        "is_vendored",
        "licence_for",
        "licence_names",
        "names",
        "script",
        "stylesheet",
        "text",
        "written_files",
    }
)


def package_modules():
    return sorted(Path(pageassets.__file__).parent.glob("*.py"))


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
    assert_package_contract(pageassets, "studyforge.render.pageassets")


def test_the_public_surface_is_exactly_what_the_contract_says():
    assert set(pageassets.__all__) == PUBLIC_SURFACE
    missing = sorted(name for name in PUBLIC_SURFACE if not hasattr(pageassets, name))
    assert missing == [], "exported but absent: " + ", ".join(missing)


@pytest.mark.parametrize("name", sorted(PUBLIC_SURFACE))
def test_every_exported_name_is_reachable_from_the_package(name):
    assert getattr(pageassets, name) is not None


def test_the_package_imports_nothing_outside_the_standard_library_and_itself():
    allowed = {"studyforge", "pathlib", "__future__"}
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        for name in sorted(imported_names(path))
        if name.split(".")[0] not in allowed
    ]
    assert offenders == [], "unexpected import: " + ", ".join(offenders)


#: ⭐ **The one exception, and it narrows the rule rather than widening it.**
#: `archive.blocks` is the *block vocabulary* — not a corpus, not a document,
#: not anything a source wrote. A class name exists to style a block type, so
#: a surface that did not know the block types is precisely how the two came
#: to disagree silently in the first place; `surface.py` takes its keys from
#: there and answers for every type either way (CTO round 12).
#: ⛔ Nothing else under `studyforge.archive` is allowed: `archive.document`
#: **is** content-shaped, and an asset reaching for it would be the failure
#: this test exists to catch.
VOCABULARY = "studyforge.archive.blocks"


def test_the_assets_know_nothing_about_a_corpus():
    # ⛔ R1 at this package's own boundary. A stylesheet that had to be told
    # which corpus it was for would be exactly the source knowledge the
    # framework may not hold — and the import is where that would arrive.
    forbidden = ("studyforge.corpus", "studyforge.unit", "studyforge.archive", "studyforge.address")
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        for name in sorted(imported_names(path))
        if name.startswith(forbidden) and name != VOCABULARY
    ]
    assert offenders == [], "the page assets reached for content: " + ", ".join(offenders)


def test_the_vocabulary_is_the_only_thing_the_assets_may_reach_for():
    # ⚠️ Pins the exception so it cannot quietly become a doorway: the check
    # above compares on equality, not on a prefix, so `archive.document` and
    # `archive.markdown` are still refused.
    assert VOCABULARY.startswith("studyforge.archive")
    reached = {
        name
        for path in package_modules()
        for name in imported_names(path)
        if name.startswith("studyforge.archive")
    }
    assert reached == {VOCABULARY}


def test_the_worked_example_in_the_contract_is_the_api_that_exists():
    # ⚠️ A contract carrying a call that no longer exists is worse than none,
    # because it is believed.
    written = pageassets.written_files()
    assert set(written) == {"page.css", "page.js"}
    assert all(isinstance(body, str) and body for body in written.values())
