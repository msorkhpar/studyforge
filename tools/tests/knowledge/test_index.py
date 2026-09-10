"""Mirror of `tools/knowledge/index.py` (R12) — freshness, without a clock.

⛔ **Every test here builds its own repository.** None of them reads this
checkout's index, so none of them can skip: a test that needs an artifact
`.gitignore` keeps out of every branch is the exact failure FND-07 exists to
close, reproduced inside FND-07.
"""

from __future__ import annotations

import json
import os

from tools.knowledge.index import (
    COMMIT_KEY,
    DESCRIBED_TREES,
    EXCLUDE,
    FRESH,
    STALE,
    UNDESCRIBED_PATHS,
    UNVERIFIABLE,
    built_at_commit,
    described_pathspecs,
    freshness,
    index_path,
    read_graph,
)
from tools.tests.knowledge.support import commit_all, make_repository


def with_a_board_and_handoffs(tmp_path):
    """A repository whose `docs/` already carries the paths the index excludes.

    ⛔ They exist in the base commit on purpose. A path added between the two
    commits would be excluded too, so creating it later would prove the
    exclusion for the easy case and leave modification — the case every merge
    actually produces — untested.
    """
    root, _first = make_repository(tmp_path)
    tasks = root / "docs" / "tasks"
    (tasks / "handoffs").mkdir(parents=True)
    (tasks / "handoffs" / "W1.md").write_text("# W1 — handoff\n", encoding="utf-8")
    (tasks / "BOARD.md").write_text("# board\n", encoding="utf-8")
    (tasks / "BOARD-ARCHIVE.md").write_text("# archive\n", encoding="utf-8")
    (tasks / "rows").mkdir(parents=True)
    (tasks / "rows" / "SF-1.md").write_text("# SF-1\n", encoding="utf-8")
    (tasks / "README.md").write_text("# tasks\n", encoding="utf-8")
    return root, commit_all(root, "the board, its archive, a row and a handoff exist")


def test_the_graph_path_is_where_graphify_writes_it(tmp_path):
    assert index_path(tmp_path).as_posix().endswith("graphify-out/graph.json")


def test_an_absent_or_malformed_graph_reads_as_none(tmp_path):
    assert read_graph(tmp_path / "nothing.json") is None
    broken = tmp_path / "graph.json"
    broken.write_text("{not json", encoding="utf-8")
    # ⚠️ Absent rather than raising: a half-written local artifact is a rebuild
    # the reader needs to be told about, not a crash in the quality floor.
    assert read_graph(broken) is None


def test_a_graph_that_does_not_say_when_it_was_built_says_so(tmp_path):
    assert built_at_commit({}) is None
    assert built_at_commit({COMMIT_KEY: ""}) is None
    assert built_at_commit({COMMIT_KEY: "abc123"}) == "abc123"


def test_an_index_built_at_head_is_fresh(tmp_path):
    root, head = make_repository(tmp_path)
    assert freshness(root, head) == FRESH


def test_an_index_is_still_fresh_after_a_commit_that_changed_nothing_it_describes(tmp_path):
    # ⛔ Ruling 18's other half, and the reason the comparison is a diff rather
    # than `built != HEAD`. Every commit moves HEAD; a check that fired on all
    # of them would be rebuilt past reflexively.
    root, head = make_repository(tmp_path)
    (root / "README.md").write_text("a change outside src, tools and docs\n", encoding="utf-8")
    commit_all(root, "docs are elsewhere")
    assert freshness(root, head) == FRESH


def test_an_index_goes_stale_when_a_described_tree_changes(tmp_path):
    root, head = make_repository(tmp_path)
    (root / "src" / "thing.py").write_text("VALUE = 2\n", encoding="utf-8")
    commit_all(root, "change what the index describes")
    assert freshness(root, head) == STALE


def test_touching_every_file_does_not_change_the_verdict(tmp_path):
    # ⛔ **Ruling 18, asserted rather than promised.** An mtime check was
    # measured wrong in both directions on the same index within 33 minutes,
    # and `git worktree add` resets every mtime — so a clock here would fail
    # in every trial-merge worktree, breaking the gate that catches C5.
    # ⭐ This is the test that makes a clock impossible to reintroduce.
    root, head = make_repository(tmp_path)
    before = freshness(root, head)
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".git" not in path.parts:
            os.utime(path, (0, 0))
    assert freshness(root, head) == before == FRESH


def test_a_commit_this_checkout_does_not_have_is_unverifiable_not_stale(tmp_path):
    # ⚠️ "I cannot answer" is not "the answer is no". The index may be current
    # and simply built in a clone this one cannot see.
    root, _head = make_repository(tmp_path)
    assert freshness(root, "0" * 40) == UNVERIFIABLE


def test_a_tree_that_is_not_a_repository_is_unverifiable(tmp_path):
    assert freshness(tmp_path, "0" * 40) == UNVERIFIABLE
    assert freshness(tmp_path, None) == UNVERIFIABLE


# --- Ruling 96 part 1: the described trees, minus what they do not describe ---


def test_a_handoff_does_not_make_the_index_stale(tmp_path):
    # ⛔ The defect this row exists for. Every merge in this project writes a
    # handoff, so before the exclusion every merge reddened the tip by
    # construction — including a one-file docs-only one.
    root, head = with_a_board_and_handoffs(tmp_path)
    (root / "docs" / "tasks" / "handoffs" / "W1.md").write_text("# W1 — edited\n", "utf-8")
    commit_all(root, "a handoff is written")
    assert freshness(root, head) == FRESH


