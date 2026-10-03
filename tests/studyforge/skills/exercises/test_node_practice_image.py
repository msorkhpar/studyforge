"""The TypeScript practice's gates, read in a container with no network.

⭐ **The same draft, the same gates, and every run (the tests and the optional type check) is a
`docker run --network none`** over a staged copy of the workspace, in a runner image whose Node
strips types. ⚠️ **Skipped unless it is told what to run in**, because no runner image carries
`typescript` yet (the `claude-sdks` profile will):

- `STUDYFORGE_NODE_IMAGE`: a runner image that has `node` (a pinned one);
- `STUDYFORGE_TSC_DIR`: a directory holding the unpacked `typescript` package, put at `/ts`
  read-only, so nothing is installed and nothing is fetched;
- `STUDYFORGE_NODE_STAGE`: an empty directory the staged workspaces are copied into. It is
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
from tests.studyforge.skills.exercises import node_practice as practice
from tests.studyforge.skills.exercises.test_node_practice import _solutions
from tests.studyforge.skills.exercises.test_pytest_practice import _brief, _g

IMAGE, LIBS, STAGE = (
    os.environ.get(name)
    for name in ("STUDYFORGE_NODE_IMAGE", "STUDYFORGE_TSC_DIR", "STUDYFORGE_NODE_STAGE")
)


class InContainer:
    """Runs each command with `--network none`, and brings the report back to the staged root."""

    def __init__(self, solutions: dict[str, str]) -> None:
        self.networks: list[str] = []
        self.solutions = solutions
        self.typechecks: list[Ran] = []
        self.outputs: dict[str, str] = {}

    def __call__(self, root: Path, command: tuple[str, ...]) -> Ran:
        work = Path(STAGE) / uuid.uuid4().hex
        shutil.copytree(root, work)
        if command[0] == "tsc":
            command = ("node", "/ts/bin/tsc", *command[1:])
        try:
            argv = [
                "docker", "--context", "desktop-linux", "run", "--rm", "--network", "none",
                *engine.run_as(),
                "-v", f"{engine.bindable(work)}:/w",
                "-v", f"{engine.bindable(LIBS)}:/ts:ro",
                "-w", "/w",
                "--entrypoint", command[0], IMAGE, *command[1:],
            ]
            self.networks.append(argv[argv.index("--network") + 1])
            done = subprocess.run(  # noqa: S603 - fixed argv, no shell
                argv, capture_output=True, text=True, check=False, stdin=subprocess.DEVNULL
            )
            for produced in work.rglob("target"):
                shutil.copytree(produced, root / produced.relative_to(work), dirs_exist_ok=True)
            ran = Ran(done.returncode, done.stdout + done.stderr)
            if command[1:2] == ("/ts/bin/tsc",):
                self.typechecks.append(ran)
            else:
                placed = next(work.rglob("normalise.ts")).read_text(encoding="utf-8")
                role = next(n for n, text in self.solutions.items() if text == placed)
                self.outputs[role] = ran.output
            return ran
        finally:
            shutil.rmtree(work, ignore_errors=True)


needs_image = pytest.mark.skipif(
    not (IMAGE and LIBS and STAGE),
    reason="set STUDYFORGE_NODE_IMAGE, STUDYFORGE_TSC_DIR and STUDYFORGE_NODE_STAGE",
)


def _typed(brief, **parts):
    return practice.draft(
        brief, typecheck_command=practice.type_check(brief.places.workspace), **parts
    )


@needs_image
def test_every_gate_holds_when_every_run_is_a_container_with_no_network(tmp_path):
    brief, ledger = _brief(tmp_path)
    made = _typed(brief)
    runner = InContainer(_solutions(made))
    gated = gate_code(made, brief, ledger, runner, source="demo", where="w")
    assert gated.clears, [verdict.says for verdict in gated.refused]
    assert len(runner.networks) == 12 and set(runner.networks) == {"none"}
    assert len(runner.typechecks) == 6 and all(ran.exit_code == 0 for ran in runner.typechecks)
    assert all(_g(gated, gate).held for gate in ("G1", "G2", "G3", "G4", "G5"))
    for role, output in runner.outputs.items():
        if role != "reference":
            assert "AssertionError [ERR_ASSERTION]" in output, role


@needs_image
def test_a_type_error_is_refused_by_name_and_a_planted_enum_by_nodes_message(tmp_path):
    brief, ledger = _brief(tmp_path)
    typed = _typed(brief, reference=practice.TYPE_ERROR_REFERENCE)
    gated = gate_code(typed, brief, ledger, InContainer(_solutions(typed)), source="demo",
                      where="w")
    assert "type check" in _g(gated, "G1").says and not _g(gated, "G1").held

    plants = dict(practice.draft(brief).plants)
    plants[practice.BLANK.id] = practice.ENUM_PLANT
    planted = practice.draft(brief, plants=plants)
    runner = InContainer(_solutions(planted))
    gate_code(planted, brief, ledger, runner, source="demo", where="w")
    assert "TypeScript enum is not supported in strip-only mode" in runner.outputs[
        "plant:" + practice.BLANK.id
    ]
