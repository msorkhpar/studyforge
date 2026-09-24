"""Mirror of `src/studyforge/skills/adapter/curriculum.py` (R12) — `W340` clause 4.

⭐ **Both ways.** A corpus whose names carry a prefix shape the first corpus never
used is filed correctly from its manifest alone, and a manifest whose declaration
disagrees with the tree refuses — once per way it can disagree.

⛔ Synthetic on purpose: a fixture that needs a sibling checkout skips, and a
skipped check is not evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from studyforge.address import Address
from studyforge.corpus.manifest import parse
from studyforge.skills.adapter.curriculum import CurriculumDisagrees, counted, filed
from tests.support import init_repository

#: The second corpus's groups: `label`, `address`, `prefix`, and its units' titles.
#: ⭐ Word prefixes with separators, in a subdirectory, recorded in `SUMMARY.md`
#: under `##` labels — none of which the first corpus's shape has.
GROUPS = (
    ("The Basics", "basics", "basics-", ("Hello", "Values", "Names")),
    ("Going Deeper", "deeper", "deep_", ("Types", "Errors")),
)


def manifest(groups=GROUPS, *, record: str = "SUMMARY.md", **curriculum) -> dict:
    """The second corpus's `corpus.json`, declaring its shape and nothing else of note."""
    declared = [
        {"label": label, "address": address} | ({"prefix": prefix} if prefix is not None else {})
        for label, address, prefix, _ in groups
    ]
    return {
        "corpus_api": 7,
        "source": "second-corpus",
        "title": "A Second Corpus",
        "levels": ["part"],
        "variants": ["prose"],
        "curriculum": {"record": record, "containers": declared, **curriculum},
        "exercises": False,
        "placement": "tree",
        "content": {"include": ["lessons/*.md"]},
    }


def corpus(root: Path, groups=GROUPS, *, listing=None, extra=(), document=None) -> Path:
    """Write the material, its record and its manifest; return the root."""
    lines = ["# A Second Corpus", "", "Words about the course.", ""]
    for label, _, prefix, titles in groups:
        lines += [f"## {label}", ""]
        for n, title in enumerate(titles, start=1):
            where = f"lessons/{prefix or ''}{n}.md"
            (root / where).parent.mkdir(parents=True, exist_ok=True)
            (root / where).write_text(f"# {title}\n\nProse.\n", encoding="utf-8")
            lines.append(f"{n}. [{title}]({where})")
        lines.append("")
    for where in extra:
        (root / where).write_text("# Extra\n\nProse.\n", encoding="utf-8")
    (root / "SUMMARY.md").write_text(listing or "\n".join(lines), encoding="utf-8")
    text = json.dumps(document or manifest(groups), indent=2)
    (root / "corpus.json").write_text(text, encoding="utf-8")
    return root


def loaded(root: Path):
    return parse((root / "corpus.json").read_text(encoding="utf-8"))


def refusal(root: Path) -> str:
    with pytest.raises(CurriculumDisagrees) as raised:
        filed(root, loaded(root))
    return str(raised.value)


# --- filed from the manifest alone -------------------------------------------


def test_a_second_corpus_with_another_prefix_shape_is_filed_from_its_manifest_alone(tmp_path):
    root = corpus(tmp_path)

    found = filed(root, loaded(root))

    assert [(group.address, group.label) for group in found] == [
        (Address.of("basics"), "The Basics"),
        (Address.of("deeper"), "Going Deeper"),
    ]
    assert [[(u.n, u.title, u.origin) for u in group.units] for group in found] == [
        [
            (1, "Hello", "lessons/basics-1.md"),
            (2, "Values", "lessons/basics-2.md"),
            (3, "Names", "lessons/basics-3.md"),
        ],
        [(1, "Types", "lessons/deep_1.md"), (2, "Errors", "lessons/deep_2.md")],
    ]


def test_the_names_on_disk_give_the_second_count(tmp_path):
    root = corpus(tmp_path)
    assert counted(root, loaded(root)) == {"basics": 3, "deeper": 2}


def test_a_group_with_no_prefix_is_filed_and_leaves_the_count_unmade(tmp_path):
    groups = (GROUPS[0], ("Going Deeper", "deeper", None, ("Types",)))
    root = corpus(tmp_path, groups)

    assert [len(group.units) for group in filed(root, loaded(root))] == [3, 1]
    assert counted(root, loaded(root)) is None


def test_the_record_files_the_units_and_no_prefix_is_needed(tmp_path):
    groups = tuple((label, address, None, titles) for label, address, _, titles in GROUPS)
    root = corpus(tmp_path, groups)
    assert [len(group.units) for group in filed(root, loaded(root))] == [3, 2]


# --- a declaration the tree disagrees with REFUSES ---------------------------


