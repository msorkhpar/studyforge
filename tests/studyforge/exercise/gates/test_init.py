"""The gates package's contract, its public surface, and the layering the seam depends on."""

from __future__ import annotations

import ast

from studyforge import exercise
from studyforge.exercise import gates
from tests.studyforge.exercise.gates.test_configuration import gates_modules
from tests.support import assert_package_contract


def test_the_package_states_its_contract():
    assert_package_contract(gates, "studyforge.exercise.gates")


def test_the_public_surface_is_declared_and_complete():
    assert set(gates.__all__) == {
        "ALGORITHMS",
        "Attempt",
        "CITED_KEYS",
        "CODE",
        "Cited",
        "DIGEST",
        "DIGEST_PERMITTED",
        "DIGEST_WIDTH",
        "Evidence",
        "FIRST",
        "Family",
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "GateRecord",
        "INPUT_KEYS",
        "Input",
        "ORIGIN_ROLE",
        "PLANT",
        "RECORD_KEYS",
        "REFERENCE",
        "ROLE_PERMITTED",
        "Run",
        "SECOND",
        "SHA256",
        "STARTER",
        "TOKEN_PERMITTED",
        "VERDICT_KEYS",
        "Verdict",
        "check",
        "declared_cases",
        "declared_order",
        "digest_of_bytes",
        "digest_of_file",
        "drifted",
        "edges",
        "family_of",
        "folded",
        "plant_role",
        "record_document",
        "record_of",
        "register",
        "registered",
        "require_digest",
        "require_role",
        "require_run",
        "required_roles",
        "taken_over",
    }
    for name in gates.__all__:
        assert hasattr(gates, name), name
    assert gates.__all__ == sorted(gates.__all__)


def test_everything_a_second_gate_family_needs_is_on_that_surface():
    # ⛔ `W199/3`'s producer half, for the consumer this package was shaped
    # around: `AX-06` registers a family, writes verdicts and cited passages
    # into this record, and must never have to import a module inside here.
    taken = ("Family", "register", "Verdict", "GateRecord", "Cited", "Input", "ORIGIN_ROLE")
    assert set(taken) <= set(gates.__all__)


def test_the_exercise_package_names_the_gates_in_its_own_table():
    # ⚠️ R17: the parent's contract is where a reader finds out this exists,
    # and a sub-package missing from it is one nobody discovers.
    assert "`gates`" in (exercise.__doc__ or "")


def test_nothing_in_the_package_imports_execute_or_starts_a_process():
    # ⛔ The layering the `Attempt` seam exists for: `execute` imports
    # `studyforge.exercise`, so a gate reaching back for it would make the two
    # circular — and a gate that started a process itself would be a second
    # runner beside the one `execute` owns.
    reached: list[str] = []
    for path in gates_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                reached += [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                reached.append(node.module)
    assert not [name for name in reached if name.startswith("studyforge.execute")]
    assert not [name for name in reached if name.split(".")[0] in ("subprocess", "shutil")]


def test_the_package_is_reachable_without_naming_a_module_inside_it():
    # ⭐ The import surface `AX-04`, `AX-06` and `AX-08` use: the package,
    # never `studyforge.exercise.gates.code`.
    assert gates.check is not None and gates.record_of is not None
    assert gates.CODE.gates == (gates.G1, gates.G2, gates.G3, gates.G4, gates.G5)
