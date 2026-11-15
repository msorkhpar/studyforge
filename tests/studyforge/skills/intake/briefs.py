"""Fixture for the intake tests: a brief that answers every costly question validly."""

from __future__ import annotations

from studyforge.skills.intake.bank import BANK
from studyforge.skills.intake.questions import applies

PILOT = "Shortest paths on a grid"

_VALUES: dict[str, object] = {
    "writing.pilot": PILOT,
    "narration.wanted": "no",
    "quiz.mocks": False,
    "privacy.fresh_history": True,
    "interview.mocks": True,
    "interview.job_description": "private:job-description.md",
    "convert.repository": "env:COURSE_SOURCE_REPOSITORY",
    "privacy.commit_identity": "env:COURSE_COMMIT_IDENTITY",
    "publish.holder": "env:COURSE_HOLDER",
    "publish.repository": "env:COURSE_REPOSITORY",
    "publish.namespace": "env:COURSE_IMAGE_NAMESPACE",
}


def _answer(value: object) -> dict:
    return {"status": "answered", "value": value, "decided_by": "author"}


def clean_brief(track: str) -> dict:
    """A JSON-shaped brief for `track` with every applicable costly question answered."""

    class _Seen:
        def __init__(self, value: object) -> None:
            self.status, self.value = "answered", value

    answers: dict[str, dict] = {}
    seen: dict[str, _Seen] = {}
    for question in BANK:
        if question.tier != "costly" or not applies(question, track, seen):
            continue
        value = _VALUES.get(question.id, f"Decision recorded for {question.id}.")
        answers[question.id] = _answer(value)
        seen[question.id] = _Seen(value)
    return {
        "brief_api": 1,
        "title": "Graph Basics",
        "track": track,
        "answers": answers,
        "outline": [
            {
                "title": "Foundations",
                "modules": [
                    {
                        "title": PILOT,
                        "pilot": True,
                        "lessons": [{"title": "Breadth-first search", "depth": "core"}],
                    },
                    {
                        "title": "Weighted graphs",
                        "lessons": [{"title": "Dijkstra", "depth": "deep"}],
                    },
                ],
            }
        ],
    }
