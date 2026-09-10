"""Mirror of `tools/quality/handoffs.py` (R12).

⛔ **Every condition here is asserted in both directions.** A check that
reports `clean` and a check that never ran are indistinguishable from their
output, and six instances last session were a probe that could not fail
reporting success — so each rule gets a document that violates it and a
document that does not, built from the same template one line apart.

⭐ **The template below is `agent-protocol.md`'s, minimally inhabited.** Every
negative is that template with one thing removed or moved, which is what makes
the negative control legible rather than a different document that happens to
fail.
"""

from __future__ import annotations

import pytest

from tests.support import repository_root
from tools.quality.handoffs import (
    DOCUMENT_KINDS,
    HANDOFF_DIR,
    KIND_MARKER,
    MARKER_NONE,
    SECTIONS,
    TASK_HANDOFF,
    check_handoffs,
    declared_kind,
    marker_lines,
)

GOOD = """# W99 — handoff

**Kind:** task handoff — W99

**Status:** done

**What landed:** a thing.

**Decisions:** one.

**Surprises:** none worth the word.

**Findings:**

### 1. `[local]` a defect somewhere else

**For dependents:** nothing.
"""


def write(tmp_path, name, text):
    """Put `text` at `HANDOFF_DIR/name` under a temporary repository root."""
    path = tmp_path / HANDOFF_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def rules(tmp_path):
    """The rule names `check_handoffs` reports for the tree, sorted."""
    return sorted(finding.rule for finding in check_handoffs(tmp_path))


# --- the shipped tree ------------------------------------------------------


def test_every_document_in_this_repository_passes():
    root = repository_root()
    findings = check_handoffs(root)
    assert findings == [], "\n".join(str(finding) for finding in findings)


def test_and_the_check_that_says_so_can_actually_fire(tmp_path):
    # ⛔ Ruling 48: the test above asserts an empty list, and an empty list is
    # also what a check reading nothing returns.
    write(tmp_path, "W99.md", GOOD.replace("**Surprises:** none worth the word.\n\n", ""))
    assert rules(tmp_path) == ["handoff-section"]


def test_the_real_directory_is_the_one_being_read():
    # ⚠️ The check is scoped to one path. If that path were wrong, every
    # assertion above would pass on an empty file list.
    assert (repository_root() / HANDOFF_DIR).is_dir()
    assert len(list((repository_root() / HANDOFF_DIR).glob("*.md"))) > 20


# --- the binding is a declaration, never the filename ----------------------


def test_a_document_with_no_declaration_is_refused(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace("**Kind:** task handoff — W99\n\n", ""))
    assert rules(tmp_path) == ["handoff-kind"]


def test_an_unknown_kind_is_refused_and_the_message_names_the_closed_set(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace(TASK_HANDOFF, "memo"))
    findings = check_handoffs(tmp_path)
    assert [finding.rule for finding in findings] == ["handoff-kind"]
    for kind in DOCUMENT_KINDS:
        assert kind in findings[0].message


def test_a_declaration_below_the_window_is_not_a_declaration(tmp_path):
    # ⭐ A declaration a reader has to scroll for is not one they will trust.
    body = GOOD.replace("**Kind:** task handoff — W99\n\n", "")
    write(tmp_path, "W99.md", body.replace("**Status:** done", "**Status:** done\n" * 12, 1))
    assert "handoff-kind" in rules(tmp_path)


@pytest.mark.parametrize("kind", [k for k in DOCUMENT_KINDS if k != TASK_HANDOFF])
def test_a_document_that_is_not_a_task_handoff_owes_only_its_declaration(tmp_path, kind):
    # ⛔ The trap this check was written to avoid: `docs/tasks/handoffs/` holds
    # surveys, ruling records and session logs, and a naive migration would
    # demand six sections of a document that owes none. ⭐ A survey is not
    # excused by an exclusion list — it says what it is.
    write(tmp_path, "anything.md", f"# Some title\n\n{KIND_MARKER} {kind}\n\nProse.\n")
    assert check_handoffs(tmp_path) == []


def test_the_next_survey_is_refused_until_it_declares_rather_than_passing_quietly(tmp_path):
    # ⚠️ A survey lands next wave. ⛔ The closed set fails toward *refusal* —
    # loudly, naming what it did not expect — where an exclusion list would
    # have admitted it silently and then been one entry short.
    write(tmp_path, "SF-12-survey.md", "# SF-12 survey — porting a thing\n\nProse.\n")
    assert rules(tmp_path) == ["handoff-kind"]
    write(tmp_path, "SF-12-survey.md", f"# SF-12 survey\n\n{KIND_MARKER} survey\n\nProse.\n")
    assert check_handoffs(tmp_path) == []


def test_a_filename_that_looks_like_a_handoff_is_not_read_as_one(tmp_path):
    # ⛔ The `<TASK-ID>.md` binding was already false on the tip: eight of the
    # ten non-handoffs in that directory carried `— handoff` in their titles.
    # Neither name nor title is consulted for the kind.
    write(tmp_path, "SF-10.md", f"# SF-10 — handoff\n\n{KIND_MARKER} survey\n\nProse.\n")
    assert check_handoffs(tmp_path) == []


def test_the_kind_registry_is_inhabited_and_every_entry_says_what_it_owes():
    assert TASK_HANDOFF in DOCUMENT_KINDS
    assert len(DOCUMENT_KINDS) >= 4
    for kind, owed in DOCUMENT_KINDS.items():
        assert kind.islower() and len(owed) > 30, kind


# --- identity: the IDs, the filename that follows them, the title ----------


def test_a_task_handoff_that_names_no_task_is_refused(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace(" — W99", ""))
    assert rules(tmp_path) == ["handoff-kind"]


def test_a_declared_id_that_is_not_a_task_id_is_refused(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace(" — W99", " — the wave"))
    assert "handoff-kind" in rules(tmp_path)


def test_a_title_that_does_not_match_is_a_finding(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace("# W99 — handoff", "# W99 — notes"))
    assert rules(tmp_path) == ["handoff-title"]


def test_a_title_naming_the_wrong_task_is_a_finding(tmp_path):
    write(tmp_path, "W99.md", GOOD.replace("# W99 — handoff", "# W98 — handoff"))
    assert rules(tmp_path) == ["handoff-title"]


def test_a_handoff_for_two_tasks_is_representable(tmp_path):
    # ⚠️ Four of the tip's handoffs cover two wave items each, and a check
    # keyed on the filename would have had to exempt every one of them.
    text = GOOD.replace("**Kind:** task handoff — W99", "**Kind:** task handoff — W98, W99")
    write(tmp_path, "W98-W99.md", text.replace("# W99 — handoff", "# W98 + W99 — handoff"))
    assert check_handoffs(tmp_path) == []


def test_and_a_two_task_title_must_still_name_both(tmp_path):
    text = GOOD.replace("**Kind:** task handoff — W99", "**Kind:** task handoff — W98, W99")
    write(tmp_path, "W98-W99.md", text.replace("# W99 — handoff", "# W98 — handoff"))
    assert rules(tmp_path) == ["handoff-title"]


def test_the_filename_follows_the_declaration_and_not_the_other_way(tmp_path):
    write(tmp_path, "notes.md", GOOD)
    assert rules(tmp_path) == ["handoff-filename"]


def test_the_declaration_reader_returns_the_kind_and_the_ids():
    assert declared_kind(GOOD) == (TASK_HANDOFF, ["W99"], 3)
    assert declared_kind("# T\n\nno declaration\n") == (None, [], 0)


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
