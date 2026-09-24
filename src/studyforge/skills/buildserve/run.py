r"""The one invocation: validate, narrate, build, serve, each through its registered verb.

**What it does.** Hands each verb its arguments through `verbs`, prints the verb's
report followed by a `step <verb> exit <code>` line, and stops at the first verb
that fails. When the site is listening, it prints the partial states. It then
serves until stopped.

**How you use it.**

    code = build_and_serve(root, out, voice=None, service=None, port=0,
                           narration=None, stream=None, started=None)

`started(server)` is called once the site is listening and before it serves,
which is how a test sends a real request and stops it.

**Depends on.** this package's `verbs` (the one seam onto the verbs) and `states`,
`cli.plan.plan_for`, `corpus.manifest`, `validate.report` and `validate.cli` for
the exit code of a run that cannot start.

## ⭐ Narration is the user's to choose, and off is not a partial state (`W460`)

⭐ The user's ruling, 2026-09-23: *"while serving or even while caputring the
matterial skills should ask if user is interested in the narrition or not"*.
`narration` is that answer, handed to `build` and `serve` as their own flag.
⛔ **Off prints no `partial` block**: the reading floor is complete (C5), so the
skill says once that narration is off and what it kept, and nothing calls it
short. ⛔ A `--voice` with narration off is refused before anything runs: it
would synthesise clips this run has been asked not to serve.

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
from studyforge.narrate import narration_on
from studyforge.skills.buildserve import verbs
from studyforge.skills.buildserve.states import (
    NARRATION_OFF,
    VOICE_UNHEARD,
    exercise_states,
    narration_states,
    probe_for,
    recorded,
)
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import OK


def build_and_serve(
    root: Path | str,
    out: Path | str,
    *,
    voice: str | None = None,
    service: str | None = None,
    port: int | None = None,
    narration: bool | None = None,
    stream=None,
    started: Callable[[object], None] | None = None,
) -> int:
    """Validate, narrate if asked, build and serve one corpus; return the exit code.

    ⭐ `narration` is the user's answer for this run (`W460`): `False` builds and
    serves the reading floor with every clip kept on disk, `True` voices a corpus
    whose `corpus.json` says no, and `None` keeps what `corpus.json` says.
    """
    target = sys.stdout if stream is None else stream

    def say(line: str) -> None:
        print(line, file=target, flush=True)

    corpus, site = str(root), str(out)
    # ⛔ `W457`: asked to narrate, the run re-makes every clip whose words moved, so
    # a stale clip is not a reason to stop before that; `narrate` reports what it could not.
    # ⭐ `W460`: a run the user asked to leave narration out judges no clip either.
    quiet = voice is not None or narration is False
    code, _ = _step(verbs.validate(corpus, narration=False if quiet else None), say)
    if code != OK:
        return code
    manifest = load(Path(corpus) / MANIFEST_FILENAME)
    speaks = narration_on(corpus, asked=narration)
    if voice is not None and not speaks:
        say(VOICE_UNHEARD)
        return UNUSABLE
    narrated = None
    said = ""
    if voice is not None:
        narrated, said = _step(verbs.narrate(corpus, voice, service), say)
    code, _ = _step(verbs.build(corpus, site, narration), say)
    if code != OK:
        return code
    states = (
        narration_states(narrated, said, has_record=recorded(plan_for(Path(corpus))))
        if speaks
        else ()
    )
    probe = probe_for(corpus, manifest.source)

    def listening(server: object) -> None:
        offered = getattr(server, "namespaces", {})
        if not speaks:
            say(NARRATION_OFF)
        for state in states + exercise_states(manifest.exercises, offered, probe):
            for line in state.lines():
                say(line)
        if started is not None:
            started(server)

    served = verbs.serve(corpus, site, port, narration)
    code = verbs.call(served, target, started=listening)
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
