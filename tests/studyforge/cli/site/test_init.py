"""Mirror of `src/studyforge/cli/site/__init__.py` (R12)."""

from __future__ import annotations

from studyforge.cli import site
from tests.support import assert_package_contract, repository_root


def test_states_its_contract():
    assert_package_contract(site, "studyforge.cli.site")


def test_the_package_is_tracked_despite_the_verb_being_called_build():
    # ⛔ The hazard the package name exists to avoid: `.gitignore` carries a
    # bare `build/`, which matches at every depth, so `cli/build/` would be
    # untracked from the moment it is written and every check that walks the
    # tracked tree would read it as absent.
    ignore = (repository_root() / ".gitignore").read_text("utf-8").splitlines()
    assert "build/" in [line.strip() for line in ignore], (
        "the bare `build/` rule is gone; this package's name no longer needs the workaround"
    )
    assert site.__file__ is not None and "/cli/site/" in site.__file__
