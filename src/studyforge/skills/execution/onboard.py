r"""What a runnable corpus gets, and what a corpus that is not gets: nothing.

**What it does.** Joins one corpus's manifest with the pinned components'
contracts and produces the compose file, the toolchain selection, the prime and
the reader's document — or, for a corpus that declares no runtime, an empty
result and no error.

**How you use it.** `generate(manifest, …)` returns an `Execution`;
`write(execution, root)` puts it on disk; `NOT_MATERIAL` and `classified` are
what a manifest declares about it.

**Depends on.** `composefile`, `runnerservice`, `reader`, `prime`, `toolchain`,
`contract`, the manifest's own reader, and `corpus.placement` for where the
practice workspaces are. ⛔ Nothing source-specific (R1).

## ⛔ A CORPUS THAT DECLARES NO RUNTIME GETS NOTHING FROM HERE, AND NO ERROR

⭐ **`manifest.runtimes` is the whole test.** An absent key is `()` — no runner,
no editor, no prime — and §7's C5 says such a corpus is **complete at the
reading floor**, not short of something.

⛔ **So the result is empty: no path, no file, no warning, no stub.** A
generator that emitted a broken compose file rather than say *"your corpus
never asked for one"* would be the theatre R5 forbids, and it would put a
Docker dependency in front of somebody converting a book (spec §11.0).

## ⭐ WHICH DIRECTORY IS BOUND IS DERIVED, AND THE DERIVATION IS THE RULING

⚠️ **§8.1: only the sources are mounted — not the repository.** The
manifest carries no key naming the directory an editor binds, so it is derived
from `content.include`'s own common root, which is the corpus's own statement
about where its material lives.

⛔ **A corpus whose material is at the repository root is REFUSED**, because
there is then no directory to bind that is not the repository. ⚠️ **`SK-09/5`:
the remedy is a manifest key, and it is a finding rather than a default written
in here** (R19).

## ⭐ THE EDITOR SEES EVERY PRACTICE, AND THE RUNNER COMES UP WITH IT

⛔ **Every practice workspace — the source's own and every authored one — lives
under `PRACTICE_DIRNAME`**, which is not under the sources' common root, so a
generated editor that bound the sources alone could open no practice file.
⭐ So the editor binds that directory too, read from the one spelling `emit`
places workspaces by (`workspaces_bind`), and the sources stay where they were.
⭐ **The runner a Submit execs into is the file's second service**
(`runnerservice`), started by the reader's one compose command — never by the
serving process (§8.3) — from the tag `record` writes into `RUNNER_ENV`.

## ⭐ A SECOND INSTANCE, AND NO KEY IN THE EDITOR (`W465`)

⭐ `write` defaults the four values `INSTANCE_ENV` records and never overwrites
a recorded one (`instance.record_instance`); `binds.unkeyed` refuses any
editor bind that reaches a quiz's key.

## ⛔ RE-RUNNING CHANGES NOTHING, AND A HAND-EDIT IS REPORTED

⭐ The same manifest and contracts render the same bytes, so `write` is
idempotent (R10). ⛔ **A hand-edit to a file this writes is a finding, not a
fix** (R19): `written` records each file's digest, and onboarding's
`hand_edited` names the one whose bytes moved (`W466`).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.corpus.manifest import Manifest
from studyforge.corpus.placement import PRACTICE_DIRNAME
from studyforge.execute import instance
from studyforge.skills.execution import composefile, contract, reader, runnerservice, toolchain
from studyforge.skills.execution import written as record_of
from studyforge.skills.execution.binds import ExecutionRefused, source_root, unkeyed
from studyforge.skills.execution.prime import Prime, PrimeRefused, prime_for
from studyforge.skills.execution.toolchain import DIRECTORY_SLOT

#: Where everything this skill generates lives. ⭐ Under the corpus's own
#: bookkeeping directory, never beside its material: every byte here is
#: generated and R3 keeps the corpus's own files untouched.
DIRECTORY = ".studyforge/execution"

#: The compose file a reader brings up.
COMPOSE_FILE = f"{DIRECTORY}/compose.yaml"

#: The selection a corpus keeps: the set, what is carried, and the two argv.
TOOLCHAIN_FILE = f"{DIRECTORY}/toolchain.json"

#: The prime the build is handed: `<tool>/` per project (`W440`).
PRIME_DIR = f"{DIRECTORY}/prime"

#: The file the reader's compose command reads the runner's tag from, which the
#: skill's record step writes (`record.record_runner`).
RUNNER_ENV = f"{DIRECTORY}/runner.env"

#: The file the same command reads the editor's tag from, which the same step
#: writes (`record.record_editor`). ⭐ Beside the runner's and in its shape, so
#: the tag a site's editor runs is the corpus's record and not a person's memory.
EDITOR_ENV = f"{DIRECTORY}/editor.env"

#: The file the same command reads THIS instance's project, editor port and
#: container names from, which `serve` reads too (`execute.instance`).
INSTANCE_ENV = instance.INSTANCE_FILE

#: What a reader opens first.
READER_DOC = "EXECUTION.md"

#: ⛔ The sentence every generated document carries, so a file nobody may edit
#: says so itself. ⚠️ `write` refuses a reader's document that does not carry
#: it, which is how a hand-written one is never silently overwritten.
GENERATED = (
    "⛔ Generated by studyforge execution onboarding. A hand-edit here is a "
    "finding against that skill rather than a fix (R19); change corpus.json "
    "and regenerate."
)

#: Why none of this is material. ⚠️ Long enough to clear the manifest's own
#: minimum, because a reason the document refuses is a reason the integrator
#: has to invent — which is the retyping R19 forbids.
WHY_DIRECTORY = (
    "the compose file, the toolchain selection and the prime project this "
    "corpus's execution onboarding generated: how its material is run, never "
    "material it teaches."
)
WHY_READER = (
    "the execution report, written from this corpus's own declarations and "
    "from the pinned components' contracts, and regenerated rather than edited."
)

#: Every glob this skill's own output needs, with the reason each one gives.
NOT_MATERIAL = (
    {"glob": f"{DIRECTORY}/**", "why": WHY_DIRECTORY},
    {"glob": READER_DOC, "why": WHY_READER},
)


@dataclass(frozen=True, slots=True)
class Execution:
    """Everything a runnable corpus gets — or, for one that is not, nothing."""

    runnable: bool
    #: `(path, text)` for each generated document, in the order they are written.
    files: tuple[tuple[str, str], ...] = ()
    #: `(generated path, corpus-relative path)` for each file the prime copies.
    copies: tuple[tuple[str, str], ...] = ()
    selection: toolchain.Selection | None = None
    primed: Prime | None = None
    #: The runner's compose service and how its tag is computed.
    runner: runnerservice.Runner | None = None
    #: `(variable, default)` for each value `INSTANCE_ENV` records, in order.
    instance: tuple[tuple[str, str], ...] = ()

    def paths(self) -> tuple[str, ...]:
        """Every path this skill occupies, in the order it writes them."""
        return tuple([where for where, _ in self.files] + [where for where, _ in self.copies])


def generate(
    manifest: Manifest,
    *,
    editor_text: str,
    root: Path,
    narration_text: str | None = None,
    project: str | None = None,
) -> Execution:
    """Everything a runnable corpus gets, from manifest data and contracts alone."""
    if not manifest.runtimes:
        return Execution(runnable=False)
    editor = contract.read(
        editor_text,
        component=contract.EDITOR_COMPONENT,
        api=contract.EDITOR_API,
        promise=contract.EDITOR_PROMISE,
    )
    block = contract.require(editor, "editor")
    if not isinstance(block, Mapping):
        raise contract.ContractRefused("the contract's editor must be an object")
    selection = toolchain.select(manifest.runtimes, editor)
    sources = source_root(manifest)
    workspaces = workspaces_bind(block, sources)
    unkeyed(sources, *(() if workspaces is None else (workspaces[0],)))
    # ⭐ The prime is selected for what the image will CARRY, not for everything
    # the corpus declared: an image without a runtime cannot compile a specimen
    # in it, and the withheld ones are named in the reader's document instead.
    seeds = contract.optional(editor, "runner", "prime", "seeds", default={})
    seeded = tuple(seeds) if isinstance(seeds, Mapping) else ()
    primed = _primed(root, selection.carried, seeded)
    flag = _prime_flag(editor) if primed.projects else None
    editor_flag = selection.primed_by(f"<this corpus>/{PRIME_DIR}") if flag else None
    names = instance.defaults(manifest.source, port=composefile.per_project_port(block))
    names[instance.PROJECT] = project or names[instance.PROJECT]
    runner = runnerservice.plan(
        editor,
        source=manifest.source,
        root=_from_compose(""),
        runtimes=manifest.runtimes,
        runs_as=_runs_as(block),
        name_variable=instance.RUNNER_NAME,
    )
    names[instance.RUNNER_NAME] = runner.name
    compose = composefile.render(
        project=composefile.interpolated(instance.PROJECT, names[instance.PROJECT]),
        container_name=composefile.interpolated(instance.EDITOR_NAME, names[instance.EDITOR_NAME]),
        port_variable=instance.EDITOR_PORT,
        editor=block,
        image=selection.image_value,
        sources=_from_compose(sources),
        runtimes=manifest.runtimes,
        seeds=seeds if isinstance(seeds, Mapping) else None,
        checked=_checked(narration_text),
        binds=() if workspaces is None else ((_from_compose(workspaces[0]), workspaces[1]),),
        runner=(runnerservice.SERVICE, runner.service),
    )
    document = reader.document(
        manifest,
        generated=GENERATED,
        compose_file=COMPOSE_FILE,
        runner_env=RUNNER_ENV,
        editor_env=EDITOR_ENV,
        instance_env=INSTANCE_ENV,
        selection=selection,
        primed=primed,
        block=block,
        sources=sources,
        workspaces=None if workspaces is None else workspaces[0],
        runner=runner,
        narration_text=narration_text,
        seeds=seeds,
        flag=flag,
        editor_flag=editor_flag,
    )
    return Execution(
        runnable=True,
        files=(
            (COMPOSE_FILE, compose),
            (TOOLCHAIN_FILE, selection.render()),
            (READER_DOC, document),
        ),
        copies=tuple((f"{PRIME_DIR}/{inside}", origin) for inside, origin in primed.copies()),
        selection=selection,
        primed=primed,
        runner=runner,
        instance=tuple(names.items()),
    )


def workspaces_bind(block: Mapping[str, object], sources: str) -> tuple[str, str] | None:
    """Return `(corpus-relative dir, container path)` for the practice workspaces, or `None`.

    ⭐ **Read FROM where `emit` places them** — `PRACTICE_DIRNAME`, the one
    spelling `exercise.bundle.Places.workspace` and the adapter's own practices
    share — ⛔ never a second spelling of it. It sits inside the
    contract's workspace root, beside the sources, under its own name.
    ⭐ `None` when the sources already hold it: a second bind of what the first
    shows is two windows onto one directory.
    """
    if PurePosixPath(PRACTICE_DIRNAME).is_relative_to(PurePosixPath(sources)):
        return None
    root = contract.require(block, "workspace", "container_path")
    inside = f"{str(root).rstrip('/')}/{PRACTICE_DIRNAME}"
    taken = {str(entry.get("container_path")) for entry in contract.blocks(block, "mounts")}
    if inside in taken:
        raise ExecutionRefused(
            "the contract already mounts something where the practice workspaces would go, "
            "and this skill will not shadow it"
        )
    return PRACTICE_DIRNAME, inside


def write(execution: Execution, root: Path) -> tuple[str, ...]:
    """Write everything, and return what was written. ⭐ Re-running changes nothing."""
    written = []
    for where, text in execution.files:
        target = root / where
        if where == READER_DOC and _is_somebody_elses(target):
            raise ExecutionRefused(
                "this corpus already carries a reader's document that this skill did not "
                "write, and R3 keeps an existing file untouched. Move it aside, or say so "
                "and regenerate"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        written.append(where)
    for where, origin in execution.copies:
        target = root / where
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root / origin).read_bytes())
        written.append(where)
    if execution.runnable and not (root / INSTANCE_ENV).exists():
        made = instance.text(dict(execution.instance), header=f"# {GENERATED}\n")
        (root / INSTANCE_ENV).write_text(made, encoding="utf-8")
        written.append(INSTANCE_ENV)
    if written:
        record_of.stamp(root, written)
    return tuple(written)


def generated_here(root: Path, where: str) -> bool:
    """Whether `where` is this skill's own output at `root`, so R3 reads it as declared.

    ⭐ **The generated non-destructive check asks this**, so a regenerate that
    rewrote `READER_DOC` at the root is not an undeclared rewrite while it is
    uncommitted. ⛔ **A reader's document this skill did not write is not its
    output** — `write` refuses to overwrite one — so a rewrite of it is still
    somebody else's file changed, and the check still names it.
    """
    if not classified(where):
        return False
    return where != READER_DOC or not _is_somebody_elses(root / where)


def _is_somebody_elses(target: Path) -> bool:
    """Whether a reader's document already there is one this skill did not write."""
    return target.is_file() and GENERATED not in target.read_text(encoding="utf-8")


