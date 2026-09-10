"""Mirror of `src/studyforge/unit/builder/__init__.py` (R12)."""

from __future__ import annotations

import json

import pytest

import studyforge.unit.builder as builder
from studyforge.unit.builder import NoMaterial, build_unit, render
from studyforge.unit.content import from_document
from tests.studyforge.unit.builder import support
from tests.support import assert_package_contract, repository_root


def test_states_its_contract():
    assert_package_contract(builder, "studyforge.unit.builder")


# --------------------------------------------------------------------------
# ⭐ SF-10's acceptance, end to end
# --------------------------------------------------------------------------


def test_a_unit_with_no_overlay_is_readable(tmp_path):
    directory = support.unit_directory(
        tmp_path / "unit-01", [support.lesson(1), support.practice(1)]
    )
    document = build_unit(directory)
    assert [section["key"] for section in document["sections"]] == ["prose", "practice-prose"]
    assert all(section["blocks"] for section in document["sections"])


def test_an_authored_overlays_section_order_is_preserved_exactly(tmp_path):
    directory = support.unit_directory(
        tmp_path / "unit-01", [support.lesson(1), support.practice(1)]
    )
    written = from_document(
        support.overlay_document(
            [
                support.authored_section("practice", lang="prose", heading="Try"),
                support.authored_section("lang", lang="prose", heading="Read"),
            ]
        ),
        depth=1,
    )
    document = build_unit(directory, overlay=written)
    assert [section["key"] for section in document["sections"]] == ["practice-prose", "prose"]


def test_a_unit_with_no_archive_yields_the_no_material_outcome(tmp_path):
    empty = tmp_path / "unit-01"
    empty.mkdir()
    with pytest.raises(NoMaterial):
        build_unit(empty)


def test_regenerating_from_disk_produces_identical_bytes(tmp_path):
    directory = support.unit_directory(tmp_path / "unit-01", [support.lesson(1)])
    once = render(build_unit(directory))
    assert render(build_unit(directory)) == once


# --------------------------------------------------------------------------
# ⭐ both FND-04 fixtures build
# --------------------------------------------------------------------------


def fixture_units():
    """Every unit directory in the two valid corpora, with its declared count."""
    found = []
    for corpus in ("depth1", "depth2"):
        root = repository_root() / "tests/fixtures" / corpus
        for container in sorted(root.glob("archive/**/container.json")):
            declared = {
                unit["n"]: unit.get("practices")
                for unit in json.loads(container.read_text(encoding="utf-8"))["units"]
            }
            for unit_dir in sorted(container.parent.glob("raw/*/unit-*")):
                found.append((unit_dir, declared.get(int(unit_dir.name.split("-")[1]))))
    return found


def test_every_unit_in_both_valid_fixtures_builds():
    # ⚠️ Ruling 48: the list is asserted to be inhabited, because a glob that
    # matched nothing would satisfy every assertion in the loop.
    units = fixture_units()
    assert len(units) >= 4, "the fixture sweep found no units"
    for directory, declared in units:
        document = build_unit(directory, declared_practices=declared)
        assert document["sections"], directory.name
        assert document["built_from"], directory.name


def test_the_graded_fixture_unit_carries_its_workspace():
    # ⭐ §7's graded state, end to end: the one fixture document with an
    # exercise produces the one served section with a workspace.
    directory = (
        repository_root()
        / "tests/fixtures/depth2/archive/basics/01-getting-started/raw/java/unit-01"
    )
    document = build_unit(directory, declared_practices=1)
    workspaces = [s["workspace"] for s in document["sections"] if s["workspace"]]
    assert len(workspaces) == 1
    assert workspaces[0]["provenance"] == "bundled"


def test_the_ungraded_fixture_unit_carries_no_workspace_and_is_not_short():
    # ⛔ Ungraded is a first-class state (§7, C5), not a gap.
    directory = (
        repository_root()
        / "tests/fixtures/depth2/archive/advanced/02-going-further/raw/java/unit-01"
    )
    document = build_unit(directory)
    assert document["sections"]
    assert all(section["workspace"] is None for section in document["sections"])
