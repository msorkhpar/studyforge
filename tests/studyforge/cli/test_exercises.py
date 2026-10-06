"""Mirror of `src/studyforge/cli/exercises.py` (R12) — `studyforge exercises stale`, end to end.

**What it asserts.** The command's exit codes — `0` nothing stale, `1` a stale
unit, `2` the tool could not run — the line per stale unit with its reason
and its practice counterpart, the total line, that nothing is written
without `--remove`, and that `--remove` removes exactly the listed folders or
refuses with nothing removed. ⭐ Each is read through the installed command's
dispatcher too, so the verb is the one a user types.
"""

from __future__ import annotations

import io

from studyforge.cli import main as dispatched
from studyforge.cli.exercises import CLEAN, main
from studyforge.exitcodes import UNUSABLE
from studyforge.skills.exercises import REASONS
from studyforge.skills.exercises.coverage import CONTRACT, PAGE, SOURCES
from studyforge.validate.report import INVALID, OK
from tests.studyforge.skills.exercises.staleness import (
    LEAK,
    authored,
    edit_report,
    page_of,
    practice_of,
    snapshot,
    tryit_of,
    unit_of,
    write,
)
from tests.support import git, init_repository, run


def _invoke(*argv, entry=main):
    out = io.StringIO()
    return entry(list(argv), out=out), out.getvalue()


def _corpus(root):
    for number in (1, 2, 3):
        authored(root, number)
    return root


def _stale_two(root):
    write(root, page_of(1), "# Page, edited\n")
    edit_report(root, 3, lambda document: document.update(coverage_api=9))


def test_a_changed_tryit_file_is_listed_stale_with_its_reason(tmp_path):
    _corpus(tmp_path)
    write(tmp_path, tryit_of(2), "print('edited')\n")
    code, printed = _invoke("stale", str(tmp_path))
    assert code == INVALID
    assert printed.splitlines()[0] == f"stale  {unit_of(2)}: {REASONS[SOURCES]}"


def test_units_authored_before_tracking_are_one_summary_line_and_not_stale(tmp_path):
    _corpus(tmp_path)
    for number in (1, 2):
        edit_report(tmp_path, number, lambda document: document.pop("sources"))
    code, printed = _invoke("stale", str(tmp_path))
    assert code == OK
    assert printed.splitlines() == [
        CLEAN,
        "2 unit(s) authored before try-it tracking; re-author to track them",
    ]


def test_nothing_stale_exits_zero_and_says_so(tmp_path):
    code, printed = _invoke("stale", str(_corpus(tmp_path)))
    assert (code, printed) == (OK, CLEAN + "\n")


def test_every_stale_unit_is_listed_with_its_reason_its_practice_and_a_total(tmp_path):
    _stale_two(_corpus(tmp_path))
    code, printed = _invoke("stale", str(tmp_path))
    assert code == INVALID, "a stale corpus must stop a build script"
    lines = printed.splitlines()
    assert lines[0] == f"stale  {unit_of(1)}: {REASONS[PAGE]}"
    assert lines[1] == f"       with {practice_of(1)}"
    assert lines[2].startswith(f"stale  {unit_of(3)}: {REASONS[CONTRACT]} (") and "9" in lines[2]
    assert lines[3] == f"       with {practice_of(3)}"
    assert lines[4] == "2 authored unit(s) are stale: nothing was changed"
    assert len(lines) == 5


def test_nothing_is_written_without_remove(tmp_path):
    _stale_two(_corpus(tmp_path))
    before = snapshot(tmp_path)
    _invoke("stale", str(tmp_path))
    assert snapshot(tmp_path) == before, "the command changed the corpus without --remove"


def test_the_installed_command_dispatches_the_same_verb(tmp_path):
    _stale_two(_corpus(tmp_path))
    assert _invoke("exercises", "stale", str(tmp_path), entry=dispatched) == _invoke(
        "stale", str(tmp_path)
    )


def test_a_root_that_is_not_a_directory_is_unusable(tmp_path):
    code, printed = _invoke("stale", str(tmp_path / "absent"))
    assert code == UNUSABLE and "not a directory" in printed


def test_a_report_carrying_personal_data_is_unusable_and_quotes_nothing(tmp_path):
    _corpus(tmp_path)
    edit_report(tmp_path, 2, lambda document: document.update(case=LEAK))
    code, printed = _invoke("stale", str(tmp_path))
    assert code == UNUSABLE and LEAK not in printed and "someone" not in printed


def _committed(root):
    init_repository(root)
    run([git(), "add", "-A"], cwd=root)
    identity = ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.org"]
    run([git(), *identity, "commit", "-q", "-m", "authored"], cwd=root)


def test_remove_takes_exactly_the_listed_folders_and_still_exits_one(tmp_path):
    # ⭐ Both stale units are committed as they are, so git can give each back.
    _stale_two(_corpus(tmp_path))
    _committed(tmp_path)
    code, printed = _invoke("stale", str(tmp_path), "--remove")
    assert code == INVALID, "their pages are still owed a pass"
    removed = [line.split()[1] for line in printed.splitlines() if line.startswith("removed")]
    assert removed == [unit_of(1), practice_of(1), unit_of(3), practice_of(3)]
    assert (
        printed.splitlines()[-1]
        == "2 authored unit(s) are stale: removed; author their pages again"
    )
    assert sorted(path.name for path in (tmp_path / "exercises/kata/python").iterdir()) == [
        "unit-02"
    ]
    code, printed = _invoke("stale", str(tmp_path))
    assert (code, printed) == (OK, CLEAN + "\n"), "a second run still found something stale"


def test_remove_over_an_uncommitted_edit_in_a_stale_unit_is_refused(tmp_path):
    _committed(_corpus(tmp_path))
    _stale_two(tmp_path)
    before = snapshot(tmp_path)
    code, printed = _invoke("stale", str(tmp_path), "--remove")
    assert code == UNUSABLE and "nothing was removed" in printed
    assert snapshot(tmp_path) == before, "an edit git does not hold was removed"


def test_remove_outside_a_git_work_tree_is_refused_and_removes_nothing(tmp_path):
    _stale_two(_corpus(tmp_path))
    before = snapshot(tmp_path)
    code, printed = _invoke("stale", str(tmp_path), "--remove")
    assert code == UNUSABLE and "nothing was removed" in printed
    assert snapshot(tmp_path) == before
