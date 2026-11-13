"""Mirror of `skills.exercises.projectcli` (R12): a manifest to fill in, and what one ships."""

from __future__ import annotations

import json
import sys

from studyforge.skills.exercises.projectcli import main, skeleton, summary
from tests.studyforge.skills.exercises.project_sample import MANIFEST, SAMPLE
from tests.support import repository_root, run


def test_the_skeleton_declares_the_step_s_new_tests_and_changed_methods_and_leaves_the_rest_blank():
    made = skeleton(SAMPLE / "steps" / "00", SAMPLE / "steps" / "01", relative_to=SAMPLE)
    assert (made["before"], made["after"], made["entry"]) == ("steps/00", "steps/01", "main.py")
    assert made["expected"]["output"] == "expected/report.txt"
    declared = {one[0] for one in made["cases"]}
    assert "tests/test_model.py::test_must_ship_lots_over_capacity_are_refused" in declared
    assert "tests/test_model.py::test_picks_the_most_valuable_fit" not in declared, "a kept test"
    names = {entry["signature"].split("(")[0] for entry in made["blueprint"]}
    assert names == {"def read_lots", "def must_ship", "def best_selection", "def render"}
    assert all(entry["idea"] == "" for entry in made["blueprint"]), "an author's fact was guessed"


def test_check_summarises_the_sample_and_refuses_a_skeleton_never_filled_in(tmp_path, capsys):
    lines = summary(MANIFEST)
    assert lines[0] == "Must-ship lots" and "  kept: 4 case(s)" in lines
    assert main(["check", str(MANIFEST)]) == 0
    unfilled = tmp_path / "project.json"
    made = skeleton(SAMPLE / "steps" / "00", SAMPLE / "steps" / "01", relative_to=tmp_path)
    unfilled.write_text(json.dumps(made), encoding="utf-8")
    assert main(["check", str(unfilled)]) == 1
    assert "refused:" in capsys.readouterr().out
    assert main([]) == 2


def test_the_module_runs_as_the_documented_command():
    done = run(
        [sys.executable, "-m", "studyforge.skills.exercises.project", "check", str(MANIFEST)],
        repository_root() / "src",  # `-m` reads the package from the working directory
    )
    assert done.returncode == 0 and "Must-ship lots" in done.stdout
