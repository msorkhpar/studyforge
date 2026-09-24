"""`validate`'s arm over an exercise claiming the source's own grader: its derivation's two gates.

⭐ Every refusal has a **negative control**: the same corpus with a record that
supports the claim is clean. ⛔ And every plant is a real edit to a real file,
observed before the report is read.
"""

from __future__ import annotations

import json

from studyforge.address import Address
from studyforge.exercise.bundle import Places
from studyforge.exercise.gates import (
    D1,
    D2,
    DERIVATION,
    GateRecord,
    Verdict,
    hole,
    record_document,
    taken_over,
)
from studyforge.exercise.gates.code import CODE
from studyforge.validate import validate
from studyforge.validate.derived import (
    RULE_DERIVATION_DIGEST,
    RULE_DERIVATION_RECORD,
    RULE_DERIVATION_SHORTFALL,
)
from tests.studyforge.validate import corpora

STARTER = "practice/total/total.py"
TESTS = "practice/total/check_total.py"
ORIGINAL = "lib/total.py"

FILES = {
    STARTER: "def total(values):\n    raise NotImplementedError\n",
    TESTS: "from total import total\n\ndef test_total():\n    assert total([1, 2]) == 3\n",
    ORIGINAL: "def total(values):\n    return sum(values)\n",
}

#: A corpus holding derived material declares where it sits, or check 14 refuses it.
MANIFEST = {
    **corpora.MANIFEST,
    "corpus_api": 2,
    "exercises": True,
    "content": {
        "include": ["src/*.md"],
        "not_material": [
            {"glob": "exercises/**", "why": "the derivation records, not the material"},
            {"glob": "practice/**", "why": "the reader's own workspace, not the material"},
            {"glob": "lib/**", "why": "the original the exercise was derived from"},
        ],
    },
}

#: Where the one practice's derivation record sits.
PLACES = Places(Address(["demo"]), "prose", 1, 1)


def exercise(trust="authoritative"):
    record = {
        "main_path": STARTER,
        "test_path": TESTS,
        "run_command": ["python3", STARTER],
        "test_command": ["python3", "-m", "pytest", "-q", TESTS],
        "provenance": "bundled",
    }
    if trust is not None:
        record["trust"] = trust
    return record


def derivation(root, *, held=(True, True), holes=("total",), roles=None, family=DERIVATION):
    """The record of the two gates over the corpus's own files, written where it is read."""
    files = roles or (("starter", STARTER), ("reference", ORIGINAL), ("tests", TESTS))
    if family is DERIVATION:
        recorded = tuple((hole(name), "expected 3 but it raised") for name in holes)
        first = Verdict(D1, family.name, held[0], "each hole failed", recorded)
        verdicts = (first, Verdict(D2, family.name, held[1], "the original passed"))
    else:
        verdicts = tuple(
            Verdict(id=gate, family=family.name, held=True, says="held") for gate in family.gates
        )
    record = GateRecord(inputs=taken_over(root, files, "test"), verdicts=verdicts)
    path = root / PLACES.gates
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record_document(record), indent=2) + "\n", encoding="utf-8")
    return path


def a_corpus(root, *, trust="authoritative", record=True, **options):
    """One corpus whose one practice carries a shipped grader claiming `trust`."""
    lesson = {
        "source": "demo",
        "address": ["demo"],
        "variant": "prose",
        "unit": 1,
        "ingested": "2026-01-05",
        "title": "Unit 1",
    }
    corpora.write(
        root,
        manifest=MANIFEST,
        containers={"demo": corpora.container([corpora.unit_entry(1, practices=1)])},
        documents={
            "demo/raw/prose/unit-01/practice-1.json": {
                **lesson,
                "kind": "practice",
                "ordinal": 1,
                "blocks": corpora.BLOCKS,
                "exercise": exercise(trust),
            }
        },
        sources={"src/one.md": corpora.SOURCE, **FILES},
    )
    if record:
        derivation(root, **options)
    return root


def messages(report, rule):
    return "\n".join(finding.message for finding in report.findings if finding.rule == rule)


def test_a_derived_exercise_whose_record_supports_its_claim_validates(tmp_path):
    report = validate(a_corpus(tmp_path / "c"))
    assert report.findings == (), [finding.message for finding in report.findings]


