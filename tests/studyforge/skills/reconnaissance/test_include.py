"""Mirror of `src/studyforge/skills/reconnaissance/include.py` (R12).

⭐ **An include reads units and nothing the record only links**: a module's
contents page beside its lessons is never included, uniform modules share one
`*/` pattern, and an entry above the record's first label is not drafted as
material. ⛔ The `*/` pattern is drafted only where it reads exactly what the
per-directory ones do.
"""

from __future__ import annotations

from studyforge.skills.reconnaissance import find, take
from studyforge.skills.reconnaissance.curriculum import heads_of
from studyforge.skills.reconnaissance.include import patterns
from tests.studyforge.skills.reconnaissance import sources


def drafted(root):
    """The include and exclude a survey of `root` drafts."""
    tree = take(root)
    record = find(tree)
    linked = heads_of(tree, record)
    return patterns(tree, record, [head.target for head in linked.heads] if linked else [])


def test_uniform_modules_share_one_pattern_that_reads_no_contents_page(tmp_path):
    include, exclude = drafted(sources.nested_sections(tmp_path / "c"))

    assert include == ["*/README_*.md"]
    assert exclude == []


def test_a_directory_whose_units_share_no_stem_lists_them(tmp_path):
    root = sources.nested_sections(tmp_path / "c")
    for old, new in (("README_1.1.1", "alpha"), ("README_1.1.2", "beta")):
        (root / f"11-basics/{old}.md").rename(root / f"11-basics/{new}.md")
        record = root / "README.md"
        record.write_text(record.read_text("utf-8").replace(old, new), "utf-8")

    include, _ = drafted(root)
    assert include == ["11-basics/alpha.md", "11-basics/beta.md", "21-objects/README_*.md"]


def test_no_star_pattern_where_it_would_read_another_directory_s_file(tmp_path):
    # ⛔ A third root directory holds a file the wide pattern would read and no
    # unit lists: the per-directory patterns stay, and nothing is widened.
    root = sources.nested_sections(tmp_path / "c")
    sources.write(root, {"notes/README_draft.md": sources.unit("Draft")})

    include, _ = drafted(root)
    assert include == ["11-basics/README_*.md", "21-objects/README_*.md"]


def test_an_entry_above_the_first_label_is_not_drafted_as_material(tmp_path):
    # ⭐ Large enough that one stray link sits inside the grouping's allowance,
    # as a link to a contributor's guide in a real overview does.
    files = {"GUIDE.md": sources.unit("Guide")}
    listing = ["# A Course", "", "> See [the guide](GUIDE.md).", ""]
    for section, module in enumerate(("11-one", "21-two"), start=1):
        listing += [f"{section}. Section {section}", ""]
        listing.append(f"- [{section}.1. {module}]({module}/README.md)")
        files[f"{module}/README.md"] = sources.unit(module)
        for n in range(1, 7):
            files[f"{module}/lesson_{n}.md"] = sources.unit(f"{module} {n}")
            listing.append(f"    - [{n}. Lesson]({module}/lesson_{n}.md)")
    files["README.md"] = "\n".join(listing) + "\n"

    include, exclude = drafted(sources.write(tmp_path / "c", files))
    assert include == ["*/lesson_*.md"]
    assert exclude == []
