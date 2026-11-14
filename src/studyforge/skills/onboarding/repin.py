r"""Move an onboarded corpus to a newer framework build in one command: `repin`.

**What it does.** From a corpus root, takes a framework checkout and runs, in
order: refuse a dirty checkout and read its full commit, build its wheel, install
the wheel into the Python running this, then — inside that freshly installed
library — re-pin and re-onboard, write and record execution, build the site, and,
when asked, stage the study server's image and bring the corpus up, and audit
with the corpus's own `ingest`. Each step prints its name and its result; the
first failure stops the run, names its step and exits non-zero.

**How you use it.**

    python3 -m studyforge.skills.onboarding repin <framework-checkout> \
        [--toolchain PATH] [--up] [--audit-date YYYY-MM-DD] [--dry-run]

`main(argv, run=..., out=...)` is the same, with the process runner injectable:
`run(argv, cwd)` answers `(exit code, standard output)`, as `execute.maintenance.ask` does.

**Depends on.** This package's `reonboard`, `hand_edited`, `library` and `verify`;
the execution skill's `generate`, `write`, `record_runner`, `record_editor` and
`stage_site`; the site build's `main`; and `execute.maintenance` for every process.

## ⛔ The pin is the checkout's FULL commit, read by git and never typed

⚠️ The hand-run sequence this replaces once wrote a truncated hash into a pin with
`sed`. ⭐ Here the commit is `git rev-parse HEAD`, checked as forty hex digits
before anything is built, and it reaches the pin only through `reonboard`, which
moves the pin, every stub and the reader document together. ⛔ A checkout with
uncommitted changes is refused: its wheel would not be the commit it names.

## ⛔ The second half runs in the library it just installed

⚠️ A Python that installed a new wheel still runs the OLD library it imported.
⭐ So after the install, `hand-over` starts the same command in a fresh
interpreter with `--installed <commit>`, and that process runs the rest — and
refuses first unless the library it imports was built from that commit.

## ⭐ Docker only when asked

`stage-site` and `compose-up` run only with `--up`, and `audit` only with
`--audit-date`; otherwise each prints that it was skipped. `--dry-run` prints
every step and its commands and runs nothing.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

from studyforge.corpus.manifest import MANIFEST_FILENAME, load
from studyforge.execute import instance, maintenance
from studyforge.skills.execution import onboard as execution
from studyforge.skills.execution import record_editor, record_runner, siteservice
from studyforge.skills.execution import stage_site as _stage_site
from studyforge.skills.onboarding import library
from studyforge.skills.onboarding.pin import PinRefused, check_commit
from studyforge.skills.onboarding.record import hand_edited
from studyforge.skills.onboarding.reonboard import reonboard

#: How a process is run: `(argv, cwd) -> (exit code, standard output)`.
Run = Callable[[Sequence[str], Path], tuple[int, str]]

#: Where wheels are built, under the corpus root, one directory per commit.
WHEELS = ".scratch/wheels"

#: The wheel builder's Python: it needs setuptools, which a corpus's venv may lack.
BUILDER = "python3"

#: The file at a toolchain checkout's root that the execution skill reads.
CONSUMING = "consuming.json"


class Stopped(Exception):
    """A step failed; the message says why, in one sentence."""


@dataclass(frozen=True)
class Step:
    """One step: its name, the commands a dry run shows, and the act (`None` is skipped)."""

    name: str
    shows: tuple[str, ...]
    act: Callable[[], str] | None
    skipped: str = ""


@dataclass
class Repin:
    """One run's arguments, the process runner, and the commit once it is read."""

    root: Path
    checkout: str
    toolchain: str | None
    up: bool
    audit_date: str | None
    platform: str | None
    builder: str
    run: Run
    out: TextIO
    commit: str = field(default="")

    def must(self, argv: Sequence[str]) -> str:
        """Run `argv` in the corpus root; its output, or stop on a non-zero exit."""
        code, said = self.run(list(argv), self.root)
        if code != 0:
            raise Stopped(f"`{' '.join(argv[:4])} ...` exited {code}")
        return said

    def wheels(self) -> Path:
        """The directory this commit's wheel is built into."""
        return self.root / WHEELS / (self.commit or "<commit>")


