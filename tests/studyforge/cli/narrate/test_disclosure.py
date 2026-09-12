"""Mirror of `src/studyforge/cli/narrate/disclosure.py` (R12).

⭐ The predicate in isolation, over hand-built records. The same predicate
over a real corpus and a planted entry is asserted in `test_stage.py` and
`test_prune.py`.
"""

from __future__ import annotations

from studyforge.cli.narrate.disclosure import Walk, dead_entries
from studyforge.narrate.synth import Clip, State


def state(*ids: str) -> State:
    return State(clips={speech_id: Clip(f"{speech_id}-aaaaaaaa.mp3", "c") for speech_id in ids})


def test_an_entry_the_walk_produced_is_not_dead():
    assert dead_entries(state("u.s.b1"), Walk(frozenset({"u.s.b1"}))) == ()


def test_every_entry_the_walk_did_not_produce_is_dead_and_sorted():
    walk = Walk(frozenset({"u.s.b1"}))
    assert dead_entries(state("u.s.b2", "u.s.b1", "u.s.b10"), walk) == ("u.s.b10", "u.s.b2")


def test_the_count_moves_with_one_planted_entry():
    # ⛔ The pass condition is the MOVED count, so the zero beside it is asserted too.
    walk = Walk(frozenset({"u.s.b1"}))
    assert len(dead_entries(state("u.s.b1"), walk)) == 0
    assert len(dead_entries(state("u.s.b1", "u.gone.b1"), walk)) == 1


def test_an_absent_record_has_no_dead_entry():
    assert dead_entries(State(clips={}, present=False), Walk(frozenset())) == ()


def test_a_walk_that_missed_a_declared_unit_is_not_whole():
    assert Walk(frozenset()).whole is True
    assert Walk(frozenset(), unwalked=("a/unit-02",)).whole is False
