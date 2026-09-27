r"""A second instance of one corpus on one host: its values, recorded by the skill.

**What it does.** Writes `INSTANCE_ENV` — the compose project, the editor's and
the study server's host ports and the three container names — for one checkout of a
corpus, each value checked. ⭐ Every value it is not handed keeps what the file
already holds, or the default when the file holds none.

⭐ **`INSTANCE_ENV` is the publisher's file.** This is the CHECKED way to change
it; setting a port there by hand is just as legitimate, is never a hand-edit
finding (`written.PUBLISHERS`), and a value that cannot work is refused by name
by `serve` and by the compose preflight (`execute.instance.problems`).

**How you use it.** After `onboard.write` (which records the defaults when
nothing is recorded yet), a checkout that must run BESIDE another records its
own:

    record_instance(execution, root, project="studyforge-iso-second",
                    port=18443, editor="iso-second-editor", runner="iso-second-runner",
                    site_port=18444, site="iso-second-site")

Then the corpus's one compose command, as `EXECUTION.md` prints it, brings that
checkout's containers up under its own names and port, and `serve` over that
checkout finds them by the same file (`execute.instance.recorded`).

**Depends on.** `onboard` for the paths, the plan and the generated sentence;
`execute.instance` for the variables, their checks and the bytes. ⛔ Nothing
source-specific (R1), and no process.

## ⛔ WHY IT IS RECORDED RATHER THAN TYPED ON A COMMAND LINE

⭐ **Two readers need the same values** — compose, which interpolates
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
    site_port: int | None = None,
    site: str | None = None,
) -> str:
    """Record this checkout's values under `root`, and return the path written."""
    if not execution.runnable or not execution.instance:
        raise ExecutionRefused("this corpus declares no runtime, so there is no instance to record")
    # ⭐ The publisher's file: what it already holds is kept, and only what is handed changes.
    values = {**dict(execution.instance), **instance.read(root)}
    chosen = {
        instance.PROJECT: project,
        instance.EDITOR_PORT: None if port is None else str(port),
        instance.EDITOR_NAME: editor,
        instance.RUNNER_NAME: runner,
        instance.SITE_PORT: None if site_port is None else str(site_port),
        instance.SITE_NAME: site,
    }
    values.update({one: value for one, value in chosen.items() if value is not None})
    try:
        made = instance.text(values, header=instance.PUBLISHER_HEADER)
    except RunRefused as refusal:
        raise ExecutionRefused(str(refusal)) from None
    target = root / INSTANCE_ENV
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(made, encoding="utf-8", newline="\n")
    # ⭐ The publisher's file is never recorded as the skill's (`written.PUBLISHERS`);
    # the stamp only drops an entry an older record kept for it.
    written.stamp(root, [INSTANCE_ENV])
    return INSTANCE_ENV
