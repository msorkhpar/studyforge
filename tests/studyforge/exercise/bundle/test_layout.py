"""The two roots an authored exercise occupies, and the closed file set (`AX-04`)."""

from __future__ import annotations

import pytest

from studyforge.address import Address
from studyforge.exercise import ExerciseError
from studyforge.exercise.bundle import (
    BUILD,
    BUNDLE_DIRNAMES,
    BUNDLES_DIRNAME,
    RUN_OUTPUT_DIRNAME,
    RUN_OUTPUT_IGNORE,
    Places,
    is_run_output,
    ordinals,
    plant_dirname,
    plant_positions,
    require_inside,
    require_no_gap,
    unpermitted,
)
from studyforge.exercise.cases import Case
from tests.studyforge.exercise.bundle import bundles


def spot() -> Places:
    return Places(Address(["demo"]), "prose", 2, 1)


def test_both_roots_are_derived_from_the_identity_and_share_their_tail():
    where = spot()
    assert where.bundle == f"{BUNDLES_DIRNAME}/demo/prose/unit-02/practice-1"
    assert where.workspace == "practice/demo/prose/unit-02/practice-1"
    assert where.bundle.endswith(where.tail) and where.workspace.endswith(where.tail)


def test_the_bundle_and_the_workspace_never_share_a_file():
    # ⛔ The property the two roots exist for: a reader editing their own file
    # can never move a digest the gate record was taken over.
    where = spot()
    assert not where.in_workspace("bitmap.py").startswith(where.bundle)
    assert not where.in_bundle("starter/bitmap.py").startswith(where.workspace)


def test_the_three_named_files_sit_at_the_top_of_the_bundle():
    where = spot()
    assert where.document == f"{where.bundle}/bundle.json"
    assert where.statement == f"{where.bundle}/statement.md"
    assert where.gates == f"{where.bundle}/gates.json"


def test_each_role_files_its_copy_under_its_own_directory():
    where = spot()
    assert where.role_path("starter", "a/b.py") == "starter/a/b.py"
    assert where.role_path("reference", "a/b.py") == "reference/a/b.py"
    assert where.role_path("tests", "t.py") == "tests/t.py"


def test_a_role_the_shape_does_not_know_is_refused():
    with pytest.raises(ExerciseError, match="and nothing"):
        spot().role_path("plant:test_empty", "b.py")


def test_a_plant_is_filed_by_position_and_never_by_case_id():
    # ⛔ `AX-03/4`: a valid case id permits '/' and ':', so one spelled as a
    # path segment could put a plant outside its own bundle. The position is
    # what reaches the path; the id reaches the gate record's role.
    cases = (
        Case(id="test_main", kind="main", says="the ask"),
        Case(id="a/b:c", kind="edge", says="a case id shaped like a path"),
        Case(id="test_other", kind="edge", says="another"),
    )
    assert plant_positions(cases) == {"a/b:c": 1, "test_other": 2}
    assert plant_dirname(1) == "edge-1"
    assert spot().plant_path(1, "bitmap.py") == "plants/edge-1/bitmap.py"
    assert "a/b:c" not in spot().plant_path(1, "bitmap.py")


def test_ordinals_run_from_one_and_a_gap_is_refused():
    assert ordinals(3) == (1, 2, 3)
    assert require_no_gap((2, 1, 3), "a page") == (1, 2, 3)
    with pytest.raises(ExerciseError, match="no gap and no repeat"):
        require_no_gap((1, 3), "a page")
    with pytest.raises(ExerciseError, match="no gap and no repeat"):
        require_no_gap((1, 1), "a page")


def test_a_path_outside_the_workspace_is_refused_without_quoting_it():
    assert require_inside("practice/x/a.py", "practice/x", "where") == "practice/x/a.py"
    assert require_inside("practice/x", "practice/x", "where") == "practice/x"
    with pytest.raises(ExerciseError) as raised:
        require_inside("practice/other/a.py", "practice/x", "where")
    # ⛔ Neither value is reproduced — not the one refused, and not the root it
    # was compared against.
    assert "practice/other" not in str(raised.value)
    assert "practice/x" not in str(raised.value)


