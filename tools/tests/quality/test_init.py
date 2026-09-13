"""Mirror of `tools/quality/__init__.py` (R12)."""

from __future__ import annotations

import tools.quality as quality
from tests.support import assert_package_contract, repository_root
from tools.quality import run_all
from tools.quality.approach import approach_notice
from tools.quality.board import board_state, check_board
from tools.quality.clauses import check_clause_counts, clause_census
from tools.quality.collisions import check_anchor_collisions, collision_census
from tools.quality.counts import check_derived_counts, count_census
from tools.quality.creators import check_owns_before_creator, creator_census
from tools.quality.docstrings import check_docstrings
from tools.quality.handoffs import check_handoffs, handoff_citations
from tools.quality.handoffs.existence import check_handoff_existence, handoff_existence
from tools.quality.handoffs.sweep import check_marker_patterns
from tools.quality.lint import lint_notice
from tools.quality.locations import location_notice
from tools.quality.mirror import check_mirrors
from tools.quality.personal_data import check_personal_data
from tools.quality.pointers import check_pointers, pointer_coverage
from tools.quality.reach import check_rulings_reach, reach_notice
from tools.quality.rulings import check_rulings_index, rulings_notice
from tools.quality.size import check_sizes
from tools.quality.source_names import check_source_names
from tools.quality.style import check_style


def test_states_its_contract():
    assert_package_contract(quality, "tools.quality")


def test_every_check_is_registered():
    # ⛔ A check that exists but is not in `CHECKS` runs in its own tests and
    # nowhere else, which is the most expensive kind of passing test.
    assert set(quality.CHECKS) == {
        check_sizes,
        check_board,
        check_mirrors,
        check_docstrings,
        check_style,
        check_personal_data,
        check_source_names,
        check_handoffs,
        check_handoff_existence,
        check_marker_patterns,
        check_pointers,
        check_anchor_collisions,
        check_rulings_index,
        check_rulings_reach,
        check_clause_counts,
        check_derived_counts,
        check_owns_before_creator,
    }
    assert quality.CHECKS, "Ruling 48: an empty registry satisfies set() == set()"


def test_every_notice_is_registered():
    # ⛔ The second channel needs the same guard as the first, and for a
    # sharper reason: a notice that is not registered prints nowhere, and
    # "nothing was printed" is indistinguishable from "there was nothing to
    # say" (FND-07, and `agent-protocol.md`'s coverage rule).
    assert set(quality.NOTICES) == {
        approach_notice,
        pointer_coverage,
        collision_census,
        location_notice,
        board_state,
        handoff_existence,
        handoff_citations,
        rulings_notice,
        reach_notice,
        clause_census,
        count_census,
        creator_census,
        lint_notice,
    }


def test_the_size_approach_prints_first():
    # ⛔ Order, not just membership, and it mirrors `check_sizes` being first in
    # `CHECKS`: the ceiling's finding and the ceiling's approach are read by the
    # same reader in the same order (`W155`).
    assert quality.NOTICES[0] is approach_notice


def test_the_collision_census_prints_directly_under_the_pointer_census():
    # ⛔ Order, not just membership, and for `W140`'s reason: the line this
    # qualifies is `document pointers: … 0 unresolved`, which is TRUE and reads
    # as *no anchor in this tree is ambiguous*. A census three lines below a
    # figure it corrects is a census the reader has already moved past.
    assert quality.NOTICES.index(collision_census) == quality.NOTICES.index(pointer_coverage) + 1


def test_the_lint_notice_prints_last():
    # ⛔ Order, not just membership. Ruling 78's notice qualifies exactly one
    # line — `quality floor:` — and a reader who finds it three lines above
    # that, under a pointer census, has to be told the two are related.
    assert quality.NOTICES[-1] is lint_notice


def test_the_lint_notice_cannot_change_the_exit_code(tmp_path):
    # ⛔ Ruling 78's hard half: a NOTICE, never a check. `run_all` is what
    # `__main__` turns into an exit code, and nothing registered in `NOTICES`
    # may appear in it — otherwise the floor's verdict would start depending on
    # whether somebody ran `pip install`, which Ruling 77 forbids.
    assert lint_notice not in quality.CHECKS
    assert run_all(tmp_path) == []
    assert [line for line in quality.run_notices(tmp_path) if line.startswith("lint:")]


def test_the_public_surface_is_what_consumers_import():
    for name in quality.__all__:
        assert hasattr(quality, name), name


def test_run_all_collects_from_every_check(tmp_path):
    source = tmp_path / "src" / "studyforge" / "wrong.py"
    source.parent.mkdir(parents=True)
    # No docstring (contract), no mirrored test (mirror), and a long line.
    source.write_text("v = '" + "x" * quality.LINE_LENGTH + "'\n", encoding="utf-8")
    assert {finding.rule for finding in run_all(tmp_path)} == {
        "contract",
        "mirror",
        "line-length",
    }


def test_run_all_is_sorted_over_the_real_tree():
    findings = run_all(repository_root())
    assert findings == sorted(findings)
