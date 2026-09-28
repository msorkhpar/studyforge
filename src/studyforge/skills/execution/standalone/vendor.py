r"""The toolchain's four builds, asked of its pinned checkout, with their context copied in.

**What it does.** Reads the toolchain's `consuming.json`, runs the command its
`builds.printed_by` names for each build a learner's course needs — the shared
unprimed `runner` and `editor`, and the course's two layers on them — checks
that the checkout computes the two tags the course recorded when its execution
was onboarded, and copies every input root those builds name into the
learner's tree, byte for byte.

**How you use it.**

    asked = ask(checkout, runtimes, prime, platform=..., run=run)   # Toolchain(...)
    pinned(course_root, checkout, runtimes, prime, platform=..., run=run)  # or refused
    copied = copy(checkout, target, asked.inputs)     # relative paths written

**Depends on.** `contract` for the one file this reads of the component, and
the caller's `run` (`split.Run`) to run the command that file names. ⛔ **It reads no Dockerfile
and no build script**: the builds arrive as data from the command the contract
names, and the context is copied as bytes, never parsed (R18).

## ⛔ The checkout the course was built with, or nothing

⭐ The course recorded the tags of its primed runner and editor
(`.studyforge/execution/runner.env`, `editor.env`), and a tag is a function
of the build's inputs. ⛔ **So a checkout whose primed tags differ is not the
one the course was built with**, and it is refused by name: vendoring it would
give a learner images the builder never ran.
"""

from __future__ import annotations

import json
import shutil
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from studyforge.archive.scrub import assert_clean, scrub
from studyforge.skills.execution.contract import (
    CONSUMING,
    EDITOR_API,
    EDITOR_COMPONENT,
    EDITOR_PROMISE,
    read,
    require,
)
from studyforge.skills.execution.onboard import EDITOR_ENV, RUNNER_ENV
from studyforge.skills.execution.standalone import split

#: The four builds a learner's course needs, in the order they are built.
BUILDS = ("runner", "editor", "runner-prime", "editor-prime")

#: ⛔ The shape of the document `builds.printed_by` prints that this module has read.
BUILDS_API = 1

#: The two slots `builds.printed_by` carries.
IMAGE_SLOT = "<runner|editor|runner-prime|editor-prime>"
SET_SLOT = "<the declared set>"

#: ⭐ What this skill keeps of a printed build: every key a learner's tree is written from.
#: ⛔ The rest (the checkout's and the prime's absolute paths among it) is dropped
#: unread, and what is kept passes the personal-data gate before it is used (R7).
KEPT = ("builds_api", "image", "tag", "dockerfile", "target", "args", "built_here", "inputs")

#: Files the interpreter writes beside an input, never copied.
SKIPPED = ("__pycache__",)


class VendorRefused(ValueError):
    """A toolchain this skill will not vendor for a course, and why."""


@dataclass(frozen=True, slots=True)
class Toolchain:
    """What the pinned toolchain said about the course's four builds."""

    commit: str
    builds: Mapping[str, Mapping[str, object]]
    inputs: tuple[str, ...]


Run = split.Run


def ask(
    checkout: Path,
    runtimes: Sequence[str],
    prime: Path,
    *,
    platform: str,
    run: Run,
) -> Toolchain:
    """Ask the toolchain at `checkout` for the four builds, as its contract says to ask."""
    checkout = Path(checkout)
    command = _printed_by(checkout)
    builds = {
        image: _asked(
            checkout, command, image, runtimes, prime if "prime" in image else None, platform, run
        )
        for image in BUILDS
    }
    inputs = sorted({str(one) for build in builds.values() for one in build["inputs"]})
    return Toolchain(commit=_commit(checkout, run), builds=builds, inputs=tuple(inputs))


def pinned(
    root: Path,
    checkout: Path,
    runtimes: Sequence[str],
    prime: Path,
    *,
    platform: str,
    run: Run,
) -> None:
    """Refuse unless `checkout` computes the primed tags the course at `root` recorded."""
    command = _printed_by(Path(checkout))
    for image, recorded in (("runner", RUNNER_ENV), ("editor", EDITOR_ENV)):
        want = _recorded(Path(root) / recorded)
        got = _asked(Path(checkout), command, image, runtimes, prime, platform, run)["tag"]
        if want != got:
            raise VendorRefused(
                f"the toolchain checkout computes {scrub(str(got))} for the course's primed "
                f"{image}, and the course recorded {scrub(str(want))}: check out the toolchain "
                "commit the course was built with, or re-onboard the course's execution"
            )


