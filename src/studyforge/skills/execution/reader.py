r"""The reader's document, `EXECUTION.md`, written from declarations alone.

**What it does.** Says what a corpus declared, how to build both images, how
the runner's tag is recorded, the ONE compose command that brings the editor
and the runner up, and where narration comes from.

**How you use it.** `onboard.generate` calls `document(…)`; nothing else does.

**Depends on.** `composefile` for the two answers it repeats, `contract` for
narration's pointer. ⛔ No I/O and nothing source-specific (R1).

⭐ **Split out of `onboard` at this seam**: that module carried the
generation and this document in one file at the 400-line bound, and the
document is the half that grew.

## ⚠️ CORPUS-RELATIVE HERE, COMPOSE-RELATIVE IN THE FILE

This document sits at the corpus root and the compose file two directories
down, and a path a reader cannot act on from where they are reading is not a
remedy — so every path below is the corpus-relative one.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from studyforge.corpus.manifest import Manifest
from studyforge.skills.execution import composefile, contract, toolchain
from studyforge.skills.execution.prime import Prime
from studyforge.skills.execution.runnerservice import Runner


def document(
    manifest: Manifest,
    *,
    generated: str,
    compose_file: str,
    runner_env: str,
    selection: toolchain.Selection,
    primed: Prime,
    block: Mapping[str, object],
    sources: str,
    workspaces: str | None,
    runner: Runner,
    narration_text: str | None,
    seeds: object,
    flag: str | None,
) -> str:
    """Write the document a reader opens first, from declarations alone."""
    volumes = composefile.volumes_for(
        seeds if isinstance(seeds, Mapping) else None, manifest.runtimes
    )
    lines = [
        f"# Execution — {manifest.title}",
        "",
        generated,
        "",
        "## What this corpus declared",
        "",
        f"- runtimes: `{'`, `'.join(selection.declared)}`",
        f"- the directory the editor binds: `{sources}` — the sources alone (§8.1)",
    ]
    if workspaces is not None:
        lines.append(f"- the practice workspaces the editor binds too: `{workspaces}`")
    lines += [
        f"- the image the component builds: `{selection.image_env}`",
        f"- the runner a Submit runs in: `{runner.name}`, from `{runner.selection.image_env}`",
        "",
        "## Build the images",
        "",
        "From the component's checkout — the runner, then the editor:",
        "",
        "```",
        _with_prime(runner.selection.build, flag),
        " ".join(selection.build),
        " ".join(selection.tag_from),
        "```",
        "",
        "⛔ Never pin a tag you did not compute: a tag is a function of the build's",
        f"inputs. Read the set back from `{selection.read_back_from}`.",
        "",
        "## Record the runner's tag",
        "",
        f"⭐ The skill records it: its record step runs `{' '.join(runner.selection.tag_from)}`",
        f"with the prime above, in the pinned checkout, and writes `{runner_env}`.",
        "⛔ Never type it, and never edit that file: re-run the step when the",
        "component's pin, the prime or the host's architecture moves.",
        "",
        "## Bring it up",
        "",
        "```",
        f"docker compose --env-file {runner_env} -f {compose_file} up -d --wait",
        "```",
        "",
        "⛔ That one command starts the editor AND the runner. The study server never",
        "starts either and never holds the Docker socket (§8.3).",
        "",
    ]
    first = composefile.must_exist_first(
        block, volumes, sources, also=() if workspaces is None else (workspaces,)
    )
    if first:
        lines += [
            "⛔ These exist on the host before the start (§8.1), or docker",
            "creates them root-owned and the container can never write them:",
            "",
            *(f"- `{one}`" for one in first),
            "",
        ]
    if selection.withheld:
        lines += [
            "## What this editor does not carry",
            "",
            *(f"- `{name}` — {why}" for name, why in selection.withheld),
            "",
        ]
    lines += _prime(primed, flag)
    if narration_text is not None:
        lines += _narration(narration_text)
    return "\n".join(lines)


def _with_prime(build: Sequence[str], flag: str | None) -> str:
    """Return the runner's build argv as a line, with the prime flag when there is a prime."""
    return " ".join(build) + ("" if flag is None else f" {flag}")


def _prime(primed: Prime, flag: str | None) -> list[str]:
    """Say what the prime copies, and the flag both builds are handed."""
    lines = ["## The prime", ""]
    if flag is None:
        return [*lines, "No runtime this corpus declares is seeded from a build: no prime.", ""]
    return [
        *lines,
        "⛔ An empty prime primes nothing while appearing to succeed. These are this",
        "corpus's own files, one project per seeded tool, copied and never authored:",
        "",
        *(f"- `{inside}` ← `{origin}`" for inside, origin in primed.copies()),
        "",
        f"Pass `{flag}` to the builds above.",
        "",
    ]


def _narration(narration_text: str) -> list[str]:
    """Where narration comes from — by pointer, never by copying its API."""
    document = contract.read(
        narration_text,
        component=contract.NARRATION_COMPONENT,
        api=contract.NARRATION_API,
        promise=contract.NARRATION_PROMISE,
    )
    default = contract.require(document, "profiles", "default")
    files = contract.words(document, "profiles", str(default), "compose_files")
    return [
        "## Narration",
        "",
        f"⛔ Not rendered into this compose file. `{contract.NARRATION_COMPONENT}` is",
        "brought up from its own checkout, by its own compose files:",
        "",
        *(f"- `{one}`" for one in files),
        "",
        "⚠️ Its contract declares no per-project keys, so a consumer cannot render it",
        "without inventing a host port and a volume name.",
        "",
    ]
