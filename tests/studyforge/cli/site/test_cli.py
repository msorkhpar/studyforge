"""Mirror of `src/studyforge/cli/site/cli.py` (R12).

⛔ **Every case writes into `tmp_path` and never into the repository.** A build
command is the exact shape that puts stray files in a working tree, and a test
that used a relative default would be the first one to do it.
"""

from __future__ import annotations

import io
import json
import shutil

import pytest

from studyforge.cli.plan import plan_for
from studyforge.cli.site.cli import build_parser, main
from studyforge.validate import validate
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES
from tests.studyforge.validate import corpora
from tests.support import repository_root


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


# --------------------------------------------------------------------------
# ⛔ `W212` — a declaration the build cannot read is refused, never raised
# --------------------------------------------------------------------------

#: ⛔ Assembled rather than written whole (R7's sweep reads this file).
HOME = "/" + "home/jane"


def a_corpus_whose_first_map_has(tmp_path, fixture, **fields):
    """A fixture copy with fields replaced in its first container map, and that map's path."""
    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / fixture, root)
    path = sorted((root / "archive").rglob("container.json"))[0]
    path.write_text(json.dumps({**json.loads(path.read_text("utf-8")), **fields}), "utf-8")
    (tmp_path / "out").mkdir()
    return root, path.relative_to(root).as_posix()


def test_a_wrong_depth_container_map_is_refused_naming_the_file_and_the_depth(tmp_path):
    # ⛔ Through the verb, with the refusal's presence as the pass condition.
    root, where = a_corpus_whose_first_map_has(
        tmp_path, "depth2", address=["basics"], titles=["Basics"]
    )
    code, printed = invoke(str(root), "--out", str(tmp_path / "out"))
    assert code == UNUSABLE
    assert printed.startswith(f"{where}: ")
    assert "the corpus declares 2 level(s)" in printed
    assert str(tmp_path) not in printed, "R7: a refusal never carries a path"
    assert list((tmp_path / "out").iterdir()) == []


def test_a_leaking_container_map_is_refused_and_not_a_traceback(tmp_path):
    # ⭐ The pass-through `BuildError` alone missed: it left `main` as an
    # exception whose traceback names absolute paths (R7).
    root, where = a_corpus_whose_first_map_has(tmp_path, "depth1", note=f"from {HOME}/corpus")
    code, printed = invoke(str(root), "--out", str(tmp_path / "out"))
    assert code == UNUSABLE
    assert where in printed and "home path" in printed
    assert "jane" not in printed


def test_a_leaking_manifest_is_refused_and_not_a_traceback(tmp_path):
    root, _ = a_corpus_whose_first_map_has(tmp_path, "depth1")
    document = json.loads((root / "corpus.json").read_text("utf-8"))
    (root / "corpus.json").write_text(json.dumps({**document, "title": f"{HOME}/x"}), "utf-8")
    code, printed = invoke(str(root), "--out", str(tmp_path / "out"))
    assert code == UNUSABLE
    assert "corpus.json" in printed and "jane" not in printed


def test_the_catch_list_is_the_build_s_own_tuple_and_not_a_copy():
    source = (repository_root() / "src/studyforge/cli/site/cli.py").read_text("utf-8")
    assert "except RAISES as refusal:" in source
    assert "except BuildError" not in source and "except (BuildError" not in source


# --------------------------------------------------------------------------
# ⛔ `INT09-5`: validate, plan and a build agree about a collision
# --------------------------------------------------------------------------


def test_a_mirrored_series_builds_one_page_per_unit_and_every_instrument_agrees(tmp_path):
    # ⚠️ Measured at `973fc67`: `validate` refused this layout while `plan` and a
    # build exited 0, and the build replaced two of its four pages.
    root = corpora.mirrored(tmp_path / "c")
    out = tmp_path / "site"
    out.mkdir()
    assert validate(root).findings == ()
    plan = plan_for(root)
    assert (plan.exit_code, plan.refusals) == (OK, ())
    code, printed = invoke(str(root), "--out", str(out))
    pages = sorted(page.relative_to(out).as_posix() for page in out.rglob("*.unit.html"))
    assert code == OK, printed
    assert "replace " not in printed
    assert len(pages) == 4
    assert pages == sorted(c.path for c in plan.creations if c.path.endswith(".unit.html"))


def test_a_collision_the_container_cannot_separate_is_refused_by_name_by_plan_and_build(tmp_path):
    root = corpora.mirrored(tmp_path / "c", separable=False)
    out = tmp_path / "site"
    out.mkdir()
    assert "duplicate-path" in validate(root).rules
    plan = plan_for(root)
    code, printed = invoke(str(root), "--out", str(out))
    assert plan.exit_code == INVALID
    assert code == UNUSABLE
    for said in ("\n".join(plan.lines()), printed):
        assert "first/series unit 1's page" in said
        assert "second/series unit 1's page" in said
        assert "'src/series-unit-01-shared-1.unit.html'" in said
    assert list(out.iterdir()) == []
