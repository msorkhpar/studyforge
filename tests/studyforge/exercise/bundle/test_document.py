"""`bundle.json`: what an authored exercise declares about itself (`AX-04`)."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.bundle import BUNDLE_KEYS, bundle_document, bundle_of
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


@pytest.mark.parametrize("key", [key for key in BUNDLE_KEYS if key != "trust"])
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
