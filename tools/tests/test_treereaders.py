"""Mirror of `tools/treereaders.py` (R12): the `reads_tree` rule, test by test (`W366`).

⭐ Each rule is asserted BOTH WAYS on a throwaway file in `tmp_path`: the shape that reads
the tree is found, and the neighbouring shape that does not is left out. ⭐ The last two
tests are the marker itself, read off pytest's own items: this module's conftest applies it
from the same rule, so one test here that reads the tree must carry it and one must not.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import tools.treereaders as treereaders_module
from tests.support import assert_package_contract, repository_root
from tools.treereaders import WHOLE, TreeReaders, names_a_token

ROOT_FINDER = "from tests.support import repository_root\n"


def _readers(tmp_path: Path, files: dict[str, str]) -> TreeReaders:
    for relative, text in files.items():
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_text(text, encoding="utf-8")
    return TreeReaders(tmp_path)


def _nodes(tmp_path: Path, source: str, **more: str) -> frozenset[str]:
    helpers = {name.replace("__", "/") + ".py": text for name, text in more.items()}
    files = {"tests/test_it.py": source, **helpers}
    return _readers(tmp_path, files).nodes("tests/test_it.py")


def test_states_its_contract():
    assert_package_contract(treereaders_module, "tools.treereaders")


# --- the tokens -------------------------------------------------------------------------


def test_every_token_is_found_and_plain_code_is_not():
    for token in treereaders_module.TREE_TOKENS:
        assert names_a_token(f"x = {token}"), token
    assert not names_a_token("x = parse(text)")


def test_a_root_finder_into_the_FIXTURE_tree_is_not_reading_the_tree():
    # ⭐ `tests/fixtures/` is shared machinery: a change there selects everything anyway.
    assert not names_a_token('FIXTURES = repository_root() / "tests" / "fixtures"')
    assert not names_a_token('FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"')
    assert names_a_token('DOCS = repository_root() / "docs"')


# --- by name, inside one file -----------------------------------------------------------


def test_a_test_that_names_a_token_READS_and_its_neighbour_does_NOT(tmp_path):
    source = ROOT_FINDER + (
        "def test_reads():\n    repository_root()\n\ndef test_pure():\n    assert 1\n"
    )
    assert _nodes(tmp_path, source) == {"test_reads"}


def test_IMPORTING_the_root_finder_is_not_reading_the_tree(tmp_path):
    assert _nodes(tmp_path, ROOT_FINDER + "def test_pure():\n    assert 1\n") == set()


def test_a_DOCSTRING_that_mentions_the_root_finder_reads_nothing(tmp_path):
    source = '"""Uses repository_root() elsewhere."""\ndef test_pure():\n    assert 1\n'
    assert _nodes(tmp_path, source) == set()


def test_a_token_reaches_a_test_through_a_HELPER_a_CONSTANT_and_a_FIXTURE(tmp_path):
    source = ROOT_FINDER + (
        "DOCS = repository_root() / 'docs'\n"
        "def _read():\n    return DOCS\n"
        "@pytest.fixture\ndef board():\n    return _read()\n"
        "def test_by_helper():\n    _read()\n"
        "def test_by_fixture(board):\n    assert board\n"
        "def test_pure(tmp_path):\n    assert tmp_path\n"
    )
    assert _nodes(tmp_path, source) == {"test_by_helper", "test_by_fixture"}


def test_a_CLASS_is_taken_by_its_name(tmp_path):
    source = ROOT_FINDER + "class TestIt:\n    def test_a(self):\n        repository_root()\n"
    assert _nodes(tmp_path, source) == {"TestIt"}


def test_ONLY_what_pytest_COLLECTS_is_named(tmp_path):
    # ⛔ `file::test_cases` for a list, or for a fixture, is an error rather than a selection.
    source = ROOT_FINDER + (
        "test_cases = [repository_root()]\n"
        "@pytest.fixture\ndef test_root():\n    return repository_root()\n"
        "def test_uses(test_root):\n    assert test_cases\n"
    )
    assert _nodes(tmp_path, source) == {"test_uses"}


# --- the WHOLE file ---------------------------------------------------------------------


def test_a_token_in_a_bare_top_level_statement_takes_the_WHOLE_file(tmp_path):
    source = ROOT_FINDER + "for path in repository_root().iterdir():\n    pass\n"
    assert _nodes(tmp_path, source + "def test_pure():\n    assert 1\n") == {WHOLE}


def test_the_MARKER_by_hand_on_the_module_takes_the_WHOLE_file(tmp_path):
    source = "import pytest\npytestmark = pytest.mark.reads_tree\ndef test_a():\n    assert 1\n"
    assert _nodes(tmp_path, source) == {WHOLE}


def test_the_MARKER_by_hand_on_one_test_takes_that_test(tmp_path):
    source = (
        "import pytest\n@pytest.mark.reads_tree\ndef test_a():\n    pass\n"
        "def test_b():\n    pass\n"
    )
    assert _nodes(tmp_path, source) == {"test_a"}


def test_an_AUTOUSE_fixture_that_reads_takes_the_WHOLE_file(tmp_path):
    source = ROOT_FINDER + (
        "@pytest.fixture(autouse=True)\ndef everywhere():\n    repository_root()\n"
        "def test_a():\n    assert 1\n"
    )
    assert _nodes(tmp_path, source) == {WHOLE}


def test_an_UNPARSEABLE_file_is_taken_WHOLE(tmp_path):
    assert _nodes(tmp_path, "def (:\n") == {WHOLE}


# --- across files: helpers and conftests ------------------------------------------------


def test_a_name_from_a_READING_helper_reaches_its_test_and_a_pure_name_does_not(tmp_path):
    helper = ROOT_FINDER + "def docs():\n    return repository_root()\ndef pure():\n    return 1\n"
    source = (
        "from tests.helper import docs, pure\n"
        "def test_docs():\n    docs()\ndef test_pure():\n    pure()\n"
    )
    assert _nodes(tmp_path, source, tests__helper=helper) == {"test_docs"}


def test_the_ROOT_FINDERS_own_module_is_never_a_reading_helper(tmp_path):
    support = "from pathlib import Path\ndef repository_root():\n    return Path(__file__)\n"
    source = ROOT_FINDER + "def test_pure():\n    assert 1\n"
    assert _nodes(tmp_path, source, tests__support=support) == set()


def test_a_CONFTEST_fixture_that_reads_reaches_the_test_that_takes_it(tmp_path):
    conftest = ROOT_FINDER + "@pytest.fixture\ndef board():\n    return repository_root()\n"
    readers = _readers(
        tmp_path,
        {
            "tests/conftest.py": conftest,
            "tests/deep/test_it.py": "def test_a(board):\n    pass\ndef test_b():\n    pass\n",
        },
    )
    assert readers.nodes("tests/deep/test_it.py") == {"test_a"}
    assert readers.reads("tests/deep/test_it.py", "test_a")
    assert not readers.reads("tests/deep/test_it.py", "test_b")


# --- the marker, read off pytest's own items --------------------------------------------


def test_THIS_test_reads_the_tree_and_CARRIES_the_marker(request):
    assert repository_root().is_dir()
    assert request.node.get_closest_marker("reads_tree") is not None


def test_this_one_reads_nothing_and_carries_NO_marker(request):
    assert request.node.get_closest_marker("reads_tree") is None


def test_the_marker_is_REGISTERED_so_strict_markers_accepts_it(pytestconfig):
    registered = pytestconfig.getini("markers")
    assert any(line.startswith("reads_tree:") for line in registered), registered


@pytest.mark.reads_tree
def test_the_marker_BY_HAND_is_read_by_the_rule_too(request):
    readers = TreeReaders(Path(__file__).resolve().parents[2])
    assert "test_the_marker_BY_HAND_is_read_by_the_rule_too" in readers.nodes(
        "tools/tests/test_treereaders.py"
    )
