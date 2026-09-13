"""Mirror of `src/studyforge/skills/personalarchive/__main__.py` (R12): the skill as real processes.

⛔ Two processes, as two machines would run it: one exports, the other imports.
"""

from __future__ import annotations

import os
import subprocess
import sys

from tests.studyforge.skills.personalarchive.archiving import TIMES, entry, machine, run
from tests.support import repository_root


def skill(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "studyforge.skills.personalarchive", *arguments],
        cwd=repository_root(),
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_one_process_exports_and_another_imports_the_same_record(tmp_path):
    first = machine(tmp_path, "a")
    run(first, passed=False, when=TIMES["t1"])
    run(first, passed=True, when=TIMES["t2"])
    archive = tmp_path / "mine.zip"
    exported = skill("export", str(first), str(archive), "--for", "owner")
    assert exported.returncode == 0, exported.stdout + exported.stderr
    second = machine(tmp_path, "b", corpus=False)
    restored = skill("import", str(archive), str(second))
    assert restored.returncode == 0, restored.stdout + restored.stderr
    assert entry(second) == entry(first)
    assert restored.stdout.splitlines()[-1] == "import exit 0"


def test_a_missing_choice_is_a_usage_error_from_the_process(tmp_path):
    missing = skill("export", str(machine(tmp_path, "a")), str(tmp_path / "x.zip"))
    assert missing.returncode == 2 and "--for" in missing.stderr
    assert not (tmp_path / "x.zip").exists()
