"""Mirror of `tests/harness/workspace.py`: a sibling is found through ONE variable, or not at all.

⭐ Every case passes its own environment, so none depends on how the run that hosts it was
started. Real `git init` trees from `tests/harness/workspaces.py`; no real sibling is touched.
"""

from __future__ import annotations

import pytest

from tests.harness import workspaces as support
from tests.harness.workspace import (
    WORKSPACE_ENV,
    absence,
    head,
    holds,
    sibling,
    workspace_root,
)


def test_the_variable_names_the_workspace_and_its_absence_names_none(tmp_path):
    assert workspace_root(support.environ(tmp_path)) == tmp_path
    assert workspace_root({}) is None
    assert workspace_root({WORKSPACE_ENV: ""}) is None


def test_a_sibling_is_the_named_directory_under_its_own_name(tmp_path):
    support.repository(tmp_path / "Alpha")
    assert sibling("Alpha", support.environ(tmp_path)) == tmp_path / "Alpha"


def test_no_variable_means_no_sibling_even_when_one_sits_beside_this_repository(tmp_path):
    # ⛔ The clause: nothing is guessed. A checkout next to the tree is not found unless named.
    support.repository(tmp_path / "Alpha")
    assert sibling("Alpha", {}) is None
    assert WORKSPACE_ENV in absence("Alpha", {}) and "not set" in absence("Alpha", {})


def test_a_named_workspace_without_the_checkout_says_so(tmp_path):
    environ = support.environ(tmp_path)
    assert sibling("Nowhere", environ) is None
    said = absence("Nowhere", environ)
    assert "Nowhere" in said and WORKSPACE_ENV in said
    # ⛔ R7: the sentence is printed into skips, so it carries no path.
    assert str(tmp_path) not in said


@pytest.mark.parametrize("name", ["a/b", "..", ".hidden", support.HOME_PATH, ""])
def test_a_name_that_is_not_one_path_component_is_refused_and_not_echoed(tmp_path, name):
    with pytest.raises(ValueError) as raised:
        sibling(name, support.environ(tmp_path))
    assert "home" not in str(raised.value)


def test_head_and_holds_answer_both_ways(tmp_path):
    mine = support.repository(tmp_path / "Alpha")
    assert head(tmp_path / "Alpha") == mine
    assert holds(tmp_path / "Alpha", mine)
    assert not holds(tmp_path / "Alpha", "0" * 40)
    (tmp_path / "plain").mkdir()
    assert head(tmp_path / "plain") is None
