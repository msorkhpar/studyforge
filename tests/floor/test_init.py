"""Mirror of `tests/floor/__init__.py`: the product floor's registry, and the floor over this tree.

⭐ **This is the product suite's wrapper.** `test_the_repository_is_on_the_product_floor` runs
every product check over the repository, so `pytest` alone fails on a finding — the same thing
the tooling's wrapper does for the tooling's floor, and the one that stays when the tooling goes.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import tests.floor as floor
from tests.floor import CHECKS, NOTICES, format_findings, run_all, run_notices
from tests.floor.docstrings import check_docstrings
from tests.floor.mirror import check_mirrors
from tests.floor.palettes import check_rejected_palettes
from tests.floor.personal_data import check_personal_data
from tests.floor.size import check_sizes
from tests.floor.source_names import check_source_names
from tests.floor.style import check_style
from tests.floor.surfaces import check_producer_half
from tests.support import assert_package_contract, repository_root

#: The package whose modules may import nothing but the standard library and each other.
FLOOR = Path(floor.__file__).parent


def test_states_its_contract():
    assert_package_contract(floor, "tests.floor")


def test_the_repository_is_on_the_product_floor():
    # ⛔ The wrapper. A finding here is a finding `python3 -m tests.floor` prints, with the
    #    same path, line and rule, so the message is the report itself.
    findings = run_all(repository_root())
    assert findings == [], format_findings(findings)


def test_the_registry_is_the_products_rules_and_nothing_else():
    # ⭐ R11, R12, R17, style, R7, R1, the producer half and the rejected palettes (§8.4).
    assert CHECKS == (
        check_sizes,
        check_mirrors,
        check_docstrings,
        check_style,
        check_personal_data,
        check_source_names,
        check_producer_half,
        check_rejected_palettes,
    )


def test_every_check_and_notice_takes_a_root_and_answers_in_its_own_channel(tmp_path):
    for check in CHECKS:
        assert isinstance(check(tmp_path), list), check.__name__
    for notice in NOTICES:
        assert all(isinstance(line, str) for line in notice(tmp_path)), notice.__name__
    assert run_all(tmp_path) == []
    assert all(isinstance(line, str) for line in run_notices(tmp_path))


def _imported_roots(path: Path) -> set[str]:
    """Every module a file imports, as the dotted name it names (relative imports excluded)."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            names.add(node.module)
    return names


def test_the_floor_imports_the_standard_library_and_itself_only():
    # ⛔ The floor must run on a clean checkout with no install and with no tooling beside
    #    it. ⚠️ Read as a parse, never a line scan: a docstring sentence starting "from" is
    #    not an import. The floor's own TESTS may use pytest and the suite's support module.
    modules = [path for path in FLOOR.rglob("*.py") if not path.name.startswith("test_")]
    assert modules, "the floor has no modules, so this assertion is vacuous"
    stray = {
        f"{path.relative_to(FLOOR)}: {name}"
        for path in modules
        for name in _imported_roots(path)
        if name.split(".")[0] not in sys.stdlib_module_names
        and not (name == "tests.floor" or name.startswith("tests.floor."))
    }
    assert stray == set()
