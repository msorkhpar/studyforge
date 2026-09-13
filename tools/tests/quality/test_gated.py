"""Mirror of `tools/quality/gated.py` (R12).

⛔ **Asserted in BOTH directions** (`W164`'s third clause): a DIRECTLY-gated test is
counted, AND a FIXTURE-gated test is counted. ⭐ **Every module here is SYNTHETIC,
written into a temporary directory, and its gate is a synthetic variable.** ⛔ No test
here names docker, and every census runs with a fake `docker` first on `PATH` that
records any call. So a census that reached the daemon goes RED instead of silently
passing (W162/7 holds the real question for the user).

⭐ **`W165`'s cost block is asserted on SHAPE.** Its handwritten reports carry fixed
`time` attributes, so no assertion reads a wall clock. The one report a real run writes is
asserted only for its lines, never for its figures.
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

import tools.quality.gated as gated_module
from tests.support import assert_package_contract
from tools.quality import CHECKS, NOTICES
from tools.quality.gated import (
    INHABITED,
    SELECTION,
    SPREAD,
    UNREAD,
    UNSEEN,
    Cost,
    cost_of,
    main,
    owed,
    read_timings,
    render,
    render_cost,
    take_census,
)

GATE = "W164_SYNTHETIC_GATE"
REASON = "the synthetic gate is unset"

MODULE = f'''
import os
import pytest


def require_gate():
    if os.environ.get("{GATE}") != "1":
        pytest.skip("{REASON}")


@pytest.fixture(scope="session")
def opened():
    require_gate()
    return "opened"


def test_direct():
    require_gate()


def test_inherited(opened):
    assert opened


class TestGrouped:
    def test_inherited_in_a_class(self, opened):
        assert opened


def test_ungated():
    assert True


def test_skipped_for_another_reason():
    pytest.skip("another reason")
'''

DIRECT = "test_synthetic.py::test_direct"
INHERITED = "test_synthetic.py::test_inherited"
IN_A_CLASS = "test_synthetic.py::TestGrouped::test_inherited_in_a_class"


def _corpus(root: Path, body: str = MODULE) -> tuple[Path, dict[str, str]]:
    """A synthetic test module, and an environment whose `docker` records every call."""
    (root / "test_synthetic.py").write_text(body, encoding="utf-8")
    tools = root / "bin"
    tools.mkdir()
    fake = tools / "docker"
    fake.write_text(f'#!/bin/sh\ntouch "{root / "DOCKER_CALLED"}"\nexit 1\n', encoding="utf-8")
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    environment = dict(os.environ, PATH=f"{tools}{os.pathsep}{os.environ.get('PATH', '')}")
    environment[GATE] = "1"  # ⛔ set on purpose: only `unset` may close it
    return root, environment


@pytest.fixture(scope="module")
def corpus(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict[str, str]]:
    """One synthetic corpus shared by the census readings below."""
    return _corpus(tmp_path_factory.mktemp("gated"))


@pytest.fixture(scope="module")
def census(corpus):
    """The synthetic gate's census, taken once with the gate unset."""
    root, environment = corpus
    return take_census(
        ["test_synthetic.py"],
        root=root,
        unset=[GATE],
        reason=REASON,
        helper="require_gate",
        environ=environment,
    )


def test_states_its_contract():
    assert_package_contract(gated_module, "tools.quality.gated")


def test_it_is_a_command_and_neither_a_floor_check_nor_a_notice():
    names = {getattr(item, "__module__", "") for item in (*CHECKS, *NOTICES)}
    assert "tools.quality.gated" not in names


# --- clause 3: both directions ------------------------------------------------


def test_a_DIRECTLY_gated_test_is_counted(census):
    nodes = [test.node for test in census.tests]
    assert DIRECT in nodes
    assert [test.direct for test in census.tests if test.node == DIRECT] == [True]


def test_a_FIXTURE_gated_test_is_counted_including_one_inside_a_class(census):
    nodes = [test.node for test in census.tests]
    assert INHERITED in nodes
    assert IN_A_CLASS in nodes
    assert {test.node: test.direct for test in census.tests if test.node != DIRECT} == {
        INHERITED: False,
        IN_A_CLASS: False,
    }


