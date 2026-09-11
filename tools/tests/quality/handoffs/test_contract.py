"""Mirror of `tools/quality/handoffs/contract.py` (R12).

⛔ **Every condition here is asserted in both directions**, and each negative is
the same template one line different from the positive — a check that reports
`clean` and a check that never ran are indistinguishable from their output.
"""

from __future__ import annotations

import re

import pytest

from tests.support import repository_root
from tools.quality.handoffs import (
    FINDING_MARKERS,
    HANDOFF_DIR,
    LEGACY_GLOBAL_MAX,
    MARKER_NONE,
    SECTIONS,
    check_handoffs,
    marker_lines,
)
from tools.quality.handoffs.contract import (
    _FINDING_NUMBER,
    _MARKERS_ON_LINE,
    LEAD_TOKENS,
)
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


# --- W63: the vocabulary is spelled once, and the lead is a closed set ------


def test_the_marker_pattern_is_derived_from_the_constant_and_not_typed_twice():
    # ⛔ Ruling 193: the shipped constant is the authority and a second reader
    # with a second spelling is the same defect at a different site. ⚠️ This
    # module held both — the three constants and a hand-typed alternation — so
    # this is Ruling 103's printed agreement, as a test rather than a sweep.
    derived = "|".join(re.escape(marker) for marker in sorted(FINDING_MARKERS))
    assert _MARKERS_ON_LINE.pattern == derived


@pytest.mark.parametrize("marker", FINDING_MARKERS)
def test_every_member_of_the_vocabulary_is_read_by_the_reader(marker):
    # ⭐ The inhabitation half (Ruling 48): a derivation that read none of its
    # own members would agree with the constant and assert nothing.
    assert _MARKERS_ON_LINE.findall(f"- {marker} a thing") == [marker]


def test_and_a_marker_shaped_token_outside_the_vocabulary_is_not_read():
    # ⛔ The closed half. A fourth marker is readable the moment it is NAMED in
    # `FINDING_MARKERS` and not before, which is the property that was missing:
    # the old hand-typed alternation would have left it invisible either way.
    outside = "`[zzqx]`"
    assert outside not in FINDING_MARKERS
    assert _MARKERS_ON_LINE.findall(f"- {outside} a thing") == []
    assert marker_lines(f"- {outside} a thing\n") == []


def test_the_lead_tokens_are_pairwise_disjoint_in_what_they_can_start():
    # ⚠️ This is what makes the order of `LEAD_TOKENS` immaterial, and therefore
    # the reader reproducible (R10). ⛔ Asserted rather than trusted: two tokens
    # that could both start at one character would make the loop's answer
    # depend on the order they happen to be written in.
    probe = "".join(chr(code) for code in range(0x20, 0x7F)) + "—–⛔⭐⚠✅️\t"
    starts: dict[str, set[str]] = {}
    for name, pattern in LEAD_TOKENS:
        token = re.compile(pattern)
        starts[name] = {char for char in probe if token.match(char) or token.match(char + "1`")}
    names = [name for name, _pattern in LEAD_TOKENS]
    assert all(starts[name] for name in names), (
        "Ruling 48: a token matching nothing asserts nothing"
    )
    for first in range(len(names)):
        for second in range(first + 1, len(names)):
            overlap = starts[names[first]] & starts[names[second]]
            assert not overlap, f"{names[first]} and {names[second]} both start at {overlap}"


@pytest.mark.parametrize(
    "line",
    [
        # ⭐ Quoted from `docs/tasks/handoffs/` at 2d0cfe7, not invented: the
        # three forms both offices have actually written for thirty rounds.
        "- **`PO-31/1`** `[structural]` — the rubric has no clause",
        "- **`CTO-27/1`** — ⛔ **`[local]` The base I was handed is pinned wrong",
        "- ⛔ **`CTO-26/1`** `[structural]` — **the rubric has no clause**",
        "### ⛔ 21 `[structural]` — `corpus.json` is not gated",
        "### ⭐ 4 `[local]` — R14 and R18 are cited by no code",
    ],
)
def test_the_form_both_offices_write_is_now_a_finding_line(line):
    # ⛔ Ruling 148's subject, measured: 163 lines in 24 documents wrote a
    # backticked finding ID and NONE of them read as a finding line, so every
    # rule downstream of the reader was vacuous on them.
    assert marker_lines(line + "\n")[0][2] is True


@pytest.mark.parametrize(
    "line",
    [
        # ⛔ The negative controls `W63` owes, and they are the whole point of
        # the closed set: a word, a `|` and a `>` are in no token.
        "`SF-04/1` and `SF-04/3` are `[local]` and need no routing",
        "| **47** | ⛔ `[structural]` | **ruled below** |",
        "> the review marked it `[structural]` and moved on",
        "**`SF-12-survey/1`** — **the R13 debt is one file.** `[structural]`",
        "Filed: 3. Marked in the branch: 5 (2 `[local]`, 3 `[structural]`).",
    ],
)
def test_and_the_shapes_that_must_stay_refused_are_still_refused(line):
    assert marker_lines(line + "\n")[0][2] is False


def test_a_backticked_scoped_id_is_read_as_the_number_it_claims(tmp_path):
    # ⚠️ The module's own docstring warns that a vocabulary is read in two
    # places or in neither: admitting this lead without teaching
    # `_FINDING_NUMBER` the same form would have made the ID rule VACUOUS on
    # every line the lead newly admits.
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]`", "- **`W99/1`** — `[local]`"))
    assert check_handoffs(tmp_path) == []


def test_and_a_backticked_id_scoped_elsewhere_is_still_a_finding(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]`", "- **`W98/1`** — `[local]`"))
    assert rules(tmp_path) == ["handoff-finding-id"]


def test_an_unclosed_backtick_is_not_a_number_and_not_a_finding_line(tmp_path):
    # ⛔ The ticks are a PAIR, and an unclosed one is in NO token — so the lead
    # stops at it and the line is refused outright.
    #
    # ⚠️ **My written prediction for this control was `[]`** — that the line
    # would pass as an unnumbered finding. ⭐ It is refused instead, and the
    # refusal is the better answer: `` `63 `` is markup nobody finished, the
    # reader says so out loud, and the one thing it must not do is read `63` as
    # a bare number above the closed legacy ceiling. That is what is asserted.
    above = LEGACY_GLOBAL_MAX + 1
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]`", f"### `{above} `[local]`"))
    assert rules(tmp_path) == ["handoff-findings", "handoff-marker"]
