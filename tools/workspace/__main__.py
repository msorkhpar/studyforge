"""Command-line entry point for the pin file: `python3 -m tools.workspace`.

**What it does.** `verify` exits **0** when every recorded component is checked
out at the commit the pin file names **and nothing else**, and **1** naming the
component when it is not — a sibling whose working tree carries work that is on
no ref is exit **1** too, with the state named (`W402`). `record` rewrites the
commits from what is checked out now.

**How you use it.** `python3 -m tools.workspace verify` from the repository
root; `--workspace PATH` overrides where the siblings are looked for.

**Depends on.** `argparse` and `tools.workspace`.

## ⛔ The workspace root is computed, never recorded

⚠️ **The one place an absolute path would have been written into a file, and
the reason it is not.** The components are siblings of this repository, so the
workspace is this repository's parent — a fact about the disk at run time,
discovered like a program on `PATH` rather than recorded like `/usr/bin/mvn`.

⭐ **And a worktree is handled, because that is where the work happens.** A
`git worktree` lives outside the repository it belongs to, so its own parent is
the wrong answer; `git rev-parse --git-common-dir` names the main checkout's
`.git`, whose grandparent is the workspace. ⚠️ Falling back to the plain parent
keeps this working in a plain copy with no git at all.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from tools.workspace import PIN_FILENAME, PinError, git, record, render, verify

#: Set by `docker/dev/Dockerfile`. ⭐ Its presence means *"this run is the one
#: that certifies a result"* — the same marker the grammar tests read.
DEV_CONTAINER = "STUDYFORGE_DEV_CONTAINER"

#: Exit codes, and there are three because there are three answers.
VERIFIED = 0
DISAGREES = 1
#: ⛔ **Ruling 53's fourth state, as a number.** Not 0 and not 1: neither
#: *"the workspace is what it says"* nor *"it is not" —* this run could not
#: tell, and a check that cannot be authoritative where it is running says so
#: and refuses. ⚠️ A merely awkward check is still `did not run`.
NOT_AUTHORITATIVE = 2


def repository_root(start: Path) -> Path:
    """Return the repository `start` is inside, or `start` itself."""
    result = git(start, "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()) if result.returncode == 0 else Path(start)


def workspace_root(repository: Path) -> Path:
    """Return where the sibling components are: the parent of the **main** checkout."""
    result = git(repository, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if result.returncode == 0 and result.stdout.strip():
        common = Path(result.stdout.strip())
        if common.name == ".git" and common.parent.parent.is_dir():
            return common.parent.parent
    return repository.parent


def main(argv: list[str] | None = None) -> int:
    """Run a subcommand and return the process exit code."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.workspace",
        description=(
            "Verify that every component in workspace.json is checked out at the "
            "commit it records, or re-record those commits."
        ),
    )
    parser.add_argument("action", choices=("verify", "record"))
    parser.add_argument("--root", type=Path, default=Path("."), help="the repository root")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="where the sibling components are (default: computed from --root)",
    )
    arguments = parser.parse_args(argv)

    repository = repository_root(arguments.root)
    if arguments.workspace is None and os.environ.get(DEV_CONTAINER):
        # ⛔ **Refuse, rather than answer.** The pinned image mounts exactly one
        # directory (FND-03), so every sibling is absent in here — and reporting
        # them absent is a plausible, well-formed, *wrong* answer, which is the
        # failure this project keeps finding. ⭐ Mounting the workspace instead
        # would hand the build four sibling repositories: a wider trust boundary
        # bought for a convenience, which Ruling 53 refuses.
        print(
            "workspace: this is the pinned image, which mounts one directory, "
            "so the sibling components cannot be seen from in here. This check "
            "is host-verified: run it on the host, or pass --workspace to point "
            "at a tree that is visible.",
            file=sys.stderr,
        )
        return NOT_AUTHORITATIVE
    workspace = arguments.workspace or workspace_root(repository)

    try:
        if arguments.action == "record":
            (repository / PIN_FILENAME).write_text(
                render(record(workspace, repository)), encoding="utf-8"
            )
            print(f"recorded {PIN_FILENAME}")
            return VERIFIED
        findings = verify(workspace, repository)
    except PinError as error:
        print(f"workspace: {error}", file=sys.stderr)
        return DISAGREES

    for finding in findings:
        print(f"workspace: {finding}", file=sys.stderr)
    if findings:
        print(
            f"workspace: {len(findings)} component(s) disagree with {PIN_FILENAME}",
            file=sys.stderr,
        )
        return DISAGREES
    print("workspace: every recorded component is checked out at its pinned commit")
    return VERIFIED


if __name__ == "__main__":  # pragma: no cover - exercised as a process
    raise SystemExit(main())
