"""A plant written as replacements is gated exactly as the equivalent full plant is.

⭐ Every reading is a real process over real files: the same practice is gated twice, once
with its plants as full text and once as replacements, and the verdicts, the sentences and
the runs must agree. What differs is only what the bundle stores.
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.bundle import PlantSpec, Replacement, materialise
from studyforge.skills.exercises import gate_code
from tests.fixtures.claude_shape import jvm
from tests.studyforge.skills.exercises import node_practice as node
from tests.studyforge.skills.exercises.authoring import (
    NEGATIVE,
    Running,
    basket,
    basket_with_a_spec_plant,
)
from tests.studyforge.skills.exercises.test_pytest_practice import _brief


def _gate(tmp_path, made, brief, ledger):
    runner = Running()
    return gate_code(made, brief, ledger, runner, source="demo", where="w"), runner


def _verdicts(gated):
    return [(v.id, v.held, v.says) for v in gated.record.verdicts]


def test_a_python_spec_plant_clears_every_gate_with_the_same_verdicts_as_the_full_plant(tmp_path):
    brief, ledger = _brief(tmp_path)
    full, ran_full = _gate(tmp_path, basket(brief), brief, ledger)
    spec, ran_spec = _gate(tmp_path, basket_with_a_spec_plant(brief), brief, ledger)
    assert full.clears and spec.clears
    assert _verdicts(spec) == _verdicts(full)
    assert ran_spec.runs == ran_full.runs


def test_the_bundle_stores_the_spec_and_no_full_plant_and_the_record_digests_the_spec(tmp_path):
    brief, ledger = _brief(tmp_path)
    spec, _ = _gate(tmp_path, basket_with_a_spec_plant(brief), brief, ledger)
    paths = [path for path, _ in spec.files]
    plants = [path for path in paths if "/plants/" in path]
    assert len(plants) == 1 and plants[0].endswith("/plants/edge-1/total.py.plant.json")
    held = dict(spec.files)[plants[0]]
    assert json.loads(held)["plant_version"] == 1
    (planted,) = [i for i in spec.record.inputs if i.role.startswith("plant:")]
    assert planted.path == "plants/edge-1/total.py.plant.json"
    full, _ = _gate(tmp_path, basket(brief), brief, ledger)
    assert [p for p in [q for q, _ in full.files] if "/plants/" in p][0].endswith(
        "/plants/edge-1/total.py"
    )


def test_full_plants_are_stored_and_digested_exactly_as_before(tmp_path):
    brief, ledger = _brief(tmp_path)
    full, _ = _gate(tmp_path, basket(brief), brief, ledger)
    (planted,) = [i for i in full.record.inputs if i.role.startswith("plant:")]
    assert planted.path == "plants/edge-1/total.py"
    assert not any(path.endswith(".plant.json") for path, _ in full.files)


def test_a_spec_plant_that_ignores_nothing_fails_g3_with_the_full_plants_sentence(tmp_path):
    brief, ledger = _brief(tmp_path)
    made = basket(brief)
    inert = "price < 0 for price in prices"
    spec = PlantSpec(
        (Replacement(made.main_file, inert, "price < 0 or False for price in prices"),)
    )
    same = materialise(made.reference, spec, made.main_file, "w")
    spec_run, _ = _gate(tmp_path, replace(made, plants={NEGATIVE.id: spec}), brief, ledger)
    full_run, _ = _gate(tmp_path, replace(made, plants={NEGATIVE.id: same}), brief, ledger)
    assert [v.id for v in spec_run.refused] == ["G3"] == [v.id for v in full_run.refused]
    assert _verdicts(spec_run) == _verdicts(full_run)


def test_the_materialised_plant_is_never_written_into_the_corpus(tmp_path):
    brief, ledger = _brief(tmp_path)
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    _gate(tmp_path, basket_with_a_spec_plant(brief), brief, ledger)
    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*")) == before


@pytest.mark.parametrize(
    ("replacement", "words"),
    [
        (Replacement("total.py", "this text is not in the reference", "x"), "cannot apply"),
        (Replacement("total.py", "price", "cost"), "6 times"),
        (Replacement("total.py", "sum(prices)", "sum(prices)"), "puts back"),
        (Replacement("other.py", "sum(prices)", "0"), "other than"),
    ],
)
def test_a_spec_plant_that_cannot_be_materialised_is_refused_before_anything_runs(
    tmp_path, replacement, words
):
    brief, ledger = _brief(tmp_path)
    made = replace(basket(brief), plants={NEGATIVE.id: PlantSpec((replacement,))})
    runner = Running()
    with pytest.raises(ExerciseError, match=words) as refused:
        gate_code(made, brief, ledger, runner, source="demo", where="w")
    assert "edge case 1" in str(refused.value) and runner.runs == 0
    assert replacement.old not in str(refused.value)


def test_a_spec_plant_identical_to_the_reference_is_refused(tmp_path):
    brief, ledger = _brief(tmp_path)
    made = basket(brief)
    spec = PlantSpec(
        (
            Replacement(made.main_file, "sum(prices)", "sum(prices) + 0"),
            Replacement(made.main_file, "sum(prices) + 0", "sum(prices)"),
        )
    )
    with pytest.raises(ExerciseError, match="identical to the reference"):
        gate_code(
            replace(made, plants={NEGATIVE.id: spec}),
            brief, ledger, Running(), source="demo", where="w",
        )


def test_a_typescript_spec_plants_clear_every_gate_with_the_full_plants_verdicts(tmp_path):
    brief, ledger = _brief(tmp_path)
    full = node.draft(brief)
    spec = node.draft(brief, plants=dict(node.SPEC_PLANTS))
    for case, plant in node.SPEC_PLANTS.items():
        assert materialise(full.reference, plant, full.main_file, "w") == full.plants[case]
    ran_full, _ = _gate(tmp_path, full, brief, ledger)
    ran_spec, _ = _gate(tmp_path, spec, brief, ledger)
    assert ran_full.clears and ran_spec.clears
    assert _verdicts(ran_spec) == _verdicts(ran_full)


def test_the_java_and_kotlin_spec_plants_materialise_to_the_full_plants_they_replace(tmp_path):
    brief, _ = _brief(tmp_path)
    for made, specs in (
        (jvm.java(brief), jvm.JAVA_SPEC_PLANTS),
        (jvm.kotlin(brief), jvm.KOTLIN_SPEC_PLANTS),
    ):
        as_spec = jvm.with_spec_plants(made, specs)
        assert set(as_spec.plants) == set(made.plants)
        for case, plant in as_spec.plants.items():
            text = materialise(made.reference, plant, made.main_file, "w")
            assert text == made.plants[case]
