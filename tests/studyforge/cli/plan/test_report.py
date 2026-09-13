"""Mirror of `src/studyforge/cli/plan/report.py` (R12).

What a plan *says*, asked of the records directly, so that the rendering is
tested without a corpus root and the derivation is tested without a renderer.
"""

from __future__ import annotations

import pytest

from studyforge.cli.plan.report import (
    UNPROJECTED,
    Creation,
    MediaProjection,
    Plan,
    Refusal,
    edit_lines,
)
from studyforge.corpus.manifest import DEFAULT_MEDIA, MediaPolicy, PermittedEdit
from studyforge.corpus.placement import UNIT_MEDIA_DIRNAMES
from studyforge.validate.report import INVALID, OK

EDIT = PermittedEdit(
    path="pom.xml",
    kind="insert-line",
    anchor="<modules>",
    content="  <module>practice</module>",
    why="Maven compiles only what sits on a source root (spec 7).",
)


def a_plan(**overrides) -> Plan:
    """A minimal plan, with whatever the test is about overridden."""
    fields = {
        "source": "demo",
        "title": "A Demo",
        "profile": "tree",
        "describes": "all output under one generated root",
        "read_files": ("corpus.json",),
        "creations": (),
        "edits": (),
        "ignore": (),
        "media": None,
    }
    return Plan(**{**fields, **overrides})


# --------------------------------------------------------------------------
# one fact per line
# --------------------------------------------------------------------------


def test_a_creation_renders_as_one_greppable_line():
    assert Creation("index.html", "the root index").line() == "create index.html  the root index"


def test_a_refusal_renders_as_one_greppable_line():
    assert Refusal("archive/a/container.json", "no origin").line().startswith("refuse ")


def test_every_verb_is_the_first_token_of_its_line():
    # ⛔ The closed set. A consumer greps by verb and a person reads by verb;
    # a line whose first token is something else is invisible to both.
    plan = a_plan(
        creations=(Creation("index.html", "the root index"),),
        edits=(EDIT,),
        ignore=("*.unit.html",),
        media=MediaProjection(DEFAULT_MEDIA, 1),
        refusals=(Refusal("x", "y"),),
    )
    verbs = {line.split(" ", 1)[0] for line in plan.lines()}
    assert verbs <= {
        "plan",
        "plan:",
        "placement",
        "read",
        "create",
        "edit",
        "ignore",
        "media",
        "refuse",
    }


# --------------------------------------------------------------------------
# ⛔ the declared edits, named with their reasons
# --------------------------------------------------------------------------


def test_one_edit_gets_four_lines_and_all_four_name_the_file():
    lines = edit_lines(EDIT)
    assert len(lines) == 4
    assert all(line.startswith("edit pom.xml  ") for line in lines)


def test_the_edit_lines_carry_the_anchor_the_addition_the_reason_and_the_undo():
    what, adds, why, undo = edit_lines(EDIT)
    assert "insert-line after '<modules>'" in what
    assert EDIT.content in adds
    assert EDIT.why in why
    assert "remove-line" in undo and EDIT.content in undo


def test_the_undo_line_reproduces_the_line_being_removed():
    # ⚠️ Composed from `Reversal`'s fields, because its own `__str__` renders
    # the content as *"a str"* — right for a refusal, useless in a plan.
    # Finding `SF-31/1`; asserted here so a later fix cannot silently
    # re-introduce the unreadable form.
    assert "a str" not in edit_lines(EDIT)[3]


# --------------------------------------------------------------------------
# ⛔ the media projection, and whether it fits
# --------------------------------------------------------------------------


def test_with_no_rate_the_footprint_says_it_is_unprojected_and_why():
    lines = MediaProjection(DEFAULT_MEDIA, 5).lines()
    assert any(UNPROJECTED in line for line in lines)


def test_the_unprojected_sentence_names_who_owes_the_measurement():
    # ⛔ A number invented here would be a guess wearing a measurement's
    # clothes; naming the owner is what makes the gap actionable instead.
    assert "SF-32" in UNPROJECTED


def test_a_rate_that_fits_says_so_with_both_numbers():
    projection = MediaProjection(MediaPolicy("auto", 1000, 100), units=4, bytes_per_unit=200)
    footprint = [line for line in projection.lines() if line.startswith("media footprint")][0]
    assert projection.total == 800
    assert "fits" in footprint and "800" in footprint and "1000" in footprint


