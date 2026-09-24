"""Mirror of `tools/quality/report.py` (R12).

⭐ **The skip census's end-to-end arms run a CHILD pytest** through the repository's own root
`conftest.py`, because the disclosure is a line in a run's summary and a line nobody
printed cannot be asserted over a pure function alone.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

from tests.floor.report import (
    DISK_WALK,
    TRACKED_WALK,
    UNREACHABLE,
    WALK_CAVEAT,
    DocumentPopulation,
    Finding,
    format_findings,
    unreachable_population,
    unread_caveat,
)
from tests.support import repository_root


def test_a_finding_renders_where_an_editor_can_jump_to_it():
    finding = Finding(path="src/studyforge/x.py", line=12, rule="size", message="too long.")
    assert str(finding) == "src/studyforge/x.py:12: [size] too long."


def test_clean_says_so_rather_than_saying_nothing():
    # A checker that prints nothing on success is a checker nobody can tell
    # apart from one that failed to run.
    assert format_findings([]) == "quality floor: clean"


def test_findings_are_sorted_so_the_report_is_the_same_everywhere():
    later = Finding(path="src/studyforge/z.py", line=1, rule="size", message="a.")
    earlier = Finding(path="src/studyforge/a.py", line=9, rule="size", message="b.")
    report = format_findings([later, earlier])
    assert report.splitlines()[0].startswith("src/studyforge/a.py")
    assert report.splitlines()[1].startswith("src/studyforge/z.py")


def test_the_count_is_pluralised_honestly():
    one = Finding(path="a.py", line=1, rule="size", message="x.")
    assert format_findings([one]).endswith("quality floor: 1 finding")
    two = Finding(path="b.py", line=1, rule="size", message="x.")
    assert format_findings([one, two]).endswith("quality floor: 2 findings")


# --- what a NOTICE's denominator says about itself -------------------------


def test_the_two_walks_are_the_only_two_and_each_has_a_caveat_entry():
    # ⛔ Two NAMED walks and never a boolean: a reader of a figure must not have
    # to infer that the disk answer is the fallback one.
    assert set(WALK_CAVEAT) == {TRACKED_WALK, DISK_WALK}


def test_only_the_disk_walk_carries_a_caveat():
    # ⭐ `tracked_paths`' third answer wearing a sentence: git failing to answer
    # neither falls through in silence nor fails the build — it SAYS so.
    assert WALK_CAVEAT[TRACKED_WALK] == ""
    caveat = WALK_CAVEAT[DISK_WALK]
    assert "DISK" in caveat
    assert "not reproducible from another checkout" in caveat


def test_a_population_carries_its_paths_and_the_walk_that_found_them():
    population = DocumentPopulation((Path("a.md"),), TRACKED_WALK)
    assert population.paths == (Path("a.md"),)
    assert population.walk == TRACKED_WALK
    assert population.unread == 0


# --- what the walk did NOT read --------------------------------------------


def test_a_tracked_figure_says_what_its_walk_did_not_read_whether_or_not_it_fired():
    # ⛔ A figure states its denominator, and that is why the sentence is not fired-only: an office
    # believing a green over its own unstaged handoff needs to read `0`, and a
    # sentence that appears only when something was missed never gives it one.
    quiet = unread_caveat(DocumentPopulation((Path("a.md"),), TRACKED_WALK))
    loud = unread_caveat(DocumentPopulation((Path("a.md"),), TRACKED_WALK, 3))
    assert "0 markdown documents" in quiet
    assert "3 markdown documents" in loud
    assert "`git add`ed gets a reading the merge will not repeat" in quiet


def test_the_disk_walk_claims_NOTHING_about_an_index_git_never_answered_for():
    # ⚠️ `tracked_paths`' third answer: a `0` here would say git had answered, and
    # `WALK_CAVEAT[DISK_WALK]` already says what that population costs a reader.
    assert unread_caveat(DocumentPopulation((Path("a.md"),), DISK_WALK)) == ""
    assert WALK_CAVEAT[DISK_WALK] != ""


# --- the population a run could not reach ----------------------------------

#: A bound on each child run. ⚠️ A bound rather than a hope: a hang is no verdict.
TIMEOUT = 180

#: ⛔ Where the child's `conftest.py` finds the REAL root one. An environment variable
#: rather than a path written into the fixture, so no path is written into any file (R7).
ROOT_CONFTEST_ENV = "STUDYFORGE_W158_ROOT_CONFTEST"

#: The child suite's `conftest.py`: the repository's own summary hook, loaded by path.
#: ⛔ The REAL hook and not a copy, or a defect in the wiring would pass here.
CHILD_CONFTEST = f"""
import importlib.util, os
_spec = importlib.util.spec_from_file_location("root_conftest", os.environ["{ROOT_CONFTEST_ENV}"])
_root = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_root)
pytest_terminal_summary = _root.pytest_terminal_summary
"""


def _skipped(reason: str) -> SimpleNamespace:
    """A skipped report the way pytest tallies one: `(path, line, "Skipped: reason")`."""
    return SimpleNamespace(nodeid="t.py::t", longrepr=("t.py", 1, f"Skipped: {reason}"))


def _pytest(arguments: list[str], cwd: Path, **extra: str) -> subprocess.CompletedProcess:
    """A child pytest with the repository importable and nothing inherited that steers it."""
    env = dict(os.environ)
    env.pop("PYTEST_ADDOPTS", None)
    env["PYTHONPATH"] = os.pathsep.join([str(repository_root()), str(repository_root() / "src")])
    env[ROOT_CONFTEST_ENV] = str(repository_root() / "conftest.py")
    env.update(extra)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *arguments],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
    )


def _child_suite(root: Path, body: str) -> subprocess.CompletedProcess:
    """Run a synthetic suite in a harness-minted directory through the root summary hook."""
    (root / "conftest.py").write_text(CHILD_CONFTEST, encoding="utf-8")
    (root / "test_child.py").write_text(f"import pytest\n\n{body}", encoding="utf-8")
    return _pytest(["-q", str(root)], root)


def _disclosure(output: str) -> list[str]:
    """The disclosure as a run printed it: the label line and the indented reasons under it."""
    lines = output.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(f"{UNREACHABLE}: "))
    found = [lines[start]]
    for line in lines[start + 1 :]:
        if not line.startswith("  "):
            break
        found.append(line)
    return found


def test_an_empty_population_is_still_PRINTED_as_zero():
    # ⛔ The arm a careless repair deletes: `0` is a reading, never an absence.
    assert unreachable_population({}) == [
        f"{UNREACHABLE}: 0 skipped test(s) — this run reached every test it collected"
    ]


def test_the_count_and_every_reason_are_DERIVED_from_the_tally():
    # ⛔ Reasons minted at run time, so no typed list of reasons can produce them.
    first, second = f"absent {uuid.uuid4().hex}", f"absent {uuid.uuid4().hex}"
    stats = {"skipped": [_skipped(first), _skipped(second), _skipped(first)], "passed": [1]}
    lines = unreachable_population(stats)
    assert lines[0].startswith(f"{UNREACHABLE}: 3 skipped test(s) — ")
    assert lines[1:] == [f"  2 × {first}", f"  1 × {second}"]


def test_a_run_that_reaches_everything_prints_the_EMPTY_population_and_exits_0(tmp_path):
    result = _child_suite(tmp_path, "def test_one():\n    pass\n")
    assert result.returncode == 0, result.stdout + result.stderr
    assert _disclosure(result.stdout) == unreachable_population({})


def test_a_run_with_skips_prints_a_NON_EMPTY_population_and_its_exit_does_not_move(tmp_path):
    reason = f"a sibling {uuid.uuid4().hex} is not checked out"
    body = f"def test_one():\n    pytest.skip({reason!r})\n\ndef test_two():\n    pass\n"
    result = _child_suite(tmp_path, body)
    # ⛔ Host state is a disclosure, never a failure — the skip-only run is still `0`.
    assert result.returncode == 0, result.stdout + result.stderr
    lines = _disclosure(result.stdout)
    assert lines[0].startswith(f"{UNREACHABLE}: 1 skipped test(s) — ")
    assert lines[1:] == [f"  1 × {reason}"]


def test_the_REAL_sibling_assertions_with_the_workspace_absent_print_a_NON_EMPTY_one(tmp_path):
    # ⭐ The row's own population: the Java corpus absent, as it is in the pinned container,
    # made absent HERE by pointing the workspace at an empty harness-minted directory.
    module = "tests/studyforge/corpus/placement/test_corpora.py"
    result = _pytest(["-q", module], repository_root(), STUDYFORGE_WORKSPACE=str(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr
    lines = _disclosure(result.stdout)
    assert not lines[0].startswith(f"{UNREACHABLE}: 0 "), lines
    assert any("is not checked out beside this repository" in line for line in lines[1:]), lines
