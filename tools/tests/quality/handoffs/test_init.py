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
    OFFICE_HANDOFF,
    TASK_HANDOFF,
    check_handoffs,
    declared_kind,
)
from tools.tests.quality.handoffs.support import GOOD, rules, write

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


@pytest.mark.parametrize(
    "kind", [k for k in DOCUMENT_KINDS if k not in (TASK_HANDOFF, OFFICE_HANDOFF)]
)
def test_a_document_that_is_not_a_task_handoff_owes_only_its_declaration(tmp_path, kind):
    # ⛔ The trap this check was written to avoid: `docs/tasks/handoffs/` holds
    # surveys, ruling records and session logs, and a naive migration would
    # demand six sections of a document that owes none. ⭐ A survey is not
    # excused by an exclusion list — it says what it is.
    write(tmp_path, "anything.md", f"# Some title\n\n{KIND_MARKER} {kind}\n\nProse.\n")
    assert check_handoffs(tmp_path) == []


def test_an_office_handoff_owes_everything_a_task_handoff_owes(tmp_path):
    # ⛔ The one kind that is NOT an escape hatch. ⭐ It exists because the id
    # space has ONE MINTER, so a supervising office asked to restructure
    # something has no ID to declare — and every other kind it could have
    # borrowed owes NOTHING. ⚠️ A kind that lets a document escape the contract
    # is not a kind, it is a hole.
    body = f"# Some title\n\n{KIND_MARKER} office handoff — ARCH\n\nProse.\n"
    write(tmp_path, "anything.md", body)
    assert "handoff-section" in rules(tmp_path)
    assert "handoff-title" in rules(tmp_path)


def test_an_office_handoff_may_not_name_a_task_id(tmp_path):
    # ⛔ Naming one would be MINTING one, which is the PO's and nobody else's.
    body = f"# Some title — handoff\n\n{KIND_MARKER} office handoff — W99\n\nProse.\n"
    write(tmp_path, "anything.md", body)
    assert "handoff-kind" in rules(tmp_path)


def test_an_office_handoff_numbers_its_findings_inside_its_own_scope(tmp_path):
    # ⭐ `ARCH/1`, not `W99/1`: the declared SCOPE is what findings are numbered
    # inside, exactly as a task ID is for a task handoff.
    good = GOOD.replace("**Kind:** task handoff — W99", "**Kind:** office handoff — ARCH")
    good = good.replace("# W99 — handoff", "# Board architecture — handoff")
    good = good.replace("W99/", "ARCH/")
    write(tmp_path, "anything.md", good)
    assert "handoff-finding-id" not in rules(tmp_path)


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


def test_the_ruling_record_sentence_names_every_role_that_writes_one():
    # ⛔ `W31`, from `PO-19/5`: the registry's sentences named **two** roles
    # where **three** produce these documents. `ruling record` read *"a CTO
    # round or a single ruling written up"* and `session log` reads *"a
    # coordinator's record of one session"* — ⚠️ a **PO round** is neither, and
    # four of them are in the shipped tree.
    #
    # ⭐ The kind was right and the sentence was short by one role, so the fix
    # is the sentence. ⛔ Never a sixth kind: a role is not a kind of document,
    # and `DOCUMENT_KINDS` is a closed set whose entries are decisions.
    #
    # ⚠️ Asserted against the tree rather than against the string alone. A
    # sentence describing what may live here is only true if what lives here
    # matches it, and that is the half a spelling check cannot see.
    po_rounds = sorted((repository_root() / HANDOFF_DIR).glob("PO-*.md"))
    assert po_rounds, "no PO round in this tree; this assertion has stopped meaning anything"
    for path in po_rounds:
        kind, _ids, _line = declared_kind(path.read_text(encoding="utf-8"))
        assert kind == "ruling record", f"{path.name} declares {kind!r}"
    sentence = DOCUMENT_KINDS["ruling record"]
    for role in ("CTO", "PO"):
        assert role in sentence, f"the sentence does not admit a {role} round: {sentence!r}"
    assert not [kind for kind in DOCUMENT_KINDS if "round" in kind], (
        f"a round is written up as a ruling record, not as a kind of its own: {DOCUMENT_KINDS}"
    )


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
