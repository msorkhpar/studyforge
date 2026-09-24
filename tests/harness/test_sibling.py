"""Mirror of `tests/harness/sibling.py`: a sibling's file, read at a commit or labelled local.

⛔ **The subject is a distinction, so every case asserts both sides of it.** A
file that is committed must read **at the commit** even when a different one
sits in the working tree; a file that is **only** in the working tree must read
as **local** and say so; and nothing to read at all must be an **answer**
rather than an exception — a clean clone's case, where no sibling is named.

⭐ **Real `git init` repositories, built per test** (`tests/harness/workspaces.py`
gives the reason and the placeholder identity). ⛔ **No real sibling is touched**,
and each case passes its own environment.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from tests.harness import sibling
from tests.harness import workspaces as support
from tests.harness.workspace import WORKSPACE_ENV

#: The sibling this builds, the file it reads out of it, and the two contents
#: that must never be confused for one another.
NAME = "Toolchain"
CONTRACT = "consuming.json"
COMMITTED = '{"provides": 2, "where": "committed"}'
IN_TREE = '{"provides": 99, "where": "the working tree only"}'


def workspace(tmp_path: Path, text: str | None = COMMITTED) -> tuple[Path, Path]:
    """`(workspace root, the sibling's checkout)`, carrying `text` as a committed contract.

    ⭐ `docs/api.md` is committed either way: a committed **directory** is what
    proves the reader refuses a tree rather than handing back a listing.
    """
    root = tmp_path / "w"
    directory = root / NAME
    support.repository(directory, NAME)
    (directory / "docs").mkdir()
    (directory / "docs" / "api.md").write_text("the component's own API\n", encoding="utf-8")
    if text is not None:
        (directory / CONTRACT).write_text(text, encoding="utf-8")
    support.run(directory, "add", "-A")
    support.run(directory, "commit", "-qm", "contract")
    return root, directory


def contract(root: Path, path: str = CONTRACT, name: str = NAME) -> sibling.Reading:
    """Read one file out of the named sibling — what every case below calls."""
    return sibling.read_sibling(name, path, environ=support.environ(root))


# ---------------------------------------------------------------------------
# ⭐ at the commit — the reading another host reproduces
# ---------------------------------------------------------------------------


def test_a_committed_file_is_read_at_the_commit(tmp_path):
    root, directory = workspace(tmp_path)
    reading = contract(root)
    assert reading.committed and not reading.working_tree and not reading.absent
    assert reading.text == COMMITTED
    assert NAME in reading.source and CONTRACT in reading.source
    assert support.run(directory, "rev-parse", "HEAD")[:12] in reading.source


def test_the_working_tree_is_not_read_when_the_commit_carries_the_file(tmp_path):
    # ⛔ `W404` head on: a different contract sits on disk and must not be seen.
    root, directory = workspace(tmp_path)
    (directory / CONTRACT).write_text(IN_TREE, encoding="utf-8")
    reading = contract(root)
    assert reading.committed
    assert reading.text == COMMITTED


def test_a_new_commit_is_what_is_read_once_it_is_checked_out(tmp_path):
    root, directory = workspace(tmp_path)
    (directory / CONTRACT).write_text(IN_TREE, encoding="utf-8")
    support.run(directory, "add", CONTRACT)
    support.run(directory, "commit", "-qm", "moved")
    reading = contract(root)
    assert reading.committed and reading.text == IN_TREE


# ---------------------------------------------------------------------------
# ⛔ the working tree — allowed, labelled, never mistaken for a commit
# ---------------------------------------------------------------------------


def test_a_staged_contract_that_exists_on_no_ref_reads_as_local_and_says_so(tmp_path):
    """⛔ **The measured case.** A checkout mid-merge, and the file is on no ref."""
    root, directory = workspace(tmp_path, text=None)
    (directory / CONTRACT).write_text(IN_TREE, encoding="utf-8")
    support.run(directory, "add", CONTRACT)
    reading = contract(root)
    assert reading.working_tree and not reading.committed and not reading.absent
    assert reading.text == IN_TREE
    assert "WORKING TREE" in reading.source and "LOCAL" in reading.source


def test_a_directory_that_is_no_checkout_is_a_local_reading(tmp_path):
    root = tmp_path / "w"
    (root / NAME).mkdir(parents=True)
    (root / NAME / CONTRACT).write_text(IN_TREE, encoding="utf-8")
    reading = contract(root)
    assert reading.working_tree and not reading.committed
    assert "not a git checkout" in reading.source


# ---------------------------------------------------------------------------
# ⛔ absent — an answer, because a clean clone names no workspace
# ---------------------------------------------------------------------------


def test_no_variable_is_absent_and_names_the_variable(tmp_path):
    workspace(tmp_path)
    reading = sibling.read_sibling(NAME, CONTRACT, environ={})
    assert reading.absent and reading.text is None
    assert WORKSPACE_ENV in reading.source and NAME in reading.source


def test_no_checkout_in_the_named_workspace_is_absent_and_not_a_crash(tmp_path):
    root, directory = workspace(tmp_path)
    shutil.rmtree(directory)
    reading = contract(root)
    assert reading.absent and reading.text is None
    assert NAME in reading.source


def test_no_contract_committed_and_none_on_disk_is_absent(tmp_path):
    root, _ = workspace(tmp_path, text=None)
    reading = contract(root)
    assert reading.absent and reading.text is None
    assert "working tree either" in reading.source


def test_a_path_that_is_a_directory_at_the_commit_is_never_read_as_content(tmp_path):
    # ⛔ `git show <commit>:docs` prints a TREE LISTING and exits 0. A reader
    # built on it hands that listing back as if it were the file.
    root, _ = workspace(tmp_path)
    assert contract(root, "docs").absent
    # ⭐ The file inside it reads fine, so the refusal is about the shape.
    assert contract(root, "docs/api.md").committed


# ---------------------------------------------------------------------------
# ⛔ a directory the caller named — local by construction
# ---------------------------------------------------------------------------


def test_a_directory_the_caller_named_is_local_by_construction(tmp_path):
    (tmp_path / CONTRACT).write_text(IN_TREE, encoding="utf-8")
    reading = sibling.read_directory(tmp_path, CONTRACT)
    assert reading.working_tree and not reading.committed
    assert reading.text == IN_TREE
    assert "no commit covers" in reading.source


def test_a_directory_the_caller_named_with_nothing_in_it_is_absent(tmp_path):
    reading = sibling.read_directory(tmp_path, CONTRACT)
    assert reading.absent and reading.text is None
    assert CONTRACT in reading.source


# ---------------------------------------------------------------------------
# ⛔ the properties every reading carries
# ---------------------------------------------------------------------------


def every_state(tmp_path: Path) -> list[sibling.Reading]:
    """One reading of each of the three states, from real repositories."""
    root, directory = workspace(tmp_path)
    committed = contract(root)
    shutil.rmtree(directory / ".git")
    local = contract(root)
    shutil.rmtree(directory)
    return [committed, local, contract(root)]


def test_exactly_one_of_the_three_states_is_true_of_any_reading(tmp_path):
    readings = every_state(tmp_path)
    assert {reading.state for reading in readings} == set(sibling.STATES)
    for reading in readings:
        assert reading.state in sibling.STATES
        assert [reading.committed, reading.working_tree, reading.absent].count(True) == 1


def test_no_reading_ever_puts_a_path_from_this_machine_in_its_sentence(tmp_path):
    # ⛔ R7: a sibling's directory is an absolute path under somebody's home, and
    # a reading's sentence is printed into skip messages and build logs.
    for reading in every_state(tmp_path):
        assert str(tmp_path) not in reading.source
        assert reading.source == reading.source.strip() and reading.source
    # ⭐ The instrument can go red: the same check over a sentence that DID carry
    # one catches it, so a green above is a measurement rather than a tautology.
    assert str(tmp_path) in f"read from {tmp_path}"
