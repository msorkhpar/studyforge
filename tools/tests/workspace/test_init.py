"""Mirror of `tools/workspace/__init__.py` (R12)."""

from __future__ import annotations

import json

import pytest

from tools.tests.workspace import support
from tools.workspace import (
    COMPONENT_KEYS,
    PIN_KEYS,
    STATUS,
    WHERE,
    WORKSPACE_API,
    Component,
    PinError,
    read,
    record,
    render,
    verify,
)

# --------------------------------------------------------------------------
# ⭐ the two failure directions — asserted, never described
# --------------------------------------------------------------------------


def test_a_correct_workspace_verifies_clean(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    assert verify(root, here) == []


def test_a_recorded_commit_absent_locally_is_named(tmp_path):
    # ⛔ **Direction one.** The pin points at nothing, and nothing about the
    # checkout says so: the component is present, on a branch, and looks fine.
    root, here = support.workspace(tmp_path / "w")
    rows = [{**row, "commit": "0" * 40} if row["name"] == "Alpha" else row for row in _rows(here)]
    support.write_pin(here, rows)
    found = verify(root, here)
    assert len(found) == 1
    assert found[0].startswith("Alpha: ")
    assert "not in that checkout" in found[0]


def test_a_component_whose_head_moved_unrecorded_is_named(tmp_path):
    # ⛔ **Direction two, and the one nobody thinks of.** Every recorded commit
    # is present, so the naive check passes — and a build that "reproduced"
    # this workspace would reproduce a different one.
    root, here = support.workspace(tmp_path / "w")
    moved = support.commit(root / "Beta", "moved")
    found = verify(root, here)
    assert len(found) == 1
    assert found[0].startswith("Beta: ")
    assert moved[:12] in found[0]


def test_a_component_with_no_checkout_at_all_is_named(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    gamma = {"name": "Gamma", "where": "sibling", "status": "present", "commit": "a" * 40}
    rows = _rows(here) + [gamma]
    support.write_pin(here, rows)
    found = verify(root, here)
    assert [f.split(":")[0] for f in found] == ["Gamma"]
    assert "no checkout found" in found[0]


def test_every_disagreeing_component_is_named_not_only_the_first(tmp_path):
    # ⚠️ R6: a report that stops at the first fault makes somebody run it
    # four times to learn four things.
    root, here = support.workspace(tmp_path / "w")
    support.commit(root / "Alpha", "moved")
    support.commit(root / "Beta", "moved")
    assert len(verify(root, here)) == 2


# --------------------------------------------------------------------------
# ⚠️ `studyforge`'s own row is ancestry, because equality is unrepresentable
# --------------------------------------------------------------------------


def test_this_repository_verifies_by_ancestry_so_new_commits_are_fine(tmp_path):
    # ⭐ A file inside a repository cannot hold the hash of the commit that
    # holds it, so `self` is verified as present and reachable from HEAD.
    root, here = support.workspace(tmp_path / "w")
    support.commit(here, "the commit that recorded the pin file")
    assert verify(root, here) == []


def test_a_self_row_naming_a_commit_this_repository_does_not_have_is_named(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    rows = [{**row, "commit": "0" * 40} if row["where"] == "self" else row for row in _rows(here)]
    support.write_pin(here, rows)
    found = verify(root, here)
    assert found[0].startswith("studyforge: ")


def test_a_self_row_on_a_commit_that_is_not_an_ancestor_is_named(tmp_path):
    # ⚠️ Present locally and still wrong: a commit on an abandoned branch is in
    # the object database and is not what this checkout is.
    root, here = support.workspace(tmp_path / "w")
    support.run(here, "checkout", "-q", "-b", "side")
    orphan = support.commit(here, "side")
    support.run(here, "checkout", "-q", "main")
    rows = [{**row, "commit": orphan} if row["where"] == "self" else row for row in _rows(here)]
    support.write_pin(here, rows)
    found = verify(root, here)
    assert "is not an ancestor of HEAD" in found[0]


# --------------------------------------------------------------------------
# ⛔ the file itself is refused rather than repaired
# --------------------------------------------------------------------------


def test_a_missing_pin_file_is_a_named_refusal(tmp_path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(PinError, match="workspace.json is missing"):
        read(tmp_path / "empty")


def test_an_unknown_workspace_api_is_refused_rather_than_read(tmp_path):
    # ⛔ R9: contracts are versioned, and an unknown version is refused rather
    # than read as the version this tool happens to know.
    root, here = support.workspace(tmp_path / "w")
    support.write_pin(here, _rows(here), api=WORKSPACE_API + 1)
    with pytest.raises(PinError, match="workspace_api"):
        verify(root, here)


@pytest.mark.parametrize("where", ["", "parent", "child", "Sibling", None])
def test_an_unknown_where_is_refused_naming_the_ones_there_are(tmp_path, where):
    # ⭐ Enumerate the legal: a workspace has exactly two kinds of member, so
    # the set is closed and an unforeseen value is refused rather than resolved.
    root, here = support.workspace(tmp_path / "w")
    support.write_pin(
        here, [{"name": "x", "where": where, "status": "present", "commit": "a" * 40}]
    )
    with pytest.raises(PinError) as raised:
        verify(root, here)
    for name in WHERE:
        assert name in str(raised.value)


@pytest.mark.parametrize("commit", ["", "abc", "z" * 40, "A" * 40, 1, None])
def test_a_commit_that_is_not_a_full_sha_is_refused(tmp_path, commit):
    # ⚠️ Full, because an abbreviation that is unique today can become
    # ambiguous, and a pin that resolves to two commits pins nothing.
    root, here = support.workspace(tmp_path / "w")
    row = {"name": "x", "where": "sibling", "status": "present", "commit": commit}
    support.write_pin(here, [row])
    with pytest.raises(PinError, match="40-character"):
        verify(root, here)


def test_an_unknown_key_anywhere_is_refused(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    rows = [{**row, "url": "https://example.invalid/x.git"} for row in _rows(here)]
    support.write_pin(here, rows)
    with pytest.raises(PinError, match="component's keys"):
        verify(root, here)


# --------------------------------------------------------------------------
# recording
# --------------------------------------------------------------------------


def test_recording_pins_every_component_to_what_is_checked_out_now(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    moved = support.commit(root / "Alpha", "moved")
    document = record(root, here)
    assert [row["commit"] for row in document["components"] if row["name"] == "Alpha"] == [moved]
    support.write_pin(here, document["components"])
    assert verify(root, here) == []


def test_recording_never_invents_a_component(tmp_path):
    # ⛔ Two of the six components do not exist yet, and their rows are added by
    # the tasks that create them. A `record` that discovered directories would
    # pin whatever happened to be beside the repository that day.
    root, here = support.workspace(tmp_path / "w")
    (root / "SomethingElse").mkdir()
    support.repository(root / "SomethingElse")
    assert [row["name"] for row in record(root, here)["components"]] == [
        "studyforge",
        "Alpha",
        "Beta",
    ]


def test_recording_twice_produces_identical_bytes(tmp_path):
    # ⛔ R10. A re-record with nothing changed must be a no-op in the diff, or
    # nobody can tell an advance from a reformat.
    root, here = support.workspace(tmp_path / "w")
    once = render(record(root, here))
    (here / "workspace.json").write_text(once, encoding="utf-8")
    assert render(record(root, here)) == once


def test_the_key_order_is_the_format(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    document = record(root, here)
    assert tuple(document) == PIN_KEYS
    assert all(tuple(row) == COMPONENT_KEYS for row in document["components"])


def test_a_component_resolves_without_the_file_naming_a_path(tmp_path):
    # ⭐ The whole design in one assertion: `sibling` becomes a real directory
    # at run time, and the file said only a name.
    root, here = support.workspace(tmp_path / "w")
    component = Component(name="Alpha", where="sibling", status="present", commit="a" * 40)
    assert component.directory(root, here) == root / "Alpha"
    assert Component("studyforge", "self", "present", "a" * 40).directory(root, here) == here


def _rows(repository_root):
    """Return the rows currently on disk, as plain dicts in key order."""
    rows = []
    for component in read(repository_root):
        row = {"name": component.name, "where": component.where, "status": component.status}
        if component.commit is not None:
            row["commit"] = component.commit
        rows.append(row)
    return rows


# --------------------------------------------------------------------------
# ⛔ the file is clean and the reader must be too: three probes, reproduced
# --------------------------------------------------------------------------


def test_a_home_path_in_workspace_api_is_not_echoed_into_the_refusal(tmp_path):
    # ⛔ **Probe one.** A refusal that quotes the value it refuses copies it
    # into a build log, from the check that exists to stop it getting there.
    root, here = support.workspace(tmp_path / "w")
    (here / "workspace.json").write_text(
        json.dumps({"workspace_api": support.HOME_PATH, "components": []}), encoding="utf-8"
    )
    with pytest.raises(PinError) as raised:
        verify(root, here)
    assert support.HOME_PATH not in str(raised.value)
    assert "a str" in str(raised.value)
    assert str(WORKSPACE_API) in str(raised.value)


def test_a_home_path_in_a_name_is_not_echoed_into_the_refusal(tmp_path):
    # ⛔ **Probe two**, and the shape that carries a home directory is exactly
    # the shape being refused — so the refusal names what is *permitted*.
    root, here = support.workspace(tmp_path / "w")
    row = {"name": support.HOME_PATH, "where": "sibling", "status": "present", "commit": "a" * 40}
    support.write_pin(here, [row])
    with pytest.raises(PinError) as raised:
        verify(root, here)
    assert support.HOME_PATH not in str(raised.value)
    assert "single path component" in str(raised.value)


@pytest.mark.parametrize(
    "name",
    [
        "..",
        ".",
        "../../elsewhere",
        "sub/dir",
        "-leading-dash",
        "trailing-dot.",
        "with space",
        "",
        None,
        1,
    ],
)
def test_a_name_that_is_not_one_path_component_is_refused(tmp_path, name):
    # ⛔ **Probe three, and the root cause of all three.** `where` was a closed
    # set and `name` was free text **in the same row** — so a name could hold a
    # traversal, an absolute path or a home directory, and resolve outside the
    # workspace root. ⭐ Constrained, the echo and the escape become
    # unrepresentable *together*: this is `where`'s own move carried the rest of
    # the way.
    root, here = support.workspace(tmp_path / "w")
    row = {"name": name, "where": "sibling", "status": "present", "commit": "a" * 40}
    support.write_pin(here, [row])
    with pytest.raises(PinError, match="single path component"):
        verify(root, here)


def test_an_absolute_name_cannot_resolve_outside_the_workspace(tmp_path):
    # ⚠️ The escape asserted where it would have happened, not only where it is
    # refused: `Path("/w") / "/etc"` is `/etc`, so an accepted absolute name
    # would have silently left the workspace root behind.
    root, here = support.workspace(tmp_path / "w")
    row = {"name": "/etc", "where": "sibling", "status": "present", "commit": "a" * 40}
    support.write_pin(here, [row])
    with pytest.raises(PinError, match="single path component"):
        verify(root, here)
    # ⭐ And the positive half, on rows that *are* accepted: every name the
    # contract admits resolves under the workspace root. `Path("/w") / "/etc"`
    # is `/etc`, so an accepted absolute name would have left it silently.
    support.write_pin(here, _accepted(root, here))
    for component in read(here):
        assert component.directory(root, here).is_relative_to(root)


def _accepted(root, here):
    """Rows that are on contract, for asserting what resolution does with them."""
    return [
        {"name": "studyforge", "where": "self", "status": "present", "commit": "a" * 40},
        {"name": "a.b_c-d", "where": "sibling", "status": "present", "commit": "b" * 40},
        {"name": "Later", "where": "sibling", "status": "not-yet-created"},
    ]


# --------------------------------------------------------------------------
# ⛔ Ruling 54 — the pin file is the register, and `status` is how it says so
# --------------------------------------------------------------------------


def test_a_component_that_does_not_exist_yet_is_a_row_not_an_omission(tmp_path):
    # ⭐ The owed half, sayable in the register itself. Without it the fact
    # lives in a second file and E12 and E13 have to remember it.
    root, here = support.workspace(tmp_path / "w")
    rows = _rows(here) + [{"name": "Later", "where": "sibling", "status": "not-yet-created"}]
    support.write_pin(here, rows)
    assert verify(root, here) == []


def test_a_component_recorded_as_absent_that_now_exists_is_named(tmp_path):
    # ⛔ **The third failure direction, and it is what makes the row a register
    # entry rather than a note.** The day the component is created this reds,
    # so it cannot be created and forgotten.
    root, here = support.workspace(tmp_path / "w")
    rows = _rows(here) + [{"name": "Later", "where": "sibling", "status": "not-yet-created"}]
    support.write_pin(here, rows)
    support.repository(root / "Later")
    found = verify(root, here)
    assert len(found) == 1
    assert found[0].startswith("Later: ")
    assert "set status to 'present'" in found[0]


def test_a_present_component_with_no_commit_is_refused(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    support.write_pin(here, [{"name": "Alpha", "where": "sibling", "status": "present"}])
    with pytest.raises(PinError, match="must record a full"):
        verify(root, here)


def test_a_component_that_does_not_exist_yet_may_not_record_a_commit(tmp_path):
    # ⛔ Both directions of "exactly when". A placeholder commit for a
    # repository that does not exist is the file pretending.
    root, here = support.workspace(tmp_path / "w")
    row = {"name": "Later", "where": "sibling", "status": "not-yet-created", "commit": "a" * 40}
    support.write_pin(here, [row])
    with pytest.raises(PinError, match="may not record a commit"):
        verify(root, here)


@pytest.mark.parametrize("status", ["", "planned", "Present", "absent", None])
def test_an_unknown_status_is_refused_naming_the_ones_there_are(tmp_path, status):
    root, here = support.workspace(tmp_path / "w")
    row = {"name": "Alpha", "where": "sibling", "status": status, "commit": "a" * 40}
    support.write_pin(here, [row])
    with pytest.raises(PinError) as raised:
        verify(root, here)
    for name in STATUS:
        assert name in str(raised.value)


def test_recording_leaves_a_not_yet_created_row_alone(tmp_path):
    # ⭐ Flipping the status is E12's decision, in the commit that creates the
    # repository — never a side effect of somebody running `record`.
    root, here = support.workspace(tmp_path / "w")
    rows = _rows(here) + [{"name": "Later", "where": "sibling", "status": "not-yet-created"}]
    support.write_pin(here, rows)
    support.repository(root / "Later")
    later = [r for r in record(root, here)["components"] if r["name"] == "Later"]
    assert later == [{"name": "Later", "where": "sibling", "status": "not-yet-created"}]
