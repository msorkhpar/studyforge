"""Mirror of `src/studyforge/cli/narrate/__init__.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.cli import VERBS, narrate
from studyforge.cli.narrate.cli import main
from tests.support import assert_package_contract, repository_root


def test_states_its_contract():
    assert_package_contract(narrate, "studyforge.cli.narrate")


@pytest.mark.parametrize("name", narrate.__all__)
def test_every_public_name_exists(name):
    assert hasattr(narrate, name)


def test_the_verb_is_registered_in_the_one_table_against_this_main():
    assert VERBS["narrate"].run is main


def test_the_verb_precedes_build_in_the_table():
    # ⛔ Clips are a build's input, so narrate comes first.
    names = list(VERBS)
    assert names.index("narrate") < names.index("build")


def test_the_package_lives_in_cli_and_not_inside_narrate():
    # ⛔ `narrate/` speaks and synthesises; this package is its caller.
    assert (repository_root() / "src/studyforge/cli/narrate/__init__.py").is_file()
    assert not (repository_root() / "src/studyforge/narrate/cli").exists()
