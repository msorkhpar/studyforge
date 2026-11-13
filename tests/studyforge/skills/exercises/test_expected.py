"""Mirror of `skills.exercises.expected` (R12): the expected-output check, run as a real pytest.

⭐ Each reading writes a tiny project, the check this module writes for it, and runs `pytest` over
it in a process of its own, as a gate's runner would.
"""

from __future__ import annotations

import sys

from studyforge.skills.exercises.expected import CHECK_FILE, CHECK_TEST, Expected, check_source
from tests.support import run

EXPECTED = "crate capacity: 10 kg\n  bean 4 kg 7.50\ntotal value: 16.40\n"


def _project(tmp_path, printed: str, *, abs_tol: float = 0.005) -> object:
    (tmp_path / "tests").mkdir(parents=True)
    (tmp_path / "expected").mkdir()
    (tmp_path / "expected" / "report.txt").write_text(EXPECTED, encoding="utf-8")
    (tmp_path / "main.py").write_text(f"print({printed!r}, end='')\n", encoding="utf-8")
    check = check_source(Expected("expected/report.txt", abs_tol, 0.0), "main.py", depth=1)
    (tmp_path / "tests" / CHECK_FILE).write_text(check, encoding="utf-8")
    argv = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
            "--rootdir", str(tmp_path), str(tmp_path / "tests" / CHECK_FILE)]
    return run(argv, tmp_path)


def test_the_same_report_passes_and_trailing_spaces_and_blank_lines_are_not_compared(tmp_path):
    done = _project(tmp_path, EXPECTED.replace("kg\n", "kg   \n") + "\n\n")
    assert done.returncode == 0, done.stdout


def test_a_number_within_the_tolerance_passes(tmp_path):
    assert _project(tmp_path, EXPECTED.replace("16.40", "16.402")).returncode == 0


def test_a_number_outside_the_tolerance_fails_on_an_assertion_naming_the_line(tmp_path):
    done = _project(tmp_path, EXPECTED.replace("16.40", "16.50"))
    assert done.returncode == 1
    assert "AssertionError" in done.stdout and CHECK_TEST in done.stdout
    assert "line 3: 16.50 is not 16.40 within abs 0.005" in done.stdout


def test_changed_text_fails_with_a_unified_diff(tmp_path):
    done = _project(tmp_path, EXPECTED.replace("bean", "beet"))
    assert "line 2: the text differs" in done.stdout
    assert "--- expected report" in done.stdout and "+++ your report" in done.stdout
    assert "-  bean 4 kg 7.50" in done.stdout and "+  beet 4 kg 7.50" in done.stdout


def test_a_missing_line_and_a_crashing_entry_point_each_fail_on_an_assertion(tmp_path):
    short = _project(tmp_path / "short", EXPECTED.rsplit("total", 1)[0])
    assert "the report has 2 lines and the expected one 3" in short.stdout
    _project(tmp_path / "crash", "")
    (tmp_path / "crash" / "main.py").write_text("raise SystemExit(3)\n", encoding="utf-8")
    crashed = run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                   str(tmp_path / "crash" / "tests" / CHECK_FILE)], tmp_path / "crash")
    assert "main.py exited with 3" in crashed.stdout and "AssertionError" in crashed.stdout


def test_the_check_imports_nothing_but_the_standard_library():
    text = check_source(Expected("expected/report.txt"), "main.py", depth=1)
    imported = {line.split()[1] for line in text.splitlines() if line.startswith("import ")}
    assert imported == {"difflib", "math", "re", "subprocess", "sys"}
    assert "from studyforge" not in text and "parents[1]" in text
