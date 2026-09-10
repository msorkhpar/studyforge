"""Mirror of `tools/quality/knowledge_index.py` (R12) — the three states.

⛔ Every state is built in `tmp_path`. Nothing here reads this checkout's
`graphify-out/`, so nothing skips — which matters more here than anywhere:
FND-07 exists because an acceptance was true in one worktree and false in
every other, and a test that needed a local index would repeat that.
"""

from __future__ import annotations

import json

from tools.knowledge import BRIDGE_FLOOR, FRESH, REBUILD_COMMANDS, STALE, UNVERIFIABLE, index_path
from tools.quality.knowledge_index import (
    ABSENT,
    PREFIX,
    RULE,
    check_knowledge_index,
    notices,
    verdict,
)
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


def stale_repository(tmp_path):
    """A repository whose index is genuinely behind what it describes."""
    root, head = make_repository(tmp_path)
    write_index(root, head, BRIDGE_FLOOR)
    (root / "src" / "thing.py").write_text("VALUE = 2\n", encoding="utf-8")
    commit_all(root, "the tree moves under the index")
    return root


def test_a_stale_index_is_a_NOTICE_and_never_a_finding(tmp_path):
    # ⛔ Ruling 96 part 2. The sentence survives; the exit code does not.
    # `graphify-out/` is git-ignored, so a finding here would read clean on a
    # fresh clone and exit 1 on a machine that had built one — Ruling 80.
    root = stale_repository(tmp_path)
    assert check_knowledge_index(root) == []
    assert verdict(root) == STALE


def test_the_stale_notice_still_says_why_stale_is_worse_than_absent(tmp_path):
    # ⭐ The argument the old finding carried is the reason the line is worth
    # quoting. Losing it would make this a deletion rather than a trade.
    root = stale_repository(tmp_path)
    line = notices(root)[0]
    assert line.startswith(f"{PREFIX}{STALE} ")
    assert "worse than an absent one" in line
    assert "yesterday's tree" in line
    for command in REBUILD_COMMANDS:
        assert command in line


def test_the_stale_notice_names_the_commit_the_index_was_built_at(tmp_path):
    # ⛔ The rubric's index line asks for the built-at commit, so the tool that
    # supplies the line supplies the commit — a reviewer must not retype it.
    root, head = make_repository(tmp_path)
    write_index(root, head, BRIDGE_FLOOR)
    (root / "src" / "thing.py").write_text("VALUE = 2\n", encoding="utf-8")
    commit_all(root, "the tree moves under the index")
    assert head[:8] in notices(root)[0]


def test_the_stale_notice_says_it_is_not_a_licence(tmp_path):
    # ⚠️ A notice that reads as permission is how the sentence above gets lost.
    root = stale_repository(tmp_path)
    line = notices(root)[0]
    assert "Not a failure" in line
    assert "not a licence" in line


def test_no_FRESHNESS_state_changes_the_floors_exit_code(tmp_path):
    # ⛔ Ruling 80, asserted rather than promised. One commit, read in all four
    # states of the rubric's vocabulary, yields the same number of findings.
    # ⚠️ Scoped to freshness on purpose — see the test below for what is left.
    root, head = make_repository(tmp_path)
    assert check_knowledge_index(root) == []  # none
    write_index(root, "0" * 40, BRIDGE_FLOOR)
    assert check_knowledge_index(root) == []  # unverifiable
    write_index(root, head, BRIDGE_FLOOR)
    assert check_knowledge_index(root) == []  # fresh
    (root / "src" / "thing.py").write_text("VALUE = 2\n", encoding="utf-8")
    commit_all(root, "the tree moves under the index")
    assert check_knowledge_index(root) == []  # stale


def test_the_UNBRIDGED_finding_still_depends_on_untracked_state(tmp_path):
    # ⛔ RECORDED, NOT FIXED — `W39/4`. Ruling 96 claims that after part 2 "the
    # floor's exit code does not depend on `graphify-out/` in ANY state", and
    # its own enumerated step names only `STALE`. ⚠️ This is the counterexample:
    # the same commit is clean with no index and exit 1 with an unbridged one,
    # which is the shape Ruling 80 forbids.
    # ⭐ It is asserted rather than left to memory, so the residual is checkable
    # and the next reader of the ruling meets the gap rather than the claim.
    root, head = make_repository(tmp_path)
    assert check_knowledge_index(root) == []
    write_index(root, head, BRIDGE_FLOOR - 1)
    assert [finding.rule for finding in check_knowledge_index(root)] == [RULE]


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


