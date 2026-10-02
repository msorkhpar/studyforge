"""Mirror of `src/studyforge/corpus/manifest/__init__.py` (R12).

What lives here is the package as a whole: its contract, its public surface,
and the property that makes the surface worth having — that nothing downstream
ever needs to reach past `__init__` into a module.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from studyforge.address import AddressError
from studyforge.corpus import manifest
from tests.support import assert_package_contract

#: The whole public surface, spelled out. ⚠️ Duplicated from `__all__` on
#: purpose, following the address package: a test that read `__all__` and then asserted the
#: names in it exist would pass whatever the module happened to export, which
#: is not a contract.
PUBLIC_SURFACE = frozenset(
    {
        "COMMIT_MODES",
        "CORPUS_API",
        "DEFAULT_MEDIA",
        "EDIT_KINDS",
        "KEY_VERSIONS",
        "KNOWN_CORPUS_API",
        "MANIFEST_FILENAME",
        "MANIFEST_KEYS",
        "MIN_WHY_CHARS",
        "NO_RUNTIMES",
        "OUTSIDE_MODES",
        "ONBOARDING_DOC",
        "PLACEMENT_PROFILES",
        "RAISES",
        "REQUIRED_KEYS",
        "REQUIRES_JAVA",
        "RUNTIMES",
        "SOURCE_SUFFIXES",
        "Classification",
        "ContentPolicy",
        "Curriculum",
        "DeclaredContainer",
        "Exclusion",
        "Language",
        "Manifest",
        "ManifestError",
        "MediaPolicy",
        "Mode",
        "NotMaterial",
        "PermittedEdit",
        "Reading",
        "Reversal",
        "all_link_suffixes",
        "from_document",
        "link_suffixes",
        "load",
        "parse",
        "parse_content",
        "parse_curriculum",
        "parse_edits",
        "parse_media",
        "parse_reading",
        "parse_runtimes",
        "source_suffixes",
        "prefix_of",
        "versions_needed",
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
    # ⚠️ A contract carrying a call that does not exist is worse than none,
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


# --------------------------------------------------------------------------
# `RAISES` — the tuple a caller catches
# --------------------------------------------------------------------------

#: ⛔ Assembled rather than written whole, so this file needs no exception from
#: the repository's own personal-data sweep (R7). Nothing here is real.
HOME = "/" + "home/jane"

VALID = {
    "corpus_api": 1,
    "source": "demo",
    "title": "Demo",
    "levels": ["section"],
    "variants": ["prose"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["**/*.md"]},
}

#: ⛔ One document per member, so the tuple is measured against what `parse`
#: does rather than against the paragraph in `errors.py`.
REACHES = {
    "ManifestError": {**VALID, "placement": "nowhere"},
    "PersonalDataLeak": {**VALID, "title": f"notes from {HOME}/corpus"},
}


def test_the_tuple_is_the_reader_s_own_error_and_the_r7_pass_through():
    assert [error.__name__ for error in manifest.RAISES] == ["ManifestError", "PersonalDataLeak"]


@pytest.mark.parametrize("name", sorted(REACHES))
def test_every_member_is_reachable_from_parse(name):
    wanted = {error.__name__: error for error in manifest.RAISES}[name]
    with pytest.raises(wanted):
        manifest.parse(json.dumps(REACHES[name]))


def test_the_population_is_not_silently_narrower_than_the_tuple():
    assert sorted(REACHES) == sorted(error.__name__ for error in manifest.RAISES)


def test_address_error_is_not_a_member_because_parse_translates_it():
    # ⚠️ **The property**: a non-slug
    # `source` is the address package's refusal, re-raised as `ManifestError` in `slug_of`.
    # `parse_key` is the one call that lets `AddressError` out, and no reader
    # makes it — if that ever moves, this fails before a command crashes.
    with pytest.raises(manifest.ManifestError):
        manifest.parse(json.dumps({**VALID, "source": "Not A Slug"}))
    built = manifest.parse(json.dumps(VALID))
    with pytest.raises(AddressError):
        built.parse_key("a/b")


#: Values of every wrong JSON type, plus one slug-shaped and one leaking string.
WRONG = [None, 0, True, 1.5, "", "Not A Slug", [], [1], {}, {"a": 1}, f"{HOME}/x"]


def test_nothing_outside_the_tuple_escapes_parse_for_any_key_of_any_type():
    # ⭐ The other direction, over a population rather than one case per
    # member: every top-level key replaced by every wrong type. ⛔ The count is
    # asserted so a sweep that iterated nothing could not pass.
    cases = 0
    for key in manifest.MANIFEST_KEYS:
        for value in WRONG:
            cases += 1
            try:
                manifest.parse(json.dumps({**VALID, key: value}))
            except manifest.RAISES:
                continue
    assert cases == len(manifest.MANIFEST_KEYS) * len(WRONG) > 0
