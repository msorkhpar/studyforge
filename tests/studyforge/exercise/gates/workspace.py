"""A real authored exercise on disk, whose tests are really run — so a plant's effect is real.

⛔ **The gate framework's acceptance is *each gate refuses its planted defect*, and a plant
is not a plant until its effect is OBSERVED.** ⭐ So nothing here stubs a run:
every reading a gate is given comes out of a real `pytest` process over real
files, and each plant is a real edit to one of those files. ⚠️ A stubbed
`Attempt` would let a plant be a value typed into a dictionary — and a negative
control that reads the same as the experiment has controlled nothing.

⭐ **The exercise is deliberately tiny and deliberately Python**: the suite
already runs under `pytest`, so the runner is present wherever this test is,
and one run costs a fraction of a second. ⛔ The framework knows nothing about
it (R1) — it is a fixture in the test tree, and the gates read it as data.

## ⛔ Why the case ids are bare test names

⚠️ **MEASURED here**: `pytest --junit-xml` writes no `file` attribute on a
`testcase`, so `report._spells`'s node-id spelling has nothing to rebuild from
and its bare-name arm is the one that matches. ⭐ That is the right id for this
runner and it is what an author would be told to write down.

## ⚠️ A JUnit report carries the machine's hostname

⛔ **MEASURED**: `pytest`'s report writes `hostname="…"` on every `testsuite`.
⭐ Every report here is written under `tmp_path`, outside the repository, and
nothing reads or prints that attribute. ⚠️ It is a hazard for whoever commits
a report into a corpus, which is why a bundle's file set is closed.
"""

from __future__ import annotations

import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from studyforge.exercise import EDGE, MAIN, Case, Exercise, Origin, Report
from studyforge.exercise.gates import (
    ORIGIN_ROLE,
    Cited,
    Evidence,
    Run,
    check,
    digest_of_bytes,
    folded,
    plant_role,
    taken_over,
)
from tests.support import run

WHERE = "corpus/adding-up/unit-01/practice-1"

#: The ask itself, and the two edges of it — each named by the id its runner
#: spells and by the one sentence a reader is shown.
MAIN_CASE = Case(id="test_totals_a_list", kind=MAIN, says="a basket adds up")
EMPTY_EDGE = Case(id="test_an_empty_list_totals_zero", kind=EDGE, says="an empty basket is zero")
NEGATIVE_EDGE = Case(
    id="test_a_negative_price_is_refused", kind=EDGE, says="a negative price is refused"
)
CASES = (MAIN_CASE, EMPTY_EDGE, NEGATIVE_EDGE)

#: The passage of the source this exercise was built from, and its bytes —
#: ⭐ the ledger's entry for it is `digest_of_bytes(SOURCE)` unless a plant drifts it.
ORIGIN_PATH = "lessons/adding-up.md"
ORIGIN_SECTION = "Adding up a basket"
SOURCE = b"A basket is a list of prices. Adding one up is a sum, with two edges.\n"

#: What the reader is asked, and where each file of the bundle sits.
STATEMENT = "Write `total(prices)`: the sum of a basket, zero when empty, refusing negatives.\n"

TESTS = """from solution import total


def test_totals_a_list():
    assert total([2, 3, 5]) == 10


def test_an_empty_list_totals_zero():
    assert total([]) == 0


def test_a_negative_price_is_refused():
    try:
        total([2, -1])
    except ValueError:
        return
    raise AssertionError("a negative price should have been refused")
"""

REFERENCE = """def total(prices):
    for price in prices:
        if price < 0:
            raise ValueError("a price is never negative")
    return sum(prices)
"""

STARTER = """def total(prices):
    raise NotImplementedError("write me")
"""

#: Solves the ask and refuses negatives, but falls over on an empty basket.
PLANT_EMPTY = """def total(prices):
    for price in prices:
        if price < 0:
            raise ValueError("a price is never negative")
    return prices[0] + sum(prices[1:])
"""

#: Solves the ask and handles an empty basket, but takes any price at all.
PLANT_NEGATIVE = """def total(prices):
    return sum(prices)
"""

#: ⛔ The plants, each a real edit to a real file. Each one is named by what it
#: breaks, never by the gate it is expected to break: a plant named after its
#: gate is a plant nobody checked the effect of.
NONE = "no plant"
VACUOUS_TEST = "the main ask's test asserts nothing"
FLAKY_TEST = "one test disagrees with itself between runs"
PLANT_SOLVES_ITS_EDGE = "the solution planted to ignore an edge handles it"
UNMAPPED_TEST = "the tests carry one the case map does not name"
DRIFTED_ORIGIN = "the source has changed since the exercise was built from it"
STARTER_THROWS_WHAT_AN_EDGE_EXPECTS = "the starter raises the exception an edge's test expects"

#: ⚠️ A starter that "is not written yet" by raising the very exception the
#: negative-price edge expects: that edge's test passes on it, as a Java course measured.
_STARTER_RAISING_VALUEERROR = """def total(prices):
    raise ValueError("write me")
"""

#: The vacuous replacement for the main ask's test — ⭐ it passes on anything
#: that imports, which is what makes it vacuous.
_VACUOUS = """def test_totals_a_list():
    assert True
"""

#: A test whose answer depends on whether it has run before, through a file it
#: leaves in the workspace. ⭐ Real flakiness, not a stubbed disagreement.
_FLAKY = """def test_a_negative_price_is_refused():
    import pathlib

    seen = pathlib.Path("seen-once")
    if seen.exists():
        raise AssertionError("this run disagrees with the last one")
    seen.write_text("once")
    try:
        total([2, -1])
    except ValueError:
        return
    raise AssertionError("a negative price should have been refused")
"""

