"""A TypeScript practice is graded with `node --test` through the framework's own gates, G1 to G5.

⭐ **Every reading is a real `node --test` process** over real files (Node's built-in type
stripping, no compiler, no install), so what each gate reads comes out of a JUnit report and
not out of a verdict typed here. The optional `tsc --noEmit` step runs a real pinned
TypeScript, put on the run by `STUDYFORGE_TSC_DIR` (a directory holding the unpacked
`typescript` package); those tests are skipped without it.

**What it asserts.**
- the reference passes and the starter and every plant fail, and the output of EACH failing
  run names an assertion (`AssertionError`), never a load error, a missing implementation or a
  timeout;
- a failure that an assertion raised is told from one that an error raised, from the report;
- a planted `enum` fails with Node's own message, kept by the run-output filter, and is a
  finding of the gate when the draft asks for assertion failures only;
- the optional type check refuses a type error by name, and a draft without it is unchanged;
- a report written to a directory that does not exist is named by the gate that found none.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

import pytest

from studyforge.execute.quiet import Quiet, select
from studyforge.exercise import EDGE, MAIN, Case, Exercise, ExerciseError, Report, breakdown_of
from studyforge.exercise.gates import G1, G2, G3, G4, G5
from studyforge.skills.exercises import Ran, gate_code
from tests.studyforge.skills.exercises import node_practice as practice
from tests.studyforge.skills.exercises.authoring import Running
from tests.studyforge.skills.exercises.test_pytest_practice import _brief, _g
from tests.support import run

TSC_DIR = os.environ.get("STUDYFORGE_TSC_DIR")
needs_tsc = pytest.mark.skipif(not TSC_DIR, reason="set STUDYFORGE_TSC_DIR to a typescript package")

#: What a failing run must NOT say: the failure would be about the draft, not the task.
NOT_AN_ASSERTION = re.compile(
    r"ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX|SyntaxError|ERR_MODULE_NOT_FOUND|TypeError|"
    r"ReferenceError|NotImplemented|timed out|ENOENT"
)


class Node(Running):
    """The real runner; `tsc` is the pinned TypeScript's own `bin/tsc`, run by this Node."""

    def __call__(self, root: Path, command: tuple[str, ...]) -> Ran:
        if command[0] == "tsc":
            assert TSC_DIR, "no typescript package was given"
            command = ("node", str(Path(TSC_DIR) / "bin" / "tsc"), *command[1:])
        return super().__call__(root, command)


class Recording(Node):
    """Remembers which solution each run had in place and what it printed."""

    def __init__(self, solutions: dict[str, str]) -> None:
        super().__init__()
        self.solutions = solutions
        self.outputs: dict[str, list[str]] = {}
        self.typechecks: list[Ran] = []

    def __call__(self, root: Path, command: tuple[str, ...]) -> Ran:
        ran = super().__call__(root, command)
        if command[0] == "tsc":
            self.typechecks.append(ran)
            return ran
        placed = next(root.rglob("normalise.ts")).read_text(encoding="utf-8")
        role = next(name for name, text in self.solutions.items() if text == placed)
        self.outputs.setdefault(role, []).append(ran.output)
        return ran


def _solutions(made) -> dict[str, str]:
    return {"reference": made.reference, "starter": made.starter, **{
        f"plant:{case}": text for case, text in made.plants.items()
    }}


def _gated(tmp_path, **parts):
    brief, ledger = _brief(tmp_path)
    made = practice.draft(brief, **parts)
    recording = Recording(_solutions(made))
    return gate_code(made, brief, ledger, recording, source="demo", where="w"), recording


def _typed(tmp_path, **parts):
    brief, ledger = _brief(tmp_path)
    made = practice.draft(
        brief, typecheck_command=practice.type_check(brief.places.workspace), **parts
    )
    recording = Recording(_solutions(made))
    return gate_code(made, brief, ledger, recording, source="demo", where="w"), recording


