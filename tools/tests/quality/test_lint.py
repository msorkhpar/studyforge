"""Mirror of `tools/quality/lint.py` (R12).

⛔ **Every state is driven through a fake runner, including the two the machine
running these tests cannot be in.** Absence is the state Ruling 78 exists for
and a container with ruff installed can never reproduce it; presence is the
state a bare host cannot. A test that only exercised whichever one the current
machine happens to be in would be the same defect this module closes — a check
that could not fail, reporting success.

⭐ The one test that does use the real tool skips when it is missing, and says
so by name.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys

import pytest

from tests.support import repository_root, tool_on_path
from tools.quality import lint
from tools.quality.lint import lint_notice

CLEAN_FORMAT = "392 files already formatted\n"
DIRTY_FORMAT = "9 files would be reformatted, 383 files already formatted\n"


def report(*entries: tuple[str, str]) -> str:
    """Ruff's `--output-format=json` for `(code, filename)` pairs."""
    return json.dumps([{"code": code, "filename": name} for code, name in entries])


def completed(returncode: int, stdout: str) -> subprocess.CompletedProcess[str]:
    """A finished process with the given verdict and output."""
    return subprocess.CompletedProcess(args=["ruff"], returncode=returncode, stdout=stdout)


def runner(
    recorded: list,
    *,
    version: str = "ruff 0.16.6\n",
    version_code: int = 0,
    check: tuple[int, str] = (0, "[]"),
    fmt: tuple[int, str] = (0, CLEAN_FORMAT),
):
    """A stand-in for `lint._run` that answers each invocation from a script."""

    def run(executable, args, root):
        recorded.append(args)
        if args == ("--version",):
            return completed(version_code, version)
        if args == lint.CHECK_ARGS:
            return completed(*check)
        if args == lint.FORMAT_ARGS:
            return completed(*fmt)
        raise AssertionError(f"unexpected invocation: {args}")

    return run


def notice(monkeypatch, tmp_path, **script) -> str:
    """The single line `lint_notice` prints with the tool present and scripted."""
    recorded: list = []
    monkeypatch.setattr(lint, "_which", lambda name: "/usr/local/bin/ruff")
    monkeypatch.setattr(lint, "_run", runner(recorded, **script))
    lines = lint_notice(tmp_path)
    assert len(lines) == 1, lines
    return lines[0]


# --- absent: the state the ruling exists for -------------------------------


def test_absence_is_reported_and_is_not_silent(monkeypatch, tmp_path):
    # ⛔ The defect Ruling 78 closes. A notice that said nothing here would
    # leave the reader with `quality floor: clean` and no way to learn that
    # half the instrument was switched off.
    monkeypatch.setattr(lint, "_which", lambda name: None)
    lines = lint_notice(tmp_path)
    assert len(lines) == 1
    assert "is NOT installed" in lines[0]
    assert "no lint signal at all" in lines[0]


def test_absence_names_both_commands_that_did_not_run(monkeypatch, tmp_path):
    monkeypatch.setattr(lint, "_which", lambda name: None)
    line = lint_notice(tmp_path)[0]
    assert lint.CHECK_SHOWN in line
    assert lint.FORMAT_SHOWN in line


def test_absence_names_the_gates_that_skipped_and_both_ways_to_get_the_signal(
    monkeypatch, tmp_path
):
    # ⭐ `knowledge_index.notices` set the standard: an absence notice prints
    # the commands that produce the missing thing, so nobody has to go looking.
    monkeypatch.setattr(lint, "_which", lambda name: None)
    line = lint_notice(tmp_path)[0]
    assert lint.GATES in line
    assert lint.INSTALL in line
    assert lint.IMAGE in line


def test_absence_says_the_floor_verdict_never_covered_lint(monkeypatch, tmp_path):
    monkeypatch.setattr(lint, "_which", lambda name: None)
    line = lint_notice(tmp_path)[0]
    assert "quality floor: clean" in line
    assert "not a failure" in line


def test_absence_asks_nothing_of_the_missing_tool(monkeypatch, tmp_path):
    # ⭐ The trick the whole ruling turns on: a notice reporting a tool's
    # absence does not depend on that tool, so Ruling 77 is untouched.
    recorded: list = []
    monkeypatch.setattr(lint, "_which", lambda name: None)
    monkeypatch.setattr(lint, "_run", runner(recorded))
    lint_notice(tmp_path)
    assert recorded == []


# --- present and clean -----------------------------------------------------


def test_clean_reports_the_version_and_both_verdicts(monkeypatch, tmp_path):
    line = notice(monkeypatch, tmp_path)
    assert line.startswith("lint: ruff 0.16.6 —")
    assert f"`{lint.CHECK_SHOWN}` clean" in line
    assert f"`{lint.FORMAT_SHOWN}` clean (392 file(s) already formatted)" in line
    assert "This run carries a real lint signal." in line


