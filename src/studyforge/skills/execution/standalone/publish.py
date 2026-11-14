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
- **Push the course's images only.** The site (once per edition), the runner and the editor
  are pushed; ⛔ a base (`serve`, `runner_base`, `editor_base` in `release.json` `images`) is
  never pushed: it is published already, and docker refuses to push a reference that carries
  a digest, which a thin export's base does.
- **Scan before push.** Each course image is saved (`docker save`) and the layers it adds on
  top of its base are written to a folder (`standalone.layerscan`) and swept with the shared
  personal-data pattern set (`python -m studyforge.archive.scrub check`). ⛔ The base's own
  layers are the toolchain's responsibility and are not swept here.
- **Clean up.** The folder is made writable (`chmod -R u+w`) before `rm -rf`, so the list,
  which runs under `set -e`, never stops on a file it cannot delete.
- **Digest after push.** Each published base's manifest digest must equal the digest the
  course images pin (`release.json` `bases`); a mismatch stops the list.

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

#: The course's own images in `release.json` `images`, each with the key of the base it starts
#: from (`images.Names`). ⭐ Every other key there is a base, which is never pushed.
COURSE_BASES = {"site": "serve", "runner": "runner_base", "editor": "editor_base"}


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


def _concrete(release: Mapping[str, object], listed: str) -> list[str]:
    """`listed` without its namespace, one name per edition where it names the narration."""
    name = _INTERPOLATION.sub("", listed)
    found = []
    for edition in editions(release) if _NARRATION.search(name) else ("",):
        concrete = _NARRATION.sub(edition, name)
        if "$" in concrete:
            raise ValueError(f"an image name keeps an interpolation: {listed}")
        found.append(concrete)
    return found


def bases_of(release: Mapping[str, object]) -> dict[str, str | None]:
    """Each course image, `repository:tag`, to the base it starts from, or `None` if unnamed.

    ⭐ The site's narration interpolation becomes one concrete tag per edition; ⛔ any
    other interpolation left in a name is refused, never printed. A base keeps the digest
    the record pins it by.
    """
    listed = release.get("images")
    if not isinstance(listed, Mapping) or not listed:
        raise ValueError("release.json lists no images")
    found: dict[str, str | None] = {}
    for key, base_key in COURSE_BASES.items():
        if key not in listed:
            continue
        base = _concrete(release, str(listed[base_key]))[0] if base_key in listed else None
        for one in _concrete(release, str(listed[key])):
            found[one] = base
    if not found:
        raise ValueError("release.json lists no course image: no site, runner or editor")
    return dict(sorted(found.items()))


def images_of(release: Mapping[str, object]) -> list[str]:
    """The course's own images `release.json` lists, as `repository:tag` without any namespace.

    ⛔ Never a base: those are published already and verified by `digest_commands`.
    """
    return list(bases_of(release))


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
    image: str, base: str | None, namespace: str, workdir: str, context: str | None = None
) -> list[str]:
    """Lines that sweep what `image` adds to `base` under `workdir`; stop on a finding.

    ⭐ The base's layer list is read from the local image (a build pulled it); with no base
    named, the list is empty and every layer is swept. The folder is made writable before it
    is removed.
    """
    name = "scan-" + re.sub(r"[^a-z0-9]+", "-", image.lower()).strip("-")
    where = shlex.quote(f"{workdir}/{name}")
    run = shlex.join(docker(context))
    layers = f"{where}/base-layers.json"
    listed = (
        f"{run} image inspect --format '{{{{json .RootFS.Layers}}}}'"
        f" {shlex.quote(f'{namespace}/{base}')} > {layers}"
        if base
        else f"echo '[]' > {layers}"
    )
    return [
        f"mkdir -p {where}",
        listed,
        f"{run} save -o {where}/image.tar {shlex.quote(f'{namespace}/{image}')}",
        f"python -m studyforge.skills.execution.standalone.layerscan"
        f" {where}/image.tar {layers} {where}/added",
        f"python -m studyforge.archive.scrub check {where}/added"
        f" || {{ echo 'personal data in {image}: stop'; exit 1; }}",
        f"chmod -R u+w {where}",
        f"rm -rf {where}",
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
    """The owner's whole list, in order: build each edition, scan and push each course image,
    verify each base."""
    bases = bases_of(release)
    images = list(bases)
    lines = ["set -e"]
    lines += [build_command(namespace, edition, context) for edition in editions(release)]
    for image, base in bases.items():
        lines += scan_commands(image, base, namespace, workdir, context)
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
