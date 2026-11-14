"""Mirror of `src/studyforge/execute/maintenance.py` (R12).

⭐ Every clause runs a real process, and the one process is this suite's own
Python: no program of this machine's is assumed beyond the interpreter running it.
"""

from __future__ import annotations

import io
import sys

from studyforge.execute.maintenance import ECHO, NOT_STARTED, ask


def test_it_answers_the_exit_code_and_the_standard_output(tmp_path):
    out = io.StringIO()

    code, said = ask([sys.executable, "-c", "print('one'); print('two')"], tmp_path, out=out)

    assert (code, said) == (0, "one\ntwo\n")


def test_each_line_is_echoed_as_it_comes_so_a_long_build_is_seen(tmp_path):
    out = io.StringIO()

    ask([sys.executable, "-c", "print('one'); print('two')"], tmp_path, out=out)

    assert out.getvalue() == f"{ECHO}one\n{ECHO}two\n"


def test_a_failing_command_is_an_exit_code_and_never_an_exception(tmp_path):
    code, _ = ask([sys.executable, "-c", "raise SystemExit(3)"], tmp_path, out=io.StringIO())

    assert code == 3


def test_standard_error_is_never_part_of_the_answer(tmp_path):
    # ⛔ A tag is read off the answer: a warning on stderr may not become part of it.
    script = "import sys; print('tag'); print('warning', file=sys.stderr)"

    _, said = ask([sys.executable, "-c", script], tmp_path, out=io.StringIO())

    assert said == "tag\n"


def test_it_runs_in_the_directory_it_is_given(tmp_path):
    (tmp_path / "here.txt").write_text("", encoding="utf-8")
    script = "import pathlib; print(pathlib.Path('here.txt').is_file())"

    _, said = ask([sys.executable, "-c", script], tmp_path, out=io.StringIO())

    assert said == "True\n"


def test_a_program_that_does_not_exist_is_an_exit_code_naming_it_not_started(tmp_path):
    out = io.StringIO()

    code, said = ask(["no-such-program-anywhere"], tmp_path, out=out)

    assert (code, said) == (NOT_STARTED, "")
    assert "did not start" in out.getvalue()
