"""The real runner container `execute`'s acceptance runs against — started as the READER starts it.

⭐ **Opt-in, by naming the image:** `STUDYFORGE_RUNNER_IMAGE=<tag>`, the tag
`code-server-toolchain`'s `docker/minimal/build.py --runtimes python` built. ⛔
Absent, or with no Docker reachable, every container-mode case SKIPS and says
which — the pinned dev image carries no Docker, so its suite reads host mode
only, and the real-container reading is taken on a host that has one.

⭐ **The container is started with the run line `code-server-toolchain`'s README
documents**, read from the sibling at run time and its placeholders filled —
never a line typed here — so the runner is proved against the container a
reader actually has: source root alone at `/work`, `--network none`, `--init`,
the reader's uid:gid, no port, no socket. ⛔ The runner itself starts nothing;
this is the test standing in for the reader.

⛔ **Every invocation that reaches this module must hold the shared container
lock** (the office rules): it is taken around the pytest run, not in here, so
one gate is one lock.
"""

from __future__ import annotations

import os
import shlex
import subprocess
import uuid
from pathlib import Path

from tests.support import repository_root, tool_on_path

IMAGE_VARIABLE = "STUDYFORGE_RUNNER_IMAGE"
SIBLING = "code-server-toolchain"


def image() -> str | None:
    """The runner image this run was asked to use, or `None`."""
    return os.environ.get(IMAGE_VARIABLE) or None


def skip_reason() -> str | None:
    """Why the container cases cannot run here, or `None` when they can."""
    if image() is None:
        return f"no runner image named: set {IMAGE_VARIABLE} to a tag built by {SIBLING}"
    if tool_on_path("docker") is None:
        return "no docker CLI in this environment (the pinned dev image carries none)"
    if _docker("image", "inspect", image()).returncode != 0:
        return f"{IMAGE_VARIABLE} names an image this daemon does not hold"
    if run_line() is None:
        return f"the sibling {SIBLING}'s README, with its documented run line, is not reachable"
    return None


def run_line() -> str | None:
    """The README's `docker run` line, continuations joined, or `None`."""
    readme = _workspace() / SIBLING / "README.md"
    if not readme.is_file():
        return None
    joined, current = [], ""
    for line in readme.read_text(encoding="utf-8").splitlines():
        if line.rstrip().endswith("\\"):
            current += line.rstrip()[:-1] + " "
            continue
        joined.append(current + line)
        current = ""
    return next((line.strip() for line in joined if line.lstrip().startswith("docker run")), None)


def start(source_root: Path) -> str:
    """Start the runner container over `source_root` as the reader would; its name."""
    name = f"sf20-{uuid.uuid4().hex[:10]}"
    line = (
        run_line()
        .replace("studyforge-runner-<source>", name)
        .replace('"$(id -u):$(id -g)"', f"{os.getuid()}:{os.getgid()}")
        .replace("<source root>", str(source_root))
        .replace("<tag>", image())
    )
    started = subprocess.run(
        shlex.split(line), stdin=subprocess.DEVNULL, capture_output=True, text=True
    )
    if started.returncode != 0:
        remove(name)
        raise RuntimeError(f"the documented run line did not start: exit {started.returncode}")
    return name


def remove(name: str) -> None:
    """Remove the container this module started. ⛔ Leave none behind."""
    _docker("rm", "-f", name)


def settings(name: str) -> str:
    """Its network mode, published ports and mounts, as `docker inspect` reports them."""
    return _docker(
        "inspect",
        "--format",
        "{{.HostConfig.NetworkMode}} {{json .HostConfig.PortBindings}} {{json .Mounts}}",
        name,
    ).stdout


def alive_in(name: str):
    """A predicate: is process `pid` alive, and not a zombie, inside container `name`?"""

    def alive(pid: int) -> bool:
        probe = _docker(
            "exec",
            name,
            "sh",
            "-c",
            'grep -q "^State:[[:space:]]*[^Z]" "/proc/$1/status"',
            "sh",
            str(pid),
        )
        return probe.returncode == 0

    return alive


def _docker(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *arguments],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )


def _workspace() -> Path:
    """Where the siblings are: the parent of the MAIN checkout, from any worktree."""
    from tools.workspace.__main__ import workspace_root

    return workspace_root(repository_root())
