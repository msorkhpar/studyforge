"""Mirror of `src/studyforge/execute/__init__.py` (R12)."""

from __future__ import annotations

import ast
from pathlib import Path

from studyforge import execute
from tests.support import assert_package_contract

PACKAGE = Path(execute.__file__).parent


def test_states_its_contract():
    assert_package_contract(execute, "studyforge.execute")


def test_every_exported_name_resolves():
    assert all(hasattr(execute, name) for name in execute.__all__)


def imported_packages(path: Path) -> set[str]:
    found = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
        elif isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
    return found


def test_the_package_never_depends_on_serve():
    """The direction is serve-depends-on-execute; the other way is the socket in the server."""
    for path in PACKAGE.glob("*.py"):
        assert not any(name.startswith("studyforge.serve") for name in imported_packages(path)), (
            path.name
        )


def test_the_dependency_reader_sees_an_import():
    """The other way: the reader above is not blind to the framework's own imports."""
    assert "studyforge.archive.scrub" in imported_packages(PACKAGE / "output.py")
