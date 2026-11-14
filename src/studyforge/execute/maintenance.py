"""One command an operator's maintenance step names, run on the host and echoed as it runs.

**What it does.** Runs one argv in a directory, echoes each line of its standard
output as it arrives, and answers `(exit code, standard output)`. Standard error
passes straight through to the operator's terminal and is never part of the answer.

**How you use it.**

    from studyforge.execute.maintenance import ask

    code, said = ask(["git", "-C", checkout, "rev-parse", "HEAD"], corpus_root)

⭐ Its shape is the `ask(argv, cwd)` the execution skill's `record_runner` and
`record_editor` take, so the one runner serves both.

**Depends on.** `subprocess`, the standard library.

## ⛔ Why it lives in the runner's package

Spec §8.3 keeps every process the framework starts in `execute`, so the one place
process starts are audited stays one place. ⭐ The onboarding skill's `repin`
hands its pip, git, docker and `ingest` commands here rather than starting a
process itself. ⛔ It is never reached by a page or by the study server: the
operator types the command that calls it, and nothing a reader does reaches it.

## ⛔ A failure is an exit code, never an exception

⭐ A program that does not exist answers `NOT_STARTED` and says so on the echo:
the caller names the step that stopped, and a traceback would name this module.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

#: The prefix each echoed line carries, so a command's output reads as the step's.
ECHO = "  | "

#: The exit code of a command whose program could not be started (a shell's own).
NOT_STARTED = 127


def ask(argv: Sequence[str], cwd: Path | str, *, out: TextIO | None = None) -> tuple[int, str]:
    """Run `argv` in `cwd`, echoing its output to `out`; answer its exit code and output."""
    stream = sys.stdout if out is None else out
    try:
        process = subprocess.Popen(  # noqa: S603 - an argv the operator's own command built
            [str(part) for part in argv],
            cwd=cwd,
            stdin=subprocess.PIPE,  # ⭐ closed at once below: DEVNULL opens /dev/null to write
            stdout=subprocess.PIPE,
            text=True,
        )
    except OSError:
        print(f"{ECHO}{argv[0]}: did not start", file=stream)
        return NOT_STARTED, ""
    if process.stdin is not None:
        process.stdin.close()  # end of input, as /dev/null would give
    said: list[str] = []
    with process:  # ⭐ closes the pipe and waits, so no descriptor outlives the call
        for line in process.stdout or ():
            said.append(line)
            print(f"{ECHO}{line.rstrip(chr(10))}", file=stream, flush=True)
    return process.returncode, "".join(said)
