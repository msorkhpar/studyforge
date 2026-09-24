"""`W365`: the file-only exercise record is taught, and its refusals are named right.

**What it does.** Asserts the two clauses of row `W365`, both ways (R12):

1. The authoring guide and the exercise epic describe the record that names a
   file and no grader, and cite §7 for it rather than restating it.
2. `tests/fixture_checks/exercise.py` names a refusal of a record with no whole
   grader under the shape rule `exercise`, and keeps `exercise-trust` for R5's
   refusal of a whole one.

**How you use it.** `pytest tests/test_fixture_exercise_rule.py`.

**Depends on.** `studyforge.exercise` for the record's keys and its reader, and
`tests.authoring.support` for reading the guide. ⛔ No key list is spelled here:
every record below is built from the framework's own constants.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.exercise import GRADER_KEYS, REQUIRED_KEYS, from_document
from tests.authoring.support import document, json_fences
from tests.fixture_checks.exercise import check_exercise

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "specs" / "2026-09-08-studyforge-v1-design.md"
EPIC = ROOT / "docs" / "tasks" / "E06-exercise-contract.md"
#: §7's subsection for the record, as a heading and as the anchor that cites it.
HEADING = "### A file with no test (`W357`)"
ANCHOR = "2026-09-08-studyforge-v1-design.md#a-file-with-no-test-w357"
WHERE = "raw/python/unit-01/practice-1.json"

#: A whole grader whose trust claim R5 accepts.
GRADED = {
    "main_path": "practice/unit/hello.py",
    "test_path": "practice/unit/test_hello.py",
    "run_command": ["python3", "practice/unit/hello.py"],
    "test_command": ["python3", "-m", "pytest", "practice/unit"],
    "provenance": "bundled",
    "trust": "authoritative",
}
#: The file half and nothing else: §7's ungraded record.
FILE_ONLY = {key: GRADED[key] for key in REQUIRED_KEYS}


def rules(record):
    """The rule ids `check_exercise` names for a practice carrying `record`."""
    found = check_exercise({"kind": "practice", "exercise": record}, WHERE)
    return [rule for rule, _message in found]


# --- clause 2: the refusal is named under the rule it broke -----------------


def test_a_well_formed_file_only_record_is_refused_under_no_rule():
    assert rules(FILE_ONLY) == []


@pytest.mark.parametrize(
    "fault",
    [
        {"main_path": "../outside/hello.py"},
        {"run_command": "python3 hello.py"},
        {"main_pth": "hello.py"},
    ],
    ids=["unsafe-path", "command-not-a-list", "misspelled-key"],
)
def test_a_file_only_record_refused_for_its_shape_is_named_a_shape_refusal(fault):
    # ⛔ The defect: no `provenance`, so `unit.trust` refused it too, and the
    # checker filed a shape fault under R5.
    assert rules({**FILE_ONLY, **fault}) == ["exercise"]


def test_half_a_grader_is_a_shape_refusal_even_when_its_trust_claim_is_forbidden():
    # ⭐ The framework refuses this for the missing grader keys before R5 is
    # asked, and says so; the rule id follows the framework's reason.
    claim = {"provenance": "generated", "trust": "authoritative"}
    assert set(claim) < set(GRADER_KEYS)
    assert rules({**FILE_ONLY, **claim}) == ["exercise"]


def test_a_whole_grader_with_a_forbidden_trust_claim_is_still_named_under_r5():
    # ⭐ The other way: the fix must not move R5's own refusal off its rule.
    assert rules({**GRADED, "provenance": "generated"}) == ["exercise-trust"]
    assert rules({key: value for key, value in GRADED.items() if key != "trust"}) == []


def test_a_whole_grader_refused_for_its_shape_is_named_a_shape_refusal():
    assert rules({**GRADED, "test_command": "pytest"}) == ["exercise"]


# --- clause 1: both documents teach the record and cite §7 ------------------


def test_the_section_both_documents_cite_is_in_the_spec():
    assert HEADING in SPEC.read_text(encoding="utf-8").splitlines()


#: ⭐ Each document is READ inside the test, never at collection, so a checkout
#: without the epic still collects this file; the `e06` case is declared process in
#: `tests/harness/process.py` and the guide's case is the product's.
CITING = {
    "authoring-guide": lambda: document("exercises.md"),
    "e06": lambda: EPIC.read_text(encoding="utf-8"),
}


@pytest.mark.parametrize("which", list(CITING), ids=list(CITING))
def test_each_document_cites_section_7_for_the_file_only_record(which):
    text = CITING[which]()
    assert ANCHOR in text
    assert "`main_path` and `run_command`" in text


def test_the_guide_shows_the_file_only_record_and_it_reads_as_ungraded():
    shown = [
        block["exercise"] for block in json_fences(document("exercises.md")) if "exercise" in block
    ]
    file_only = [record for record in shown if set(record) == set(REQUIRED_KEYS)]
    assert len(file_only) == 1, shown
    assert from_document(file_only[0], "exercises.md").graded is False
    # ⭐ The graded example stays first: `test_authoring_reference` reads the
    # first record shown as the full key set.
    assert set(shown[0]) > set(REQUIRED_KEYS)
