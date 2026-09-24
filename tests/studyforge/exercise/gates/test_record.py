"""The gate record: complete or refused, round-tripped byte for byte, and family-agnostic.

⭐ **The record is the artifact `studyforge validate` re-reads** (spec §7 §10),
so what is asserted here is what a bundle can and cannot claim about itself.
⛔ **The seam the quiz gates use is asserted too**: a second family's gates are
required, accepted and ordered by this module without a line of it knowing what
a quiz is — proved by registering one and reading a record that carries both.
"""

from __future__ import annotations

import dataclasses

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates import (
    RECORD_KEYS,
    VERDICT_KEYS,
    Cited,
    Family,
    GateRecord,
    Input,
    Verdict,
    digest_of_bytes,
    record_document,
    record_of,
    register,
)
from studyforge.exercise.gates.code import CODE
from studyforge.exercise.gates.record import GATES_API, UNVERSIONED_KEYS
from studyforge.version import CONTRACT_FIELDS

WHERE = "corpus/adding-up/unit-01/practice-1"

DIGEST = digest_of_bytes(b"the bytes a reading was taken over\n")


def verdicts(*, held: bool = True) -> tuple[Verdict, ...]:
    """One verdict per gate the `code` family declares, in its declared order."""
    return tuple(
        Verdict(id=gate, family=CODE.name, held=held, says=f"{gate} was read")
        for gate in CODE.gates
    )


def record() -> GateRecord:
    """A complete record over one input and one cited passage."""
    return GateRecord(
        inputs=(Input(role="starter", path="work/starter.py", digest=DIGEST),),
        origins=(
            Cited(role="origin", path="lessons/adding-up.md", section="Adding up", digest=DIGEST),
        ),
        verdicts=verdicts(),
    )


def test_a_record_round_trips_to_the_same_bytes():
    document = record_document(record())
    assert record_document(record_of(document, WHERE)) == document
    assert list(document) == list(RECORD_KEYS)
    assert list(document["gates"][0]) == list(VERDICT_KEYS)


def test_clears_is_derived_and_a_failed_gate_cannot_be_talked_out_of():
    assert record().clears is True
    failed = GateRecord(verdicts=verdicts(held=False))
    assert failed.clears is False
    assert failed.refused_by == CODE.gates
    # ⛔ Frozen, and `clears` is a property with no setter: there is no field,
    # no argument and no key by which a record with a failed gate reports that
    # it cleared.
    assert "clears" not in {entry.name for entry in dataclasses.fields(GateRecord)}
    assert isinstance(GateRecord.clears, property) and GateRecord.clears.fset is None
    assert "clears" not in record_document(record())
    with pytest.raises(AttributeError):
        failed.verdicts = verdicts()


def test_a_record_naming_no_gate_at_all_is_refused():
    # ⛔ MEASURED by this test before the arm existed: `all(())` is true, so an
    # empty record read as one that cleared. Deleting the gates that refused a
    # bundle was the cheapest way through, and it is closed here and in
    # `clears`.
    document = record_document(record())
    document["gates"] = []
    with pytest.raises(ExerciseError, match="names no gate at all"):
        record_of(document, WHERE)
    assert GateRecord().clears is False


def test_a_record_missing_a_gate_is_refused():
    document = record_document(record())
    document["gates"] = document["gates"][:-1]
    with pytest.raises(ExerciseError, match="every gate of every family it names"):
        record_of(document, WHERE)


def test_a_record_whose_gates_are_reordered_is_refused():
    document = record_document(record())
    document["gates"] = list(reversed(document["gates"]))
    with pytest.raises(ExerciseError, match="an order somebody chose"):
        record_of(document, WHERE)


def test_a_gate_no_family_declares_is_refused():
    document = record_document(record())
    document["gates"][0]["id"] = "G0"
    with pytest.raises(ExerciseError, match="no registered family"):
        record_of(document, WHERE)


def test_a_verdict_claiming_somebody_elses_family_is_refused():
    document = record_document(record())
    document["gates"][0]["family"] = "quiz"
    with pytest.raises(ExerciseError, match="answering for somebody"):
        record_of(document, WHERE)


def test_a_verdict_with_nothing_to_say_is_refused():
    document = record_document(record())
    document["gates"][2]["says"] = "   "
    with pytest.raises(ExerciseError, match="required whether the gate held or not"):
        record_of(document, WHERE)


def test_held_is_true_or_false_and_never_a_truthy_value():
    document = record_document(record())
    document["gates"][0]["held"] = 1
    with pytest.raises(ExerciseError, match="did the gate hold"):
        record_of(document, WHERE)