def test_an_authoritative_grader_with_no_derivation_record_is_refused(tmp_path):
    root = a_corpus(tmp_path / "c", record=False)
    assert not (root / PLACES.gates).exists()  # ⭐ the planted state
    report = validate(root)
    assert RULE_DERIVATION_RECORD in report.rules
    assert PLACES.gates in messages(report, RULE_DERIVATION_RECORD)


def test_a_claim_defaulted_from_bundled_is_held_to_the_same_gates(tmp_path):
    # ⛔ `trust` omitted defaults to authoritative for `bundled`, so the claim
    # is made by saying nothing, and it is refused the same way.
    root = a_corpus(tmp_path / "c", trust=None, record=False)
    assert RULE_DERIVATION_RECORD in validate(root).rules


def test_a_shipped_grader_claiming_only_advisory_asks_nothing(tmp_path):
    root = a_corpus(tmp_path / "c", trust="advisory", record=False)
    assert validate(root).findings == ()


def test_a_gate_that_did_not_hold_is_a_shortfall(tmp_path):
    for held in ((False, True), (True, False)):
        root = a_corpus(tmp_path / f"c{held}", held=held)
        written = json.loads((root / PLACES.gates).read_text(encoding="utf-8"))
        assert [gate["held"] for gate in written["gates"]] == list(held)
        report = validate(root)
        assert RULE_DERIVATION_SHORTFALL in report.rules
        assert RULE_DERIVATION_RECORD not in report.rules


def test_another_familys_gates_are_no_evidence_for_the_claim(tmp_path):
    # ⛔ An authored exercise's gates prove an advisory grader; they never
    # promote a shipped one.
    root = a_corpus(tmp_path / "c", family=CODE)
    written = json.loads((root / PLACES.gates).read_text(encoding="utf-8"))
    assert {gate["family"] for gate in written["gates"]} == {CODE.name}
    report = validate(root)
    assert RULE_DERIVATION_RECORD in report.rules
    assert "derivation" in messages(report, RULE_DERIVATION_RECORD)


def test_a_first_gate_naming_no_blanked_method_is_refused(tmp_path):
    root = a_corpus(tmp_path / "c", holes=())
    written = json.loads((root / PLACES.gates).read_text(encoding="utf-8"))
    assert written["gates"][0]["recorded"] == {}
    assert RULE_DERIVATION_RECORD in validate(root).rules


def test_a_record_over_some_other_exercises_files_is_refused(tmp_path):
    other = (("starter", ORIGINAL), ("reference", STARTER), ("tests", TESTS))
    report = validate(a_corpus(tmp_path / "c", roles=other))
    assert "'starter' is not the file the exercise names" in messages(
        report, RULE_DERIVATION_RECORD
    )


def test_a_record_missing_the_original_is_refused(tmp_path):
    report = validate(a_corpus(tmp_path / "c", roles=(("starter", STARTER), ("tests", TESTS))))
    assert "reference" in messages(report, RULE_DERIVATION_RECORD)


def test_a_starter_identical_to_the_original_is_refused(tmp_path):
    root = a_corpus(tmp_path / "c", record=False)
    (root / STARTER).write_text(FILES[ORIGINAL], encoding="utf-8")
    assert (root / STARTER).read_bytes() == (root / ORIGINAL).read_bytes()  # ⭐ the plant
    derivation(root)
    report = validate(root)
    assert "nothing was blanked" in messages(report, RULE_DERIVATION_RECORD)


def test_a_file_changed_after_the_gates_ran_is_refused_naming_it(tmp_path):
    root = a_corpus(tmp_path / "c")
    tests = root / TESTS
    before = tests.read_text(encoding="utf-8")
    tests.write_text(before.replace("== 3", "is not None"), encoding="utf-8")
    assert tests.read_text(encoding="utf-8") != before  # ⭐ the plant, observed
    report = validate(root)
    assert TESTS in messages(report, RULE_DERIVATION_DIGEST)


def test_a_derivation_record_that_will_not_read_is_refused(tmp_path):
    root = a_corpus(tmp_path / "c")
    (root / PLACES.gates).write_text('{"gates_api": 2, "inputs": [], "origins": [], "gates": []}')
    report = validate(root)
    assert "gates_api" in messages(report, RULE_DERIVATION_RECORD)