def test_the_census_is_exactly_the_gated_population_and_names_its_reason(census):
    assert sorted(test.node for test in census.tests) == sorted([DIRECT, INHERITED, IN_A_CLASS])
    assert census.reasons == (REASON,)
    assert census.verdict == INHABITED


# --- clause 1: the runner, with the gate unset ---------------------------------


def test_the_gate_is_closed_only_by_unset_and_an_open_gate_reads_UNREAD(corpus):
    root, environment = corpus
    opened = take_census(["test_synthetic.py"], root=root, reason=REASON, environ=environment)
    assert opened.tests == ()
    assert opened.verdict == UNREAD


def test_no_census_reaches_docker(corpus, census):
    root, _ = corpus
    assert census.tests, "the census this control guards must be inhabited"
    assert not (root / "DOCKER_CALLED").exists()


# --- clause 2: grep's figure is a LOWER BOUND and names what it cannot see ------


def test_the_grep_figure_is_printed_as_a_LOWER_BOUND_naming_the_unseen_spelling(census):
    lines = render(census)
    assert lines[0].endswith("3 skipped test(s) under 1 reason(s)")
    [grep] = [line for line in lines if line.startswith("grep census")]
    assert "`require_gate(` in the test bodies: 1 — a LOWER BOUND, never exact" in grep
    assert f"grep cannot see {UNSEEN}" in grep
    assert "(2 test(s) in this census inherit one)" in grep
    assert grep.split(" — ", 1)[1].startswith("a LOWER BOUND")
    assert sum("[inherited:" in line for line in lines) == 2


# --- the exit: an empty or unfinished population is never the pass reading -----


def test_main_exits_0_on_an_inhabited_census_and_prints_it(corpus, capsys, monkeypatch):
    root, environment = corpus
    monkeypatch.setattr(os, "environ", environment)
    code = main(["--root", str(root), "--unset", GATE, "--reason", REASON, "test_synthetic.py"])
    assert code == INHABITED
    assert DIRECT in capsys.readouterr().out


def test_an_EMPTY_population_exits_2(tmp_path):
    root, environment = _corpus(tmp_path, "def test_ungated():\n    assert True\n")
    empty = take_census(["test_synthetic.py"], root=root, unset=[GATE], environ=environment)
    assert empty.report_read and empty.tests == ()
    assert empty.verdict == UNREAD
    assert "UNREAD: an empty population" in render(empty)[0]


def test_a_COLLECTION_ERROR_exits_2_even_beside_a_skip(tmp_path):
    root, environment = _corpus(tmp_path)
    (root / "test_broken.py").write_text("import nowhere_to_be_found\n", encoding="utf-8")
    broken = take_census(
        ["test_synthetic.py", "test_broken.py"], root=root, unset=[GATE], environ=environment
    )
    assert broken.verdict == UNREAD
    assert "collection did not finish" in render(broken)[0]


# --- W165: a cost figure over a gated population names its selection and spread --

#: The witness's per-member figures (row W165, RECEIVED, host), one per synthetic member.
WITNESS = {DIRECT: 1.09, INHERITED: 9.5, IN_A_CLASS: 34.7}
UNGATED = "test_synthetic.py::test_ungated"


def _report(path: Path, seconds: dict[str, float]) -> Path:
    """A handwritten `xunit1` report: fixed times, and one test skipped for another reason."""
    cases = []
    for node, time in seconds.items():
        file, *classes, name = node.split("::")
        classname = ".".join(["test_synthetic", *classes])
        attributes = f'file="{file}" classname="{classname}" name="{name}" time="{time}"'
        cases.append(f"<testcase {attributes}/>")
    cases.append(
        '<testcase file="test_synthetic.py" classname="test_synthetic" '
        'name="test_skipped_for_another_reason" time="0.1"><skipped message="x"/></testcase>'
    )
    path.write_text(f"<testsuites><testsuite>{''.join(cases)}</testsuite></testsuites>")
    return path


def _block(output: str) -> list[str]:
    """The printed cost block, from its header to the end."""
    lines = output.splitlines()
    starts = [index for index, line in enumerate(lines) if line.startswith("cost of the gated")]
    assert len(starts) == 1, output
    return lines[starts[0] :]


