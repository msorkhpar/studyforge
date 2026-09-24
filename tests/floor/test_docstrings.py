"""Mirror of `tools/quality/docstrings.py` (R12)."""

from __future__ import annotations

from tests.floor import config
from tests.floor.docstrings import check_docstrings


def write(root, relative, text):
    """Write a module at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


CONTRACT = (
    '"""Does one thing.\n\nHow you use it: call `thing`.\n\nDepends on: nothing at all.\n"""\n'
)


def test_a_module_with_a_contract_passes(tmp_path):
    write(tmp_path, "src/studyforge/address/__init__.py", CONTRACT)
    assert check_docstrings(tmp_path) == []


def test_a_module_with_no_docstring_fails(tmp_path):
    write(tmp_path, "src/studyforge/address/__init__.py", "value = 1\n")
    findings = check_docstrings(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "contract"
    assert "R17" in findings[0].message


def test_a_label_is_not_a_contract(tmp_path):
    # ⛔ `"""path utilities"""` is the failure R17 exists to prevent: it says
    # what the module is filed under, not what it promises.
    write(tmp_path, "src/studyforge/paths.py", '"""path utilities."""\n')
    findings = check_docstrings(tmp_path)
    assert len(findings) == 1
    assert str(config.MIN_DOCSTRING_CHARS) in findings[0].message


def test_test_modules_are_not_checked(tmp_path):
    # A test module's name and its assertions say what it covers. Demanding a
    # contract from it would be demanding a second description of the same
    # thing, which is a description that goes stale.
    write(tmp_path, "tests/studyforge/test_init.py", "def test_x():\n    assert True\n")
    assert check_docstrings(tmp_path) == []


def test_an_unparseable_module_is_left_to_the_tools_that_report_it_better(tmp_path):
    write(tmp_path, "src/studyforge/broken.py", "def (\n")
    assert check_docstrings(tmp_path) == []
