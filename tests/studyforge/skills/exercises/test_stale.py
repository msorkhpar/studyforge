"""Mirror of `src/studyforge/skills/exercises/stale.py` (R12) — every stale unit, from the corpus.

**What it asserts.** On fixture corpora with nothing stale, a moved page, a
moved test file, a moved plan and an old contract version, `stale_units`
names exactly the stale units with their reasons, in unit order, and writes
nothing. `remove_stale` removes exactly the listed folders when git could
restore them, and refuses, removing nothing, when it could not.
"""

from __future__ import annotations

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.skills.exercises import (
    AuthoringError,
    remove_stale,
    stale_units,
    untracked_summary,
    untracked_units,
)
from studyforge.skills.exercises.coverage import CONTRACT, PAGE, PLAN, SOURCES, TESTS
from tests.studyforge.skills.exercises.staleness import (
    LEAK,
    authored,
    edit_report,
    grader_of,
    page_of,
    practice_of,
    snapshot,
    tryit_of,
    unit_of,
    write,
)
from tests.support import git, init_repository, run


def _corpus(root, count=3):
    for number in range(1, count + 1):
        authored(root, number)
    return root


def _move_page(root, number):
    write(root, page_of(number), "# Page, edited\n\n## Greeting\n\nSay hello twice.\n")


def _move_tests(root, number):
    write(root, grader_of(number), "def test_greets():\n    assert 1\n")


def _move_plan(root, number):
    def renamed(document):
        document["plan"]["exercises"][0]["slot"] = 2

    edit_report(root, number, renamed)


def _old_contract(root, number):
    edit_report(root, number, lambda document: document["plan"].update(plan_api=1))


def _move_tryit(root, number):
    write(root, tryit_of(number), "print('try it, edited')\n")


def _unrecord_sources(root, number):
    edit_report(root, number, lambda document: document.pop("sources"))


def test_a_changed_tryit_file_makes_its_unit_stale_with_the_reason(tmp_path):
    _corpus(tmp_path)
    _move_tryit(tmp_path, 2)
    (stale,) = stale_units(tmp_path)
    assert (stale.unit, stale.reasons) == (unit_of(2), (SOURCES,))
    assert "try-it" in stale.says


def test_a_deleted_tryit_file_makes_its_unit_stale(tmp_path):
    _corpus(tmp_path)
    (tmp_path / tryit_of(1)).unlink()
    assert [one.reasons for one in stale_units(tmp_path)] == [(SOURCES,)]


def test_an_unchanged_tryit_file_leaves_every_unit_fresh(tmp_path):
    _corpus(tmp_path)
    write(tmp_path, tryit_of(2), "print('try it')\n")  # same bytes
    assert stale_units(tmp_path) == ()


def test_a_source_folder_is_moved_by_an_added_file(tmp_path):
    from studyforge.skills.exercises.ledger import source_digest

    _corpus(tmp_path, count=1)
    folder = tryit_of(1).rsplit("/", 1)[0]
    edit_report(
        tmp_path,
        1,
        lambda document: document.update(
            sources={folder: source_digest(tmp_path, folder, "the fixture")}
        ),
    )
    assert stale_units(tmp_path) == ()
    write(tmp_path, f"{folder}/extra.py", "x = 1\n")
    assert [one.reasons for one in stale_units(tmp_path)] == [(SOURCES,)]


def _declare_folder(root, number):
    from studyforge.skills.exercises.ledger import source_digest

    folder = tryit_of(number).rsplit("/", 1)[0]
    edit_report(
        root,
        number,
        lambda document: document.update(
            sources={folder: source_digest(root, folder, "the fixture")}
        ),
    )
    return folder


def test_editing_a_file_inside_a_declared_folder_makes_the_unit_stale(tmp_path):
    _corpus(tmp_path, count=1)
    _declare_folder(tmp_path, 1)
    assert stale_units(tmp_path) == ()
    _move_tryit(tmp_path, 1)  # same name, new bytes
    assert [one.reasons for one in stale_units(tmp_path)] == [(SOURCES,)]


