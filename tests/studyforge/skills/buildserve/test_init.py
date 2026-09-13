"""Mirror of `src/studyforge/skills/buildserve/__init__.py` (R12), and the procedure beside it."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from studyforge.cli import PROGRAM, VERBS
from studyforge.skills import buildserve
from studyforge.skills.buildserve import KNOWN
from studyforge.skills.buildserve.cli import PROG
from tests.authoring.support import rows_under
from tests.support import assert_package_contract

#: The verbs the procedure runs, in the order it runs them.
STEPS = ("validate", "narrate", "build", "serve")

#: The heading whose table names every partial state.
STATES_HEADING = "3. Read the partial states. None of them is an error"


def skill_text() -> str:
    return (Path(buildserve.__file__).parent / "SKILL.md").read_text(encoding="utf-8")


def test_states_its_contract():
    assert_package_contract(buildserve, "studyforge.skills.buildserve")


def test_the_surface_is_exactly_what_it_declares():
    assert all(hasattr(buildserve, name) for name in buildserve.__all__)
    assert len(set(buildserve.__all__)) == len(buildserve.__all__)


def test_the_procedure_ships_beside_the_package():
    # ⛔ §9: the document is the deliverable and this package is what it calls.
    assert "# Skill — build and serve" in skill_text()


def test_every_verb_the_procedure_gives_is_registered_and_in_order():
    # ⛔ Derived from the one table, never pinned: retiring a verb fails here.
    text = skill_text()
    positions = []
    for verb in STEPS:
        assert verb in VERBS, f"{verb!r} is not a registered verb"
        line = f"{PROGRAM} {verb} <corpus-root>"
        assert line in text, f"the procedure no longer gives {line!r}"
        positions.append(text.index(line))
    assert positions == sorted(positions)


def test_the_one_invocation_the_procedure_gives_is_this_package_and_it_runs():
    assert f"{PROG} <corpus-root> --out <directory>" in skill_text()
    module = PROG.removeprefix("python3 -m ")
    assert module == buildserve.__name__
    assert importlib.util.find_spec(f"{module}.__main__") is not None


def test_the_state_table_names_every_known_state_and_nothing_else():
    rows = rows_under(skill_text(), STATES_HEADING)
    named = {re.fullmatch(r"`([\w-]+)`", row[0]).group(1) for row in rows}
    assert named == {state.name for state in KNOWN}
    assert len(rows) == len(KNOWN)
