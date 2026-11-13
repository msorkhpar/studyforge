r"""Checks about a project practice's workspace: every file it names is there, and nothing else is.

**What it does.** The arm project practices owe `studyforge validate`. For every practice whose
record names `read_only` files (a project, `exercise.workfiles`), it requires each file the record
names to be in the workspace, and names each file in the workspace the record does not name.

**How you use it.** `CHECKS`, which `validate.run` drains like every other check's tuple. Each
function takes the `Walk` and yields `Finding`s.

**Depends on.** `exercise` for the record and `ExerciseError`, `exercise.bundle` for the run
output directory, `validate.corpus` and `validate.report`. Standard library otherwise.

⛔ **Every check yields; none raises.** One run reports every problem (R6).

## ⭐ EVERY FILE IS VISIBLE, SO A FILE THE RECORD DOES NOT NAME IS A FINDING

⭐ A project's page lists every file of its workspace and its explorer opens each one, both read
off the record. ⛔ So a file in the workspace that the record does not name is one the reader can
never see, and a file the record names that is not there is a button that opens nothing. ⚠️ A
run's output (`target/`), the editor's own folder (`.vscode/`), a cache and a dot-file are a
run's or a tool's, never the project's, and are not judged.
"""

from __future__ import annotations

import posixpath
from collections.abc import Iterator

from studyforge.exercise import ExerciseError
from studyforge.exercise import of as exercise_of
from studyforge.exercise.bundle import RUN_OUTPUT_DIRNAME
from studyforge.validate.corpus import Walk
from studyforge.validate.report import Finding

#: A project practice whose workspace and record disagree about which files it has.
RULE_PROJECT_FILES = "project-files"

#: What a workspace holds that is a run's or a tool's, never the project's, at any depth.
NOT_JUDGED = (RUN_OUTPUT_DIRNAME, "__pycache__")


def check_project_files(walk: Walk) -> Iterator[Finding]:
    """Every file a project's record names is in its workspace, and the workspace holds no other."""
    for unit in walk.units:
        if unit.document.get("kind") != "practice":
            continue
        try:
            exercise = exercise_of(unit.document, unit.where)
        except ExerciseError:  # pragma: no cover - `validate.corpus` refuses it first
            continue
        if exercise is None or exercise.read_only is None:
            continue
        named = {
            exercise.main_path,
            *(exercise.files or ()),
            *((exercise.test_path,) if exercise.test_path else ()),
            *exercise.read_only,
        }
        base = posixpath.commonpath([posixpath.dirname(path) for path in named])
        held = set(_workspace_files(walk, base))
        for path in sorted(named - held):
            yield Finding(
                RULE_PROJECT_FILES,
                unit.where,
                f"names '{path}', which its workspace does not hold, so the project's explorer "
                f"would offer a file that opens nothing.",
            )
        for path in sorted(held - named):
            yield Finding(
                RULE_PROJECT_FILES,
                unit.where,
                f"holds '{path}' in its workspace and its record does not name it, so a reader "
                f"never sees it. Every file of a project is visible: author it into the practice, "
                f"or take it out of the workspace.",
            )


def _workspace_files(walk: Walk, base: str) -> Iterator[str]:
    """Every file under the workspace, corpus-relative, but a run's, a tool's and a dot-file."""
    root = walk.root / base
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        parts = relative.split("/")
        if path.is_file() and not any(p in NOT_JUDGED or p.startswith(".") for p in parts):
            yield f"{base}/{relative}"


#: The one check this arm owes.
CHECKS = (check_project_files,)
