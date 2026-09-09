"""Mirror of `tools/quality/size.py` (R12).

The two acceptance cases for FND-01 are `test_oversized_source_module_fails`
and `test_justified_oversized_module_passes`: the ceiling must actually stop a
file, and the documented opt-out must actually let one through.
"""

from __future__ import annotations

from pathlib import Path

from tools.quality import config
from tools.quality.size import check_sizes, count_lines, module_docstring, size_exception


def write_module(root: Path, relative: str, text: str) -> Path:
    """Write `text` at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def module_of(lines: int, docstring: str = "") -> str:
    """A syntactically valid module of exactly `lines` physical lines."""
    head = f'"""{docstring}"""\n' if docstring else ""
    body_lines = lines - len(head.splitlines())
    return head + "".join(f"x{number} = {number}\n" for number in range(body_lines))


# --- counting --------------------------------------------------------------


def test_count_lines_matches_wc_l():
    assert count_lines("") == 0
    assert count_lines("a\n") == 1
    assert count_lines("a\nb\n") == 2
    assert count_lines("a\nb") == 2  # no trailing newline: the last line counts


def test_module_of_produces_the_length_it_claims():
    assert count_lines(module_of(50)) == 50
    assert count_lines(module_of(50, "one\nSize exception: two")) == 50


# --- the ceiling -----------------------------------------------------------


def test_a_module_under_the_ceiling_passes(tmp_path):
    write_module(tmp_path, "src/studyforge/small.py", module_of(config.SOURCE_LINE_CEILING))
    assert check_sizes(tmp_path) == []


def test_oversized_source_module_fails(tmp_path):
    write_module(tmp_path, "src/studyforge/big.py", module_of(config.SOURCE_LINE_CEILING + 1))
    findings = check_sizes(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "size"
    assert findings[0].path == "src/studyforge/big.py"
    assert "401 lines, ceiling 400" in findings[0].message
    # ⭐ The message has to say how to get through the gate legitimately,
    # or the next person's move is to delete the check.
    assert config.SIZE_EXCEPTION_MARKER in findings[0].message


def test_a_test_module_gets_the_looser_ceiling(tmp_path):
    write_module(
        tmp_path,
        "tests/studyforge/test_big.py",
        module_of(config.SOURCE_LINE_CEILING + 1),
    )
    assert check_sizes(tmp_path) == []

    write_module(
        tmp_path,
        "tests/studyforge/test_bigger.py",
        module_of(config.TEST_LINE_CEILING + 1),
    )
    findings = check_sizes(tmp_path)
    assert [finding.path for finding in findings] == ["tests/studyforge/test_bigger.py"]
    assert "601 lines, ceiling 600" in findings[0].message


# --- the opt-out -----------------------------------------------------------


def test_justified_oversized_module_passes(tmp_path):
    docstring = (
        "A template renderer.\n\n"
        "Size exception: the substitution table is one literal mapping and "
        "splitting it across modules would hide half the placeholders from "
        "the reader of the other half."
    )
    write_module(
        tmp_path,
        "src/studyforge/justified.py",
        module_of(config.SOURCE_LINE_CEILING + 100, docstring),
    )
    assert check_sizes(tmp_path) == []


def test_an_empty_justification_does_not_pass(tmp_path):
    write_module(
        tmp_path,
        "src/studyforge/hollow.py",
        module_of(config.SOURCE_LINE_CEILING + 1, "Thing.\n\nSize exception: yes"),
    )
    findings = check_sizes(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "size-justification"
    assert "3 characters of reason" in findings[0].message


def test_the_marker_must_be_in_the_docstring_not_merely_in_the_file(tmp_path):
    # ⛔ A comment beside the offending code is not a contract. The exception
    # is recorded where the next reader of the module will meet it: the top.
    body = module_of(config.SOURCE_LINE_CEILING + 1)
    body += "# Size exception: a comment is not a contract and must not count here\n"
    write_module(tmp_path, "src/studyforge/sneaky.py", body)
    findings = check_sizes(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "size"


def test_the_marker_is_the_ruled_literal_and_case_sensitive():
    # ⛔ Case-sensitive by ruling. The review rubric greps for `Size
    # exception:` exactly, so a lowercase variant must be reported as no
    # exception claimed rather than quietly accepted here and rejected there.
    assert size_exception("Thing.\n\nSize exception: because it is one table.") == (
        "because it is one table."
    )
    assert size_exception("Thing.\n\nsize-exception: because it is one table.") is None
    assert size_exception("Thing.") is None
    assert size_exception(None) is None


def test_an_unparseable_module_is_measured_anyway(tmp_path):
    # A file too broken to parse still has a length, and reporting it is the
    # safe direction: the alternative is a syntax error that also silently
    # buys an exemption from the ceiling.
    body = module_of(config.SOURCE_LINE_CEILING + 1) + "def (\n"
    path = write_module(tmp_path, "src/studyforge/broken.py", body)
    assert module_docstring(path.read_text("utf-8"), path) is None
    assert [finding.rule for finding in check_sizes(tmp_path)] == ["size"]
