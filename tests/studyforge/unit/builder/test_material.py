"""Mirror of `src/studyforge/unit/builder/material.py` (R12)."""

from __future__ import annotations

import json

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.unit.builder.material import KIND_ORDER, Material, NoMaterial, of, read
from studyforge.unit.errors import ContentError
from tests.studyforge.unit.builder import support

# --------------------------------------------------------------------------
# ⭐ no material is an answer, not a failure
# --------------------------------------------------------------------------


def test_a_unit_nobody_has_ingested_is_a_named_outcome(tmp_path):
    # ⛔ A named outcome, and never an empty document: a unit that renders as
    # "lesson, then the end" is a page that lies by omission.
    empty = tmp_path / "unit-01"
    empty.mkdir()
    with pytest.raises(NoMaterial):
        read(empty)


def test_no_material_is_catchable_apart_from_every_other_refusal(tmp_path):
    # ⭐ A caller walking a whole corpus skips these and reports the rest, so
    # it must be a *distinct* type — and still a ContentError, so a caller that
    # only wants "this unit did not build" catches one family.
    assert issubclass(NoMaterial, ContentError)


# --------------------------------------------------------------------------
# ⛔ order comes from the record, never from the filename
# --------------------------------------------------------------------------


def test_lessons_come_before_practices(tmp_path):
    material = of([support.practice(1), support.lesson(1)], "unit-01")
    assert [d["kind"] for d in material.documents] == ["lesson", "practice"]


def test_each_kind_is_in_its_own_ordinal_order(tmp_path):
    material = of([support.lesson(3), support.lesson(1), support.lesson(2)], "unit-01")
    assert [d["ordinal"] for d in material.documents] == [1, 2, 3]


def test_a_misleading_filename_does_not_change_the_order(tmp_path):
    # ⛔ §6 arriving somewhere unexpected: the document records its own kind
    # and ordinal, and the record is the answer. ⚠️ Whether the *name* agrees
    # with the record is a different question with a different consumer, and
    # `studyforge validate` already asks it — see finding-free note in the
    # module docstring on what this module does not assert.
    directory = tmp_path / "unit-01"
    directory.mkdir()
    for document, name in ((support.lesson(1), "lesson-9.json"), (support.practice(1), "a.json")):
        (directory / name).write_text(json.dumps(document, indent=2), encoding="utf-8")
    material = read(directory)
    assert [d["kind"] for d in material.documents] == ["lesson", "practice"]


def test_the_kind_order_is_inhabited_and_is_the_reading_order():
    # ⚠️ The denominator: the tuple is asserted to have members, not only to be a
    # subset of something — an empty KIND_ORDER would satisfy a membership test
    # and order nothing.
    assert KIND_ORDER == ("lesson", "practice")
    assert len(KIND_ORDER) == 2


# --------------------------------------------------------------------------
# ⛔ documents that do not belong together are refused
# --------------------------------------------------------------------------


@pytest.mark.parametrize("field,value", [("unit", 2), ("variant", "kotlin"), ("source", "other")])
def test_documents_from_two_units_are_refused(field, value):
    # ⛔ Nothing downstream could notice this: both halves are individually
    # valid, and joined they make one page out of two units' work.
    second = support.lesson(2)
    second[field] = value
    with pytest.raises(ContentError, match="one unit's material"):
        of([support.lesson(1), second], "unit-01")


def test_two_documents_of_one_kind_claiming_one_ordinal_are_refused():
    # ⛔ Silently lossy: one would be ordered arbitrarily against the other and
    # a reader would see whichever the sort happened to put first.
    with pytest.raises(ContentError, match="both record ordinal"):
        of([support.lesson(1), support.lesson(1)], "unit-01")


def test_a_document_of_an_unknown_kind_is_refused():
    odd = support.lesson(1)
    odd["kind"] = "appendix"
    with pytest.raises(ContentError, match="kind must be one of"):
        of([odd], "unit-01")


# --------------------------------------------------------------------------
# ⛔ the gate runs here, by delegation
# --------------------------------------------------------------------------


def test_a_document_carrying_personal_data_is_refused_on_the_way_in(tmp_path):
    # ⛔ Reading a file off disk is a trust boundary. ⭐ Asserted by
    # delegation — `archive.document.load` owns R7 and this module adds no
    # second spelling of it.
    directory = tmp_path / "unit-01"
    directory.mkdir()
    poison = support.lesson(1)
    separator = "/"
    poison["blocks"] = [{"type": "para", "text": f"{separator}home{separator}jane{separator}x"}]
    (directory / "lesson-1.json").write_text(json.dumps(poison, indent=2), encoding="utf-8")
    with pytest.raises(PersonalDataLeak):
        read(directory)


def test_a_personal_data_refusal_is_not_catchable_as_this_unit_did_not_build():
    # ⭐ **The half that matters more than the refusal.** A caller walking a
    # corpus catches `ContentError` per unit and reports the rest; if an R7
    # refusal were in that family it would be logged as one more unit that did
    # not build, and the run would finish green-ish. ⛔ It is not, so it stops.
    assert not issubclass(PersonalDataLeak, ContentError)


def test_a_document_off_contract_is_refused_as_this_packages_error(tmp_path):
    # ⚠️ Re-typed, not re-worded: the archive owns the sentence, this package
    # owns the family a caller catches.
    directory = tmp_path / "unit-01"
    directory.mkdir()
    (directory / "lesson-1.json").write_text('{"raw_api": 99}', encoding="utf-8")
    with pytest.raises(ContentError):
        read(directory)


def test_the_material_reports_what_it_holds():
    material = of([support.lesson(1), support.practice(1), support.practice(2)], "unit-01")
    assert isinstance(material, Material)
    assert material.variant == "prose"
    assert material.unit == 1
    assert material.archived_practices == 2
    assert len(material.of_kind("lesson")) == 1
