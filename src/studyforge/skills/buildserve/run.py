r"""The one invocation: validate, narrate, build, serve, each through its registered verb.

**What it does.** Calls each verb through `studyforge.cli.VERBS`, prints its
report followed by a `step <verb> exit <code>` line, and stops at the first verb
that fails. When the site is listening, it prints the partial states. It then
serves until stopped.

**How you use it.**

    code = build_and_serve(root, out, voice=None, service=None, port=0,
                           stream=None, started=None)

`started(server)` is called once the site is listening and before it serves,
which is how a test sends a real request and stops it.

**Depends on.** `studyforge.cli.VERBS`, `cli.plan.plan_for`, `corpus.manifest`,
`validate.report`, and this package's `states`.

## ⛔ Thin: no step here re-implements a verb

⭐ `validate`, `narrate`, `build` and `serve` are the registered callables, reached
by name from the one table. This module opens no file and no socket. It reads the
plan and the manifest only to know which partial state holds.
"""

from __future__ import annotations

import io
import sys
from collections.abc import Callable
from pathlib import Path

from studyforge.cli import VERBS
from studyforge.cli.plan import plan_for
from studyforge.corpus.manifest import MANIFEST_FILENAME, load
from studyforge.skills.buildserve.states import exercise_states, narration_states, recorded
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
    code, _ = _step(["validate", corpus], say)
    if code != OK:
        return code
    narrated = None
    said = ""
    if voice is not None:
        asked = ["narrate", corpus, "--voice", voice]
        narrated, said = _step(asked + (["--service", service] if service else []), say)
    code, _ = _step(["build", corpus, "--out", site], say)
    if code != OK:
        return code
    states = narration_states(narrated, said, has_record=recorded(plan_for(Path(corpus))))
    declared = load(Path(corpus) / MANIFEST_FILENAME).exercises

    def listening(server: object) -> None:
        offered = getattr(server, "namespaces", {})
        for state in states + exercise_states(declared, offered):
            for line in state.lines():
                say(line)
        if started is not None:
            started(server)

    served = [corpus, "--site", site] + ([] if port is None else ["--port", str(port)])
    code = VERBS["serve"].run(served, out=target, started=listening)
    say(f"step serve exit {code}")
    return code


def _step(argv: list[str], say: Callable[[str], None]) -> tuple[int, str]:
    """Run one registered verb, print its report and its exit code, return both."""
    captured = io.StringIO()
    code = VERBS[argv[0]].run(argv[1:], out=captured)
    said = captured.getvalue()
    for line in said.splitlines():
        say(line)
    say(f"step {argv[0]} exit {code}")
    return code, said
