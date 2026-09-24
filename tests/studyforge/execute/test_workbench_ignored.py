"""Mirror of `src/studyforge/execute/workbench.py`, `W435`: a served corpus stays clean.

⭐ **Measured the way `tools.workspace verify` measures it** — a throwaway git
repository shaped like a corpus, a practice's settings written into it, and
`git status` asked what it sees. ⛔ The text of the ignore file is never the
evidence on its own: a rule that reads right and ignores nothing is exactly the
defect this row was minted over.

⚠️ **Both directions.** The framework's own three files vanish from `git
status`; a `.vscode/` the source or the reader already carries keeps every file
of its own visible and tracked, and an ignore file of theirs is never
rewritten. ⛔ **And the plant**: the same directory MINUS the ignore file is
dirty, so a green run here is about the rule and not about the fixture.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.execute.workbench import (
    IGNORE_FILE,
    IGNORE_TEXT,
    SETTINGS_DIR,
    SETTINGS_FILE,
    STAGING_DIR,
    WorkbenchRefused,
    write_settings,
)
from tests.support import git, init_repository, is_ignored, run

#: Where a corpus's editor folder sits, as the first corpus has it.
BASE = "practice"
INSIDE_MAIN = "bitmap/Bitmap.java"
INSIDE_TEST = "bitmap/BitmapTest.java"


def status(root: Path) -> list[str]:
    """`git status --porcelain` for `root`, untracked files listed one by one."""
    result = run([git(), "status", "--porcelain", "--untracked-files=all"], cwd=root)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.splitlines()


def corpus(tmp_path: Path) -> Path:
    """A repository with one practice folder in it, its source staged and clean of strays."""
    root = init_repository(tmp_path / "corpus")
    (root / BASE / "bitmap").mkdir(parents=True)
    (root / BASE / "bitmap" / "Bitmap.java").write_text("class Bitmap {}\n", encoding="utf-8")
    assert run([git(), "add", "-A"], cwd=root).returncode == 0
    return root


def untracked(root: Path) -> list[str]:
    """The paths `git status` reports as untracked — what `verify` refuses."""
    return [line[3:] for line in status(root) if line.startswith("??")]


# --- ⭐ the framework's own files never reach a commit ----------------------


def test_a_served_practice_leaves_the_corpus_clean(tmp_path):
    root = corpus(tmp_path)
    write_settings(root / BASE, INSIDE_MAIN, INSIDE_TEST)
    assert (root / BASE / SETTINGS_DIR / SETTINGS_FILE).is_file()
    assert untracked(root) == []


def test_a_second_ask_and_another_practice_leave_it_clean_too(tmp_path):
    root = corpus(tmp_path)
    write_settings(root / BASE, INSIDE_MAIN, INSIDE_TEST)
    write_settings(root / BASE, "other/Kata.java", None)
    assert untracked(root) == []


def test_the_ignore_file_names_the_three_files_and_itself_and_is_not_a_star(tmp_path):
    root = corpus(tmp_path)
    write_settings(root / BASE, INSIDE_MAIN, INSIDE_TEST)
    folder = f"{BASE}/{SETTINGS_DIR}"
    # ⭐ Each write stages under its OWN name inside the staging
    # directory, so the directory is what is named and whatever is in it is ours.
    for name in (SETTINGS_FILE, f"{STAGING_DIR}/{SETTINGS_FILE}k3x9_q", IGNORE_FILE):
        assert is_ignored(f"{folder}/{name}", cwd=root), name
    # ⛔ Names, never `*`: anything else in the directory is somebody else's.
    assert not is_ignored(f"{folder}/launch.json", cwd=root)
    assert "*" not in IGNORE_TEXT


def test_the_corpus_goes_dirty_the_moment_the_ignore_file_is_not_written(tmp_path):
    # ⛔ The plant: the directory exactly as `write_settings` leaves it, MINUS
    # the ignore file. If this ever reads clean, the test above proves nothing.
    root = corpus(tmp_path)
    write_settings(root / BASE, INSIDE_MAIN, INSIDE_TEST)
    (root / BASE / SETTINGS_DIR / IGNORE_FILE).unlink()
    assert untracked(root) == [f"{BASE}/{SETTINGS_DIR}/{SETTINGS_FILE}"]


# --- ⛔ a `.vscode/` somebody else carries is never rewritten, never ignored --


def test_a_sources_own_tracked_vscode_stays_tracked_and_visible(tmp_path):
    root = corpus(tmp_path)
    theirs = root / BASE / SETTINGS_DIR
    theirs.mkdir()
    (theirs / "launch.json").write_text("{}\n", encoding="utf-8")
    assert run([git(), "add", "-A"], cwd=root).returncode == 0
    write_settings(root / BASE, INSIDE_MAIN, INSIDE_TEST)
    tracked = run([git(), "ls-files", f"{BASE}/{SETTINGS_DIR}"], cwd=root).stdout.split()
    assert tracked == [f"{BASE}/{SETTINGS_DIR}/launch.json"]
    assert untracked(root) == []
    # ⭐ And a file the reader adds there later is SEEN, not swallowed.
    (theirs / "extensions.json").write_text("{}\n", encoding="utf-8")
    assert untracked(root) == [f"{BASE}/{SETTINGS_DIR}/extensions.json"]


def test_an_ignore_file_already_there_is_never_rewritten(tmp_path):
    root = corpus(tmp_path)
    theirs = root / BASE / SETTINGS_DIR
    theirs.mkdir()
    own = "# the source's own rules\n/local.json\n"
    (theirs / IGNORE_FILE).write_text(own, encoding="utf-8")
    write_settings(root / BASE, INSIDE_MAIN, INSIDE_TEST)
    assert (theirs / IGNORE_FILE).read_text(encoding="utf-8") == own
    # ⚠️ The cost, stated rather than hidden: their rule does not name the
    # settings, so git reports them — somebody else's rule is not overridden.
    assert f"{BASE}/{SETTINGS_DIR}/{SETTINGS_FILE}" in untracked(root)


def test_the_refusal_of_a_settings_file_it_did_not_write_survives_and_adds_nothing(tmp_path):
    root = corpus(tmp_path)
    theirs = root / BASE / SETTINGS_DIR
    theirs.mkdir()
    mine = '{"editor.fontSize": 18}\n'
    (theirs / SETTINGS_FILE).write_text(mine, encoding="utf-8")
    assert run([git(), "add", "-A"], cwd=root).returncode == 0
    with pytest.raises(WorkbenchRefused):
        write_settings(root / BASE, INSIDE_MAIN, INSIDE_TEST)
    assert (theirs / SETTINGS_FILE).read_text(encoding="utf-8") == mine
    # ⛔ Refused BEFORE anything is written: no ignore file appears beside a
    # settings file that is not this framework's.
    assert sorted(one.name for one in theirs.iterdir()) == [SETTINGS_FILE]
    assert untracked(root) == []