# --- the framework functions a step calls, named so a test can stand in ------


def build_site(root: Path, out: TextIO) -> int:
    """Build the site into the corpus root, as `studyforge build . --out .` does."""
    from studyforge.cli.site.cli import main as build

    return build([str(root), "--out", str(root)], out=out)


def runtimes_of(root: Path) -> tuple[str, ...]:
    """The runtimes the corpus's manifest declares; empty means nothing to execute."""
    return tuple(load(root / MANIFEST_FILENAME).runtimes)


def write_execution(root: Path, toolchain: Path, platform: str | None, run: Run) -> None:
    """Execution steps 5 and 5a: write the files, then record both tags."""
    manifest = load(root / MANIFEST_FILENAME)
    try:
        editor_text = (toolchain / CONSUMING).read_text(encoding="utf-8")
    except OSError as error:  # ⛔ strerror, never the error: it names the path (R7)
        raise Stopped(f"cannot read the toolchain's {CONSUMING}: {error.strerror}") from None
    made = execution.generate(manifest, editor_text=editor_text, root=root)
    execution.write(made, root)
    record_runner(made, root, toolchain, ask=run, platform=platform)
    record_editor(made, root, toolchain, ask=run, platform=platform)


def stage_site(root: Path) -> None:
    """Execution step 5b: stage the study server's image from the pinned library."""
    _stage_site(root)


def compose_argv(*verb: str) -> list[str]:
    """The execution skill's compose command, reading every recorded env file, then `verb`."""
    files = (execution.RUNNER_ENV, execution.EDITOR_ENV, execution.INSTANCE_ENV, execution.SITE_ENV)
    flags = [part for name in files for part in ("--env-file", name)]
    return ["docker", "compose", *flags, "-f", execution.COMPOSE_FILE, *verb]


# --- the steps --------------------------------------------------------------


def first_half(job: Repin, handed: list[str], shown: list[str]) -> list[Step]:
    """The steps the invoking Python runs: checkout, wheel, install, hand-over.

    `handed` is what the installed library is started with, every path absolute;
    `shown` is the same as the operator typed it, which is what a dry run prints.
    """
    checkout, python, typed = job.checkout, sys.executable, shown[0]

    def check() -> str:
        if job.must(["git", "-C", checkout, "status", "--porcelain"]).strip():
            raise Stopped("the checkout has uncommitted changes; commit or stash them first")
        head = job.must(["git", "-C", checkout, "rev-parse", "HEAD"]).strip()
        try:
            job.commit = check_commit(head)
        except PinRefused as refusal:
            raise Stopped(str(refusal)) from None
        return f"clean, at {job.commit}"

    def wheel() -> str:
        job.wheels().mkdir(parents=True, exist_ok=True)
        for old in job.wheels().glob("studyforge-*.whl"):
            old.unlink()
        job.must([job.builder, *WHEEL_ARGS, str(job.wheels()), checkout])
        built = sorted(job.wheels().glob("studyforge-*.whl"))
        if len(built) != 1:
            raise Stopped(f"the build left {len(built)} studyforge wheels, not one")
        return built[0].name

    def install() -> str:
        (built,) = job.wheels().glob("studyforge-*.whl")
        job.must([python, "-m", "pip", *INSTALL_ARGS, str(built)])
        return f"installed {built.name}"

    def hand_over() -> str:
        code, _ = job.run([python, "-m", "studyforge.skills.onboarding", "repin", *handed,
                           job.commit], job.root)  # fmt: skip
        if code != 0:
            raise Stopped(f"the installed library stopped (exit {code}) at the step it named")
        return "the installed library finished every step"

    wheels = f"{WHEELS}/<commit>"
    return [
        Step("checkout", (f"git -C {typed} status --porcelain",
                          f"git -C {typed} rev-parse HEAD"), check),  # fmt: skip
        Step("wheel", (f"{job.builder} {' '.join(WHEEL_ARGS)} {wheels} {typed}",), wheel),
        Step("install", (f"{python} -m pip {' '.join(INSTALL_ARGS)} {wheels}/studyforge-*.whl",),
             install),  # fmt: skip
        Step("hand-over", (f"{python} -m studyforge.skills.onboarding repin "
                           f"{' '.join(shown)} <commit>",), hand_over),  # fmt: skip
    ]


