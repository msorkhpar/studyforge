"""Mirror of `src/studyforge/cli/plan/cli.py` (R12).

⛔ **The golden files are asserted here**, because a golden is what the command
prints and not what a dataclass holds.
"""

from __future__ import annotations

import io

import pytest

from studyforge.cli.plan.cli import UNUSABLE, build_parser, main
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES, VALID

#: Where the goldens live, one per valid corpus. ⚠️ Beside the fixtures rather
#: than inside one:
#: a plan describes what would be written **into** a corpus root, so a golden
#: sitting in that root is a file the plan would have to explain.
GOLDEN = FIXTURES / "golden"


def invoke(*argv):
    """Run the CLI, returning `(exit code, what it printed)`."""
    out = io.StringIO()
    return main(list(argv), out=out), out.getvalue()


# --------------------------------------------------------------------------
# the interface
# --------------------------------------------------------------------------


def test_the_parser_takes_one_root_and_says_what_it_is_for():
    parser = build_parser()
    assert parser.prog == "studyforge plan"
    assert "before anything is generated" in parser.description


def test_the_rate_is_optional_and_defaults_to_no_projection():
    assert build_parser().parse_args(["somewhere"]).bytes_per_unit is None
    assert build_parser().parse_args(["x", "--bytes-per-unit", "7"]).bytes_per_unit == 7


# --------------------------------------------------------------------------
# ⛔ the three exit codes
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", VALID)
def test_a_corpus_that_plans_cleanly_exits_zero(name):
    code, printed = invoke(str(FIXTURES / name))
    assert code == OK
    assert printed.startswith("plan ")


def test_a_corpus_that_cannot_be_planned_exits_one(tmp_path):
    code, printed = invoke(str(tmp_path))
    assert code == INVALID
    assert "refuse corpus.json" in printed


def test_a_root_that_is_not_a_directory_exits_two_and_says_so(tmp_path):
    # ⛔ Distinct from INVALID: a script that cannot tell "your corpus is
    # broken" from "you gave me a path that is not there" treats one as the
    # other, and CI goes green on a typo.
    code, printed = invoke(str(tmp_path / "nowhere"))
    assert code == UNUSABLE
    assert printed.strip().endswith(": not a directory")


def test_the_unusable_message_names_what_was_asked_for_not_where_it_resolved(tmp_path):
    # ⛔ R7: a plan is the most-pasted artifact this command produces.
    _, printed = invoke("no-such-corpus")
    assert printed.strip() == "no-such-corpus: not a directory"


# --------------------------------------------------------------------------
# ⛔ the golden files (FND-04's largest deferred golden, closed here)
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", VALID)
def test_the_output_is_byte_for_byte_the_committed_golden(name):
    """⛔ R10, and the reason the golden exists at all.

    `FND-04` could not write this one: §5 pins the *kinds* of path and not
    artifact naming, and `SF-03` owns the derivation. It is written here
    instead, beside the contract that produces it.
    """
    _, printed = invoke(str(FIXTURES / name))
    assert printed == (GOLDEN / f"{name}.plan.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", VALID)
def test_two_runs_of_one_corpus_agree_byte_for_byte(name):
    # ⛔ No clock, no filesystem enumeration order, no set iteration (R10).
    assert invoke(str(FIXTURES / name)) == invoke(str(FIXTURES / name))


def test_the_goldens_are_one_per_valid_corpus_and_exactly_what_is_on_disk():
    # ⚠️ The name used to say "two". It is read from `VALID` and has been three
    # since `W95`, and a test name that states a count states it in the one
    # place nothing checks.
    on_disk = sorted(p.name for p in GOLDEN.iterdir())
    assert on_disk == sorted(f"{name}.plan.txt" for name in VALID)


@pytest.mark.parametrize("name", VALID)
def test_the_golden_carries_no_personal_data(name):
    # ⛔ R7, asked with the framework's own gate rather than a pattern of this
    # test's. A golden is committed, so a home path in one is permanent — and
    # `tests/test_fixture_consistency.py` sweeps the whole fixture tree for
    # exactly this, which is the second, independent end of the same claim.
    from tests.fixture_checks import shape_in

    assert shape_in((GOLDEN / f"{name}.plan.txt").read_text(encoding="utf-8")) is None


@pytest.mark.parametrize("name", VALID)
def test_every_path_the_golden_names_is_relative_to_the_corpus_root(name):
    text = (GOLDEN / f"{name}.plan.txt").read_text(encoding="utf-8")
    named = [line.split("  ")[0].removeprefix("create ") for line in text.splitlines()]
    assert [p for p in named if p.startswith(("/", "~"))] == []


# --------------------------------------------------------------------------
# what a person reads
# --------------------------------------------------------------------------


def test_the_plan_says_which_profile_it_used_and_what_that_profile_does():
    _, printed = invoke(str(FIXTURES / "depth2"))
    assert "placement sibling  each artifact beside the source file" in printed


def test_the_rate_reaches_the_projection_through_the_command_line():
    _, printed = invoke(str(FIXTURES / "depth2"), "--bytes-per-unit", "1")
    assert "media footprint  fits" in printed


# --------------------------------------------------------------------------
# ⛔ `W314` — a crossed limit reaches the exit code, through `main`
# --------------------------------------------------------------------------


def a_corpus_with_clips(tmp_path, sizes, **limits):
    """A depth1 copy declaring `limits`, with clips of `sizes` bytes in its first unit."""
    import json
    import shutil

    from studyforge.corpus.manifest import MANIFEST_FILENAME
    from studyforge.corpus.placement import AUDIO_DIRNAME
    from studyforge.generate import read_corpus, unit_location

    root = tmp_path / "corpus"
    shutil.copytree(FIXTURES / "depth1", root)
    manifest = json.loads((root / MANIFEST_FILENAME).read_text("utf-8"))
    manifest["media"] = {"commit": "auto", **limits}
    (root / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    corpus = read_corpus(root)
    audio = root / str(unit_location(corpus, corpus.units[0]).media_dir(AUDIO_DIRNAME))
    audio.mkdir(parents=True)
    for n, size in enumerate(sizes):
        (audio / f"clip-{n}.mp3").write_bytes(b"x" * size)
    return root


def test_W314_a_corpus_over_a_limit_exits_one_and_names_the_number_and_the_limit(tmp_path):
    root = a_corpus_with_clips(tmp_path, (10, 20, 30), max_total_bytes=50, max_file_bytes=100)
    code, printed = invoke(str(root))
    assert code == INVALID
    assert "media footprint  EXCEEDS" in printed
    assert "max_total_bytes crossed: 60 byte(s) against a limit of 50" in printed
    assert printed.rstrip().endswith("1 refusal(s)")


def test_W314_a_corpus_inside_its_limits_still_exits_zero(tmp_path):
    root = a_corpus_with_clips(tmp_path, (10, 20, 30), max_total_bytes=500, max_file_bytes=100)
    code, printed = invoke(str(root))
    assert code == OK
    assert "media footprint  fits" in printed
