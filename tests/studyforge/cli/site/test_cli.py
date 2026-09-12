"""Mirror of `src/studyforge/cli/site/cli.py` (R12).

⛔ **Every case writes into `tmp_path` and never into the repository.** A build
command is the exact shape that puts stray files in a working tree, and a test
that used a relative default would be the first one to do it.
"""

from __future__ import annotations

import io

import pytest

from studyforge.cli.site.cli import build_parser, main
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES


def invoke(*argv):
    """Run the CLI, returning `(exit code, what it printed)`."""
    out = io.StringIO()
    return main(list(argv), out=out), out.getvalue()


# --------------------------------------------------------------------------
# the interface
# --------------------------------------------------------------------------


def test_the_parser_takes_a_root_and_an_output_directory():
    parser = build_parser()
    assert parser.prog == "studyforge build"
    arguments = parser.parse_args(["corpus", "--out", "site"])
    assert (arguments.root, arguments.out) == ("corpus", "site")


def test_the_output_directory_is_required_and_has_no_default():
    # ⛔ The row that matters: where a build writes is an open decision, and a
    # default here would answer it by convention. Requiring the flag defers it
    # to the person running the command.
    with pytest.raises(SystemExit):
        build_parser().parse_args(["corpus"])


def test_the_help_says_why_there_is_no_default():
    # ⚠️ Read off the action rather than the formatted help, which argparse
    # rewraps to the terminal's width and would make this assertion depend on it.
    out = [action for action in build_parser()._actions if action.dest == "out"]
    assert out and "the corpus owner's decision" in (out[0].help or "")


# --------------------------------------------------------------------------
# what it does
# --------------------------------------------------------------------------


def test_it_builds_a_corpus_into_the_named_directory(tmp_path):
    code, printed = invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path))
    assert code == OK
    assert (tmp_path / "index.html").is_file()
    assert printed.splitlines()[0].startswith("build ")
    assert "wrote index.html" in printed


def test_it_builds_the_deeper_fixture_too(tmp_path):
    # ⛔ Both `FND-04` fixtures, so a command that only worked on the flat one
    # could not pass.
    code, _ = invoke(str(FIXTURES / "depth2"), "--out", str(tmp_path))
    assert code == OK
    assert (tmp_path / "index.html").is_file()


def test_a_second_run_rebuilds_its_own_output_and_exits_zero(tmp_path):
    """⛔ *Build, edit a lesson, build again* has to be usable from a script.

    ⭐ This clause asserted the OPPOSITE before the rebuild policy: exit `1`,
    every path refused, no site. ⚠️ A replacement is NOT a refusal, and the
    exit code is what a script reads.
    """
    invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path))
    code, printed = invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path))
    assert code == OK
    assert "replace index.html" in printed
    assert "refuse " not in printed


def test_a_rebuild_prints_each_path_exactly_once(tmp_path):
    """⛔ Ruling 99: the report is a path-for-path diff against `studyforge
    plan`, and a path printed as both `wrote` and `replace` breaks the diff."""
    invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path))
    _, printed = invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path))

    subjects = [
        line.split()[1]
        for line in printed.splitlines()
        if line.startswith(("wrote ", "replace ", "refuse "))
    ]

    assert subjects
    assert len(subjects) == len(set(subjects))


def test_a_file_the_plan_never_declared_survives_a_rebuild_untouched(tmp_path):
    """⛔ The other half of the decision, through the command: R3 is absolute
    for everything outside the footprint."""
    mine = b"a reader's own file"
    (tmp_path / "notes.txt").write_bytes(mine)

    invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path))
    code, _ = invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path))

    assert code == OK
    assert (tmp_path / "notes.txt").read_bytes() == mine


def test_a_directory_where_a_declared_page_belongs_still_exits_one(tmp_path):
    """⭐ The refusal exit code is still reachable, and still named."""
    (tmp_path / "index.html").mkdir()

    code, printed = invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path))

    assert code == INVALID
    assert "refuse index.html" in printed
    assert (tmp_path / "index.html").is_dir()


def test_a_corpus_root_that_is_not_a_directory_is_unusable(tmp_path):
    code, printed = invoke(str(tmp_path / "nowhere"), "--out", str(tmp_path))
    assert code == UNUSABLE
    assert "not a directory" in printed


def test_a_bad_corpus_root_creates_nothing_under_the_output_directory(tmp_path):
    # ⛔ A typo in the corpus root must not leave a tree behind to clean up.
    out = tmp_path / "site"
    out.mkdir()
    invoke(str(tmp_path / "nowhere"), "--out", str(out))
    assert list(out.iterdir()) == []


def test_an_output_root_that_does_not_exist_is_unusable_and_says_so(tmp_path):
    # ⚠️ The build mints its own pages and never its own root. Reported as
    # "could not run" rather than as a verdict about the corpus.
    code, printed = invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path / "missing"))
    assert code == UNUSABLE
    assert "output root" in printed


def test_the_refusal_message_is_not_prefixed_with_the_corpus_root(tmp_path):
    # ⛔ A refusal about `--out` misattributed to the corpus sends its reader to
    # the wrong directory.
    _, printed = invoke(str(FIXTURES / "depth1"), "--out", str(tmp_path / "missing"))
    assert not printed.startswith(str(FIXTURES / "depth1"))