#: `pip wheel`'s arguments, before the output directory and the checkout.
WHEEL_ARGS = ("-m", "pip", "wheel", "-q", "--no-deps", "--no-build-isolation", "-w")

#: `pip install`'s arguments, before the wheel: offline, this wheel alone, replaced.
INSTALL_ARGS = ("install", "--no-index", "--no-deps", "--force-reinstall")


def second_half(job: Repin) -> list[Step]:
    """The steps the installed library runs: pin, execution, build, site, up, audit."""
    root = job.root

    def pin() -> str:
        built = library.commit()
        if built != job.commit:
            raise Stopped(f"the library this Python imports was not built from {job.commit}")
        reonboard(root, framework_commit=job.commit).write(root, regenerate=True)
        edited = hand_edited(root)
        if edited:
            raise Stopped(f"hand-edited after the re-onboarding: {edited}")
        return f"pinned {job.commit}; hand_edited: []"

    def execute() -> str:
        if not runtimes_of(root):
            return "the corpus declares no runtimes: nothing to write"
        if job.toolchain is None:
            raise Stopped("the corpus declares runtimes: pass --toolchain <its checkout>")
        write_execution(root, Path(job.toolchain), job.platform, job.run)
        return "written, and both tags recorded"

    def build() -> str:
        code = build_site(root, job.out)
        if code != 0:
            raise Stopped(f"the build exited {code}")
        return "built"

    def stage() -> str:
        if not runtimes_of(root):
            return "the corpus declares no runtimes: nothing to stage"
        stage_site(root)
        return "staged"

    def up() -> str:
        if not runtimes_of(root):
            return "the corpus declares no runtimes: nothing to bring up"
        job.must(compose_argv("build", siteservice.SERVICE))
        job.must(siteservice.prune(instance.project_for(_source(root))).split())
        job.must(compose_argv("up", "-d", "--wait"))
        return "up"

    def audit() -> str:
        job.must([sys.executable, "-m", "ingest", ".", str(job.audit_date)])
        return f"ingested at {job.audit_date}"

    toolchain = job.toolchain or "<--toolchain>"
    prune = siteservice.prune(_project(root))
    docker = "skipped (pass --up to stage the site image and bring the corpus up)"
    return [
        Step("pin", ("reonboard('.', framework_commit=<commit>).write('.', regenerate=True)",
                     "hand_edited('.') == []"), pin),  # fmt: skip
        Step("execution", (f"generate + write + record_runner + record_editor ({toolchain})",),
             execute),  # fmt: skip
        Step("build", ("studyforge build . --out .",), build),
        Step("stage-site", ("stage_site('.')",), stage if job.up else None, docker),
        Step("compose-up", (" ".join(compose_argv("build", siteservice.SERVICE)), prune,
                            " ".join(compose_argv("up", "-d", "--wait"))),
             up if job.up else None, docker),  # fmt: skip
        Step("audit", (f"{sys.executable} -m ingest . {job.audit_date or '<date>'}",),
             audit if job.audit_date else None, "skipped (pass --audit-date YYYY-MM-DD)"),
    ]


def _source(root: Path) -> str:
    """The corpus's `source`, which names its compose project."""
    return load(root / MANIFEST_FILENAME).source


def _project(root: Path) -> str:
    """The compose project a dry run prints, or its shape when the manifest is unread."""
    try:
        return instance.project_for(_source(root))
    except Exception:  # noqa: BLE001 - a dry run prints the shape rather than refuse
        return instance.project_for("<source>")


