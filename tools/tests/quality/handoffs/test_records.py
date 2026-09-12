"""Mirror of `tools/quality/handoffs/records.py` (R12) — gates two and three.

⛔ **Every test here that goes GREEN would also have gone green before `W64`**,
because before it `check_handoffs` returned at the kind test and a record was
read by no rule at all. ⭐ **So the tests that matter are the ones that FIRE**
— and each is paired with the same document under a kind that was already
admitted, so the two readers cannot drift apart (`W121`'s discipline).

⭐ **`W172` adds gate three below, and its three REFUSED arms are asserted as
refusals rather than left silent** (the row's clause 2): each has a test that
goes green on a document a task handoff would be refused for, paired with the
handoff that IS refused for it.
"""

from __future__ import annotations

from tools.quality.handoffs import KIND_MARKER, check_handoffs, record_scopes
from tools.quality.handoffs.records import derived_scope, record_finding_lines
from tools.tests.quality.handoffs.support import GOOD, rules, write

#: ⭐ The minimally-inhabited RECORD, in the shape both offices actually write:
#: a round filename, the office spelling on the declaration, and one finding
#: numbered inside the scope the filename derives.
RECORD_NAME = "CTO-2026-09-12-round99.md"
RECORD = f"""# CTO round 99 — closing

{KIND_MARKER} ruling record — CTO round 99

## Findings

| id | marker | finding |
|---|---|---|
| `CTO-99/1` | `[local]` | ⭐ Something that was measured and is now recorded. |
"""


def record(text=RECORD, name=RECORD_NAME):
    """`(name, text)` for `write`, so a variant reads as one edit."""
    return (name, text)


# --- the derivation itself, shipped rather than described (`W121/2`) --------


def test_the_scope_is_derived_from_the_filename_at_zero_record_edits():
    # ⭐ Ruling 219: a record's scope is already on its face, in its filename.
    assert derived_scope("CTO-2026-09-12-round69") == "CTO-69"
    assert derived_scope("PO-2026-09-12-round54") == "PO-54"


def test_a_filename_that_is_not_a_round_derives_nothing():
    # ⚠️ Eight records in the tree predate the settled filename. They are held
    # to the legacy ceiling and nothing else — see `records.py`'s docstring.
    assert derived_scope("ruling-46") is None
    assert derived_scope("CTO-2026-09-09-m0-readiness") is None
    assert derived_scope("W19-provenance-pin") is None


def test_the_office_spelling_of_a_declaration_is_read_rather_than_corrected():
    # ⛔ 37 records write `CTO round 44`. Demanding this module's punctuation
    # would be 37 record edits for no reading gained (Ruling 106).
    assert record_scopes("CTO-2026-09-12-round99", ["CTO round 99"]) == ["CTO-99"]
    assert record_scopes("CTO-2026-09-12-round99", ["CTO-99"]) == ["CTO-99"]


def test_a_declaration_that_agrees_with_the_filename_is_not_counted_twice():
    assert len(record_scopes("PO-2026-09-12-round54", ["PO round 54"])) == 1


def test_an_unparseable_declaration_contributes_no_scope():
    # ⭐ A typo may not quietly WIDEN what a record owns; it is reported.
    assert record_scopes("CTO-2026-09-12-round99", ["the ninety-ninth"]) == ["CTO-99"]


# --- the declaration rules -------------------------------------------------


def test_the_shape_both_offices_write_today_is_clean(tmp_path):
    write(tmp_path, *record())
    assert check_handoffs(tmp_path) == []


def test_a_declared_scope_that_disagrees_with_the_filename_is_refused(tmp_path):
    write(tmp_path, *record(RECORD.replace("— CTO round 99", "— CTO round 98")))
    assert rules(tmp_path) == ["handoff-record-scope"]


def test_a_declared_scope_that_is_not_a_scope_is_refused(tmp_path):
    write(tmp_path, *record(RECORD.replace("— CTO round 99", "— the ninety-ninth round")))
    assert rules(tmp_path) == ["handoff-record-scope"]


def test_a_record_files_its_findings_inside_ONE_scope(tmp_path):
    # ⛔ The others are citations, and a citation is written on the finding
    # line, never on the declaration.
    # ⚠️ TWO findings, and the second is not noise: any second scope also
    # disagrees with the filename, and saying so names both defects rather
    # than making the author re-run to discover the one it swallowed.
    write(tmp_path, *record(RECORD.replace("— CTO round 99", "— CTO round 99, PO round 54")))
    findings = check_handoffs(tmp_path)
    assert [finding.rule for finding in findings] == ["handoff-record-scope"] * 2
    assert "declares 2 scopes" in findings[0].message
    assert "derives CTO-99" in findings[1].message


def test_a_record_that_declares_nothing_keeps_the_derived_scope(tmp_path):
    write(tmp_path, *record(RECORD.replace(" — CTO round 99", "")))
    assert check_handoffs(tmp_path) == []


