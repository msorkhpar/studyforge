"""Every product check answers for the run where it compared NOTHING.

**What it does.** An empty population is never a pass: a check that read no files prints the
same clean line as one that read every file and found nothing. `DISCLOSED_BY` pairs each check
whose own notice already prints its denominator with that notice; `POPULATIONS` names, for
every other check (or arm), the population it reads — and `vacuity_notice(root)` prints ONE
line naming each of those that is EMPTY on this tree, and nothing when every one is inhabited.

**How you use it.** `vacuity_notice` is registered in `tests.floor.NOTICES`. ⛔ Adding a check
to `tests.floor.CHECKS` means answering for it in one of the two tables here, and
`tests/floor/test_vacuity.py` fails until it is.

**Depends on.** The check modules it names, `collections.abc`, `dataclasses` and `pathlib`.
⛔ It derives no population of its own: every `members` below is the SAME function its check
iterates, so the disclosure can never describe a different walk than the verdict.

⭐ **The product's own registry, shaped as the tooling's.** The tooling's `vacuity` answers for
every check the tooling runs, process checks included; this one answers for the product's
checks only, with the same populations, so it is written here rather than copied.
"""

from __future__ import annotations

from collections.abc import Callable, Sized
from dataclasses import dataclass
from pathlib import Path

from tests.floor import config
from tests.floor.docstrings import check_docstrings, contract_modules
from tests.floor.mirror import check_mirrors, mirrored
from tests.floor.personal_data import check_personal_data, identity_notice
from tests.floor.personal_data.registry import judged_directories
from tests.floor.personal_data.shapes import swept_files
from tests.floor.report import Finding
from tests.floor.size import check_sizes
from tests.floor.source_names import FRAMEWORK_ROOT, check_source_names, framework_modules
from tests.floor.style import check_style
from tests.floor.surfaces import check_producer_half, surface_census

Check = Callable[[Path], list[Finding]]
Notice = Callable[[Path], list[str]]

TAG = "vacuous checks (Ruling 191):"

#: ⭐ Checks whose OWN notice prints the denominator in every state, the empty one included.
#: ⚠️ `check_personal_data` is here for its identifier arm's VALUES only; that arm's files,
#: and its shapes and registry arms, are in `POPULATIONS`.
DISCLOSED_BY: tuple[tuple[Check, Notice], ...] = (
    (check_personal_data, identity_notice),
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


#: ⛔ Every product check (or arm) with no notice of its own. ⭐ Each `members` is the
#: function its check iterates, never a restatement. ⚠️ `check_sizes` is here and not in
#: `DISCLOSED_BY`: the tooling pairs it with its approach notice, which reads offices and
#: branches and stays with the tooling.
POPULATIONS: tuple[Population, ...] = (
    Population(check_sizes, "", "Python files under the scan roots", config.python_files),
    Population(
        check_mirrors,
        "",
        f"source modules under a mirrored root ({', '.join(s for s, _ in config.MIRRORS)})",
        mirrored,
    ),
    Population(check_docstrings, "", "non-test modules under the scan roots", contract_modules),
    Population(check_style, "", "Python files under the scan roots", config.python_files),
    Population(check_personal_data, "shapes arm", "text files swept", swept_files),
    Population(check_personal_data, "identifier arm", "text files read", config.text_files),
    Population(
        check_personal_data,
        "registry arm",
        "registered negative-fixture directories whose fixture area exists",
        judged_directories,
    ),
    Population(check_source_names, "", f"modules under {FRAMEWORK_ROOT}/", framework_modules),
)


def vacuity_notice(root: Path) -> list[str]:
    """Return one line naming every population in `POPULATIONS` that is EMPTY, or nothing.

    ⛔ Nothing at all when every one is inhabited, and never a finding, whatever it says: the
    floor runs over trees that are not this repository, and an empty population there is
    correct.
    """
    empty = [population for population in POPULATIONS if not len(population.members(root))]
    if not empty:
        return []
    named = "; ".join(f"{population.label()} read 0 {population.noun}" for population in empty)
    return [
        f"{TAG} these compared NOTHING on this tree, so their clean verdict is 0 = 0 and "
        f"not a clean bill — {named}. This is not a failure: the floor runs over trees that "
        f"are not this repository."
    ]


__all__ = ["DISCLOSED_BY", "POPULATIONS", "TAG", "Population", "vacuity_notice"]
