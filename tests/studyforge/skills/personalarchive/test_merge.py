"""Mirror of `src/studyforge/skills/personalarchive/merge.py` (R12): the rule, bound to `SKILL.md`.

⛔ The worked table in `SKILL.md` is parsed and every row is run through `merged`, so the
document and the code cannot state two different rules. The same rows land in a real
store in `test_record.py`.
"""

from __future__ import annotations

import pytest

from studyforge.skills.personalarchive.merge import (
    FIRST_AFTER_LAST,
    MERGED,
    NO_FIRST_PASS,
    ONE_RUN_NOT_THE_PASS,
    OUTCOMES,
    REFUSALS,
    REFUSED,
    RESTORED,
    UNCHANGED,
    later,
    merged,
    refusal,
)
from tests.studyforge.skills.personalarchive.archiving import COMMANDS, TIMES, worked_rows

ROWS = worked_rows()
IDS = [row[0] for row in ROWS]
BELIEVED = [row for row in ROWS if row[4] != REFUSED]


def made(runs: int, first: str | None, at: str, passed: bool) -> dict:
    return {
        "first_passed_at": TIMES.get(first) if first else None,
        "last": {
            "at": TIMES.get(at, at),
            "commands": list(COMMANDS),
            "exit": 0 if passed else 1,
            "mode": "test",
            "passed": passed,
        },
        "runs": runs,
    }


@pytest.mark.parametrize(("case", "here", "archived", "after", "says"), ROWS, ids=IDS)
def test_every_worked_row_of_skill_md_is_what_the_code_does(case, here, archived, after, says):
    plan = merged(here, archived)
    assert (plan.outcome, plan.entry) == (says, after), case


def test_the_worked_table_reaches_every_outcome_and_every_refusal():
    # ⛔ A table that skipped an outcome would bind the document to less than the code does.
    assert {row[4] for row in ROWS} == set(OUTCOMES)
    reasons = {
        merged(here, archived).reason for _, here, archived, _, says in ROWS if says == REFUSED
    }
    assert reasons == set(REFUSALS)


@pytest.mark.parametrize(
    ("case", "here", "archived", "after", "says"), BELIEVED, ids=[row[0] for row in BELIEVED]
)
def test_the_merge_is_a_join_so_importing_the_same_entry_again_changes_nothing(
    case, here, archived, after, says
):
    again = merged(after, archived)
    assert (again.outcome, again.entry, again.runs) == (UNCHANGED, after, ()), case


def test_the_runs_to_record_are_exactly_what_moves_the_count_and_end_on_the_last_run():
    for case, here, archived, after, says in ROWS:
        plan = merged(here, archived)
        before = here["runs"] if here else 0
        if says in (RESTORED, MERGED):
            assert len(plan.runs) == after["runs"] - before, case
            assert plan.runs[-1].when == after["last"]["at"], case
            assert plan.runs[-1].exit_code == after["last"]["exit"], case
        else:
            assert plan.runs == (), case


def test_a_count_is_the_larger_never_the_sum():
    here, archived = made(3, "t1", "t2", False), made(3, "t1", "t2", False)
    assert merged(here, archived).outcome == UNCHANGED
    assert merged(made(2, "t1", "t2", False), made(5, "t1", "t2", False)).entry["runs"] == 5


def test_each_entry_the_store_could_never_have_written_is_refused_by_name():
    assert refusal(made(2, None, "t2", True)) == NO_FIRST_PASS
    assert refusal(made(1, "t1", "t2", False)) == ONE_RUN_NOT_THE_PASS
    assert refusal(made(1, "t1", "t2", True)) == ONE_RUN_NOT_THE_PASS
    assert refusal(made(3, "t4", "t2", False)) == FIRST_AFTER_LAST


def test_every_entry_the_store_can_write_is_believed():
    for entry in (
        made(1, "t1", "t1", True),
        made(1, None, "t1", False),
        made(2, "t1", "t2", False),
        made(2, "t2", "t2", True),
    ):
        assert refusal(entry) is None, entry


def test_an_imported_pass_is_believed_as_recorded_with_no_run_that_shows_it():
    # ⚠️ The record keeps no history, so the belief rule cannot ask for one.
    plan = merged(None, made(5, "t1", "t3", False))
    assert plan.outcome == RESTORED
    assert plan.entry["first_passed_at"] == TIMES["t1"]


def test_this_machines_first_pass_never_moves_even_to_an_earlier_one():
    plan = merged(made(2, "t3", "t3", True), made(2, "t1", "t2", False))
    assert plan.outcome == UNCHANGED


def test_timestamps_that_cannot_be_ordered_are_never_later_so_this_machines_run_stands():
    assert later(TIMES["t2"], TIMES["t1"]) and not later(TIMES["t1"], TIMES["t2"])
    naive = "2026-09-09T10:00:00"
    assert later(naive, TIMES["t1"]) is False and later(TIMES["t1"], naive) is False
    plan = merged(made(2, None, "t1", False), made(3, None, naive, False))
    assert plan.entry["last"]["at"] == TIMES["t1"] and plan.entry["runs"] == 3


def test_each_report_line_says_what_was_done_to_which_practice():
    key = "basics/intro/unit-01/practice-1"
    restored = merged(None, made(3, "t1", "t2", False)).line(key)
    assert restored == f"progress restored {key} runs 3 first {TIMES['t1']}"
    fresh = merged(None, made(1, None, "t1", False)).line(key)
    assert fresh == f"progress restored {key} runs 1 first none"
    both = merged(made(4, None, "t4", False), made(2, "t1", "t2", False)).line(key)
    assert both == f"progress merged {key} runs 4->6 first archive last kept"
    assert merged(made(3, "t1", "t2", False), made(3, "t1", "t2", False)).line(key) == (
        f"progress unchanged {key}"
    )
    refused = merged(None, made(2, None, "t2", True)).line(key)
    assert refused == f"progress refused {key} {NO_FIRST_PASS}"
