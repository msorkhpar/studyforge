"""Mirror of `src/studyforge/skills/delivery/epics.py` (R12).

⚠️ Most of this file moved here from `test_capability.py` when `W94` split the
reading half of that module out; the assertions are unchanged, so the tests
that already pinned this behaviour still pin it.
"""

from __future__ import annotations

import pytest

from studyforge.skills.delivery import IndexRefused, read_epic, read_epics, read_sequence
from tests.studyforge.skills.delivery import plans

#: A document whose FOUR rows are each unreadable, and unreadable in both of
#: the two ways `read_epic` refuses. ⛔ The population the first-witness form
#: reported one of.
FOUR_BAD_ROWS = """# E09 — Delivery

### Something
**Milestone** M1

### SF-01 — Unreadable milestone
**Milestone** Mx · **Team** solo

### Another thing
**Milestone** M2

### SF-02 — Also unreadable
**Milestone** TBD · **Team** solo
"""


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


def test_a_task_heading_with_no_id_is_refused_rather_than_skipped():
    # ⚠️ Skipping it would be the same silence the adjacency rule exists to
    # avoid, arriving one line later.
    with pytest.raises(IndexRefused, match="carries no id"):
        read_epic("E09.md", "# E09 — Delivery\n\n### Something\n**Milestone** M1\n")


def test_a_document_with_no_area_title_is_refused():
    with pytest.raises(IndexRefused, match="no `# E<nn>"):
        read_epic("stray.md", "### SF-01 — A thing\n**Milestone** M1\n")


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


# --- W247: a milestone id of any width is read, and only a dash cancels ------


def test_a_row_at_m10_is_a_capability_at_m10_and_never_cancelled():
    epic = read_epic("E12.md", plans.WIDE_EPIC)
    assert epic.cancelled == ()
    assert [(c.id, c.milestone) for c in epic.capabilities] == [("SF-40", "M10"), ("SF-41", "M9")]


def test_an_m10_section_is_declared_in_the_order():
    assert read_sequence("README.md", plans.WIDE_SEQUENCE).milestones == ("M1", "M2", "M10", "M9")


@pytest.mark.parametrize("unreadable", ["Mx", "TBD", "m10", "M10a"])
def test_a_milestone_that_is_neither_an_id_nor_a_dash_is_refused_by_name(unreadable):
    text = (
        f"# E12 — Wide ids\n\n### SF-42 — Unreadable\n**Milestone** {unreadable} · **Team** solo\n"
    )
    with pytest.raises(IndexRefused, match=r"E12\.md line 3: SF-42 .*never counted as cancelled"):
        read_epic("E12.md", text)


# --- W94 / Ruling 188: the refusal names its whole population ----------------


def test_a_document_with_four_unreadable_rows_names_all_four():
    # ⛔ The defect this row exists for: the reader fixed the row that was
    # named, re-ran, and was told about the next one — four times.
    with pytest.raises(IndexRefused) as refused:
        read_epic("E09.md", FOUR_BAD_ROWS)
    message = str(refused.value)
    assert "4 refusals" in message
    assert [line for line in ("line 3:", "line 6:", "line 9:", "line 12:") if line in message] == [
        "line 3:",
        "line 6:",
        "line 9:",
        "line 12:",
    ]


def test_a_document_with_one_unreadable_row_reads_exactly_as_it_did():
    # ⭐ The other direction (R12): the single-violation message did not move,
    # so none of the refusals that were already right moved either.
    with pytest.raises(IndexRefused) as refused:
        read_epic("E09.md", "# E09 — Delivery\n\n### Something\n**Milestone** M1\n")
    assert str(refused.value) == (
        "E09.md line 3: a task heading declares a milestone and carries no id. "
        "⛔ The line is not quoted: it is caller text"
    )


def test_reading_several_documents_names_every_one_that_cannot_be_read():
    # ⛔ The member no function-local instrument can see: `read_epic` is right
    # about its own document and first-witness about a set of them.
    with pytest.raises(IndexRefused) as refused:
        read_epics(
            (
                ("E01.md", plans.EPIC_ONE),
                ("E08.md", "### SF-30 — No title above it\n**Milestone** M1\n"),
                ("E09.md", FOUR_BAD_ROWS),
            )
        )
    message = str(refused.value)
    assert "2 refusals" in message
    assert "E08.md: no `# E<nn>" in message
    assert "E09.md line 3:" in message and "E09.md line 12:" in message


def test_reading_several_documents_where_one_fails_reads_exactly_as_one_would():
    unreadable = ("E08.md", "### SF-30 — No title above it\n**Milestone** M1\n")
    with pytest.raises(IndexRefused) as several:
        read_epics((("E01.md", plans.EPIC_ONE), unreadable))
    with pytest.raises(IndexRefused) as alone:
        read_epic(*unreadable)
    assert str(several.value) == str(alone.value)


def test_reading_several_readable_documents_gives_them_all_back():
    read = read_epics((("E01.md", plans.EPIC_ONE), ("E05.md", plans.EPIC_TWO)))
    assert [epic.epic for epic in read] == ["E01", "E05"]


# --- W92: the `Owns` cell is read VERBATIM, and nothing here interprets it ---


def test_the_owns_cell_is_carried_onto_the_capability_it_declares():
    # ⭐ It is the only thing any document says about whose work a row is, and
    # a walk that read only the declaration line could never see it.
    epic = read_epic("E01.md", plans.EPIC_ONE)
    assert [c.owns for c in epic.capabilities] == ["`address/`", "`corpus/manifest/`"]


def test_a_row_that_declares_no_owns_cell_carries_an_empty_one_and_is_not_refused():
    text = "# E09 — Delivery\n\n### SF-90 — A row with no Owns\n**Milestone** M1 · **Team** solo\n"
    assert read_epic("E09.md", text).capabilities[0].owns == ""


def test_this_module_forms_no_opinion_about_the_side_a_row_is_delivered_on():
    # ⛔ The seam, asserted rather than described: this module carries the cell
    # and `components` reads it. A Capability has no side to ask for.
    epic = read_epic("E01.md", plans.EPIC_ONE)
    assert not hasattr(epic.capabilities[0], "side")


def test_the_epics_preamble_is_carried_so_a_component_can_be_read_off_it():
    epic = read_epic("E01.md", plans.EPIC_ONE)
    assert epic.preamble.startswith("# E01 — Core contracts")
    assert "### SF-01" not in epic.preamble