# --- the line the reviewer quotes -------------------------------------------


def test_the_floor_prints_a_line_in_every_one_of_the_four_states(tmp_path):
    # ⛔ Ruling 96's mechanism is QUOTATION, so a state that prints nothing is a
    # state the reviewer fills in from memory. `fresh` is the one that used to
    # be silent, and it is the one a green review needs most.
    root, head = make_repository(tmp_path)
    assert len(notices(root)) == 1  # none
    write_index(root, "0" * 40, BRIDGE_FLOOR)
    assert len(notices(root)) == 1  # unverifiable
    write_index(root, head, BRIDGE_FLOOR)
    fresh = notices(root)
    assert len(fresh) == 1 and fresh[0].startswith(f"{PREFIX}{FRESH} ")
    (root / "src" / "thing.py").write_text("VALUE = 2\n", encoding="utf-8")
    commit_all(root, "the tree moves under the index")
    assert len(notices(root)) == 1  # stale


def test_every_line_opens_with_the_same_prefix_and_its_verdict_word(tmp_path):
    # ⭐ So a reviewer can obtain the line with one grep, and the rubric can
    # name that grep instead of describing the output.
    root, head = make_repository(tmp_path)
    assert notices(root)[0].startswith(f"{PREFIX}{ABSENT} ")
    write_index(root, "0" * 40, BRIDGE_FLOOR)
    assert notices(root)[0].startswith(f"{PREFIX}{UNVERIFIABLE} ")
    write_index(root, head, BRIDGE_FLOOR)
    assert notices(root)[0].startswith(f"{PREFIX}{FRESH} ")


def test_the_fresh_line_names_the_commit_too(tmp_path):
    root, head = make_repository(tmp_path)
    write_index(root, head, BRIDGE_FLOOR)
    assert head[:8] in notices(root)[0]


def test_the_verdict_word_is_the_rubrics_own_vocabulary(tmp_path):
    root, head = make_repository(tmp_path)
    assert verdict(root) == ABSENT == "none"
    write_index(root, "0" * 40, BRIDGE_FLOOR)
    assert verdict(root) == UNVERIFIABLE
    write_index(root, head, BRIDGE_FLOOR)
    assert verdict(root) == FRESH


def test_a_handoff_or_a_board_row_leaves_the_floor_saying_fresh(tmp_path):
    # ⛔ Part 1 and part 2 meeting, at the level the floor prints. This is the
    # measured defect: a one-file docs-only merge reddened the tip.
    root, head = make_repository(tmp_path)
    write_index(root, head, BRIDGE_FLOOR)
    tasks = root / "docs" / "tasks"
    (tasks / "handoffs").mkdir(parents=True)
    (tasks / "handoffs" / "W39.md").write_text("# W39 — handoff\n", encoding="utf-8")
    (tasks / "BOARD.md").write_text("# board\n", encoding="utf-8")
    commit_all(root, "a round closes: a handoff and a board row")
    assert verdict(root) == FRESH
    assert check_knowledge_index(root) == []


# --- the finding's own shape ------------------------------------------------


def test_a_finding_points_at_a_repository_relative_path(tmp_path):
    # ⛔ R7: an absolute path in a build log carries the user's home directory.
    root, head = make_repository(tmp_path)
    write_index(root, head, 0)
    found = check_knowledge_index(root)
    assert found[0].path == "graphify-out/graph.json"
    assert not found[0].path.startswith("/")


def test_the_prefix_is_pinned_to_its_literal_and_not_merely_to_itself(tmp_path):
    # ⛔ `W39/5`, and it is a defect the first sweep found in these tests rather
    # than in the module: every assertion above builds its expected string from
    # `PREFIX`, so a mutant that renamed `PREFIX` renamed the expectation with
    # it and SURVIVED. ⭐ The rubric hard-codes `grep '^knowledge index: '`, so
    # the literal is a contract with a document and is pinned as one.
    assert PREFIX == "knowledge index: "
    root, head = make_repository(tmp_path)
    write_index(root, head, BRIDGE_FLOOR)
    assert notices(root)[0].startswith("knowledge index: fresh — ")
