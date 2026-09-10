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
    FRESH,
    STALE,
    UNVERIFIABLE,
    built_at_commit,
    freshness,
    index_path,
    read_graph,
)
from tools.tests.knowledge.support import commit_all, make_repository


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


def test_the_graph_round_trips_through_the_reader(tmp_path):
    path = tmp_path / "graph.json"
    path.write_text(json.dumps({COMMIT_KEY: "deadbee", "nodes": [], "links": []}), "utf-8")
    assert built_at_commit(read_graph(path)) == "deadbee"
