"""Mirror of `src/studyforge/skills/personalarchive/__init__.py` (R12), and its procedure."""

from __future__ import annotations

import importlib.util
import re

from studyforge.skills import personalarchive
from studyforge.skills.personalarchive import KINDS, OUTCOMES
from studyforge.skills.personalarchive.cli import PROG
from tests.authoring.support import rows_under
from tests.studyforge.skills.personalarchive.archiving import skill_text
from tests.support import assert_package_contract

#: The heading whose table names every report line.
LINES = "3. Read what it merged"


def test_states_its_contract():
    assert_package_contract(personalarchive, "studyforge.skills.personalarchive")


def test_the_surface_is_exactly_what_it_declares():
    assert all(hasattr(personalarchive, name) for name in personalarchive.__all__)
    assert len(set(personalarchive.__all__)) == len(personalarchive.__all__)


def test_the_procedure_ships_beside_the_package_and_states_both_rules():
    text = skill_text()
    assert "# Skill — personal archive" in text
    assert "## ⛔ The merge rule" in text and "## ⛔ The belief rule" in text


def test_both_invocations_the_procedure_gives_are_this_package_and_it_runs():
    text = skill_text()
    choice = "<" + "|".join(KINDS) + ">"
    assert f"{PROG} export <corpus-root> <archive-file> --for {choice}" in text
    assert f"{PROG} import <archive-file> <corpus-root>" in text
    module = PROG.removeprefix("python3 -m ")
    assert module == personalarchive.__name__
    assert importlib.util.find_spec(f"{module}.__main__") is not None


def test_the_report_table_names_every_progress_outcome_and_nothing_else():
    rows = rows_under(skill_text(), LINES)
    named = {re.match(r"`progress (\w+)", row[0]).group(1) for row in rows if "`progress" in row[0]}
    assert named == set(OUTCOMES)
