"""The golden floor: R10 as a build failure, over every golden in the tree at once.

⛔ **Not a fourth comparison of the same files.** Each renderer already compares
its own goldens where its own tests live. What fails here is the shape between
them — the census, the orphan, the collision — plus one place a reader can count
the total, which is what makes `SF-30`'s assertions checkable against something
other than a harness's own concatenation.
"""

from __future__ import annotations

import pytest

from tests.harness import goldens
from tests.harness.goldens import Golden

#: A floor on **coverage**, not a count. ⚠️ Measured 2026-09-10 at `5e608bfc`:
#: 10 goldens — 7 rendered pages and 3 plans. ⛔ A lower bound rather than an
#: equality, so adding a golden is not a failing test; it can only break by the
#: census reaching LESS than it does today, which is the failure that matters.
LEAST_GOLDENS = 10

#: How many writers claim them. ⭐ Four: three regenerators and the plan CLI.
LEAST_WRITERS = 4

#: The census, built once at collection. ⚠️ Parametrised by `writer:case` and not
#: by case alone — the index regenerator and the plan CLI both have a case called
#: `depth1`, so a case name is not an identifier and a test id built from one
#: would silently run one subject twice under two numbers.
_CLAIMED = goldens.claimed()
_IDS = [f"{golden.writer.rsplit('.', 1)[-1]}:{golden.case}" for golden in _CLAIMED]


@pytest.fixture(scope="module")
def claimed():
    return _CLAIMED


def test_the_census_is_inhabited_and_says_what_it_reached(claimed):
    # ⛔ Ruling 191: print the population before any verdict. A census that
    # reached nothing reports no mismatches, and no mismatches is what a clean
    # tree reports — so the size is asserted before anything is asserted about
    # the contents.
    for golden in claimed:
        print(f"{golden.writer}  {golden.case}  {golden.path.name}")
    writers = {golden.writer for golden in claimed}
    print(f"goldens {len(claimed)} claimed by {len(writers)} writers")
    assert len(claimed) >= LEAST_GOLDENS
    assert len(writers) >= LEAST_WRITERS


@pytest.mark.parametrize("golden", _CLAIMED, ids=_IDS)
def test_every_golden_is_byte_for_byte_what_the_tree_produces(golden):
    # ⛔ SF-26's first acceptance clause, and R10. One subject per test, so a
    # failure names one case and its module rather than "the goldens".
    assert goldens.mismatches((golden,)) == []


def test_no_committed_golden_is_claimed_by_nobody(claimed):
    # ⚠️ An orphan is green forever: it is compared against nothing, so it is
    # evidence of nothing, and it outlives the renderer that wrote it.
    print(f"committed {len(goldens.committed())}, claimed {len(claimed)}")
    assert goldens.orphans() == []


def test_no_two_cases_claim_one_golden(claimed):
    # ⛔ Ruling 187. "Every case has a golden" and "every golden has a case" are
    # both satisfied by a collision, which pins only whichever case writes last
    # — surjectivity, asserted twice, is still not injectivity.
    print(f"distinct paths {len({golden.path for golden in claimed})} of {len(claimed)} cases")
    assert goldens.collisions() == []


def test_producing_the_same_golden_twice_agrees(claimed):
    # ⛔ R10 from the other end: no clock, no filesystem enumeration order, no
    # set iteration. The byte comparison above would pass a renderer that was
    # stable only within one call.
    for golden in claimed:
        assert golden.emit() == golden.emit(), f"{golden.writer}: {golden.case} is not stable"


# --------------------------------------------------------------------------
# ⛔ the instrument's own three readings
# --------------------------------------------------------------------------


def test_the_comparison_catches_one_moved_byte_and_names_the_module(tmp_path):
    # ⛔ The planted reading, adversarial to the SEARCH TERM: one byte, in the
    # middle, of a file that is otherwise the real golden.
    real = goldens.claimed()[0]
    was = real.path.read_bytes()
    moved = tmp_path / real.path.name
    moved.write_bytes(was[:20] + bytes([was[20] ^ 0x20]) + was[21:])
    reported = goldens.mismatches((Golden(moved, real.writer, real.case, real.emit),))
    print(reported)
    assert len(reported) == 1
    assert real.writer in reported[0], "a failure must name the module, not the subsystem"
    assert "differs at byte 20" in reported[0]
    assert f"python3 -m {real.writer}" in reported[0]


def test_the_comparison_tells_a_missing_golden_from_a_changed_one(tmp_path):
    # ⛔ The impossible reading: a golden that cannot match because it is not
    # there. ⭐ Its message must DIFFER from the pass AND from the planted one —
    # the remedies are different (commit it, versus regenerate it), and a check
    # that reported both as "differs" would send a reader to the wrong one.
    real = goldens.claimed()[0]
    absent = Golden(tmp_path / "nothing.unit.html", real.writer, real.case, real.emit)
    reported = goldens.mismatches((absent,))
    print(reported)
    assert len(reported) == 1
    assert "is not committed" in reported[0]
    assert "differs at byte" not in reported[0]


def test_the_comparison_is_silent_on_a_golden_that_matches(tmp_path):
    # ⚠️ The other half of the planted reading: the same machinery, the same
    # file, unmodified — so the reading above is attributable to the one byte
    # and not to the copy, the tmp directory or the path.
    real = goldens.claimed()[0]
    copy = tmp_path / real.path.name
    copy.write_bytes(real.path.read_bytes())
    assert goldens.mismatches((Golden(copy, real.writer, real.case, real.emit),)) == []
