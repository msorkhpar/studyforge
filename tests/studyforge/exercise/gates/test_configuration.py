"""⛔ *No gate can be disabled, skipped or weakened by configuration* — asserted by TRYING.

⭐ **R5's honesty as gates, and the gate record's promise.** ⚠️ A module
docstring saying so is a promise; this file is the check. Every case below
attempts the thing and asserts it did not work — ⛔ **and each attempt is
observed first**: the environment really is set, the key really is in the
document, the gate really did fail.

⭐ **Four surfaces, because a gate can be turned off at four different heights:**
the call, the run list, the document, and the process's environment.
"""

from __future__ import annotations

import ast
import inspect
import os
from pathlib import Path

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates import (
    Evidence,
    GateRecord,
    Verdict,
    check,
    record_document,
    record_of,
)
from studyforge.exercise.gates.code import CODE
from tests.studyforge.exercise.gates.workspace import Bundle
from tests.support import repository_root

WHERE = "corpus/adding-up/unit-01/practice-1"

#: ⚠️ Every spelling somebody reaching for an off switch would plausibly try.
#: ⛔ A forbidden list, and it says so: what is enumerable here is the attempt,
#: never the set of things a process could read — which is why the sweep below
#: is the layer that actually holds, and this one is the one that reads well.
SWITCHES = (
    "STUDYFORGE_GATES",
    "STUDYFORGE_SKIP_GATES",
    "STUDYFORGE_GATES_OFF",
    "STUDYFORGE_DISABLE_GATES",
    "STUDYFORGE_NO_GATES",
    "SKIP_GATES",
    "GATES",
    "NO_COLOR",
)

#: The package whose modules must read no configuration at all.
PACKAGE = "src/studyforge/exercise/gates"


def gates_modules() -> list[Path]:
    """Every module of the gates package — this sweep's population."""
    found = sorted((repository_root() / PACKAGE).rglob("*.py"))
    assert found, "the sweep found no module, so it would pass over nothing"
    return found


def verdicts(*, held: bool) -> tuple[Verdict, ...]:
    """One verdict per gate the `code` family declares."""
    return tuple(
        Verdict(id=gate, family=CODE.name, held=held, says=f"{gate} was read")
        for gate in CODE.gates
    )


def test_no_module_in_the_package_reads_the_environment_or_any_other_switch():
    # ⭐ THE LAYER THAT HOLDS: not a list of variable names, but the absence of
    # any reader for one. A module that imports `os` at all is reported, so a
    # future `os.environ.get("…")` cannot arrive quietly.
    read: list[str] = []
    for path in gates_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                read += [
                    f"{path.name}: import {alias.name}"
                    for alias in node.names
                    if alias.name.split(".")[0] in ("os", "configparser", "tomllib")
                ]
            if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in (
                "os",
                "configparser",
                "tomllib",
            ):
                read.append(f"{path.name}: from {node.module}")
            if isinstance(node, ast.Name) and node.id in ("environ", "getenv"):
                read.append(f"{path.name}: {node.id}")
    assert read == []


def test_setting_every_switch_changes_no_verdict(monkeypatch, tmp_path):
    bundle = Bundle(tmp_path)
    evidence = Evidence.taken(bundle.exercise, bundle.attempt, WHERE)
    before = check(bundle.exercise, evidence, bundle.origins, bundle.ledger, WHERE)

    # ⭐ The attempt, OBSERVED: the variables really are set in this process,
    # printed, and only then is the reading taken again.
    for name in SWITCHES:
        monkeypatch.setenv(name, "G1,G2,G3,G4,G5")
    print("set in this process:", {name: os.environ[name] for name in SWITCHES})
    assert all(os.environ.get(name) for name in SWITCHES)

    after = check(bundle.exercise, evidence, bundle.origins, bundle.ledger, WHERE)
    assert after == before
    assert [verdict.id for verdict in after] == list(CODE.gates)


def test_check_takes_no_option_that_asks_for_fewer_gates():
    parameters = inspect.signature(check).parameters
    assert list(parameters) == ["exercise", "evidence", "origins", "ledger", "where"]
    assert all(entry.default is inspect.Parameter.empty for entry in parameters.values())
    assert not any(
        entry.kind in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL)
        for entry in parameters.values()
    )


def test_a_bundle_that_invents_an_off_switch_is_refused_rather_than_ignored():
    complete = record_document(GateRecord(verdicts=verdicts(held=True)))
    assert record_of(complete, WHERE).clears is True

    for key, value in (("skip", ["G2"]), ("enabled", False), ("gates_off", True)):
        document = record_document(GateRecord(verdicts=verdicts(held=True)))
        document[key] = value
        # ⭐ The attempt, OBSERVED: the key really is in the document.
        assert key in document
        with pytest.raises(ExerciseError, match="refused rather than ignored"):
            record_of(document, WHERE)

    for key, value in (("enabled", False), ("skip", True), ("weight", "0")):
        document = record_document(GateRecord(verdicts=verdicts(held=True)))
        document["gates"][1][key] = value
        assert key in document["gates"][1]
        with pytest.raises(ExerciseError, match="nothing else"):
            record_of(document, WHERE)


def test_a_failed_gate_cannot_be_dropped_to_make_a_record_clear():
    failed = GateRecord(verdicts=verdicts(held=False))
    assert failed.clears is False and failed.refused_by == CODE.gates

    # ⭐ The attempt, OBSERVED: the failing verdicts really are gone from the
    # document, and the record is refused for it rather than reading green.
    document = record_document(failed)
    document["gates"] = [entry for entry in document["gates"] if entry["held"]]
    print("verdicts left after dropping the failures:", len(document["gates"]))
    assert document["gates"] == []
    with pytest.raises(ExerciseError, match="names no gate at all"):
        record_of(document, WHERE)
    # ⛔ And the same answer for one built in memory rather than read: `all(())`
    # is true, so a record with no verdicts must not report that it cleared.
    assert GateRecord().clears is False

    # ⛔ And flipping the answer instead is not a way through either: the
    # record then says something the gate never said, which is the drift a
    # digest over the inputs is there to catch (`AX-04`).
    flipped = record_document(failed)
    for entry in flipped["gates"]:
        entry["held"] = True
    assert record_of(flipped, WHERE).clears is True
    assert record_of(record_document(failed), WHERE).clears is False


def test_a_gate_with_no_evidence_does_not_hold(tmp_path):
    # ⛔ The last way to disable a gate is to give it nothing to read. A gate
    # that passed for want of evidence would be the off switch, spelled
    # differently.
    bundle = Bundle(tmp_path)
    verdicts_read = check(bundle.exercise, Evidence(runs=()), (), {}, WHERE)
    assert [entry.id for entry in verdicts_read] == list(CODE.gates)
    assert not any(entry.held for entry in verdicts_read[:4])
