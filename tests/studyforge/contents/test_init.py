"""Mirror of `src/studyforge/contents/__init__.py` (R12)."""

from __future__ import annotations

import inspect
import pkgutil

from studyforge import contents
from tests.support import assert_package_contract

#: The modules this package is made of. ⛔ Stated, so a new one arriving
#: without a line on the contract's table is a failure rather than a surprise.
MODULES = ("document", "entries", "errors", "order", "status", "tree", "writing")


def test_states_its_contract():
    assert_package_contract(contents, "studyforge.contents")


def test_every_exported_name_is_really_there():
    missing = [name for name in contents.__all__ if not hasattr(contents, name)]
    assert missing == []


def test_the_surface_is_the_whole_surface():
    # ⛔ `__init__.py` is the contract: a consumer that has to import
    # `studyforge.contents.order` directly is a consumer this contract failed.
    # ⚠️ Submodules are excluded by asking what the name *is*, never by name:
    # `order` and `status` are both a module of this package and a function on
    # its surface, so a name-based filter would drop two real exports.
    public = {
        name
        for name, value in vars(contents).items()
        if not name.startswith("_") and name != "annotations" and not inspect.ismodule(value)
    }
    assert public == set(contents.__all__)


def test_the_package_is_the_modules_it_says_it_is():
    found = tuple(sorted(info.name for info in pkgutil.iter_modules(contents.__path__)))
    assert found == tuple(sorted(MODULES))


def test_the_contract_names_every_module_it_is_made_of():
    # ⭐ The docstring carries a table of what is in the package; a module with
    # no row in it is a module the next reader has to find by listing files.
    for module in MODULES:
        assert f"`{module}`" in contents.__doc__
