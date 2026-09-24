"""What is on disk, and what a filename implies.

⛔ `W272`: a nested `.studyforge` or `.git` is what `validate` says it is, asserted
both ways against `validate`'s own walk, on synthetic trees.
"""

from __future__ import annotations

import pytest

from studyforge.skills.reconnaissance import prefix_groups, take
from studyforge.skills.reconnaissance.inventory import observe
from studyforge.skills.reconnaissance.report import Observation, Uncertainty
from studyforge.validate.source import RULE_NESTED_REPOSITORY, source_files
from tests.studyforge.skills.reconnaissance import sources
from tests.support import init_repository


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


# --------------------------------------------------------------------------
# ⛔ `W272`: the survey and `validate` agree on a nested `.studyforge` or `.git`
# --------------------------------------------------------------------------


def write(root, where, text="# Notes\n\nProse.\n"):
    path = root / where
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def validated(root):
    return {path.relative_to(root).as_posix() for path in source_files(root).files}


def surveyed(inventory):
    root = inventory.root
    return {path.relative_to(root).as_posix() for path in inventory.material}


def test_a_NESTED_studyforge_is_read_by_the_survey_as_validate_reads_it(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    write(root, "src/deep/.studyforge/notes.md")
    inventory = take(root)
    assert "src/deep/.studyforge/notes.md" in surveyed(inventory)
    assert "src/deep/.studyforge/notes.md" in validated(root)
    assert root / "src/deep/.studyforge" in inventory.directories


def test_the_ROOT_studyforge_is_skipped_by_both(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    write(root, ".studyforge/notes.md")
    assert ".studyforge/notes.md" not in surveyed(take(root))
    assert ".studyforge/notes.md" not in validated(root)


@pytest.mark.parametrize("store", ["directory", "gitfile"])
def test_a_NESTED_git_is_never_entered_and_is_named_as_the_store_validate_refuses(tmp_path, store):
    root = sources.flat_prose(tmp_path / "c")
    if store == "directory":
        write(root, "vendor/lib/.git/HEAD", "ref: refs/heads/main\n")
        write(root, "vendor/lib/.git/notes.md")
    else:
        write(root, "vendor/lib/.git", "gitdir: ../elsewhere\n")
    inventory = take(root)
    walked = [*inventory.material, *inventory.unrecognised, *inventory.directories]
    assert not [path for path in walked if ".git" in path.relative_to(root).parts]
    assert inventory.stores == list(source_files(root).stores) == [root / "vendor/lib/.git"]
    [question] = [q for q in questions(observe(inventory)) if "repository store" in q.question]
    assert RULE_NESTED_REPOSITORY in question.why and "vendor/lib/.git" in question.why


def test_a_store_the_repository_DECLARES_output_is_named_by_neither(tmp_path):
    root = sources.flat_prose(tmp_path / "c")
    init_repository(root)
    write(root, ".gitignore", "vendor/\n")
    write(root, "vendor/lib/.git/HEAD", "ref: refs/heads/main\n")
    inventory = take(root)
    assert inventory.stores == list(source_files(root).stores) == []
    assert not [q for q in questions(observe(inventory)) if "repository store" in q.question]


def test_control_a_tree_with_no_store_prints_zero_and_asks_nothing(tmp_path):
    inventory = take(sources.flat_prose(tmp_path / "c"))
    items = list(observe(inventory))
    label = "nested repository stores validate refuses"
    [count] = [i for i in items if getattr(i, "what", "") == label]
    assert count.measured == "0"
    assert not [q for q in questions(items) if "repository store" in q.question]


def test_every_OTHER_dot_directory_is_still_skipped_at_any_depth_unchanged(tmp_path):
    # ⚠️ Outside the row: stated, and asserted so a change to it is never silent.
    root = sources.flat_prose(tmp_path / "c")
    write(root, ".github/about.md")
    write(root, "src/.idea/about.md")
    write(root, "src/node_modules/about.md")
    material = surveyed(take(root))
    assert not {".github/about.md", "src/.idea/about.md", "src/node_modules/about.md"} & material


# --------------------------------------------------------------------------
# ⛔ W329: what this framework wrote is set aside, not classified
# --------------------------------------------------------------------------

#: Onboarding's own footprint, in the two shapes the walk would otherwise
#: classify: a document it reads as material, and code it reads as unrecognised.
FOOTPRINT = {"ONBOARDING.md": "# Generated\n", "ingest/read.py": "def read(): pass\n"}


def seen(inventory):
    """Every path the walk classified, either way, relative and posix-spelled."""
    return {
        path.relative_to(inventory.root).as_posix()
        for path in (*inventory.material, *inventory.unrecognised)
    }


def test_a_file_the_install_record_names_is_neither_material_nor_unrecognised(tmp_path):
    root = sources.onboarded(sources.flat_prose(tmp_path / "c"), FOOTPRINT)

    inventory = take(root)

    assert seen(inventory).isdisjoint(FOOTPRINT)
    assert inventory.generated == frozenset(FOOTPRINT)


def test_the_same_files_unrecorded_ARE_classified_so_the_clause_above_measures_something(tmp_path):
    # ⭐ The control. Without a record the identical tree is read as it always
    # was, which is what a corpus nobody onboarded must keep getting.
    root = sources.write(sources.flat_prose(tmp_path / "c"), FOOTPRINT)

    inventory = take(root)

    assert set(FOOTPRINT) <= seen(inventory)
    assert inventory.generated == frozenset()


def test_a_directory_holding_only_generated_files_is_not_reported_as_holding_material(tmp_path):
    root = sources.onboarded(sources.flat_prose(tmp_path / "c"), FOOTPRINT)

    held = {path.relative_to(root).as_posix() for path in take(root).directories}

    assert "ingest" not in held
    assert "src" in held, "the corpus's own directory was dropped with the framework's"


def test_a_directory_the_framework_shares_with_the_corpus_is_still_reported(tmp_path):
    # ⭐ The control: only a directory this framework wholly occupies is dropped.
    root = sources.onboarded(sources.flat_prose(tmp_path / "c"), FOOTPRINT)
    sources.write(root, {"ingest/mine.md": "# a person's note beside the adapter\n"})

    held = {path.relative_to(root).as_posix() for path in take(root).directories}

    assert "ingest" in held


def test_the_survey_says_how_many_files_it_set_aside(tmp_path):
    # ⛔ Said out loud: a reader comparing two surveys of one corpus needs to
    # know which of them was reading this framework's own output.
    root = sources.onboarded(sources.flat_prose(tmp_path / "c"), FOOTPRINT)

    counted = [i for i in observe(take(root)) if isinstance(i, Observation)]
    counted = [i for i in counted if "set aside" in i.what]

    assert [i.measured for i in counted] == [str(len(FOOTPRINT))]
