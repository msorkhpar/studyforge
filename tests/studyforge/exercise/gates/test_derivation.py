"""The derivation family: its two gates, the holes `D1` names, and every fault in a record."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates import (
    D1,
    D2,
    DERIVATION,
    GateRecord,
    Input,
    Verdict,
    digest_of_bytes,
    faults,
    hole,
    holes,
    record_document,
    record_of,
    registered,
)
from studyforge.exercise.gates.code import CODE

MAIN, TEST, ORIGINAL = "practice/a/Impl.java", "practice/a/ImplTest.java", "src/Impl.java"
BLANKED, WHOLE = digest_of_bytes(b"blanked\n"), digest_of_bytes(b"whole\n")


def inputs(starter=MAIN, starter_digest=BLANKED, tests=TEST, *, drop=()):
    entries = (
        Input("starter", starter, starter_digest),
        Input("reference", ORIGINAL, WHOLE),
        Input("tests", tests, digest_of_bytes(b"tests\n")),
    )
    return tuple(entry for entry in entries if entry.role not in drop)


#: One blanked method, and the failure Gate 1 attributed to it.
ONE_HOLE = ((hole("primary"), "expected 40 but was 00"),)


def record(*, recorded=ONE_HOLE, held=True, **options):
    return GateRecord(
        inputs=inputs(**options),
        verdicts=(
            Verdict(D1, DERIVATION.name, held, "each hole failed alone", recorded),
            Verdict(D2, DERIVATION.name, True, "the original passed"),
        ),
    )


def test_the_family_is_registered_with_its_two_gates_in_order():
    assert DERIVATION in registered()
    assert DERIVATION.gates == (D1, D2) == ("D1", "D2")


def test_a_record_that_supports_the_claim_has_no_fault_and_round_trips():
    written = record()
    assert faults(written, MAIN, TEST) == ()
    assert holes(written) == ("primary",)
    document = record_document(written)
    assert record_of(document, "gates.json") == written


def test_a_gate_that_did_not_hold_is_not_a_fault_it_is_a_shortfall():
    failed = record(held=False)
    assert faults(failed, MAIN, TEST) == ()
    assert failed.clears is False and failed.refused_by == (D1,)


def test_only_the_derivations_own_gates_are_evidence():
    authored = GateRecord(
        inputs=inputs(),
        verdicts=tuple(Verdict(gate, CODE.name, True, "held") for gate in CODE.gates),
    )
    assert len(faults(authored, MAIN, TEST)) == 1
    assert "code" in faults(authored, MAIN, TEST)[0]


@pytest.mark.parametrize(
    "recorded",
    [(), (("note", "a key that names no method"),), ((hole("a"), "x"), ("note", "y"))],
)
def test_the_first_gate_names_every_hole_and_at_least_one(recorded):
    assert any(
        "blanked method" in sentence for sentence in faults(record(recorded=recorded), MAIN, TEST)
    )


def test_a_missing_role_is_named():
    (sentence,) = faults(record(drop=("reference",)), MAIN, TEST)
    assert "reference" in sentence


def test_the_starter_and_tests_are_the_exercises_own_files():
    assert "'starter'" in " ".join(faults(record(starter="practice/b/Other.java"), MAIN, TEST))
    assert "'tests'" in " ".join(faults(record(tests="practice/b/OtherTest.java"), MAIN, TEST))


def test_a_starter_identical_to_the_original_blanked_nothing():
    (sentence,) = faults(record(starter_digest=WHOLE), MAIN, TEST)
    assert "nothing was blanked" in sentence


def test_a_record_carrying_half_the_family_is_refused_by_the_reader():
    document = record_document(record())
    document["gates"] = document["gates"][:1]
    with pytest.raises(ExerciseError):
        record_of(document, "gates.json")
