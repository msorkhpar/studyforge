"""Mirror of `tests/floor/size.py` (R12).

The two acceptance cases for the ceiling are `test_oversized_source_module_fails`
and `test_justified_oversized_module_passes`: the ceiling must actually stop a
file, and the documented opt-out must actually let one through.

The deferral cases are the `--- a promise of later work is refused ---` block:
R11 admits a design claim only, so a justification that promises later work is
refused wherever in the paragraph it is written, and a design claim of the same
length passes.

The authored-file cases are the `--- authored stylesheets, scripts and templates ---`
block: the ceiling stops an authored non-Python file under `src/`, and lets a
vendored one through only by its exact path.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.floor import config
from tests.floor.size import (
    AUTHORED_SUFFIXES,
    DESIGN_FORM,
    SPLIT_ONLY,
    VENDORED,
    authored_files,
    check_sizes,
    count_lines,
    module_docstring,
    promises,
    size_exception,
)


def write_module(root: Path, relative: str, text: str) -> Path:
    """Write `text` at `relative` under `root`, creating parents."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def module_of(lines: int, docstring: str = "") -> str:
    """A syntactically valid module of exactly `lines` physical lines."""
    head = f'"""{docstring}"""\n' if docstring else ""
    body_lines = lines - len(head.splitlines())
    return head + "".join(f"x{number} = {number}\n" for number in range(body_lines))


# --- counting --------------------------------------------------------------


def test_count_lines_matches_wc_l():
    assert count_lines("") == 0
    assert count_lines("a\n") == 1
    assert count_lines("a\nb\n") == 2
    assert count_lines("a\nb") == 2  # no trailing newline: the last line counts


def test_module_of_produces_the_length_it_claims():
    assert count_lines(module_of(50)) == 50
    assert count_lines(module_of(50, "one\nSize exception: two")) == 50


# --- the ceiling -----------------------------------------------------------


def test_a_module_under_the_ceiling_passes(tmp_path):
    write_module(tmp_path, "src/studyforge/small.py", module_of(config.SOURCE_LINE_CEILING))
    assert check_sizes(tmp_path) == []