def test_a_NEW_handoff_does_not_make_the_index_stale_either(tmp_path):
    root, head = with_a_board_and_handoffs(tmp_path)
    (root / "docs" / "tasks" / "handoffs" / "W2.md").write_text("# W2\n", encoding="utf-8")
    commit_all(root, "a handoff is added")
    assert freshness(root, head) == FRESH


def test_a_board_row_does_not_make_the_index_stale(tmp_path):
    root, head = with_a_board_and_handoffs(tmp_path)
    (root / "docs" / "tasks" / "BOARD.md").write_text("# board\n\n| W39 | done |\n", "utf-8")
    commit_all(root, "a board row moves")
    assert freshness(root, head) == FRESH


def test_the_board_archive_does_not_make_the_index_stale(tmp_path):
    root, head = with_a_board_and_handoffs(tmp_path)
    (root / "docs" / "tasks" / "BOARD-ARCHIVE.md").write_text("# archive\n\n| W1 |\n", "utf-8")
    commit_all(root, "the board is archived")
    assert freshness(root, head) == FRESH


def test_all_three_moving_at_once_still_leaves_the_index_fresh(tmp_path):
    # ⭐ The shape of a real merge: a handoff, a board row and the archive, in
    # one commit, and nothing the index describes.
    root, head = with_a_board_and_handoffs(tmp_path)
    tasks = root / "docs" / "tasks"
    (tasks / "handoffs" / "W1.md").write_text("# W1 — edited\n", encoding="utf-8")
    (tasks / "BOARD.md").write_text("# board — edited\n", encoding="utf-8")
    (tasks / "BOARD-ARCHIVE.md").write_text("# archive — edited\n", encoding="utf-8")
    commit_all(root, "a round closes")
    assert freshness(root, head) == FRESH


def test_a_row_file_under_the_boards_rows_directory_leaves_the_index_fresh(tmp_path):
    # ⭐ Ruling 175: `docs/tasks/rows/` is the board under a new carrier, not a
    # new subject. Every byte in it was inside `BOARD.md`, where it was already
    # excluded, so a round that edits one row must not redden the tip. ⛔ Run,
    # not read — the whole point of the entry is that this instrument stops
    # firing, and a received reading is not a reading (Ruling 115).
    root, head = with_a_board_and_handoffs(tmp_path)
    rows = root / "docs" / "tasks" / "rows"
    (rows / "SF-1.md").write_text("# SF-1 — state changed\n", encoding="utf-8")
    (rows / "SF-2.md").write_text("# SF-2 — minted\n", encoding="utf-8")
    commit_all(root, "a row moves and a row is minted")
    assert freshness(root, head) == FRESH


def test_a_DOCUMENT_THAT_IS_NOT_ONE_OF_THE_THREE_still_makes_it_stale(tmp_path):
    # ⛔ The negative control, run negatively. An exclusion that swallowed
    # `docs/` would be indistinguishable from these tests passing, and it would
    # be the same defect in the opposite direction: a check that never fires.
    root, head = with_a_board_and_handoffs(tmp_path)
    (root / "docs" / "note.md").write_text("# a convention changes\n", encoding="utf-8")
    commit_all(root, "a described document moves")
    assert freshness(root, head) == STALE


def test_a_SIBLING_of_the_board_inside_docs_tasks_still_makes_it_stale(tmp_path):
    # ⚠️ The exclusion is three named paths, not the directory that holds them.
    root, head = with_a_board_and_handoffs(tmp_path)
    (root / "docs" / "tasks" / "README.md").write_text("# tasks — edited\n", encoding="utf-8")
    commit_all(root, "an epic document moves")
    assert freshness(root, head) == STALE


def test_an_excluded_path_beside_a_described_one_does_not_mask_it(tmp_path):
    # ⛔ Exclusion removes paths from the diff; it must not remove commits.
    root, head = with_a_board_and_handoffs(tmp_path)
    (root / "docs" / "tasks" / "BOARD.md").write_text("# board — edited\n", encoding="utf-8")
    (root / "src" / "thing.py").write_text("VALUE = 3\n", encoding="utf-8")
    commit_all(root, "a board row and a module, together")
    assert freshness(root, head) == STALE


def test_the_pathspecs_are_the_trees_plus_one_exclusion_each(tmp_path):
    spelled = described_pathspecs()
    assert spelled[: len(DESCRIBED_TREES)] == list(DESCRIBED_TREES)
    assert spelled[len(DESCRIBED_TREES) :] == [f"{EXCLUDE}{path}" for path in UNDESCRIBED_PATHS]


def test_gitignore_gets_no_entry_because_it_is_already_outside_the_trees(tmp_path):
    # ⚠️ The comment's third example, and the one a reader is most likely to
    # "fix" by adding a fourth entry. It is not under any described tree, so an
    # entry for it would be dead configuration that looks load-bearing.
    assert not any(path.endswith(".gitignore") for path in UNDESCRIBED_PATHS)
    assert all(path.split("/")[0] in DESCRIBED_TREES for path in UNDESCRIBED_PATHS)


def test_the_graph_round_trips_through_the_reader(tmp_path):
    path = tmp_path / "graph.json"
    path.write_text(json.dumps({COMMIT_KEY: "deadbee", "nodes": [], "links": []}), "utf-8")
    assert built_at_commit(read_graph(path)) == "deadbee"
