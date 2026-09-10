"""Mirror of `tools/quality/handoffs/contract.py` (R12).

⛔ **Every condition here is asserted in both directions**, and each negative is
the same template one line different from the positive — a check that reports
`clean` and a check that never ran are indistinguishable from their output.
"""

from __future__ import annotations

import pytest

from tests.support import repository_root
from tools.quality.handoffs import (
    HANDOFF_DIR,
    LEGACY_GLOBAL_MAX,
    MARKER_NONE,
    SECTIONS,
    check_handoffs,
    marker_lines,
)
from tools.quality.handoffs.contract import _FINDING_NUMBER
from tools.tests.quality.handoffs.support import GOOD, rules, write

# --- the six sections ------------------------------------------------------


@pytest.mark.parametrize("section", SECTIONS)
def test_a_handoff_missing_any_section_is_a_finding(tmp_path, section):
    write(tmp_path, "W99.md", GOOD.replace(f"**{section}:**", f"**Not{section}:**"))
    assert "handoff-section" in rules(tmp_path)


@pytest.mark.parametrize("section", SECTIONS)
def test_and_the_heading_spelling_rubric_8_also_accepts_passes(tmp_path, section):
    # ⭐ Both spellings, by ruling: the sections are the contract and the
    # emphasis markers are not. ⚠️ A check taking only one of them would have
    # red-lined the long handoffs, which is how a check gets switched off.
    write(tmp_path, "W99.md", GOOD.replace(f"**{section}:**", f"## {section}\n"))
    assert check_handoffs(tmp_path) == []


def test_a_section_name_that_merely_starts_the_right_way_is_not_the_section(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace("**Status:**", "## Statuses"))
    assert "handoff-section" in rules(tmp_path)


# --- rubric §8a: a finding is a marked item --------------------------------


def test_a_marker_in_prose_is_a_finding(tmp_path):
    write(
        tmp_path,
        "W99.md",
        GOOD.replace("**Findings:**", "**Findings:** each one carries `[local]` or `[structural]`"),
    )
    assert "handoff-marker" in rules(tmp_path)


def test_two_markers_on_one_line_is_a_finding(tmp_path):
    doubled = GOOD.replace("`[local]` a defect", "`[local]` `[structural]` a defect")
    write(tmp_path, "W99.md", doubled)
    assert "handoff-marker" in rules(tmp_path)


@pytest.mark.parametrize(
    "line",
    [
        "### 1. `[local]` a defect",
        "### `[structural]` a defect",
        "1. `[local]` a defect",
        "**1. `[local]` — a defect",
        "### 13 `[structural]` — a defect",
        "- **`[local]`** a defect",
    ],
)
def test_every_finding_line_shape_on_the_tip_still_reads_as_one(line):
    # ⭐ Derived by reading all 199 marker lines in `docs/tasks/handoffs/`
    # rather than guessed. A rule that rejected any of these would have made
    # the migration a rewrite of every handoff.
    assert marker_lines(line + "\n")[0][2] is True


@pytest.mark.parametrize(
    "line",
    [
        "each one carries `[local]` or `[structural]`",
        "every `[structural]` one is ruled, scheduled, or open",
        "⭐ **Triaged** — each carries `[local]`, and",
    ],
)
def test_and_a_marker_with_a_word_in_front_of_it_does_not(line):
    assert marker_lines(line + "\n")[0][2] is False


def test_a_marker_inside_a_fenced_block_is_quoted_material(tmp_path):
    # ⭐ Found by this rule going red on its own handoff: a handoff that
    # documents the vocabulary — a transcript of the check firing, a migration
    # table — necessarily contains the literal markers, and every one of them
    # is evidence rather than a claim.
    transcript = "```text\nW20.md:198 [handoff-marker] `[local]` `[structural]` in prose\n```\n"
    write(
        tmp_path,
        "W99.md",
        GOOD.replace("**For dependents:**", transcript + "\n**For dependents:**"),
    )
    assert check_handoffs(tmp_path) == []


def test_and_the_fence_closes_so_prose_after_it_is_still_read(tmp_path):
    # ⛔ The inhabitation half: a skip that never turned back on would make
    # every marker after the first fence invisible, which is the silent
    # direction and the one that has to be asserted.
    block = "```text\nquoted\n```\n\neach one carries `[local]` or `[structural]`\n"
    write(tmp_path, "W99.md", GOOD.replace("**For dependents:**", block + "\n**For dependents:**"))
    assert "handoff-marker" in rules(tmp_path)


