"""A heading that links a file is not a unit by the link alone.

⭐ Two halves. `cut` says whether a linked file's headings are regions (Ruling
92); the record reads a heading that links such a file, where the group labels
stand and opening no entry, as a container of sub-file units. ⛔ Asserted both
ways, over `sources.linked_regions`, which is shaped like the finding.
"""

from __future__ import annotations

import json

from studyforge.corpus.manifest import Classification, parse
from studyforge.skills.reconnaissance import find, survey, take
from studyforge.skills.reconnaissance.regions import cut
from studyforge.validate.headings import region
from tests.studyforge.skills.reconnaissance import sources

# --------------------------------------------------------------------------
# `cut`: which files are regions, and the reason for every one that is not
# --------------------------------------------------------------------------


def regions_of(tmp_path, text):
    (tmp_path / "f.md").write_text(text, encoding="utf-8")
    return cut(tmp_path, "f.md")


def test_top_level_headings_that_repeat_are_the_regions(tmp_path):
    found = regions_of(tmp_path, sources.CASES)
    assert found.cut and found.depth == 1
    assert found.sections == ("1. Card issuance", "2. Accounts", "3. Payments")


def test_a_title_above_the_regions_is_not_one(tmp_path):
    found = regions_of(tmp_path, "# Title\n\n## A\n\n## B\n")
    assert found.cut and found.sections == ("A", "B")


def test_every_proposed_section_names_exactly_one_region_the_validator_reads(tmp_path):
    # ⭐ The judge is `check_completeness`'s own region reader.
    for section in regions_of(tmp_path, sources.CASES).sections:
        assert region(sources.CASES, section).occurrences == 1, section


def test_a_file_that_is_one_unit_says_so(tmp_path):
    found = regions_of(tmp_path, "# One unit\n\nProse.\n")
    assert not found.cut and "one unit" in found.why


def test_a_heading_inside_a_fence_is_not_a_region(tmp_path):
    found = regions_of(tmp_path, "# Unit\n\n```sh\n# a comment\n```\n")
    assert not found.cut


def test_a_shallower_heading_after_a_region_refuses_the_cut_by_name(tmp_path):
    found = regions_of(tmp_path, "## A\n\n## B\n\n# Appendix\n")
    assert not found.cut and "'Appendix'" in found.why


def test_a_section_that_is_not_unique_refuses_the_cut_by_name(tmp_path):
    found = regions_of(tmp_path, "# Case\n\n# Other\n\n## Case\n")
    assert not found.cut and "'Case'" in found.why


# --------------------------------------------------------------------------
# ⛔ the record: a linked heading at a label's position is a container
# --------------------------------------------------------------------------


def record_of(root):
    return find(take(root))


def shaped(record):
    return [(e.target, e.title, e.ordinal, e.group, e.section) for e in record.entries]


def test_a_heading_linking_a_file_of_regions_is_a_container_not_a_unit(tmp_path):
    record = record_of(sources.linked_regions(tmp_path / "c"))
    assert record.groups == ["Fundamentals", "Server", "Test cases"]
    assert ("TestCases.md", None) not in [(e.target, e.section) for e in record.entries]
    assert shaped(record)[-3:] == [
        ("TestCases.md", "Card issuance", "1", "Test cases", "1. Card issuance"),
        ("TestCases.md", "Accounts", "2", "Test cases", "2. Accounts"),
        ("TestCases.md", "Payments", "3", "Test cases", "3. Payments"),
    ]
    assert len(record.entries) == 8


def test_a_linked_heading_inside_a_run_of_entries_stays_a_unit(tmp_path):
    # ⚠️ Its file has two subsections, so the shape alone would cut it.
    record = record_of(sources.linked_regions(tmp_path / "c"))
    # ⭐ A heading-form entry reads the ordinal its bullet twin reads.
    heading = [
        (e.target, e.ordinal, e.group, e.section) for e in record.entries if e.target == "src/3.md"
    ]
    assert heading == [("src/3.md", "3", "Fundamentals", None)]


def test_a_linked_heading_that_opens_entries_stays_an_entry(tmp_path):
    record = record_of(sources.linked_regions(tmp_path / "c", linked_aggregate=True))
    assert record.groups == ["Fundamentals", "Test cases"]
    assert ("src/Server.md", None) in [(e.target, e.section) for e in record.entries]


def test_a_linked_heading_whose_file_is_one_unit_stays_an_entry_and_is_asked_about(tmp_path):
    root = sources.linked_regions(tmp_path / "c", cases="# Test cases\n\nProse.\n")
    record = record_of(root)
    assert ("TestCases.md", "Server", None) in [
        (e.target, e.group, e.section) for e in record.entries
    ]
    assert [found.path for found in record.uncut] == ["TestCases.md"]
    asked = [q for q in survey(root).uncertainties if q.question.startswith("is TestCases.md one")]
    assert len(asked) == 1 and "one unit" in asked[0].why


def test_the_survey_proposes_the_regions_file_as_a_container(tmp_path):
    found = survey(sources.linked_regions(tmp_path / "c"))
    measured = {o.what: o.measured for o in found.observations}
    assert measured["containers whose units are regions of one file"] == "1 ['TestCases.md: 3']"
    assert measured["groups it expresses"].startswith("3 ")
    assert any(
        q.question == "is TestCases.md a container of 3 units, one per region?"
        for q in found.uncertainties
    )


def test_the_draft_is_accepted_and_includes_the_regions_file_but_not_the_record(tmp_path):
    root = sources.linked_regions(tmp_path / "c")
    content = parse(json.dumps(sources.settled(survey(root).proposal))).content
    assert content.classify("TestCases.md") is Classification.INCLUDED
    assert content.classify("README.md") is not Classification.INCLUDED


# --------------------------------------------------------------------------
# ⭐ the control: the same heading, linking nothing, reads as it did
# --------------------------------------------------------------------------


def test_a_heading_that_links_nothing_is_unchanged(tmp_path):
    control = sources.linked_regions(tmp_path / "control", link=False)
    record = record_of(control)
    readme = control / "README.md"
    readme.write_text(readme.read_text("utf-8").replace("# Test cases\n", ""), "utf-8")
    assert shaped(record) == shaped(record_of(control))
    assert record.groups == ["Fundamentals", "Server"] == record_of(control).groups
    assert record.containers == [] and record.uncut == []
    # ⚠️ An unlinked file no include reads is proposed `not_material`, not
    # excluded; it is still not read, which is what this control holds.
    content = survey(control).proposal["content"]
    assert content["exclude"] == []
    assert {"glob": "TestCases.md", "why": None} in content["not_material"]
