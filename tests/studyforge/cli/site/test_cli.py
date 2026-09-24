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
    # ⛔ Both fixture corpora, so a command that only worked on the flat one
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
    """⛔ The report is a path-for-path diff against `studyforge
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
# ⛔ A declaration the build cannot read is refused, never raised
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
    # ⚠️ Every instrument must agree on this layout: a build that replaced two
    # of its four pages while `plan` exited 0 would pass unseen.
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
    assert pages == [
        "src/study/first.unit-01-shared-1.unit.html",
        "src/study/first.unit-02-shared-2.unit.html",
        "src/study/second.unit-01-shared-1.unit.html",
        "src/study/second.unit-02-shared-2.unit.html",
    ]
    assert pages == sorted(c.path for c in plan.creations if c.path.endswith(".unit.html"))


def test_a_path_two_units_claim_is_refused_by_name_by_plan_and_build_and_nothing_is_written(
    tmp_path,
):
    root = corpora.repeated_label(tmp_path / "c")
    out = tmp_path / "site"
    out.mkdir()
    assert "duplicate-path" in validate(root).rules
    plan = plan_for(root)
    code, printed = invoke(str(root), "--out", str(out))
    assert plan.exit_code == INVALID
    assert code == INVALID
    for said in ("\n".join(plan.lines()), printed):
        assert "unit 2's page is placed at 'src/study/first.1-shared.unit.html'" in said
        assert "unit 1's page already claims" in said
    assert "build refused" in printed
    assert list(out.iterdir()) == []


# --------------------------------------------------------------------------
# ⛔ A crossed media limit stops the build and says so (§5)
# --------------------------------------------------------------------------

#: The bytes the depth1 fixture's own media weighs once a build has copied it
#: into the unit directory its page addresses. ⚠️ Read off the build below
#: rather than asserted as a figure: a fixture may gain a file.
OVER_AFTER_A_BUILD = {"max_total_bytes": 100, "max_file_bytes": 50}


def a_corpus_with_clips(tmp_path, sizes=(), **limits):
    """A depth1 copy declaring `limits`, with clips of `sizes` bytes in its first unit."""
    from studyforge.corpus.placement import AUDIO_DIRNAME
    from studyforge.generate import read_corpus, unit_location

    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "depth1", root)
    manifest = json.loads((root / "corpus.json").read_text("utf-8"))
    manifest["media"] = {"commit": "auto", **limits}
    if "max_files" in limits:
        # ⛔ R9: `media.max_files` is `corpus_api` 3's key, declared and never inferred.
        manifest["corpus_api"] = 3
    (root / "corpus.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    corpus = read_corpus(root)
    audio = root / str(unit_location(corpus, corpus.units[0]).media_dir(AUDIO_DIRNAME))
    audio.mkdir(parents=True)
    for n, size in enumerate(sizes):
        (audio / f"clip-{n}.mp3").write_bytes(b"x" * size)
    return root


def test_W314_a_corpus_inside_its_limits_builds_and_exits_zero(tmp_path):
    # ⭐ The other way round (R12): the stop is a stop, not a new floor.
    root = a_corpus_with_clips(tmp_path, (10, 20), max_total_bytes=5000, max_file_bytes=1000)
    out = tmp_path / "site"
    out.mkdir()
    code, printed = invoke(str(root), "--out", str(out))
    assert code == OK, printed
    assert "crossed" not in printed
    assert (out / "index.html").is_file()


@pytest.mark.parametrize(
    ("limits", "crossed"),
    [
        ({"max_total_bytes": 50, "max_file_bytes": 100}, "max_total_bytes crossed: 60 byte(s)"),
        ({"max_total_bytes": 500, "max_file_bytes": 25}, "max_file_bytes crossed: 30 byte(s)"),
        (
            {"max_total_bytes": 500, "max_file_bytes": 100, "max_files": 2},
            "max_files crossed: 3 file(s)",
        ),
    ],
)
def test_W314_media_already_over_a_limit_refuses_the_build_and_writes_nothing(
    tmp_path, limits, crossed
):
    root = a_corpus_with_clips(tmp_path, (10, 20, 30), **limits)
    out = tmp_path / "site"
    out.mkdir()

    code, printed = invoke(str(root), "--out", str(out))

    assert code == INVALID
    assert crossed in printed
    assert "build refused" in printed and "nothing was written" in printed
    assert list(out.iterdir()) == []


def test_W314_the_refusal_names_the_ways_forward_and_the_file_responsible(tmp_path):
    # ⛔ A refusal with no way forward is a wall, and one that does not name the
    # file responsible sends a person looking. Both sentences are the verdict's
    # own, so this reads them through the command rather than writing them here.
    from studyforge.corpus.media import WAYS_FORWARD

    root = a_corpus_with_clips(tmp_path, (60,), max_total_bytes=500, max_file_bytes=50)
    out = tmp_path / "site"
    out.mkdir()
    _, printed = invoke(str(root), "--out", str(out))
    for way in WAYS_FORWARD:
        assert way in printed
    assert "clip-0.mp3" in printed


def test_W314_media_this_build_wrote_over_a_limit_stops_it_after_the_site_is_written(tmp_path):
    # ⛔ A build into the corpus root copies the archive's media into the unit
    # directory its page addresses, and those bytes are weighable only once
    # they exist — predicting them would be a second measurement (§5). So the
    # build re-measures, and the non-zero exit lands before anything is
    # committed.
    root = a_corpus_with_clips(tmp_path, **OVER_AFTER_A_BUILD)

    code, printed = invoke(str(root), "--out", str(root))

    assert code == INVALID
    assert "wrote index.html" in printed
    assert "max_total_bytes crossed" in printed
    assert "build stopped" in printed and "commit nothing yet" in printed


def test_W314_the_same_build_under_limits_that_fit_exits_zero(tmp_path):
    # ⭐ The same run, asserted the other way: what stops it is the limit and
    # not the fact that a build into the corpus root writes media at all.
    root = a_corpus_with_clips(tmp_path, max_total_bytes=5_000_000, max_file_bytes=1_000_000)
    code, printed = invoke(str(root), "--out", str(root))
    assert code == OK, printed
    assert "crossed" not in printed


@pytest.mark.parametrize("commit", ["always", "never"])
def test_W314_a_policy_whose_limits_are_inapplicable_never_stops_the_build(commit, tmp_path):
    root = a_corpus_with_clips(tmp_path, (10, 20, 30), max_total_bytes=1, max_file_bytes=1)
    manifest = json.loads((root / "corpus.json").read_text("utf-8"))
    manifest["media"] = {**manifest["media"], "commit": commit}
    (root / "corpus.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    out = tmp_path / "site"
    out.mkdir()
    code, printed = invoke(str(root), "--out", str(out))
    assert code == OK, printed
    assert "crossed" not in printed


def test_W314_a_reading_that_could_not_be_taken_is_a_stop_only_after_the_build(tmp_path):
    # ⛔ Never silently committable: a footprint that could not be weighed after
    # the build is said and exits 1. ⭐ Before one it is not this command's
    # refusal — the build's own reader refuses the same record with its own
    # exit code, and refusing here would answer it twice with two codes.
    from studyforge.cli.plan import MediaProjection
    from studyforge.cli.site.cli import media_stop
    from studyforge.corpus.manifest import DEFAULT_MEDIA

    unweighed = MediaProjection(DEFAULT_MEDIA, units=3, unmeasured="the record cannot be read")

    assert media_stop(unweighed, measured=False) == ""
    assert "the record cannot be read" in media_stop(unweighed, measured=True)
    assert media_stop(None, measured=True) == ""


def test_W314_an_unreadable_narration_record_never_lets_a_build_exit_zero(tmp_path):
    # ⭐ The end the command actually has today, read rather than assumed: the
    # build's own reader refuses the record before the site is written.
    root = a_corpus_with_clips(tmp_path, max_total_bytes=5_000_000, max_file_bytes=1_000_000)
    (root / ".studyforge").mkdir(exist_ok=True)
    (root / ".studyforge" / "narration.json").write_text("{not json", encoding="utf-8")
    out = tmp_path / "site"
    out.mkdir()

    code, printed = invoke(str(root), "--out", str(out))

    assert code != OK
    assert "narration record" in printed
    assert list(out.iterdir()) == []
