"""`W309`: every check in `CHECKS` answers for the run where it compared NOTHING.

**What it does.** Two things, both about Ruling 191 — *an empty population is
never a pass*. `DISCLOSED_BY` pairs each check whose own notice ALREADY prints
its denominator with that notice, so the answer is a registered fact rather than
somebody's memory of a sweep. `POPULATIONS` names, for every check (or arm) that
had no such notice, the population it reads — and `vacuity_notice(root)` prints
ONE line naming each of those that is EMPTY on this tree, and nothing at all when
every one is inhabited.

**How you use it.** `vacuity_notice` is registered in `tools.quality.NOTICES`;
nothing else calls it. ⛔ Adding a check to `CHECKS` means answering for it in one
of the two tables here, and `tools/tests/quality/test_vacuity.py` fails until it
is.

**Depends on.** The check and notice modules it names, `collections.abc`, `dataclasses`
and `pathlib`.
⛔ It derives no population of its own: every `members` below is the SAME function
its check iterates, so the disclosure can never describe a different walk than
the verdict (`pointers.py`'s rule, and `W307`'s decision 2).

## ⛔ Why silence when inhabited, and one line when not

⚠️ **The floor's output is read by every agent at session start**, so a line per
check printed on every green run is a cost paid on every run for a condition that
is almost never true of this repository. ⭐ The condition this exists for — `0 = 0`
read as a clean bill (Ruling 48) — only arises over a tree where a population is
EMPTY, so that is the only run on which it speaks. ⛔ **A notice, never a finding**
(`W307`'s precedent): the floor runs over trees that are not this repository, and
an empty population there is CORRECT.

## ⚠️ What this does NOT claim

⭐ A check in `DISCLOSED_BY` is answered by its notice's own line, which prints
its denominator in every state; this module does not re-print it. ⛔ The pairing is
not the evidence — `test_vacuity.py` runs each notice over an empty tree and over
this repository and asserts the two readings differ.
"""

from __future__ import annotations

from collections.abc import Callable, Sized
from dataclasses import dataclass
from pathlib import Path

from tools.quality import config
from tools.quality.approach import approach_notice
from tools.quality.board import board_state, check_board
from tools.quality.clauses import check_clause_counts, clause_census
from tools.quality.collisions import check_anchor_collisions, collision_census
from tools.quality.counts import check_derived_counts, count_census
from tools.quality.creators import check_owns_before_creator, creator_census
from tools.quality.docstrings import check_docstrings, contract_modules
from tools.quality.handoffs import check_handoffs, handoff_citations
from tools.quality.handoffs.existence import check_handoff_existence, handoff_existence
from tools.quality.handoffs.sweep import (
    CONVENTIONS_DIR,
    check_marker_patterns,
    convention_documents,
)
from tools.quality.mirror import check_mirrors, mirrored
from tools.quality.personal_data import check_personal_data, identity_notice
from tools.quality.personal_data.registry import judged_directories
from tools.quality.personal_data.shapes import swept_files
from tools.quality.pointers import check_pointers, pointer_coverage
from tools.quality.reach import check_rulings_reach, reach_notice
from tools.quality.report import Finding
from tools.quality.rulings import check_rulings_index, rulings_notice
from tools.quality.size import check_sizes
from tools.quality.source_names import FRAMEWORK_ROOT, check_source_names, framework_modules
from tools.quality.style import check_style
from tools.quality.surfaces import check_producer_half, surface_census

Check = Callable[[Path], list[Finding]]
Notice = Callable[[Path], list[str]]

TAG = "vacuous checks (W309, Ruling 191):"

#: ⭐ Checks whose OWN notice prints the denominator in every state, the empty one
#: included. ⚠️ `check_personal_data` is here for its identifier arm's VALUES only
#: (`W307`); that arm's files, and its shapes and registry arms, are in `POPULATIONS`.
DISCLOSED_BY: tuple[tuple[Check, Notice], ...] = (
    (check_sizes, approach_notice),
    (check_board, board_state),
    (check_personal_data, identity_notice),
    (check_handoffs, handoff_citations),
    (check_handoff_existence, handoff_existence),
    (check_pointers, pointer_coverage),
    (check_anchor_collisions, collision_census),
    (check_rulings_index, rulings_notice),
    (check_rulings_reach, reach_notice),
    (check_clause_counts, clause_census),
    (check_derived_counts, count_census),
    (check_owns_before_creator, creator_census),
    (check_producer_half, surface_census),
)


@dataclass(frozen=True)
class Population:
    """What one check (or one arm of it) reads, named for a reader, and the reader itself."""

    check: Check
    arm: str
    noun: str
    members: Callable[[Path], Sized]

    def label(self) -> str:
        """Name the check, and the arm where the check has more than one."""
        name = self.check.__name__
        return f"{name} ({self.arm})" if self.arm else name


#: ⛔ Every check (or arm) that had NO line saying its population was empty before
#: `W309`. ⭐ Each `members` is the function its check iterates, never a restatement.
POPULATIONS: tuple[Population, ...] = (
    Population(
        check_mirrors,
        "",
        f"source modules under a mirrored root ({', '.join(s for s, _ in config.MIRRORS)})",
        mirrored,
    ),
    Population(check_docstrings, "", "non-test modules under the scan roots", contract_modules),
    Population(check_style, "", "Python files under the scan roots", config.python_files),
    Population(check_personal_data, "shapes arm", "text files swept", swept_files),
    # ⚠️ `identity_notice` discloses whether this arm had a VALUE to compare (`W307`), and
    # nothing about the FILES it compared against — that half is answered here.
    Population(check_personal_data, "identifier arm", "text files read", config.text_files),
    Population(
        check_personal_data,
        "registry arm",
        "registered negative-fixture directories whose fixture area exists",
        judged_directories,
    ),
    Population(check_source_names, "", f"modules under {FRAMEWORK_ROOT}/", framework_modules),
    Population(
        check_marker_patterns, "", f"documents under {CONVENTIONS_DIR}/", convention_documents
    ),
)


def vacuity_notice(root: Path) -> list[str]:
    """Return one line naming every population in `POPULATIONS` that is EMPTY, or nothing.

    ⛔ Nothing at all when every one is inhabited — the row forbids a disclosure
    printed on every green run — and never a finding, whatever it says.
    """
    empty = [population for population in POPULATIONS if not len(population.members(root))]
    if not empty:
        return []
    named = "; ".join(f"{population.label()} read 0 {population.noun}" for population in empty)
    return [
        f"{TAG} these compared NOTHING on this tree, so their clean verdict is 0 = 0 and "
        f"not a clean bill (Ruling 48) — {named}. This is not a failure: the floor runs "
        f"over trees that are not this repository."
    ]


__all__ = ["DISCLOSED_BY", "POPULATIONS", "TAG", "Population", "vacuity_notice"]