def test_a_file_named_for_a_group_the_record_never_lists_is_refused(tmp_path):
    # ⭐ The chapter somebody forgot to list: the record alone reads clean.
    root = corpus(tmp_path, extra=["lessons/deep_3.md"])
    assert "lessons/deep_3.md is named for deeper and not filed there" in refusal(root)


def test_a_unit_filed_under_another_group_s_prefix_is_refused_by_name(tmp_path):
    root = corpus(tmp_path)
    text = (root / "SUMMARY.md").read_text(encoding="utf-8")
    # ⭐ The record moves `basics-3.md` under the second label; the names do not agree.
    moved = text.replace("3. [Names](lessons/basics-3.md)\n", "").replace(
        "2. [Errors](lessons/deep_2.md)",
        "2. [Errors](lessons/deep_2.md)\n3. [Names](lessons/basics-3.md)",
    )
    (root / "SUMMARY.md").write_text(moved, encoding="utf-8")
    message = refusal(root)
    assert "lessons/basics-3.md is filed at deeper" in message
    assert "lessons/basics-3.md is named for basics and not filed there" in message


def test_every_disagreement_is_named_in_one_refusal(tmp_path):
    root = corpus(tmp_path, extra=["lessons/deep_3.md", "lessons/basics-4.md"])
    message = refusal(root)
    assert "2 file(s) disagree" in message


def test_a_declared_record_that_is_not_there_is_refused(tmp_path):
    root = corpus(tmp_path, document=manifest(record="CONTENTS.md"))
    assert "CONTENTS.md, and it is not there" in refusal(root)


def test_labels_that_are_not_the_record_s_own_are_refused(tmp_path):
    renamed = (("Basics", "basics", "basics-", ()), GROUPS[1])
    root = corpus(tmp_path, document=manifest(renamed))
    assert "the labels must be the record's own" in refusal(root)


def test_labels_declared_out_of_the_record_s_order_are_refused(tmp_path):
    root = corpus(tmp_path, document=manifest(tuple(reversed(GROUPS))))
    assert "in its order" in refusal(root)


def test_an_ordinal_that_is_not_the_position_is_refused(tmp_path):
    root = corpus(tmp_path)
    text = (root / "SUMMARY.md").read_text(encoding="utf-8")
    (root / "SUMMARY.md").write_text(text.replace("2. [Values]", "5. [Values]"), encoding="utf-8")
    assert "numbers entry 2 of basics as 5" in refusal(root)


def test_a_record_that_lists_no_included_file_is_refused(tmp_path):
    root = corpus(tmp_path, listing="# Nothing\n\n- [Elsewhere](elsewhere.md)\n")
    assert "links to none of the files corpus.json includes" in refusal(root)


def test_a_manifest_declaring_no_groups_has_nothing_to_file_from(tmp_path):
    document = manifest()
    document["curriculum"] = {"record": "SUMMARY.md"}
    root = corpus(tmp_path, document=document)
    with pytest.raises(CurriculumDisagrees, match="no curriculum.containers"):
        filed(root, loaded(root))
    with pytest.raises(CurriculumDisagrees, match="no curriculum.containers"):
        counted(root, loaded(root))


def test_the_first_corpus_s_prefix_shape_files_by_the_record_too(tmp_path):
    # ⭐ The empty prefix, `s` and `c`, in one flat directory under `#` labels.
    groups = (
        ("Fundamentals", "fundamentals", "", ("One", "Two")),
        ("Server", "server", "s", ("Setup",)),
        ("Client", "client", "c", ("Setup",)),
    )
    root = corpus(tmp_path, groups)
    found = filed(root, loaded(root))
    assert [[u.origin for u in group.units] for group in found] == [
        ["lessons/1.md", "lessons/2.md"],
        ["lessons/s1.md"],
        ["lessons/c1.md"],
    ]
    assert counted(root, loaded(root)) == {"fundamentals": 2, "server": 1, "client": 1}


def test_a_unit_whose_name_lacks_its_group_s_prefix_is_refused(tmp_path):
    root = corpus(tmp_path, extra=["lessons/intro.md"])
    text = (root / "SUMMARY.md").read_text(encoding="utf-8")
    (root / "SUMMARY.md").write_text(
        text.replace(
            "3. [Names](lessons/basics-3.md)",
            "3. [Names](lessons/basics-3.md)\n4. [Intro](lessons/intro.md)",
        ),
        encoding="utf-8",
    )
    assert "lessons/intro.md is filed at basics, not named 'basics-'" in refusal(root)


def test_a_file_the_repository_ignores_is_not_one_the_filing_counts(tmp_path):
    # ⭐ The population `validate` judges: an ignored file is not material to either.
    root = init_repository(corpus(tmp_path, extra=["lessons/deep_3.md"]))
    (root / ".gitignore").write_text("lessons/deep_3.md\n", encoding="utf-8")
    assert [len(group.units) for group in filed(root, loaded(root))] == [3, 2]
    assert counted(root, loaded(root)) == {"basics": 3, "deeper": 2}
