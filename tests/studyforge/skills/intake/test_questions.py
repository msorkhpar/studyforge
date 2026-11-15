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
    assert _q(kind="choice", choices=("a",), default="a").kind == "choice"


def test_an_unknown_track_is_refused():
    with pytest.raises(ValueError):
        _q(tracks=frozenset({"nonsense"}))


def test_an_unknown_tier_is_refused():
    with pytest.raises(ValueError):
        _q(tier="never")


def test_a_choice_question_needs_choices_and_others_must_have_none():
    with pytest.raises(ValueError):
        _q(kind="choice")
    with pytest.raises(ValueError):
        _q(kind="text", choices=("a",))


def test_a_boolean_default_is_spelled_as_json_and_read_as_a_bool():
    assert _q(kind="boolean", default="true").default_value is True
    assert _q(kind="boolean", default="false").default_value is False
    assert _q(default="d").default_value == "d"
    with pytest.raises(ValueError, match="true or false"):
        _q(kind="boolean", default="yes")


def test_a_choice_default_is_one_of_its_choices():
    with pytest.raises(ValueError, match="one of its choices"):
        _q(kind="choice", choices=("a", "b"), default="c")
