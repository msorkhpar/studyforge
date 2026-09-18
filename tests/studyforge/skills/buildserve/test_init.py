"""Mirror of `src/studyforge/skills/buildserve/__init__.py` (R12), and the procedure beside it."""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

from studyforge.cli import PROGRAM, VERBS
from studyforge.skills import buildserve
from studyforge.skills.buildserve import KNOWN, narration
from studyforge.skills.buildserve.cli import PROG
from tests.authoring.support import rows_under
from tests.support import assert_package_contract, repository_root

#: The verbs the procedure runs, in the order it runs them.
STEPS = ("validate", "narrate", "build", "serve")

#: The heading whose table names every partial state.
STATES_HEADING = "3. Read the partial states. None of them is an error"

#: The section that tells an operator narration exists at all.
NARRATION_HEADING = "## ⭐ Narration — what provides it, and how to have it"


def skill_text() -> str:
    return (Path(buildserve.__file__).parent / "SKILL.md").read_text(encoding="utf-8")


def narration_section() -> str:
    """The narration section alone, from its heading to the next top-level one."""
    text = skill_text()
    start = text.index(NARRATION_HEADING)
    return text[start : text.index("\n## ", start + len(NARRATION_HEADING))]


def narration_prose() -> str:
    """The same section with its wrapping collapsed.

    ⚠️ A sentence in this document is wrapped wherever the column ran out, and a
    check a re-wrap could defeat is a check about the margin rather than about
    what the section says.
    """
    return " ".join(narration_section().split())


def fenced(text: str) -> list[str]:
    """Every command line inside a fence, in order. ⛔ A blank line is not a command."""
    return [
        line.strip()
        for block in re.findall(r"^```\n(.*?)^```", text, re.MULTILINE | re.DOTALL)
        for line in block.splitlines()
        if line.strip()
    ]


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


def test_the_procedure_says_narration_exists_what_provides_it_and_where_it_answers():
    # ⛔ The row: an operator following the skills is TOLD, without having to know
    # this workspace's layout. ⭐ Each fact is read from `narration`, never retyped.
    section = narration_prose()
    assert narration.COMPONENT in section
    assert narration.ADDRESS in section
    assert all(document in section for document in narration.CONTRACT)
    assert f"**`{narration.PROMISE}`**" in section, "the promise a caller built against"
    assert "loopback" in section


def test_the_procedure_says_what_the_first_start_fetches_before_it_happens():
    # ⛔ *No network beyond loopback is implied or required*: what IS fetched, once,
    # is stated rather than met as a command failing in an operator's hands.
    section = narration_prose()
    assert "pulls container images and downloads an engine model" in section
    assert "nothing this framework does leaves loopback" in section


def test_the_procedure_starts_no_container_and_says_so():
    # ⛔ Spec §8.3, and the skill's own *will not do* list carries it too.
    assert "§8.3" in narration_prose()
    assert "start, stop or reach a container" in skill_text()
    assert "docker compose" not in skill_text().lower()


def test_the_procedure_gives_no_route_of_that_component():
    # ⛔ *Must not become a second copy of the service's API*: it points instead.
    for document in narration.CONTRACT:
        assert document in narration_prose()
    assert "/v1/" not in skill_text()


def test_every_command_the_narration_section_prints_runs_as_written():
    # ⛔ `W313`'s standing bar: executed, never string-matched. ⭐ Nothing here needs
    # a service or a container, which is why these are the lines that are fenced.
    commands = fenced(narration_section())
    assert commands, "the section fences no command, so this check is vacuous"
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in ("PYTHONPATH", "PYTEST_ADDOPTS", "PYTEST_CURRENT_TEST")
    }
    environment["PYTHONPATH"] = str(repository_root() / "src")
    for command in commands:
        ran = subprocess.run(
            command.replace("python3", sys.executable, 1),
            shell=True,
            cwd=repository_root(),
            env=environment,
            capture_output=True,
            text=True,
        )
        assert ran.returncode == 0, f"{command!r}: exit {ran.returncode}\n{ran.stderr}"
        assert "Traceback" not in ran.stderr, command


def test_the_fenced_help_prints_the_address_the_section_states():
    # ⭐ The one binding that makes the section's address checkable rather than
    # asserted: the verb's own help, executed, prints it.
    command = fenced(narration_section())[0]
    environment = {**os.environ, "PYTHONPATH": str(repository_root() / "src")}
    environment.pop("PYTEST_ADDOPTS", None)
    ran = subprocess.run(
        command.replace("python3", sys.executable, 1),
        shell=True,
        cwd=repository_root(),
        env=environment,
        capture_output=True,
        text=True,
    )
    assert narration.ADDRESS in ran.stdout, ran.stdout
