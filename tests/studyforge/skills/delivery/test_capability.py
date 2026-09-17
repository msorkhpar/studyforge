"""Mirror of `src/studyforge/skills/delivery/capability.py` (R12).

⚠️ The tests over the markdown parse moved to `test_epics.py` when `W94` split
that half out; what stays here is the index over what the parse produced —
⭐ including **which side delivers a row** (`W92`). What READS a side out of
the pin document is asserted next door, in `test_components.py`.
"""

from __future__ import annotations

import re

import pytest

from studyforge.skills.delivery import (
    ELSEWHERE,
    HERE,
    SIDE_COLUMN,
    SIDES,
    UNDECLARED,
    Components,
    Index,
    IndexRefused,
    read_epic,
    read_sequence,
)
from studyforge.skills.delivery.capability import BANNER, EMPTY
from studyforge.skills.delivery.epics import MILESTONE_ID
from tests.studyforge.skills.delivery import plans


def test_the_bold_some_rows_put_round_their_milestone_does_not_hide_it():
    assert plans.index().milestone_of("SF-02") == "M2"


def test_an_index_of_no_epics_is_refused():
    with pytest.raises(IndexRefused, match="silence"):
        Index.of((), plans.sequence(), Components.none())


def test_a_capability_declared_twice_is_refused_and_both_epics_are_named():
    with pytest.raises(IndexRefused, match="SF-01 is declared twice"):
        Index.of(
            (read_epic("E01.md", plans.EPIC_ONE), read_epic("E02.md", plans.EPIC_ONE)),
            plans.sequence(),
            Components.none(),
        )


def test_asking_for_a_capability_the_index_does_not_carry_is_refused():
    with pytest.raises(IndexRefused, match="no such capability"):
        plans.index().milestone_of("SF-77")


def test_asking_after_a_milestone_the_index_does_not_know_is_refused():
    with pytest.raises(IndexRefused, match="no such milestone"):
        plans.index().after("M9")


def test_after_is_strictly_later_because_it_is_what_a_corpus_forgoes():
    index = plans.index()
    assert [c.id for c in index.after("M1")] == ["SF-02", "SF-20"]
    assert [c.id for c in index.after("M2")] == ["SF-20"]
    assert index.after("M5") == ()


def test_at_is_the_complement_and_the_two_partition_the_index():
    index = plans.index()
    at_every_milestone = [c.id for m in index.milestones for c in index.at(m)]
    assert sorted(at_every_milestone) == sorted(c.id for c in index.capabilities)


def test_the_rendered_document_says_it_is_generated():
    # ⛔ A generated document that does not say so is a document somebody edits.
    assert BANNER in plans.index().render()


def test_rendering_twice_gives_the_same_bytes():
    assert plans.index().render() == plans.index().render()


# --- W238: the order is DECLARED, and the fixture's is not id order ----------


def test_the_fixture_order_is_not_id_order_or_every_test_below_proves_nothing():
    # ⛔ The control this block rests on: over an order ids already sort to, an
    # index that sorted ids would pass every assertion here.
    declared = plans.sequence().milestones
    assert declared == ("M1", "M2", "M6", "M5")
    assert declared != tuple(sorted(declared))


def test_milestones_run_in_the_declared_order_and_an_empty_one_is_kept():
    assert plans.index().milestones == ("M1", "M2", "M6", "M5")


def test_later_compares_places_in_the_declared_order_never_ids():
    index = plans.index()
    assert index.later("M5", than="M6")
    assert not index.later("M6", than="M5")
    assert not index.later("M6", than="M6")


def test_later_refuses_a_milestone_the_order_does_not_declare():
    with pytest.raises(IndexRefused, match="no such milestone"):
        plans.index().later("M9", than="M1")


def test_after_follows_the_declared_order_so_m5_is_after_m6():
    # ⛔ By id, `M5` sorts before `M6` and this would be empty.
    assert [c.id for c in plans.index().after("M6")] == ["SF-20"]


def test_a_declared_milestone_with_no_capability_is_printed_and_says_so():
    rendered = plans.index().render()
    assert f"## M6 — 0 capabilities\n\n{EMPTY}\n" in rendered
    assert rendered.index("## M6 — ") < rendered.index("## M5 — ")


def test_the_document_prints_the_order_it_was_given_and_names_its_source():
    assert "`README.md` declares" in plans.index().render()
    assert "`M1` → `M2` → `M6` → `M5`" in plans.index().render()


