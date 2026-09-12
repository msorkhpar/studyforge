"""What is on disk, and what a filename implies (SK-01)."""

from __future__ import annotations

from studyforge.skills.reconnaissance import prefix_groups, take
from studyforge.skills.reconnaissance.inventory import observe
from studyforge.skills.reconnaissance.report import Uncertainty
from tests.studyforge.skills.reconnaissance import sources


def questions(items):
    return [i for i in items if isinstance(i, Uncertainty)]


def test_a_flat_prose_corpus_is_counted(tmp_path):
    inventory = take(sources.flat_prose(tmp_path / "c"))
    assert len(inventory.material) == 20  # 19 lessons and the README
    assert inventory.flat


def test_generated_and_tooling_directories_are_not_material(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    (root / "build").mkdir()
    (root / "build" / "output.md").write_text("# x", encoding="utf-8")
    (root / ".studyforge").mkdir()
    (root / ".studyforge" / "notes.md").write_text("# x", encoding="utf-8")
    assert all("build" not in p.as_posix() for p in take(root).material)
    assert all(".studyforge" not in p.as_posix() for p in take(root).material)


def test_prefixes_partition_a_flat_directory(tmp_path):
    groups = prefix_groups(["1.md", "2.md", "s1.md", "s2.md", "c1.md"])
    assert set(groups) == {"", "s", "c"}
    assert len(groups[""]) == 2


def test_a_name_with_no_leading_ordinal_is_kept_apart_rather_than_guessed(tmp_path):
    # ⛔ It is not forced into a group. A file nobody can place is a question.
    assert prefix_groups(["intro.md", "1.md"])["?"] == ["intro.md"]


def test_the_prefix_grouping_is_reported_as_a_question_not_an_answer(tmp_path):
    # ⭐ **The correction the ISO integration paid for.** Reading names is
    # derivation; the grouping is almost always also written down, and reading
    # that document is a record (§6).
    inventory = take(sources.prefixed_groups(tmp_path / "c"))
    asked = questions(observe(inventory))
    assert any("prefixes imply" in q.question for q in asked)
    assert any("records the grouping" in q.settles_it for q in asked)


def test_a_file_of_an_unrecognised_kind_is_asked_about_never_swept_in(tmp_path):
    # ⛔ Enumerate the legal: an unforeseen suffix is refused to the reader and
    # raised with a person, rather than admitted because no rule excluded it.
    root = sources.flat_prose(tmp_path / "c")
    (root / "src" / "notes.org").write_text("* org mode", encoding="utf-8")
    inventory = take(root)
    assert any(p.name == "notes.org" for p in inventory.unrecognised)
    assert any("material?" in q.question for q in questions(observe(inventory)))