def test_every_gate_holds_for_a_node_practice_graded_through_its_junit_report(tmp_path):
    gated, recording = _gated(tmp_path)
    assert gated.clears, [verdict.says for verdict in gated.refused]
    assert [verdict.id for verdict in gated.record.verdicts] == [G1, G2, G3, G4, G5]
    assert sorted(recording.outputs) == sorted(
        ["reference", "starter", *[f"plant:{case}" for case in practice.PLANTS]]
    )
    assert len(recording.outputs["reference"]) == 2, "G1 reads the reference twice"
    assert recording.typechecks == [], "no type check was declared, so none ran"


def test_each_failing_run_fails_on_an_assertion_and_its_output_says_so(tmp_path):
    _, recording = _gated(tmp_path)
    for role, outputs in recording.outputs.items():
        text = "\n".join(outputs)
        if role == "reference":
            assert "AssertionError" not in text and "ℹ fail 0" in text
            continue
        assert "AssertionError [ERR_ASSERTION]" in text, f"{role} did not fail on an assertion"
        assert NOT_AN_ASSERTION.search(text) is None, f"{role} failed for another reason"


def test_a_plant_fails_its_own_edge_and_only_the_cases_it_names(tmp_path):
    _, recording = _gated(tmp_path)
    failed = {
        role: set(re.findall(r"^✖ (.+?) \(", "\n".join(outputs).split("failing tests")[0], re.M))
        for role, outputs in recording.outputs.items()
        if role != "reference"
    }
    assert failed["plant:" + practice.BLANK.id] == {practice.BLANK.id}
    assert failed["plant:" + practice.INNER.id] == {practice.INNER.id}
    assert failed["plant:" + practice.TABS.id] == {practice.TABS.id}
    assert failed["starter"] == {c.id for c in (practice.MAIN_CASE, practice.BLANK,
                                                practice.INNER, practice.TABS)}


# --- the planted enum: Node's own message, and a finding of the gate -----------------------------


def test_a_planted_enum_fails_with_nodes_own_message_and_the_gate_refuses_it(tmp_path):
    brief, _ = _brief(tmp_path)
    plants = dict(practice.draft(brief).plants)
    plants[practice.BLANK.id] = practice.ENUM_PLANT
    gated, recording = _gated(tmp_path, plants=plants)
    assert [verdict.id for verdict in gated.refused] == [G3]
    assert "not an assertion" in _g(gated, G3).says
    text = "\n".join(recording.outputs["plant:" + practice.BLANK.id])
    assert "ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX" in text
    assert "TypeScript enum is not supported in strip-only mode" in text


def test_the_same_enum_plant_is_still_refused_without_the_request_but_not_as_an_assertion(
    tmp_path,
):
    brief, _ = _brief(tmp_path)
    plants = dict(practice.draft(brief).plants)
    plants[practice.BLANK.id] = practice.ENUM_PLANT
    gated, _ = _gated(tmp_path, plants=plants, assertions_only=False)
    assert [verdict.id for verdict in gated.refused] == [G3]
    assert "not an assertion" not in _g(gated, G3).says


def test_the_filter_keeps_nodes_message_for_an_enum_and_drops_only_its_tallies(tmp_path):
    brief, _ = _brief(tmp_path)
    plants = dict(practice.draft(brief).plants)
    plants[practice.BLANK.id] = practice.ENUM_PLANT
    _, recording = _gated(tmp_path, plants=plants)
    lines = "\n".join(recording.outputs["plant:" + practice.BLANK.id]).splitlines()
    toolchain = select(["node", "gradle"], ("node", "--test", "x.test.ts"))
    assert toolchain is not None and toolchain.name == "node"
    quiet = Quiet(toolchain)
    kept = [line for line in lines if quiet.keeps(line)]
    dropped = [line for line in lines if not quiet.keeps(line)]
    assert any("TypeScript enum is not supported in strip-only mode" in line for line in kept)
    assert any("ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX" in line for line in kept)
    assert dropped and all(
        re.match(r"ℹ (suites|cancelled|skipped|todo|duration_ms) |Node\.js v", line)
        for line in dropped
    ), dropped


def test_a_starter_that_does_not_load_is_not_a_clean_failure(tmp_path):
    gated, recording = _gated(tmp_path, starter="export function normalise(: string {\n")
    assert not gated.clears
    assert "SyntaxError" in "\n".join(recording.outputs["starter"])
    assert _g(gated, G2).held is False