def test_a_capability_at_a_milestone_the_order_omits_is_refused():
    omitting = read_sequence("README.md", "### M1 — One\n### M2 — Two\n")
    with pytest.raises(IndexRefused, match="SF-20 lands at M5, which README.md does not declare"):
        Index.of(
            (read_epic("E01.md", plans.EPIC_ONE), read_epic("E05.md", plans.EPIC_TWO)),
            omitting,
            Components.none(),
        )


# --- W94 / Ruling 188: `of` names every capability it cannot place -----------

#: An epic placing two capabilities at milestones the order does not declare.
MISPLACED = """# E20 — Misplaced

### SF-60 — Lands nowhere
**Milestone** M7 · **Team** solo

### SF-61 — Also lands nowhere
**Milestone** M8 · **Team** solo
"""

#: And a second one repeating an id from the first. ⛔ Four reasons in all.
MISPLACED_AGAIN = """# E21 — Misplaced again

### SF-60 — The same id
**Milestone** M7 · **Team** solo
"""


def test_every_capability_that_cannot_be_placed_is_named_not_the_first():
    # ⛔ The row's founding argument: fixing the one that was named and
    # re-running told the reader about the next one, four runs deep.
    with pytest.raises(IndexRefused) as refused:
        Index.of(
            (read_epic("E20.md", MISPLACED), read_epic("E21.md", MISPLACED_AGAIN)),
            read_sequence("README.md", "### M1 — One\n"),
            Components.none(),
        )
    message = str(refused.value)
    assert "4 refusals" in message
    assert "SF-60 lands at M7" in message
    assert "SF-61 lands at M8" in message
    assert "SF-60 is declared twice — in E20 and in E21" in message


def test_one_misplaced_capability_reads_exactly_as_it_did():
    # ⭐ The other direction (R12): a single violation keeps its own sentence,
    # with no count and no preamble in front of it.
    with pytest.raises(IndexRefused) as refused:
        Index.of(
            (read_epic("E05.md", plans.EPIC_TWO),),
            read_sequence("README.md", "### M1 — One\n### M2 — Two\n"),
            Components.none(),
        )
    assert str(refused.value) == (
        "SF-20 lands at M5, which README.md does not declare, so it has no place in the order"
    )


# --- the live population, because a parser tested only on its own fixture has
# --- been tested against the shape somebody imagined ------------------------


def test_every_task_in_every_epic_document_reaches_the_index():
    # ⭐ Counted from the documents by a second, deliberately dumber walk: the
    # index's number must not be checkable only against the code that made it.
    declaration = re.compile(r"^\*\*Milestone\*\*")
    heading = re.compile(r"^###\s+\S")
    counted = 0
    for _, text in plans.live_epics():
        lines = text.splitlines()
        for position, line in enumerate(lines):
            if not heading.match(line):
                continue
            following = [item for item in lines[position + 1 : position + 4] if item.strip()]
            if following and declaration.match(following[0]):
                counted += 1
    index = plans.live_index()
    assert counted == len(index.capabilities) + len(index.cancelled)


def test_the_derivation_the_document_prints_is_computed_and_not_typed():
    # ⛔ Ruling on a measurement pinned as a literal: a thirteenth check leaves
    # a document claiming twelve with the test still green. So the assertion is
    # the derivation, and no number is written here at all.
    index = plans.live_index()
    rendered = index.render()
    empty = sum(1 for milestone in index.milestones if not index.at(milestone))
    assert (
        f"**{len(index.capabilities)} capabilities · {len(index.epics)} epic documents · "
        f"{len(index.milestones)} milestones, {empty} with no capability"
    ) in rendered


def test_every_milestone_section_holds_exactly_the_capabilities_at_it():
    index = plans.live_index()
    rendered = index.render()
    for milestone in index.milestones:
        delivered = index.at(milestone)
        word = "capability" if len(delivered) == 1 else "capabilities"
        assert f"## {milestone} — {len(delivered)} {word}" in rendered
    assert sum(len(index.at(m)) for m in index.milestones) == len(index.capabilities)


def test_the_live_sections_print_in_the_order_the_task_index_declares():
    # ⭐ Re-derived by a second walk over the rendered headings, not over the
    # sequence object the renderer iterated.
    printed = re.findall(rf"^## ({MILESTONE_ID}) — ", plans.live_index().render(), re.M)
    assert tuple(printed) == plans.live_sequence().milestones


def test_no_capability_in_the_live_index_lost_its_area():
    assert all(capability.area for capability in plans.live_index().capabilities)


