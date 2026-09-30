"""Tag the serving base image for a registry namespace, and push it only when asked.

**What it does.** Plans the build exactly as `build.py` does, takes the tag that plan
computes, and names the image `<namespace>/studyforge-serve:<that tag>`. It then runs
the build, `docker tag`, and, with `--push`, `docker push`. ⭐ The tag is never written
by hand: it is the plan's, so the name a registry holds says which inputs built it.

**How you use it.** From the repository root, with the namespace in the environment and
a login already done by you (this script never logs in):

    export STUDYFORGE_NAMESPACE=<your registry namespace>
    python3 docker/serve/publish.py --dry-run
    python3 docker/serve/publish.py            # build and tag locally
    python3 docker/serve/publish.py --push     # and push

`--dry-run` prints the exact commands and runs none of them, so it needs no Docker.

⛔ **The namespace comes from `STUDYFORGE_NAMESPACE` and from nowhere else**: no flag,
no default, no literal in this repository. With it unset or empty the script refuses
before it plans anything. ⭐ A consumer pins the pushed image by DIGEST (`docker push`
prints it), because a digest names one image for good; a course's site build starts
`FROM` that reference.

**Depends on.** The standard library, `build.py` beside it, and a Docker CLI when it is
not a dry run.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402

#: The one place the namespace is read from.
NAMESPACE_VARIABLE = "STUDYFORGE_NAMESPACE"

#: What a registry namespace may look like: lower-case path parts, with an optional host and port first.
NAMESPACE = re.compile(r"^[a-z0-9]+(?:[._:-][a-z0-9]+)*(?:/[a-z0-9]+(?:[._-][a-z0-9]+)*)*$")


class Refused(ValueError):
    """A publish that will not start, and why."""


def namespace(env) -> str:
    """The registry namespace from the environment, or `Refused`."""
    value = (env.get(NAMESPACE_VARIABLE) or "").strip()
    if not value:
        raise Refused(f"{NAMESPACE_VARIABLE} is not set; export it (login is yours, outside this script)")
    if not NAMESPACE.match(value):
        raise Refused(f"{NAMESPACE_VARIABLE} is not a registry namespace: lower-case letters, digits and . _ - /")
    return value


def commands(local: str, remote: str, platform: str | None, push: bool) -> list[list[str]]:
    """The build, the tag, and, when asked, the push."""
    script = ["python3", "docker/serve/build.py"] + (["--platform", platform] if platform else [])
    steps = [script, ["docker", "tag", local, remote]]
    return steps + ([["docker", "push", remote]] if push else [])


def main(argv: list[str], env=None, run=subprocess.run, out=sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--platform", default=None)
    parser.add_argument("--push", action="store_true", help="push the tag; without it nothing leaves this host")
    parser.add_argument("--dry-run", action="store_true", help="print the commands and run none of them")
    args = parser.parse_args(argv)
    try:
        space = namespace(os.environ if env is None else env)
        local = build.planned().tag
    except (Refused, build.Refused) as refusal:
        print(f"refused: {refusal}", file=sys.stderr)
        return 2
    remote = f"{space}/{local}"
    for step in commands(local, remote, args.platform, args.push):
        print(shlex.join(step), file=out)
        if not args.dry_run:
            completed = run(step, stdin=subprocess.DEVNULL)
            if completed.returncode != 0:
                return completed.returncode
    print("consumers pin by the DIGEST `docker push` prints, never by the tag", file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
