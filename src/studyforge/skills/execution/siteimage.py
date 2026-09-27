r"""The study server's image, staged from the INSTALLED library at the corpus's pin.

**What it does.** Checks that the library this Python imports is the one the
corpus pinned — its version and the commit it was built from — copies that
library beside a generated build file, names the image by a digest of
exactly those bytes, and records the name where the corpus's one compose
command reads it (`SITE_ENV`), with the profile that brings the site up.

**How you use it.** After `onboard.write`:

    staged = stage_site(root)                    # Staged(tag, argv, written)
    subprocess.run(staged.argv, cwd=root)        # the caller runs the build

and then the corpus's one compose command, as `EXECUTION.md` prints it, brings
up the site with the editor and the runner.

**Depends on.** `onboarding.library` for the installed version, commit and the
corpus's pin, `written` for the hand-edit record, and `hashlib`.
⛔ No process: the build's argv is returned, and the caller runs it, as
`record` hands its caller the tag's argv (spec §8.3's structural assertion
over this package).

## ⛔ THE LIBRARY THE CORPUS PINNED, OR NO IMAGE

⭐ **An image built from a library the corpus did not pin serves pages built by
another version**, so a version or a commit that differs from `pin.json` is
refused by name, and a source tree — which carries no commit — is refused too:
install the wheel built from the pinned commit, and stage again.

## ⭐ THE TAG IS A FUNCTION OF THE BYTES, AND THE PULL IS PINNED

⭐ **`studyforge-site:<version>-<digest>`**, the digest over the build file
and every copied file by path, so the same library stages the same tag
(R10), and a moved byte moves it. ⭐ The base image is pulled by digest
(`BASE`), never by a moving tag. ⛔ The copy is ignored by the corpus's
repository (`IGNORE`); the build file and `SITE_ENV` are the record.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from studyforge.skills.execution import written
from studyforge.skills.execution.binds import ExecutionRefused
from studyforge.skills.execution.onboard import DIRECTORY, GENERATED, SITE_ENV
from studyforge.skills.execution.siteservice import BUILD_CONTEXT, BUILD_FILE, GATED, IMAGE, SERVICE
from studyforge.skills.onboarding import library

#: Where the image's build context is staged, under the skill's own directory.
SITE_DIR = f"{DIRECTORY}/{BUILD_CONTEXT}"

#: The copy of the installed library inside that context.
LIBRARY = "library"

#: The ignore file that keeps the copied library out of the repository.
IGNORE = f"/{LIBRARY}/\n"

#: ⛔ The base image, pinned by digest: the dev image's own `FROM`.
BASE = "python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6"

#: The image's repository; its tag is the version and the digest.
REPOSITORY = "studyforge-site"

#: The profile the site service is in, which `SITE_ENV` turns on once recorded.
PROFILE = SERVICE

#: What is never copied: bytecode the running Python left.
SKIPPED = ("__pycache__",)
SKIPPED_SUFFIXES = (".pyc",)


@dataclass(frozen=True, slots=True)
class Staged:
    """What staging answered: the tag, the build's argv, and the files it recorded."""

    tag: str
    argv: tuple[str, ...]
    written: tuple[str, ...]


def build_file() -> str:
    """Return the site image's build file: the pinned base, the library, and `serve`."""
    return "".join(
        [
            f"# {GENERATED}\n",
            f"FROM {BASE}\n",
            f"COPY {LIBRARY}/ /opt/studyforge/{LIBRARY}/\n",
            f"ENV PYTHONPATH=/opt/studyforge/{LIBRARY} PYTHONDONTWRITEBYTECODE=1 "
            "PYTHONUNBUFFERED=1\n",
            'ENTRYPOINT ["python3", "-m", "studyforge.cli"]\n',
        ]
    )


def stage_site(root: Path, *, package: Path = library.PACKAGE) -> Staged:
    """Stage the image from the library at `package`, record its tag, and return the build."""
    root = Path(root)
    version, commit = _pinned_library(root, package)
    context = root / SITE_DIR
    copied(package, context / LIBRARY / package.name)
    (context / BUILD_FILE).write_text(build_file(), encoding="utf-8", newline="\n")
    (context / ".gitignore").write_text(IGNORE, encoding="utf-8", newline="\n")
    tag = f"{REPOSITORY}:{version}-{digest(context)[:12]}"
    (root / SITE_ENV).write_text(site_env(tag, commit), encoding="utf-8", newline="\n")
    recorded = (f"{SITE_DIR}/{BUILD_FILE}", f"{SITE_DIR}/.gitignore", SITE_ENV)
    written.stamp(root, recorded)
    argv = ("docker", "build", "--file", f"{SITE_DIR}/{BUILD_FILE}", "--tag", tag, SITE_DIR)
    return Staged(tag=tag, argv=argv, written=recorded)


def copied(package: Path, target: Path) -> int:
    """Copy the library at `package` to `target`, whole and nothing else; return the count.

    ⭐ A file the copy holds that the library does not is removed first, so the
    digest is of this library and no earlier one.
    """
    wanted = {
        path.relative_to(package): path
        for path in package.rglob("*")
        if path.is_file()
        and not any(part in SKIPPED for part in path.relative_to(package).parts)
        and path.suffix not in SKIPPED_SUFFIXES
    }
    for stale in sorted(target.rglob("*"), reverse=True) if target.exists() else []:
        if stale.is_file() and stale.relative_to(target) not in wanted:
            stale.unlink()
        elif stale.is_dir() and not any(stale.iterdir()):
            stale.rmdir()
    for relative, path in wanted.items():
        (target / relative).parent.mkdir(parents=True, exist_ok=True)
        (target / relative).write_bytes(path.read_bytes())
    return len(wanted)


def site_env(tag: str, commit: str) -> str:
    """Return `SITE_ENV`'s bytes: the image, the profile that brings the site up, the gate."""
    return (
        f"# {GENERATED}\n"
        f"# The study server's image, staged from the library built from {commit}.\n"
        f"{IMAGE}={tag}\n"
        f"COMPOSE_PROFILES={PROFILE}\n"
        f"{GATED}=true\n"
    )


def digest(context: Path) -> str:
    """Return the sha256 over every file under `context` but its ignore file, by path."""
    hashed = hashlib.sha256()
    for path in sorted(p for p in context.rglob("*") if p.is_file() and p.name != ".gitignore"):
        hashed.update(path.relative_to(context).as_posix().encode("utf-8") + b"\x00")
        hashed.update(hashlib.sha256(path.read_bytes()).digest())
    return hashed.hexdigest()


def _pinned_library(root: Path, package: Path) -> tuple[str, str]:
    """Return the library's version and commit when both are the corpus's pin, else refuse."""
    try:
        pin = library.pinned(root)
        version, commit = library.version(package), library.commit(package)
    except library.LibraryRefused as refusal:
        raise ExecutionRefused(str(refusal)) from None
    if commit is None:
        raise ExecutionRefused(
            "the library this Python imports is a source tree, which carries no commit; "
            "install the wheel built from the corpus's pinned commit and stage again"
        )
    if (version, commit) != (pin["version"], pin["commit"]):
        raise ExecutionRefused(
            "the library this Python imports is not the one the corpus pinned (its version or "
            "its commit differs); install the pinned one, or re-pin, and stage again"
        )
    return version, commit