def copy(checkout: Path, target: Path, inputs: Sequence[str]) -> tuple[str, ...]:
    """Copy each input root from `checkout` into `target`, as bytes; return what was written."""
    checkout, target = Path(checkout), Path(target)
    written: list[str] = []
    for entry in inputs:
        source = checkout / entry
        if source.is_file():
            files = [source]
        elif source.is_dir():
            files = sorted(p for p in source.rglob("*") if p.is_file())
        else:
            raise VendorRefused(f"the toolchain names an input it does not hold: {scrub(entry)}")
        for one in files:
            relative = one.relative_to(checkout)
            if any(part in SKIPPED for part in relative.parts) or one.suffix == ".pyc":
                continue
            (target / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(one, target / relative)
            written.append(relative.as_posix())
    return tuple(sorted(written))


def _printed_by(checkout: Path) -> list[str]:
    """Return the command the contract names for a build as data, read from `consuming.json`."""
    try:
        text = (checkout / CONSUMING).read_text(encoding="utf-8")
    except OSError as missing:
        raise VendorRefused("the toolchain checkout carries no consuming.json") from missing
    contract = read(text, component=EDITOR_COMPONENT, api=EDITOR_API, promise=EDITOR_PROMISE)
    if require(contract, "builds", "builds_api") != BUILDS_API:
        raise VendorRefused("the toolchain prints its builds in a shape this skill has not read")
    command = [str(one) for one in require(contract, "builds", "printed_by")]
    if IMAGE_SLOT not in command or SET_SLOT not in command:
        raise VendorRefused("the toolchain's builds.printed_by names no image or no set slot")
    return command


def _asked(
    checkout: Path,
    command: list[str],
    image: str,
    runtimes: Sequence[str],
    prime: Path | None,
    platform: str,
    run: Run,
) -> Mapping[str, object]:
    """One build, as the toolchain printed it."""
    argv = [
        image if one == IMAGE_SLOT else ",".join(runtimes) if one == SET_SLOT else one
        for one in command
    ]
    if "--prime" in argv:
        at = argv.index("--prime")
        argv = (
            argv[:at] + (["--prime", str(Path(prime).resolve())] if prime else []) + argv[at + 2 :]
        )
    argv = [sys.executable if one == "python3" else one for one in argv] + ["--platform", platform]
    code, printed = run(argv, checkout)
    if code != 0:
        raise VendorRefused(
            f"the toolchain refused the {image} build (exit {code}): run its builds command "
            "in the checkout to read why"
        )
    try:
        decoded = json.loads(printed)
    except ValueError as garbled:
        raise VendorRefused(f"the toolchain printed no document for the {image} build") from garbled
    if not isinstance(decoded, dict):
        raise VendorRefused(f"the toolchain printed no document for the {image} build")
    document = {key: decoded[key] for key in KEPT if key in decoded}
    assert_clean(document, f"the toolchain's {image} build")
    if document.get("builds_api") != BUILDS_API or document.get("image") != image:
        raise VendorRefused(
            f"the toolchain answered the {image} build in a shape this skill has not read"
        )
    return document


def _recorded(path: Path) -> str:
    """Return the one image tag an env file the execution skill wrote records."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as missing:
        raise VendorRefused(
            "the course records no runner or editor tag: onboard its execution first"
        ) from missing
    values = [line.split("=", 1)[1] for line in lines if "=" in line and not line.startswith("#")]
    if len(values) != 1:
        raise VendorRefused("a recorded env file holds other than one tag")
    return values[0].strip()


def _commit(checkout: Path, run: Run) -> str:
    """Return the toolchain checkout's commit, or the word `unknown` outside a git checkout."""
    code, printed = run(["git", "-C", str(checkout), "rev-parse", "HEAD"], checkout)
    return printed.strip() if code == 0 else "unknown"