# --- the report directory: Node does not make one ------------------------------------------------


def test_the_built_in_reporter_to_a_missing_directory_leaves_no_report_and_the_gate_says_where(
    tmp_path,
):
    brief, _ = _brief(tmp_path)
    ws = brief.places.workspace
    command = (
        "node", "--test", "--test-reporter=junit",
        f"--test-reporter-destination={ws}/{practice.REPORT}", f"{ws}/normalise.test.ts",
    )
    gated, recording = _gated(tmp_path, test_command=command, build={})
    assert not gated.clears
    says = [_g(gated, gate).says for gate in (G1, G4)]
    assert all(f"{practice.REPORT}'" in text and "no report at '" in text for text in says), says
    assert "ENOENT" in "\n".join(recording.outputs["reference"])


def test_a_wrong_report_path_reads_no_report_and_the_gate_names_the_path(tmp_path):
    gated, _ = _gated(tmp_path, report="target/elsewhere.xml")
    assert not gated.clears
    says = [_g(gated, gate).says for gate in (G1, G4)]
    assert all("target/elsewhere.xml'" in text for text in says), says


@pytest.mark.parametrize(
    "flag",
    [
        "--test-reporter-destination=/elsewhere/report.xml",
        "--test-reporter-destination=../report.xml",
        "--test-reporter=./other/dir/junit-file.mjs",
        "--test-reporter=././other/junit-file.mjs",
        "--test-reporter=./../junit-file.mjs",
    ],
)
def test_an_option_naming_a_path_outside_the_workspace_is_still_refused(tmp_path, flag):
    brief, ledger = _brief(tmp_path)
    made = practice.draft(brief, test_command=("node", "--test", flag, "x.test.ts"))
    with pytest.raises(ExerciseError):
        gate_code(made, brief, ledger, Running(), source="demo", where="w")


# --- the optional type check ---------------------------------------------------------------------


@needs_tsc
def test_a_declared_type_check_that_passes_leaves_every_gate_as_it_was(tmp_path):
    gated, recording = _typed(tmp_path)
    assert gated.clears, [verdict.says for verdict in gated.refused]
    assert len(recording.typechecks) == 6 and all(t.exit_code == 0 for t in recording.typechecks)


@needs_tsc
def test_a_reference_with_a_type_error_passes_when_no_type_check_is_declared(tmp_path):
    gated, recording = _gated(tmp_path, reference=practice.TYPE_ERROR_REFERENCE)
    assert gated.clears, [verdict.says for verdict in gated.refused]
    assert recording.typechecks == []


@needs_tsc
def test_the_same_reference_fails_by_name_when_the_type_check_is_declared(tmp_path):
    gated, recording = _typed(tmp_path, reference=practice.TYPE_ERROR_REFERENCE)
    assert [verdict.id for verdict in gated.refused] == [G1]
    says = _g(gated, G1).says
    assert "type check" in says and "reference" in says and "not a test case" in says
    assert any("TS2322" in ran.output for ran in recording.typechecks)


@needs_tsc
def test_a_starter_and_a_plant_that_do_not_type_check_are_named_by_their_gates(tmp_path):
    brief, _ = _brief(tmp_path)
    bad = 'export function normalise(text: string): string {\n  return 1;\n}\n'
    starter, _ = _typed(tmp_path, starter=bad)
    assert [verdict.id for verdict in starter.refused] == [G2]
    assert "starter" in _g(starter, G2).says
    plants = dict(practice.draft(brief).plants)
    plants[practice.INNER.id] = bad
    planted, _ = _typed(tmp_path, plants=plants)
    assert [verdict.id for verdict in planted.refused] == [G3]
    assert "plant" in _g(planted, G3).says


@needs_tsc
def test_an_enum_is_refused_by_the_type_check_when_it_asks_for_erasable_syntax_only(tmp_path):
    gated, recording = _typed(tmp_path, reference=practice.ENUM_PLANT)
    assert G1 in [verdict.id for verdict in gated.refused]
    assert any("TS1294" in ran.output for ran in recording.typechecks)


