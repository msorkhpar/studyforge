"""Mirror of `tools/workspace/pinned.py` (R12).

⛔ **The subject is a distinction, so every case asserts both sides of it.** A
file that is at the pin must read **at the pin** even when a different one sits
in the working tree; a file that is **only** in the working tree must read as
**local** and say so; and nothing to read at all must be an **answer** rather
than an exception — the pinned image's case, where no sibling resolves.

⭐ **Real `git init` repositories, built per test** (`tools/tests/workspace/support.py`
gives the reason and the placeholder identity). ⛔ **No real sibling is touched:**
another office's gate may be reading one, and a test that needed one would skip
inside the authoritative image, where a skipped check is not evidence.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from tools.tests.workspace import support
from tools.workspace import pinned

#: The sibling this builds, the file it reads out of it, and the two contents
#: that must never be confused for one another.
NAME = "Toolchain"
CONTRACT = "consuming.json"
AT_PIN = '{"provides": 2, "where": "at the pin"}'
IN_TREE = '{"provides": 99, "where": "the working tree only"}'


def sibling(root: Path, text: str | None) -> tuple[Path, str]:
    """A sibling checkout, carrying `text` as its contract when there is one.

    ⭐ `docs/api.md` is committed either way: a committed **directory** is what
    proves the reader refuses a tree rather than handing back a listing.
    """
    directory = root / NAME
    support.repository(directory, NAME)
    (directory / "docs").mkdir()
    (directory / "docs" / "api.md").write_text("the component's own API\n", encoding="utf-8")
    if text is not None:
        (directory / CONTRACT).write_text(text, encoding="utf-8")
    support.run(directory, "add", "-A")
    support.run(directory, "commit", "-qm", "contract")
    return directory, support.run(directory, "rev-parse", "HEAD")


def workspace(tmp_path: Path, text: str | None = AT_PIN) -> tuple[Path, Path, Path]:
    """`(workspace root, this repository, the sibling's checkout)`, all pinned correctly."""
    root = tmp_path / "w"
    root.mkdir(parents=True, exist_ok=True)
    here = root / "studyforge"
    mine = support.repository(here)
    directory, commit = sibling(root, text)
    support.write_pin(
        here,
        [
            {"name": "studyforge", "where": "self", "status": "present", "commit": mine},
            {"name": NAME, "where": "sibling", "status": "present", "commit": commit},
        ],
    )
    return root, here, directory


def contract(root: Path, here: Path, path: str = CONTRACT) -> pinned.Reading:
    """Read one file out of the pinned sibling — what every case below calls."""
    return pinned.read_sibling(NAME, path, repository_root=here, workspace_root=root)


def repin(here: Path, commit: str) -> None:
    """Point the sibling's row at `commit`, leaving every other row alone."""
    document = json.loads((here / "workspace.json").read_text(encoding="utf-8"))
    rows = [
        {**row, "commit": commit} if row["name"] == NAME else row
        for row in document["components"]
    ]
    support.write_pin(here, rows)


# ---------------------------------------------------------------------------
# ⭐ at the pin — the only reading another host reproduces
# ---------------------------------------------------------------------------


def test_a_file_at_the_pinned_commit_is_read_at_the_pin(tmp_path):
    root, here, _ = workspace(tmp_path)
    reading = contract(root, here)
    assert reading.pinned and not reading.working_tree and not reading.absent
    assert reading.text == AT_PIN
    assert NAME in reading.source and CONTRACT in reading.source


def test_the_working_tree_is_not_read_when_the_pin_carries_the_file(tmp_path):
    # ⛔ `W404` head on: a different contract sits on disk and must not be seen.
    root, here, directory = workspace(tmp_path)
    (directory / CONTRACT).write_text(IN_TREE, encoding="utf-8")
    reading = contract(root, here)
    assert reading.pinned
    assert reading.text == AT_PIN
    assert "99" not in reading.text


def test_a_checkout_whose_head_moved_past_its_pin_is_still_read_at_the_pin(tmp_path):
    # ⭐ Committed this time, so the file exists on a ref — and on the WRONG one.
    root, here, directory = workspace(tmp_path)
    (directory / CONTRACT).write_text(IN_TREE, encoding="utf-8")
    support.run(directory, "add", CONTRACT)
    support.run(directory, "commit", "-qm", "moved")
    reading = contract(root, here)
    assert reading.pinned and reading.text == AT_PIN


# ---------------------------------------------------------------------------
# ⛔ the working tree — allowed, labelled, never mistaken for the pin
# ---------------------------------------------------------------------------


