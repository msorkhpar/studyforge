"""Mirror of `src/studyforge/skills/intake/questions.py`."""

from __future__ import annotations

from collections import namedtuple

import pytest

from studyforge.skills.intake.questions import HEDGE, Question, applies

Ans = namedtuple("Ans", "status value")


def _q(**kw):
    base = dict(
        id="practice.shape", group="practice", ask="a?", why="w", default="d",
        tracks=frozenset({"topic"}), tier="costly",
    )
    base.update(kw)
    return Question(**base)


def test_a_question_outside_the_track_does_not_apply():
    assert not applies(_q(), "exam", {})


def test_an_ungated_question_applies_on_its_track():
    assert applies(_q(), "topic", {})


def test_a_gated_question_applies_only_when_the_gate_holds_a_listed_value():
    q = _q(id="narration.style", group="narration",
           depends_on=("narration.wanted", ("yes",)))
    assert applies(q, "topic", {"narration.wanted": Ans("answered", "yes")})
    assert not applies(q, "topic", {"narration.wanted": Ans("answered", "no")})


def test_a_gate_that_is_deferred_or_missing_does_not_apply_its_dependants():
    q = _q(id="narration.style", group="narration",
           depends_on=("narration.wanted", ("yes",)))
    assert not applies(q, "topic", {})
    assert not applies(q, "topic", {"narration.wanted": Ans("deferred", "yes")})
    assert not applies(q, "topic", {"narration.wanted": Ans("proposed", "yes")})


def test_hedge_matches_whole_words_only():
    assert HEDGE.search("TBD")
    assert HEDGE.search("Do it where possible")
    assert HEDGE.search("to be decided")
    assert HEDGE.search("if time allows")
    assert not HEDGE.search("maybeline")


def test_group_is_the_id_prefix():
    with pytest.raises(ValueError):
        _q(group="other")
    with pytest.raises(ValueError):
        _q(kind="number")
    assert _q(kind="choice", choices=("a",)).kind == "choice"
