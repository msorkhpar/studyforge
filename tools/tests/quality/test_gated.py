"""Mirror of `tools/quality/gated.py` (R12).

⛔ **Asserted in BOTH directions** (`W164`'s third clause): a DIRECTLY-gated test is
counted, AND a FIXTURE-gated test is counted. ⭐ **Every module here is SYNTHETIC,
written into a temporary directory, and its gate is a synthetic variable.** ⛔ No test
here names docker, and every census runs with a fake `docker` first on `PATH` that
records any call. So a census that reached the daemon goes RED instead of silently
passing (W162/7 holds the real question for the user).
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

import tools.quality.gated as gated_module
from tests.support import assert_package_contract
from tools.quality import CHECKS, NOTICES
from tools.quality.gated import INHABITED, UNREAD, UNSEEN, main, render, take_census

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