# --- running them -----------------------------------------------------------


def perform(steps: Sequence[Step], out: TextIO, *, dry_run: bool, start: int = 1) -> int:
    """Run (or, dry, print) each step in order; 1 at the first failure, naming it."""
    for number, step in enumerate(steps, start):
        if step.act is None:
            print(f"[{number}] {step.name}: {step.skipped}", file=out)
            continue
        print(f"[{number}] {step.name}", file=out, flush=True)
        if dry_run:
            print("\n".join(f"      {line}" for line in step.shows), file=out)
            continue
        try:
            print(f"      -> {step.act()}", file=out, flush=True)
        except Exception as error:  # noqa: BLE001 - any refusal stops the run, named
            said = error if isinstance(error, Stopped) else f"{type(error).__name__}: {error}"
            print(f"      FAILED: {said}\nrepin stopped at step '{step.name}'", file=out)
            return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser, so a test can read the interface."""
    parser = argparse.ArgumentParser(
        prog="python3 -m studyforge.skills.onboarding repin",
        description="Move the corpus here to the framework build at a checkout, in one command.",
    )
    parser.add_argument("checkout", help="the framework checkout to build, install and pin")
    parser.add_argument("--toolchain", help="the code-server-toolchain checkout (execution)")
    parser.add_argument("--up", action="store_true", help="stage the site image, bring it up")
    parser.add_argument("--audit-date", type=_date, help="re-ingest with this date at the end")
    parser.add_argument("--platform", help="linux/amd64 or linux/arm64, for a profiled corpus")
    parser.add_argument("--builder", default=BUILDER, help="the Python that builds the wheel")
    parser.add_argument("--root", default=".", help="the corpus root (default: here)")
    parser.add_argument("--dry-run", action="store_true", help="print the steps, run nothing")
    parser.add_argument("--installed", help=argparse.SUPPRESS)
    return parser


def _date(text: str) -> str:
    """Accept `YYYY-MM-DD` and nothing else."""
    try:
        return datetime.date.fromisoformat(text).isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a YYYY-MM-DD date") from None


def main(
    argv: list[str] | None = None, *, run: Run | None = None, out: TextIO | None = None
) -> int:
    """Run the re-pin from the corpus root; 0 when every step finished, 1 at a failure."""
    stream = sys.stdout if out is None else out
    arguments = build_parser().parse_args(argv)
    job = Repin(
        root=_absolute(arguments.root),
        checkout=str(_absolute(arguments.checkout)),
        toolchain=arguments.toolchain,
        up=arguments.up,
        audit_date=arguments.audit_date,
        platform=arguments.platform,
        builder=arguments.builder,
        run=run or (lambda argv, cwd: maintenance.ask(argv, cwd, out=stream)),
        out=stream,
        commit=arguments.installed or "",
    )
    second = second_half(job)
    if arguments.installed:
        return perform(second, stream, dry_run=arguments.dry_run, start=5)
    first = first_half(job, _handed(arguments, _absolute), _handed(arguments, str))
    return perform(first + (second if arguments.dry_run else []), stream, dry_run=arguments.dry_run)


def _handed(arguments: argparse.Namespace, place: Callable[[str], object]) -> list[str]:
    """The arguments the installed library is started with, up to `--installed`'s value."""
    handed = [str(place(arguments.checkout)), "--root", str(place(arguments.root))]
    if arguments.toolchain:
        handed += ["--toolchain", str(place(arguments.toolchain))]
    handed += ["--up"] if arguments.up else []
    handed += ["--audit-date", arguments.audit_date] if arguments.audit_date else []
    handed += ["--platform", arguments.platform] if arguments.platform else []
    return [*handed, "--installed"]


def _absolute(path: str) -> Path:
    """`path` as the invoking directory reads it, so the hand-over reads the same place."""
    return Path(path).absolute()
