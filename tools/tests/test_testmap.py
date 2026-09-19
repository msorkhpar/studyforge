"""Mirror of `tools/testmap.py` (R12): the import map, asserted in both directions (`W366`).

⭐ Every tree here is a throwaway in `tmp_path`, laid out like this repository — `src/`,
`tools/`, `tests/` — so the map is measured against real files and never against its own
idea of them. One assertion reads the real tree, and only to show the population is inhabited.
"""

from __future__ import annotations

import ast
from pathlib import Path

import tools.testmap as testmap_module
from tests.support import assert_package_contract, repository_root
from tools.testmap import TestMap, imports, is_conftest, is_test_file, module_of


def _write(root: Path, files: dict[str, str]) -> Path:
    for relative, text in files.items():
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text(text, encoding="utf-8")
    return root


def _imports(source: str, module: str = "tests.test_x", known=frozenset()) -> set[str]:
    return imports(ast.parse(source), module, False, frozenset(known))


def test_states_its_contract():
    assert_package_contract(testmap_module, "tools.testmap")


# --- names ------------------------------------------------------------------------------


def test_a_path_names_its_module_and_src_is_dropped():
    assert module_of("src/studyforge/render/page/rail.py") == "studyforge.render.page.rail"
    assert module_of("src/studyforge/render/__init__.py") == "studyforge.render"
    assert module_of("tools/gates.py") == "tools.gates"
    assert module_of("tests/support.py") == "tests.support"


def test_a_path_that_is_NOT_a_module_names_none():
    for path in ("docs/x.md", "docker/dev/check", "conftest.py", "tests/fixtures/a/b.py"):
        assert module_of(path) == "", path


def test_a_test_file_is_what_pytest_collects_and_nothing_else():
    assert is_test_file("tests/test_repository.py")
    assert is_test_file("tools/tests/quality/test_size.py")
    assert not is_test_file("tests/support.py")
    assert not is_test_file("src/studyforge/test_like.py")
    assert is_conftest("tests/visual/conftest.py") and not is_conftest("tests/test_conftest.py")


# --- what counts as an import -----------------------------------------------------------


def test_importing_a_submodule_imports_EVERY_PARENT_package():
    assert _imports("import studyforge.render.page") == {
        "studyforge",
        "studyforge.render",
        "studyforge.render.page",
    }


def test_from_import_names_the_submodule_only_when_it_IS_one():
    known = {"studyforge.render", "studyforge.render.page"}
    found = _imports("from studyforge.render import page, CONSTANT", known=known)
    assert "studyforge.render.page" in found
    assert "studyforge.render.CONSTANT" not in found


def test_a_RELATIVE_import_resolves_against_its_package():
    tree = ast.parse("from . import sibling\nfrom ..up import thing\n")
    known = frozenset({"tools.a.sibling", "tools.up", "tools.up.thing"})
    found = imports(tree, "tools.a.here", False, known)
    assert {"tools.a", "tools.a.sibling", "tools.up", "tools.up.thing"} <= found


def test_a_DOTTED_STRING_naming_a_module_is_an_import_and_an_unrelated_one_is_not():
    known = {"tools.quality", "tools"}
    assert "tools.quality" in _imports('RUN = ["python3", "-m", "tools.quality"]', known=known)
    assert _imports('RUN = "tools.qualityx"', known=known) == set()


def test_a_BARE_package_name_in_prose_is_not_an_import_outside_a_test():
    known = {"studyforge"}
    assert _imports('SAY = "studyforge"', "tools.x", known) == set()
    assert _imports('RUN = ["-m", "studyforge"]', "tests.test_cli", known) == {"studyforge"}


def test_an_F_STRING_under_a_package_reaches_every_module_beneath_it():
    known = {"studyforge.cli", "studyforge.cli.plan", "studyforge.render"}
    found = _imports('mod = f"studyforge.cli.{name}"', known=known)
    assert "studyforge.cli.plan" in found and "studyforge.render" not in found


def test_a_name_that_no_longer_RESOLVES_is_kept_when_it_is_local():
    # ⛔ A test importing a module the branch DELETED is exactly the test that must run.
    assert "studyforge.gone" in _imports("import studyforge.gone")
    assert _imports("import json.decoder") == set()


# --- the map ----------------------------------------------------------------------------

TREE = {
    "src/pkg/__init__.py": "",
    "src/pkg/low.py": "VALUE = 1\n",
    "src/pkg/mid.py": "from pkg.low import VALUE\n",
    "src/pkg/alone.py": "OTHER = 2\n",
    "tests/helper.py": "from pkg import mid\n",
    "tests/test_direct.py": "from pkg.low import VALUE\n",
    "tests/test_through_a_helper.py": "from tests.helper import mid\n",
    "tests/test_unrelated.py": "from pkg.alone import OTHER\n",
    "tests/fixtures/corpus/code.py": "import pkg.low\n",
}


def test_dependents_are_TRANSITIVE_through_modules_and_helpers(tmp_path):
    graph = TestMap.build(_write(tmp_path, TREE))
    assert graph.dependents({"pkg.low"}) == {
        "tests/test_direct.py",
        "tests/test_through_a_helper.py",
    }


def test_a_module_nothing_imports_selects_NO_test_but_its_own_importer(tmp_path):
    graph = TestMap.build(_write(tmp_path, TREE))
    assert graph.dependents({"pkg.alone"}) == {"tests/test_unrelated.py"}
    assert graph.dependents({"pkg.nothing"}) == set()


def test_a_changed_TEST_selects_itself(tmp_path):
    graph = TestMap.build(_write(tmp_path, TREE))
    assert graph.dependents({"tests.test_unrelated"}) == {"tests/test_unrelated.py"}


def test_the_PARENT_package_reaches_every_test_under_it(tmp_path):
    graph = TestMap.build(_write(tmp_path, TREE))
    assert len(graph.dependents({"pkg"})) == 3


def test_FIXTURE_corpora_are_never_parsed_as_modules(tmp_path):
    graph = TestMap.build(_write(tmp_path, TREE))
    assert not any(path.startswith("tests/fixtures/") for path in graph.files.values())
    assert graph.tests == (
        "tests/test_direct.py",
        "tests/test_through_a_helper.py",
        "tests/test_unrelated.py",
    )


def test_an_UNPARSEABLE_file_imports_nothing_but_is_still_on_the_map(tmp_path):
    graph = TestMap.build(_write(tmp_path, {**TREE, "tests/test_broken.py": "def (:\n"}))
    assert "tests/test_broken.py" in graph.tests
    assert graph.dependents({"tests.test_broken"}) == {"tests/test_broken.py"}


def test_the_REAL_tree_is_INHABITED():
    # ⛔ Ruling 191: a map of nothing would select nothing and read as a pass.
    graph = TestMap.build(repository_root())
    assert "tools/tests/test_testmap.py" in graph.tests
    assert "tools/tests/test_testmap.py" in graph.dependents({"tools.testmap"})
