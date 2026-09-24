r"""The runner's and the editor's tags, recorded by the skill — never typed, never hand-written.

**What it does.** Runs the component's own `tag_from` argv for each image — the
declared set in its slot and, for the runner, the prime flag pointing at the
prime this skill wrote — in the pinned component checkout, checks what it
printed, and writes it into the environment file the reader's compose command
names: `RUNNER_ENV` for the runner, `EDITOR_ENV` for the editor. So
`docker compose` starts both from exactly the tags the corpus recorded.

**How you use it.** After `onboard.write`, because the runner's tag is a
function of the prime on disk: `record_runner(execution, root, component,
ask=…)` and `record_editor(execution, root, component, ask=…)` each return the
path written. `ask(argv, cwd)` runs one argv and answers `(exit code, stdout)`:

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

⚠️ Unrecorded, the tags a corpus's primed runner and editor builds produce are
known only to the running environment, and a switch-over would have to take
them from a person. ⭐ A tag is
a function of the build's inputs (the contract says so), so the only honest way
to hold one is to ask the build for it and write down what it answered.
⛔ **A hand-edit to either file is a finding against this skill**, exactly as
for every other file it writes.

## ⭐ THE EDITOR'S TAG IS ASKED EXACTLY AS THE READER'S DOCUMENT BUILDS IT

⭐ **From `provides` 3 the contract declares `editor.prime` as it declares the
runner's**, so the editor's tag is asked with the same prime flagged,
and `EXECUTION.md` prints the editor's build with it: the tag recorded is the
tag the printed, primed build produces. ⚠️ A contract that declares no editor
prime is read as it stands: the editor is asked, printed and recorded unprimed.

## ⚠️ RE-RUN IT WHEN AN INPUT MOVES

The component's pin, the prime, and the host's architecture each move a tag.
Re-running with none of them moved rewrites the same bytes.

## ⛔ NO ABSOLUTE PATH IS WRITTEN (R7)

⭐ The prime's absolute path is an ARGUMENT to the component's build and never
reaches a file; what is written is a tag, which the contract builds from a
repository, a set, an architecture and a digest — never from a host path.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from studyforge.skills.execution import written
from studyforge.skills.execution.onboard import (
    DIRECTORY_SLOT,
    EDITOR_ENV,
    GENERATED,
    PRIME_DIR,
    RUNNER_ENV,
    Execution,
    ExecutionRefused,
)
from studyforge.skills.execution.runnerservice import Runner
from studyforge.skills.execution.toolchain import Selection

#: What a printed tag may be made of. ⛔ One image reference and nothing else: no
#: space, no `=`, no `#`, no newline, nothing a compose env file reads otherwise.
TAG_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._/:-")

#: What each environment file says it holds, and when to re-record it. ⭐ The
#: runner's lines are the bytes a corpus already carries, unchanged.
WHAT_IT_HOLDS = {
    "runner": (
        "# The primed runner's tag, as the component's own runner.image.tag_from printed it\n"
        "# for the prime beside this file. Re-run the skill's record step when the\n"
        "# component's pin, the prime or the host's architecture moves.\n"
    ),
    "editor": (
        "# The editor's tag, as the component's own editor.image.tag_from printed it.\n"
        "# Re-run the skill's record step when the component's pin or the host's\n"
        "# architecture moves.\n"
    ),
}

#: Runs one argv in one directory and answers `(exit code, stdout)`.
Ask = Callable[[Sequence[str], Path], tuple[int, str]]


def argv(execution: Execution, root: Path) -> list[str]:
    """Return the runner's own `tag_from`, with the prime this skill wrote flagged."""
    runner = _runner(execution)
    return _flagged(execution, root, runner.selection.tag_from, runner.prime_flag)


def editor_argv(execution: Execution, root: Path) -> list[str]:
    """Return the editor's own `tag_from`, with the same prime flagged when it declares one."""
    editor = _editor(execution)
    return _flagged(execution, root, editor.tag_from, editor.prime_flag)


def _flagged(
    execution: Execution, root: Path, tag_from: Sequence[str], flag: str | None
) -> list[str]:
    """Return `tag_from`, plus `flag` pointing at the written prime when there is one."""
    command = list(tag_from)
    if flag is not None and execution.primed is not None and execution.primed.projects:
        prime = str((root / PRIME_DIR).resolve())
        command += [prime if part == DIRECTORY_SLOT else part for part in flag.split()]
    return command


def record_runner(execution: Execution, root: Path, component: Path, *, ask: Ask) -> str:
    """Ask the component for the primed runner's tag, write it, and return the path written."""
    runner = _runner(execution)
    tag = _asked(ask, argv(execution, root), component, runner.repository, "runner")
    return _written(root, RUNNER_ENV, text(runner.selection.image_env, tag))


def record_editor(execution: Execution, root: Path, component: Path, *, ask: Ask) -> str:
    """Ask the component for the editor's tag, write it, and return the path written."""
    editor = _editor(execution)
    tag = _asked(ask, editor_argv(execution, root), component, editor.repository, "editor")
    return _written(root, EDITOR_ENV, text(editor.image_env, tag, image="editor"))


def _asked(ask: Ask, command: list[str], component: Path, repository: str, block: str) -> str:
    """Run one `tag_from` through `ask`, and return the one tag it printed or refuse."""
    code, printed = ask(command, component)
    if code != 0:
        raise ExecutionRefused(
            f"the component's {block}.image.tag_from exited {code}; its output is not "
            f"reproduced here, since it can carry a home path. Run it in the pinned "
            f"checkout to read why"
        )
    tag = printed.strip()
    if not _one_tag(tag, repository):
        raise ExecutionRefused(
            f"the component's {block}.image.tag_from printed something that is not one tag "
            f"of its own {block}.image.repository, and a tag this skill cannot read is not "
            f"one it will record"
        )
    return tag


def _written(root: Path, where: str, content: str) -> str:
    """Write one environment file under `root`, and return where."""
    target = root / where
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    written.stamp(root, [where])
    return where


def text(variable: str, tag: str, *, image: str = "runner") -> str:
    """Return one environment file's bytes: the generated sentence and the one variable."""
    holds = WHAT_IT_HOLDS.get(image)
    if holds is None:
        raise ExecutionRefused(
            f"an environment file is recorded for one of {sorted(WHAT_IT_HOLDS)} and for "
            f"no other image; the one asked for is not reproduced here, since a refusal never "
            f"quotes a value that may be personal"
        )
    return f"# {GENERATED}\n{holds}{variable}={tag}\n"


def _one_tag(tag: str, repository: str) -> bool:
    """Whether `tag` is one reference into `repository`, with a tag after its colon."""
    head, _, name = tag.rpartition(":")
    return head == repository and bool(name) and "/" not in name and set(tag) <= TAG_CHARACTERS


def _runner(execution: Execution) -> Runner:
    """Return the runner the execution planned, or refuse a corpus that is not runnable."""
    if not execution.runnable or execution.runner is None:
        raise ExecutionRefused("this corpus declares no runtime, so there is no runner to record")
    return execution.runner


def _editor(execution: Execution) -> Selection:
    """Return the editor's selection, or refuse a corpus that is not runnable."""
    if not execution.runnable or execution.selection is None:
        raise ExecutionRefused("this corpus declares no runtime, so there is no editor to record")
    return execution.selection
