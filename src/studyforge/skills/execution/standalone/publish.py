"""The publishing hand-off: commands the owner runs, printed here and never run here.

⭐ Nothing in this module starts a process. It reads `.studyforge/release.json` and prints
the lines of the owner's command list, so the list is testable without a daemon.

- **Identity.** The learner tree is committed as one fresh commit by a placeholder author
  set on the command (`git -c user.name=... -c user.email=...`), never the machine's git
  identity (`commit_argv`, `fresh_tree_commands`).
- **Namespace.** Every docker line sets `STUDYFORGE_NAMESPACE` explicitly. ⚠️ A value
  inherited from the shell would otherwise reach registry lookups and tags.
- **Scan before push.** Each built image's filesystem is exported to a folder and swept
  with the shared personal-data pattern set (`python -m studyforge.archive.scrub check`).
- **Digest after push.** Each pushed base's manifest digest must equal the digest the course
  images pin (`release.json` `bases`); a mismatch stops the list.

    python -m studyforge.skills.execution.standalone.publish RELEASE_JSON NAMESPACE WORKDIR
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from collections.abc import Mapping, Sequence

from studyforge.skills.execution.standalone.images import NAMESPACE_VARIABLE

#: The placeholder author of the learner tree's single commit.
AUTHOR_NAME = "Example"
AUTHOR_EMAIL = "noreply@example.invalid"

DOCKER = ("docker", "--context", "desktop-linux")
_INTERPOLATION = re.compile(r"^\$\{[A-Z_]+:-[^}]*\}/")


def commit_argv(message: str) -> list[str]:
    """Return the `git commit` argv with the placeholder author set on the command."""
    return [
        "git",
        "-c",
        f"user.name={AUTHOR_NAME}",
        "-c",
        f"user.email={AUTHOR_EMAIL}",
        "commit",
        "-q",
        "-m",
        message,
    ]


def fresh_tree_commands(branch: str, message: str) -> list[list[str]]:
    """The argvs that make a learner tree one fresh commit, run inside the exported folder."""
    return [
        ["git", "init", "-q", "-b", branch],
        ["git", "add", "-A"],
        commit_argv(message),
    ]


def images_of(release: Mapping[str, object]) -> list[str]:
    """Every image `release.json` lists, as `repository:tag` without any namespace."""
    listed = release.get("images")
    if not isinstance(listed, Mapping) or not listed:
        raise ValueError("release.json lists no images")
    return sorted({_INTERPOLATION.sub("", str(one)) for one in listed.values()})


def pinned_digests(release: Mapping[str, object]) -> dict[str, str]:
    """`repository:tag` to the digest the course images pin, for each published base."""
    found: dict[str, str] = {}
    bases = release.get("bases") or {}
    assert isinstance(bases, Mapping)
    for kind, one in bases.items():
        group = one.items() if kind == "profile" and isinstance(one, Mapping) else [(kind, one)]
        for _name, entry in group:
            if isinstance(entry, Mapping) and entry.get("digest"):
                found[f"{entry['image']}:{entry['tag']}"] = str(entry["digest"])
    return found


def _env(namespace: str) -> str:
    return f"{NAMESPACE_VARIABLE}={shlex.quote(namespace)}"


def build_command(namespace: str) -> str:
    return f"{_env(namespace)} {shlex.join([*DOCKER, 'compose', 'build'])}"


def scan_commands(image: str, namespace: str, workdir: str) -> list[str]:
    """Lines that export `image`'s filesystem under `workdir` and sweep it; stop on a finding."""
    name = "scan-" + re.sub(r"[^a-z0-9]+", "-", image.lower()).strip("-")
    where = f"{workdir}/{name}"
    ref = f"{namespace}/{image}"
    docker = shlex.join(DOCKER)
    return [
        f"mkdir -p {shlex.quote(where)}",
        f"{docker} create --name {name} {shlex.quote(ref)} >/dev/null",
        f"{docker} export {name} | tar -x -C {shlex.quote(where)} --exclude='dev/*'",
        f"{docker} rm {name} >/dev/null",
        f"python -m studyforge.archive.scrub check {shlex.quote(where)}"
        f" || {{ echo 'personal data in {image}: stop'; exit 1; }}",
        f"rm -rf {shlex.quote(where)}",
    ]


def digest_matches(expected: str, printed: str) -> bool:
    """True when `printed` (a registry's answer) is exactly the digest the course pins."""
    return printed.strip() == expected.strip() and expected.startswith("sha256:")


def digest_commands(namespace: str, pinned: Mapping[str, str]) -> list[str]:
    """Lines that compare each pushed manifest digest to the pinned one and stop on a mismatch."""
    docker = shlex.join([*DOCKER, "buildx", "imagetools", "inspect"])
    return [
        f'test "$({docker} {shlex.quote(f"{namespace}/{image}")}'
        f" --format '{{{{.Manifest.Digest}}}}')\" = {shlex.quote(digest)}"
        f" || {{ echo 'digest mismatch for {image}: stop'; exit 1; }}"
        for image, digest in sorted(pinned.items())
    ]


def owner_commands(release: Mapping[str, object], namespace: str, workdir: str) -> list[str]:
    """The owner's whole list, in order: build, scan every image, push, verify every digest."""
    images = images_of(release)
    lines = ["set -e", build_command(namespace)]
    for image in images:
        lines += scan_commands(image, namespace, workdir)
    docker = shlex.join(DOCKER)
    lines += [f"{docker} push {shlex.quote(f'{namespace}/{image}')}" for image in images]
    lines += digest_commands(namespace, pinned_digests(release))
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 3:
        print("usage: publish RELEASE_JSON NAMESPACE WORKDIR", file=sys.stderr)
        return 2
    with open(args[0], encoding="utf-8") as handle:
        release = json.load(handle)
    for line in owner_commands(release, args[1], args[2]):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