def test_clean_never_claims_the_tool_is_missing(monkeypatch, tmp_path):
    assert "NOT installed" not in notice(monkeypatch, tmp_path)


def test_an_unreadable_version_is_stated_rather_than_guessed(monkeypatch, tmp_path):
    line = notice(monkeypatch, tmp_path, version="\n")
    assert "ruff of unknown version" in line


def test_a_failed_version_probe_is_not_read_as_a_version(monkeypatch, tmp_path):
    # ⚠️ A non-zero exit means the words on stdout are a diagnostic, not a
    # version. Printing the last of them would put an unverified string where a
    # review is required to state the version that produced its lint line
    # (Ruling 79).
    line = notice(monkeypatch, tmp_path, version="error: unknown flag\n", version_code=2)
    assert "ruff of unknown version" in line
    assert "flag" not in line


# --- present and dirty -----------------------------------------------------


def test_dirty_lint_counts_findings_files_and_codes(monkeypatch, tmp_path):
    entries = [("F401", "/w/a.py")] * 9 + [("D401", f"/w/b{n}.py") for n in range(6)]
    line = notice(monkeypatch, tmp_path, check=(1, report(*entries)))
    assert "15 finding(s) in 7 file(s)" in line
    assert "(D401, F401)" in line


def test_dirty_format_counts_the_files_that_would_change(monkeypatch, tmp_path):
    line = notice(monkeypatch, tmp_path, fmt=(1, DIRTY_FORMAT))
    assert f"`{lint.FORMAT_SHOWN}` 9 file(s) would be reformatted" in line


def test_either_half_dirty_points_at_the_module_that_enforces(monkeypatch, tmp_path):
    # ⚠️ The notice must never read as a verdict of its own. Enforcement is in
    # `tests/test_repository.py` (Ruling 78) and the line says which.
    dirty_lint = notice(monkeypatch, tmp_path, check=(1, report(("F401", "/w/a.py"))))
    dirty_format = notice(monkeypatch, tmp_path, fmt=(1, DIRTY_FORMAT))
    for line in (dirty_lint, dirty_format):
        assert "Not a floor failure and not a floor pass" in line
        assert lint.GATES in line


def test_a_long_tail_of_codes_is_capped_rather_than_dumped(monkeypatch, tmp_path):
    entries = [(f"E{n:03d}", "/w/a.py") for n in range(lint.MAX_CODES + 3)]
    line = notice(monkeypatch, tmp_path, check=(1, report(*entries)))
    assert "and 3 more" in line
    assert f"E{lint.MAX_CODES + 2:03d}" not in line


#: ⛔ A bound written here and NOT read from the module, because a test that
#: sizes its own input off `MAX_CODES` moves with the constant and cannot tell
#: a cap of 6 from a cap of 60. ⚠️ Measured: the sweep's `MAX_CODES = 60`
#: SURVIVED the test above for exactly that reason, and this is the row that
#: killed it. The property is the one the constant's comment states — a notice
#: names a handful of codes, never a wall of forty.
MOST_CODES_A_NOTICE_MAY_NAME = 10


def test_forty_distinct_codes_still_leave_a_line_worth_reading(monkeypatch, tmp_path):
    codes = [f"E{n:03d}" for n in range(40)]
    line = notice(monkeypatch, tmp_path, check=(1, report(*[(code, "/w/a.py") for code in codes])))
    named = [code for code in codes if code in line]
    assert len(named) <= MOST_CODES_A_NOTICE_MAY_NAME, named
    assert f"and {40 - len(named)} more" in line


def test_an_entry_with_no_code_still_counts(monkeypatch, tmp_path):
    # ⚠️ Some ruff diagnostics carry a `name` and a null `code`. Dropping them
    # would under-report the number a reader compares against the gate's.
    payload = json.dumps([{"code": None, "name": "syntax-error", "filename": "/w/a.py"}])
    line = notice(monkeypatch, tmp_path, check=(1, payload))
    assert "1 finding(s) in 1 file(s) (syntax-error)" in line


# --- R7: nothing ruff reports about the disk is printed --------------------


#: ⚠️ A placeholder, and it has to be one: the floor's own `check_personal_data`
#: refuses a home path in a tracked file (R7), including in a fixture that
#: exists to prove home paths are not printed. ⭐ The rule holds against the
#: test written to demonstrate it, which is the strongest form it has.
ABSOLUTE = "/path/to/checkout/src/studyforge/render.py"


def test_no_path_ruff_reports_ever_reaches_the_line(monkeypatch, tmp_path):
    # ⛔ `--output-format=json` carries an ABSOLUTE filename per finding, which
    # on a contributor's machine contains their home directory (R7). Counted,
    # never printed.
    line = notice(monkeypatch, tmp_path, check=(1, report(("F401", ABSOLUTE))))
    assert ABSOLUTE not in line
    assert "/path/to/" not in line
    assert "1 finding(s) in 1 file(s) (F401)" in line


