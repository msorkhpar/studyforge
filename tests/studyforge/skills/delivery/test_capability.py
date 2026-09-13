"""Mirror of `src/studyforge/skills/delivery/capability.py` (R12)."""

from __future__ import annotations

import re

import pytest

from studyforge.skills.delivery import Index, IndexRefused, read_epic, read_sequence
from studyforge.skills.delivery.capability import BANNER, EMPTY
from tests.studyforge.skills.delivery import plans


def test_a_heading_is_a_task_only_when_the_next_line_declares_a_milestone():
    # ⛔ The rule is adjacency, never a list of headings to skip. E01's carried
    # ruling is a `###` heading and is not a capability.
    epic = read_epic("E01.md", plans.EPIC_ONE)
    assert [c.id for c in epic.capabilities] == ["SF-01", "SF-02"]


def test_the_shouting_in_a_heading_is_not_part_of_the_capabilitys_name():
    epic = read_epic("E01.md", plans.EPIC_ONE)
    assert epic.capabilities[1].what == "Corpus manifest"


def test_a_row_that_declares_no_milestone_is_cancelled_and_is_counted():
    # ⛔ A generator that quietly discards input is one nobody can check.
    epic = read_epic("E05.md", plans.EPIC_TWO)
    assert epic.cancelled == ("SF-99",)
    assert [c.id for c in epic.capabilities] == ["SF-20"]


def test_the_bold_some_rows_put_round_their_milestone_does_not_hide_it():
    assert plans.index().milestone_of("SF-02") == "M2"


def test_a_task_heading_with_no_id_is_refused_rather_than_skipped():
    # ⚠️ Skipping it would be the same silence the adjacency rule exists to
    # avoid, arriving one line later.
    with pytest.raises(IndexRefused, match="carries no id"):
        read_epic("E09.md", "# E09 — Delivery\n\n### Something\n**Milestone** M1\n")


def test_a_document_with_no_area_title_is_refused():
    with pytest.raises(IndexRefused, match="no `# E<nn>"):
        read_epic("stray.md", "### SF-01 — A thing\n**Milestone** M1\n")


def test_an_index_of_no_epics_is_refused():
    with pytest.raises(IndexRefused, match="silence"):
        Index.of((), plans.sequence())


def test_a_capability_declared_twice_is_refused_and_both_epics_are_named():
    with pytest.raises(IndexRefused, match="SF-01 is declared twice"):
        Index.of(
            (read_epic("E01.md", plans.EPIC_ONE), read_epic("E02.md", plans.EPIC_ONE)),
            plans.sequence(),
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


def test_a_heading_that_names_milestones_but_is_not_a_section_declares_nothing():
    # ⭐ The fixture's `### ⛔ REORDERED — `M2` → `M6` → `M5`` is prose.
    assert read_sequence("README.md", "### ⛔ REORDERED — `M5`\n### M1 — One\n").milestones == (
        "M1",
    )


def test_a_document_declaring_no_milestone_is_refused():
    with pytest.raises(IndexRefused, match="declares no order"):
        read_sequence("README.md", "# A task index\n\n#### M1 — Too deep to be a section\n")


def test_a_milestone_declared_twice_is_refused_because_its_place_is_ambiguous():
    with pytest.raises(IndexRefused, match="M1 declared twice"):
        read_sequence("README.md", "### M1 — One\n### M2 — Two\n### M1 — One again\n")


def test_the_order_document_is_cited_by_a_bare_filename_only():
    with pytest.raises(IndexRefused, match="bare filename"):
        read_sequence("docs/tasks/README.md", plans.SEQUENCE)


def test_a_capability_at_a_milestone_the_order_omits_is_refused():
    omitting = read_sequence("README.md", "### M1 — One\n### M2 — Two\n")
    with pytest.raises(IndexRefused, match="SF-20 lands at M5, which README.md does not declare"):
        Index.of(
            (read_epic("E01.md", plans.EPIC_ONE), read_epic("E05.md", plans.EPIC_TWO)), omitting
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
    printed = re.findall(r"^## (M[0-9]) — ", plans.live_index().render(), re.M)
    assert tuple(printed) == plans.live_sequence().milestones


def test_no_capability_in_the_live_index_lost_its_area():
    assert all(capability.area for capability in plans.live_index().capabilities)