def test_an_absolute_path_is_refused_before_it_is_quoted(tmp_path):
    # ⛔ R7: `require_path` runs first, so the sentence cannot carry a home
    # directory. The shape is assembled at run time rather than written down.
    home = "/" + "/".join(("home", "someone", "secret"))
    with pytest.raises(ExerciseError) as raised:
        require_inside(f"{home}/a.py", "practice/x", "where")
    assert home not in str(raised.value)
    with pytest.raises(ExerciseError) as raised:
        require_inside("a.py", home, "where")
    assert home not in str(raised.value)


def test_a_bundle_that_is_not_there_holds_nothing_unpermitted(tmp_path):
    assert unpermitted(tmp_path, spot()) == ()


def test_a_complete_bundle_holds_only_what_the_shape_permits(tmp_path):
    where = bundles.write_bundle(tmp_path)
    assert unpermitted(tmp_path, where) == ()


def test_a_committed_run_report_is_named(tmp_path):
    # ⛔ `AX-03/1`: a JUnit report carries the machine's hostname, and a corpus
    # repository is where this repository's personal-data gate never looks.
    where = bundles.write_bundle(tmp_path)
    (tmp_path / where.bundle / "report.xml").write_text("<testsuite/>", encoding="utf-8")
    assert unpermitted(tmp_path, where) == ("report.xml",)


def test_a_file_under_an_unknown_directory_is_named(tmp_path):
    where = bundles.write_bundle(tmp_path)
    (tmp_path / where.bundle / "output").mkdir()
    (tmp_path / where.bundle / "output" / "out.xml").write_text("x", encoding="utf-8")
    assert unpermitted(tmp_path, where) == ("output/out.xml",)


# ⭐ `W436`: the build role widened the set by one directory, and `AX-03/1`'s
# reason survives it.


def test_a_bundle_with_a_build_role_holds_only_what_the_shape_permits(tmp_path):
    where = bundles.write_bundle(tmp_path, build=["pom.xml", "gradle/libs.versions.toml"])
    assert (tmp_path / where.bundle / "build" / "gradle" / "libs.versions.toml").is_file()
    assert unpermitted(tmp_path, where) == ()


@pytest.mark.parametrize("role", ["build", "tests", "starter", "plants/edge-1"])
def test_a_run_output_directory_is_refused_under_every_role(tmp_path, role):
    # ⛔ A report a run wrote lands in RUN_OUTPUT_DIRNAME, so a bundle file
    # anywhere under one is a run's output somebody committed.
    where = bundles.write_bundle(tmp_path, build=["pom.xml"])
    planted = tmp_path / where.bundle / role / RUN_OUTPUT_DIRNAME / "TEST-x.xml"
    planted.parent.mkdir(parents=True, exist_ok=True)
    planted.write_text("<testsuite hostname='h'/>", encoding="utf-8")
    assert unpermitted(tmp_path, where) == (f"{role}/{RUN_OUTPUT_DIRNAME}/TEST-x.xml",)


def test_a_run_output_path_is_one_under_the_directory_and_nothing_else():
    assert is_run_output(f"{RUN_OUTPUT_DIRNAME}/r.xml")
    assert is_run_output(f"{RUN_OUTPUT_DIRNAME}/surefire-reports")
    assert not is_run_output("r.xml")
    assert not is_run_output(f"a/{RUN_OUTPUT_DIRNAME}/r.xml")
    assert not is_run_output(f"{RUN_OUTPUT_DIRNAME}x/r.xml")


def test_the_one_ignore_line_names_the_run_output_directory_at_any_depth():
    # ⭐ `ISO-M10/4`: one git pattern, written once — a trailing slash matches a
    # directory of that name at any depth below the ignore file.
    assert RUN_OUTPUT_IGNORE == f"{RUN_OUTPUT_DIRNAME}/"
    assert "/" not in RUN_OUTPUT_IGNORE[:-1]


def test_a_build_file_sits_under_the_build_role_directory():
    assert spot().build_path("pom.xml") == "build/pom.xml"
    assert BUILD in BUNDLE_DIRNAMES
