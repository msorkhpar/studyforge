"""Is anything runnable, and does a grader ship with it? (SK-01)"""

from __future__ import annotations

from studyforge.skills.reconnaissance import assess, take
from studyforge.skills.reconnaissance.capability import observe
from studyforge.skills.reconnaissance.report import Observation, Uncertainty
from tests.studyforge.skills.reconnaissance import sources


def seen(root):
    return list(observe(assess(take(root))))


def test_a_prose_only_corpus_reports_no_runnable_code_and_no_graders(tmp_path):
    # ⭐ E11's named acceptance, and it is a **finished verdict** rather than a
    # blank section: a corpus with no graders is complete at the reading floor,
    # not short (§11.0, C5).
    verdicts = [
        i.measured
        for i in seen(sources.flat_prose(tmp_path / "c"))
        if isinstance(i, Observation) and i.what == "verdict"
    ]
    assert verdicts == ["no runnable code, no graders — complete at the reading floor"]


def test_a_corpus_with_a_build_and_tests_is_both(tmp_path):
    able = assess(take(sources.runnable(tmp_path / "c")))
    assert able.runnable and able.graded
    assert able.build_files == ["pom.xml"]


def test_and_it_does_not_claim_the_reading_floor_verdict(tmp_path):
    assert not [
        i
        for i in seen(sources.runnable(tmp_path / "c"))
        if isinstance(i, Observation) and i.what == "verdict"
    ]


def test_a_build_with_no_recognisable_tests_is_a_question(tmp_path):
    # ⚠️ An ungraded exercise is a first-class state (§7), so this asks rather
    # than concluding either way.
    root = sources.runnable(tmp_path / "c")
    (root / "src/test/java/ThingTest.java").unlink()
    asked = [i for i in seen(root) if isinstance(i, Uncertainty)]
    assert any("graders this skill did not recognise" in q.question for q in asked)


def test_non_prose_files_with_no_build_are_asked_about(tmp_path):
    # ⛔ The closed set costs exactly one question, and the question names what
    # was looked for — which is also how the set grows.
    root = sources.flat_prose(tmp_path / "c")
    (root / "script.sh").write_text("echo hi\n", encoding="utf-8")
    asked = [i for i in seen(root) if isinstance(i, Uncertainty)]
    assert any("meant to be run" in q.question for q in asked)
