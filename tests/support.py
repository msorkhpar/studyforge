"""Helpers shared between test modules. Imported, never copied.

⛔ The rule that puts this file here, carried from the extraction source: **if a
block is repeated between test files, extract it and import it.** Fifteen
copies of "does this package state its contract" is fifteen places to forget
when R17's shape changes, and the copies drift silently because each one keeps
passing.

Imported as `from tests.support import ...` — `pythonpath = ["src", "."]` in
`pyproject.toml` makes that work with no install and no `__init__.py`.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from types import ModuleType

#: R17's three parts, as the §3.2 packages spell them. A package that fills in
#: its implementation keeps them; a reader who has not seen the spec must be
#: able to use the package from its docstring alone, and these are the three
#: questions they will have.
CONTRACT_PARTS = ("What it does", "How you use it", "Depends on")

#: A contract shorter than this is a label. Higher than the repository-wide
#: floor in `tools.quality.config`, because that floor applies to every module
#: and this applies only to the packages spec §3.2 names, which are the ones a
#: consumer meets first.
MIN_CONTRACT_CHARS = 200


def repository_root() -> Path:
    """The repository root, found from this file rather than from the cwd.

    ⛔ Never `Path.cwd()`: a test that passes only when pytest was started from
    one directory is a test that fails for the next person for a reason that
    has nothing to do with the code.
    """
    return Path(__file__).resolve().parent.parent


def assert_package_contract(module: ModuleType, expected_name: str) -> None:
    """Assert `module` is the named package and states its contract (R17)."""
    assert module.__name__ == expected_name, (
        f"imported {module.__name__!r}, expected {expected_name!r}"
    )
    docstring = (module.__doc__ or "").strip()
    assert docstring, f"{expected_name} states no contract; R17 requires one"
    assert len(docstring) >= MIN_CONTRACT_CHARS, (
        f"{expected_name}'s contract is {len(docstring)} characters; "
        f"R17 wants a contract, not a label"
    )
    for part in CONTRACT_PARTS:
        assert part in docstring, f"{expected_name}'s contract does not say {part!r}"


def tool_on_path(name: str) -> str | None:
    """The absolute path to `name`, or None when it is not installed.

    Used by the optional-tool tests, which skip with a message naming the
    extra that would install the tool rather than passing quietly.
    """
    return shutil.which(name)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run `command` in `cwd` and capture both streams as text.

    ⛔ Never `shell=True`, and never an absolute path built from the
    environment: a captured command line ends up in a failure message, and a
    home directory in a failure message is personal data (R7).
    """
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