def test_a_type_check_that_is_not_on_the_image_is_named_as_missing(tmp_path):
    brief, ledger = _brief(tmp_path)
    made = practice.draft(brief, typecheck_command=("sh", "-c", "exit 127"))
    gated = gate_code(made, brief, ledger, Running(), source="demo", where="w")
    assert "the checker is not on this image" in _g(gated, G1).says


def test_a_type_check_naming_a_path_outside_the_workspace_is_refused(tmp_path):
    brief, ledger = _brief(tmp_path)
    made = practice.draft(brief, typecheck_command=("tsc", "--noEmit", "/elsewhere/x.ts"))
    with pytest.raises(ExerciseError):
        gate_code(made, brief, ledger, Running(), source="demo", where="w")


# --- the report reader, over a real node report ---------------------------------------------------


SOURCE = """import { test, describe } from "node:test";
import assert from "node:assert/strict";

test("plain", () => {});
test("assert", () => { assert.equal(1, 2); });
test("assert with words", () => { assert.ok(false, "AssertionError: not at line start"); });
test("raised assertion", () => { throw new assert.AssertionError({ message: "x" }); });
test("missing throw", () => { assert.throws(() => {}); });
test("type error", () => { (null as any).x; });
test("says assertion", () => { throw new Error("AssertionError: pretend"); });
test("skipped", { skip: true }, () => {});
describe("Group", () => { test("inside", () => { assert.equal(1, 2); }); });
"""

IDS = ["plain", "assert", "assert with words", "raised assertion", "missing throw", "type error",
       "says assertion", "skipped", "inside"]


def _report(tmp_path, source: str, name: str = "it.test.ts") -> Path:
    (tmp_path / name).write_text(source, encoding="utf-8")
    done = run(
        ["node", "--test", "--test-reporter=junit",
         f"--test-reporter-destination={tmp_path}/report.xml", name],
        tmp_path,
    )
    assert done.returncode in (0, 1), done.stdout + done.stderr
    return tmp_path


def _fold(root, ids, started=0.0):
    cases = tuple(Case(i, MAIN if n == 0 else EDGE, "one sentence") for n, i in enumerate(ids))
    exercise = Exercise(
        main_path="m.ts", test_path="it.test.ts", run_command=("node", "m.ts"),
        test_command=("node", "--test"), provenance="generated", trust="advisory",
        cases=cases, report=Report(format="junit", path="report.xml"),
    )
    return breakdown_of(exercise, root, "w", started=started)


def test_a_failure_an_assertion_raised_is_told_from_one_an_error_raised(tmp_path):
    folded = _fold(_report(tmp_path, SOURCE), IDS)
    assert folded.passed_ids == frozenset({"plain"})
    assert folded.unasserted == {"type error", "says assertion", "skipped"}


def test_a_test_file_that_did_not_load_is_a_finding_and_not_a_refusal(tmp_path):
    root = _report(tmp_path, practice.ENUM_PLANT + 'import { test } from "node:test";\n'
                   'test("plain", () => {});\n')
    folded = _fold(root, ["plain", "other"])
    assert folded.passed_ids == frozenset()
    assert folded.unasserted == {"plain", "other"}


def test_a_test_the_cases_do_not_name_is_still_refused(tmp_path):
    root = _report(tmp_path, 'import { test } from "node:test";\ntest("plain", () => {});\n')
    with pytest.raises(ExerciseError, match="names a test"):
        _fold(root, ["another"])


def test_a_test_named_like_a_file_that_passed_is_still_refused_when_unnamed(tmp_path):
    root = _report(tmp_path, 'import { test } from "node:test";\ntest("it.test.ts", () => {});\n')
    with pytest.raises(ExerciseError, match="names a test"):
        _fold(root, ["another"])


def test_a_report_is_still_refused_when_stale(tmp_path):
    root = _report(tmp_path, 'import { test } from "node:test";\ntest("plain", () => {});\n')
    with pytest.raises(ExerciseError, match="older than the run"):
        _fold(root, ["plain"], started=time.time() + 3600)
