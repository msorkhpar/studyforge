"""Mirror of `src/studyforge/skills/exercises/corpus.py` (R12) — the whole pass, read end to end.

**What it asserts.** `AX-08`'s Acceptance, clause by clause, on a corpus whose
pages carry each of spec §7 §1's three source cases and a prose page that gets
a quiz: each ships a gate-cleared exercise; every exercise is
`generated`/`advisory`; a grader-less source gets exercises, which is what
supersedes `SK-04`'s refusal; the pass writes only inside the corpus and only
additively (R3); and re-running it with nothing changed rewrites nothing (R10).

⭐ **One real pass, taken once per module**: the runs are real `pytest`
processes, and every clause below reads the tree that pass left.
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from studyforge.exercise import from_document
from studyforge.exercise.bundle import Places, bundle_of, emit, unpermitted
from studyforge.exercise.gates import drifted, record_of
from studyforge.skills.exercises import (
    CODE_AND_TESTS,
    CODE_NO_TESTS,
    LEDGER_PATH,
    NEITHER,
    QUIZ_DOCUMENT,
    Aspect,
    AuthoringError,
    author_corpus,
)
from tests.studyforge.skills.exercises.authoring import (
    ASPECTS,
    CLEAN,
    Judging,
    Running,
    Scripted,
    snapshot,
    write_corpus,
)

#: Each code page, and the case the ledger must read off it.
CASES = {
    "lessons/greeting.md": CODE_AND_TESTS,
    "lessons/shout.md": CODE_NO_TESTS,
    "lessons/basket.md": NEITHER,
}


@pytest.fixture(scope="module")
def corpus(tmp_path_factory):
    """One clean pass over the fixture corpus, with the tree as it stood before it."""
    root = tmp_path_factory.mktemp("authoring") / "corpus"
    root.mkdir()
    material, graders, pages = write_corpus(root)
    before = snapshot(root)
    author, judge, runner = Scripted(CLEAN), Judging(), Running()
    authored = author_corpus(
        root,
        source="demo",
        material=material,
        graders=graders,
        pages=pages,
        author=author,
        judge=judge,
        runner=runner,
    )
    return {
        "root": root,
        "inputs": (material, graders, pages),
        "before": before,
        "authored": authored,
        "author": author,
    }


def _coverage(root, page_path):
    for path in sorted(root.glob("exercises/**/coverage.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["page"] == page_path:
            return document
    raise AssertionError(f"no coverage report names {page_path}")


def _record(root, bundle):
    return record_of(json.loads((root / bundle / "gates.json").read_text("utf-8")), bundle)


@pytest.mark.parametrize("page_path", sorted(CASES))
def test_each_source_case_ships_a_gate_cleared_exercise(corpus, page_path):
    root = corpus["root"]
    coverage = _coverage(root, page_path)
    assert coverage["case"] == CASES[page_path], "the case was not read off the ledger"
    assert coverage["plan"]["count"] >= 1, "the page planned nothing, so this reads nothing"
    assert len(coverage["shipped"]) == coverage["plan"]["count"] and not coverage["shortfalls"]
    for bundle in coverage["shipped"]:
        record = _record(root, bundle)
        assert record.clears, f"{bundle} shipped with a gate that did not hold"
        assert [verdict.id for verdict in record.verdicts] == ["G1", "G2", "G3", "G4", "G5"]
        assert drifted(root / bundle, record.inputs, bundle) == (), "the record is not its files'"


def test_the_quiz_case_runs_on_the_prose_page(corpus):
    root = corpus["root"]
    coverage = _coverage(root, "notes/gauge.md")
    assert coverage["kind"] == "quiz" and len(coverage["shipped"]) == 1
    (bundle,) = coverage["shipped"]
    record = _record(root, bundle)
    assert record.clears and [v.id for v in record.verdicts] == ["Q1", "Q2", "Q3", "Q4", "Q5"]
    assert drifted(root / bundle, record.inputs, bundle) == ()
    document = json.loads((root / bundle / QUIZ_DOCUMENT).read_text(encoding="utf-8"))
    exercise = from_document(document["exercise"], bundle)
    assert exercise.is_quiz and len(exercise.questions) == 2
    assert not exercise.authoritative, "a quiz can never be the source's own grader (R5)"


def test_every_exercise_it_writes_is_generated_and_advisory(corpus):
    root = corpus["root"]
    documents = sorted(root.glob("exercises/**/bundle.json"))
    assert len(documents) == len(CASES), "not every code page shipped a bundle"
    for path in documents:
        bundle = bundle_of(json.loads(path.read_text(encoding="utf-8")), str(path.name))
        assert (bundle.provenance, bundle.trust) == ("generated", "advisory")


def test_it_supersedes_sk04_s_refusal_of_a_grader_less_source(corpus):
    # ⛔ `SK-04` once refused a source that ships no grader. Run on two of
    # them — one with an example and one with nothing at all — and each ships
    # a gate-cleared exercise instead of a refusal.
    authored = corpus["authored"]
    graderless = [page for page in corpus["inputs"][2] if not page.graders]
    assert graderless, "the fixture has no grader-less page, so this asserts nothing"
    shipped = {covered.page: covered.shipped for covered in authored.pages}
    for page in graderless:
        assert shipped[page.path], f"the grader-less page {page.path} shipped nothing"
    assert authored.bare == () and authored.shortfalls == ()


def test_the_committed_bundles_are_what_an_adapter_emits_and_validate_accepts(corpus):
    root = corpus["root"]
    for path in sorted(root.glob("exercises/**/bundle.json")):
        bundle = bundle_of(json.loads(path.read_text(encoding="utf-8")), path.name)
        emission = emit(root, bundle, source="demo", ingested="2026-01-05")
        assert unpermitted(root, bundle.places) == (), "the bundle holds a file it may not"
        for written, data in emission.files:
            assert (root / written).read_bytes() == data, "the workspace is not the emission's"


def test_the_ledger_accounts_for_every_entry_and_asks_only_for_what_nothing_built_on(corpus):
    root, author = corpus["root"], corpus["author"]
    ledger = json.loads((root / LEDGER_PATH).read_text(encoding="utf-8"))
    assert ledger["entries"], "the ledger carries nothing, so this asserts nothing"
    for entry in ledger["entries"]:
        assert bool(entry["exercises"]) != bool(entry["reason"]), "an entry with no one ending"
    excused = {(entry.path, entry.ordinal) for entry in author.excused}
    unbuilt = {(e["path"], e["ordinal"]) for e in ledger["entries"] if not e["exercises"]}
    assert excused == unbuilt, "the author was asked for a reason nothing needed, or not asked"
    assert ("checks/test_greeting.py", 0) in unbuilt, "the grader's entry was not accounted"


def test_it_writes_only_inside_the_corpus_and_only_additively(corpus):
    root, before = corpus["root"], corpus["before"]
    after = snapshot(root)
    for path, (data, mtime) in before.items():
        assert after[path] == (data, mtime), f"the pass rewrote a source file: {path}"
    new = sorted(set(after) - set(before))
    assert new and set(new) == set(corpus["authored"].written)
    assert all(path.split("/")[0] in ("exercises", "practice") for path in new)
    outside = [path for path in root.parent.iterdir() if path != root]
    assert outside == [], "the pass wrote beside the corpus root"


def test_re_running_with_nothing_changed_rewrites_nothing(corpus):
    root = corpus["root"]
    material, graders, pages = corpus["inputs"]
    before = snapshot(root)
    author, judge, runner = Scripted(CLEAN), Judging(), Running()
    again = author_corpus(
        root,
        source="demo",
        material=material,
        graders=graders,
        pages=pages,
        author=author,
        judge=judge,
        runner=runner,
    )
    assert again.written == (), "a re-run with nothing changed wrote a file"
    assert snapshot(root) == before, "a re-run with nothing changed touched a file"
    assert (author.briefs, author.excused, judge.calls, runner.runs) == ([], [], 0, 0)
    assert all(not covered.authored for covered in again.pages)


def test_a_page_that_moved_is_refused_naming_its_unit_and_nothing_is_written(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    author, judge, runner = Scripted(CLEAN), Judging(), Running()
    arguments = dict(material=material, graders=graders, pages=pages[1:2], author=author)
    author_corpus(tmp_path, source="demo", judge=judge, runner=runner, **arguments)
    page = tmp_path / pages[1].path
    page.write_text(page.read_text(encoding="utf-8") + "\nOne more line.\n", encoding="utf-8")
    before = snapshot(tmp_path)
    with pytest.raises(AuthoringError, match="exercises/kata/python/unit-02"):
        author_corpus(tmp_path, source="demo", judge=judge, runner=runner, **arguments)
    assert snapshot(tmp_path) == before, "a refused pass wrote something"


def test_an_existing_file_with_other_bytes_refuses_the_whole_pass_before_any_write(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    blocking = Places(pages[2].address, pages[2].variant, pages[2].unit, 1).in_workspace("total.py")
    (tmp_path / blocking).parent.mkdir(parents=True)
    (tmp_path / blocking).write_text("# the reader's own work\n", encoding="utf-8")
    before = snapshot(tmp_path)
    with pytest.raises(AuthoringError, match="R3"):
        author_corpus(
            tmp_path,
            source="demo",
            material=material,
            graders=graders,
            pages=pages[2:3],
            author=Scripted(CLEAN),
            judge=Judging(),
            runner=Running(),
        )
    assert snapshot(tmp_path) == before, "the pass wrote some files before refusing"


#: A minor aspect, carried by the short reason the user's refinement words.
TONE = Aspect(
    "tone", "a shout is loud", ("section:How to shout",), reason="incidental detail, not practised"
)


def test_an_aspect_nothing_checks_is_visible_in_the_report_and_on_the_pass(tmp_path):
    """⭐ `W453`: a thin plan is VISIBLE — each unchecked aspect, with its reason."""
    material, graders, pages = write_corpus(tmp_path)
    shout = replace(pages[1], aspects=(*pages[1].aspects, TONE))
    arguments = dict(material=material, graders=graders, pages=[shout], judge=Judging())
    authored = author_corpus(
        tmp_path, source="demo", author=Scripted(CLEAN), runner=Running(), **arguments
    )
    assert authored.reasoned == (("lessons/shout.md", "tone"),)
    plan = _coverage(tmp_path, "lessons/shout.md")["plan"]
    assert {row["id"]: row["reason"] for row in plan["aspects"]}["tone"] == TONE.reason
    again = author_corpus(
        tmp_path, source="demo", author=Scripted(CLEAN), runner=Running(), **arguments
    )
    assert again.reasoned == authored.reasoned, "a kept unit lost its reasoned aspects"


def test_a_unit_planned_under_the_withdrawn_band_is_refused_by_its_plan_api(tmp_path):
    """⛔ `W453`: a `plan_api` 1 report is re-planned by aspects, never silently kept."""
    material, graders, pages = write_corpus(tmp_path)
    author, judge, runner = Scripted(CLEAN), Judging(), Running()
    arguments = dict(material=material, graders=graders, pages=pages[1:2], author=author)
    author_corpus(tmp_path, source="demo", judge=judge, runner=runner, **arguments)
    report = tmp_path / "exercises/kata/python/unit-02/coverage.json"
    document = json.loads(report.read_text(encoding="utf-8"))
    document["plan"] = {"plan_api": 1, "words": 300, "skills": 1, "band": "short", "count": 1}
    report.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    before = snapshot(tmp_path)
    with pytest.raises(AuthoringError, match="unit-02.*plan_api 1"):
        author_corpus(tmp_path, source="demo", judge=judge, runner=runner, **arguments)
    assert snapshot(tmp_path) == before, "a refused pass wrote something"


def test_each_brief_carries_the_aspects_its_planned_exercise_checks(corpus):
    """⭐ The author drafts against what the page teaches, never against a count."""
    briefs = corpus["author"].briefs
    assert briefs, "no brief was handed out, so this reads nothing"
    for brief in briefs:
        expected = sorted(ASPECTS[brief.page.path], key=lambda aspect: aspect.id)
        assert list(brief.aspects) == expected, brief.page.path