def test_a_record_whose_filename_derives_nothing_is_not_refused(tmp_path):
    # ⚠️ Refusing would demand a rename or a declaration inside a record
    # Ruling 106 protects. It is held to the legacy ceiling and nothing else.
    body = RECORD.replace(" — CTO round 99", "").replace("`CTO-99/1`", "`3`")
    write(tmp_path, *record(body, "ruling-46.md"))
    assert check_handoffs(tmp_path) == []


# --- the finding-ID rule, which now reaches a record -----------------------


def test_a_record_continuing_the_closed_global_sequence_is_now_SEEN(tmp_path):
    # ⛔ THE test of this row. Before it, this document was read by no rule but
    # *say what you are*, and `63` above a ceiling closed at 62 was invisible.
    write(tmp_path, *record(RECORD.replace("`CTO-99/1`", "`63`")))
    assert rules(tmp_path) == ["handoff-finding-id"]


def test_and_the_legacy_range_is_still_grandfathered_inside_a_record(tmp_path):
    write(tmp_path, *record(RECORD.replace("`CTO-99/1`", "`47`")))
    assert check_handoffs(tmp_path) == []


def test_the_message_names_a_shape_when_the_record_owns_no_scope(tmp_path):
    # ⛔ A record with neither a derived nor a declared scope has nothing to
    # suggest; the reader must still print advice rather than crash.
    body = RECORD.replace(" — CTO round 99", "").replace("`CTO-99/1`", "`63`")
    write(tmp_path, *record(body, "ruling-46.md"))
    findings = check_handoffs(tmp_path)
    assert [finding.rule for finding in findings] == ["handoff-finding-id"]
    assert "`<SCOPE>/<n>`" in findings[0].message


def test_a_record_CITES_another_scope_and_a_handoff_TAKES_it(tmp_path):
    # ⚠️ The one rule that INVERTS between the two kinds, asserted as a PAIR so
    # the halves cannot drift apart. ⭐ A review record's disposition table
    # rules on findings numbered inside the row it reviewed; a task handoff
    # numbering a finding inside another task's name has taken that name.
    write(tmp_path, *record(RECORD.replace("`CTO-99/1`", "`W140/3`")))
    assert check_handoffs(tmp_path) == []

    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]`", "### `W140/3` `[local]`"))
    assert rules(tmp_path) == ["handoff-finding-id"]


# --- gate three: the PREDICATE, which is what tells a finding from prose ---


def test_a_marker_OUTSIDE_the_findings_section_is_prose_and_is_not_read(tmp_path):
    # ⛔ THE test of gate three. A record's prose names markers constantly and
    # legitimately; measured at `bec9d5c`, 724 of a record's marker-bearing
    # lines sit outside any Findings section. ⚠️ This one claims a scope AND
    # buries its marker, so only the region keeps it quiet.
    body = RECORD.replace(
        "## Findings",
        "## Decisions\n\n`CTO-99/4` was ruled `[structural]` and not `[local]`.\n\n## Findings",
    )
    write(tmp_path, *record(body))
    assert check_handoffs(tmp_path) == []
    assert [number for number, _line in record_finding_lines(body)] == [13]

    # ⭐ The pair, one edit away: the SAME line inside the section IS read.
    moved = RECORD.replace(
        "|---|---|---|",
        "|---|---|---|\n\n`CTO-99/4` was ruled `[structural]` and not `[local]`.\n",
    )
    write(tmp_path, *record(moved))
    assert rules(tmp_path) == ["handoff-marker"]


def test_inside_the_section_a_line_claiming_NO_scope_is_still_prose(tmp_path):
    # ⭐ Gate two's own ruling read forward: a record's finding is numbered
    # inside a SCOPE, so a marker on a line claiming none is a sentence about
    # markers. Measured: 80 such lines in the corpus, every one of them prose.
    body = RECORD.replace(
        "|---|---|---|",
        "|---|---|---|\n\nAll 5 were `[structural]`, and 2 of them `[local]` as well.\n",
    )
    write(tmp_path, *record(body))
    assert check_handoffs(tmp_path) == []


def test_the_marker_may_sit_in_ANY_cell_of_a_numbered_row(tmp_path):
    # ⛔ Ruling 189(b): *the marker may sit in the first cell or the fifth*.
    # ⚠️ The offices write `| # | Finding | Marker |`, so the marker sits
    # BEHIND a cell of prose and `marker_lines`'s own_line refuses it.
    behind = RECORD.replace(
        "| `CTO-99/1` | `[local]` | ⭐ Something that was measured and is now recorded. |",
        "| `CTO-99/1` | ⭐ Something that was measured and is now recorded. | `[local]` |",
    )
    write(tmp_path, *record(behind))
    assert check_handoffs(tmp_path) == []

    # ⭐ The other direction: no cell of the row starts with a marker at all.
    buried = RECORD.replace(
        "| `CTO-99/1` | `[local]` | ⭐ Something that was measured and is now recorded. |",
        "| `CTO-99/1` | ⭐ Something measured, filed `[local]`, and now recorded. |",
    )
    write(tmp_path, *record(buried))
    findings = check_handoffs(tmp_path)
    assert [finding.rule for finding in findings] == ["handoff-marker"]
    assert "buries its marker" in findings[0].message


