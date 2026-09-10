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

import ast
import json
import re
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


def git() -> str:
    """The absolute path to git, or a failed assertion saying why it matters.

    ⛔ Asserted rather than skipped. The checks that use it — the ignore rules
    that keep FND-04's golden fixtures trackable, and FND-02's index rules —
    guard states whose failure is *silent* on a fresh clone. A skip there would
    look green and guard nothing.
    """
    tool = shutil.which("git")
    assert tool is not None, "git is not installed; this test cannot answer"
    return tool


def init_repository(path: Path) -> Path:
    """`git init` a throwaway repository at `path` and return it.

    For tests that need git to answer a question about a tree — which ignore
    rules apply, what is ignored — rather than about this repository.

    ⛔ No commit is made and no identity is configured. Nothing here needs an
    author, and configuring one would mean writing a name into a test.
    """
    path.mkdir(parents=True, exist_ok=True)
    result = run([git(), "init", "-q"], cwd=path)
    assert result.returncode == 0, result.stdout + result.stderr
    return path


def is_ignored(path: str, cwd: Path | None = None) -> bool:
    """Whether git, run in `cwd`, would ignore `path`. The path need not exist.

    `git check-ignore -q` exits 0 when the path is ignored and 1 when it is
    not; ⛔ anything else is git failing rather than answering, and is raised
    rather than read as a verdict — "not ignored" and "git could not tell you"
    must never arrive as the same answer.

    ⭐ One definition, per this file's own rule. It was written twice —
    `tests/test_repository.py` had it first and `tests/test_knowledge_index.py`
    copied it, because FND-02 was told not to touch the file that already had
    it and recorded the duplication as a finding rather than reaching outside
    its task. Consolidated here by FND-06, which owns both callers.

    ⚠️ `cwd` defaults to this repository and is a parameter because FND-02 asks
    the same question of *sibling* repositories, where the answer is about
    their ignore rules and not ours.
    """
    where = repository_root() if cwd is None else cwd
    result = run([git(), "check-ignore", "-q", "--no-index", path], cwd=where)
    assert result.returncode in (0, 1), (
        f"git check-ignore failed on {path!r} in {where.name}: {result.stdout + result.stderr}"
    )
    return result.returncode == 0


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


def imports_module(path: Path, module: str) -> bool:
    """Does the Python file at `path` take something from `module` by name?

    ⛔ **The one spelling of "does this module go to the owner?"**, and it was
    written by hand twice before it was extracted (W13): `test_version.py`'s
    `imports_the_guard` and `test_blocks.py`'s `imports_the_vocabulary` are the
    same eleven lines with a different constant, and the fixture checker was
    about to be the third. ⚠️ This file's own contract says a block repeated
    between test files is extracted and imported; two copies is where that
    starts, not where it becomes urgent.

    ⭐ **Equality, not a prefix, and not a re-export chain.** A module deriving
    from the one source of truth says where it got it — `studyforge.version`
    matches, `studyforge` does not, and neither does a name re-exported through
    a package `__init__`.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == module:
            return True
        if isinstance(node, ast.Import) and any(alias.name == module for alias in node.names):
            return True
    return False


#: Ruling 47's shared evidence: the one table both personal-data gates are
#: measured against. ⛔ Shared as **data**, never as code — `tools/quality` may
#: not import the framework (Ruling 31), so the two sides read this file and
#: each asserts only its own column.
SHAPE_VOCABULARY = "docs/conventions/personal-data-shapes.md"


def personal_data_shapes() -> list[dict]:
    """Every row of the shared shape vocabulary, with `spelling` joined.

    ⚠️ `spelling` is stored as fragments and joined here: a real personal-data
    shape written whole into that document would be a finding against it, by
    the sweep its own last column describes.
    """
    text = (repository_root() / SHAPE_VOCABULARY).read_text(encoding="utf-8")
    match = re.search(r"```json\n(.*?)\n```", text, re.S)
    if match is None:  # pragma: no cover - the document without its table
        raise AssertionError(f"{SHAPE_VOCABULARY} carries no ```json table")
    rows = json.loads(match.group(1))
    for row in rows:
        row["example"] = "".join(row["spelling"])
    return rows


def shapes_agree(row: dict) -> bool:
    """Do all three columns of `row` say the same thing?

    ⭐ The rule the table enforces: a row whose columns disagree must carry a
    `why`, so a divergence is declared with a reason rather than discovered.
    """
    return (row["gate"] == "refuse") == (row["scrub"] == "rewrite") == (row["quality"] == "report")
