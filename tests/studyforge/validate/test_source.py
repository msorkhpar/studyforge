"""The two checks that read the material, not only what the adapter wrote.

⭐ **This is the module SF-25 exists for.** Every other check compares the
archive against itself; a digest taken over the blocks and compared against the
blocks answers *"was this corrupted after we wrote it?"* and can never answer
*"did the adapter read everything?"*.

⚠️ The heading count on one side of this comparison comes from a regex in
`validate.source` and on the other from the adapter's parser. ⛔ If it ever
comes from the same reader twice, the check is dead and the suite will not say
so — which is why `test_the_count_does_not_come_from_the_markdown_reader`
exists.
"""

import ast

from studyforge.validate import validate
from studyforge.validate.source import SKIP_DIRS, count_headings, source_files
from tests.studyforge.validate import corpora
from tests.support import repository_root

# --------------------------------------------------------------------------
# counting a structural feature the parser did not produce
# --------------------------------------------------------------------------


def test_atx_headings_are_counted():
    assert count_headings("# One\n\ntext\n\n## Two\n### Three\n") == 3


def test_a_hash_inside_a_fence_is_a_comment_and_not_a_heading():
    # ⚠️ **Fence awareness is not decoration.** A `#` at the start of a line
    # inside a fence is a comment in Python, Ruby, shell and YAML; counting
    # those would make this check fire on correct output, and a check that
    # fires on correct output is a check somebody turns off.
    assert count_headings("# One\n\n```python\n# not a heading\n# nor this\n```\n") == 1


def test_a_tilde_fence_closes_only_on_a_tilde_fence():
    assert count_headings("~~~\n# no\n```\n# still no\n~~~\n# yes\n") == 1


def test_an_unclosed_fence_swallows_the_rest_of_the_file():
    # ⚠️ Recorded rather than "fixed": an unclosed fence is a malformed source
    # and guessing where it ends would invent a count. Undercounting produces
    # a *finding*, which is the safe direction — the check errs towards saying
    # "look at this file".
    assert count_headings("# One\n\n```\n# two\n# three\n") == 1


def test_up_to_three_spaces_of_indent_is_still_a_heading():
    assert count_headings("   # yes\n    # no, that is code\n") == 1


def test_a_hash_that_starts_no_heading_is_not_counted():
    assert count_headings("#no-space\n#\n# yes\n") == 2


def test_seven_hashes_is_not_a_heading():
    assert count_headings("####### no\n###### yes\n") == 1


def test_the_count_does_not_come_from_the_markdown_reader():
    # ⛔ **The assertion the whole task rests on.** Two readings from the same
    # parser are not two readings, and the only way to keep that true is to
    # forbid the import outright — a later hand could otherwise "simplify" this
    # module by reusing the reader and the suite would stay green.
    source = (repository_root() / "src/studyforge/validate/source.py").read_text("utf-8")
    imported = {
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module and "markdown" in node.module
    }
    assert imported == set(), f"the completeness check imports the reader: {imported}"


# --------------------------------------------------------------------------
# the check, end to end
# --------------------------------------------------------------------------


def test_a_source_and_an_archive_that_agree_are_clean(tmp_path):
    report = validate(corpora.one_unit(tmp_path / "c", source=corpora.SOURCE))
    assert report.findings == ()
    assert "short-read" not in {u.rule for u in report.unchecked}


def test_a_heading_in_the_source_and_not_in_the_archive_is_a_short_read(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE + "\n### Three\n\nSkipped.\n")
    report = validate(root)
    assert report.rules == ("short-read",)
    assert "the digest cannot see this" in report.findings[0].message.lower()


def test_the_message_names_both_counts(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE + "\n### Three\n")
    message = validate(root).findings[0].message
    assert "3 heading line(s)" in message
    assert "2 heading block(s)" in message


# --------------------------------------------------------------------------
# ⛔ where the source is, and what happens when it is not there
# --------------------------------------------------------------------------


def test_an_absent_source_tree_is_unchecked_rather_than_failed(tmp_path):
    # ⭐ An archive is a shippable artifact on its own, and `validate` is the
    # adapter's definition of done for *the archive* (R2). What it may not do
    # is pretend it checked.
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert report.findings == ()
    assert "short-read" in {u.rule for u in report.unchecked}


def test_a_half_present_source_tree_is_a_failure_and_not_a_discount(tmp_path):
    # ⛔ **All or nothing.** A per-file skip would excuse precisely the file
    # that went missing, which is where a short read hides.
    root = corpora.write(
        tmp_path / "c",
        containers={
            "demo": corpora.container(
                [
                    corpora.unit_entry(1, origin="src/one.md"),
                    corpora.unit_entry(2, origin="src/two.md"),
                ]
            )
        },
        documents={
            f"demo/raw/prose/unit-0{n}/lesson-1.json": {
                "source": "demo",
                "address": ["demo"],
                "variant": "prose",
                "unit": n,
                "kind": "lesson",
                "ordinal": 1,
                "ingested": "2026-01-05",
                "title": f"Unit {n}",
                "blocks": corpora.BLOCKS,
            }
            for n in (1, 2)
        },
        sources={"src/one.md": corpora.SOURCE},
    )
    assert "origin-missing" in validate(root).rules


# --------------------------------------------------------------------------
# the classification check
# --------------------------------------------------------------------------


def test_a_file_the_manifest_classifies_as_neither_is_refused(tmp_path):
    # ⛔ **Silence is the double ingest.** One corpus ships per-unit files
    # beside whole-series aggregates that are digest-identical concatenations
    # of them, so a glob sweeping both reads every unit twice and nothing
    # complains.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / "strays.txt").write_text("unaccounted for\n", encoding="utf-8")
    report = validate(root)
    assert "unclassified" in report.rules
    assert "src/strays.txt" in report.findings[0].where


def test_a_corpus_with_no_material_beside_the_archive_says_so(tmp_path):
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert "unclassified" in {u.rule for u in report.unchecked}


def test_the_archive_is_never_swept_as_source_material(tmp_path):
    # ⚠️ The archive is generated output living inside the corpus root;
    # sweeping it would classify the adapter's own writing as unclassified.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    found = {path.relative_to(root).as_posix() for path in source_files(root)}
    assert found == {"src/one.md"}


def test_the_manifest_itself_is_not_material(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    assert "corpus.json" not in {p.name for p in source_files(root)}


def test_the_generated_root_and_the_vcs_directory_are_skipped():
    assert ".git" in SKIP_DIRS
    assert ".studyforge" in SKIP_DIRS
