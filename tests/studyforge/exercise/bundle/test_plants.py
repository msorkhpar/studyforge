"""Mirror of `src/studyforge/exercise/bundle/plants.py`: a plant written as replacements.

⭐ Every refusal is exercised, and each is checked to name the plant and the replacement
by position and to reproduce none of the text it was given (R7).
"""

from __future__ import annotations

import json

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.bundle import (
    PlantSpec,
    Replacement,
    bundle_of,
    emit,
    materialise,
    read_plant,
    spec_bytes,
    spec_file,
    spec_of,
)
from tests.studyforge.exercise.bundle import bundles

MAIN = "bitmap.py"
REFERENCE = (
    "def build(fields):\n    total = 0\n    for n in fields:\n"
    "        total += 1 << (64 - n)\n    return total\n"
)
SECRET = "SECRET_TEXT_THAT_MUST_NOT_BE_ECHOED"


def one(old, new, file=MAIN):
    return PlantSpec((Replacement(file, old, new),))


def test_a_spec_materialises_into_the_reference_with_the_replacement_applied():
    text = materialise(REFERENCE, one("total += 1 << (64 - n)", "total += 1"), MAIN, "w")
    assert text == REFERENCE.replace("total += 1 << (64 - n)", "total += 1")


def test_replacements_apply_in_order_each_to_the_text_the_last_left():
    spec = PlantSpec(
        (
            Replacement(MAIN, "total = 0", "total = 5"),
            Replacement(MAIN, "total = 5", "total = 6"),
        )
    )
    assert "total = 6" in materialise(REFERENCE, spec, MAIN, "w")


def test_materialising_writes_nothing_and_leaves_the_reference_alone(tmp_path):
    materialise(REFERENCE, one("return total", "return 0"), MAIN, "w")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("spec", "words"),
    [
        (one("not in the reference " + SECRET, "x"), "not there"),
        (one("total", "t"), "3 times"),
        (one(SECRET, "x"), "not there"),
        (one("", "x"), "no text to find"),
        (one("return total", "return total"), "puts back"),
        (one("return total", "x", file="other.py"), "other than"),
    ],
)
def test_a_replacement_that_cannot_apply_is_refused_by_position_without_echoing(spec, words):
    with pytest.raises(ExerciseError) as refused:
        materialise(REFERENCE, spec, MAIN, "ex: the plant for edge case 2")
    message = str(refused.value)
    assert "edge case 2" in message and "replacement 1" in message and words in message
    assert SECRET not in message and "other.py" not in message


def test_a_second_replacement_is_named_by_its_own_position():
    spec = PlantSpec((Replacement(MAIN, "total = 0", "total = 1"), Replacement(MAIN, "nope", "x")))
    with pytest.raises(ExerciseError, match="replacement 2"):
        materialise(REFERENCE, spec, MAIN, "w")


def test_a_plant_that_comes_out_identical_to_the_reference_is_refused():
    spec = PlantSpec(
        (Replacement(MAIN, "total = 0", "total = 1"), Replacement(MAIN, "total = 1", "total = 0"))
    )
    with pytest.raises(ExerciseError, match="identical to the reference"):
        materialise(REFERENCE, spec, MAIN, "w")


def test_the_spec_file_round_trips_and_is_the_bytes_the_bundle_holds():
    spec = one("return total", "return 0")
    data = spec_bytes(spec)
    assert data.endswith(b"\n") and json.loads(data)["plant_version"] == 1
    assert spec_of(json.loads(data), "w") == spec
    assert spec_file(MAIN) == "bitmap.py.plant.json"


@pytest.mark.parametrize(
    "document",
    [
        [],
        {"plant_version": 1},
        {"plant_version": 2, "replacements": []},
        {"plant_version": True, "replacements": [{"file": MAIN, "old": "a", "new": "b"}]},
        {"plant_version": 1, "replacements": []},
        {"plant_version": 1, "replacements": "x"},
        {"plant_version": 1, "replacements": [{"file": MAIN, "old": "a"}]},
        {"plant_version": 1, "replacements": [{"file": MAIN, "old": "a", "new": 3}]},
        {"plant_version": 1, "replacements": [{"file": MAIN, "old": "a", "new": "b", "x": 1}]},
        {"plant_version": 1, "replacements": [{"file": MAIN, "old": "a", "new": "b"}], "x": 1},
    ],
)
def test_a_spec_file_with_the_wrong_shape_is_refused(document):
    with pytest.raises(ExerciseError):
        spec_of(document, "w")


