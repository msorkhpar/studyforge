"""Mirror of `src/studyforge/skills/reconnaissance/linked.py` (R12).

⭐ **A linked level is read by position**: beneath a label, the shallowest
linked list entries open containers and the entries indented under each are its
units, nested ones included. ⛔ A record with the shape only in part is refused
by line, and a flat record never reads as linked.
"""

from __future__ import annotations

import pytest

from studyforge.skills.reconnaissance import NotLinked, find, split_linked, take
from tests.studyforge.skills.reconnaissance import sources


def linked_of(root):
    """Read the root's record and split its linked level."""
    record = find(take(root))
    lines = (root / record.path).read_text(encoding="utf-8").splitlines()
    return split_linked(lines, record.path.as_posix(), record.entries, record.labels)


def rewritten(root, old: str, new: str):
    """Edit the root's record in place, and return the root."""
    record = root / "README.md"
    record.write_text(record.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    return root


def test_each_linked_entry_opens_a_container_holding_the_entries_beneath_it(tmp_path):
    linked = linked_of(sources.nested_sections(tmp_path / "c"))

    assert [(h.group, h.ordinal, h.title, h.directory) for h in linked.heads] == [
        ("Foundations", "1.1", "Basics", "11-basics"),
        ("Design", "2.1", "Objects", "21-objects"),
    ]
    assert [[e.target for e in linked.units[h.line]] for h in linked.heads] == [
        ["11-basics/README_1.1.1.md", "11-basics/README_1.1.2.md"],
        ["21-objects/README_2.1.1.md", "21-objects/README_2.1.2.md"],
    ]


def test_an_entry_nested_under_a_unit_is_a_unit_of_the_same_container(tmp_path):
    root = sources.nested_sections(tmp_path / "c")
    sources.write(root, {"11-basics/README_1.1.1.1.md": sources.unit("Deeper")})
    rewritten(
        root,
        "(11-basics/README_1.1.1.md)\n",
        "(11-basics/README_1.1.1.md)\n        - [1.1.1.1. Deeper](11-basics/README_1.1.1.1.md)\n",
    )

    first = linked_of(root).heads[0]
    assert [e.ordinal for e in linked_of(root).units[first.line]] == ["1.1.1", "1.1.1.1", "1.1.2"]


def test_an_entry_above_the_first_linked_entry_of_its_group_is_refused(tmp_path):
    root = rewritten(
        sources.nested_sections(tmp_path / "c"),
        "1. Foundations\n\n",
        "1. Foundations\n\n    - [1.0.1. Stray](11-basics/README_1.1.1.md)\n",
    )
    with pytest.raises(NotLinked, match="above any linked entry"):
        linked_of(root)


def test_an_entry_under_a_later_label_is_never_held_by_the_label_before_it(tmp_path):
    # ⛔ The last linked entry above belongs to another group: a unit between a
    # label and that label's first linked entry is held by no container.
    root = rewritten(
        sources.nested_sections(tmp_path / "c"),
        "2. Design\n\n",
        "2. Design\n\n    - [2.0.1. Stray](21-objects/README_2.1.1.md)\n",
    )
    with pytest.raises(NotLinked, match="above any linked entry"):
        linked_of(root)


def test_a_linked_entry_with_no_unit_beneath_it_is_refused(tmp_path):
    root = rewritten(
        sources.nested_sections(tmp_path / "c"),
        "2. Design",
        "- [1.9. Empty](19-empty/README.md)\n\n2. Design",
    )
    sources.write(root, {"19-empty/README.md": sources.unit("Empty")})
    with pytest.raises(NotLinked, match="no unit indented beneath"):
        linked_of(root)


def test_a_flat_record_is_not_linked(tmp_path):
    # ⛔ Every entry at one indent: each would be a head with nothing beneath it.
    with pytest.raises(NotLinked):
        linked_of(sources.prefixed_groups(tmp_path / "c"))


def test_a_linked_page_at_the_root_names_no_directory_and_is_refused(tmp_path):
    root = rewritten(
        sources.nested_sections(tmp_path / "c"), "(11-basics/README.md)", "(basics.md)"
    )
    sources.write(root, {"basics.md": sources.unit("Basics")})
    with pytest.raises(NotLinked, match="at the corpus root"):
        linked_of(root)
