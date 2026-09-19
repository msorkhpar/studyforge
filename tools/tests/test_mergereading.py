"""Mirror of `tools/mergereading.py` (R12): what a reading SAYS about its scope (`W366`).

⭐ Every reading here is built by hand — a `Gate`, an exit code, the ids its summary named —
so what `render` prints is asserted without a merge, a git repository or a docker daemon.
The merge itself, and the planted hidden dependency, are `test_mergegate_selection.py`'s.
"""

from __future__ import annotations

import tools.mergegate as mergegate_module
import tools.mergereading as mergereading_module
from tests.support import assert_package_contract
from tools.gates import HOST, Gate
from tools.mergereading import MERGED, REFUSED, Outcome, Reading, render

SUITE = Gate("suite", HOST, ("pytest",), "the host's own answer")


def _suite(scope: str = "", audit: frozenset[str] | None = None) -> Gate:
    return Gate(SUITE.name, SUITE.environment, SUITE.argv, SUITE.answers, "", scope, audit)


def _outcome(*readings: Reading, restored: bool = True) -> Outcome:
    return Outcome(readings=readings, tip_before="a" * 40, restored=restored, scope=("scope: x",))


def test_states_its_contract():
    assert_package_contract(mergereading_module, "tools.mergereading")


def test_the_merge_gate_RE_EXPORTS_every_name_a_caller_already_reads():
    # ⛔ A split, not a rename: `tools.quality.certify` imports `Reading` from `mergegate`.
    for name in ("Reading", "Outcome", "render", "MERGED", "REFUSED", "UNREAD"):
        assert getattr(mergegate_module, name) is getattr(mergereading_module, name), name


# --- clause 3: a targeted GREEN is never printed as a full one --------------------------


def test_a_TARGETED_green_says_it_read_a_SELECTION():
    lines = render(_outcome(Reading(_suite("SELECTED 3 whole test file(s)"), 0)))
    assert "(SELECTED 3 whole test file(s))" in lines[-2]
    assert lines[-1].endswith("the suite read a SELECTION, not the full suite")
    assert _outcome(Reading(_suite("SELECTED x"), 0)).verdict == MERGED


def test_a_FULL_green_carries_no_such_qualifier():
    lines = render(_outcome(Reading(_suite("FULL"), 0)))
    assert lines[-1] == "⭐ PASSED: every declared gate is green on the merged tree"


def test_the_SCOPE_lines_are_printed_before_any_gate():
    lines = render(_outcome(Reading(_suite("FULL"), 0)))
    assert lines.index("scope: x") < next(i for i, line in enumerate(lines) if "exit 0" in line)


# --- clause 4: the audit, RED by name ---------------------------------------------------


def test_an_AUDIT_names_every_failure_the_selection_would_have_MISSED():
    gate = _suite("FULL, AUDITING the selection", frozenset({"tests/test_a.py"}))
    reading = Reading(gate, 1, ("tests/test_a.py::test_in", "tests/test_b.py::test_hidden"))
    assert reading.missed == ("tests/test_b.py::test_hidden",)
    lines = render(_outcome(reading))
    assert any(
        "⛔ AUDIT RED [host]: the selection would have MISSED tests/test_b.py::test_hidden" in line
        for line in lines
    ), lines
    assert not any("test_in" in line and "MISSED" in line for line in lines)
    assert _outcome(reading).verdict == REFUSED


def test_an_AUDIT_whose_failures_all_lie_INSIDE_the_selection_says_so():
    gate = _suite("FULL, AUDITING the selection", frozenset({"tests/test_a.py"}))
    lines = render(_outcome(Reading(gate, 1, ("tests/test_a.py::test_in",))))
    assert any("every failure lies inside the selection" in line for line in lines)
    assert not any("MISSED" in line for line in lines)


def test_a_GREEN_audit_says_the_selection_missed_nothing():
    gate = _suite("FULL, AUDITING the selection", frozenset())
    lines = render(_outcome(Reading(gate, 0)))
    assert any("⭐ AUDIT GREEN [host]" in line for line in lines)


def test_a_red_audit_that_NAMED_no_test_is_UNREAD_never_green():
    gate = _suite("FULL, AUDITING the selection", frozenset())
    lines = render(_outcome(Reading(gate, 2)))
    assert any("⛔ AUDIT UNREAD [host]" in line for line in lines)
    assert not any("AUDIT GREEN" in line for line in lines)


def test_a_gate_that_audits_NOTHING_prints_no_audit_line():
    lines = render(_outcome(Reading(_suite("FULL"), 1, ("tests/test_b.py::test_x",))))
    assert Reading(_suite("FULL"), 1, ("tests/test_b.py::test_x",)).missed == ()
    assert not any("AUDIT" in line for line in lines)