def test_a_staged_contract_that_exists_on_no_ref_reads_as_local_and_says_so(tmp_path):
    """⛔ **The measured case.** A checkout mid-merge, and the file is on no ref."""
    root, here, directory = workspace(tmp_path, text=None)
    (directory / CONTRACT).write_text(IN_TREE, encoding="utf-8")
    support.run(directory, "add", CONTRACT)
    reading = contract(root, here)
    assert reading.working_tree and not reading.pinned and not reading.absent
    assert reading.text == IN_TREE
    assert "WORKING TREE" in reading.source and "LOCAL" in reading.source
    # ⭐ The other half of the measurement: the file really is on disk, so the
    # reader that looked at disk read it as the contract and went green.
    assert (directory / CONTRACT).read_text(encoding="utf-8") == IN_TREE


def test_a_checkout_that_does_not_hold_its_pin_is_a_local_reading(tmp_path):
    root, here, directory = workspace(tmp_path)
    repin(here, "0" * 40)
    reading = contract(root, here)
    assert reading.working_tree and not reading.pinned
    assert reading.text == AT_PIN
    assert "does not hold its pinned commit" in reading.source


# ---------------------------------------------------------------------------
# ⛔ absent — an answer, because the pinned image mounts one directory
# ---------------------------------------------------------------------------


def test_no_checkout_beside_this_repository_is_absent_and_not_a_crash(tmp_path):
    root, here, directory = workspace(tmp_path)
    shutil.rmtree(directory)
    reading = contract(root, here)
    assert reading.absent and reading.text is None
    assert NAME in reading.source


def test_a_component_the_pin_file_does_not_name_is_absent(tmp_path):
    root, here, _ = workspace(tmp_path)
    reading = pinned.read_sibling(
        "Nowhere", CONTRACT, repository_root=here, workspace_root=root
    )
    assert reading.absent and "Nowhere" in reading.source


def test_a_component_that_is_not_created_yet_is_absent(tmp_path):
    # ⭐ `not-yet-created` is a first-class row (Ruling 54), so it is a first-class
    # reading too — never a lookup that silently falls through to the disk.
    root, here, _ = workspace(tmp_path)
    document = json.loads((here / "workspace.json").read_text(encoding="utf-8"))
    rows = [row for row in document["components"] if row["name"] != NAME]
    rows.append({"name": NAME, "where": "sibling", "status": "not-yet-created"})
    support.write_pin(here, rows)
    assert contract(root, here).absent


def test_no_contract_at_the_pin_and_none_on_disk_is_absent(tmp_path):
    root, here, _ = workspace(tmp_path, text=None)
    reading = contract(root, here)
    assert reading.absent and reading.text is None
    assert "working tree either" in reading.source


def test_a_path_that_is_a_directory_at_the_pin_is_never_read_as_content(tmp_path):
    # ⛔ `git show <commit>:docs` prints a TREE LISTING and exits 0. A reader
    # built on it hands that listing back as if it were the file.
    root, here, _ = workspace(tmp_path)
    assert contract(root, here, "docs").absent
    # ⭐ The file inside it reads fine, so the refusal is about the shape.
    assert contract(root, here, "docs/api.md").pinned


# ---------------------------------------------------------------------------
# ⛔ a directory the caller named — the fourth thing, and not one of the three
# ---------------------------------------------------------------------------


def test_a_directory_the_caller_named_is_local_by_construction(tmp_path):
    (tmp_path / CONTRACT).write_text(IN_TREE, encoding="utf-8")
    reading = pinned.read_directory(tmp_path, CONTRACT)
    assert reading.working_tree and not reading.pinned
    assert reading.text == IN_TREE
    assert "does not pin" in reading.source


def test_a_directory_the_caller_named_with_nothing_in_it_is_absent(tmp_path):
    reading = pinned.read_directory(tmp_path, CONTRACT)
    assert reading.absent and reading.text is None
    assert CONTRACT in reading.source


# ---------------------------------------------------------------------------
# ⛔ the properties every reading carries
# ---------------------------------------------------------------------------


def every_state(tmp_path: Path) -> list[pinned.Reading]:
    """One reading of each of the three states, from real repositories."""
    root, here, directory = workspace(tmp_path)
    at_pin = contract(root, here)
    repin(here, "0" * 40)
    local = contract(root, here)
    shutil.rmtree(directory)
    return [at_pin, local, contract(root, here)]


def test_exactly_one_of_the_three_states_is_true_of_any_reading(tmp_path):
    readings = every_state(tmp_path)
    assert {reading.state for reading in readings} == set(pinned.STATES)
    for reading in readings:
        assert reading.state in pinned.STATES
        assert [reading.pinned, reading.working_tree, reading.absent].count(True) == 1


def test_no_reading_ever_puts_a_path_from_this_machine_in_its_sentence(tmp_path):
    # ⛔ R7: a sibling's directory is an absolute path under somebody's home, and
    # a reading's sentence is printed into skip messages and build logs.
    for reading in every_state(tmp_path):
        assert str(tmp_path) not in reading.source
        assert reading.source == reading.source.strip() and reading.source
    # ⭐ The instrument can go red: the same check over a sentence that DID carry
    # one catches it, so a green above is a measurement rather than a tautology.
    assert str(tmp_path) in f"read from {tmp_path}"
