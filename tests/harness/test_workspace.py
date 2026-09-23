"""Mirror of `tests/harness/workspace.py`: the pin file READ, refused rather than repaired.

⭐ `REL-02`: the reading half of the tooling original's tests, asked of `read` directly — the
original asks them through `verify`, which stays with the tooling. Real `git init` trees from
`tests/harness/workspaces.py`; no real sibling is touched.
"""

from __future__ import annotations

import pytest

from tests.harness import workspaces as support
from tests.harness.workspace import (
    COMPONENT_KEYS,
    PIN_KEYS,
    STATUS,
    WHERE,
    WORKSPACE_API,
    Component,
    PinError,
    holds,
    read,
    workspace_root,
)


def _rows(here) -> list[dict]:
    """The rows of `here`'s pin file, as written."""
    return [
        {"name": c.name, "where": c.where, "status": c.status, "commit": c.commit}
        for c in read(here)
    ]


def test_a_correct_pin_file_reads_every_component_in_order(tmp_path):
    _, here = support.workspace(tmp_path / "w")
    assert [c.name for c in read(here)] == ["studyforge", "Alpha", "Beta"]
    assert all(isinstance(c, Component) and c.present for c in read(here))


def test_the_key_orders_are_the_format():
    assert PIN_KEYS == ("workspace_api", "components")
    assert COMPONENT_KEYS == ("name", "where", "status", "commit")


def test_a_missing_pin_file_is_a_named_refusal(tmp_path):
    (tmp_path / "empty").mkdir()
    with pytest.raises(PinError, match="workspace.json is missing"):
        read(tmp_path / "empty")


def test_an_unknown_workspace_api_is_refused_rather_than_read(tmp_path):
    _, here = support.workspace(tmp_path / "w")
    support.write_pin(here, _rows(here), api=WORKSPACE_API + 1)
    with pytest.raises(PinError, match="workspace_api"):
        read(here)


@pytest.mark.parametrize("where", ["", "parent", "child", "Sibling", None])
def test_an_unknown_where_is_refused_naming_the_ones_there_are(tmp_path, where):
    _, here = support.workspace(tmp_path / "w")
    support.write_pin(
        here, [{"name": "x", "where": where, "status": "present", "commit": "a" * 40}]
    )
    with pytest.raises(PinError) as raised:
        read(here)
    for name in WHERE:
        assert name in str(raised.value)


@pytest.mark.parametrize("status", ["", "planned", "Present", "absent", None])
def test_an_unknown_status_is_refused_naming_the_ones_there_are(tmp_path, status):
    _, here = support.workspace(tmp_path / "w")
    support.write_pin(here, [{"name": "x", "where": "sibling", "status": status}])
    with pytest.raises(PinError) as raised:
        read(here)
    for name in STATUS:
        assert name in str(raised.value)


@pytest.mark.parametrize("commit", ["", "abc", "z" * 40, "A" * 40, 1, None])
def test_a_commit_that_is_not_a_full_sha_is_refused(tmp_path, commit):
    _, here = support.workspace(tmp_path / "w")
    row = {"name": "x", "where": "sibling", "status": "present", "commit": commit}
    support.write_pin(here, [row])
    with pytest.raises(PinError, match="40-character"):
        read(here)


def test_a_component_that_does_not_exist_yet_may_not_record_a_commit(tmp_path):
    _, here = support.workspace(tmp_path / "w")
    row = {"name": "x", "where": "sibling", "status": "not-yet-created", "commit": "a" * 40}
    support.write_pin(here, [row])
    with pytest.raises(PinError, match="may not record a commit"):
        read(here)


def test_a_component_that_does_not_exist_yet_is_a_row_and_not_present(tmp_path):
    _, here = support.workspace(tmp_path / "w")
    support.write_pin(here, [{"name": "x", "where": "sibling", "status": "not-yet-created"}])
    assert [c.present for c in read(here)] == [False]


def test_an_unknown_key_anywhere_is_refused(tmp_path):
    _, here = support.workspace(tmp_path / "w")
    rows = [{**row, "url": "https://example.invalid/x.git"} for row in _rows(here)]
    support.write_pin(here, rows)
    with pytest.raises(PinError, match="component's keys"):
        read(here)


@pytest.mark.parametrize("name", ["a/b", "..", ".hidden", support.HOME_PATH, ""])
def test_a_name_that_is_not_one_path_component_is_refused_and_not_echoed(tmp_path, name):
    _, here = support.workspace(tmp_path / "w")
    support.write_pin(here, [{"name": name, "where": "sibling", "status": "not-yet-created"}])
    with pytest.raises(PinError) as raised:
        read(here)
    assert "home" not in str(raised.value)


def test_a_home_path_in_workspace_api_is_not_echoed_into_the_refusal(tmp_path):
    _, here = support.workspace(tmp_path / "w")
    support.write_pin(here, _rows(here), api=support.HOME_PATH)
    with pytest.raises(PinError) as raised:
        read(here)
    assert support.HOME_PATH not in str(raised.value)


def test_a_sibling_resolves_beside_this_repository_and_self_is_this_repository(tmp_path):
    root, here = support.workspace(tmp_path / "w")
    found = {c.name: c.directory(workspace_root(here), here) for c in read(here)}
    assert found == {"studyforge": here, "Alpha": root / "Alpha", "Beta": root / "Beta"}


def test_a_worktree_resolves_to_the_main_checkouts_parent_not_its_own(tmp_path):
    # ⭐ Agents work in worktrees, which live outside the repository they belong to.
    root, here = support.workspace(tmp_path / "w")
    elsewhere = tmp_path / "far" / "away"
    elsewhere.parent.mkdir(parents=True)
    support.run(here, "worktree", "add", "-q", "-b", "side", str(elsewhere))
    assert workspace_root(elsewhere) == root


def test_a_plain_copy_with_no_git_falls_back_to_its_parent(tmp_path):
    plain = tmp_path / "plain" / "studyforge"
    plain.mkdir(parents=True)
    assert workspace_root(plain) == plain.parent


def test_holds_answers_both_ways(tmp_path):
    _, here = support.workspace(tmp_path / "w")
    mine = support.run(here, "rev-parse", "HEAD")
    assert holds(here, mine)
    assert not holds(here, "0" * 40)
