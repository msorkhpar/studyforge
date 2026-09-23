"""`bundle.json`: what an authored exercise declares about itself (`AX-04`)."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.bundle import (
    BUNDLE_KEYS,
    OPTIONAL_KEYS,
    RUN_OUTPUT_DIRNAME,
    bundle_document,
    bundle_of,
)
from tests.studyforge.exercise.bundle import bundles


def test_a_bundle_document_round_trips_to_the_same_bytes():
    declared = bundles.document()
    read = bundle_of(declared, "bundle.json")
    written = bundle_document(read)
    assert written == declared
    assert list(written) == [key for key in BUNDLE_KEYS if key in written]


def test_the_one_optional_key_is_omitted_when_it_is_not_carried():
    declared = bundles.document()
    del declared["trust"]
    written = bundle_document(bundle_of(declared, "bundle.json"))
    assert "trust" not in written
    assert written == declared


def test_both_roots_are_derived_from_the_document_alone():
    read = bundle_of(bundles.document(), "bundle.json")
    assert read.places.bundle == "exercises/demo/prose/unit-02/practice-1"
    assert read.places.workspace == "practice/demo/prose/unit-02/practice-1"


def test_every_edge_case_is_mapped_to_the_position_its_plant_is_filed_under():
    read = bundle_of(bundles.document(), "bundle.json")
    assert read.plants == {"test_empty": 1}


@pytest.mark.parametrize("key", [key for key in BUNDLE_KEYS if key not in OPTIONAL_KEYS])
def test_a_missing_required_key_is_refused_by_name(key):
    declared = bundles.document()
    del declared[key]
    with pytest.raises(ExerciseError, match="required"):
        bundle_of(declared, "bundle.json")


def test_an_unknown_key_is_refused_rather_than_ignored():
    # ⛔ Tolerating an unknown key is tolerating a typo in a known one, and a
    # typo'd `test_file` is a grader nothing runs while the corpus is green.
    with pytest.raises(ExerciseError, match="does not define"):
        bundle_of(bundles.document(test_fiel="t.py"), "bundle.json")


def test_a_bundle_api_this_build_does_not_read_is_refused():
    with pytest.raises(ExerciseError, match="bundle_api"):
        bundle_of(bundles.document(bundle_api=2), "bundle.json")


def test_a_document_that_is_not_an_object_is_refused():
    with pytest.raises(ExerciseError, match="an object"):
        bundle_of(["not", "an", "object"], "bundle.json")


def test_an_authored_exercise_with_no_origin_is_refused():
    # ⛔ `E14`'s first property: `G5` resolves an origin against the ledger, so
    # an authored exercise with none is material the ledger cannot account for.
    with pytest.raises(ExerciseError, match="source ledger"):
        bundle_of(bundles.document(origin=None), "bundle.json")


@pytest.mark.parametrize("field", ["variant", "title", "lang", "provenance"])
def test_an_empty_text_field_is_refused_by_name(field):
    with pytest.raises(ExerciseError, match=field):
        bundle_of(bundles.document(**{field: "  "}), "bundle.json")


@pytest.mark.parametrize("field", ["unit", "ordinal"])
def test_a_unit_or_an_ordinal_that_does_not_count_from_one_is_refused(field):
    with pytest.raises(ExerciseError, match=field):
        bundle_of(bundles.document(**{field: 0}), "bundle.json")
    with pytest.raises(ExerciseError, match=field):
        bundle_of(bundles.document(**{field: "two"}), "bundle.json")


def test_an_address_that_is_not_an_array_of_slugs_is_refused():
    with pytest.raises(ExerciseError, match="address"):
        bundle_of(bundles.document(address=[]), "bundle.json")
    with pytest.raises(ExerciseError, match="address"):
        bundle_of(bundles.document(address=["Not A Slug"]), "bundle.json")


def test_a_variant_that_could_not_be_a_path_segment_is_refused():
    # ⚠️ The two roots are computed from the identity, so a value that cannot
    # be a path is refused where the field is named rather than at the join.
    with pytest.raises(ExerciseError):
        bundle_of(bundles.document(variant=".."), "bundle.json")


def test_a_workspace_path_that_escapes_is_refused_without_quoting_it():
    home = "/" + "/".join(("home", "someone"))
    with pytest.raises(ExerciseError) as raised:
        bundle_of(bundles.document(main_file=f"{home}/a.py"), "bundle.json")
    assert home not in str(raised.value)
    with pytest.raises(ExerciseError):
        bundle_of(bundles.document(test_file="../elsewhere/t.py"), "bundle.json")


def test_a_report_path_that_escapes_the_workspace_is_refused():
    with pytest.raises(ExerciseError):
        bundle_of(
            bundles.document(report={"format": "junit", "path": "../report.xml"}),
            "bundle.json",
        )


def test_a_command_that_is_a_shell_line_is_refused():
    # ⛔ `safety`'s rule, imported rather than re-spelled: a command is argv.
    with pytest.raises(ExerciseError):
        bundle_of(bundles.document(test_command="pytest; rm -rf ~"), "bundle.json")


# ⭐ `W436`: the build role, and the one report convention.


def test_a_bundle_with_no_build_role_reads_and_writes_exactly_as_before():
    declared = bundles.document()
    assert "build" not in declared
    read = bundle_of(declared, "bundle.json")
    assert read.build == ()
    assert "build" not in bundle_document(read)


def test_a_declared_build_role_round_trips_in_its_place_in_the_key_order():
    declared = bundles.document(build=["pom.xml", "lib/versions.properties"])
    read = bundle_of(declared, "bundle.json")
    assert read.build == ("pom.xml", "lib/versions.properties")
    written = bundle_document(read)
    assert written == declared
    assert list(written) == [key for key in BUNDLE_KEYS if key in written]
    assert list(written).index("build") == list(written).index("test_file") + 1


@pytest.mark.parametrize(
    "build",
    [[], "pom.xml", [""], ["pom.xml", "pom.xml"], ["../pom.xml"], ["-rf"]],
    ids=["empty", "a-string", "blank", "repeated", "escaping", "a-flag"],
)
def test_a_build_role_that_is_not_a_list_of_distinct_workspace_paths_is_refused(build):
    with pytest.raises(ExerciseError):
        bundle_of(bundles.document(build=build), "bundle.json")


def test_an_escaping_build_path_is_refused_without_quoting_it():
    home = "/" + "/".join(("home", "someone"))
    with pytest.raises(ExerciseError) as raised:
        bundle_of(bundles.document(build=[f"{home}/pom.xml"]), "bundle.json")
    assert home not in str(raised.value)


@pytest.mark.parametrize("path", ["bitmap.py", "test_bitmap.py"])
def test_a_build_file_that_is_the_main_or_the_test_file_is_refused(path):
    with pytest.raises(ExerciseError, match="two roles"):
        bundle_of(bundles.document(build=[path]), "bundle.json")


def test_a_build_file_in_the_run_output_directory_is_refused():
    with pytest.raises(ExerciseError, match=RUN_OUTPUT_DIRNAME):
        bundle_of(bundles.document(build=[f"{RUN_OUTPUT_DIRNAME}/pom.xml"]), "bundle.json")


@pytest.mark.parametrize(
    "path",
    ["report.xml", "reports/TEST-x.xml", f"{RUN_OUTPUT_DIRNAME}x/report.xml", "a/target/r.xml"],
)
def test_a_report_outside_the_run_output_directory_is_refused_naming_the_convention(path):
    # ⭐ `ISO-M10/4`: one convention, so a corpus ignores every run's report
    # with one line. Each of these would need a rule of its own.
    with pytest.raises(ExerciseError, match="ISO-M10/4"):
        bundle_of(bundles.document(report={"format": "junit", "path": path}), "bundle.json")


@pytest.mark.parametrize(
    "path", [f"{RUN_OUTPUT_DIRNAME}/report.xml", f"{RUN_OUTPUT_DIRNAME}/surefire-reports"]
)
def test_a_report_file_or_directory_inside_the_run_output_directory_is_read(path):
    read = bundle_of(bundles.document(report={"format": "junit", "path": path}), "bundle.json")
    assert read.report.path == path
