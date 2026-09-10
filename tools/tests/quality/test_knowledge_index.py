"""Mirror of `tools/quality/knowledge_index.py` (R12) — the three states.

⛔ Every state is built in `tmp_path`. Nothing here reads this checkout's
`graphify-out/`, so nothing skips — which matters more here than anywhere:
FND-07 exists because an acceptance was true in one worktree and false in
every other, and a test that needed a local index would repeat that.
"""

from __future__ import annotations

import json

from tools.knowledge import BRIDGE_FLOOR, REBUILD_COMMANDS, index_path
from tools.quality.knowledge_index import RULE, check_knowledge_index, notices
from tools.tests.knowledge.support import commit_all, make_repository


def write_index(root, commit, bridged):
    """An index at `root` built at `commit`, carrying `bridged` bridge edges."""
    nodes = [
        {"id": "r", "label": "R7 — A rule", "file_type": "rationale", "source_file": "docs/s.md"}
    ]
    links = []
    for number in range(bridged):
        nodes.append(
            {
                "id": f"c{number}",
                "label": "thing()",
                "file_type": "code",
                "source_file": f"src/m{number}.py",
                "source_location": "L1",
            }
        )
        links.append({"source": "r", "target": f"c{number}", "relation": "implemented_by"})
    path = index_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"built_at_commit": commit, "nodes": nodes, "links": links}), "utf-8"
    )
    return path


# --- absent -----------------------------------------------------------------


def test_an_absent_index_is_not_a_finding(tmp_path):
    # ⛔ The first state, and the one most easily got wrong. A fresh clone
    # legitimately has no index; a red suite on clone is hostile and gets
    # muted, which is how a check stops being read.
    assert check_knowledge_index(tmp_path) == []


def test_an_absent_index_is_reported_with_the_command_that_fixes_it(tmp_path):
    reported = notices(tmp_path)
    assert len(reported) == 1
    for command in REBUILD_COMMANDS:
        assert command in reported[0]
    assert "not a failure" in reported[0]


# --- stale ------------------------------------------------------------------


def test_a_stale_index_fails(tmp_path):
    # ⭐ Worse than absent, because absence is visible: a stale index answers
    # confidently with yesterday's tree.
    root, head = make_repository(tmp_path)
    write_index(root, head, BRIDGE_FLOOR)
    assert check_knowledge_index(root) == []
    (root / "src" / "thing.py").write_text("VALUE = 2\n", encoding="utf-8")
    commit_all(root, "the tree moves under the index")
    found = check_knowledge_index(root)
    assert [finding.rule for finding in found] == [RULE]
    assert "stale" in found[0].message
    for command in REBUILD_COMMANDS:
        assert command in found[0].message


def test_the_verdict_is_made_by_content_and_never_by_a_clock(tmp_path):
    # ⛔ Ruling 18, at the level the floor sees. A commit that touches nothing
    # the index describes leaves it fresh; `built != HEAD` would fail here.
    root, head = make_repository(tmp_path)
    write_index(root, head, BRIDGE_FLOOR)
    (root / "README.md").write_text("outside src, tools and docs\n", encoding="utf-8")
    commit_all(root, "a commit the index does not describe")
    assert check_knowledge_index(root) == []


# --- present, current, unbridged --------------------------------------------


def test_a_current_but_unbridged_index_fails(tmp_path):
    # ⛔ The worst of the three: every green light is on and the one question
    # that matters returns silence.
    root, head = make_repository(tmp_path)
    write_index(root, head, BRIDGE_FLOOR - 1)
    found = check_knowledge_index(root)
    assert [finding.rule for finding in found] == [RULE]
    assert "unbridged" in found[0].message
    assert str(BRIDGE_FLOOR) in found[0].message
    assert REBUILD_COMMANDS[1] in found[0].message


def test_a_bridged_index_at_the_floor_passes(tmp_path):
    root, head = make_repository(tmp_path)
    write_index(root, head, BRIDGE_FLOOR)
    assert check_knowledge_index(root) == []


# --- unverifiable -----------------------------------------------------------


def test_an_index_whose_commit_this_checkout_lacks_is_reported_not_failed(tmp_path):
    # ⚠️ "I cannot answer" must never arrive as "the answer is no".
    root, _head = make_repository(tmp_path)
    write_index(root, "0" * 40, BRIDGE_FLOOR)
    assert check_knowledge_index(root) == []
    assert "could not be checked" in notices(root)[0]


def test_a_malformed_index_is_absent_rather_than_a_crash(tmp_path):
    path = index_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("{not json", encoding="utf-8")
    assert check_knowledge_index(tmp_path) == []
    assert "none in this checkout" in notices(tmp_path)[0]


# --- the finding's own shape ------------------------------------------------


def test_a_finding_points_at_a_repository_relative_path(tmp_path):
    # ⛔ R7: an absolute path in a build log carries the user's home directory.
    root, head = make_repository(tmp_path)
    write_index(root, head, 0)
    found = check_knowledge_index(root)
    assert found[0].path == "graphify-out/graph.json"
    assert not found[0].path.startswith("/")