def test_the_unrunnable_line_carries_no_diagnostic_stream(monkeypatch, tmp_path):
    # ⚠️ Same reasoning as above, applied to the error path: an exit code
    # cannot leak a path and a captured stderr can, so only the code is used.
    line = notice(monkeypatch, tmp_path, check=(2, f"{ABSOLUTE}: bad config"))
    assert "/path/to/" not in line
    assert "it exited 2" in line


# --- present, and it would not answer --------------------------------------


def test_an_unexpected_exit_is_the_fourth_state(monkeypatch, tmp_path):
    line = notice(monkeypatch, tmp_path, check=(2, ""))
    assert "could not be run" in line
    assert "no lint signal" in line
    assert "not a failure" in line


def test_an_unexpected_format_exit_is_the_fourth_state(monkeypatch, tmp_path):
    line = notice(monkeypatch, tmp_path, fmt=(3, ""))
    assert "its formatter exited 3" in line


def test_an_unparseable_report_is_the_fourth_state(monkeypatch, tmp_path):
    line = notice(monkeypatch, tmp_path, check=(1, "not json at all"))
    assert "its report could not be parsed" in line


def test_a_timeout_is_the_fourth_state(monkeypatch, tmp_path):
    # ⛔ A notice may never hang the floor: the floor's job is to reach a
    # verdict and this may not stop it reaching one.
    def timing_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ruff", timeout=lint.TIMEOUT)

    monkeypatch.setattr(lint, "_which", lambda name: "/usr/local/bin/ruff")
    monkeypatch.setattr(subprocess, "run", timing_out)
    line = lint_notice(tmp_path)[0]
    assert f"did not finish within {lint.TIMEOUT}s" in line


def test_a_process_that_will_not_start_is_the_fourth_state(monkeypatch, tmp_path):
    def refusing(*args, **kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr(lint, "_which", lambda name: "/usr/local/bin/ruff")
    monkeypatch.setattr(subprocess, "run", refusing)
    line = lint_notice(tmp_path)[0]
    assert "the process could not be started (PermissionError)" in line


# --- the invocation itself -------------------------------------------------


def test_neither_invocation_writes_a_cache_into_the_tree(monkeypatch, tmp_path):
    # ⛔ A notice that made the floor write `.ruff_cache/` into the tree it is
    # reporting on would be changing its subject in order to describe it.
    assert "--no-cache" in lint.CHECK_ARGS
    assert "--no-cache" in lint.FORMAT_ARGS
    recorded: list = []
    monkeypatch.setattr(lint, "_which", lambda name: "/usr/local/bin/ruff")
    monkeypatch.setattr(lint, "_run", runner(recorded))
    lint_notice(tmp_path)
    assert lint.CHECK_ARGS in recorded
    assert lint.FORMAT_ARGS in recorded


def test_the_displayed_commands_are_ones_a_reader_can_paste(monkeypatch, tmp_path):
    # ⚠️ The machine-readable flags are noise in a report, and a reader who
    # pastes the shown form must get the same verdict.
    assert "--output-format" not in lint.CHECK_SHOWN
    assert "--no-cache" not in lint.FORMAT_SHOWN
    assert lint.CHECK_SHOWN == "ruff check ."
    assert lint.FORMAT_SHOWN == "ruff format --check ."


def test_the_notice_module_imports_only_the_standard_library():
    # ⛔ Ruling 77's boundary, asserted rather than asserted-about. The floor
    # stays standard-library-only, and the module that reports on an optional
    # tool is the one most likely to reach for it.
    path = repository_root() / "tools" / "quality" / "lint.py"
    tree = ast.parse(path.read_text("utf-8"), filename="tools/quality/lint.py")
    roots: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots += [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            roots.append((node.module or "").split(".")[0])
    assert roots, "no imports parsed; the guard would pass on an unreadable file"
    assert [name for name in roots if name not in sys.stdlib_module_names] == []


# --- the real tool, where there is one -------------------------------------


def test_the_real_tool_reports_the_repository_as_clean():
    # ⭐ The fakes above prove the shape; this proves the invocation. It skips
    # where ruff is absent, naming the extra — and that skip is itself the
    # state `test_absence_is_reported_and_is_not_silent` covers.
    if tool_on_path(lint.TOOL) is None:
        pytest.skip(f"{lint.TOOL} not installed; `{lint.INSTALL}` to enable this check")
    line = lint_notice(repository_root())[0]
    assert line.startswith(f"lint: {lint.TOOL} ")
    assert "of unknown version" not in line
    assert "This run carries a real lint signal." in line
