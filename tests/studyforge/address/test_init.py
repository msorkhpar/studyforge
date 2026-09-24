"""Mirror of `src/studyforge/address/__init__.py` (R12).

What lives here is the package as a whole: its contract, its public surface,
and the one property the package's acceptance states negatively — that it knows
nothing about files.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from studyforge import address
from tests.support import assert_package_contract

#: Modules that would let this package touch a filesystem. ⛔ The check is on
#: the import, not on a call, because an import is what makes the capability
#: reachable at all — and because a test that looked for `open(` would pass a
#: module that imported `pathlib` and used it next week.
#: ⚠️ Exactly the filesystem ones, so the constant's name is true. `sys` and
#: `io` are not here and are not missing: the allowlist test below is strictly
#: stronger and refuses them along with everything else.
FILESYSTEM_MODULES = frozenset(
    {"pathlib", "os", "shutil", "glob", "tempfile", "fileinput", "zipfile", "sqlite3"}
)

#: The whole public surface, spelled out. ⚠️ Duplicated from `__all__` on
#: purpose: a test that read `__all__` and then asserted the names in it exist
#: would pass whatever the module happened to export, which is not a contract.
PUBLIC_SURFACE = frozenset(
    {
        "DIGIT_PREFIX",
        "FIRST_ORDINAL",
        "SEPARATOR",
        "Address",
        "AddressError",
        "identifier",
        "is_slug",
        "parse_key",
        "parse_unit_key",
        "require_ordinal",
        "require_slug",
        "slugify",
        "unit_name",
    }
)


def package_modules() -> list[Path]:
    """Every source module in the package, including `__init__`."""
    root = Path(address.__file__).parent
    return sorted(root.glob("*.py"))


def imported_names(path: Path) -> set[str]:
    """Every module name `path` imports, top-level or inside a function."""
    tree = ast.parse(path.read_text("utf-8"), filename=path.name)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module)
    return names


def test_states_its_contract():
    assert_package_contract(address, "studyforge.address")


def test_no_filesystem_import_anywhere_in_the_package():
    # The package's acceptance, stated negatively because that is how R1 and R4 are
    # stated: an address is an identity, and where it lives is somebody else's
    # answer. A single `from pathlib import Path` here would make it this
    # package's answer instead, and nothing downstream would notice.
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        for name in sorted(imported_names(path))
        if name.split(".")[0] in FILESYSTEM_MODULES
    ]
    assert offenders == [], "the address model reaches the filesystem: " + ", ".join(offenders)


def test_the_package_imports_nothing_outside_the_standard_library_and_itself():
    allowed_roots = {"studyforge", "dataclasses", "re", "__future__"}
    offenders = [
        f"{path.name}: {name}"
        for path in package_modules()
        for name in sorted(imported_names(path))
        if name.split(".")[0] not in allowed_roots
    ]
    assert offenders == [], "unexpected import: " + ", ".join(offenders)


def test_the_public_surface_is_exactly_what_the_contract_says():
    assert set(address.__all__) == PUBLIC_SURFACE
    missing = sorted(name for name in PUBLIC_SURFACE if not hasattr(address, name))
    assert missing == [], "exported but absent: " + ", ".join(missing)


@pytest.mark.parametrize("name", sorted(PUBLIC_SURFACE))
def test_every_exported_name_is_reachable_from_the_package(name):
    # ⛔ The point of `__init__.py` being the contract: nothing downstream
    # should ever need `from studyforge.address.address import ...`.
    assert getattr(address, name) is not None
