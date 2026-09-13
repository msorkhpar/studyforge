r"""`W164`: a census of a GATED population is taken from the RUNNER, never from `grep`.

**What it does.** Runs pytest over the paths it is given, with each `--unset` variable
removed from the environment. It reads the runner's own report and prints every test the
runner SKIPPED, with its reason and a count. ⭐ **A gate is not only where it is called:
a fixture propagates it.** The runner resolves fixtures, so this census counts a test
that inherits its gate. `grep` cannot see that test.

With `--helper NAME` it also prints the census `grep` would take: the gated tests whose
own body names `NAME(`. ⛔ **That figure is printed as a LOWER BOUND, and the line names
the spelling it cannot see**, which is a gate inherited through a fixture. This is
Ruling 280's form, carried from citations to gates.

`W165`: with `--timings REPORT` it also prints the COST of that population. The report
is a JUnit report from a run this command did not take, because this command never opens
a gate. Each gated member gets a line with its own seconds and its node id, and the block
ends with min and max. ⛔ **A report that times only some members is printed as a SAMPLE,
with the untimed members named.** A timing of an ungated test is outside the clause, and
the block does not list it. `owed(Cost)` is the clause as a predicate: a figure over a
gated population owes its SELECTION if it names only a directory, and its SPREAD if some
gated member has no figure. ⛔ An ungated figure owes nothing.

- Exit `0`: the census is inhabited, and the runner collected without error.
- Exit `2`: no test was skipped, or the runner produced no report, or it did not finish
  collecting. ⛔ An empty population is never the pass reading (Ruling 191). A census
  over a collection that errored is a silent under-count.
- ⛔ **A cost figure never moves the exit**, whether it is whole, a sample, or unread.

**How you use it.**

    python3 -m tools.quality.gated --unset STUDYFORGE_DOCKER_TESTS \
        --reason STUDYFORGE_DOCKER_TESTS --helper require_docker_run tests/docker/

`take_census(paths, ...)` returns the `Census` the command prints, and `render` gives
the printed lines. The clause lives in `docs/conventions/review-rubric.md`, under the
`W164` heading beside Ruling 142. With a report, add `--timings <report.xml>`;
`read_timings`, `cost_of` and `render_cost` give the cost block, under the `W165` heading.

**Depends on.** `argparse`, `ast`, `os`, `re`, `subprocess`, `sys`, `tempfile`,
`xml.etree.ElementTree`, `dataclasses` and `pathlib`. Pytest is run as a subprocess and
is never imported.

## ⛔ WHAT IT MUST NOT BECOME (the row)

- ⛔ **It does not ban `grep`**, and it prints `grep`'s figure beside its own.
- ⛔ **It changes no fixture.** A session fixture that gates once is the correct design.
  The defect was in how it is counted.
- ⛔ **It is not in `CHECKS` or `NOTICES`.** A floor check gives the same reading for
  the same files and never runs a test; this runs the suite.
- ⛔ **It only REMOVES variables and never sets one.** So it opens no gate, and a census
  of the docker population makes no docker call that a default test run would not.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

#: The exits this command returns.
INHABITED = 0
UNREAD = 2

#: Pytest's own exits that mean collection finished: all passed, or some failed.
#: ⛔ Anything else (interrupted, usage error, internal error, nothing collected) leaves
#: the population unknown.
COLLECTED = frozenset({0, 1})

#: The spelling a `grep` census cannot see, named on the line that prints its figure.
UNSEEN = "a gate inherited through a fixture"


@dataclass(frozen=True)
class Gated:
    """One skipped test: its node id, the runner's reason, and whether its body calls the helper."""

    node: str
    reason: str
    direct: bool | None  # None when no `--helper` was given, or the body was not found


@dataclass(frozen=True)
class Census:
    """What the runner reported: its exit, every gated test, and the helper read for grep."""

    pytest_exit: int
    report_read: bool
    tests: tuple[Gated, ...]
    helper: str | None

    @property
    def verdict(self) -> int:
        """`INHABITED` only for a finished collection with at least one skipped test."""
        if self.report_read and self.pytest_exit in COLLECTED and self.tests:
            return INHABITED
        return UNREAD

    @property
    def reasons(self) -> tuple[str, ...]:
        """The distinct reasons, in first-seen order."""
        return tuple(dict.fromkeys(test.reason for test in self.tests))


def _module_of(file: str) -> str:
    """Return the dotted module a report's `file` attribute names."""
    return file.removesuffix(".py").replace("/", ".").replace("\\", ".")


