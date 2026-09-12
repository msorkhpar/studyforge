"""`W64` gate two: a `ruling record` has a scope, and the ID rule reaches it.

⛔ **Every test here that goes GREEN would also have gone green before this
row**, because before it `check_handoffs` returned at the kind test and a record
was read by no rule at all. ⭐ **So the tests that matter are the ones that FIRE**
— and each is paired with the same document under a kind that was already
admitted, so the two readers cannot drift apart (`W121`'s discipline).

⚠️ **Gate three is NOT this row and is asserted absent, not asserted correct**:
`test_a_record_is_held_to_neither_the_marker_rule_nor_the_six_sections` pins the
scope of this change so that widening it later is a visible decision.
"""

from __future__ import annotations

from tools.quality.handoffs import KIND_MARKER, check_handoffs, record_scopes
from tools.quality.handoffs.records import derived_scope
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


# --- what gate two deliberately does NOT do (Ruling 218) -------------------


def test_a_record_is_held_to_neither_the_marker_rule_nor_the_six_sections(tmp_path):
    # ⛔ Gate three — a rule separating a record's Findings section from its
    # prose — is NOT YET A ROW. ⚠️ This document has a marker in prose, no six
    # sections, and no title a handoff would accept; every one of those is a
    # finding for a task handoff and none of them is one here.
    body = f"""# CTO round 99 — closing

{KIND_MARKER} ruling record — CTO round 99

The reviewer marked it `[structural]` and said so twice, `[local]` as well.
"""
    write(tmp_path, *record(body))
    assert check_handoffs(tmp_path) == []

    handoff = body.replace("ruling record — CTO round 99", "task handoff — W99")
    write(tmp_path, "W99.md", handoff)
    assert set(rules(tmp_path)) == {
        "handoff-findings",
        "handoff-marker",
        "handoff-section",
        "handoff-title",
    }


def test_a_survey_is_still_outside_this_gate(tmp_path):
    # ⭐ Every reading this row inherited measured *records + surveys*, and the
    # row names ONE kind. ⛔ Admitting a second is a decision the row does not
    # make, so it is pinned here rather than left to the next reader.
    body = RECORD.replace("ruling record — CTO round 99", "survey").replace("`CTO-99/1`", "`63`")
    write(tmp_path, *record(body, "SF-12-survey.md"))
    assert check_handoffs(tmp_path) == []
