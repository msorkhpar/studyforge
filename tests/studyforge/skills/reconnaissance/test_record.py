"""The document that records the curriculum (SK-01).

⭐ Every shape here reproduces a trap measured in a real repository. The
countermeasure this module implements is *"find the document that records the
grouping"*, never *"learn to read prefixes"* — reading names is derivation and
reading the document is a record (§6).
"""

from __future__ import annotations

import json

import pytest

from studyforge.corpus.manifest import Classification, parse
from studyforge.skills.reconnaissance import find, survey, take
from studyforge.skills.reconnaissance.record import observe
from studyforge.skills.reconnaissance.report import Uncertainty
from tests.studyforge.skills.reconnaissance import sources


def read(root):
    inventory = take(root)
    return find(inventory), inventory


def questions(record, inventory):
    return [i for i in observe(record, inventory) if isinstance(i, Uncertainty)]


# --------------------------------------------------------------------------
# ⭐ the record is found, and it is found by what it links to
# --------------------------------------------------------------------------


def test_the_curriculum_document_is_found_by_what_it_links_to(tmp_path):
    # ⛔ Never by its name. `SUMMARY.md`, `index.md` and `curriculum.md` are all
    # real conventions; keying on a filename list is an open set in disguise.
    record, _ = read(sources.flat_prose(tmp_path / "c"))
    assert record.path.as_posix() == "README.md"
    assert len(record.entries) == 19


def test_a_record_named_anything_at_all_is_still_found(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    (root / "README.md").rename(root / "SUMMARY.md")
    record, _ = read(root)
    assert record.path.as_posix() == "SUMMARY.md"


def test_the_order_is_the_order_the_document_states(tmp_path):
    # ⛔ **Never a filename sort.** Measured: `sorted()` places 37 of 38 units
    # at the wrong index in one real corpus, every page renders, and unit 1 of
    # each group stays first so the spot-check passes.
    record, _ = read(sources.flat_prose(tmp_path / "c"))
    assert record.order == [f"src/{n:02d}.md" for n in range(1, 20)]


def test_a_corpus_with_no_record_is_a_question_not_a_sorted_guess(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    (root / "README.md").unlink()
    record, inventory = read(root)
    assert record is None
    asked = questions(record, inventory)
    assert any("reading order" in q.question for q in asked)
    assert any("37 of 38" in q.settles_it for q in asked)


# --------------------------------------------------------------------------
# ⛔ role is positional, not syntactic — both directions
# --------------------------------------------------------------------------


def test_groups_recorded_as_headings_are_read(tmp_path):
    # ISO's shape.
    record, _ = read(sources.prefixed_groups(tmp_path / "c"))
    assert record.groups == ["Fundamentals", "Server", "Client"]


def test_groups_recorded_as_bare_numbered_lines_are_read_too(tmp_path):
    # ⭐ Java's shape: **zero headings** in the curriculum region. A
    # heading-keyed parser proposes no sections for a two-section corpus.
    record, _ = read(sources.nested_sections(tmp_path / "c"))
    assert record.groups == ["Foundations", "Design"]


def test_a_heading_with_no_units_beneath_it_is_not_a_container(tmp_path):
    # ⛔ **The 21-containers-for-3 trap.** ISO's README carries 21 top-level
    # headings: three are containers, one links other material, and seventeen
    # are chapters of an entirely different document. Every one of them is a
    # well-formed container heading to a parser.
    root = sources.prefixed_groups(tmp_path / "c")
    readme = root / "README.md"
    spurious = "\n".join(f"\n# Unrelated chapter {n}\n\nText.\n" for n in range(1, 18))
    readme.write_text(readme.read_text(encoding="utf-8") + spurious, encoding="utf-8")
    record, _ = read(root)
    assert record.groups == ["Fundamentals", "Server", "Client"]


def test_every_unit_is_placed_under_the_group_that_opens_it(tmp_path):
    record, _ = read(sources.prefixed_groups(tmp_path / "c"))
    counted: dict[str, int] = {}
    for entry in record.entries:
        counted[entry.group] = counted.get(entry.group, 0) + 1
    assert counted == {"Fundamentals": 4, "Server": 3, "Client": 3}


# --------------------------------------------------------------------------
# ⚠️ the drift a hand-maintained record accumulates
# --------------------------------------------------------------------------


def test_an_ordinal_is_read_from_either_place_it_is_written(tmp_path):
    # ⚠️ Measured: 205 entries write it inside the link text and **6** write it
    # outside. A reader for the majority form drops six and raises nothing.
    root = sources.flat_prose(tmp_path / "c")
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            "- [1. Lesson 1](src/01.md)", "- 1. [Lesson 1](src/01.md)"
        ),
        encoding="utf-8",
    )
    record, _ = read(root)
    assert len(record.entries) == 19
    assert record.entries[0].ordinal == "1"


def test_entries_written_in_two_shapes_are_reported_as_drift(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            "- [5. Lesson 5](src/05.md)", "## [5. Lesson 5](src/05.md)"
        ),
        encoding="utf-8",
    )
    record, inventory = read(root)
    assert len(record.entries) == 19
    assert any("minority-shaped" in q.question for q in questions(record, inventory))


def test_material_the_record_does_not_name_is_a_question(tmp_path):
    # ⚠️ A whole-series aggregate looks exactly like this and must be excluded;
    # so does a chapter somebody forgot to link, and that must not be.
    record, inventory = read(sources.unlisted(tmp_path / "c"))
    asked = questions(record, inventory)
    assert any("part of the corpus" in q.question for q in asked)
    assert any("src/3.md" in q.why for q in asked)


def test_a_link_inside_a_fence_is_not_an_entry(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\n```\n- [99. Nope](src/01.md)\n```\n",
        encoding="utf-8",
    )
    record, _ = read(root)
    assert len(record.entries) == 19


