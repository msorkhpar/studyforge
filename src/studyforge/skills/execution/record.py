r"""The primed runner's tag, recorded by the skill — never typed, never a hand-written file.

**What it does.** Runs the component's own `runner.image.tag_from` argv — the
declared set in its slot, the prime flag pointing at the prime this skill
wrote — in the pinned component checkout, checks what it printed, and writes
it into `RUNNER_ENV`: the one environment file the reader's compose command
names, so `docker compose` starts the runner from exactly that tag (`W445`).

**How you use it.** After `onboard.write`, because the tag is a function of the
prime on disk: `record_runner(execution, root, component, ask=…)` returns the path
written. `ask(argv, cwd)` runs one argv and answers `(exit code, stdout)`:

    def ask(argv, cwd):
        done = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=60)
        return done.returncode, done.stdout

**Depends on.** `onboard` for the plan and the paths. ⛔ Nothing
source-specific (R1).

## ⛔ THE CALLER HANDS IN THE ONE PROCESS, AND IT IS NOT DOCKER

⭐ **This package imports nothing that can start a process** (§8.3, asserted
structurally over every module it ships), and this module keeps that property:
the argv it composes is the component's own `tag_from`, whose `--print-tag`
hashes files and exits without reaching a daemon, and the caller's `ask` is
what runs it. ⭐ Everything else — which argv, where, what a tag may look like,
and the bytes written — is decided here, so the record is the skill's and not
the caller's.

## ⛔ WHY THE SKILL RUNS IT RATHER THAN THE READER TYPING ITS OUTPUT

⚠️ `ISO-20` measured the gap: nothing generated recorded the tag the corpus's
primed build produced, so the corpus hand-scripted a record of it, and nothing
generated READ that record either. ⭐ A tag is a function of the build's inputs
(the contract says so), so the only honest way to hold one is to ask the build
for it and write down what it answered. ⛔ **A hand-edit to `RUNNER_ENV` is a
finding against this skill**, exactly as for every other file it writes.

## ⚠️ RE-RUN IT WHEN AN INPUT MOVES

The component's pin, the prime, and the host's architecture each move the tag.
Re-running with none of them moved rewrites the same bytes.

## ⛔ NO ABSOLUTE PATH IS WRITTEN (R7)

⭐ The prime's absolute path is an ARGUMENT to the component's build and never
reaches the file; what is written is the tag, which the contract builds from a
repository, a set, an architecture and a digest — never from a host path.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from studyforge.skills.execution.onboard import (
    DIRECTORY_SLOT,
    GENERATED,
    PRIME_DIR,
    RUNNER_ENV,
    Execution,
    ExecutionRefused,
)
from studyforge.skills.execution.runnerservice import Runner

#: What a printed tag may be made of. ⛔ One image reference and nothing else: no
#: space, no `=`, no `#`, no newline, nothing a compose env file reads otherwise.
TAG_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._/:-")

#: Runs one argv in one directory and answers `(exit code, stdout)`.
Ask = Callable[[Sequence[str], Path], tuple[int, str]]


def argv(execution: Execution, root: Path) -> list[str]:
    """Return the component's own `tag_from`, with the prime this skill wrote flagged."""
    runner = _runner(execution)
    command = list(runner.selection.tag_from)
    if execution.primed is not None and execution.primed.projects:
        prime = str((root / PRIME_DIR).resolve())
        command += [prime if part == DIRECTORY_SLOT else part for part in runner.prime_flag.split()]
    return command


def record_runner(execution: Execution, root: Path, component: Path, *, ask: Ask) -> str:
    """Ask the component for the primed runner's tag, write it, and return the path written."""
    runner = _runner(execution)
    code, printed = ask(argv(execution, root), component)
    if code != 0:
        raise ExecutionRefused(
            f"the component's runner.image.tag_from exited {code}; its output is not "
            f"reproduced here (R7). Run it in the pinned checkout to read why"
        )
    tag = printed.strip()
    if not _one_tag(tag, runner.repository):
        raise ExecutionRefused(
            "the component's runner.image.tag_from printed something that is not one tag "
            "of its own runner.image.repository, and a tag this skill cannot read is not one "
            "it will record"
        )
    target = root / RUNNER_ENV
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text(runner.selection.image_env, tag), encoding="utf-8")
    return RUNNER_ENV


def text(variable: str, tag: str) -> str:
    """Return the environment file's bytes: the generated sentence and the one variable."""
    return (
        f"# {GENERATED}\n"
        "# The primed runner's tag, as the component's own runner.image.tag_from printed it\n"
        "# for the prime beside this file. Re-run the skill's record step when the\n"
        "# component's pin, the prime or the host's architecture moves.\n"
        f"{variable}={tag}\n"
    )


def _one_tag(tag: str, repository: str) -> bool:
    """Whether `tag` is one reference into `repository`, with a tag after its colon."""
    head, _, name = tag.rpartition(":")
    return head == repository and bool(name) and "/" not in name and set(tag) <= TAG_CHARACTERS


def _runner(execution: Execution) -> Runner:
    """Return the runner the execution planned, or refuse a corpus that is not runnable."""
    if not execution.runnable or execution.runner is None:
        raise ExecutionRefused("this corpus declares no runtime, so there is no runner to record")
    return execution.runner
