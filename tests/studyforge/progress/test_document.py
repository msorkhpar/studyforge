"""Mirror of `src/studyforge/progress/document.py` (R12): the pass rule, the shape, the bytes."""

from __future__ import annotations

import copy
import json

import pytest

from studyforge.address import Address
from studyforge.progress.document import (
    MODES,
    PROGRESS_API,
    is_pass,
    new_document,
    next_entry,
    render,
    validate,
)
from studyforge.progress.errors import ProgressError, ProgressFormatError
from studyforge.progress.keys import practice_key
from studyforge.version import CONTRACT_FIELDS

T1 = "2026-09-12T10:00:00+00:00"
T2 = "2026-09-12T11:00:00+00:00"
T3 = "2026-09-12T12:00:00+00:00"
COMMANDS = ["./gradlew test"]
KEY = practice_key(Address.of("basics", "intro"), 1, "practice-java")


def run(previous, mode, exit_code, when):
    return next_entry(previous, mode=mode, exit_code=exit_code, commands=COMMANDS, when=when)


def document_with(entry):
    return {"progress_api": PROGRESS_API, "practices": {KEY: entry}}


# --------------------------------------------------------------------------
# The pass rule
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mode", "exit_code", "passed"),
    [
        ("test", 0, True),
        ("run", 0, False),
        ("test", 1, False),
        ("test", "timeout", False),
        ("test", "stopped", False),
        ("test", False, False),
    ],
)
def test_only_a_test_run_that_exits_zero_is_a_pass(mode, exit_code, passed):
    assert is_pass(mode, exit_code) is passed


def test_a_run_that_printed_successfully_never_sets_passed():
    entry = run(None, "run", 0, T1)
    assert entry["last"]["passed"] is False
    assert entry["first_passed_at"] is None


def test_the_first_pass_is_recorded_once_and_never_moves():
    first = run(None, "test", 0, T1)
    assert first["first_passed_at"] == T1
    failed = run(first, "test", 1, T2)
    assert (failed["first_passed_at"], failed["last"]["passed"]) == (T1, False)
    passed_again = run(failed, "test", 0, T3)
    assert passed_again["first_passed_at"] == T1
    assert passed_again["runs"] == 3


def test_there_is_no_mode_a_read_mark_could_be_recorded_under():
    # ⛔ §8.5: a read mark is never a pass, so the record has no way to hold one.
    assert MODES == ("run", "test")
    with pytest.raises(ProgressError):
        run(None, "read", 0, T1)
    marked = document_with(run(None, "test", 0, T1))
    marked["practices"][KEY]["last"]["mode"] = "read"
    with pytest.raises(ProgressFormatError):
        validate(marked, 2)


@pytest.mark.parametrize(
    "arguments",
    [
        {"mode": "test", "exit_code": -1, "commands": COMMANDS, "when": T1},
        {"mode": "test", "exit_code": True, "commands": COMMANDS, "when": T1},
        {"mode": "test", "exit_code": 0, "commands": [], "when": T1},
        {"mode": "test", "exit_code": 0, "commands": ["  "], "when": T1},
        {"mode": "test", "exit_code": 0, "commands": COMMANDS, "when": "yesterday"},
    ],
)
def test_a_bad_run_is_refused_before_anything_is_built(arguments):
    with pytest.raises(ProgressError):
        next_entry(None, **arguments)


# --------------------------------------------------------------------------
# The shape
# --------------------------------------------------------------------------


def test_what_next_entry_builds_is_what_validate_accepts():
    assert validate(document_with(run(None, "test", 0, T1)), 2)
    assert validate(new_document(), 1) == {"progress_api": PROGRESS_API, "practices": {}}


def test_the_version_key_is_registered_in_the_one_tuple():
    assert "progress_api" in CONTRACT_FIELDS


def malformed():
    good = document_with(run(None, "test", 0, T1))
    cases = {}

    def case(name, change):
        document = copy.deepcopy(good)
        change(document)
        cases[name] = document

    case("unknown version", lambda d: d.update(progress_api=99))
    case("extra top-level key", lambda d: d.update(more=1))
    case("practices not an object", lambda d: d.update(practices=[]))
    case(
        "key at another depth",
        lambda d: d.update(practices={"basics/unit-01/x": good["practices"][KEY]}),
    )
    case("passed disagrees", lambda d: d["practices"][KEY]["last"].update(passed=False))
    case("run marked passed", lambda d: d["practices"][KEY]["last"].update(mode="run"))
    case("runs zero", lambda d: d["practices"][KEY].update(runs=0))
    case("first not a timestamp", lambda d: d["practices"][KEY].update(first_passed_at=7))
    case("missing entry key", lambda d: d["practices"][KEY].pop("runs"))
    case("commands empty", lambda d: d["practices"][KEY]["last"].update(commands=[]))
    return cases


@pytest.mark.parametrize("name", sorted(malformed()))
def test_a_document_that_is_not_exactly_the_shape_raises(name):
    with pytest.raises(ProgressFormatError):
        validate(malformed()[name], 2)