def test_renaming_a_file_inside_a_declared_folder_makes_the_unit_stale(tmp_path):
    _corpus(tmp_path, count=1)
    folder = _declare_folder(tmp_path, 1)
    (tmp_path / tryit_of(1)).rename(tmp_path / folder / "renamed.py")
    assert [one.reasons for one in stale_units(tmp_path)] == [(SOURCES,)]


def test_a_folder_digest_changes_on_a_content_edit_a_rename_and_not_otherwise(tmp_path):
    from studyforge.skills.exercises.ledger import source_digest

    write(tmp_path, "f/a.py", "one\n")
    first = source_digest(tmp_path, "f", "the test")
    assert source_digest(tmp_path, "f", "the test") == first
    write(tmp_path, "f/a.py", "two\n")
    edited = source_digest(tmp_path, "f", "the test")
    (tmp_path / "f/a.py").rename(tmp_path / "f/b.py")
    assert len({first, edited, source_digest(tmp_path, "f", "the test")}) == 3


def test_a_unit_authored_before_tracking_is_counted_and_never_stale(tmp_path):
    _corpus(tmp_path)
    _unrecord_sources(tmp_path, 1)
    _unrecord_sources(tmp_path, 3)
    _move_tryit(tmp_path, 1)  # not visible to a unit that recorded nothing
    assert stale_units(tmp_path) == ()
    assert untracked_units(tmp_path) == 2
    assert untracked_summary(2) == "2 unit(s) authored before try-it tracking; re-author to track them"
    assert untracked_summary(0) == ""


def test_a_corpus_authored_with_tracking_has_no_untracked_unit(tmp_path):
    assert untracked_units(_corpus(tmp_path)) == 0


def test_a_corpus_with_nothing_stale_has_nothing_to_say(tmp_path):
    assert stale_units(_corpus(tmp_path)) == ()


def test_a_corpus_with_no_authored_unit_has_nothing_to_say(tmp_path):
    assert stale_units(tmp_path) == ()


@pytest.mark.parametrize(
    ("move", "reason"),
    [(_move_page, PAGE), (_move_tests, TESTS), (_move_plan, PLAN), (_old_contract, CONTRACT)],
    ids=["moved-page", "moved-test-file", "moved-plan", "old-contract"],
)
def test_each_stale_unit_is_named_with_its_reason_and_its_practice(tmp_path, move, reason):
    _corpus(tmp_path)
    move(tmp_path, 2)
    (stale,) = stale_units(tmp_path)
    assert (stale.unit, stale.reasons) == (unit_of(2), (reason,))
    assert stale.folders == (unit_of(2), practice_of(2))


def test_every_stale_unit_is_listed_in_one_run_in_unit_order(tmp_path):
    # ⭐ The point of the command: all of them at once, never the first alone.
    _corpus(tmp_path, count=4)
    _old_contract(tmp_path, 4)
    _move_page(tmp_path, 1)
    _move_tests(tmp_path, 3)
    found = stale_units(tmp_path)
    assert [(one.unit, one.reasons) for one in found] == [
        (unit_of(1), (PAGE,)),
        (unit_of(3), (TESTS,)),
        (unit_of(4), (CONTRACT,)),
    ]


def test_a_deleted_page_and_a_deleted_test_file_are_moved(tmp_path):
    _corpus(tmp_path)
    (tmp_path / page_of(1)).unlink()
    (tmp_path / grader_of(2)).unlink()
    assert [one.reasons for one in stale_units(tmp_path)] == [(PAGE,), (TESTS,)]


def test_a_plan_whose_quiz_no_exercise_names_has_moved(tmp_path):
    _corpus(tmp_path, count=1)
    edit_report(tmp_path, 1, lambda document: document.update(quiz="check"))
    assert [one.reasons for one in stale_units(tmp_path)] == [(PLAN,)]


