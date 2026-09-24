"""One pass over a source — reconnaissance's acceptance, end to end.

⚠️ **The four real corpora are measured in their own repositories, not here.** A claim
about another repository is verified in that repository (the integration
catalogue's own entry 2), and a test that skipped when a sibling checkout was
missing would be a check that is not evidence. ⛔ The authoritative run
carries no skips, and this adds none.

⭐ What these fixtures do is pin the **shape**, so the measurements taken in
those repositories cannot quietly stop being reproducible.
"""

from __future__ import annotations

from studyforge.skills.reconnaissance import survey
from studyforge.skills.reconnaissance.survey import PASSES
from tests.studyforge.skills.reconnaissance import sources


def test_a_flat_prose_source_gets_a_one_level_manifest(tmp_path):
    # ⭐ The skill's second acceptance clause.
    found = survey(sources.flat_prose(tmp_path / "c"))
    assert found.proposal["levels"] == ["course"]
    assert found.proposal["content"]["include"] == ["src/*.md"]


def test_a_prose_only_source_reports_no_runnable_code_and_no_graders(tmp_path):
    # ⭐ The skill's third clause, and it is a **verdict**: a corpus with no graders
    # is complete at the reading floor, not short.
    found = survey(sources.flat_prose(tmp_path / "c"))
    assert found.proposal["exercises"] is False
    assert any("complete at the reading floor" in o.measured for o in found.observations)


def test_a_two_level_source_gets_a_two_level_manifest(tmp_path):
    # ⭐ The skill's first clause, in the shape the Java corpus actually has: the
    # sections exist **only** in the record, as bare numbered lines.
    found = survey(sources.nested_sections(tmp_path / "c"))
    assert found.proposal["levels"] == ["section", "module"]


def test_every_survey_carries_open_questions_rather_than_a_finished_look(tmp_path):
    # ⛔ The skill's fourth clause, and the hardest one: every uncertainty appears in
    # the report rather than as a silent guess. ⚠️ Unfamiliar material always
    # leaves something open — the level vocabulary is §4's and cannot be known.
    for build in (sources.flat_prose, sources.nested_sections, sources.prefixed_groups):
        found = survey(build(tmp_path / build.__name__))
        assert found.uncertainties, f"{build.__name__} reported nothing open"
        assert all(q.settles_it for q in found.uncertainties)


def test_the_report_shows_the_measurements_and_the_questions_together(tmp_path):
    # ⛔ Never the draft alone. The questions are the other half of the
    # deliverable.
    lines = survey(sources.aggregated(tmp_path / "c")).lines()
    assert any("measured" == line for line in lines)
    assert any(line.startswith("not settled") for line in lines)
    assert lines[-1].startswith("a draft manifest is proposed")


def test_a_source_with_nothing_recording_its_order_still_produces_a_report(tmp_path):
    # ⛔ It never raises for difficult material: difficult material is a
    # *result*, and a caller that had to catch an exception could not be handed
    # the half that was determined.
    root = sources.flat_prose(tmp_path / "c")
    (root / "README.md").unlink()
    found = survey(root)
    assert found.proposal is not None
    assert any("reading order" in q.question for q in found.uncertainties)


def test_the_pass_list_is_one_list(tmp_path):
    # ⭐ "What does reconnaissance look at" has one answer, not five.
    assert len(PASSES) == len(set(PASSES))


def test_reconnaissance_writes_nothing_into_the_source(tmp_path):
    # ⛔ R3, and it is the rule most easily broken by a tool that "just caches
    # something". Reconnaissance reads.
    root = sources.aggregated(tmp_path / "c")
    before = {p: p.stat().st_mtime_ns for p in sorted(root.rglob("*")) if p.is_file()}
    survey(root)
    after = {p: p.stat().st_mtime_ns for p in sorted(root.rglob("*")) if p.is_file()}
    assert before == after, "reconnaissance touched the source"


def test_a_survey_of_dot_names_the_directory_it_read(tmp_path, monkeypatch):
    # ⚠️ The report's header names the resolved directory, never an empty `.`.
    root = sources.flat_prose(tmp_path / "named-course")
    monkeypatch.chdir(root)
    assert survey(".").root == "named-course"
