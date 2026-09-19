"""Mirror of `tools/gates.py` (R12): both suite forms, asserted both ways (`W364`).

⛔ **NO TEST CALLS DOCKER.** The gates are argv tuples; every reading here is a string or
an injected answer, and `xdist_importable` is pointed at a STUB interpreter.
"""

from __future__ import annotations

import stat

import tools.gates as gates_module
import tools.mergegate as mergegate_module
from tests.support import assert_package_contract
from tools.gates import (
    FLOOR,
    GATES,
    HOST,
    IMAGE,
    PARALLEL,
    PARALLEL_FORM,
    SERIAL_FORM,
    WRAPPER,
    declared,
    suite_gate,
    xdist_importable,
)
from tools.mergegate import Outcome, Reading, render, stage_and_read


def test_states_its_contract():
    assert_package_contract(gates_module, "tools.gates")


def test_the_merge_gate_RE_EXPORTS_the_one_declaration():
    # ⛔ One declaration, read from two names: a second copy would drift.
    assert mergegate_module.GATES is GATES
    assert mergegate_module.Gate is gates_module.Gate


# --- clause 5: both argv forms ----------------------------------------------------------


def test_the_PARALLEL_form_carries_n_auto_in_BOTH_environments():
    for environment in (IMAGE, HOST):
        gate = suite_gate(environment, parallel=True)
        assert gate.argv[-len(PARALLEL) :] == PARALLEL, gate
        assert gate.form == PARALLEL_FORM


def test_the_SERIAL_form_carries_NO_worker_flag_in_either_environment():
    for environment in (IMAGE, HOST):
        gate = suite_gate(environment, parallel=False)
        assert "-n" not in gate.argv, gate
        assert gate.form == SERIAL_FORM


def test_the_two_forms_differ_ONLY_by_the_worker_flag():
    for environment in (IMAGE, HOST):
        serial, parallel = suite_gate(environment, False), suite_gate(environment, True)
        assert parallel.argv == (*serial.argv, *PARALLEL)
        assert serial.form != parallel.form


def test_only_the_IMAGE_suite_runs_through_the_wrapper():
    assert suite_gate(IMAGE, True).argv[0] == WRAPPER
    assert WRAPPER not in suite_gate(HOST, True).argv


# --- clause 4: the image is parallel always, the host only where xdist imports ----------


def test_the_static_declaration_takes_the_IMAGE_suite_parallel_and_the_HOST_serial():
    assert GATES == (FLOOR, suite_gate(IMAGE, True), suite_gate(HOST, False))


def test_a_host_WITH_xdist_takes_its_suite_PARALLEL():
    host = [gate for gate in declared(lambda: True) if gate.environment == HOST]
    assert host == [suite_gate(HOST, True)]


def test_a_host_WITHOUT_xdist_takes_its_suite_SERIAL_and_the_image_stays_PARALLEL():
    taken = declared(lambda: False)
    assert taken == GATES
    assert suite_gate(IMAGE, True) in taken


def _interpreter(tmp_path, exit_code: int) -> str:
    stub = tmp_path / f"python-{exit_code}"
    stub.write_text(f"#!/bin/sh\nexit {exit_code}\n", encoding="utf-8")
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    return str(stub)


def test_importability_is_asked_of_THE_GATES_OWN_interpreter_both_ways(tmp_path):
    assert xdist_importable(_interpreter(tmp_path, 0)) is True
    assert xdist_importable(_interpreter(tmp_path, 1)) is False


def test_an_interpreter_that_is_NOT_THERE_reads_as_serial_and_never_crashes(tmp_path):
    assert xdist_importable(str(tmp_path / "no-such-python")) is False


# --- the reading SAYS which form it took ------------------------------------------------


def test_every_printed_suite_reading_SAYS_ITS_FORM():
    for parallel, form in ((True, PARALLEL_FORM), (False, SERIAL_FORM)):
        printed = "\n".join(render(Outcome(readings=(Reading(suite_gate(HOST, parallel), 0),))))
        assert f"suite [{HOST}] ({form})" in printed, printed


def test_a_gate_with_ONE_form_prints_no_form_at_all():
    printed = "\n".join(render(Outcome(readings=(Reading(FLOOR, 0),))))
    assert f"floor [{IMAGE}] — " in printed, printed


def test_the_merge_gate_takes_the_gates_THIS_HOST_can_take_unless_told(tmp_path, monkeypatch):
    # ⭐ `stage_and_read` with no gates asks `declared()`; the spy returns none, so the run
    #    is UNREAD before any git or gate is touched — and the spy proves it was asked.
    asked: list[bool] = []
    monkeypatch.setattr(mergegate_module, "declared", lambda: asked.append(True) or ())
    outcome = stage_and_read(tmp_path, "branch")
    assert asked == [True]
    assert outcome.unread == "no gate is declared, so nothing was read"
