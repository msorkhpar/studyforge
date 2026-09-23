"""Mirror of `tools/quality/style.py` (R12).

⚠️ Every offending sample here is *built* from escapes rather than written as a
literal line, because a literal trailing space or tab in this file would be
caught by the checker it is testing — and "fix the test" would then mean
removing the only case that proves the rule works.
"""

from __future__ import annotations

from tests.floor import config
from tests.floor.style import check_file, check_style

SPACE = " "
TAB = "\t"


def rules(text: str) -> list[str]:
    """The rule names `check_file` reports for `text`, in order."""
    return [finding.rule for finding in check_file(text, "src/studyforge/x.py")]


def test_a_clean_file_reports_nothing():
    assert rules("value = 1\n") == []


def test_trailing_whitespace():
    assert rules("value = 1" + SPACE + "\n") == ["trailing-whitespace"]


def test_tab_indentation():
    assert rules("def f():\n" + TAB + "return 1\n") == ["tabs"]


def test_crlf():
    assert "line-endings" in rules("value = 1\r\n")


def test_missing_final_newline():
    findings = check_file("value = 1", "src/studyforge/x.py")
    assert [finding.rule for finding in findings] == ["final-newline"]
    assert "no newline at end of file" in findings[0].message


def test_blank_line_at_end_of_file():
    findings = check_file("value = 1\n\n", "src/studyforge/x.py")
    assert [finding.rule for finding in findings] == ["final-newline"]
    assert "exactly one newline" in findings[0].message


def test_an_empty_file_is_not_a_missing_newline():
    # An empty `__init__.py` is a contract failure (R17), reported by the
    # docstring check. It is not also a newline failure — one defect, one
    # finding, or the report teaches people to skim it.
    assert rules("") == []


def test_line_length_uses_the_shared_limit():
    long_line = "v = '" + "x" * config.LINE_LENGTH + "'\n"
    findings = check_file(long_line, "src/studyforge/x.py")
    assert [finding.rule for finding in findings] == ["line-length"]
    assert f"limit {config.LINE_LENGTH}" in findings[0].message


def test_the_line_number_is_reported():
    findings = check_file("a = 1\nb = 2" + SPACE + "\nc = 3\n", "src/studyforge/x.py")
    assert [(finding.line, finding.rule) for finding in findings] == [(2, "trailing-whitespace")]


def test_check_style_reads_the_tree(tmp_path):
    path = tmp_path / "src" / "studyforge" / "x.py"
    path.parent.mkdir(parents=True)
    path.write_text("value = 1" + SPACE + "\n", encoding="utf-8")
    findings = check_style(tmp_path)
    assert [finding.path for finding in findings] == ["src/studyforge/x.py"]
