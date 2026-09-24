"""Mirror of `src/studyforge/skills/exercises/gating.py` (R12) — and `G5`'s seam, gate-side.

⛔ **The requirement, and why these tests exist.** The contract
between the ledger and `G5` — `G5` asks `ledger.get(origin.path)` of the
mapping `digests(ledger)` returns — was asserted from ONE side only:
`test_ledger.py` pins the ledger's key spelling, and the gates' own suite hands
`G5` a dictionary it built by hand. ⚠️ **Re-key the ledger and the first goes
RED while the gates' suite stays GREEN**, because nothing on the gates' side
ever read a real ledger. ⭐ So the two tests below hand `G5` and `Q5` the
mapping `digests(take(...))` ACTUALLY produces over a corpus on disk, and the
digest they are compared against is taken by an instrument of the test's own —
the file's bytes, digested here — never by the module under test.

**What else it asserts.** A draft missing a plant is refused before anything
runs, and a run's output is made relative to its staging root and scrubbed
before it can reach a committed report (R7).
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from studyforge.exercise import EDGE, MAIN, Case, Exercise, Origin, Report
from studyforge.exercise.bundle import Places
from studyforge.exercise.gates import (
    ORIGIN_ROLE,
    Cited,
    Evidence,
    Run,
    check,
    digest_of_bytes,
)
from studyforge.exercise.gates.quiz import check_quiz, cited_role
from studyforge.skills.exercises import (
    AuthoringError,
    Brief,
    Ran,
    digests,
    gate_code,
    gate_quiz,
    source_case,
    take,
)
from tests.studyforge.skills.exercises.authoring import (
    Judging,
    Running,
    basket,
    gauge,
    gauge_questions,
    write_corpus,
)

#: The page with neither code nor tests, and the prose page, by position.
BASKET, GAUGE = 2, 3

#: ⚠️ Built by concatenation so no file in this tree spells a home path (R7).
HOME = "/" + "home/somebody"


def _brief(page, ledger) -> Brief:
    places = Places(page.address, page.variant, page.unit, 1)
    return Brief(page, source_case(page, ledger), 1, places, 1, ())


def _g(verdicts, gate):
    return next(verdict for verdict in verdicts if verdict.id == gate)


def test_g5_holds_on_the_mapping_digests_of_take_actually_produces(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    page = pages[BASKET]
    ledger = take(tmp_path, material, graders, "the ledger")
    exercise = Exercise(
        main_path="w/total.py",
        test_path="w/test_total.py",
        run_command=("python3", "w/total.py"),
        test_command=("python3", "-m", "pytest", "w"),
        provenance="generated",
        trust="advisory",
        cases=(Case("t_main", MAIN, "the ask"), Case("t_edge", EDGE, "the edge")),
        report=Report("junit", "w/report.xml"),
        origin=Origin(page.path, None),
    )
    # ⭐ What the source digested to, taken HERE, by reading its bytes.
    cited = (
        Cited(ORIGIN_ROLE, page.path, None, digest_of_bytes((tmp_path / page.path).read_bytes())),
    )
    evidence = Evidence.taken(exercise, lambda role, number: Run(role, number, 1), "the gates")
    held = _g(check(exercise, evidence, cited, digests(ledger), "the gates"), "G5")
    assert held.held, f"G5 refused the ledger take() produced: {held.says}"
    # ⛔ The negative control, so this test is known to be able to go RED: the
    # source moves after it was cited, and the same mapping refuses it.
    (tmp_path / page.path).write_text("# moved\n", encoding="utf-8")
    moved = take(tmp_path, material, graders, "the ledger")
    refused = _g(check(exercise, evidence, cited, digests(moved), "the gates"), "G5")
    assert not refused.held, "G5 held on a source that moved, so the positive reading is vacuous"


def test_q5_holds_on_the_mapping_digests_of_take_actually_produces(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    questions = gauge_questions()
    exercise = Exercise(
        None, None, None, None, "generated", "advisory", kind="quiz", questions=questions
    )
    bytes_now = digest_of_bytes((tmp_path / pages[GAUGE].path).read_bytes())
    cited = tuple(
        Cited(cited_role(q.id), q.origin.path, q.origin.section, bytes_now) for q in questions
    )
    judged = Judging()(_brief(pages[GAUGE], ledger), questions)
    q5 = _g(check_quiz(exercise, judged, cited, digests(ledger), "the gates"), "Q5")
    assert q5.held, f"Q5 refused the ledger take() produced: {q5.says}"


def test_the_loop_cites_what_the_ledger_read_and_its_gate_asks_the_same_ledger(tmp_path):
    # ⭐ The same seam, through the loop's own path: `gate_code` cites off the
    # ledger's Source rows and hands `G5` `digests(ledger)` — so a re-keyed
    # ledger is refused here, as a gate verdict, not somewhere downstream.
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    brief = _brief(pages[BASKET], ledger)
    gated = gate_code(basket(brief), brief, ledger, Running(), source="demo", where="w")
    assert _g(gated.record.verdicts, "G5").held, _g(gated.record.verdicts, "G5").says
    (origin,) = gated.record.origins
    assert origin.digest == digest_of_bytes((tmp_path / pages[BASKET].path).read_bytes())
    assert gated.clears, [verdict.says for verdict in gated.refused]


def test_a_quiz_is_gated_by_its_judge_and_cites_every_question(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    brief = _brief(pages[GAUGE], ledger)
    gated = gate_quiz(gauge(brief), brief, ledger, Judging(), where="w")
    assert gated.clears and len(gated.record.origins) == len(gauge_questions())
    assert gated.output == "", "a quiz runs nothing, so there is no output to report"


def test_a_draft_missing_a_plant_is_refused_before_anything_runs(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    brief = _brief(pages[BASKET], ledger)
    runs = []
    with pytest.raises(AuthoringError, match="plants do not match"):
        gate_code(
            replace(basket(brief), plants={}),
            brief,
            ledger,
            lambda root, command: runs.append(command),
            source="demo",
            where="w",
        )
    assert runs == [], "a draft that could not be gated was run anyway"


def test_a_runs_output_is_made_relative_and_scrubbed_before_it_is_kept(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    brief = _brief(pages[BASKET], ledger)
    seen = []

    def leaking(root, command):
        seen.append(str(root))
        return Ran(1, f"{root}/practice/test_total.py failed\nran as {HOME}/work\n")

    gated = gate_code(basket(brief), brief, ledger, leaking, source="demo", where="w")
    assert seen and all(root not in gated.output for root in seen), "the staging root leaked"
    assert gated.output.startswith("./practice/"), "the output was not made relative"
    assert HOME not in gated.output, "a home path reached what a report would commit"
    assert not gated.clears, "a run that wrote no report cleared the gates"


# ⭐ A draft's build role is staged into every run, digested, and shipped.

#: A build file of the draft's own. ⚠️ The framework never reads it, so its
#: content only has to reach every place it is owed, byte for byte.
BUILD = {"pyproject.toml": "[tool.pytest.ini_options]\naddopts = '-q'\n"}


def test_a_build_role_is_staged_into_every_run_digested_and_shipped(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    brief = _brief(pages[BASKET], ledger)
    real = Running()
    staged = []

    def watching(root, command):
        staged.append((root / brief.places.in_workspace("pyproject.toml")).read_text())
        return real(root, command)

    draft = replace(basket(brief), build=BUILD)
    gated = gate_code(draft, brief, ledger, watching, source="demo", where="w")
    assert staged and set(staged) == {BUILD["pyproject.toml"]}, "a run missed the build role"
    assert gated.clears, [verdict.says for verdict in gated.refused]
    files = dict(gated.files)
    assert files[brief.places.in_bundle("build/pyproject.toml")] == BUILD["pyproject.toml"].encode()
    assert files[brief.places.in_workspace("pyproject.toml")] == BUILD["pyproject.toml"].encode()
    (build,) = [one for one in gated.record.inputs if one.role.startswith("build:")]
    assert (build.role, build.path) == ("build:pyproject.toml", "build/pyproject.toml")
    assert build.digest == digest_of_bytes(BUILD["pyproject.toml"].encode())


def test_a_draft_with_no_build_role_ships_no_build_file_and_no_build_input(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    brief = _brief(pages[BASKET], ledger)
    gated = gate_code(basket(brief), brief, ledger, Running(), source="demo", where="w")
    assert not any("/build/" in path for path, _ in gated.files)
    assert not any(one.role.startswith("build:") for one in gated.record.inputs)