def classified(where: str, entries: Sequence[Mapping[str, str]] = NOT_MATERIAL) -> bool:
    """Whether one path is covered by a glob this module declares."""
    candidate = PurePosixPath(where)
    return any(candidate.full_match(entry["glob"]) for entry in entries)


def _checked(narration_text: str | None) -> tuple[tuple[str, Mapping[str, object]], ...]:
    """Return the narration block, whose rulings are asserted and never rendered."""
    if narration_text is None:
        return ()
    document = contract.read(
        narration_text,
        component=contract.NARRATION_COMPONENT,
        api=contract.NARRATION_API,
        promise=contract.NARRATION_PROMISE,
    )
    block = contract.require(document, "service")
    if not isinstance(block, Mapping):
        raise contract.ContractRefused("the contract's service must be an object")
    return ((contract.NARRATION_COMPONENT, block),)


def _primed(root: Path, runtimes: Sequence[str], seeded: Sequence[str]) -> Prime:
    """Select the prime, with the seeded set from the contract's own prime map."""
    try:
        return prime_for(root, runtimes, seeded=seeded)
    except PrimeRefused as refusal:
        raise ExecutionRefused(str(refusal)) from None


def _runs_as(block: Mapping[str, object]) -> Mapping[str, object]:
    """Return the editor's `runs_as`, which answers the runner's too (`runnerservice`)."""
    runs_as = contract.require(block, "runs_as")
    if not isinstance(runs_as, Mapping):
        raise contract.ContractRefused("the contract's editor.runs_as must be an object")
    return runs_as


def _prime_flag(editor: Mapping[str, object]) -> str:
    """Return the contract's own prime flag, with this corpus's directory in its slot."""
    flag = contract.require(editor, "runner", "prime", "declared_by")
    if not isinstance(flag, str) or DIRECTORY_SLOT not in flag:
        raise contract.ContractRefused(f"runner.prime.declared_by has no {DIRECTORY_SLOT} slot")
    return flag.replace(DIRECTORY_SLOT, f"<this corpus>/{PRIME_DIR}")


def _from_compose(sources: str) -> str:
    """Return `sources` as the compose file at `COMPOSE_FILE` reaches it; `""` is the root."""
    return "/".join([".."] * len(PurePosixPath(DIRECTORY).parts) + ([sources] if sources else []))