def test_a_malformed_key_is_not_reproduced_by_the_refusal():
    document = {"progress_api": PROGRESS_API, "practices": {"/" + "home/jane/x": {}}}
    with pytest.raises(ProgressFormatError) as refused:
        validate(document, 2)
    assert "jane" not in str(refused.value)


# --------------------------------------------------------------------------
# The bytes
# --------------------------------------------------------------------------


def test_keys_sort_stably_whatever_order_they_were_built_in():
    a = practice_key(Address.of("basics", "intro"), 1, "practice-a")
    b = practice_key(Address.of("basics", "intro"), 2, "practice-b")
    entry = run(None, "test", 0, T1)
    one = {"progress_api": PROGRESS_API, "practices": {b: entry, a: entry}}
    other = {"practices": {a: entry, b: entry}, "progress_api": PROGRESS_API}
    assert render(one) == render(other)
    assert render(json.loads(render(one))) == render(one)
    assert render(one).index(a) < render(one).index(b)
    assert render(one).endswith("}\n") and render(one).startswith('{\n  "practices"')


# --------------------------------------------------------------------------
# `last.cases` — the breakdown, which is a report and never a pass rule (AX-02)
# --------------------------------------------------------------------------

VERDICTS = {"test_the_ask": True, "test_an_edge": False}


def graded(previous=None, cases=VERDICTS, mode="test", exit_code=0, when=T1):
    return next_entry(
        previous, mode=mode, exit_code=exit_code, commands=COMMANDS, when=when, cases=cases
    )


def test_a_submit_carries_one_verdict_per_case_into_the_entry():
    entry = graded()
    assert entry["last"]["cases"] == VERDICTS
    validate(document_with(entry), 2)


def test_the_breakdown_is_copied_rather_than_held_by_reference():
    mutable = dict(VERDICTS)
    entry = graded(cases=mutable)
    mutable["test_an_edge"] = True
    assert entry["last"]["cases"] == VERDICTS


def test_a_failing_edge_does_not_stop_the_run_passing_and_a_passing_one_does_not_start_it():
    # ⛔ The clause AX-02 may not touch: `is_pass` is the mode and the status,
    # and nothing in the breakdown is allowed to become a second definition.
    incomplete = graded(cases={"test_the_ask": True, "test_an_edge": False}, exit_code=0)
    assert incomplete["last"]["passed"] is True
    assert incomplete["first_passed_at"] == T1
    complete = graded(cases={"test_the_ask": True, "test_an_edge": True}, exit_code=1)
    assert complete["last"]["passed"] is False
    assert complete["first_passed_at"] is None
    # ⛔ And the validator agrees with the writer about both, rather than
    # cross-checking the verdicts against `passed` and refusing them.
    validate(document_with(incomplete), 2)
    validate(document_with(complete), 2)


def test_a_run_recorded_before_this_task_reads_back_unchanged():
    # ⭐ The Acceptance's fourth clause, read as bytes rather than as a shape:
    # an entry built with no breakdown carries no key and renders as it did.
    plain = run(None, "test", 0, T1)
    assert "cases" not in plain["last"]
    assert validate(document_with(plain), 2) == document_with(plain)
    assert json.loads(render(document_with(plain)))["practices"][KEY] == plain


def test_a_document_carrying_a_breakdown_re_renders_to_one_byte_sequence():
    one = document_with(graded(cases={"b": True, "a": False}))
    other = copy.deepcopy(one)
    other["practices"][KEY]["last"]["cases"] = {"a": False, "b": True}
    assert render(one) == render(other) == render(json.loads(render(one)))


def test_a_later_run_with_no_report_drops_the_previous_run_s_breakdown():
    # ⚠️ `last` is the LAST run, so a Submit that wrote no report leaves no
    # breakdown — carrying the previous one forward would report a run nobody
    # took as this one's.
    first = graded()
    second = run(first, "test", 1, T2)
    assert "cases" not in second["last"] and second["runs"] == 2


@pytest.mark.parametrize(
    "cases",
    [{}, {"": True}, {"  ": True}, {"test_x": None}, {"test_x": 1}, {7: True}, [], "test_x"],
)
def test_a_breakdown_that_is_not_one_verdict_per_case_id_is_refused_both_ways(cases):
    with pytest.raises(ProgressError):
        graded(cases=cases)
    entry = graded()
    entry["last"]["cases"] = cases
    with pytest.raises(ProgressFormatError):
        validate(document_with(entry), 2)


def test_a_run_mode_run_has_no_breakdown_to_record_or_to_read_back():
    with pytest.raises(ProgressError):
        graded(mode="run")
    entry = run(None, "run", 0, T1)
    entry["last"]["cases"] = VERDICTS
    with pytest.raises(ProgressFormatError):
        validate(document_with(entry), 2)


def test_a_key_in_last_that_is_neither_required_nor_cases_is_still_refused():
    entry = graded()
    entry["last"]["edges_passed"] = 1
    with pytest.raises(ProgressFormatError):
        validate(document_with(entry), 2)


def test_a_bad_breakdown_leaves_no_half_formed_entry_and_names_no_case_id():
    with pytest.raises(ProgressError) as refused:
        graded(cases={"test_secret_name": "yes"})
    assert "test_secret_name" not in str(refused.value)
