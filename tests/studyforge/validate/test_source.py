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

from studyforge.validate import source as source_module
from studyforge.validate import validate
from studyforge.validate.corpus import ARCHIVE_DIR
from studyforge.validate.source import SKIP_DIRS, count_headings, source_files
from tests.studyforge.validate import corpora
from tests.support import git, init_repository, repository_root, run


def declared_output(root, *lines):
    """Make `root` a repository that declares `lines` as generated output."""
    init_repository(root)
    (root / ".gitignore").write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")


def track(root, where):
    """Put `where` in the repository's index, so git's ignore rules yield to it."""
    result = run([git(), "add", "--force", where], cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr


def scanned(root):
    """The scan's files as posix strings relative to `root`."""
    return {path.relative_to(root).as_posix() for path in source_files(root).files}


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
    assert scanned(root) == {"src/one.md"}


def test_the_manifest_itself_is_not_material(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    assert "corpus.json" not in {p.name for p in source_files(root).files}


def test_the_generated_root_and_the_vcs_directory_are_skipped():
    assert ".git" in SKIP_DIRS
    assert ".studyforge" in SKIP_DIRS


# --------------------------------------------------------------------------
# ⛔ W28 — what is material is the corpus's declaration, not this file's guess
# --------------------------------------------------------------------------


def test_the_framework_names_only_its_own_three_directories():
    # ⛔ **`SKIP_DIRS` was R1 in miniature.** Two of its five names were the
    # framework knowing about two ecosystems it was told nothing about, and a
    # list of other people's build directories is wrong for the first corpus
    # that uses a third. These three are the framework's own: `archive` is
    # R2's, `.studyforge` is this tool's, `.git` holds the declaration.
    assert SKIP_DIRS == (ARCHIVE_DIR, ".git", ".studyforge")
    assert "node_modules" not in SKIP_DIRS
    assert "__pycache__" not in SKIP_DIRS


def test_a_corpus_that_uses_neither_ecosystem_is_unaffected(tmp_path):
    # ⭐ The acceptance's third clause. Dropping two names may not change what
    # a corpus naming neither of them scans — under git and without it.
    plain = corpora.one_unit(tmp_path / "plain", source=corpora.SOURCE)
    assert scanned(plain) == {"src/one.md"}
    versioned = corpora.one_unit(tmp_path / "versioned", source=corpora.SOURCE)
    init_repository(versioned)
    assert scanned(versioned) == {"src/one.md"}


def test_a_file_the_repository_declares_as_output_is_not_material(tmp_path):
    # ⛔ **The whole task, in one assertion.** Measured against a real corpus,
    # 100 of 159 enumerated files were the repository's own declared output and
    # every one was reported as unclassified material.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "generated").mkdir()
    (root / "generated" / "graph.json").write_text("{}\n", encoding="utf-8")
    declared_output(root, "generated/")
    assert scanned(root) == {"src/one.md", ".gitignore"}


def test_the_same_file_is_material_when_the_repository_does_not_declare_it(tmp_path):
    # ⛔ **The negative control for the test above, and it is the whole reason
    # to trust it.** Same tree, same file, one line removed from the
    # declaration: the file must come back. Without this, a `source_files` that
    # dropped everything under a directory called `generated` would pass.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "generated").mkdir()
    (root / "generated" / "graph.json").write_text("{}\n", encoding="utf-8")
    declared_output(root)
    assert "generated/graph.json" in scanned(root)


def test_the_framework_no_longer_guesses_at_another_ecosystems_output(tmp_path):
    # ⛔ **R1, stated as a test.** A corpus that does NOT declare `node_modules`
    # as output gets it scanned, because the framework has no opinion about
    # what an ecosystem calls its build directory. The corpus decides.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    for directory in ("node_modules", "__pycache__"):
        (root / directory).mkdir()
        (root / directory / "thing.txt").write_text("x\n", encoding="utf-8")
    declared_output(root)
    assert {"node_modules/thing.txt", "__pycache__/thing.txt"} <= scanned(root)
    declared_output(root, "node_modules/", "__pycache__/")
    assert not {"node_modules/thing.txt", "__pycache__/thing.txt"} & scanned(root)


def test_a_tracked_file_is_material_even_when_a_pattern_would_ignore_it(tmp_path):
    # ⚠️ git's index wins over its ignore rules, and this test holds that
    # property: a file somebody committed is material even if a later
    # `.gitignore` names it. Adding `--no-index` to the query would reverse it.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / "kept.md").write_text("# Kept\n", encoding="utf-8")
    declared_output(root, "src/kept.md")
    assert "src/kept.md" not in scanned(root), "the control: the pattern does bite"
    track(root, "src/kept.md")
    assert "src/kept.md" in scanned(root)


def test_an_untracked_file_that_is_not_declared_output_is_still_material(tmp_path):
    # ⛔ **Newly written material is material.** This is what forbids reading
    # the declaration as `git ls-files`: a file added and not yet committed is
    # exactly the file an adapter author is about to ingest, and answering
    # "not tracked, therefore not material" would hide it.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    (root / "src" / "brand-new.md").write_text("# New\n", encoding="utf-8")
    assert "src/brand-new.md" in scanned(root)


# --------------------------------------------------------------------------
# ⛔ the degradation, and it may not guess
# --------------------------------------------------------------------------


def test_a_corpus_root_that_is_not_a_repository_says_so_and_still_scans(tmp_path):
    # ⛔ **The walk stands and `validate` SAYS SO.** Refusing a non-repository
    # corpus is wrong (R2: an archive is a shippable artifact on its own), and
    # silently falling back to a scan that over-reports is worse than either,
    # because it looks like a clean run.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / "strays.txt").write_text("unaccounted for\n", encoding="utf-8")
    report = validate(root)
    assert "ignore-declaration" in {u.rule for u in report.unchecked}
    assert not source_files(root).consulted
    assert "src/strays.txt" in {f.where for f in report.findings}


def test_a_repository_is_not_reported_unchecked(tmp_path):
    # ⛔ The negative control for the claim above: an `Unchecked` that is always
    # emitted says nothing. It must be absent exactly when git answered.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    assert source_files(root).consulted
    assert "ignore-declaration" not in {u.rule for u in validate(root).unchecked}


def test_an_unchecked_declaration_does_not_fail_the_run(tmp_path):
    # ⚠️ `Unchecked` is loud and counted, and it is not a `Finding`. A corpus
    # with nothing else wrong and no git is valid, and says what it could not
    # read.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    report = validate(root)
    assert report.findings == ()
    assert report.exit_code == 0
    assert "ignore-declaration" in {u.rule for u in report.unchecked}


def test_git_being_absent_degrades_the_same_way_as_a_missing_repository(tmp_path, monkeypatch):
    # ⚠️ The other half of "could not answer". A machine without git must reach
    # the same announced fallback, never a silent one.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root, "src/")
    assert source_files(root).consulted, "the control: with git installed it answers"
    assert "src/one.md" not in scanned(root)
    monkeypatch.setattr(source_module.shutil, "which", lambda name: None)
    scan = source_files(root)
    assert not scan.consulted
    assert "src/one.md" in {p.relative_to(root).as_posix() for p in scan.files}


def test_an_unexpected_answer_from_git_is_not_read_as_nothing_is_ignored(tmp_path):
    # ⛔ **128 is "not a repository, or worse", and "or worse" is the point.**
    # Reading any non-verdict return code as an empty ignore set is the
    # fail-open this task exists to remove.
    # ⭐ Asked with an empty candidate list on purpose: git still discriminates
    # "a repository, nothing ignored" (frozenset()) from "not a repository"
    # (None), so `consulted` is truthful even for a corpus with no files.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    assert source_module._declared_output(root, []) == frozenset()
    outside = tmp_path / "not-a-repository"
    outside.mkdir()
    assert source_module._declared_output(outside, []) is None


def test_a_corpus_with_no_material_says_so_before_it_says_anything_else(tmp_path):
    # ⚠️ An empty corpus root reports "nothing to classify" and does not also
    # complain that it could not read a declaration it had no use for.
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert "unclassified" in {u.rule for u in report.unchecked}
    assert "ignore-declaration" not in {u.rule for u in report.unchecked}
