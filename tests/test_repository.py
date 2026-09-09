"""The repository's own acceptance: what it declares, and what it actually imports.

Not a mirror of any source module — it is about the tree as a whole, which is
why it sits at the top of `tests/` rather than under `tests/studyforge/`. The
size, mirror, contract and style floor is next door in
`tests/test_quality_floor.py`; what lives here is dependency policy and the
optional tooling.
"""

from __future__ import annotations

import ast
import sys
import tomllib

import pytest

from tests.support import repository_root, run, tool_on_path
from tools.quality.config import python_files, relative


def pyproject() -> dict:
    """`pyproject.toml`, parsed."""
    return tomllib.loads((repository_root() / "pyproject.toml").read_text("utf-8"))


# --- dependencies ----------------------------------------------------------


def test_no_runtime_dependencies():
    # ⛔ Standard library only in framework source. A runtime dependency is a
    # design change — it is also what would make R15's exemption for the
    # serving process stop being true, since a process with dependencies does
    # gain reproducibility from an image.
    assert pyproject()["project"]["dependencies"] == []


def test_optional_dependencies_are_tooling_only():
    extras = pyproject()["project"]["optional-dependencies"]
    assert set(extras) == {"test", "lint"}


def test_no_source_module_imports_a_third_party_package():
    # The declaration above says what is allowed; this says what is actually
    # imported, which is the half that goes wrong silently.
    root = repository_root()
    allowed = set(sys.stdlib_module_names) | {"studyforge"}
    offenders: list[str] = []
    for path in python_files(root):
        name = relative(path, root)
        if not name.startswith("src/"):
            continue
        tree = ast.parse(path.read_text("utf-8"), filename=name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                roots = [(node.module or "").split(".")[0]] if node.level == 0 else []
            else:
                continue
            offenders += [f"{name}: {root_name}" for root_name in roots if root_name not in allowed]
    assert offenders == []


def test_the_quality_tooling_is_excluded_from_packaging():
    # ⛔ `tools/` is developer tooling, not shipped API. Packaging looks only
    # in `src`, so an installed `studyforge` contains no `tools` package —
    # which is the other half of the ruling that kept the size checker out of
    # `src/studyforge/`.
    assert pyproject()["tool"]["setuptools"]["packages"]["find"]["where"] == ["src"]
    assert not (repository_root() / "src" / "tools").exists()


# --- optional tooling ------------------------------------------------------


def test_ruff_lint_is_clean_where_ruff_exists():
    # ⚠️ Ruff is not installed in the environment this was built in and no
    # network install is assumed, so this skips with a message that names the
    # extra rather than passing quietly. Where ruff is present — FND-03's
    # image is the obvious place — it runs for real.
    ruff = tool_on_path("ruff")
    if ruff is None:
        pytest.skip("ruff not installed; `pip install -e '.[lint]'` to enable this check")
    result = run([ruff, "check", "."], cwd=repository_root())
    assert result.returncode == 0, result.stdout + result.stderr


def test_ruff_format_is_clean_where_ruff_exists():
    ruff = tool_on_path("ruff")
    if ruff is None:
        pytest.skip("ruff not installed; `pip install -e '.[lint]'` to enable this check")
    result = run([ruff, "format", "--check", "."], cwd=repository_root())
    assert result.returncode == 0, result.stdout + result.stderr
