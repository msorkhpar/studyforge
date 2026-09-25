r"""Build and serve: one invocation from a corpus to a running study site.

**What it does.** Runs the framework's registered verbs in order: `validate`,
`narrate` when a voice is given, `build`, then `serve`. It prints each verb's own
report and exits with the code of the first verb that fails. Once the site is
listening, it reports every honest partial state: what is missing, and what
still works.

**How you use it.** Through the skill document beside this file (`SKILL.md`),
which is the procedure:

    python3 -m studyforge.skills.buildserve <corpus-root> --out <directory>

    from studyforge.skills.buildserve import build_and_serve
    build_and_serve(root, out, voice=None, port=0, started=on_listening)

**Depends on.** `studyforge.cli` for the verb table, reached only through this
package's `verbs` module — the ONE seam that spells a verb's arguments, so a verb
whose interface changes is one edit there — `cli.plan.plan_for` for
whether a narration record exists, `cli.narrate.report` for the no-service
sentence, `cli.narrate.cli` for the loopback address the narration component
publishes on, `corpus.manifest` for whether exercises are declared, and
`validate.report` for the exit codes. ⛔ Not on `generate/`, `serve/` or
`narrate/`, and not on any adapter (R1).

## ⛔ Thin, or the finding is against the verbs

⭐ **Every file on disk is written by `studyforge build` and every socket is
opened by `studyforge serve` or `studyforge narrate`.** This package only
decides the order and reads the verbs' answers. If a step needed more than a
verb gives, the verb drew its surface wrong, and that is recorded as a finding
rather than patched here.

## ⛔ A partial state is a known state with a stated consequence, never an error

Narration not run, nothing to narrate, no narration service, no exercises and a
run that would execute on the host are each reported in `states` and never change
the exit code (R6, R8).
⭐ A corpus with no graders is complete at the reading floor, not short (C5).

## ⛔ SILENT IS NOT ONE STATE, AND *NOT FINISHED* IS SAID OUT LOUD

⚠️ A corpus that **has not** narrated and one that **cannot** are different
answers, and reporting both as the same partial state told an operator a
silent site was finished. ⭐ `states` separates them from the narration run's
own answer, and `narration` carries what provides narration, where it answers,
and the `provides` promise this framework's client was built against — so an
operator is told narration exists, rather than left to find out.
"""

from __future__ import annotations

from studyforge.skills.buildserve import narration
from studyforge.skills.buildserve.run import build_and_serve
from studyforge.skills.buildserve.states import (
    EXECUTION_NAMESPACE,
    HOST_EXECUTION,
    RUNNER_DOWN,
    KNOWN,
    NARRATION_INCOMPLETE,
    NO_EXERCISES,
    NO_NARRATION_SERVICE,
    NOT_NARRATED,
    NOTHING_TO_NARRATE,
    PartialState,
    exercise_states,
    narration_states,
    probe_for,
    recorded,
)

#: ⛔ The package's whole public surface.
__all__ = [
    "EXECUTION_NAMESPACE",
    "HOST_EXECUTION",
    "RUNNER_DOWN",
    "KNOWN",
    "NARRATION_INCOMPLETE",
    "NOTHING_TO_NARRATE",
    "NOT_NARRATED",
    "NO_EXERCISES",
    "NO_NARRATION_SERVICE",
    "PartialState",
    "build_and_serve",
    "exercise_states",
    "narration",
    "narration_states",
    "probe_for",
    "recorded",
]
