"""Mirror of `src/studyforge/corpus/placement/__init__.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.corpus import placement
from tests.support import assert_package_contract

#: The whole public surface, spelled out. ⚠️ Duplicated from `__all__` on
#: purpose, following SF-01.
PUBLIC_SURFACE = frozenset(
    {
        "ARCHIVE_DIRNAME",
        "ASSETS_DIRNAME",
        "CACHE_IGNORE_LINES",
        "ATTACHMENTS_DIRNAME",
        "AUDIO_DIRNAME",
        "CONTAINER_SUFFIX",
        "GENERATED_IGNORE_HOME",
        "GENERATED_ROOT",
        "IDENTITY_API",
        "IDENTITY_ELEMENT_ID",
        "IDENTITY_KEYS",
        "IGNORE_FILENAME",
        "IMAGES_DIRNAME",
        "KINDS",
        "KNOWN_IDENTITY_API",
        "PRACTICE_DIRNAME",
        "RAW_DIRNAME",
        "ROOT_INDEX_FILENAME",
        "SELF_IGNORE_LINE",
        "SIBLING",
        "SITE_CACHE_FILENAME",
        "STAGING_SUFFIX",
        "STUDY_DIRNAME",
        "TREE",
        "UNITS_DIRNAME",
        "UNIT_MEDIA_DIRNAMES",
        "UNIT_SUFFIX",
        "VIDEO_DIRNAME",
        "ContainerLocations",
        "CorpusLocations",
        "Identity",
        "IgnoreFile",
        "PlacementError",
        "Profile",
        "SiblingProfile",
        "TreeProfile",
        "UnitLocations",
        "cache_ignore_lines",
        "container_page_name",
        "identity",
        "is_container_page",
        "is_unit_page",
        "label_of",
        "origin_directory",
        "profile_for",
        "register",
        "registered",
        "relative_href",
        "unit_page_name",
        "unit_stem",
    }
)

#: Modules that would let this package touch a disk. ⛔ It answers "where would
#: this go"; whether anything is there is SF-04's question, and `studyforge
#: plan` exists because the answer is computable before a file is written.
FILESYSTEM_MODULES = frozenset({"os", "shutil", "glob", "tempfile", "fileinput", "zipfile"})


def package_modules():
    return sorted(Path(placement.__file__).parent.glob("*.py"))


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
    assert_package_contract(placement, "studyforge.corpus.placement")


def test_the_public_surface_is_exactly_what_the_contract_says():
    assert set(placement.__all__) == PUBLIC_SURFACE
    missing = sorted(name for name in PUBLIC_SURFACE if not hasattr(placement, name))
    assert missing == [], "exported but absent: " + ", ".join(missing)


@pytest.mark.parametrize("name", sorted(PUBLIC_SURFACE))
def test_every_exported_name_is_reachable_from_the_package(name):
    assert getattr(placement, name) is not None


def test_the_package_never_touches_a_filesystem():
    # ⛔ `PurePosixPath` is a pure path object and never opens anything; the
    # check is on the IMPORT, because an import is what makes the capability
    # reachable at all.
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        for name in sorted(imported_names(path))
        if name.split(".")[0] in FILESYSTEM_MODULES
    ]
    assert offenders == [], "placement reaches the filesystem: " + ", ".join(offenders)


def test_the_package_imports_nothing_outside_the_standard_library_and_itself():
    allowed = {"studyforge", "dataclasses", "json", "pathlib", "re", "__future__"}
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        for name in sorted(imported_names(path))
        if name.split(".")[0] not in allowed
    ]
    assert offenders == [], "unexpected import: " + ", ".join(offenders)


def test_the_package_knows_no_source():
    # ⛔ R1. Placement is the most tempting place to hardcode one — a corpus's
    # directory names are right there in front of you.
    tokens = ("codesignal", "jpos", "iso8583", "sparql", "readme")
    offenders = []
    for path in package_modules():
        for node in ast.walk(ast.parse(path.read_text("utf-8"))):
            name = getattr(node, "name", None) or getattr(node, "id", None)
            if isinstance(name, str):
                offenders += [
                    f"{path.name}: {name}"
                    for token in tokens
                    if token in name.lower().replace("_", "")
                ]
    assert offenders == [], "a source is named in placement code: " + ", ".join(offenders)


def test_the_worked_example_in_the_contract_is_the_api_that_exists():
    address = Address.of("basics", "16-streams-api")
    where = placement.profile_for("sibling").unit(
        address, 7, "Streams", origin="16-streams-api/README_4.4.1.md"
    )
    assert str(where.page) == (
        "16-streams-api/study/basics.16-streams-api.unit-07-streams.unit.html"
    )
    # ⭐ The href is relative to the page and starts at the kind directory
    # `study/` holds: the page and its media share one `study/` parent.
    assert where.href("audio", "07.mp3").endswith("/07.mp3")
    assert where.href("audio", "07.mp3").startswith("audio/")
