"""Mirror of `tools/quality/mirror.py` (R12)."""

from __future__ import annotations

from tests.floor.mirror import check_mirrors, mirror_for


def write(root, relative, text='"""x."""\n'):
    """Write a module at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_the_mapping_is_the_one_the_convention_document_gives():
    assert mirror_for("src/studyforge/serve/routes/content.py") == (
        "tests/studyforge/serve/routes/test_content.py"
    )


def test_a_package_contract_is_tested_as_test_init():
    assert mirror_for("src/studyforge/address/__init__.py") == (
        "tests/studyforge/address/test_init.py"
    )
    assert mirror_for("src/studyforge/__init__.py") == "tests/studyforge/test_init.py"


def test_tools_mirrors_itself_beside_itself():
    # ⛔ "Outside src/" must not mean "outside R12". The size checker is
    # developer tooling rather than shipped API, so its tests sit beside it at
    # `tools/tests/` — locality, which is what R12 is actually asking for —
    # and the mapping is the same mapping.
    assert mirror_for("tools/quality/size.py") == "tools/tests/quality/test_size.py"
    assert mirror_for("tools/quality/__main__.py") == "tools/tests/quality/test_main.py"


def test_the_tooling_test_tree_is_not_itself_mirrored():
    # ⚠️ `tools/tests/` sits inside its own source root. Without the guard it
    # would be read as a source module wanting a test of its own, forever.
    assert mirror_for("tools/tests/quality/test_size.py") is None


def test_a_path_under_no_source_root_is_not_mirrored():
    assert mirror_for("tests/support.py") is None
    assert mirror_for("docs/conventions/module-structure.md") is None


def test_a_source_module_with_no_test_fails(tmp_path):
    write(tmp_path, "src/studyforge/address/__init__.py")
    findings = check_mirrors(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "mirror"
    assert findings[0].line == 0  # the file as a whole, not a line in it
    assert "tests/studyforge/address/test_init.py" in findings[0].message


def test_a_source_module_with_its_mirror_passes(tmp_path):
    write(tmp_path, "src/studyforge/address/__init__.py")
    write(tmp_path, "tests/studyforge/address/test_init.py")
    assert check_mirrors(tmp_path) == []


def test_the_tooling_passes_with_its_mirror_beside_it(tmp_path):
    write(tmp_path, "tools/quality/size.py")
    findings = check_mirrors(tmp_path)
    assert "tools/tests/quality/test_size.py" in findings[0].message
    write(tmp_path, "tools/tests/quality/test_size.py")
    assert check_mirrors(tmp_path) == []


def test_a_test_with_no_source_is_not_a_finding(tmp_path):
    # ⚠️ One-way on purpose. `tests/harness/` (SF-26), `tests/visual/`
    # (QA-03), `tests/support.py` and the repository-level tests all exist
    # without a source counterpart; checking the reverse direction would turn
    # each of them into an exemption, and an exemption list that grows is how
    # a check stops being believed.
    write(tmp_path, "tests/harness/golden.py")
    write(tmp_path, "tests/test_repository.py")
    assert check_mirrors(tmp_path) == []