def _node_id(file: str, classname: str, name: str) -> str:
    """`file::Class::name`, rebuilt from an `xunit1` testcase."""
    module = _module_of(file)
    classes = classname[len(module) + 1 :].split(".") if classname.startswith(f"{module}.") else []
    return "::".join([file, *[part for part in classes if part], name])


def _body_calls(source: Path, line: int, name: str, helper: str) -> bool | None:
    """Whether the test's own body names `helper(`, as a grep of that body reads it.

    `line` is the report's zero-based line, which is the `def` or its first decorator.
    """
    try:
        text = source.read_text(encoding="utf-8")
        tree = ast.parse(text)
    except OSError, SyntaxError, ValueError:
        return None
    bare = name.partition("[")[0]
    call = re.compile(rf"\b{re.escape(helper)}\s*\(")
    lines = text.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != bare:
            continue
        starts = {node.lineno - 1, *(item.lineno - 1 for item in node.decorator_list)}
        if line not in starts:
            continue
        body = lines[node.body[0].lineno - 1 : node.end_lineno]
        return any(call.search(row) for row in body)
    return None


def read_report(report: Path, root: Path, helper: str | None) -> tuple[Gated, ...]:
    """Every testcase the `xunit1` report marks skipped (an xfail is not a gate)."""
    tests: list[Gated] = []
    for case in ElementTree.parse(report).getroot().iter("testcase"):
        skipped = case.find("skipped")
        if skipped is None or skipped.get("type") == "pytest.xfail":
            continue
        file = case.get("file", "")
        name = case.get("name", "")
        direct = None
        if helper is not None and file and case.get("line", "").isdigit():
            direct = _body_calls(root / file, int(case.get("line", "")), name, helper)
        node = _node_id(file, case.get("classname", ""), name)
        tests.append(Gated(node=node, reason=skipped.get("message", ""), direct=direct))
    return tuple(tests)


