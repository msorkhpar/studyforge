"""Mirror of `src/studyforge/corpus/manifest/__init__.py` (R12).

What lives here is the package as a whole: its contract, its public surface,
and the property that makes the surface worth having — that nothing downstream
ever needs to reach past `__init__` into a module.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.corpus import manifest
from tests.support import assert_package_contract

#: The whole public surface, spelled out. ⚠️ Duplicated from `__all__` on
#: purpose, following SF-01: a test that read `__all__` and then asserted the
#: names in it exist would pass whatever the module happened to export, which
#: is not a contract.
PUBLIC_SURFACE = frozenset(
    {
        "COMMIT_MODES",
        "CORPUS_API",
        "DEFAULT_MEDIA",
        "EDIT_KINDS",
        "KNOWN_CORPUS_API",
        "MANIFEST_FILENAME",
        "MANIFEST_KEYS",
        "MIN_WHY_CHARS",
        "PLACEMENT_PROFILES",
        "REQUIRED_KEYS",
        "Classification",
        "ContentPolicy",
        "Exclusion",
        "Manifest",
        "ManifestError",
        "MediaPolicy",
        "PermittedEdit",
        "Reversal",
        "from_document",
        "load",
        "parse",
        "parse_content",
        "parse_edits",
        "parse_media",
    }
)

#: ⛔ The one module in the package that may touch a filesystem, and only in
#: `load`. Everything a test needs to say about a manifest can be said about
#: its text, which is what keeps this package's own tests free of temporary
#: directories.
FILESYSTEM_MODULES = frozenset({"os", "shutil", "glob", "tempfile", "fileinput", "zipfile"})

MAY_READ_FILES = frozenset({"document.py"})


def package_modules() -> list[Path]:
    return sorted(Path(manifest.__file__).parent.glob("*.py"))


def imported_names(path: Path) -> set[str]:
    """Every module name `path` imports, top-level or inside a function."""
    tree = ast.parse(path.read_text("utf-8"), filename=path.name)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module)
    return names


def test_states_its_contract():
    assert_package_contract(manifest, "studyforge.corpus.manifest")


def test_the_public_surface_is_exactly_what_the_contract_says():
    assert set(manifest.__all__) == PUBLIC_SURFACE
    missing = sorted(name for name in PUBLIC_SURFACE if not hasattr(manifest, name))
    assert missing == [], "exported but absent: " + ", ".join(missing)


@pytest.mark.parametrize("name", sorted(PUBLIC_SURFACE))
def test_every_exported_name_is_reachable_from_the_package(name):
    # ⛔ The point of `__init__.py` being the contract: nothing downstream
    # should ever need `from studyforge.corpus.manifest.document import ...`.
    assert getattr(manifest, name) is not None


def test_only_the_document_module_reaches_a_filesystem():
    # ⭐ `parse` does no I/O and `load` is four lines on top of it. A
    # classification, a media policy and a declared edit are all decided from
    # the document, so a test of any of them needs no disk — and a module that
    # grew a read would make that quietly untrue.
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        if path.name not in MAY_READ_FILES
        for name in sorted(imported_names(path))
        if name.split(".")[0] in FILESYSTEM_MODULES
    ]
    assert offenders == [], "the manifest reaches the filesystem: " + ", ".join(offenders)


def test_the_package_imports_nothing_outside_the_standard_library_and_itself():
    allowed_roots = {"studyforge", "dataclasses", "enum", "json", "pathlib", "re", "__future__"}
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        for name in sorted(imported_names(path))
        if name.split(".")[0] not in allowed_roots
    ]
    assert offenders == [], "unexpected import: " + ", ".join(offenders)


def test_the_worked_example_in_the_contract_is_the_api_that_exists():
    # ⚠️ A contract carrying a call that no longer exists is worse than none,
    # because it is believed. Each of these is the line `__init__.py` shows.
    built = manifest.parse(
        '{"corpus_api": 1, "source": "example", "title": "Example",'
        ' "levels": ["section", "module"], "variants": ["java"],'
        ' "exercises": true, "placement": "tree",'
        ' "content": {"include": ["*/*/README*.md"], "exclude": []}}'
    )
    assert built.depth == 2
    assert built.parse_key("basics/01-intro").key == "basics/01-intro"
    assert built.media.commits is True
    assert built.allows_edit_to("pom.xml") is False
