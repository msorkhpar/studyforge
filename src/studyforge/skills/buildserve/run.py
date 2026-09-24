r"""The one invocation: validate, narrate, build, serve, each through its registered verb.

**What it does.** Hands each verb its arguments through `verbs`, prints the verb's
report followed by a `step <verb> exit <code>` line, and stops at the first verb
that fails. When the site is listening, it prints the partial states. It then
serves until stopped.

**How you use it.**

    code = build_and_serve(root, out, voice=None, service=None, port=0,
                           stream=None, started=None)

`started(server)` is called once the site is listening and before it serves,
which is how a test sends a real request and stops it.

**Depends on.** this package's `verbs` (the one seam onto the verbs) and `states`,
`cli.plan.plan_for`, `corpus.manifest` and `validate.report`.

## ⛔ Thin: no step here re-implements a verb, or spells one's arguments

⭐ This module opens no file and no socket, and names no verb flag: every argument
list comes from `verbs`, so a verb whose interface changes (`W230`) is one edit
there. It reads the plan and the manifest only to know which partial state holds, and
hands `states` the probe that says where a run would execute (`W381`).
"""

from __future__ import annotations

import io
import sys
from collections.abc import Callable
from pathlib import Path

from studyforge.cli.plan import plan_for
from studyforge.corpus.manifest import MANIFEST_FILENAME, load
from studyforge.skills.buildserve import verbs
from studyforge.skills.buildserve.states import (
    exercise_states,
    narration_states,
    probe_for,
    recorded,
)
from studyforge.validate.report import OK


def build_and_serve(
    root: Path | str,
    out: Path | str,
    *,
    voice: str | None = None,
    service: str | None = None,
    port: int | None = None,
    stream=None,
    started: Callable[[object], None] | None = None,
) -> int:
    """Validate, narrate if asked, build and serve one corpus; return the exit code."""
    target = sys.stdout if stream is None else stream

    def say(line: str) -> None:
        print(line, file=target, flush=True)

    corpus, site = str(root), str(out)
    # ⛔ `W457`: asked to narrate, the run re-makes every clip whose words moved, so
    # a stale clip is not a reason to stop before that; `narrate` reports what it could not.
    code, _ = _step(verbs.validate(corpus, narration=False if voice is not None else None), say)
    if code != OK:
        return code
    narrated = None
    said = ""
    if voice is not None:
        narrated, said = _step(verbs.narrate(corpus, voice, service), say)
    code, _ = _step(verbs.build(corpus, site), say)
    if code != OK:
        return code
    states = narration_states(narrated, said, has_record=recorded(plan_for(Path(corpus))))
    manifest = load(Path(corpus) / MANIFEST_FILENAME)
    probe = probe_for(corpus, manifest.source)

    def listening(server: object) -> None:
        offered = getattr(server, "namespaces", {})
        for state in states + exercise_states(manifest.exercises, offered, probe):
            for line in state.lines():
                say(line)
        if started is not None:
            started(server)

    code = verbs.call(verbs.serve(corpus, site, port), target, started=listening)
    say(f"step serve exit {code}")
    return code


def _step(argv: list[str], say: Callable[[str], None]) -> tuple[int, str]:
    """Run one verb through the seam, print its report and its exit code, return both."""
    captured = io.StringIO()
    code = verbs.call(argv, captured)
    said = captured.getvalue()
    for line in said.splitlines():
        say(line)
    say(f"step {argv[0]} exit {code}")
    return code, said
