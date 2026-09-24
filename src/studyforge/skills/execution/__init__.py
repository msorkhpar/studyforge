r"""Execution onboarding — what a corpus with runnable material gets, and only it.

**What it does.** Generates the compose file, the toolchain selection and the
prime project for a corpus whose manifest declares runtimes, from that manifest
and the pinned components' own consuming contracts. ⛔ **A corpus that declares
none gets nothing from this skill and no error.**

**How you use it.** Through `SKILL.md` beside this file, which is the procedure.
In code:

    from studyforge.skills.execution import generate, write

    made = generate(manifest, editor_text=..., root=corpus)
    if made.runnable:
        write(made, corpus)

**Depends on.** `corpus.manifest` for the declarations, `archive.scrub` for
R7's gate. ⛔ Not on Docker, not on a YAML library, not on any adapter (R1),
and on nothing inside either component but its `consuming.json` (R18).

| module | what it owns |
|---|---|
| `contract` | one component's `consuming.json`, read — and the refusal that is a finding |
| `toolchain` | which runtimes an image carries, and the two commands for it |
| `rulings` | spec §8.1's four compose rules and §8.3's, asserted against a block |
| `emit` | the smallest deterministic YAML a generated compose file needs |
| `composefile` | one contract block to one compose service, and the file around it |
| `runnerservice` | the runner a Submit execs into, as the compose file's second service |
| `reader` | the reader's document, `EXECUTION.md` |
| `record` | the runner's and the editor's tags, asked of the component and written for compose |
| `written` | every file this skill wrote and its digest, so a hand-edit to one is reported |
| `prime` | the corpus's own build, source and test, as one project per seeded tool |
| `binds` | which directories the editor binds, and the keyed ones it never may |
| `instance` | this checkout's project, editor port and container names, recorded |
| `onboard` | the whole of it, and the empty answer for a corpus that is not runnable |

## ⛔ SEPARATED FROM ONBOARDING, AND THE SEPARATION IS THE POINT

⭐ **The reading floor is what every corpus gets** — narrated, navigable,
offline, no server — and it is a complete product for prose material (spec
§11.0). ⛔ **A container is what a corpus with runnable code earns.** Folding
this into `skills.onboarding` would put a Docker dependency in front of
somebody converting a book, and §7's C5 already says a corpus with no runnable
unit is **complete**, not short.

## ⭐ THIS IS WHERE `consuming.json`'s SUFFICIENCY IS DEMONSTRATED

⛔ `E12`'s `TC-05` says a component's consuming contract is **sufficient** to
generate a working compose file with no other input. ⭐ **This package is where
that is demonstrated rather than asserted** — so a key it needs and the
contract does not carry is a **finding against that component**, raised by
`contract.require` and never answered by a value written in here (R19).
"""

from studyforge.skills.execution.composefile import ComposeRefused, must_exist_first, render
from studyforge.skills.execution.contract import (
    CONSUMING,
    EDITOR_API,
    EDITOR_COMPONENT,
    EDITOR_PROMISE,
    NARRATION_API,
    NARRATION_COMPONENT,
    NARRATION_PROMISE,
    ContractRefused,
    read,
)
from studyforge.skills.execution.instance import record_instance
from studyforge.skills.execution.onboard import (
    COMPOSE_FILE,
    DIRECTORY,
    EDITOR_ENV,
    GENERATED,
    INSTANCE_ENV,
    NOT_MATERIAL,
    PRIME_DIR,
    READER_DOC,
    RUNNER_ENV,
    TOOLCHAIN_FILE,
    Execution,
    ExecutionRefused,
    classified,
    generate,
    generated_here,
    source_root,
    workspaces_bind,
    write,
)
from studyforge.skills.execution.prime import Prime, PrimeRefused, Project, Specimen, prime_for
from studyforge.skills.execution.record import record_editor, record_runner
from studyforge.skills.execution.rulings import findings
from studyforge.skills.execution.runnerservice import Runner, RunnerRefused
from studyforge.skills.execution.toolchain import Selection, select

__all__ = [
    "COMPOSE_FILE",
    "CONSUMING",
    "DIRECTORY",
    "EDITOR_API",
    "EDITOR_ENV",
    "EDITOR_COMPONENT",
    "EDITOR_PROMISE",
    "GENERATED",
    "INSTANCE_ENV",
    "NARRATION_API",
    "NARRATION_COMPONENT",
    "NARRATION_PROMISE",
    "NOT_MATERIAL",
    "PRIME_DIR",
    "READER_DOC",
    "RUNNER_ENV",
    "TOOLCHAIN_FILE",
    "ComposeRefused",
    "ContractRefused",
    "Execution",
    "ExecutionRefused",
    "Prime",
    "PrimeRefused",
    "Project",
    "Runner",
    "RunnerRefused",
    "Selection",
    "Specimen",
    "classified",
    "findings",
    "generate",
    "generated_here",
    "must_exist_first",
    "prime_for",
    "read",
    "record_editor",
    "record_instance",
    "record_runner",
    "render",
    "select",
    "source_root",
    "workspaces_bind",
    "write",
]