def test_a_key_this_build_does_not_define_is_refused_rather_than_ignored():
    document = record_document(record())
    document["skip"] = ["G2"]
    with pytest.raises(ExerciseError, match="refused rather than ignored"):
        record_of(document, WHERE)

    entry = record_document(record())
    entry["gates"][1]["enabled"] = False
    with pytest.raises(ExerciseError, match="nothing else"):
        record_of(entry, WHERE)


def test_a_digest_this_build_cannot_read_is_refused():
    document = record_document(record())
    document["inputs"][0]["digest"] = "md5:" + "0" * 32
    with pytest.raises(ExerciseError, match="a digest is written"):
        record_of(document, WHERE)

    truncated = record_document(record())
    truncated["inputs"][0]["digest"] = "sha256:abc123"
    with pytest.raises(ExerciseError, match="hex characters"):
        record_of(truncated, WHERE)


def test_two_entries_claiming_one_role_are_refused():
    document = record_document(record())
    document["inputs"].append(dict(document["inputs"][0], path="work/other.py"))
    with pytest.raises(ExerciseError, match="role more than once"):
        record_of(document, WHERE)


def test_an_absolute_path_never_reaches_the_record():
    # ⛔ R7: a record is a tracked file in a corpus repository, so a path in it
    # is workspace-relative or it is refused. The shape is assembled at run
    # time rather than written into this file.
    document = record_document(record())
    document["inputs"][0]["path"] = "/" + "/".join(("home", "someone", "work", "starter.py"))
    with pytest.raises(ExerciseError):
        record_of(document, WHERE)


def test_a_cited_passage_may_name_a_whole_file():
    document = record_document(record())
    document["origins"][0]["section"] = None
    assert record_of(document, WHERE).origins[0].section is None


def test_a_second_family_shares_this_record_and_edits_nothing_here():
    # ⭐ THE SEAM the quiz gates USE, asserted by doing it: a family registered
    # from outside this package is required, accepted and ordered by `record`,
    # which has never heard of it.
    family = register(Family("zz-example", ("X1", "X2")))
    both = GateRecord(
        verdicts=(
            *verdicts(),
            *(
                Verdict(id=gate, family=family.name, held=True, says=f"{gate} was read")
                for gate in family.gates
            ),
        )
    )
    document = record_document(both)
    assert record_document(record_of(document, WHERE)) == document

    # ⛔ And the completeness rule reaches it on the day it registered: half a
    # family is refused exactly as half the code family is.
    document["gates"] = document["gates"][:-1]
    with pytest.raises(ExerciseError, match="every gate of every family it names"):
        record_of(document, WHERE)


def test_a_familys_own_evidence_round_trips_and_decides_nothing():
    # ⭐ `Q1`–`Q3` are model judgements shipped as a record, so a verdict
    # carries the family's own keys. ⛔ `held` is still the verdict.
    recorded = (("prompt", "given the page, pick the key"), ("outcome", "picked it twice"))
    carried = GateRecord(
        verdicts=(
            Verdict(id=CODE.gates[0], family=CODE.name, held=True, says="read", recorded=recorded),
            *verdicts()[1:],
        )
    )
    document = record_document(carried)
    assert document["gates"][0]["recorded"] == dict(recorded)
    assert record_of(document, WHERE).verdicts[0].recorded == recorded

    document["gates"][0]["recorded"] = {"prompt": 3}
    with pytest.raises(ExerciseError, match="'recorded' value is text"):
        record_of(document, WHERE)


# --- the version (R9) --------------------------------------------------------


def test_the_record_writes_its_version_first():
    document = record_document(record())
    assert next(iter(document)) == "gates_api"
    assert document["gates_api"] == GATES_API == 1
    assert "gates_api" in CONTRACT_FIELDS


@pytest.mark.parametrize("declared", [2, 0, True, 1.0, "1", None])
def test_a_version_this_build_does_not_speak_is_refused_naming_the_key(declared):
    document = record_document(record()) | {"gates_api": declared}
    with pytest.raises(ExerciseError) as refused:
        record_of(document, WHERE)
    assert "gates_api" in str(refused.value)


def test_a_record_written_before_the_key_is_read_as_version_one():
    # ⭐ The stated rule: the whole shape every record had before the key.
    versioned = record_document(record())
    earlier = {key: value for key, value in versioned.items() if key != "gates_api"}
    assert list(earlier) == list(UNVERSIONED_KEYS)
    assert record_of(earlier, WHERE) == record_of(versioned, WHERE)
    assert record_document(record_of(earlier, WHERE)) == versioned


def test_a_record_with_no_version_and_any_other_shape_is_refused_naming_the_key():
    earlier = {key: value for key, value in record_document(record()).items() if key != "gates_api"}
    for planted in (earlier | {"skip": True}, {"inputs": [], "gates": []}):
        with pytest.raises(ExerciseError) as refused:
            record_of(planted, WHERE)
        assert "'gates_api'" in str(refused.value)
