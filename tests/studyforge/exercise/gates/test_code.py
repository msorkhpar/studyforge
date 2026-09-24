"""`G1`–`G5`, read over real runs of a real exercise — one planted defect per gate.

⛔ **The gate framework's acceptance, and its first half is the NEGATIVE CONTROL**: the
same bundle with nothing planted reads every gate GREEN, in this same module,
off the same machinery. ⚠️ A plant whose reading is indistinguishable from the
control has controlled nothing, so every case below **asserts the planted state
exists and prints it** before it reads a single gate.

⭐ **Nothing here is stubbed.** Each reading comes out of five real `pytest`
processes over files on disk, and each plant is a real edit to one of them —
[`workspace.py`](workspace.py) says why.

## ⚠️ Four plants are isolated and the fifth is not, and that is stated

⭐ **`VACUOUS_TEST`, `FLAKY_TEST`, `PLANT_SOLVES_ITS_EDGE` and `DRIFTED_ORIGIN`
each refuse exactly one gate** — asserted, not hoped, because each case reads
the whole refusal list. ⛔ **`UNMAPPED_TEST` cannot be isolated**: a report
naming a test the case map does not is refused by `report.breakdown_of` on
*every* run of that exercise, so `G1`–`G3` lose their evidence with it. ⭐ That
is asserted too, with the sentence each of them gives.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates import G1, G2, G3, G4, G5, Evidence, check
from studyforge.exercise.gates.runs import FIRST, REFERENCE, SECOND, STARTER, plant_role
from tests.studyforge.exercise.gates.workspace import (
    DRIFTED_ORIGIN,
    EMPTY_EDGE,
    FLAKY_TEST,
    MAIN_CASE,
    NEGATIVE_EDGE,
    PLANT_SOLVES_ITS_EDGE,
    UNMAPPED_TEST,
    VACUOUS_TEST,
    WHERE,
    Bundle,
)


@pytest.fixture(scope="module")
def clean(tmp_path_factory):
    """⭐ The negative control: the same bundle, nothing planted, every gate read."""
    return Bundle(tmp_path_factory.mktemp("clean")).read()


def test_the_control_clears_every_gate(clean):
    # ⛔ Without this, a plant that refused a gate would prove nothing: a suite
    # that refuses everything refuses the plant too.
    assert clean.refused() == ()
    assert [verdict.id for verdict in clean.verdicts] == [G1, G2, G3, G4, G5]
    assert all(verdict.says.strip() for verdict in clean.verdicts)


def test_the_control_really_ran_the_tests(clean):
    # ⚠️ The control is only a control if the runs happened. Five runs, each
    # with a report this build folded.
    roles = [(run.role, run.attempt) for run in clean.evidence.runs]
    assert roles == [
        (REFERENCE, FIRST),
        (REFERENCE, SECOND),
        (STARTER, FIRST),
        (plant_role(EMPTY_EDGE), FIRST),
        (plant_role(NEGATIVE_EDGE), FIRST),
    ]
    assert all(run.reported for run in clean.evidence.runs)


def test_a_vacuous_test_is_refused_by_g2(tmp_path, capsys):
    reading = Bundle(tmp_path, VACUOUS_TEST).read()

    # ⭐ The plant, OBSERVED: the main ask's test passed on the starter, which
    # is what "vacuous" means and what the control did not do.
    starter = reading.evidence.of(STARTER, FIRST)
    print("the starter run passed:", sorted(starter.passed_ids))
    assert starter.passed(MAIN_CASE)

    assert reading.refused() == (G2,)
    assert MAIN_CASE.says in reading.verdict(G2).says
    assert capsys.readouterr().out


def test_a_flaky_test_is_refused_by_g1(tmp_path, capsys):
    reading = Bundle(tmp_path, FLAKY_TEST).read()

    # ⭐ The plant, OBSERVED: the reference's two runs disagreed. ⛔ Compared
    # against each other, never against a constant — an equality that reads the
    # same on both sides is the no-op this project has been burned by.
    first = reading.evidence.of(REFERENCE, FIRST)
    second = reading.evidence.of(REFERENCE, SECOND)
    print("run 1 passed:", sorted(first.passed_ids))
    print("run 2 passed:", sorted(second.passed_ids))
    assert first.passed_ids != second.passed_ids

    assert reading.refused() == (G1,)
    assert "flaky" in reading.verdict(G1).says


def test_an_edge_test_the_ignoring_solution_passes_is_refused_by_g3(tmp_path, capsys):
    reading = Bundle(tmp_path, PLANT_SOLVES_ITS_EDGE).read()

    # ⭐ The plant, OBSERVED: the solution planted to IGNORE the empty basket
    # passed the very test that edge names, so that test catches nothing.
    plant = reading.evidence.of(plant_role(EMPTY_EDGE), FIRST)
    print("the plant for the empty-basket edge passed:", sorted(plant.passed_ids))
    assert plant.passed(EMPTY_EDGE)

    assert reading.refused() == (G3,)
    assert EMPTY_EDGE.says in reading.verdict(G3).says
    # ⛔ Per case, not per exercise: the other edge is still proven, and the
    # sentence says so by naming one of two.
    assert NEGATIVE_EDGE.says not in reading.verdict(G3).says
    assert capsys.readouterr().out


def test_a_test_the_map_does_not_name_is_refused_by_g4(tmp_path, capsys):
    reading = Bundle(tmp_path, UNMAPPED_TEST).read()

    # ⭐ The plant, OBSERVED: every run's report now refuses to fold, which the
    # control's runs did not do.
    reference = reading.evidence.of(REFERENCE, FIRST)
    print("the reference run's fold refused:", reference.refusal)
    assert reference.refusal is not None
    assert reference.passed_ids is None

    assert G4 in reading.refused()
    assert "names a test the record's 'cases' does not" in reading.verdict(G4).says
    # ⚠️ And the cost, asserted rather than left to be discovered: this is the
    # one plant that is not isolable, and the other three say why.
    assert reading.refused() == (G1, G2, G3, G4)
    for gate in (G1, G2, G3):
        assert "G4 names what is wrong" in reading.verdict(gate).says


def test_an_origin_whose_digest_drifted_is_refused_by_g5(tmp_path, capsys):
    bundle = Bundle(tmp_path, DRIFTED_ORIGIN)

    # ⭐ The plant, OBSERVED: the ledger's digest for the cited passage is no
    # longer the one the record recorded — printed, and compared to each other.
    recorded = bundle.origins[0]
    current = bundle.ledger[recorded.path]
    print("recorded:", recorded.digest)
    print("the ledger now says:", current)
    assert recorded.digest != current

    reading = bundle.read()
    assert reading.refused() == (G5,)
    assert recorded.path in reading.verdict(G5).says
    assert capsys.readouterr().out


def test_an_exercise_with_no_cases_is_refused_rather_than_gated(tmp_path):
    # ⛔ A gate suite with nothing to fold answers nothing, and answering
    # nothing green is the theatre these gates exist to prevent.
    bundle = Bundle(tmp_path)
    bare = type(bundle.exercise)(
        main_path="work/solution.py",
        test_path="work/test_solution.py",
        run_command=("python3", "work/solution.py"),
        test_command=("python3", "-m", "pytest", "work"),
        provenance="generated",
        trust="advisory",
    )
    with pytest.raises(ExerciseError, match="answering nothing"):
        Evidence.taken(bare, bundle.attempt, WHERE)
    with pytest.raises(ExerciseError, match="answering nothing"):
        check(bare, Evidence(runs=()), (), {}, WHERE)


def test_a_gate_with_nothing_to_read_does_not_hold(tmp_path):
    # ⛔ Never "held vacuously": a gate that passes for want of evidence is the
    # defect R5's gates are written against. Every run is absent
    # here, and every gate but the vacuous-origin arm refuses.
    bundle = Bundle(tmp_path)
    verdicts = check(bundle.exercise, Evidence(runs=()), bundle.origins, bundle.ledger, WHERE)
    refused = [verdict.id for verdict in verdicts if not verdict.held]
    assert refused == [G1, G2, G3, G4]
    assert [verdict.id for verdict in verdicts] == [G1, G2, G3, G4, G5]