def test_zero_markers_is_a_failure_and_not_a_pass(tmp_path):
    # ⛔ Ruling 29's half that catches the class. ⚠️ Measured: `SK-01` carried
    # six findings and zero markers and was APPROVEd twice. The old counter
    # returned `0 = 0` and passed; this returns a finding.
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]` a defect somewhere else", "None."))
    assert rules(tmp_path) == ["handoff-findings"]


def test_a_none_marker_with_a_sentence_is_how_zero_is_written(tmp_path):
    write(
        tmp_path,
        "W99.md",
        GOOD.replace(
            "### 1. `[local]` a defect somewhere else",
            "- `[none]` nothing outside this task's scope; the two neighbouring "
            "modules were read and are clean.",
        ),
    )
    assert check_handoffs(tmp_path) == []


def test_a_bare_none_marker_is_a_quieter_way_of_writing_zero(tmp_path):
    bare = GOOD.replace("### 1. `[local]` a defect somewhere else", "- `[none]`")
    write(tmp_path, "W99.md", bare)
    assert rules(tmp_path) == ["handoff-findings"]


def test_none_may_not_stand_beside_a_real_finding(tmp_path):
    write(
        tmp_path,
        "W99.md",
        GOOD.replace(
            "**For dependents:**",
            "- `[none]` nothing outside this task's scope, nothing at all.\n\n**For dependents:**",
        ),
    )
    findings = check_handoffs(tmp_path)
    assert [finding.rule for finding in findings] == ["handoff-findings"]
    assert MARKER_NONE in findings[0].message


def test_a_tree_with_no_handoff_directory_is_not_an_error(tmp_path):
    assert check_handoffs(tmp_path) == []


# --- a finding is numbered inside its own document -------------------------


def test_the_new_form_scoped_to_this_document_passes(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]`", "### W99/1 `[local]`"))
    assert check_handoffs(tmp_path) == []


def test_a_number_scoped_to_another_document_is_a_finding(tmp_path):
    # ⛔ The half a shape check can actually assert: the `<TASK-ID>` must be one
    # this document declared. A number scoped elsewhere is a citation, and a
    # citation is not a heading.
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]`", "### W98/1 `[local]`"))
    assert rules(tmp_path) == ["handoff-finding-id"]


def test_a_bare_number_continuing_the_global_sequence_is_refused(tmp_path):
    above = LEGACY_GLOBAL_MAX + 1
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]`", f"### {above} `[local]`"))
    findings = check_handoffs(tmp_path)
    assert [finding.rule for finding in findings] == ["handoff-finding-id"]
    assert "W99/<n>" in findings[0].message


@pytest.mark.parametrize("legacy", [1, 20, 47, LEGACY_GLOBAL_MAX])
def test_and_the_closed_legacy_range_is_never_red(tmp_path, legacy):
    # ⛔ A handoff is a record and is never rewritten, so a check that demanded
    # the record be renumbered is a check this project forbids. The ceiling is
    # what makes "grandfathered" representable without a snapshot list.
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]`", f"### {legacy} `[local]`"))
    assert check_handoffs(tmp_path) == []


def test_the_pinned_ceiling_still_matches_the_tree():
    # ⚠️ Ruling 55, as a test rather than a comment: `BOARD.md` says the legacy
    # range ends at 58 and the merged tree runs to 62, because `SF-10` minted
    # four more on a branch before the ruling landed. ⛔ If this goes red, the
    # constant has stopped being a measurement — re-measure, do not raise it to
    # fit, because raising it grandfathers whatever just landed.
    numbers = []
    for path in (repository_root() / HANDOFF_DIR).glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for _number, line, own_line in marker_lines(text):
            if not own_line:
                continue
            claim = _FINDING_NUMBER.match(line.lstrip("#*-").lstrip())
            if claim and claim.group("scope") is None:
                numbers.append(int(claim.group("number")))
    assert numbers, "Ruling 48: no numbers read means this asserts nothing"
    assert max(numbers) == LEGACY_GLOBAL_MAX, f"the tree's highest bare number is {max(numbers)}"


def test_an_unnumbered_finding_claims_no_name_and_is_left_alone(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]`", "### `[local]`"))
    assert check_handoffs(tmp_path) == []
