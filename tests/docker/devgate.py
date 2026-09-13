"""The gate the image-starting checks pass, and the ground its skip states (`W162`).

⛔ **The defect.** The gate refused all of them with one sentence, *"the build needs
network; a test run must not"*, whatever the image cache held. ⭐ That is true of a COLD
cache and false of a WARM one: with the image the build inputs name already present,
`check`'s `--build` runs every step from cache (Ruling 333 moved the cost from the MODE
to the TEST). So the reason now names the cache this run found.

⭐ **"Present" is read off `check`'s OWN identity, never a retyped tag.** `probe` runs
`docker/dev/check` verbatim up to the line that prints the image, the same derivation and
the same print, and asks the daemon for that name. ⛔ Nothing above that line builds
(`test_dev_gate.py` asserts it), and the pinned base is inspected FIRST, because the
derivation's `docker run` would pull an absent one.

⛔ **Still OFF by default.** Unset, every cache state skips, and a warm reason names
`INVOCATION`, the environment that reaches the checks, instead of running them. ⚠️ A check
that builds a FRESH image (`builds_fresh=True`) needs the network on any cache and says so.
A default HOST run pays one `--network none` container start per session to tell cold from
warm; inside the image the recursion guard answers first and nothing starts.
"""

from __future__ import annotations

import functools
import os
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

import pytest

from tests.docker.devfiles import DEV
from tests.support import repository_root, run, tool_on_path

#: Set to "1" to run the checks that start `check`. Off by default: see above.
OPT_IN = "STUDYFORGE_DOCKER_TESTS"

#: Set inside the image by the Dockerfile. Its only job is to stop those checks recursing.
MARKER = "STUDYFORGE_DEV_CONTAINER"

#: The start of the line `check` prints its image with; the probe runs `check` through it.
ANNOUNCEMENT = 'echo "docker/dev/check: image '

#: What `check` prints on stderr before it runs anything: the image, by its inputs (`W225`).
ANNOUNCED = re.compile(r"^docker/dev/check: image (\S+:inputs-[0-9a-f]{64})$", re.MULTILINE)

#: ⭐ The environment that reaches the gated checks, named once.
INVOCATION = (
    f"{OPT_IN}=1 python3 -m pytest tests/docker/ on the HOST, with a docker daemon and "
    f"Compose, never through docker/dev/check, whose recursion guard skips them"
)

WARM, COLD, UNKNOWN = "warm", "cold", "unknown"


@dataclass(frozen=True)
class Cache:
    """What the image cache holds for one checkout's build inputs, and why that is known."""

    state: str
    image: str | None
    why: str


def announced_images(stderr: str) -> list[str]:
    """Every image name a `check` run printed, in the order printed."""
    return ANNOUNCED.findall(stderr)


def announced_image(stderr: str) -> str:
    """The one image a `check` run printed; fails unless there is exactly one."""
    found = set(announced_images(stderr))
    assert len(found) == 1, f"check printed {len(found)} image name(s), not one: {sorted(found)}"
    return found.pop()


def base_image(dockerfile: str) -> str | None:
    """The image after the one `FROM`, read as `check`'s own loop reads it, or None."""
    found = [
        line.split()[1]
        for line in dockerfile.splitlines()
        if line.startswith("FROM ") and len(line.split()) > 1
    ]
    return found[0] if len(found) == 1 else None


def announcement_prefix(script: str) -> str | None:
    """`check`'s text through the line that prints its image, or None unless there is one."""
    lines = script.splitlines(keepends=True)
    cuts = [index for index, line in enumerate(lines) if line.startswith(ANNOUNCEMENT)]
    return "".join(lines[: cuts[0] + 1]) if len(cuts) == 1 else None


def inspect(docker: str, image: str, cwd: Path) -> str:
    """WARM if the daemon holds `image`, COLD if it says it does not, else UNKNOWN."""
    result = run([docker, "image", "inspect", "--format", "{{.Id}}", image], cwd=cwd)
    if result.returncode == 0:
        return WARM
    return COLD if "no such image" in result.stderr.lower() else UNKNOWN


def probe(root: Path, docker: str) -> Cache:
    """Whether `root`'s build inputs name a present image, read building and pulling nothing."""
    base = base_image((root / DEV / "Dockerfile").read_text("utf-8"))
    prefix = announcement_prefix((root / DEV / "check").read_text("utf-8"))
    if base is None or prefix is None:
        return Cache(UNKNOWN, None, f"{DEV}/ names no single base or prints no image")
    held = inspect(docker, base, root)
    if held != WARM:
        why = "the pinned base is not present, so a build would pull it"
        return Cache(held, None, why if held == COLD else "the docker daemon did not answer")
    derived = run(["sh", "-c", prefix, str(root / DEV / "check")], cwd=root)
    images = announced_images(derived.stderr)
    if derived.returncode != 0 or len(images) != 1:
        return Cache(UNKNOWN, None, "check's own derivation printed no image")
    image = images[0]
    held = inspect(docker, image, root)
    whys = {
        WARM: f"{image}, the image these build inputs name, is present",
        COLD: f"{image}, the image these build inputs name, is not present, so a run builds it",
        UNKNOWN: "the docker daemon did not answer",
    }
    return Cache(held, image, whys[held])


def skip_reason(
    environ: Mapping[str, str],
    docker: str | None,
    cache: Callable[[], Cache],
    *,
    builds_fresh: bool,
) -> str | None:
    """Why a check that starts `check` must not run here, or None when it may."""
    if environ.get(MARKER) == "1":
        return "already inside the dev image; building it again would recurse"
    if docker is None:
        return "docker is not installed"
    if environ.get(OPT_IN) == "1":
        return None
    if builds_fresh:
        return (
            f"{OPT_IN} is unset. This check builds a FRESH image whatever the cache holds, "
            f"and a build needs network; a test run must not"
        )
    found = cache()
    if found.state == WARM:
        return (
            f"{OPT_IN} is unset. The image cache is WARM: {found.why}, so this check builds "
            f"from cache and pulls nothing. It is reached by {INVOCATION}"
        )
    if found.state == COLD:
        return (
            f"{OPT_IN} is unset. The image cache is COLD: {found.why}, and a build needs "
            f"network; a test run must not"
        )
    return f"{OPT_IN} is unset, and the image cache could not be read: {found.why}"


@functools.cache
def this_checkout(docker: str) -> Cache:
    """`probe` of this checkout, read once per session."""
    return probe(repository_root(), docker)


def require_docker_run(*, builds_fresh: bool = False) -> str:
    """Skip unless this run may start containers through `check`; return the docker client."""
    docker = tool_on_path("docker")
    reason = skip_reason(
        os.environ, docker, lambda: this_checkout(docker or ""), builds_fresh=builds_fresh
    )
    if reason is not None:
        pytest.skip(reason)
    assert docker is not None
    return docker