# --------------------------------------------------------------------------
# ⛔ an ordinal is read from all three places it is written
# --------------------------------------------------------------------------


def test_the_ordinal_that_IS_the_list_marker_is_still_an_ordinal(tmp_path):
    # ⛔ **The form every top-level entry of all three measured corpora uses**,
    # and the one a reader that strips list markers first silently eats.
    record, _ = read(sources.marker_ordinals(tmp_path / "c"))
    assert [entry.ordinal for entry in record.entries] == ["1", "2", "3"]


def test_an_ordinal_after_a_bullet_is_read_too(tmp_path):
    # ⚠️ `- 1.5. [Title](x)` — measured, 6 of 211 entries in one real corpus.
    root = sources.marker_ordinals(tmp_path / "c")
    (root / "README.md").write_text("# X\n\n- 1.5. [Chapter 1](src/1.md)\n", encoding="utf-8")
    record, _ = read(root)
    assert record.entries[0].ordinal == "1.5"


def test_an_ordinal_inside_the_link_text_is_read_too(tmp_path):
    record, _ = read(sources.flat_prose(tmp_path / "c"))
    assert [entry.ordinal for entry in record.entries][:3] == ["1", "2", "3"]


# --------------------------------------------------------------------------
# ⚠️ emphasis is presentation, not name
# --------------------------------------------------------------------------


def test_emphasis_wrapped_round_a_whole_title_is_not_part_of_the_title(tmp_path):
    # ⚠️ Measured: 22 of one corpus's 38 recorded titles are written `**Like
    # This**`, and a manifest that kept the marks shows them to a reader.
    record, _ = read(sources.marker_ordinals(tmp_path / "c"))
    assert [entry.title for entry in record.entries] == ["Chapter 1", "Chapter 2", "Chapter 3"]


def test_emphasis_inside_a_title_is_left_alone(tmp_path):
    # ⛔ Removing it would be editing the author's text rather than reading it.
    root = sources.marker_ordinals(tmp_path / "c")
    (root / "README.md").write_text("# X\n\n1. [**Basic** setup](src/1.md)\n", encoding="utf-8")
    record, _ = read(root)
    assert record.entries[0].title == "**Basic** setup"


# --------------------------------------------------------------------------
# ⛔ a heading-form entry yields the ordinal its bullet-form twin yields (W252)
# --------------------------------------------------------------------------


def entries_of(root):
    record, _ = read(root)
    return [(e.target, e.title, e.ordinal, e.group, e.section) for e in record.entries]


def test_a_heading_form_entry_yields_the_ordinal_its_bullet_form_twin_yields(tmp_path):
    # ⚠️ W250/2, measured: a corpus's two heading-form entries read no ordinal.
    headed = entries_of(sources.heading_entries(tmp_path / "h"))
    assert headed == entries_of(sources.heading_entries(tmp_path / "b", heading=False))
    assert [(entry[0], entry[2]) for entry in headed][2:4] == [("src/3.md", "3"), ("src/4.md", "4")]
    assert [entry[3] for entry in headed] == ["A Numbered Course"] * 4 + ["Server"] * 2


#: `(entry text, the ordinal it yields)`, written after a bullet and after hashes.
TWINS = [
    ("15. [T](src/1.md)", "15"),
    ("1.5. [T](src/1.md)", "1.5"),
    ("15 [T](src/1.md)", "15"),
    ("15. [**T**](src/1.md) ##", "15"),
    ("[15. T](src/1.md)", "15"),
    ("[T](src/1.md)", None),
    ("2024 notes on [T](src/1.md)", None),
]


@pytest.mark.parametrize("hashes", ["#", "###", "######"])
@pytest.mark.parametrize(("text", "ordinal"), TWINS)
def test_a_heading_yields_what_a_bullet_yields_and_nothing_more(tmp_path, hashes, text, ordinal):
    # ⛔ Both ways: an ordinal where the bullet has one, and none where it has none.
    root = sources.marker_ordinals(tmp_path / "c")
    yielded = []
    for marker in ("-", hashes):
        (root / "README.md").write_text(f"Words.\n\n{marker} {text}\n", encoding="utf-8")
        record, _ = read(root)
        yielded.append((record.entries[0].ordinal, record.entries[0].title))
    assert yielded == [(ordinal, "T"), (ordinal, "T")]


def test_a_numbered_heading_that_links_a_file_of_regions_is_still_a_container(tmp_path):
    # ⛔ W250's reading holds when the label carries an ordinal: its units are
    # still the regions, and each keeps its own ordinal, never the label's.
    root = sources.linked_regions(tmp_path / "c")
    readme = root / "README.md"
    text = readme.read_text(encoding="utf-8")
    assert text.count("# [Test cases]") == 1
    readme.write_text(text.replace("# [Test cases]", "# 4. [Test cases]"), encoding="utf-8")
    record, _ = read(root)
    assert record.groups == ["Fundamentals", "Server", "Test cases"]
    assert [found.path for found in record.containers] == ["TestCases.md"]
    assert [(e.ordinal, e.section) for e in record.entries if e.target == "TestCases.md"] == [
        ("1", "1. Card issuance"),
        ("2", "2. Accounts"),
        ("3", "3. Payments"),
    ]


def test_sf02_accepts_the_draft_of_a_record_with_heading_form_entries(tmp_path):
    headed = survey(sources.heading_entries(tmp_path / "h")).proposal
    assert headed == survey(sources.heading_entries(tmp_path / "b", heading=False)).proposal
    content = parse(json.dumps(sources.settled(headed))).content
    assert content.classify("src/3.md") is Classification.INCLUDED
    assert content.classify("README.md") is not Classification.INCLUDED
