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