def test_a_report_that_will_not_read_is_stale_by_its_contract(tmp_path):
    _corpus(tmp_path, count=1)
    write(tmp_path, f"{unit_of(1)}/coverage.json", "{ not json\n")
    (stale,) = stale_units(tmp_path)
    assert stale.reasons == (CONTRACT,) and "will not read" in stale.says


def test_a_recorded_path_outside_the_source_is_never_opened_and_is_moved(tmp_path):
    _corpus(tmp_path, count=1)
    edit_report(tmp_path, 1, lambda document: document["digests"].update({"../x.py": "sha256:0"}))
    assert [one.reasons for one in stale_units(tmp_path)] == [(TESTS,)]


def test_a_report_carrying_personal_data_is_refused_before_it_is_read(tmp_path):
    _corpus(tmp_path, count=1)
    edit_report(tmp_path, 1, lambda document: document.update(case=LEAK))
    with pytest.raises(PersonalDataLeak):
        stale_units(tmp_path)


def test_reading_writes_nothing(tmp_path):
    _corpus(tmp_path)
    _move_page(tmp_path, 1)
    _old_contract(tmp_path, 3)
    before = snapshot(tmp_path)
    assert len(stale_units(tmp_path)) == 2
    assert snapshot(tmp_path) == before, "listing the stale units changed the corpus"


# --- removal ------------------------------------------------------------------


def _committed(root):
    init_repository(root)
    run([git(), "add", "-A"], cwd=root)
    identity = ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.org"]
    run([git(), *identity, "commit", "-q", "-m", "authored"], cwd=root)
    return root


def test_removal_takes_exactly_the_listed_folders_and_git_gives_them_back(tmp_path):
    _committed(_corpus(tmp_path))
    _move_page(tmp_path, 2)
    removed = remove_stale(tmp_path, stale_units(tmp_path))
    assert removed == (unit_of(2), practice_of(2))
    assert not (tmp_path / unit_of(2)).exists() and not (tmp_path / practice_of(2)).exists()
    assert (tmp_path / unit_of(1)).is_dir() and (tmp_path / practice_of(3)).is_dir()
    run([git(), "restore", "--", unit_of(2), practice_of(2)], cwd=tmp_path)
    assert (tmp_path / unit_of(2) / "coverage.json").is_file(), "git could not restore it"


def test_removing_nothing_stale_removes_nothing(tmp_path):
    _corpus(tmp_path)
    assert remove_stale(tmp_path, stale_units(tmp_path)) == ()


def _not_a_repository(root):
    return root


def _staged(root):
    _committed(root)
    write(root, "notes.md", "staged\n")
    run([git(), "add", "notes.md"], cwd=root)


def _untracked(root):
    _committed(root)
    write(root, f"{practice_of(2)}/practice-1/scratch.py", "# the reader's own\n")


def _ignored(root):
    write(root, ".gitignore", "*.log\n")
    _committed(root)
    write(root, f"{unit_of(2)}/practice-1/run.log", "output\n")


def _modified(root):
    _committed(root)
    write(root, f"{practice_of(2)}/practice-1/greeting.py", "def greet():\n    return 1\n")


@pytest.mark.parametrize(
    "unsafe",
    [_not_a_repository, _staged, _untracked, _ignored, _modified],
    ids=["no-repository", "staged-change", "untracked-file", "ignored-file", "modified-file"],
)
def test_a_removal_git_could_not_give_back_is_refused_and_removes_nothing(tmp_path, unsafe):
    _corpus(tmp_path)
    unsafe(tmp_path)
    _move_page(tmp_path, 2)
    found = stale_units(tmp_path)
    before = snapshot(tmp_path)
    with pytest.raises(AuthoringError, match="refused, and nothing was removed"):
        remove_stale(tmp_path, found)
    assert snapshot(tmp_path) == before, "a refused removal removed something"
