r"""A second instance of one corpus on one host: its four values, recorded by the skill.

**What it does.** Writes `INSTANCE_ENV` — the compose project, the editor's host
port and the editor's and the runner's container names — for one checkout of a
corpus, each value checked, every one it is not handed kept at the value the
corpus has always used.

**How you use it.** After `onboard.write` (which records the defaults when
nothing is recorded yet), a checkout that must run BESIDE another records its
own four:

    record_instance(execution, root, project="studyforge-iso-second",
                    port=18443, editor="iso-second-editor", runner="iso-second-runner")

Then the corpus's one compose command, as `EXECUTION.md` prints it, brings that
checkout's containers up under its own names and port, and `serve` over that
checkout finds them by the same file (`execute.instance.recorded`).

**Depends on.** `onboard` for the paths, the plan and the generated sentence;
`execute.instance` for the variables, their checks and the bytes. ⛔ Nothing
source-specific (R1), and no process.

## ⛔ WHY IT IS RECORDED RATHER THAN TYPED ON A COMMAND LINE

⭐ **Two readers need the same four values** — compose, which interpolates
them, and `serve`, which probes and execs into the containers they name. A
value typed into one command reaches the first and not the second, which would
leave a second runner that `serve` cannot be pointed at. ⭐ One file both read cannot come apart.

## ⛔ THE BIND IS NOT A VALUE

⛔ **Only the PORT is recorded.** The compose file writes the contract's
loopback address literally beside it, and `execute.instance.checked` refuses a
port that is not a whole number in its range — so no recorded value can widen
the editor's bind, which is the whole of its access control.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.execute import instance
from studyforge.execute.errors import RunRefused
from studyforge.skills.execution import written
from studyforge.skills.execution.onboard import (
    GENERATED,
    INSTANCE_ENV,
    Execution,
    ExecutionRefused,
)


def record_instance(
    execution: Execution,
    root: Path,
    *,
    project: str | None = None,
    port: int | None = None,
    editor: str | None = None,
    runner: str | None = None,
) -> str:
    """Record this checkout's four values under `root`, and return the path written."""
    if not execution.runnable or not execution.instance:
        raise ExecutionRefused("this corpus declares no runtime, so there is no instance to record")
    values = dict(execution.instance)
    chosen = {
        instance.PROJECT: project,
        instance.EDITOR_PORT: None if port is None else str(port),
        instance.EDITOR_NAME: editor,
        instance.RUNNER_NAME: runner,
    }
    values.update({one: value for one, value in chosen.items() if value is not None})
    try:
        made = instance.text(values, header=f"# {GENERATED}\n")
    except RunRefused as refusal:
        raise ExecutionRefused(str(refusal)) from None
    target = root / INSTANCE_ENV
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(made, encoding="utf-8")
    # ⭐ Stamped as `record_runner` stamps its file: a value recorded
    # here is the skill's own write, so the hand-edit check does not name it.
    written.stamp(root, [INSTANCE_ENV])
    return INSTANCE_ENV
