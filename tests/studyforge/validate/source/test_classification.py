"""Mirror of `src/studyforge/validate/source/classification.py` (R12).

⛔ **Silence is the double ingest.** Every assertion here is about a file the
manifest did not account for, or accounted for twice, or that the repository
itself calls generated output — and about the one degradation this check is
allowed: saying out loud that it could not read the declaration.

⚠️ The imports come through the package surface, not through the submodule,
except where a test reaches for a private name or monkeypatches one. Those two
name `classification` directly because that is the module they are about.
"""

import json

from studyforge.corpus.placement import ARCHIVE_DIRNAME as ARCHIVE_DIR
from studyforge.validate import validate
from studyforge.validate.source import (
    RULE_CONTESTED,
    RULE_UNCLASSIFIED,
    SKIP_DIRS,
    classification,
    source_files,
)
from tests.studyforge.validate import corpora
from tests.support import git, init_repository, run


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


# --------------------------------------------------------------------------
# ⛔ the third state — never material, rather than withheld
# --------------------------------------------------------------------------

#: A reason long enough to be one, written where a corpus would write it.
WHY = "the repository's own scaffolding, never read aloud"


def redeclare(root, content, corpus_api=2):
    """Rewrite this corpus's `corpus.json` with `content` and a version."""
    declared = {**corpora.MANIFEST, "corpus_api": corpus_api, "content": content}
    (root / "corpus.json").write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    return root


def test_a_file_the_manifest_calls_never_material_is_not_a_finding(tmp_path):
    # ⛔ **The hole this closes.** Measured against a real corpus: 100 of its
    # files were reported unclassified and only 3 were material withheld from
    # anybody — the rest a licence, ignore files, an editor's workspace. There
    # was no honest state for them and `exclude` made every `why` a small lie.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "LICENSE").write_text("A licence.\n", encoding="utf-8")
    redeclare(root, {"include": ["src/*.md"], "not_material": [{"glob": "LICENSE", "why": WHY}]})
    report = validate(root)
    assert report.findings == ()
    assert report.exit_code == 0


def test_the_third_state_does_not_silence_the_unclassified_catch(tmp_path):
    # ⛔ Rule 4 is not weakened by one line: a file the third state does not
    # name is still unaccounted for, and still exits 1.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "LICENSE").write_text("A licence.\n", encoding="utf-8")
    (root / "notes.txt").write_text("unaccounted for\n", encoding="utf-8")
    redeclare(root, {"include": ["src/*.md"], "not_material": [{"glob": "LICENSE", "why": WHY}]})
    report = validate(root)
    assert report.rules == ("unclassified",)
    assert [finding.where for finding in report.findings] == ["notes.txt"]
    assert report.exit_code == 1


def test_a_file_matched_by_include_and_not_material_is_a_finding_of_its_own(tmp_path):
    # ⛔ **Never a precedence, and its own rule id.** This is what stops the
    # third state becoming a drain: a glob that sweeps up material says so
    # loudly, per file, against a real tree.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    redeclare(root, {"include": ["src/*.md"], "not_material": [{"glob": "src/*", "why": WHY}]})
    report = validate(root)
    assert report.rules == ("contested",)
    assert report.findings[0].where == "src/one.md"
    assert report.exit_code == 1


def test_the_contested_finding_is_not_filed_under_the_unclassified_rule(tmp_path):
    # ⚠️ A different fact: the manifest classified this file twice and
    # disagreed with itself, which is not the same as never classifying it —
    # and a script filters on the two separately.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    redeclare(root, {"include": ["src/*.md"], "not_material": [{"glob": "src/*", "why": WHY}]})
    assert "unclassified" not in validate(root).rules
    assert RULE_CONTESTED != RULE_UNCLASSIFIED


def test_a_manifest_using_the_third_state_at_the_older_version_is_refused(tmp_path):
    # ⛔ R9: the version is the corpus's statement of which contract it was
    # written to, and it is refused rather than upgraded on its behalf.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    redeclare(
        root,
        {"include": ["src/*.md"], "not_material": [{"glob": "LICENSE", "why": WHY}]},
        corpus_api=1,
    )
    report = validate(root)
    assert "manifest" in report.rules
    assert "not_material" in report.findings[0].message


def test_a_corpus_with_no_material_beside_the_archive_says_so(tmp_path):
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert "unclassified" in {u.rule for u in report.unchecked}


def test_the_archive_is_never_swept_as_source_material(tmp_path):
    # ⚠️ The archive is generated output living inside the corpus root;
    # sweeping it would classify the adapter's own writing as unclassified.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    assert scanned(root) == {"src/one.md"}


def test_a_sources_own_nested_archive_directory_is_material_and_never_skipped(tmp_path):
    # ⛔ `W241/2`: the scan skipped ANY `archive/`, so a source keeping its own
    # lost it from every reading. Only the root beside `corpus.json` is skipped.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    (root / "src" / ARCHIVE_DIR).mkdir()
    (root / "src" / ARCHIVE_DIR / "old.md").write_text("# Old\n", encoding="utf-8")
    assert scanned(root) == {"src/one.md", f"src/{ARCHIVE_DIR}/old.md"}
    report = validate(root)
    assert f"src/{ARCHIVE_DIR}/old.md" in {
        f.where for f in report.findings if f.rule == "unclassified"
    }


def test_the_manifest_itself_is_not_material(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    assert "corpus.json" not in {p.name for p in source_files(root).files}


def test_the_generated_root_and_the_vcs_directory_are_skipped():
    assert ".git" in SKIP_DIRS
    assert ".studyforge" in SKIP_DIRS


# --------------------------------------------------------------------------
# ⛔ W28 — what is material is the corpus's declaration, not this file's guess
# --------------------------------------------------------------------------


def test_the_framework_names_only_its_own_two_directories():
    # ⛔ **`SKIP_DIRS` was R1 in miniature.** Two of its five names were the
    # framework knowing about two ecosystems it was told nothing about, and a
    # list of other people's build directories is wrong for the first corpus
    # that uses a third. These two are the framework's own: `.studyforge` is
    # this tool's, `.git` holds the declaration. ⚠️ The archive root left the
    # list (`W248`): it is skipped at the corpus root only.
    assert SKIP_DIRS == (".git", ".studyforge")
    assert ARCHIVE_DIR not in SKIP_DIRS
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
    monkeypatch.setattr(classification.shutil, "which", lambda name: None)
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
    assert classification.repository_ignores(root, []) == frozenset()
    outside = tmp_path / "not-a-repository"
    outside.mkdir()
    assert classification.repository_ignores(outside, []) is None


def test_a_corpus_with_no_material_says_so_before_it_says_anything_else(tmp_path):
    # ⚠️ An empty corpus root reports "nothing to classify" and does not also
    # complain that it could not read a declaration it had no use for.
    report = validate(corpora.one_unit(tmp_path / "c"))
    assert "unclassified" in {u.rule for u in report.unchecked}
    assert "ignore-declaration" not in {u.rule for u in report.unchecked}