def test_a_marker_QUOTED_in_a_findings_prose_does_not_make_it_two_findings(tmp_path):
    # ⚠️ A disposition quotes the marker it is arguing about. That is one
    # finding, not two — the count arm survives only for markers where no
    # claim precedes them.
    quoted = RECORD.replace(
        "⭐ Something that was measured and is now recorded.",
        "⭐ Recorded, and `[local]` was the right marker for it after all.",
    )
    write(tmp_path, *record(quoted))
    assert check_handoffs(tmp_path) == []

    # ⭐ The pair: two markers where NO claim precedes either is still one
    # finding claiming to be two.
    twice = RECORD.replace("| `[local]` |", "| `[local]` | `[structural]` |")
    write(tmp_path, *record(twice))
    findings = check_handoffs(tmp_path)
    assert [finding.rule for finding in findings] == ["handoff-marker"]
    assert "marks it 2 times" in findings[0].message


def test_a_records_none_marker_still_owes_its_sentence(tmp_path):
    # ⛔ The one `[none]` arm a record DOES owe: `0` is never self-certifying,
    # and that argument does not turn on the kind of document.
    bare = RECORD.replace(
        "| `[local]` | ⭐ Something that was measured and is now recorded. |",
        "| `[none]` | ⭐ nothing |",
    )
    write(tmp_path, *record(bare))
    assert rules(tmp_path) == ["handoff-findings"]

    said = RECORD.replace("| `[local]` |", "| `[none]` |")
    write(tmp_path, *record(said))
    assert check_handoffs(tmp_path) == []


# --- gate three's three REFUSALS, each taken explicitly (the row's clause 2)


def test_a_record_does_not_owe_the_six_sections_and_that_is_RATIFIED(tmp_path):
    # ⛔ `W64` left this a silence; `W172` ends it. ⭐ A record hands nothing
    # over, so *Status*, *What landed* and *For dependents* name nothing it
    # has — and applying them prints 437 findings in 98 of the 110 records.
    write(tmp_path, *record())
    assert check_handoffs(tmp_path) == []

    # ⭐ The pair: the same body as a task handoff owes all six.
    handoff = (
        RECORD.replace("ruling record — CTO round 99", "task handoff — W99")
        .replace("# CTO round 99 — closing", "# W99 — handoff")
        .replace("`CTO-99/1`", "`W99/1`")
    )
    write(tmp_path, "W99.md", handoff)
    assert set(rules(tmp_path)) == {"handoff-section"}


def test_a_record_that_marks_NO_finding_is_not_refused(tmp_path):
    # ⛔ The measurement that decides gate three: of 311 numbered claims inside
    # a record's Findings section, 92 in 27 documents carry no marker at all.
    # ⭐ A record's findings are DISPOSITIONS, not triage items; Ruling 29's
    # *a finding is a marked item* is a task handoff's contract.
    unmarked = RECORD.replace("| `[local]` | ", "| ACCEPTED | ")
    write(tmp_path, *record(unmarked))
    assert check_handoffs(tmp_path) == []

    # ⭐ The pair: a task handoff marking nothing IS refused.
    write(tmp_path, "W99.md", GOOD.replace("### 1. `[local]` a defect somewhere else", "none."))
    assert rules(tmp_path) == ["handoff-findings"]


def test_a_records_none_may_stand_BESIDE_a_real_finding(tmp_path):
    # ⚠️ In a handoff `[none]` means *nothing outside this task's scope*, so it
    # cannot stand beside a finding. ⭐ A record uses it per-finding, to mean a
    # recorded negative — all 4 in the corpus do exactly that.
    both = RECORD + (
        "| `CTO-99/2` | `[none]` | ⭐ A recorded negative: I predicted a "
        "collision and measured none. |\n"
    )
    write(tmp_path, *record(both))
    assert check_handoffs(tmp_path) == []

    # ⭐ The pair: the same pairing inside a task handoff is refused.
    handoff = GOOD.replace(
        "### 1. `[local]` a defect somewhere else",
        "### 1. `[local]` a defect somewhere else\n\n"
        "### 2. `[none]` and nothing else was outside my scope at all",
    )
    write(tmp_path, "W99.md", handoff)
    assert rules(tmp_path) == ["handoff-findings"]


# --- what NEITHER gate takes, and it is a decision (Ruling 218) -------------


def test_a_survey_is_still_outside_this_gate(tmp_path):
    # ⭐ Every reading this row inherited measured *records + surveys*, and the
    # row names ONE kind. ⛔ Admitting a second is a decision the row does not
    # make, so it is pinned here rather than left to the next reader.
    body = RECORD.replace("ruling record — CTO round 99", "survey").replace("`CTO-99/1`", "`63`")
    write(tmp_path, *record(body, "SF-12-survey.md"))
    assert check_handoffs(tmp_path) == []
