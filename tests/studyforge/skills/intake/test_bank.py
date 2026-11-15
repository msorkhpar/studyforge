"""Mirror of `src/studyforge/skills/intake/bank.py`."""

from __future__ import annotations

import re

import pytest

from studyforge.archive.scrub import findings
from studyforge.skills.intake import TRACKS
from studyforge.skills.intake.bank import BANK, by_id
from studyforge.skills.intake.brief import Answer, parse
from studyforge.skills.intake.check import check
from studyforge.skills.intake.questions import HEDGE, applies


def test_ids_are_unique_and_shaped_group_dot_name():
    ids = [q.id for q in BANK]
    assert len(ids) == len(set(ids)) == 60
    for i in ids:
        assert re.fullmatch(r"[a-z_]+\.[a-z_]+", i), i


def test_every_question_has_why_and_default_and_a_valid_track():
    for q in BANK:
        assert q.ask.strip() and q.why.strip() and q.default.strip(), q.id
        assert q.tracks and q.tracks <= set(TRACKS), q.id
        assert q.tier in {"costly", "later"}, q.id


def test_every_dependency_names_a_gate_in_the_bank_whose_kind_is_typed():
    bank = by_id()
    gated = [q for q in BANK if q.depends_on]
    assert {q.id for q in gated} == {"narration.scope", "narration.voice"}
    for q in gated:
        gate_id, values = q.depends_on
        gate = bank[gate_id]
        assert gate.kind in {"boolean", "choice"}
        assert values
        for v in values:
            assert isinstance(v, bool) if gate.kind == "boolean" else v in gate.choices


def test_the_lessons_skill_owner_questions_are_all_in_the_bank():
    ids = by_id()
    for i in (
        "privacy.private_folder", "publish.licence", "publish.holder", "publish.repository",
        "publish.namespace", "publish.preview", "publish.joint", "runtimes.licensed_tools",
        "runtimes.hardware", "scope.ruled_out", "narration.wanted", "practice.density",
        "practice.projects",
    ):
        assert i in ids, i


def test_no_default_or_why_holds_a_hedge_or_personal_data():
    for q in BANK:
        for field in ("ask", "why", "default"):
            text = getattr(q, field)
            assert not HEDGE.search(text), (q.id, field)
            assert not findings(text, q.id), (q.id, field)
            assert not re.search(r"\b[A-Za-z]+\d+\b|\b\d{4}-\d\d-\d\d\b", text), (q.id, field)


def test_the_rows_carry_the_specified_tiers_kinds_and_tracks():
    bank = by_id()
    assert bank["narration.wanted"].choices == ("yes", "no", "after-release")
    assert bank["narration.scope"].depends_on == ("narration.wanted", ("yes", "after-release"))
    assert bank["narration.voice"].tier == "later"
    assert bank["quiz.mocks"].kind == "boolean"
    assert bank["interview.job_description"].kind == "private_ref"
    assert bank["interview.job_description"].default.startswith("private:")
    assert bank["convert.repository"].tracks == frozenset({"convert"})
    assert bank["goal.end_state"].tracks == frozenset(TRACKS)
    assert sum(q.kind == "private_ref" for q in BANK) == 6
    assert sum(q.tier == "later" for q in BANK) == 12


def _all_defaults(track: str) -> dict:
    """A brief that records every applicable costly default, as "just pick" would.

    `writing.pilot`'s default says how to choose the pilot, so the outline's pilot module is
    named by that sentence: picking the default is choosing that module.
    """
    pilot = by_id()["writing.pilot"].default
    answers: dict[str, dict] = {}
    seen: dict[str, Answer] = {}
    for question in BANK:
        if question.tier != "costly" or not applies(question, track, seen):
            continue
        record = {"status": "answered", "decided_by": "claude", "value": question.default_value}
        answers[question.id] = record
        seen[question.id] = Answer(**record)
    lesson = {"title": "First lesson", "depth": "core"}
    module = {"title": pilot, "pilot": True, "lessons": [lesson]}
    return {"brief_api": 1, "title": "Defaults Only", "track": track, "answers": answers,
            "outline": [{"title": "Only section", "modules": [module]}]}


@pytest.mark.parametrize("track", TRACKS)
def test_a_brief_of_every_default_passes_the_checker(track):
    assert check(parse(_all_defaults(track)), private_ignored=True) == []


def test_typed_defaults_are_the_values_a_brief_records():
    bank = by_id()
    assert bank["quiz.mocks"].default_value is False
    assert bank["privacy.fresh_history"].default_value is True
    assert bank["narration.wanted"].default_value in bank["narration.wanted"].choices
    assert bank["interview.job_description"].default == "private:job-description.md"
