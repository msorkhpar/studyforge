"""What reconnaissance found, and what it could not tell (SK-01)."""

from __future__ import annotations

from studyforge.skills.reconnaissance import Observation, Survey, Uncertainty


def uncertainty(**changes):
    fields = {
        "question": "how deep is the hierarchy?",
        "why": "19 files in one directory",
        "settles_it": "point at the document that groups them",
    }
    return Uncertainty(**{**fields, **changes})


def test_an_observation_always_carries_its_number():
    # ⭐ "The corpus looks flat" is an opinion; "41 files, 0 directories" is a
    # measurement somebody can check.
    assert "41" in Observation("material files", "41").line()


def test_an_uncertainty_renders_the_question_the_evidence_and_the_way_out():
    lines = uncertainty().lines()
    assert len(lines) == 3
    assert "how deep" in lines[0]
    assert "seen:" in lines[1]
    assert "settle:" in lines[2]


def test_every_uncertainty_states_what_would_settle_it():
    # ⛔ A question a reader cannot act on is a question they skip, and a
    # skipped question is a silent guess with extra steps.
    assert uncertainty().settles_it


def test_a_survey_sorts_the_two_shapes_into_their_own_halves():
    survey = Survey.of("demo", [Observation("a", "1"), uncertainty(), Observation("b", "2")])
    assert len(survey.observations) == 2
    assert len(survey.uncertainties) == 1
    assert not survey.settled


def test_a_survey_with_nothing_open_says_so_rather_than_going_quiet():
    # ⛔ A section that disappears when it is empty cannot be told from one
    # nobody wrote.
    lines = Survey.of("demo", [Observation("a", "1")]).lines()
    assert any("not settled (0)" in line for line in lines)
    assert any("none — every question" in line for line in lines)


def test_the_open_questions_come_last_and_the_verdict_last_of_all():
    survey = Survey.of("demo", [Observation("a", "1"), uncertainty()])
    lines = survey.lines()
    assert lines.index("measured") < lines.index("not settled (1)")
    assert lines[-1] == survey.verdict()


def test_the_verdict_says_whether_a_manifest_is_proposed():
    survey = Survey.of("demo", [])
    assert "no manifest is proposed" in survey.verdict()
    survey.proposal = {"corpus_api": 1}
    assert "a draft manifest is proposed" in survey.verdict()


def test_a_proposal_does_not_make_the_open_questions_go_away():
    # ⚠️ The two are handed over together or not at all.
    survey = Survey.of("demo", [uncertainty()])
    survey.proposal = {"corpus_api": 1}
    assert "1 open question(s)" in survey.verdict()
