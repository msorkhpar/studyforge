r"""The reader's document, `EXECUTION.md`, written from declarations alone.

**What it does.** Says what a corpus declared, how to build both images, how
both tags are recorded, the ONE compose command that brings the editor and the
runner up from them, and where narration comes from.

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
    editor_env: str,
    instance_env: str,
    site_env: str,
    selection: toolchain.Selection,
    primed: Prime,
    block: Mapping[str, object],
    sources: str,
    workspaces: str | None,
    runner: Runner,
    code: str | None = None,
    narration_text: str | None,
    seeds: object,
    flag: str | None,
    editor_flag: str | None = None,
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
    also = tuple(one for one in (workspaces, code) if one is not None and one != sources)
    if code is not None:
        lines.append(
            f"- the copy of the corpus's code, which a lesson's code links open and a "
            f"test runs in, so the author's files are never written: `{code}`"
        )
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
        _with_prime(selection.build, editor_flag),
        _with_prime(selection.tag_from, editor_flag),
        "```",
        "",
        "⛔ Never pin a tag you did not compute: a tag is a function of the build's",
        f"inputs. Read the set back from `{selection.read_back_from}`.",
        "",
        "## Record both tags",
        "",
        f"⭐ The skill records them: its record step runs `{' '.join(runner.selection.tag_from)}`",
        f"with the prime above, in the pinned checkout, and writes `{runner_env}`;",
        f"then `{' '.join(selection.tag_from)}`"
        f"{' with the same prime' if editor_flag else ''}, and writes `{editor_env}`.",
        "⛔ Never type a tag, and never edit either file: re-run the step when the",
        "component's pin, the prime or the host's architecture moves.",
        "",
        "## Stage the study server's image",
        "",
        "⭐ The skill's site step (`siteimage.stage_site`) checks the installed library is",
        f"the one this corpus pinned, stages it with its build file, writes `{site_env}`",
        "and hands back the one build to run, from this corpus's root:",
        "",
        "```",
        "docker build --file .studyforge/execution/site/site.containerfile --tag "
        f"\"$(sed -n 's/^STUDYFORGE_SITE_IMAGE=//p' {site_env})\" .studyforge/execution/site",
        "```",
        "",
        "## Bring it up",
        "",
        "```",
        f"docker compose --env-file {runner_env} --env-file {editor_env} "
        f"--env-file {instance_env} --env-file {site_env} -f {compose_file} up -d --wait",
        "```",
        "",
        "⛔ That one command starts the study server, the editor AND the runner, each",
        "from the tag the corpus recorded; before the site's image is staged it starts",
        "the editor and the runner alone. The study server reaches the runner over",
        "the compose network's internal side, which the runner publishes no port on,",
        "and never holds the Docker socket (§8.3).",
        "",
        f"⭐ `{instance_env}` is the one place a port is set: the study server's, the",
        "editor's, the compose project and the container names. Change one there and",
        "bring it up again; a page learns the editor's address from the study server,",
        "never from a built file. A second checkout on one host records its own with",
        "the skill's record step, and runs beside this one.",
        "",
        "⛔ Every port is published on 127.0.0.1 alone. The editor has no password",
        "because loopback is its whole access control: widening either bind means",
        "restoring the editor's authentication first.",
        "",
        "⭐ Serving on the host instead (`studyforge serve <root>`) stays the",
        "development path: it finds the editor and the runner by the same file.",
        "",
    ]
    first = composefile.must_exist_first(block, volumes, sources, also=also)
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
    lines += _prime(primed, flag, editor_flag)
    if narration_text is not None:
        lines += _narration(narration_text)
    return "\n".join(lines)


def _with_prime(build: Sequence[str], flag: str | None) -> str:
    """Return one build argv as a line, with its prime flag when it is handed a prime."""
    return " ".join(build) + ("" if flag is None else f" {flag}")


def _prime(primed: Prime, flag: str | None, editor_flag: str | None) -> list[str]:
    """Say what the prime copies, and exactly which of the lines above carry its flag."""
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
        *_carried(flag, editor_flag),
        "",
    ]


def _carried(flag: str, editor_flag: str | None) -> list[str]:
    """Say which printed lines carry the prime, so the sentence matches the block."""
    if editor_flag is None:
        return [
            f"The runner's build above carries `{flag}`. The component's contract declares",
            "no prime for the editor, so the editor is built, and its tag asked, unprimed.",
        ]
    if editor_flag == flag:
        return [
            f"All three lines above carry `{flag}`: the runner's build, the editor's",
            "build and the editor's tag command. One prime warms both images.",
        ]
    return [
        f"The runner's build above carries `{flag}`; the editor's build and its tag",
        f"command carry `{editor_flag}`.",
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