def test_oversized_source_module_fails(tmp_path):
    write_module(tmp_path, "src/studyforge/big.py", module_of(config.SOURCE_LINE_CEILING + 1))
    findings = check_sizes(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "size"
    assert findings[0].path == "src/studyforge/big.py"
    assert "401 lines, ceiling 400" in findings[0].message
    # ⭐ The message has to say how to get through the gate legitimately,
    # or the next person's move is to delete the check.
    assert config.SIZE_EXCEPTION_MARKER in findings[0].message


def test_a_test_module_gets_the_looser_ceiling(tmp_path):
    write_module(
        tmp_path,
        "tests/studyforge/test_big.py",
        module_of(config.SOURCE_LINE_CEILING + 1),
    )
    assert check_sizes(tmp_path) == []

    write_module(
        tmp_path,
        "tests/studyforge/test_bigger.py",
        module_of(config.TEST_LINE_CEILING + 1),
    )
    findings = check_sizes(tmp_path)
    assert [finding.path for finding in findings] == ["tests/studyforge/test_bigger.py"]
    assert "601 lines, ceiling 600" in findings[0].message


# --- the opt-out -----------------------------------------------------------


def test_justified_oversized_module_passes(tmp_path):
    docstring = (
        "A template renderer.\n\n"
        "Size exception: the substitution table is one literal mapping and "
        "splitting it across modules would hide half the placeholders from "
        "the reader of the other half."
    )
    write_module(
        tmp_path,
        "src/studyforge/justified.py",
        module_of(config.SOURCE_LINE_CEILING + 100, docstring),
    )
    assert check_sizes(tmp_path) == []


def test_an_empty_justification_does_not_pass(tmp_path):
    write_module(
        tmp_path,
        "src/studyforge/hollow.py",
        module_of(config.SOURCE_LINE_CEILING + 1, "Thing.\n\nSize exception: yes"),
    )
    findings = check_sizes(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "size-justification"
    assert "3 characters of reason" in findings[0].message


def test_the_marker_must_be_in_the_docstring_not_merely_in_the_file(tmp_path):
    # ⛔ A comment beside the offending code is not a contract. The exception
    # is recorded where the next reader of the module will meet it: the top.
    body = module_of(config.SOURCE_LINE_CEILING + 1)
    body += "# Size exception: a comment is not a contract and must not count here\n"
    write_module(tmp_path, "src/studyforge/sneaky.py", body)
    findings = check_sizes(tmp_path)
    assert len(findings) == 1
    assert findings[0].rule == "size"


def test_the_marker_is_the_ruled_literal_and_case_sensitive():
    # ⛔ Case-sensitive by R11. Every reader looks for `Size
    # exception:` exactly, so a lowercase variant must be reported as no
    # exception claimed rather than quietly accepted here and rejected there.
    assert size_exception("Thing.\n\nSize exception: because it is one table.") == (
        "because it is one table."
    )
    assert size_exception("Thing.\n\nsize-exception: because it is one table.") is None
    assert size_exception("Thing.") is None
    assert size_exception(None) is None


def test_an_unparseable_module_is_measured_anyway(tmp_path):
    # A file too broken to parse still has a length, and reporting it is the
    # safe direction: the alternative is a syntax error that also silently
    # buys an exemption from the ceiling.
    body = module_of(config.SOURCE_LINE_CEILING + 1) + "def (\n"
    path = write_module(tmp_path, "src/studyforge/broken.py", body)
    assert module_docstring(path.read_text("utf-8"), path) is None
    assert [finding.rule for finding in check_sizes(tmp_path)] == ["size"]


# --- a promise of later work is refused ------------------------------------------

# ⚠️ Fixtures written the way a module would write one, as literals. ⛔ Each is a
# promise that later work will split the module: one names a work item on the
# marker line, one names it a line further down, and one names nothing at all.
DEFERRAL_BY_ID = (
    "The two checks that read the material.\n"
    "\n"
    "Size exception: W44 splits this module into a package, and it is left here\n"
    "because this file crossed the ceiling only when two branches merged.\n"
)

DEFERRAL_WRAPPED = (
    "The two checks that read the material.\n"
    "\n"
    "Size exception: this module is split into a package by the task that owns\n"
    "it, AB-35, because the file crossed the ceiling only when two branches merged.\n"
)

DEFERRAL_IN_WORDS = (
    "The two checks that read the material.\n"
    "\n"
    "Size exception: the split into a package is deferred until the two readers\n"
    "settle, because moving them now would conflict with the work on both.\n"
)

#: A design claim: why splitting would be worse. ⭐ It cites a rule, which is
#: not a promise of anything.
DESIGN_CLAIM = (
    "A template renderer.\n\nSize exception: the substitution table is one\n"
    "literal mapping and splitting it across modules would hide half the\n"
    "placeholders from the reader of the other half. R11 permits this."
)


def oversized(tmp_path: Path, name: str, docstring: str) -> list:
    write_module(
        tmp_path,
        f"src/studyforge/{name}.py",
        module_of(config.SOURCE_LINE_CEILING + 25, docstring.strip("\n")),
    )
    return check_sizes(tmp_path)


def test_the_justification_is_the_whole_paragraph_not_the_marker_line():
    # ⛔ A reader that stopped at the line break would print, in a sweep,
    # whatever reason fitted on one line, and would miss a promise below it.
    reason = size_exception(DEFERRAL_WRAPPED)
    assert reason.startswith("this module is split into a package")
    assert reason.endswith("only when two branches merged.")
    assert "\n" not in reason  # joined, so a sweep can print it on one line


def test_the_justification_stops_at_the_next_blank_line():
    docstring = (
        "Thing.\n\nSize exception: one table, and splitting it would hide half\n"
        "the placeholders from the reader of the other half.\n"
        "\nDepends on. Nothing, and this paragraph is not the reason.\n"
    )
    reason = size_exception(docstring)
    assert reason.endswith("the reader of the other half.")
    assert "Depends on" not in reason


def test_promises_finds_work_items_and_deferral_words_and_nothing_else():
    assert promises("W44 splits this module") == ["W44"]
    assert promises("AB-35 and AB-36 merged") == ["AB-35", "AB-36"]
    assert promises("ABC-05a is the task") == ["ABC-05a"]
    assert promises("W44, and again W44") == ["W44"]  # deduplicated, order kept
    assert promises("the split is deferred until later") == ["deferred", "later"]
    assert promises("TODO: split it") == ["TODO"]
    # ⛔ A rule, a milestone, a constraint and an epic are not work anybody
    # promises. A design claim must stay free to cite them.
    assert promises("R11 is the ceiling, M2 the milestone, C5 a state, E08 an epic") == []
    assert promises("") == []
    assert promises(None) == []


@pytest.mark.parametrize(
    ("docstring", "named"),
    [
        pytest.param(DEFERRAL_BY_ID, "W44", id="work-item-on-the-marker-line"),
        pytest.param(DEFERRAL_WRAPPED, "AB-35", id="work-item-past-the-wrap"),
        pytest.param(DEFERRAL_IN_WORDS, "deferred", id="deferral-in-words"),
    ],
)
def test_a_deferral_is_refused_wherever_it_is_written(tmp_path, docstring, named):
    # ⛔ R11 admits a design claim only. A promise of later work reads to a
    # stranger as permanent, so the floor refuses it, however it is spelled.
    findings = oversized(tmp_path, "deferred", docstring)
    assert [finding.rule for finding in findings] == ["size-deferral"]
    assert named in findings[0].message
    assert DESIGN_FORM in findings[0].message


def test_a_design_claim_passes(tmp_path):
    # ⭐ The negative control for the refusals above: the same ceiling, the same
    # length, and a reason that says why splitting would be worse.
    assert promises(size_exception(DESIGN_CLAIM)) == []
    assert oversized(tmp_path, "claimed", DESIGN_CLAIM) == []


def test_a_long_justification_with_a_short_first_line_is_not_refused_for_length(tmp_path):
    # ⛔ `MIN_JUSTIFICATION_CHARS` is measured against the whole paragraph, so
    # a correct multi-line reason whose first line is short is not refused for
    # being short.
    docstring = (
        "Thing.\n\nSize exception: one table.\n"
        "Splitting it across modules would hide half the placeholders from\n"
        "the reader of the other half, and every one of them is read together."
    )
    assert len("one table.") < config.MIN_JUSTIFICATION_CHARS
    assert oversized(tmp_path, "short_first_line", docstring) == []


# --- the remedy names the one form ------------------------------------------


def test_the_remedy_names_the_design_claim_and_refuses_a_promise():
    assert "<why splitting would be worse>" in DESIGN_FORM
    assert "never a promise of later work" in DESIGN_FORM
    assert "<TASK-ID>" not in DESIGN_FORM


def test_every_size_remedy_offers_the_design_claim(tmp_path):
    # ⛔ Each of the three refusals says what the one admissible form is.
    write_module(tmp_path, "src/studyforge/none.py", module_of(config.SOURCE_LINE_CEILING + 1))
    write_module(
        tmp_path,
        "src/studyforge/hollow.py",
        module_of(config.SOURCE_LINE_CEILING + 1, "Thing.\n\nSize exception: yes"),
    )
    findings = oversized(tmp_path, "deferred", DEFERRAL_BY_ID)
    assert sorted(finding.rule for finding in findings) == [
        "size",
        "size-deferral",
        "size-justification",
    ]
    for finding in findings:
        assert DESIGN_FORM in finding.message


# --- authored stylesheets, scripts and templates ----------------------------


def lines_of(count: int) -> str:
    """A text of exactly `count` physical lines, in no particular language."""
    return "".join(f"/* {number} */\n" for number in range(count))


def test_an_authored_file_over_the_ceiling_fails_in_every_authored_language(tmp_path):
    for suffix in AUTHORED_SUFFIXES:
        write_module(
            tmp_path, f"src/studyforge/assets/big{suffix}", lines_of(config.SOURCE_LINE_CEILING + 1)
        )
    findings = check_sizes(tmp_path)
    assert sorted(finding.path for finding in findings) == sorted(
        f"src/studyforge/assets/big{suffix}" for suffix in AUTHORED_SUFFIXES
    )
    for finding in findings:
        assert finding.rule == "size"
        assert SPLIT_ONLY in finding.message


def test_an_authored_file_at_the_ceiling_passes(tmp_path):
    for suffix in AUTHORED_SUFFIXES:
        write_module(
            tmp_path, f"src/studyforge/assets/full{suffix}", lines_of(config.SOURCE_LINE_CEILING)
        )
    assert check_sizes(tmp_path) == []


def test_a_vendored_file_is_excluded_by_its_path_and_only_by_its_path(tmp_path):
    oversized = lines_of(config.SOURCE_LINE_CEILING + 50)
    for vendored in VENDORED:
        write_module(tmp_path, vendored, oversized)
    assert check_sizes(tmp_path) == []
    # ⛔ The same basename anywhere else is authored, and is read.
    elsewhere = [f"src/studyforge/other/{Path(vendored).name}" for vendored in VENDORED]
    for path in elsewhere:
        write_module(tmp_path, path, oversized)
    assert sorted(finding.path for finding in check_sizes(tmp_path)) == sorted(elsewhere)


def test_the_authored_walk_reads_src_only_and_not_documents(tmp_path):
    oversized = lines_of(config.SOURCE_LINE_CEILING + 1)
    write_module(tmp_path, "src/studyforge/skills/big/SKILL.md", oversized)
    write_module(tmp_path, "tools/big.css", oversized)
    write_module(tmp_path, "src/studyforge/assets/big.css", oversized)
    assert [finding.path for finding in check_sizes(tmp_path)] == ["src/studyforge/assets/big.css"]


def test_a_size_exception_comment_does_not_open_the_gate_for_a_stylesheet(tmp_path):
    text = f"/* {config.SIZE_EXCEPTION_MARKER} a long and entirely sincere reason */\n"
    write_module(
        tmp_path,
        "src/studyforge/assets/claimed.css",
        text + lines_of(config.SOURCE_LINE_CEILING),
    )
    assert [finding.path for finding in check_sizes(tmp_path)] == [
        "src/studyforge/assets/claimed.css"
    ]


def test_every_vendored_exclusion_names_a_file_the_tree_holds_and_its_licence():
    root = Path(__file__).resolve().parents[2]
    for vendored, reason in VENDORED.items():
        assert (root / vendored).is_file(), f"{vendored} is excluded but does not exist"
        licence = next(word for word in reason.split() if word.endswith(".LICENSE"))
        assert (root / vendored).with_name(licence).is_file(), f"{vendored}: no {licence}"


def test_the_authored_walk_reads_every_shipped_non_vendored_file():
    root = Path(__file__).resolve().parents[2]
    shipped = {
        config.relative(path, root)
        for path in (root / "src").rglob("*")
        if path.is_file() and path.suffix in AUTHORED_SUFFIXES
    }
    read = {config.relative(path, root) for path in authored_files(root)}
    assert read == shipped - set(VENDORED)
    assert read, "the walk read nothing, so every assertion above is vacuous"


# --- the tree itself --------------------------------------------------------


def test_no_size_exception_in_this_repository_promises_later_work():
    # ⭐ The in-the-wild check, asserted over whatever exceptions the tree holds,
    # so it stays true (vacuously) while there is none.
    root = Path(__file__).resolve().parents[2]
    for path in config.python_files(root):
        text = path.read_text(encoding="utf-8")
        if count_lines(text) <= config.ceiling_for(config.relative(path, root)):
            continue
        reason = size_exception(module_docstring(text, path))
        assert not promises(reason), (
            f"{config.relative(path, root)} justifies its size with a promise of later work"
        )