#: A test nothing in the case map names.
_UNMAPPED = """

def test_a_basket_is_never_none():
    assert total([1]) == 1
"""


@dataclass(frozen=True, slots=True)
class Reading:
    """What one gate suite produced, kept beside the runs it was read off."""

    evidence: Evidence
    verdicts: tuple

    def verdict(self, gate: str):
        """This gate's verdict, by id."""
        return next(entry for entry in self.verdicts if entry.id == gate)

    def refused(self) -> tuple[str, ...]:
        """Every gate that did not hold, in order."""
        return tuple(entry.id for entry in self.verdicts if not entry.held)


class Bundle:
    """One authored exercise written to disk, optionally with one defect planted in it."""

    def __init__(self, root: Path, plant: str = NONE) -> None:
        self.root = root
        self.plant = plant
        (root / "work").mkdir(parents=True, exist_ok=True)
        (root / "reports").mkdir(parents=True, exist_ok=True)
        (root / "work" / "statement.md").write_text(STATEMENT, encoding="utf-8")
        (root / "work" / "reference.py").write_text(REFERENCE, encoding="utf-8")
        (root / "work" / "starter.py").write_text(self._starter(), encoding="utf-8")
        (root / "work" / "plant-empty.py").write_text(self._plant_empty(), encoding="utf-8")
        (root / "work" / "plant-negative.py").write_text(PLANT_NEGATIVE, encoding="utf-8")
        (root / "work" / "test_solution.py").write_text(self._tests(), encoding="utf-8")

    @property
    def exercise(self) -> Exercise:
        """The record the gates are read over: the case map, the report, the origin."""
        return Exercise(
            main_path="work/solution.py",
            test_path="work/test_solution.py",
            run_command=("python3", "work/solution.py"),
            test_command=("python3", "-m", "pytest", "work"),
            provenance="generated",
            trust="advisory",
            cases=CASES,
            report=Report(format="junit", path="reports/report.xml"),
            origin=Origin(path=ORIGIN_PATH, section=ORIGIN_SECTION),
        )

    @property
    def files(self) -> tuple[tuple[str, str], ...]:
        """Every input the gate reading is taken over, with the role each plays."""
        return (
            ("statement", "work/statement.md"),
            ("starter", "work/starter.py"),
            ("reference", "work/reference.py"),
            ("tests", "work/test_solution.py"),
            (plant_role(EMPTY_EDGE), "work/plant-empty.py"),
            (plant_role(NEGATIVE_EDGE), "work/plant-negative.py"),
        )

    @property
    def inputs(self):
        """The digests of those files, taken now."""
        return taken_over(self.root, self.files, WHERE)

    @property
    def origins(self) -> tuple[Cited, ...]:
        """What the source digested to when this exercise was authored."""
        return (
            Cited(
                role=ORIGIN_ROLE,
                path=ORIGIN_PATH,
                section=ORIGIN_SECTION,
                digest=digest_of_bytes(SOURCE),
            ),
        )

    @property
    def ledger(self) -> dict[str, str]:
        """What the source digests to NOW — ⛔ the only thing the drift plant moves."""
        source = SOURCE + b"And a third edge was added to the page later.\n"
        return {ORIGIN_PATH: digest_of_bytes(source if self.plant == DRIFTED_ORIGIN else SOURCE)}

    def attempt(self, role: str, number: int) -> Run:
        """Put this role's solution in place, run the tests for real, and fold the report."""
        (self.root / "work" / "solution.py").write_text(self._solutions()[role], encoding="utf-8")
        shutil.rmtree(self.root / "work" / "__pycache__", ignore_errors=True)
        shutil.rmtree(self.root / "reports", ignore_errors=True)
        (self.root / "reports").mkdir()
        started = time.time()
        finished = run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "--junit-xml",
                "../reports/report.xml",
                ".",
            ],
            self.root / "work",
        )
        return folded(
            self.exercise, self.root, role, number, finished.returncode, WHERE, started=started
        )

    def read(self) -> Reading:
        """Take every run the gates require, then read all five gates off them."""
        evidence = Evidence.taken(self.exercise, self.attempt, WHERE)
        return Reading(
            evidence=evidence,
            verdicts=check(self.exercise, evidence, self.origins, self.ledger, WHERE),
        )

    def _solutions(self) -> dict[str, str]:
        """Which file stands in for the reader's answer, per role."""
        return {
            "reference": REFERENCE,
            "starter": self._starter(),
            plant_role(EMPTY_EDGE): self._plant_empty(),
            plant_role(NEGATIVE_EDGE): PLANT_NEGATIVE,
        }

    def _starter(self) -> str:
        """The starter, or the one that raises what the negative-price edge expects."""
        if self.plant == STARTER_THROWS_WHAT_AN_EDGE_EXPECTS:
            return _STARTER_RAISING_VALUEERROR
        return STARTER

    def _plant_empty(self) -> str:
        """⛔ Under `PLANT_SOLVES_ITS_EDGE` this is the reference: it solves the edge."""
        return REFERENCE if self.plant == PLANT_SOLVES_ITS_EDGE else PLANT_EMPTY

    def _tests(self) -> str:
        """The test file, with whichever test-level plant this bundle carries."""
        if self.plant == VACUOUS_TEST:
            return TESTS.replace(
                "def test_totals_a_list():\n    assert total([2, 3, 5]) == 10\n", _VACUOUS
            )
        if self.plant == FLAKY_TEST:
            return TESTS[: TESTS.index("def test_a_negative_price_is_refused")] + _FLAKY
        if self.plant == UNMAPPED_TEST:
            return TESTS + _UNMAPPED
        return TESTS
