"""Mirror of `src/studyforge/cli/plan/report.py` (R12).

What a plan *says*, asked of the records directly, so that the rendering is
tested without a corpus root and the derivation is tested without a renderer.
"""

from __future__ import annotations

from studyforge.cli.plan.media import MediaProjection
from studyforge.cli.plan.report import (
    Creation,
    Plan,
    Refusal,
    SupersededClip,
    edit_lines,
)
from studyforge.corpus.manifest import DEFAULT_MEDIA, PermittedEdit
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
        superseded=(SupersededClip("u/audio/old-0123abcd.mp3", "u.intro.b1"),),
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
        "replace",
        "keep",
        "claim",
        "expect",
        "superseded",
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
    # Asserted here so a later fix cannot silently
    # re-introduce the unreadable form.
    assert "a str" not in edit_lines(EDIT)[3]


# --------------------------------------------------------------------------
# the plan as a whole
# --------------------------------------------------------------------------


def test_the_summary_prints_every_count_including_the_zeroes():
    # ⚠️ A number that disappears when it is zero cannot be told from a number
    # nobody wrote, and "this build edits nothing of yours" is the one line a
    # repository owner most wants stated.
    summary = a_plan().summary()
    assert "0 path(s) to create" in summary
    for said in ("0 to replace", "0 to keep", "0 claimed", "0 expected from another command"):
        assert said in summary
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


# --------------------------------------------------------------------------
# ⛔ `W267`: a path's verb says who writes it and whether it is there
# --------------------------------------------------------------------------


def test_a_path_on_disk_is_never_a_create_and_is_named_as_replaced_or_kept():
    assert Creation("index.html", "the root index", present=True).verb == "replace"
    assert Creation("archive/", "the archive", writer="an adapter", present=True).verb == "keep"
    assert Creation("u/audio/", "u's audio", when_filled=True, present=True).verb == "keep"


def test_a_path_a_build_does_not_write_is_never_a_create_and_names_what_does():
    expected = Creation("site.json", "the cache", writer="`studyforge serve`")
    assert expected.verb == "expect"
    assert expected.line() == (
        "expect site.json  the cache — `studyforge serve` writes it; "
        "a build into this root does not"
    )
    claimed = Creation("u/audio/", "u's audio", when_filled=True)
    assert claimed.verb == "claim"
    assert claimed.line().endswith("a build creates it only when it copies a file into it")


def test_W288_a_superseded_clip_is_its_own_line_counted_and_never_a_path():
    clip = SupersededClip("u/audio/u.intro.b1-0123abcd.mp3", "u.intro.b1")
    copy = Creation("u/audio/u.intro.b1-feedbeef.mp3", "copy")
    plan = a_plan(creations=(copy,), superseded=(clip,))
    assert clip.line().startswith("superseded u/audio/u.intro.b1-0123abcd.mp3  u.intro.b1's ")
    assert "no build copies it" in clip.line() and "--prune" in clip.line()
    assert clip.line() in plan.lines()
    assert plan.paths == ("u/audio/u.intro.b1-feedbeef.mp3",)
    assert "1 superseded clip(s) no build copies" in plan.summary()
    assert "0 superseded clip(s)" in a_plan().summary()


def test_the_summary_counts_each_verb_it_printed():
    creations = (
        Creation("a", "one"),
        Creation("b", "two", present=True),
        Creation("c/", "three", when_filled=True),
        Creation("d", "four", writer="x"),
        Creation("e", "five", writer="x", present=True),
    )
    summary = a_plan(creations=creations).summary()
    assert "1 path(s) to create, 1 to replace, 1 to keep, 1 claimed, 1 expected" in summary
