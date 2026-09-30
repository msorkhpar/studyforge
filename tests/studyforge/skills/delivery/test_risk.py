"""Mirror of `src/studyforge/skills/delivery/risk.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.delivery import INSIDE, OUTSIDE, Carrier, RiskRefused, concentration
from tests.studyforge.skills.delivery import plans


def test_ranking_without_declaring_the_outside_is_refused():
    # ⛔ A plan whose risk sits in another repository reads as a small
    # plan, and a report that could only see its own tasks would say so.
    with pytest.raises(RiskRefused, match="undeclared outside"):
        concentration(plans.backlog().tasks)


def test_an_empty_outside_is_a_declaration_and_is_accepted():
    # ⭐ Passing `()` says there is none. Omitting it says nothing, and saying
    # nothing is the failure.
    report = concentration(plans.backlog().tasks, outside=())
    assert report.outside_share == 0.0


def test_risk_outside_the_repository_reaches_the_headline():
    report = concentration(
        plans.backlog().tasks,
        outside=(Carrier("RS-28", "the framework, not started", 20),),
    )
    assert report.outside_share > 0.5
    assert OUTSIDE in report.headline()
    assert "80%" in report.headline()


def test_the_heaviest_carriers_are_the_fewest_reaching_half_the_work():
    report = concentration(plans.backlog().tasks, outside=(Carrier("RS-28", "the framework", 20),))
    assert [carrier.id for carrier in report.heaviest] == ["RS-28"]
    assert report.concentrated


def test_an_even_plan_is_reported_as_spread():
    tasks = tuple(plans.reading_task(f"C-0{n}") for n in range(1, 5))
    report = concentration(tasks, outside=())
    assert not report.concentrated
    assert "⭐ spread" in report.headline()


def test_the_report_prints_the_whole_population_and_not_a_top_slice():
    # ⛔ R6: an instrument reducing a population to a scalar prints
    # that population in full.
    tasks = tuple(plans.reading_task(f"C-0{n}") for n in range(1, 5))
    report = concentration(tasks, outside=(Carrier("RS-28", "the framework", 3),))
    rows = [line for line in report.lines() if line.startswith("| `")]
    assert len(rows) == len(tasks) + 1 == len(report.carriers)


def test_a_carrier_named_inside_and_outside_is_refused():
    # ⛔ It inflates the total and flatters every share in the table.
    with pytest.raises(RiskRefused, match="1 carrier id\\(s\\) counted twice"):
        concentration(plans.backlog().tasks, outside=(Carrier("C-01", "somewhere else", 2),))


def test_a_plan_with_no_carriers_at_all_is_refused():
    with pytest.raises(RiskRefused, match="no plan here to rank"):
        concentration((), outside=())


def test_a_carrier_with_no_effort_is_refused():
    with pytest.raises(RiskRefused, match="which is not work"):
        Carrier("RS-28", "the framework", 0)


def test_a_carrier_with_no_name_or_no_place_is_refused():
    with pytest.raises(RiskRefused, match="names what it is and where it lives"):
        Carrier("RS-28", "  ", 3)


def test_neither_side_of_the_report_is_the_unmarked_default():
    # ⚠️ `INSIDE` is a literal too, so a reader scanning the table can find
    # every row of either kind.
    report = concentration(plans.backlog().tasks, outside=(Carrier("RS-28", OUTSIDE, 3),))
    wheres = {carrier.where for carrier in report.carriers}
    assert wheres == {INSIDE, OUTSIDE}
    assert not Carrier("C-01", INSIDE, 1).is_outside


def test_the_headline_carries_both_numbers_a_reader_acts_on():
    report = concentration(plans.backlog().tasks, outside=())
    assert f"of {report.total} " in report.headline()
    assert f"{len(report.heaviest)} of {len(report.carriers)} carriers" in report.headline()
