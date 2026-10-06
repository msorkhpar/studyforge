"""The runner the authoring pass uses in a container: every gate's command, `--network none`.

⭐ **The same image a reader's graded run uses**, so a gate reads what a reader's Submit will
read. Nothing is mounted: the staged workspace goes into a created container with `docker cp`
and the run's output comes back the same way, so it works on any engine, Windows included,
and never binds a host temporary directory. The container has no network, runs as the runner
image's own user, has a writable root of its own for the build tool's cache, and is removed
whatever happened.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from studyforge.skills.exercises import Ran

LABEL = "com.local.scratch=claude-shape"


def _docker(*args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["docker", *args], capture_output=True, text=True, check=check, stdin=subprocess.DEVNULL
    )


class InContainer:
    """`runner(root, command)`: run `command` from a copy of `root` in `image`."""

    def __init__(self, image: str) -> None:
        self.image = image
        self.runs = 0

    def __call__(self, root: Path, command: tuple[str, ...]) -> Ran:
        self.runs += 1
        name = f"shape-gate-{uuid.uuid4().hex[:10]}"
        try:
            _docker(
                "create", "--name", name, "--label", LABEL, "--network", "none",
                "-e", "GRADLE_USER_HOME=/tmp/gradle-home", "-e", "PYTHONDONTWRITEBYTECODE=1",
                "-w", "/w", "--entrypoint", command[0],
                self.image, *command[1:], check=True,
            )
            _docker("cp", f"{root}/.", f"{name}:/w", check=True)
            done = subprocess.run(  # noqa: S603 - fixed argv, no shell
                ["docker", "start", "-a", name], capture_output=True, text=True, check=False,
                stdin=subprocess.DEVNULL,
            )
            with tempfile.TemporaryDirectory(dir=Path.cwd()) as back:
                if _docker("cp", f"{name}:/w/.", back).returncode == 0:
                    for produced in Path(back).rglob("target"):
                        shutil.copytree(
                            produced, root / produced.relative_to(back), dirs_exist_ok=True
                        )
            return Ran(done.returncode, done.stdout + done.stderr)
        finally:
            _docker("rm", "-f", name)