def test_a_rate_that_does_not_fit_names_the_number_and_the_limit_it_crossed():
    projection = MediaProjection(MediaPolicy("auto", 1000, 100), units=4, bytes_per_unit=400)
    footprint = [line for line in projection.lines() if line.startswith("media footprint")][0]
    assert "EXCEEDS max_total_bytes" in footprint
    assert "1600" in footprint and "1000" in footprint


def test_the_unit_count_is_reported_even_when_the_footprint_is_not():
    # ⭐ "Will this corpus's audio fit in git?" has a knowable half before the
    # gigabytes exist, and it is printed rather than withheld with the rest.
    lines = MediaProjection(DEFAULT_MEDIA, 17).lines()
    assert any(line.startswith("media units 17") for line in lines)


def test_the_media_kinds_come_from_placements_own_tuple():
    # ⛔ Never retyped: a fifth kind must not leave this sentence listing four.
    units = [line for line in MediaProjection(DEFAULT_MEDIA, 1).lines() if "units" in line][0]
    for kind in UNIT_MEDIA_DIRNAMES:
        assert kind in units


@pytest.mark.parametrize("commit", ["always", "never"])
def test_only_auto_consults_the_limits_and_the_others_say_so(commit):
    lines = MediaProjection(MediaPolicy(commit, 1, 1), 3).lines()
    assert any("not consulted" in line for line in lines)
    assert not any(line.startswith("media limit ") for line in lines)


def test_media_is_ignored_only_when_the_policy_does_not_commit_it():
    # ⛔ Generated media is committed by DEFAULT (§5). A framework that ignored
    # a corpus's narration by reflex produces clones that are silent with no
    # error, which is the outcome the whole policy exists to refuse.
    assert MediaProjection(DEFAULT_MEDIA, 1).ignored is False
    assert MediaProjection(MediaPolicy("always", 1, 1), 1).ignored is False
    assert MediaProjection(MediaPolicy("never", 1, 1), 1).ignored is True


# --------------------------------------------------------------------------
# the plan as a whole
# --------------------------------------------------------------------------


def test_the_summary_prints_every_count_including_the_zeroes():
    # ⚠️ A number that disappears when it is zero cannot be told from a number
    # nobody wrote, and "this build edits nothing of yours" is the one line a
    # repository owner most wants stated.
    summary = a_plan().summary()
    assert "0 path(s) to create" in summary
    assert "0 file(s) to edit" in summary
    assert "0 ignore line(s)" in summary
    assert "0 refusal(s)" in summary


def test_a_plan_with_no_refusals_exits_zero_and_one_with_any_exits_one():
    assert a_plan().exit_code == OK
    assert a_plan(refusals=(Refusal("x", "y"),)).exit_code == INVALID


def test_paths_is_what_ops_05_compares_a_finished_build_against():
    plan = a_plan(creations=(Creation("a", "one"), Creation("b", "two")))
    assert plan.paths == ("a", "b")


def test_the_header_says_how_much_was_read_and_that_none_of_it_was_material():
    read = a_plan(read_files=("corpus.json", "archive/x/container.json")).lines()[2]
    assert read.startswith("read corpus.json + 1 container.json")
    assert "no file inside the source material was opened" in read


def test_a_plan_with_no_media_projection_prints_no_media_line():
    # The corpus whose manifest would not parse: there is no policy to report,
    # and inventing one would be a claim nothing here is entitled to make.
    assert not [line for line in a_plan().lines() if line.startswith("media ")]


def test_the_read_line_counts_container_maps_and_names_the_narration_record():
    read = a_plan(
        read_files=("corpus.json", "archive/x/container.json", ".studyforge/narration.json")
    ).lines()[2]
    assert read.startswith("read corpus.json + 1 container.json + .studyforge/narration.json  ")


def test_a_creation_is_not_narration_unless_it_says_so_and_its_line_is_unchanged():
    plain = Creation("a/audio/", "one")
    marked = Creation("a/audio/", "one", narration=True)
    assert not plain.narration
    assert marked.line() == plain.line() == "create a/audio/  one"


def test_an_ignore_line_names_the_file_that_holds_it():
    # ⛔ INT-06/8: a rule with no named file is a rule pasted into the root
    # ignore file, which R3 forbids however declared.
    lines = a_plan(ignore=("**/audio/",), ignore_home=".studyforge/.gitignore").lines()
    assert "ignore **/audio/  in .studyforge/.gitignore" in lines
