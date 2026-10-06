"""Build the shared study server image from the library in this checkout.

**What it does.** Finds the part of `studyforge` that serves a course (the closure
of `cli.serve`, `standalone.closure`), stages it beside `Dockerfile`, computes the
image's tag from a digest of exactly those inputs, and runs `docker build`.
⭐ The tag is never written by hand: `studyforge-serve:<version>-<sha256>`, where the
sha256 is over the build file, the version and every staged file by path and content,
so the same inputs name the same image and a moved byte names a new one.

**How you use it.** From the repository root:

    python3 docker/serve/build.py --print-tag
    python3 docker/serve/build.py                  # build it, tagged locally
    python3 docker/serve/build.py --platform linux/amd64 --pull never

`--print-tag` builds nothing and needs no Docker. `--pull never` fetches no image:
the pinned Python must already be on this host.

**Depends on.** The standard library, `standalone/closure.py` (read by path, so no
import of the framework), and a Docker CLI with BuildKit for the build itself. It
mounts no socket and runs no container.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

#: The image's repository, unqualified: a registry namespace is the publisher's.
REPOSITORY = "studyforge-serve"

#: The build file, beside this script.
DOCKERFILE = "Dockerfile"

#: Where the framework's package sits, and the module that finds what serving needs.
SOURCE = Path("src")
CLOSURE = SOURCE / "studyforge" / "skills" / "execution" / "standalone" / "closure.py"


class Refused(ValueError):
    """A build that will not start, and why."""


@dataclass(frozen=True, slots=True)
class Plan:
    """What an image is built from, and the name that says so."""

    version: str
    digest: str
    files: tuple[str, ...]
    root: Path

    @property
    def tag(self) -> str:
        """Return the image tag: the version and the digest of the build's inputs."""
        return f"{REPOSITORY}:{self.version}-{self.digest}"


def _closure(root: Path):
    """Return the closure module, loaded from its file so the framework itself is not imported."""
    path = root / CLOSURE
    spec = importlib.util.spec_from_file_location("serve_closure", path)
    if spec is None or spec.loader is None or not path.is_file():
        raise Refused(f"{CLOSURE.as_posix()} is missing from this checkout")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def planned(root: Path = ROOT) -> Plan:
    """Return the build for this checkout, computed before any Docker is touched."""
    try:
        version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"][
            "version"
        ]
    except (OSError, KeyError, tomllib.TOMLDecodeError) as error:
        raise Refused(
            f"the framework's version cannot be read from pyproject.toml: {error}"
        ) from None
    closure = _closure(root)
    files = closure.vendored(root / SOURCE)
    digest = hashlib.sha256()
    for part in (version, (root / "docker" / "serve" / DOCKERFILE).read_text(encoding="utf-8")):
        digest.update(part.encode("utf-8") + b"\0")
    for one in files:
        digest.update(one.encode("utf-8") + b"\0" + (root / SOURCE / one).read_bytes() + b"\0")
    return Plan(version=version, digest=digest.hexdigest(), files=tuple(files), root=root)


def stage(plan: Plan, out: Path) -> None:
    """Write the build context: the build file and the library files, nothing else."""
    shutil.copyfile(plan.root / "docker" / "serve" / DOCKERFILE, out / DOCKERFILE)
    for one in plan.files:
        target = out / "library" / one
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(plan.root / SOURCE / one, target)


def argv(plan: Plan, context: Path, platform: str | None, pull: str) -> list[str]:
    """Return the `docker build` command for a staged context."""
    command = ["docker", "build", "--tag", plan.tag, "--build-arg", f"SERVE_VERSION={plan.version}"]
    command += ["--platform", platform] if platform else []
    command += ["--pull=false"] if pull == "never" else []
    return command + [str(context)]


def main(args_in: list[str], run=subprocess.run, out=sys.stdout) -> int:
    """Build the image, or only print its tag; return the exit status."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--print-tag", action="store_true", help="print the tag and build nothing")
    parser.add_argument("--platform", default=None)
    parser.add_argument("--pull", choices=("missing", "never"), default="missing")
    parser.add_argument("--root", default=str(ROOT), help="build another copy of this checkout")
    args = parser.parse_args(args_in)
    try:
        plan = planned(Path(args.root).resolve())
    except Refused as refusal:
        print(f"refused: {refusal}", file=sys.stderr)
        return 2
    if args.print_tag:
        print(plan.tag, file=out)
        return 0
    with tempfile.TemporaryDirectory(prefix="studyforge-serve-") as scratch:
        stage(plan, Path(scratch))
        completed = run(
            argv(plan, Path(scratch), args.platform, args.pull), stdin=subprocess.DEVNULL
        )
    if completed.returncode == 0:
        print(plan.tag, file=out)
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
