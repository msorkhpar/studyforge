"""Mirror of `src/studyforge/narrate/release/__init__.py` (R12).

⭐ The package's surface is what its three modules export, and the two commands
its docstring gives are the narrate verb's own flags.
"""

from __future__ import annotations

from studyforge import narrate
from studyforge.cli.narrate.cli import build_parser
from studyforge.narrate import release
from tests.support import assert_package_contract


def test_states_its_contract():
    assert_package_contract(release, "studyforge.narrate.release")


def test_every_exported_name_resolves():
    for name in release.__all__:
        assert hasattr(release, name), name


def test_the_commands_it_gives_are_flags_the_verb_takes():
    flags = {option for action in build_parser()._actions for option in action.option_strings}
    for flag in ("--pack", "--upload", "--tag", "--dry-run"):
        assert flag in flags
        assert flag in release.__doc__


def test_the_parent_package_does_not_load_it():
    # ⭐ Narration's own surface stays the one predicate; release is reached by name.
    assert "release" not in narrate.__all__