def test_a_figure_quoted_from_ONE_member_owes_its_spread_and_is_not_the_spread(census, tmp_path):
    timings = read_timings(_report(tmp_path / "r.xml", {**WITNESS, UNGATED: 0.5}))
    whole = cost_of(census, timings)
    cheapest = Cost(((DIRECT, WITNESS[DIRECT]),), whole.gated)
    assert owed(whole) == ()
    assert owed(cheapest) == (SPREAD,)
    [spread] = [line for line in render_cost(whole, "r.xml") if "spread over" in line]
    assert f"min 1.090 s ({DIRECT})" in spread
    assert f"max 34.700 s ({IN_A_CLASS})" in spread
    # ⛔ The per-member ratio, never the witness's file-total "~160x".
    assert spread.endswith("max/min 31.8x per member")


def test_a_gated_figure_naming_only_its_DIRECTORY_owes_its_selection(census):
    gated = tuple(test.node for test in census.tests)
    assert owed(Cost((("tests/docker/", 1.05),), gated)) == (SELECTION, SPREAD)
    assert owed(Cost((("test_synthetic.py", 45.29),), gated)) == (SPREAD,)
    assert owed(Cost(tuple(WITNESS.items()), gated)) == ()


def test_an_UNGATED_timing_owes_nothing_even_from_one_member_under_a_directory():
    # ⛔ The row's MUST-NOT: the clause binds a GATED population, never every timing.
    assert owed(Cost((("tests/", 292.73),), ())) == ()
    assert owed(Cost(((UNGATED, 0.5),), ())) == ()


def test_the_cost_block_names_every_gated_member_by_node_id_and_no_ungated_one(
    corpus, tmp_path, capsys, monkeypatch
):
    root, environment = corpus
    report = _report(tmp_path / "r.xml", {**WITNESS, UNGATED: 0.5})
    monkeypatch.setattr(os, "environ", environment)
    main(["--root", str(root), "--unset", GATE, "--reason", REASON, "--timings", str(report)])
    block = _block(capsys.readouterr().out)
    for node, seconds in WITNESS.items():
        assert f"{seconds:.3f} s  {node}" in "\n".join(block)
    assert sum("spread over 3 timed member(s): min" in line for line in block) == 1
    assert not any(UNGATED in line or "SAMPLE" in line for line in block)
    assert block[-1].endswith("1 ungated timing(s) in the report: outside this clause, not listed")


def test_a_report_timing_SOME_members_is_printed_as_a_SAMPLE_naming_the_untimed(census):
    cost = cost_of(census, {DIRECT: WITNESS[DIRECT]})
    lines = render_cost(cost, "r.xml")
    assert sum(line.strip().startswith("untimed") for line in lines) == 2
    assert any(line.strip() == f"untimed  {IN_A_CLASS}" for line in lines)
    assert lines[-1].endswith("a SAMPLE, not the population's cost: 1 of 3 gated member(s) timed")


def test_the_exit_never_moves_on_a_cost_figure(corpus, tmp_path, capsys, monkeypatch):
    root, environment = corpus
    monkeypatch.setattr(os, "environ", environment)
    unread = tmp_path / "not-a-report.xml"
    unread.write_text("not xml", encoding="utf-8")
    reports = [_report(tmp_path / "sample.xml", {DIRECT: 1.09}), unread]
    base = ["--root", str(root), "--unset", GATE, "--reason", REASON]
    assert [main([*base, "--timings", str(report)]) for report in reports] == [INHABITED] * 2
    assert "cost: UNREAD" in capsys.readouterr().out


def test_a_REAL_report_from_an_opened_synthetic_gate_is_costed_without_reaching_docker(
    corpus, tmp_path, capsys, monkeypatch
):
    root, environment = corpus
    report = tmp_path / "opened.xml"
    command = [
        sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--rootdir={root}",
        "-o", "junit_family=xunit1", f"--junitxml={report}", "test_synthetic.py",
    ]  # fmt: skip
    subprocess.run(command, cwd=root, env=environment, capture_output=True, check=False)
    monkeypatch.setattr(os, "environ", environment)
    main(["--root", str(root), "--unset", GATE, "--reason", REASON, "--timings", str(report)])
    block = _block(capsys.readouterr().out)
    for node in WITNESS:
        assert any(line.endswith(f" s  {node}") for line in block), block
    assert not any("untimed" in line or "SAMPLE" in line for line in block)
    assert not (root / "DOCKER_CALLED").exists()