def test_m10_keeps_its_declared_place_and_is_not_sorted_after_m1():
    index = plans.wide_index()
    assert index.milestones == ("M1", "M2", "M10", "M9")
    assert index.milestones not in (tuple(sorted(index.milestones)), ("M1", "M2", "M9", "M10"))
    assert index.later("M9", than="M10") and index.later("M10", than="M2")
    assert not index.later("M10", than="M9")
    assert [c.id for c in index.after("M10")] == ["SF-41"]
    rendered = index.render()
    assert rendered.index("## M2 — ") < rendered.index("## M10 — ") < rendered.index("## M9 — ")


# --- W92: the index can say NOT THIS SIDE, and it is READ, never judged ------


def test_no_side_the_index_reports_is_outside_the_closed_vocabulary():
    # ⛔ Ruling 185: a narrowed population, never a widened predicate. Every
    # value that reaches a row comes out of `SIDES`.
    assert set(plans.sided_index().sides.values()) <= set(SIDES)
    assert set(plans.live_index().sides.values()) <= set(SIDES)


def test_a_row_owning_inside_a_pinned_component_is_not_this_frameworks():
    assert plans.sided_index().sides["TC-00"] == ELSEWHERE


def test_a_row_owning_a_path_that_reaches_no_component_is_this_frameworks():
    assert plans.sided_index().sides["SF-01"] == HERE


def test_a_row_that_names_no_path_at_all_is_undeclared_and_is_never_guessed():
    # ⛔ The hole is printed rather than smoothed into a confident value: a
    # `why` written against a guess is the defect `W92` reports, one layer on.
    assert plans.sided_index().sides["TC-01"] == UNDECLARED


def test_an_epics_preamble_places_a_row_whose_own_cell_names_no_path():
    # ⭐ The weak derivation, and it is the one that carries the shared
    # components: their prose rows own "the job API", not a path.
    text = plans.EPIC_ELSEWHERE.replace(
        "# E12 — A shared component",
        "# E12 — A shared component\n\nIt becomes **`elsewhere-component`**, its own repository.",
    )
    index = Index.of((read_epic("E12.md", text),), plans.sequence(), plans.components())
    assert index.sides["TC-01"] == ELSEWHERE


def test_a_workspace_that_pins_nothing_but_itself_places_every_row_here():
    epics = (read_epic("E12.md", plans.EPIC_ELSEWHERE),)
    index = Index.of(epics, plans.sequence(), Components.none())
    assert set(index.sides.values()) == {HERE, UNDECLARED}
    assert index.sides["TC-00"] == HERE


def test_asking_for_a_side_outside_the_vocabulary_is_refused():
    with pytest.raises(IndexRefused, match="no such side"):
        plans.sided_index().on("somebody else's")


def test_the_three_sides_partition_the_index():
    index = plans.live_index()
    counted = sum(len(index.on(side)) for side in SIDES)
    assert counted == len(index.capabilities)


# --- the column appears when the distinction applies, and not when it does not


def test_the_column_is_rendered_when_at_least_one_row_is_not_this_frameworks():
    index = plans.sided_index()
    assert index.distinguishes
    rendered = index.render()
    assert f"| capability | what it is | area | {SIDE_COLUMN} | waits on |" in rendered
    assert f"| `TC-00` | The runner image | A shared component | {ELSEWHERE} |" in rendered


def test_the_column_is_absent_when_no_row_is_delivered_anywhere_else():
    # ⭐ A column that would say the same thing in every row says nothing. A
    # plan where the distinction does not apply renders what it always did.
    index = plans.index()
    assert not index.distinguishes
    rendered = index.render()
    assert "| capability | what it is | area | waits on |" in rendered
    assert SIDE_COLUMN not in rendered
    assert HERE not in rendered


def test_the_legend_is_printed_only_beside_a_table_that_carries_the_column():
    assert SIDE_COLUMN in plans.sided_index().render()
    assert "READ, never judged" in plans.sided_index().render()
    assert "READ, never judged" not in plans.index().render()


def test_no_component_is_ever_NAMED_in_what_the_index_renders():
    # ⛔ R1 in the direction that is easy to miss: the pin document's names are
    # READ and never printed. The distinction a planner needs is structural.
    index = plans.live_index()
    rendered = index.render()
    assert index.components.names, "the live workspace pins no component, so this checks nothing"
    for name in index.components.names:
        assert name not in rendered, name


def test_the_split_by_side_the_document_prints_is_derived_too():
    index = plans.live_index()
    assert (
        f"**Of those capabilities, {len(index.on(HERE))} are this framework's to deliver, "
        f"{len(index.on(ELSEWHERE))} are delivered inside a component pinned somewhere "
        f"else, and {len(index.on(UNDECLARED))} declare no path at all.**"
    ) in index.render()
