"""The registry: discovery, a derived order, and the collision that keeps a gate unweakenable.

⛔ **The interesting attack on a gate suite is not deleting a gate — it is
REDECLARING one**, so a second family answering for `G3` with a weaker rule
would leave every reader of the record seeing a `G3` that held. ⭐ That is
asserted here by trying it.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.gates import Family, declared_order, family_of, register, registered
from studyforge.exercise.gates.code import CODE, G1, G5


def test_the_code_family_is_registered_by_importing_the_package():
    # ⭐ THE SEAM: a family registers itself at its own import, and the one
    # line that makes it exist is the package contract's — the line R17
    # already obliges a new sub-package to add. ⛔ Nothing reaches a module by
    # name at run time; `tests/harness/test_isolation.py` refuses that for the
    # whole framework and it refused the discovery this package had first.
    assert CODE in registered()
    assert family_of(G1) == CODE.name
    assert family_of("G0") is None
    assert family_of(None) is None


def test_the_write_order_is_derived_from_the_names_not_from_the_import_order():
    order = declared_order()
    code_gates = [gate for family, gate in order if family == CODE.name]
    assert code_gates == list(CODE.gates)
    families = [family for family, _ in order]
    assert families == sorted(families)


def test_a_family_redeclaring_another_familys_gate_is_refused():
    with pytest.raises(ExerciseError, match="belongs to exactly one"):
        register(Family("weaker", (G5,)))


def test_a_family_re_registered_with_different_gates_is_refused():
    assert register(Family(CODE.name, CODE.gates)) is CODE
    with pytest.raises(ExerciseError, match="registered once and never replaced"):
        register(Family(CODE.name, CODE.gates[:-1]))


def test_a_family_with_no_gates_or_a_repeated_one_is_refused():
    with pytest.raises(ExerciseError, match="declares at least one gate"):
        Family("empty", ())
    with pytest.raises(ExerciseError, match="more than once"):
        Family("repeating", ("A1", "A1"))


def test_a_name_a_record_could_not_carry_is_refused():
    for bad in ("with space", "", None, 3, "a/b"):
        with pytest.raises(ExerciseError):
            Family(bad, ("A1",))
    with pytest.raises(ExerciseError):
        Family("fine", ("has space",))


def test_only_a_family_is_registered_as_one():
    with pytest.raises(ExerciseError, match="only a Family"):
        register(("code", ("G1",)))
