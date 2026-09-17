"""The bounded exception: directories permitted to carry personal-data shapes.

**What it does.** Checks that every directory in
`config.SANCTIONED_PERSONAL_DATA_DIRS` still exists and still declares itself
in a `VIOLATION.md` beside its data.

**How you use it.** `check_registry(repo_root)`. The registry itself lives in
`config`, so the list of exceptions is one place and the tests that bound it
read the same list.

**Depends on.** `config` and `pathlib`.

⚠️ **Why an exception exists at all.** A gate that refuses personal data needs
an input to refuse — SF-08's and SF-25's acceptance is a corpus that trips
them. ⛔ And the existence of that exception is exactly how a real leak gets
waved through, so it is bounded by tests rather than by a reviewer's memory
(rubric §1e): one directory, registered, self-declaring, asserted to be the
only one and asserted still to carry what it claims.
"""

from __future__ import annotations

from pathlib import Path

from tools.quality import config
from tools.quality.report import Finding

RULE_REGISTRY = "personal-data-registry"


def judged_directories(root: Path) -> list[str]:
    """Return the registered directories whose fixture area exists — this arm's population.

    ⚠️ Over a tree with no fixture area this is EMPTY and the arm compares nothing,
    which `vacuity` discloses (`W309`); it is never a finding, for the reason below.
    """
    return [
        directory
        for directory in config.SANCTIONED_PERSONAL_DATA_DIRS
        if (root / directory).parent.is_dir()
    ]


def check_registry(root: Path) -> list[Finding]:
    """Every registered negative-fixture directory exists and declares itself.

    Rubric §1e, condition 3: a sanctioned directory says what it is, in a file
    beside the data. ⛔ Without this the registry could name a directory that
    has quietly become an ordinary one, and the exemption would keep applying
    to whatever moved in.

    ⚠️ Judged only where the fixture area it names exists. The other four
    checks are properties of any tree; this one is a property of *this*
    repository's fixture tree, and a floor that reported "the negative fixture
    is missing" against every temporary directory would be a floor that cannot
    be run on anything but the real root.
    """
    findings: list[Finding] = []
    for directory in judged_directories(root):
        path = root / directory
        if not path.is_dir():
            findings.append(
                Finding(
                    path=directory,
                    line=0,
                    rule=RULE_REGISTRY,
                    message=(
                        "registered as a personal-data negative fixture but is not a "
                        "directory. Remove it from SANCTIONED_PERSONAL_DATA_DIRS."
                    ),
                )
            )
            continue
        if not (path / "VIOLATION.md").is_file():
            findings.append(
                Finding(
                    path=f"{directory}/VIOLATION.md",
                    line=0,
                    rule=RULE_REGISTRY,
                    message=(
                        "missing. A directory permitted to hold personal-data shapes "
                        "states the rule it violates and what the gate must say."
                    ),
                )
            )
    return findings
