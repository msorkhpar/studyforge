"""The command runner — the only package in the framework that runs a corpus's commands.

**What it does.** Runs a corpus's commands — a unit's run and test commands,
read from its generated document — inside the corpus's runner container when
the reader has it up, and on the host otherwise, streaming the merged output
line by line and ending with exactly one exit line.

**How you use it.**

    from studyforge.execute import Runner, container_for

    runner = Runner(source_root, container_for(source))
    handle = runner.start([exercise.run_command, exercise.test_command])
    for line in handle.lines():  # ... and last, "--- exit 0 ---"
        ...

`handle.stop()` ends a run from another thread. A refused input raises
`RunRefused`; a command that runs and fails is output, never an exception.

**Depends on.** The standard library, `studyforge.exercise` for what a command
and a path may be, and `studyforge.archive`'s `scrub` for R7. ⛔ Not on `serve`:
the direction is serve-depends-on-execute, and inverting it is how the
web-facing process ends up holding the socket that spec §8.3 forbids it.

| module | what it owns |
|---|---|
| `runner` | `Runner`, the two modes' launchers, and the run's environment |
| `handle` | `RunHandle`: the sequence, the stream, the exit line, stop and timeout |
| `mode` | `ModeProbe`: is the runner container up over this root, cached briefly |
| `output` | `LineGate`: every line relative to the source root, then scrubbed |
| `commands` | what the runner will start, checked before any process exists |
| `errors` | `RunRefused`, the one exception |

## The ruled seam (round 112, on `TC-00`'s answer 6)

⭐ **The READER starts the runner container** with `code-server-toolchain`'s
documented run line — the source root alone at `/work`, `--network none`, no
port, no socket. ⭐ **This package PROBES that it is up and runs
`docker exec -w /work/<cwd>` with the command's argv VERBATIM; not up means
HOST mode, the same argv.** ⛔ It never starts, stops or builds a container, and
⛔ **the Docker socket is never mounted into the serving process** (§8.3) — not
behind a flag, not "only locally".

⭐ **Both modes are one contract** — the same argv, the same directory relative
to the source root, the same environment, output relative to the source root in
both — so a run from a page and a run from the reader's own terminal (`SF-44`)
agree. `runner`'s docstring is the table.

⚠️ **Reproducibility comes from the image, not the host** (R15). Host mode is
the honest fallback, not an equal: it runs whatever toolchain the host has.

⚠️ **Raw build output is not reader output.** Filtering it down to what the
reader asked for is `SF-29`'s, on top of this stream.
"""

from __future__ import annotations

from studyforge.execute.commands import (
    CONTAINER_PREFIX,
    ROOT_DIR,
    container_for,
    require_commands,
    require_container,
    require_workdir,
)
from studyforge.execute.errors import RunRefused
from studyforge.execute.handle import EXIT_STOPPED, EXIT_TIMEOUT, RunHandle, exit_line
from studyforge.execute.mode import CONTAINER, HOST, MODES, WORKDIR_IN_CONTAINER, ModeProbe
from studyforge.execute.output import LineGate
from studyforge.execute.runner import RUN_ENVIRONMENT, Runner

__all__ = [
    "CONTAINER",
    "CONTAINER_PREFIX",
    "EXIT_STOPPED",
    "EXIT_TIMEOUT",
    "HOST",
    "MODES",
    "ROOT_DIR",
    "RUN_ENVIRONMENT",
    "WORKDIR_IN_CONTAINER",
    "LineGate",
    "ModeProbe",
    "RunHandle",
    "RunRefused",
    "Runner",
    "container_for",
    "exit_line",
    "require_commands",
    "require_container",
    "require_workdir",
]