def take_census(
    paths: Sequence[str],
    *,
    root: Path,
    unset: Sequence[str] = (),
    reason: str | None = None,
    helper: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> Census:
    """Run pytest over `paths` from `root` with `unset` removed, and read what it skipped.

    `reason`, when given, keeps only the tests whose skip reason contains it.
    """
    environment = dict(os.environ if environ is None else environ)
    for name in unset:
        environment.pop(name, None)
    with tempfile.TemporaryDirectory(prefix="gated-census-") as scratch:
        report = Path(scratch) / "report.xml"
        command = [
            sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
            f"--rootdir={root}", "-o", "junit_family=xunit1", f"--junitxml={report}",
            *paths,
        ]  # fmt: skip
        finished = subprocess.run(
            command, cwd=root, env=environment, capture_output=True, text=True, check=False
        )
        if not report.is_file():
            return Census(finished.returncode, False, (), helper)
        tests = read_report(report, root, helper)
    if reason is not None:
        tests = tuple(test for test in tests if reason in test.reason)
    return Census(finished.returncode, True, tests, helper)


def render(census: Census) -> list[str]:
    """Return the printed census: a count header, each reason with its tests, then grep."""
    if not census.report_read:
        return [f"gated census: UNREAD — pytest exited {census.pytest_exit} and wrote no report"]
    header = (
        f"gated census from the runner (pytest exit {census.pytest_exit}): "
        f"{len(census.tests)} skipped test(s) under {len(census.reasons)} reason(s)"
    )
    if census.pytest_exit not in COLLECTED:
        header += " — UNREAD: collection did not finish, so the population is unknown"
    elif not census.tests:
        header += " — UNREAD: an empty population is not the pass reading (Ruling 191)"
    lines = [header]
    for reason in census.reasons:
        lines.append(f"  reason: {reason}")
        for test in census.tests:
            if test.reason != reason:
                continue
            through_fixture = test.direct is False
            mark = "  [inherited: its body does not call the helper]" if through_fixture else ""
            lines.append(f"    {test.node}{mark}")
    if census.helper is not None:
        seen = sum(1 for test in census.tests if test.direct)
        inherited = sum(1 for test in census.tests if test.direct is False)
        lines.append(
            f"grep census of `{census.helper}(` in the test bodies: {seen} — a LOWER BOUND, "
            f"never exact: grep cannot see {UNSEEN} "
            f"({inherited} test(s) in this census inherit one)"
        )
    return lines


#: What a cost figure over a gated population can owe (`W165`).
SELECTION = "selection"
SPREAD = "spread"


@dataclass(frozen=True)
class Cost:
    """A cost figure: each selection it names with its seconds, and the gated population.

    `gated` is empty for a timing of an ungated population.
    """

    seconds: tuple[tuple[str, float], ...]
    gated: tuple[str, ...]


def _names_only_a_directory(selection: str) -> bool:
    """Return whether a selection is neither a node id nor a `.py` file."""
    return "::" not in selection and not selection.endswith(".py")


def owed(cost: Cost) -> tuple[str, ...]:
    """Return what `cost` still owes under `W165`. ⛔ An ungated figure owes nothing."""
    if not cost.gated:
        return ()
    named = [selection for selection, _ in cost.seconds]
    owes = []
    if not named or any(_names_only_a_directory(selection) for selection in named):
        owes.append(SELECTION)
    if not set(cost.gated) <= set(named):
        owes.append(SPREAD)
    return tuple(owes)


def read_timings(report: Path) -> dict[str, float] | None:
    """Return every testcase the report RAN, node id to seconds, or `None` if unreadable."""
    try:
        root = ElementTree.parse(report).getroot()
    except OSError, ElementTree.ParseError:
        return None
    timings: dict[str, float] = {}
    for case in root.iter("testcase"):
        if case.find("skipped") is not None:
            continue
        try:
            seconds = float(case.get("time", ""))
        except ValueError:
            continue
        node = _node_id(case.get("file", ""), case.get("classname", ""), case.get("name", ""))
        timings[node] = seconds
    return timings


def cost_of(census: Census, timings: Mapping[str, float]) -> Cost:
    """Return the census's gated members that `timings` ran, with their seconds."""
    gated = tuple(test.node for test in census.tests)
    return Cost(tuple((node, timings[node]) for node in gated if node in timings), gated)


def render_cost(cost: Cost, source: str, ungated: int = 0) -> list[str]:
    """Return the cost block: a line per gated member, then min and max, then any sample."""
    lines = [
        f"cost of the gated population, read from {source} "
        "(a run this command did not take; the exit never moves on it):"
    ]
    timed = dict(cost.seconds)
    for node in cost.gated:
        figure = f"{timed[node]:.3f} s" if node in timed else "untimed"
        lines.append(f"  {figure:>12}  {node}")
    if cost.seconds:
        low = min(cost.seconds, key=lambda pair: pair[1])
        high = max(cost.seconds, key=lambda pair: pair[1])
        spread = f"min {low[1]:.3f} s ({low[0]}) · max {high[1]:.3f} s ({high[0]})"
        if low[1] > 0:
            spread += f" · max/min {high[1] / low[1]:.1f}x per member"
        lines.append(f"  spread over {len(cost.seconds)} timed member(s): {spread}")
    if SPREAD in owed(cost):
        lines.append(
            f"  a SAMPLE, not the population's cost: {len(cost.seconds)} of "
            f"{len(cost.gated)} gated member(s) timed"
        )
    if ungated:
        lines.append(
            f"  {ungated} ungated timing(s) in the report: outside this clause, not listed"
        )
    return lines


def main(argv: list[str] | None = None) -> int:
    """Take the census over the given paths, print it, and return its verdict."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.quality.gated",
        description="Count a gated test population from the runner, not from grep (W164).",
    )
    parser.add_argument("paths", nargs="*", help="test paths for pytest (default: all)")
    parser.add_argument("--root", type=Path, default=Path("."), help="the repository root")
    parser.add_argument(
        "--unset", action="append", default=[], help="an environment variable to remove"
    )
    parser.add_argument("--reason", help="keep only skips whose reason contains this text")
    parser.add_argument("--helper", help="the gate's helper, for the grep lower bound")
    parser.add_argument("--timings", type=Path, help="a JUnit report to cost the population by")
    arguments = parser.parse_args(argv)
    census = take_census(
        arguments.paths,
        root=arguments.root.resolve(),
        unset=arguments.unset,
        reason=arguments.reason,
        helper=arguments.helper,
    )
    print("\n".join(render(census)))
    if arguments.timings is not None and census.tests:
        timings = read_timings(arguments.timings)
        if timings is None:
            print(f"cost: UNREAD — {arguments.timings} is not a readable JUnit report")
        else:
            cost = cost_of(census, timings)
            ungated = sum(1 for node in timings if node not in cost.gated)
            print("\n".join(render_cost(cost, str(arguments.timings), ungated)))
    return census.verdict


if __name__ == "__main__":  # pragma: no cover - the CLI's one line
    sys.exit(main())