def test_a_valid_spec_file_is_read():
    document = {"plant_version": 1, "replacements": [{"file": MAIN, "old": "a", "new": "b"}]}
    assert spec_of(document, "w") == one("a", "b")


def _bundle_on_disk(root):
    bundles.write_bundle(root)
    bundle = bundle_of(bundles.document(), "bundle.json")
    base = root / bundle.places.bundle
    return bundle, base, base / "plants" / "edge-1"


def test_read_plant_reads_a_full_plant_as_it_always_did(tmp_path):
    bundle, _, _ = _bundle_on_disk(tmp_path)
    assert read_plant(tmp_path, bundle, 1, bundles.REFERENCE, "w") == bundles.PLANT


def test_read_plant_materialises_a_spec_plant(tmp_path):
    bundle, _, plant = _bundle_on_disk(tmp_path)
    (plant / bundle.main_file).unlink()
    spec = one("return sum(1 << (64 - n) for n in fields)", "return 1", bundle.main_file)
    (plant / spec_file(bundle.main_file)).write_bytes(spec_bytes(spec))
    text = read_plant(tmp_path, bundle, 1, bundles.REFERENCE, "w")
    assert text == "def build(fields):\n    return 1\n"


def test_read_plant_refuses_both_files_and_neither(tmp_path):
    bundle, _, plant = _bundle_on_disk(tmp_path)
    spec = one("return", "return 1 +", bundle.main_file)
    (plant / spec_file(bundle.main_file)).write_bytes(spec_bytes(spec))
    with pytest.raises(ExerciseError, match="both"):
        read_plant(tmp_path, bundle, 1, bundles.REFERENCE, "w")
    (plant / spec_file(bundle.main_file)).unlink()
    (plant / bundle.main_file).unlink()
    with pytest.raises(ExerciseError, match="neither"):
        read_plant(tmp_path, bundle, 1, bundles.REFERENCE, "w")


def test_read_plant_refuses_a_spec_file_that_is_not_json(tmp_path):
    bundle, _, plant = _bundle_on_disk(tmp_path)
    (plant / bundle.main_file).unlink()
    (plant / spec_file(bundle.main_file)).write_text("not json", encoding="utf-8")
    with pytest.raises(ExerciseError, match="edge case 1"):
        read_plant(tmp_path, bundle, 1, bundles.REFERENCE, "w")


def test_emit_accepts_a_bundle_whose_plant_is_a_spec(tmp_path):
    bundle, _, plant = _bundle_on_disk(tmp_path)
    (plant / bundle.main_file).unlink()
    spec = one("return sum(1 << (64 - n) for n in fields)", "return 1", bundle.main_file)
    (plant / spec_file(bundle.main_file)).write_bytes(spec_bytes(spec))
    emit(tmp_path, bundle, source="demo", ingested="2026-01-05")


def test_emit_refuses_a_plant_filed_both_ways_and_one_not_filed(tmp_path):
    bundle, _, plant = _bundle_on_disk(tmp_path)
    (plant / spec_file(bundle.main_file)).write_bytes(spec_bytes(one("a", "b", bundle.main_file)))
    with pytest.raises(ExerciseError, match="filed twice"):
        emit(tmp_path, bundle, source="demo", ingested="2026-01-05")
    (plant / spec_file(bundle.main_file)).unlink()
    (plant / bundle.main_file).unlink()
    with pytest.raises(ExerciseError, match="edge case 1"):
        emit(tmp_path, bundle, source="demo", ingested="2026-01-05")


def test_a_text_that_repeats_itself_overlapping_is_read_as_two_places_not_one():
    text = "a\nb\na\nb\na\n"
    with pytest.raises(ExerciseError, match="2 times"):
        materialise(text + "tail\n", one("a\nb\na\n", "x\n"), MAIN, "w")
