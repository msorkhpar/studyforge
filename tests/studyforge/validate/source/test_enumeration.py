"""Mirror of `src/studyforge/validate/source/enumeration.py` (R12).

⛔ **What the corpus root holds, asked of the repository and the plan, before any
verdict.** Moved here from `test_classification.py` when the module split:
the tests are unchanged, and the module they name is the one they are about.
"""

import pytest

from studyforge.corpus.placement import ARCHIVE_DIRNAME as ARCHIVE_DIR
from studyforge.validate.source import SKIP_DIRS, enumeration, source_files
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


def test_the_manifest_itself_is_not_material(tmp_path):
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    assert "corpus.json" not in {p.name for p in source_files(root).files}


def test_the_generated_root_and_the_vcs_directory_are_skipped():
    assert ".git" in SKIP_DIRS
    assert ".studyforge" in SKIP_DIRS


# --------------------------------------------------------------------------
# ⛔ What is material is the corpus's declaration, not this file's guess
# --------------------------------------------------------------------------


def test_the_framework_names_only_its_own_two_directories():
    # ⛔ **A list of ecosystem directories would be R1 in miniature**: the
    # framework knowing about ecosystems it was told nothing about, wrong for
    # any corpus that uses another. These two are the framework's own:
    # `.studyforge` is this tool's, `.git` holds the declaration. ⚠️ The archive
    # root is not in the list: it is skipped at the corpus root only.
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
    # ⛔ **The whole point, in one assertion.** A real corpus's walk can be
    # mostly its own declared output, and none of it is unclassified material.
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


def test_git_being_absent_degrades_the_same_way_as_a_missing_repository(tmp_path, monkeypatch):
    # ⚠️ The other half of "could not answer". A machine without git must reach
    # the same announced fallback, never a silent one.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root, "src/")
    assert source_files(root).consulted, "the control: with git installed it answers"
    assert "src/one.md" not in scanned(root)
    monkeypatch.setattr(enumeration.shutil, "which", lambda name: None)
    scan = source_files(root)
    assert not scan.consulted
    assert "src/one.md" in {p.relative_to(root).as_posix() for p in scan.files}


def test_an_unexpected_answer_from_git_is_not_read_as_nothing_is_ignored(tmp_path):
    # ⛔ **128 is "not a repository, or worse", and "or worse" is the point.**
    # Reading any non-verdict return code as an empty ignore set is the
    # fail-open this check exists to refuse.
    # ⭐ Asked with an empty candidate list on purpose: git still discriminates
    # "a repository, nothing ignored" (frozenset()) from "not a repository"
    # (None), so `consulted` is truthful even for a corpus with no files.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    assert enumeration.repository_ignores(root, []) == frozenset()
    outside = tmp_path / "not-a-repository"
    outside.mkdir()
    assert enumeration.repository_ignores(outside, []) is None


def test_a_candidate_outside_the_root_is_refused_naming_neither_path(tmp_path):
    # ⛔ R7, for a public reader: `relative_to`'s own
    # message quotes the root, which is the input that carries a home directory.
    root = corpora.one_unit(tmp_path / "c", source=corpora.SOURCE)
    declared_output(root)
    stray = tmp_path / "elsewhere" / "file.md"
    with pytest.raises(ValueError) as refused:
        enumeration.repository_ignores(root, [stray])
    assert str(tmp_path) not in str(refused.value)
    assert refused.value.__suppress_context__, "the chained message still quotes the root"


# --- restorable: whether git could give back what a removal takes -------------


def _tracked(root):
    init_repository(root)
    (root / "kept").mkdir()
    (root / "kept" / "a.txt").write_text("a\n", encoding="utf-8")
    run([git(), "add", "-A"], cwd=root)
    identity = ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.org"]
    run([git(), *identity, "commit", "-q", "-m", "tracked"], cwd=root)
    return root


def test_restorable_is_true_only_for_tracked_unmodified_files_and_nothing_staged(tmp_path):
    assert enumeration.restorable(_tracked(tmp_path), ["kept"]) is True


def test_restorable_is_unanswered_outside_a_work_tree(tmp_path):
    assert enumeration.restorable(tmp_path, ["kept"]) is None


@pytest.mark.parametrize(
    ("path", "staged"),
    [("kept/a.txt", False), ("kept/new.txt", False), ("elsewhere.txt", True)],
    ids=["modified", "untracked", "staged-elsewhere"],
)
def test_restorable_is_false_for_a_byte_git_could_not_give_back(tmp_path, path, staged):
    root = _tracked(tmp_path)
    (root / path).write_text("changed\n", encoding="utf-8")
    if staged:
        run([git(), "add", path], cwd=root)
    assert enumeration.restorable(root, ["kept"]) is False


def test_restorable_reads_a_path_as_written_never_as_a_glob(tmp_path):
    root = _tracked(tmp_path)
    (root / "kXpt").mkdir()
    (root / "kXpt" / "b.txt").write_text("untracked\n", encoding="utf-8")
    assert enumeration.restorable(root, ["k?pt"]) is True, "a glob matched another folder"
