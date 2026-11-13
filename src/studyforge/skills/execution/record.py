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

## ⭐ A CORPUS THAT NAMES A PROFILE RECORDS THE PROFILE'S TAGS

⭐ **A corpus that names an image profile (`profile` in `corpus.json`) runs on
the profile's images**, which the component layers on the base of its declared
runtimes. So each image is asked with the contract's `profile_tag.printed_by`,
its profile, image and set filled by `toolchain.select` and its platform the
host's, which the caller hands in as `platform`, exactly as the export's
lock check asks it; and what is recorded must be one tag of
`<block>.image.repository-<profile>`. ⛔ The plain base's tag is never recorded
in its place: that image lacks what the profile adds.

⛔ **A profile and a prime do not combine here, and such a corpus is refused.**
The contract's profile command takes no prime, and a profile image is built on
the unprimed base, so no tag the component computes names an image carrying
both: recording either half would start images that cannot run this corpus's
practices offline. The export layers the prime on the profile image itself.

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

#: The platforms a profile's tag is asked for, as the contract's `<platform>` slot names them.
#: ⭐ The caller names the host's: this package reads nothing of the machine it runs on.
PLATFORMS = frozenset({"linux/amd64", "linux/arm64"})

#: Runs one argv in one directory and answers `(exit code, stdout)`.
Ask = Callable[[Sequence[str], Path], tuple[int, str]]


def argv(execution: Execution, root: Path, *, platform: str | None = None) -> list[str]:
    """Return the runner's own `tag_from`, with the prime this skill wrote flagged.

    ⭐ For a corpus that names a profile, the profile's tag command on `platform`.
    """
    runner = _runner(execution)
    if runner.selection.profile is not None:
        return _profiled(execution, runner.selection, platform)
    return _flagged(execution, root, runner.selection.tag_from, runner.prime_flag)


def editor_argv(execution: Execution, root: Path, *, platform: str | None = None) -> list[str]:
    """Return the editor's own `tag_from`, with the same prime flagged when it declares one.

    ⭐ For a corpus that names a profile, the profile's tag command on `platform`.
    """
    editor = _editor(execution)
    if editor.profile is not None:
        return _profiled(execution, editor, platform)
    return _flagged(execution, root, editor.tag_from, editor.prime_flag)


def _profiled(execution: Execution, selection: Selection, platform: str | None) -> list[str]:
    """Return the profile's tag command for one image, or refuse a corpus that also primes."""
    if execution.primed is not None and execution.primed.projects:
        raise ExecutionRefused(
            "this corpus names an image profile and also has a prime, and the two do not "
            "combine in a local record: the component's profile_tag.printed_by takes no prime "
            "and a profile image is built on the unprimed base, so no tag it computes names an "
            "image with both. Run it from its export, whose course layer primes the profile "
            "image, or drop one of the two"
        )
    if platform not in PLATFORMS:
        raise ExecutionRefused(
            f"this corpus names an image profile, whose tag is computed for one platform: hand "
            f"the record step platform= one of {sorted(PLATFORMS)}, the host's"
        )
    return list(selection.profile_tag_on(platform))


def _flagged(
    execution: Execution, root: Path, tag_from: Sequence[str], flag: str | None
) -> list[str]:
    """Return `tag_from`, plus `flag` pointing at the written prime when there is one."""
    command = list(tag_from)
    if flag is not None and execution.primed is not None and execution.primed.projects:
        prime = str((root / PRIME_DIR).resolve())
        command += [prime if part == DIRECTORY_SLOT else part for part in flag.split()]
    return command


def record_runner(
    execution: Execution, root: Path, component: Path, *, ask: Ask, platform: str | None = None
) -> str:
    """Ask the component for the runner's tag, write it, and return the path written.

    ⭐ The primed runner's tag, or, for a corpus naming a profile, its runner on `platform`.
    """
    runner = _runner(execution)
    command = argv(execution, root, platform=platform)
    tag = _asked(ask, command, component, runner.selection, "runner")
    return _written(
        root, RUNNER_ENV, text(runner.selection.image_env, tag, profile=runner.selection.profile)
    )


def record_editor(
    execution: Execution, root: Path, component: Path, *, ask: Ask, platform: str | None = None
) -> str:
    """Ask the component for the editor's tag, write it, and return the path written.

    ⭐ The editor's tag, or, for a corpus naming a profile, its editor on `platform`.
    """
    editor = _editor(execution)
    command = editor_argv(execution, root, platform=platform)
    tag = _asked(ask, command, component, editor, "editor")
    return _written(
        root, EDITOR_ENV, text(editor.image_env, tag, image="editor", profile=editor.profile)
    )


def _asked(ask: Ask, command: list[str], component: Path, selection: Selection, block: str) -> str:
    """Run one tag command through `ask`, and return the one tag it printed or refuse."""
    asked = "profile_tag.printed_by" if selection.profile else f"{block}.image.tag_from"
    repository = selection.profile_repository or selection.repository
    code, printed = ask(command, component)
    if code != 0:
        raise ExecutionRefused(
            f"the component's {asked} exited {code}; its output is not "
            f"reproduced here, since it can carry a home path. Run it in the pinned "
            f"checkout to read why"
        )
    tag = printed.strip()
    if not _one_tag(tag, repository):
        whose = f"{block}.image.repository" + ("-<profile>" if selection.profile else "")
        raise ExecutionRefused(
            f"the component's {asked} printed something that is not one tag "
            f"of its own {whose}, and a tag this skill cannot read is not "
            f"one it will record"
        )
    return tag


def _written(root: Path, where: str, content: str) -> str:
    """Write one environment file under `root`, and return where."""
    target = root / where
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    written.stamp(root, [where])
    return where


def text(variable: str, tag: str, *, image: str = "runner", profile: str | None = None) -> str:
    """Return one environment file's bytes: the generated sentence and the one variable.

    ⭐ A profile's tag says so: which profile, and the contract key that printed it.
    """
    holds = WHAT_IT_HOLDS.get(image)
    if holds is None:
        raise ExecutionRefused(
            f"an environment file is recorded for one of {sorted(WHAT_IT_HOLDS)} and for "
            f"no other image; the one asked for is not reproduced here, since a refusal never "
            f"quotes a value that may be personal"
        )
    if profile is not None:
        holds = (
            f"# The {image}'s tag for image profile {profile}, as the component's own\n"
            "# profile_tag.printed_by printed it for this host's platform. Re-run the skill's\n"
            "# record step when the component's pin or the host's architecture moves.\n"
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
