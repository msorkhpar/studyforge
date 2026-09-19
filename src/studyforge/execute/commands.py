"""What the runner will start: argv lists, a relative directory, one container name.

**What it does.** Checks every input `Runner.start` is handed before any
process exists, and returns it unchanged or raises `RunRefused`.

**How you use it.** `require_commands(commands)`, `require_workdir(cwd)` and
`require_container(name)`; `container_for(source)` names the runner container
a corpus's reader starts.

**Depends on.** `studyforge.exercise`'s `require_command` and `require_path` —
⛔ the one existing definition of what a command and a path may be, never a
second pattern set here — and `errors`.

## ⛔ Nothing a client sends becomes a command

⭐ **The property is structural.** A command is a list of argv tokens, each in
`exercise`'s permitted set, and the runner hands it to the operating system's
`exec` **verbatim** — nothing on the path parses it (the container's `sh`
runs one fixed program that `exec`s its positional arguments), so `;`, `|`,
`$(…)` and globs mean nothing even if one arrived. ⛔ A `str` is refused rather
than split: splitting one is writing a shell parser at the boundary that exists
to avoid needing a shell (`exercise.safety`). The commands a caller passes are
the generated document's, read from disk (spec §8.3, rule 3); a request body
has no parameter on this surface to arrive through.

⛔ **The same check runs again here although the record was checked when it was
read.** A runner that trusted its caller would make every future caller part of
its security argument; checking at the one place a process starts keeps the
argument in one file.
"""

from __future__ import annotations

from collections.abc import Sequence

from studyforge.execute.errors import RunRefused
from studyforge.exercise import SAFE_SEGMENT, ExerciseError, require_command, require_path

#: The directory a command runs in when the caller names none: the source root.
ROOT_DIR = "."

#: The runner container's name is this prefix and the corpus's `source`, the
#: name `code-server-toolchain`'s README gives the reader's run line.
CONTAINER_PREFIX = "studyforge-runner-"

COMMANDS_PERMITTED = "a non-empty list of commands, each a list of arguments"


def require_commands(commands: object) -> tuple[tuple[str, ...], ...]:
    """Return `commands` as a tuple of argv tuples, or raise `RunRefused`."""
    if isinstance(commands, (str, bytes)) or not isinstance(commands, Sequence) or not commands:
        raise RunRefused(
            f"the runner takes {COMMANDS_PERMITTED}; the value is not reproduced here (R7)"
        )
    checked = []
    for index, command in enumerate(commands, start=1):
        try:
            checked.append(require_command(command, f"command {index}", "run"))
        except ExerciseError as refusal:
            raise RunRefused(str(refusal)) from None
    return tuple(checked)


def require_workdir(cwd: object) -> str:
    """Return `cwd`, a relative directory inside the source root, or raise `RunRefused`."""
    if cwd == ROOT_DIR:
        return ROOT_DIR
    try:
        return require_path(cwd, "cwd", "run")
    except ExerciseError as refusal:
        raise RunRefused(str(refusal)) from None


def require_container(name: object) -> str:
    """Return `name` if it is one safe word, or raise `RunRefused`."""
    if not isinstance(name, str) or SAFE_SEGMENT.match(name) is None:
        raise RunRefused(
            "a container name must be one word of ASCII letters, digits, '.', '_' and '-', "
            "not beginning '-'; the value is not reproduced here (R7)"
        )
    return name


def container_for(source: str) -> str:
    """Name the runner container the reader starts for corpus `source`."""
    return require_container(CONTAINER_PREFIX + source)
