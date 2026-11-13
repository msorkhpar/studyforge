"""The publishing hand-off: commands the owner runs, printed here and never run here.

⭐ Nothing in this module starts a process. It reads `.studyforge/release.json` and prints
the lines of the owner's command list, so the list is testable without a daemon.

- **Identity.** The learner tree is committed as one fresh commit by a placeholder author
  set on the command (`git -c user.name=... -c user.email=...`), never the machine's git
  identity (`commit_argv`, `fresh_tree_commands`).
- **Namespace.** Every docker line sets `STUDYFORGE_NAMESPACE` explicitly. ⚠️ A value
  inherited from the shell would otherwise reach registry lookups and tags.
- **Editions.** ⭐ Every image is named by a concrete tag, never a compose interpolation:
  the site once per edition the corpus has, `without-narration` always and
  `with-narration` only when the tree keeps the clips' checksums (`images.CLIPS`). Each
  build sets `COURSE_NARRATION` on the command, which picks the site's build target and
  its tag in `compose.yaml`.
- **Context.** No docker line names a context unless the owner names one
  (`--context NAME`); otherwise docker uses `DOCKER_CONTEXT` or the current context.
- **Scan before push.** Each built image's filesystem is exported to a folder and swept
  with the shared personal-data pattern set (`python -m studyforge.archive.scrub check`).
- **Digest after push.** Each pushed base's manifest digest must equal the digest the course
  images pin (`release.json` `bases`); a mismatch stops the list.

    python -m studyforge.skills.execution.standalone.publish [--context NAME] \
        RELEASE_JSON NAMESPACE WORKDIR
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from collections.abc import Mapping, Sequence

from studyforge.skills.execution.standalone.images import (
    CLIPS,
    NAMESPACE_VARIABLE,
    NARRATION_VARIABLE,
    NARRATIONS,
)

#: The placeholder author of the learner tree's single commit.
AUTHOR_NAME = "Example"
AUTHOR_EMAIL = "noreply@example.invalid"

USAGE = "usage: publish [--context NAME] RELEASE_JSON NAMESPACE WORKDIR"

_INTERPOLATION = re.compile(r"^\$\{[A-Z_]+:-[^}]*\}/")
_NARRATION = re.compile(r"\$\{" + NARRATION_VARIABLE + r":-[^}]*\}")


def docker(context: str | None = None) -> list[str]:
    """The docker argv prefix: the named context, or none so docker uses the current one."""
    return ["docker", "--context", context] if context else ["docker"]


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


def editions(release: Mapping[str, object]) -> tuple[str, ...]:
    """The site's editions: without narration always, with it when the tree keeps the clips."""
    keeps = release.get("keeps") or ()
    return NARRATIONS if CLIPS in keeps else NARRATIONS[:1]


def images_of(release: Mapping[str, object]) -> list[str]:
    """Every image `release.json` lists, as `repository:tag` without any namespace.

    ⭐ The site's narration interpolation becomes one concrete tag per edition; ⛔ any
    other interpolation left in a name is refused, never printed.
    """
    listed = release.get("images")
    if not isinstance(listed, Mapping) or not listed:
        raise ValueError("release.json lists no images")
    found: set[str] = set()
    for one in listed.values():
        name = _INTERPOLATION.sub("", str(one))
        for edition in editions(release) if _NARRATION.search(name) else ("",):
            concrete = _NARRATION.sub(edition, name)
            if "$" in concrete:
                raise ValueError(f"an image name keeps an interpolation: {one}")
            found.add(concrete)
    return sorted(found)


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


def build_command(namespace: str, edition: str = NARRATIONS[0], context: str | None = None) -> str:
    """The build of one edition: every image for the first, the site alone for the voiced one."""
    services = [] if edition == NARRATIONS[0] else ["site"]
    argv = [*docker(context), "compose", "build", *services]
    return f"{_env(namespace)} {NARRATION_VARIABLE}={shlex.quote(edition)} {shlex.join(argv)}"


def scan_commands(
    image: str, namespace: str, workdir: str, context: str | None = None
) -> list[str]:
    """Lines that export `image`'s filesystem under `workdir` and sweep it; stop on a finding."""
    name = "scan-" + re.sub(r"[^a-z0-9]+", "-", image.lower()).strip("-")
    where = f"{workdir}/{name}"
    ref = f"{namespace}/{image}"
    run = shlex.join(docker(context))
    return [
        f"mkdir -p {shlex.quote(where)}",
        f"{run} create --name {name} {shlex.quote(ref)} >/dev/null",
        f"{run} export {name} | tar -x -C {shlex.quote(where)} --exclude='dev/*'",
        f"{run} rm {name} >/dev/null",
        f"python -m studyforge.archive.scrub check {shlex.quote(where)}"
        f" || {{ echo 'personal data in {image}: stop'; exit 1; }}",
        f"rm -rf {shlex.quote(where)}",
    ]


def digest_matches(expected: str, printed: str) -> bool:
    """True when `printed` (a registry's answer) is exactly the digest the course pins."""
    return printed.strip() == expected.strip() and expected.startswith("sha256:")


def digest_commands(
    namespace: str, pinned: Mapping[str, str], context: str | None = None
) -> list[str]:
    """Lines that compare each pushed manifest digest to the pinned one and stop on a mismatch."""
    inspect = shlex.join([*docker(context), "buildx", "imagetools", "inspect"])
    return [
        f'test "$({inspect} {shlex.quote(f"{namespace}/{image}")}'
        f" --format '{{{{.Manifest.Digest}}}}')\" = {shlex.quote(digest)}"
        f" || {{ echo 'digest mismatch for {image}: stop'; exit 1; }}"
        for image, digest in sorted(pinned.items())
    ]


def owner_commands(
    release: Mapping[str, object], namespace: str, workdir: str, context: str | None = None
) -> list[str]:
    """The owner's whole list, in order: build each edition, scan every image, push, verify."""
    images = images_of(release)
    lines = ["set -e"]
    lines += [build_command(namespace, edition, context) for edition in editions(release)]
    for image in images:
        lines += scan_commands(image, namespace, workdir, context)
    run = shlex.join(docker(context))
    lines += [f"{run} push {shlex.quote(f'{namespace}/{image}')}" for image in images]
    lines += digest_commands(namespace, pinned_digests(release), context)
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    context = None
    if args[:1] == ["--context"]:
        if len(args) < 2 or not args[1] or args[1].startswith("-"):
            print(USAGE, file=sys.stderr)
            return 2
        context, args = args[1], args[2:]
    if len(args) != 3:
        print(USAGE, file=sys.stderr)
        return 2
    with open(args[0], encoding="utf-8") as handle:
        release = json.load(handle)
    for line in owner_commands(release, args[1], args[2], context):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
