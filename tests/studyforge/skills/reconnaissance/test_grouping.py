"""Which lines are group labels, and which are units.

⭐ `record` finds *which document* records the curriculum; this decides *what
grouping it expresses*. The tests that drive it end to end live in
`test_record.py`; these are the rule itself, at the smallest size.
"""

from __future__ import annotations

from studyforge.skills.reconnaissance import read
from studyforge.skills.reconnaissance.grouping import (
    UNLABELLED_ALLOWANCE,
    choose,
    grouping,
    label,
    shape,
)
from studyforge.skills.reconnaissance.record import Entry


def entry(line, target="src/x.md"):
    return Entry(target=target, title="T", ordinal=None, line=line, group=None)


def test_a_heading_and_a_bare_numbered_line_are_both_possible_labels():
    # ⛔ Role is positional, not syntactic — both real corpora prove it, in
    # opposite directions.
    assert label("# Fundamentals") == "Fundamentals"
    assert label("1. Java Fundamentals") == "Java Fundamentals"


def test_label_never_reads_a_line_carrying_a_link():
    # ⚠️ Whether a linked HEADING is a label is decided by its position,
    # in `choose` (`test_regions.py`), never by this syntactic reader.
    assert label("- [1. Chapter](src/1.md)") is None
    assert label("# [Test cases](TestCases.md)") is None


def test_a_linked_heading_is_a_label_only_where_it_holds_regions_and_opens_nothing():
    lines = ["# One", "- [a](x)", "# Two", "- [b](x)", "# [Cases](c.md)"]
    cases = Entry(target="c.md", title="Cases", ordinal=None, line=5, group=None)
    entries = [entry(2), entry(4), cases]
    assert grouping(lines, entries, frozenset({"c.md"}))[0] == ["One", "Two", "Cases"]
    assert grouping(lines, entries)[0] == ["One", "Two"]


def test_two_lines_marked_the_same_way_have_the_same_shape():
    assert shape("# A") == shape("# B") == "h1"
    assert shape("## A") != shape("# A")
    assert shape("- a") != shape("    - a")


def test_labels_that_head_no_entries_are_refused():
    # ⛔ **The 21-containers-for-3 trap**, at its smallest. Seventeen of ISO's
    # top-level headings head a chapter of an entirely different document, and
    # every one of them is a well-formed container heading to a parser.
    lines = ["# One", "- [a](x)", "# Two", "- [b](x)", "# Spurious", "# Also spurious"]
    groups, _ = grouping(lines, [entry(2), entry(4)])
    assert groups == ["One", "Two"]


def test_a_grouping_is_refused_outright_when_no_shape_partitions_the_entries():
    # ⚠️ **Nothing is better than a guess here**: a grouping invented at this
    # point becomes a container tree in the built site and the reader would
    # never know it was invented.
    lines = ["- [a](x)", "# Only one label", "- [b](x)"]
    groups, entries = grouping(lines, [entry(1), entry(3)])
    assert groups == []
    assert all(e.group is None for e in entries)


def test_one_stray_entry_above_the_first_label_does_not_cost_the_hierarchy():
    # ⚠️ Measured: the Java corpus links its contributor guide from a
    # blockquote 22 lines above the curriculum. 1 of 212 entries.
    # ⚠️ 1 in 16 here; the real ratio was 1 in 212.
    lines = ["- [stray](x)"] + [
        line
        for n in range(1, 6)
        for line in [f"{n}. Group {n}"] + [f"- [u{n}.{k}](x)" for k in range(1, 4)]
    ]
    entries = [entry(1)] + [
        entry(1 + 4 * (n - 1) + 1 + k) for n in range(1, 6) for k in range(1, 4)
    ]
    groups, _ = grouping(lines, entries)
    assert len(groups) == 5


def test_but_the_allowance_is_small_and_stated():
    # ⛔ It is not a tolerance for being wrong — `survey` names whatever it
    # covered, every time.
    assert 0 < UNLABELLED_ALLOWANCE <= 0.2


def test_a_leading_label_that_opens_almost_nothing_is_dropped_not_kept():
    # ⚠️ Measured: kept, it becomes an eleventh "section" of the Java corpus
    # holding one entry that is not a unit. ⛔ The bullet is a list item, the
    # shape the numbered labels have, or it never competes and nothing is dropped.
    lines = ["- Overview bullet", "- [stray](x)"] + [
        line
        for n in range(1, 6)
        for line in [f"{n}. Group {n}"] + [f"- [u{n}.{k}](x)" for k in range(1, 4)]
    ]
    entries = [entry(2)] + [
        entry(2 + 4 * (n - 1) + 1 + k) for n in range(1, 6) for k in range(1, 4)
    ]
    groups, _ = grouping(lines, entries)
    assert "Overview bullet" not in groups
    assert len(groups) == 5


def test_the_stray_is_dropped_as_one_label_never_as_a_run_of_them():
    # ⚠️ A second single-entry label after the stray is a real group: only one goes.
    lines = ["- Overview bullet", "- [stray](x)", "1. Short", "- [s](x)"] + [
        line
        for n in range(2, 7)
        for line in [f"{n}. Group {n}"] + [f"- [u{n}.{k}](x)" for k in range(1, 4)]
    ]
    entries = [entry(2), entry(4)] + [
        entry(4 + 4 * (n - 2) + 1 + k) for n in range(2, 7) for k in range(1, 4)
    ]
    groups, _ = grouping(lines, entries)
    assert groups == ["Short"] + [f"Group {n}" for n in range(2, 7)]


#: Entries per section of a measured course record: the first three each hold
#: under a tenth of the 155 entries.
SIZES = (9, 13, 14, 33, 14, 29, 16, 7, 14, 3, 3)


def numbered_record(sizes=SIZES):
    """Return `(lines, entries)` for numbered bare-line labels over linked units."""
    lines, entries = ["# Course", "", "## Curriculum", ""], []
    for n, size in enumerate(sizes, start=1):
        lines += [f"{n}. Section {n}", ""]
        for k in range(1, size + 1):
            lines.append(f"- [{n}.{k}. Unit](s{n:02}/u{k:02}.md)")
            entries.append(entry(len(lines), f"s{n:02}/u{k:02}.md"))
        lines.append("")
    return lines, entries


def test_small_leading_sections_are_groups_not_strays():
    # ⛔ Regression: dropping every leading label under the allowance ate the
    # first three sections of a 155-entry course, and ingest then counted 8
    # groups against the 11 its corpus declares.
    lines, entries = numbered_record()
    found, kept = choose(lines, entries)
    assert [text for _, text in found] == [f"Section {n}" for n in range(1, 12)]
    assert len(kept) == sum(SIZES)


def test_every_numbered_section_survives_read(tmp_path):
    lines, entries = numbered_record()
    targets = {entry.target for entry in entries}
    for target in targets:
        (tmp_path / target).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / target).write_text("# Unit\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    record = read(tmp_path / "README.md", tmp_path, targets)
    assert record is not None
    assert list(record.groups) == [f"Section {n}" for n in range(1, 12)]
