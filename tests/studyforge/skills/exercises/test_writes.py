"""Mirror of `src/studyforge/skills/exercises/writes.py` (R12) — the additive commit.

**What it asserts.** R3 whole: a file already there with other bytes refuses
every write, before any; the same bytes are kept; and `replaces` — the one
exception, the ledger's — rewrites a file and never a directory.
"""

from __future__ import annotations

import pytest

from studyforge.skills.exercises import LEDGER_PATH, AuthoringError, commit


def test_a_new_file_is_written_and_the_same_bytes_are_kept(tmp_path):
    written, kept = commit(tmp_path, [("a/one.txt", b"one\n")], "the pass")
    assert (written, kept) == (("a/one.txt",), ())
    assert commit(tmp_path, [("a/one.txt", b"one\n")], "the pass") == ((), ("a/one.txt",))


def test_other_bytes_refuse_every_write_before_any(tmp_path):
    (tmp_path / "old.txt").write_text("the reader's own\n", encoding="utf-8")
    with pytest.raises(AuthoringError, match="non-destructive"):
        commit(tmp_path, [("new.txt", b"new\n"), ("old.txt", b"mine\n")], "the pass")
    assert not (tmp_path / "new.txt").exists(), "a refused pass wrote a file"


def test_the_ledger_named_in_replaces_is_rewritten(tmp_path):
    (tmp_path / LEDGER_PATH).parent.mkdir()
    (tmp_path / LEDGER_PATH).write_bytes(b"{}\n")
    files = [(LEDGER_PATH, b'{"merged": true}\n')]
    with pytest.raises(AuthoringError, match="non-destructive"):
        commit(tmp_path, files, "the pass")
    assert commit(tmp_path, files, "the pass", replaces=(LEDGER_PATH,)) == ((LEDGER_PATH,), ())
    assert (tmp_path / LEDGER_PATH).read_bytes() == b'{"merged": true}\n'
    assert commit(tmp_path, files, "the pass", replaces=(LEDGER_PATH,)) == ((), (LEDGER_PATH,))


def test_a_replaceable_path_holding_a_directory_is_still_refused(tmp_path):
    (tmp_path / LEDGER_PATH).mkdir(parents=True)
    with pytest.raises(AuthoringError, match="non-destructive"):
        commit(tmp_path, [(LEDGER_PATH, b"{}\n")], "the pass", replaces=(LEDGER_PATH,))


#: A bundle's build role, where the exercises skill writes one.
BUILD = "exercises/m/java/unit-01/practice-1/build/pom.xml"


def _repository(root):
    """A git working tree whose root ignore file ignores `build/`, as most JVM repositories do."""
    from tests.studyforge.skills.onboarding.corpora import git

    root.mkdir(parents=True, exist_ok=True)
    (root / ".gitignore").write_text("build/\n", encoding="utf-8")
    git(root, "init", "-q")
    return root


def test_a_file_git_would_leave_out_refuses_the_pass_naming_it_before_any_write(tmp_path):
    root = _repository(tmp_path / "corpus")
    files = [("exercises/m/java/unit-01/practice-1/bundle.json", b"{}\n"), (BUILD, b"<project/>\n")]
    with pytest.raises(AuthoringError, match=r"ignored by the corpus's git, the first '" + BUILD):
        commit(root, files, "the authoring pass")
    assert not (root / "exercises").exists(), "nothing was written"


def test_the_corpus_s_own_negation_lets_the_same_pass_finish(tmp_path):
    root = _repository(tmp_path / "corpus")
    (root / "exercises").mkdir()
    (root / "exercises/.gitignore").write_text("!build/\n", encoding="utf-8")
    written, _ = commit(root, [(BUILD, b"<project/>\n")], "the authoring pass")
    assert written == (BUILD,)
