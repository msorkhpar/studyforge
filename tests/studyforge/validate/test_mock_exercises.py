"""`validate` owes a mock exam its mock gate, and every plant is a real edit to a real file.

⭐ The corpus is built the way an authoring pass builds one: a draft is gated by `gate_quiz`, its
files are written where the pass writes them, and the practice document is made from the quiz
document it wrote. ⛔ So the gate record under test is the one the gates produced, and each plant
is an edit to it whose effect is read back before `validate` is asked anything.
"""

from __future__ import annotations

import json

from studyforge.address import Address
from studyforge.archive.document import build, render
from studyforge.exercise.bundle import Places
from studyforge.exercise.quiz import mock_of, questions_of
from studyforge.skills.exercises import (
    CORE,
    QUIZ_DOCUMENT,
    Aspect,
    Brief,
    Page,
    QuizDraft,
    gate_quiz,
    quiz_of,
    source_case,
    take,
)
from studyforge.validate import validate
from studyforge.validate.exercises import RULE_GATE_SHORTFALL
from tests.studyforge.exercise.quiz import mock_exam, mock_form
from tests.studyforge.skills.exercises.authoring import Judging
from tests.studyforge.validate import corpora
from tests.studyforge.validate.test_exercises import MANIFEST

WHERE = "demo"
ORIGIN = {"path": "src/one.md", "section": "Two"}


def a_mock_corpus(root, *, plain=False, form=False):
    """One corpus whose unit 1 carries a gated quiz, a mock exam unless `plain`."""
    corpora.write(
        root,
        manifest=MANIFEST,
        containers={"demo": corpora.container([corpora.unit_entry(1, practices=1)])},
        sources={"src/one.md": corpora.SOURCE},
    )
    places = Places(Address.of("demo"), "prose", 1, 1)
    ledger = take(root, ["src/one.md"], [], "the ledger")
    page = Page(
        path="src/one.md",
        address=Address.of("demo"),
        variant="prose",
        unit=1,
        kind="quiz",
        aspects=(Aspect("two", "the second part", ("section:Two",), "check"),),
        tier=CORE,
    )
    brief = Brief(page, source_case(page, ledger), 1, places, 1, ())
    raw = mock_form.questions(ORIGIN) if form else mock_exam.questions(ORIGIN)
    if plain:
        raw = [{k: v for k, v in one.items() if k != "domain"} for one in raw]
    draft = QuizDraft(
        title="A mock exam",
        questions=questions_of(raw, WHERE),
        mock=None if plain else mock_of((mock_form if form else mock_exam).mock(), WHERE),
    )
    gated = gate_quiz(draft, brief, ledger, Judging(), where=WHERE)
    assert gated.clears, [verdict.says for verdict in gated.refused]
    for path, data in gated.files:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(data)
    written = json.loads((root / places.in_bundle(QUIZ_DOCUMENT)).read_text(encoding="utf-8"))
    quiz = quiz_of(written, places.bundle)
    document = build(
        source="demo",
        address=["demo"],
        variant="prose",
        unit=1,
        kind="practice",
        ordinal=1,
        ingested="2026-01-05",
        title=quiz.title,
        blocks=corpora.PRACTICE_BLOCKS,
        exercise=dict(quiz.record),
    )
    target = root / "archive" / "demo" / "raw" / "prose" / "unit-01" / "practice-1.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(document), encoding="utf-8")
    return root, places


def gate_ids(root, places) -> list[str]:
    record = json.loads((root / places.gates).read_text(encoding="utf-8"))
    return [gate["id"] for gate in record["gates"]]


def test_a_gated_mock_exam_validates_clean(tmp_path):
    root, places = a_mock_corpus(tmp_path / "c")
    assert gate_ids(root, places) == ["P1", "Q1", "Q2", "Q3", "Q4", "Q5"]
    report = validate(root)
    assert report.findings == (), [f.message for f in report.findings]


def test_a_plain_quiz_validates_clean_with_the_five_it_always_carried(tmp_path):
    root, places = a_mock_corpus(tmp_path / "c", plain=True)
    assert gate_ids(root, places) == ["Q1", "Q2", "Q3", "Q4", "Q5"]
    assert validate(root).findings == ()


def test_a_mock_exam_whose_record_lost_its_mock_gate_is_refused_naming_it(tmp_path):
    root, places = a_mock_corpus(tmp_path / "c")
    path = root / places.gates
    record = json.loads(path.read_text(encoding="utf-8"))
    record["gates"] = [gate for gate in record["gates"] if gate["id"] != "P1"]
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    assert gate_ids(root, places) == ["Q1", "Q2", "Q3", "Q4", "Q5"]  # ⭐ the plant, observed
    report = validate(root)
    assert RULE_GATE_SHORTFALL in report.rules
    assert "P1" in "\n".join(f.message for f in report.findings)


def test_a_mock_exam_whose_mock_gate_did_not_hold_is_refused(tmp_path):
    root, places = a_mock_corpus(tmp_path / "c")
    path = root / places.gates
    record = json.loads(path.read_text(encoding="utf-8"))
    for gate in record["gates"]:
        if gate["id"] == "P1":
            gate["held"] = False
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    assert [g["held"] for g in json.loads(path.read_text())["gates"]].count(False) == 1
    assert RULE_GATE_SHORTFALL in validate(root).rules


def test_a_gated_exam_form_mock_validates_clean_with_the_same_six_gates(tmp_path):
    root, places = a_mock_corpus(tmp_path / "c", form=True)
    assert gate_ids(root, places) == ["P1", "Q1", "Q2", "Q3", "Q4", "Q5"]
    assert validate(root).findings == ()


def test_an_exam_form_record_edited_to_a_scenario_nobody_declared_is_refused(tmp_path):
    root, _ = a_mock_corpus(tmp_path / "c", form=True)
    path = root / "archive" / "demo" / "raw" / "prose" / "unit-01" / "practice-1.json"
    text = path.read_text(encoding="utf-8")
    assert text.count('"scenario": "support-bot"') == 2
    path.write_text(text.replace('"scenario": "support-bot"', '"scenario": "nowhere"'), encoding="utf-8")
    report = validate(root)
    assert report.findings and "not declared" in "\n".join(f.message for f in report.findings)
