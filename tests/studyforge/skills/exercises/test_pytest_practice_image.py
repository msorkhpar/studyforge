"""The pytest practice's gates, read in a container with no network.

⭐ **The same draft, the same gates, and every run is a `docker run --network none`** over
a staged copy of the workspace. ⚠️ **Skipped unless it is told what to run in**, because
no runner image carries Python and pytest yet:

- `STUDYFORGE_PYTEST_IMAGE`: an image that has `python3` (a pinned one);
- `STUDYFORGE_PYTEST_LIBS`: a directory holding pytest and its pure-Python dependencies,
  put on `PYTHONPATH` read-only, so nothing is installed and nothing is fetched;
- `STUDYFORGE_PYTEST_STAGE`: an empty directory the staged workspaces are copied into. It is
  never under the host's temporary directory, which a Docker Desktop VM cannot mount.

⛔ A heavy job: run it through the heavy-job slot, one at a time.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

from studyforge.skills.exercises import Ran, gate_code
from tests.harness import engine
from tests.studyforge.skills.exercises import pytest_practice as practice
from tests.studyforge.skills.exercises.test_pytest_practice import _brief, _g

IMAGE, LIBS, STAGE = (
    os.environ.get(name)
    for name in ("STUDYFORGE_PYTEST_IMAGE", "STUDYFORGE_PYTEST_LIBS", "STUDYFORGE_PYTEST_STAGE")
)


class InContainer:
    """Runs each command with `--network none`, and brings the report back to the staged root."""

    def __init__(self) -> None:
        self.networks: list[str] = []

    def __call__(self, root: Path, command: tuple[str, ...]) -> Ran:
        work = Path(STAGE) / uuid.uuid4().hex
        shutil.copytree(root, work)
        try:
            argv = [
                "docker",
                "--context",
                "desktop-linux",
                "run",
                "--rm",
                "--network",
                "none",
                *engine.run_as(),
                "-e",
                "PYTHONPATH=/libs",
                "-e",
                "PYTHONDONTWRITEBYTECODE=1",
                "-v",
                f"{engine.bindable(work)}:/w",
                "-v",
                f"{engine.bindable(LIBS)}:/libs:ro",
                "-w",
                "/w",
                "--entrypoint",
                command[0],
                IMAGE,
                *command[1:],
            ]
            self.networks.append(argv[argv.index("--network") + 1])
            done = subprocess.run(  # noqa: S603 - fixed argv, no shell
                argv, capture_output=True, text=True, check=False, stdin=subprocess.DEVNULL
            )
            for produced in work.rglob("target"):
                shutil.copytree(produced, root / produced.relative_to(work), dirs_exist_ok=True)
            return Ran(done.returncode, done.stdout + done.stderr)
        finally:
            shutil.rmtree(work, ignore_errors=True)


@pytest.mark.skipif(
    not (IMAGE and LIBS and STAGE),
    reason="set STUDYFORGE_PYTEST_IMAGE, STUDYFORGE_PYTEST_LIBS and STUDYFORGE_PYTEST_STAGE",
)
def test_every_gate_holds_when_every_run_is_a_container_with_no_network(tmp_path):
    brief, ledger = _brief(tmp_path)
    runner = InContainer()
    gated = gate_code(practice.draft(brief), brief, ledger, runner, source="demo", where="w")
    assert gated.clears, [verdict.says for verdict in gated.refused]
    assert len(runner.networks) == 6 and set(runner.networks) == {"none"}
    assert all(_g(gated, gate).held for gate in ("G1", "G2", "G3", "G4", "G5"))
