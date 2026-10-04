"""Mirror of `exercise/bundle/plantfiles.py` (R12): a plant that may change any edited file."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.bundle import PlantSpec, Replacement, materialise_files, materialised_files

REFERENCES = {"main.py": "x = 1\n", "settings.json": '{"on": true}\n'}
WHERE = "here"


def test_a_replacement_changes_the_file_it_names_and_leaves_the_rest_as_the_reference_has_them():
    spec = PlantSpec((Replacement("settings.json", "true", "false"),))
    made = materialise_files(REFERENCES, spec, WHERE)
    assert made["settings.json"] == '{"on": false}\n' and made["main.py"] == REFERENCES["main.py"]


def test_a_file_the_reader_does_not_edit_and_a_plant_that_changes_nothing_are_refused():
    with pytest.raises(ExerciseError):
        materialise_files(REFERENCES, PlantSpec((Replacement("other.md", "a", "b"),)), WHERE)
    with pytest.raises(ExerciseError):
        materialise_files(REFERENCES, PlantSpec(()), WHERE)


def test_every_plant_is_answered_by_case_and_a_full_plant_is_the_main_file_alone():
    spec = PlantSpec((Replacement("settings.json", "true", "false"),))
    full, specs = materialised_files(
        {"case-a": spec, "case-b": "x = 2\n"}, REFERENCES, "main.py",
        {"case-a": 1, "case-b": 2}, WHERE,
    )
    assert full["case-a"]["settings.json"] == '{"on": false}\n'
    assert full["case-b"] == {"main.py": "x = 2\n", "settings.json": REFERENCES["settings.json"]}
    assert set(specs) == {"case-a"}
