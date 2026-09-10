"""Mirror of `src/studyforge/skills/delivery/capability.py` (R12)."""

from __future__ import annotations

import re

import pytest

from studyforge.skills.delivery import Index, IndexRefused, read_epic
from studyforge.skills.delivery.capability import BANNER
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
        Index.of(())


def test_a_capability_declared_twice_is_refused_and_both_epics_are_named():
    with pytest.raises(IndexRefused, match="SF-01 is declared twice"):
        Index.of((read_epic("E01.md", plans.EPIC_ONE), read_epic("E02.md", plans.EPIC_ONE)))


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


# --- the live population, because a parser tested only on its own fixture has
# --- been tested against the shape somebody imagined ------------------------


def live_index() -> Index:
    return Index.of(read_epic(name, text) for name, text in plans.live_epics())


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
    index = live_index()
    assert counted == len(index.capabilities) + len(index.cancelled)


def test_the_derivation_the_document_prints_is_computed_and_not_typed():
    # ⛔ Ruling on a measurement pinned as a literal: a thirteenth check leaves
    # a document claiming twelve with the test still green. So the assertion is
    # the derivation, and the only number written here is `1` for the one
    # cancelled row — itself re-derived from the documents below.
    index = live_index()
    rendered = index.render()
    assert (
        f"**{len(index.capabilities)} capabilities · {len(index.epics)} epic documents · "
        f"{len(index.milestones)} milestones"
    ) in rendered


def test_every_milestone_section_holds_exactly_the_capabilities_at_it():
    index = live_index()
    rendered = index.render()
    for milestone in index.milestones:
        delivered = index.at(milestone)
        word = "capability" if len(delivered) == 1 else "capabilities"
        assert f"## {milestone} — {len(delivered)} {word}" in rendered
    assert sum(len(index.at(m)) for m in index.milestones) == len(index.capabilities)


def test_no_capability_in_the_live_index_lost_its_area():
    assert all(capability.area for capability in live_index().capabilities)
