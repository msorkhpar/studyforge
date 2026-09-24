"""One environment, one identifier: the build exports no provenance.

⛔ **A fourth module under `tests/docker/` rather than a section of an existing
one, and R11 is half the reason.** `test_dev_image.py` stands at 586 lines
against a 600-line ceiling for tests. ⭐ The other half is the seam: these checks
have one subject — *can two offices holding the same environment quote the same
thing about it* — which is not the subject of any of the three neighbours.

## ⛔ The defect these exist over

⚠️ `docker/dev/check` passes `--build` on every invocation, deliberately: a stale
image is a result attributed to a version of the environment nobody can name.
⛔ But BuildKit exports **four** digests and stamps **two** of them with
build-time provenance, so byte-identical contents produce a fresh attestation
manifest — and a fresh manifest list indexing it — every single time.

```text
MEASURED on this branch, three `docker/dev/check` invocations, `docker/dev/`
untouched, every build step CACHED, on the HOST in the dev2 worktree:

  with the wrapper's line ABSENT            with it PRESENT
    exporting config       IDENTICAL 3/3      exporting config     IDENTICAL 3/3
    exporting manifest     IDENTICAL 3/3      exporting manifest   IDENTICAL 3/3
    exporting attestation manifest  3 DISTINCT    (not exported at all)
    exporting manifest list         3 DISTINCT    (not exported at all)
```

⛔ **And `docker image inspect --format '{{.Id}}'` reports the manifest LIST** —
the worst of the four and the first one an office reaches for. Two offices then
read different shas for one identical environment, and a reviewer comparing them
reads a difference where there is none — a false refutation — and this module
is its repair, enforced by the build rather than remembered by a reader.

## ⭐ THE PINS STILL PIN

⛔ **An environment is still named by its pins, and that must not change** —
`Dockerfile`'s `FROM` digest, its two toolchain `ARG`s, every `==`
in `requirements.txt`. ⭐ What changes is that the exported config digest becomes
**quotable** across offices instead of dead text; it never becomes authoritative.

## ⚠️ Why the last check is opt-in and the rest are not

⭐ The static half reads text and runs everywhere — host, container, any
checkout — and **each positive assertion is paired with a control that feeds the
same predicate a doctored copy and requires it to say no**, so no check in here
is dark. ⛔ The one check that actually builds twice and compares
what came out is gated on `STUDYFORGE_DOCKER_TESTS=1` and on not already being
inside the image, for `test_dev_image.py`'s reasons: the build needs the network,
and without the recursion guard the suite would build a container to run the
suite that builds a container.
"""

from __future__ import annotations

import re

from tests.docker.devfiles import DEV, instructions, read
from tests.docker.devgate import require_docker_run
from tests.support import repository_root, run

#: ⛔ buildx's own switch for "export no default attestations". Set by the
#: wrapper for the docker CLIENT; it never crosses into the container.
VARIABLE = "BUILDX_NO_DEFAULT_ATTESTATIONS"

#: ⭐ The two digests that are stable across byte-identical builds, and the two
#: that are not. ⚠️ Ordered longest-first because `manifest` is a prefix of
#: neither but a SUBSTRING of both of the others — an alternation in the other
#: order would match `manifest` inside `manifest list` and misfile it.
EXPORT_KINDS = ("attestation manifest", "manifest list", "manifest", "config")

STABLE = ("config", "manifest")
PROVENANCE_BEARING = ("attestation manifest", "manifest list")

_EXPORTING = re.compile(
    r"exporting (" + "|".join(EXPORT_KINDS) + r") (sha256:[0-9a-f]{64})",
)


# --- the predicates, so every one of them can be shown to bite --------------


def joined(script: str) -> str:
    """`script` with backslash continuations collapsed, one element per LOGICAL line.

    ⛔ **The name is `test_dev_continuations.py`'s vocabulary and is deliberate.**
    That module classifies a decomposition site by the reader it goes through, and
    `joined` is one of the two names it accepts as a collapse — so every site below
    is `collapsed` by a mechanical check rather than by a comment claiming it.

    ⚠️ It earns its keep twice over. `docker/dev/check` continues its Compose
    invocation across three physical lines, so an ordering test that split raw lines
    would compare against a fragment; and `compose.yaml`'s header documents the
    direct invocation as a variable on one comment line and the command on the next,
    which is the shape a reader copies and the shape a raw split cannot see whole.
    """
    return script.replace("\\\n", " ")


def assigned_value(script: str) -> str | None:
    """The value `script` assigns to the variable, or `None` if it assigns none.

    ⛔ A function over TEXT rather than an assertion over the real file, so the
    control below can hand it a doctored copy and require a `None`. A predicate
    that only ever sees the right answer has never been shown to have a wrong one.
    """
    values = [
        line.strip().split("=", 1)[1]
        for line in joined(script).splitlines()
        if line.strip().startswith(f"{VARIABLE}=")
    ]
    return values[0] if len(values) == 1 else None


def exports_the_variable(script: str) -> bool:
    """Does `script` export it, rather than leaving it to its own shell?"""
    return any(
        line.strip().startswith("export ") and VARIABLE in line.split()
        for line in joined(script).splitlines()
    )


def set_before_the_build(script: str) -> bool:
    """Is it set before the Compose invocation that consumes it?

    ⚠️ Ordering is not cosmetic here: `exec` replaces the shell, so anything set
    after the Compose line is set in a shell that no longer exists.
    """
    lines = [line.strip() for line in joined(script).splitlines()]
    assignment = [i for i, line in enumerate(lines) if line.startswith(f"{VARIABLE}=")]
    compose = [i for i, line in enumerate(lines) if "docker compose" in line]
    return bool(assignment) and bool(compose) and max(assignment) < min(compose)


def declares_the_inert_key(compose: str) -> bool:
    """Does `compose.yaml` carry a `provenance:` build key?

    ⛔ It is INERT on this Docker — Compose v5.2.0 / buildx v0.35.0, measured
    through `run --build`, plain `build` and `COMPOSE_BAKE=true`, the attestation
    exported and moving every time. ⚠️ So shipping it would be a decoration that
    READS like the fix, and the next office would compare tag ids believing the
    problem solved. Compose does not reject the key, so nothing but this stands
    between the tree and that.

    ⭐ A line-by-line read is sound here because `compose.yaml` has no continuation
    lines at all, which `test_dev_continuations.py` asserts rather than assumes.
    """
    return any(line.strip().startswith("provenance:") for line in compose.splitlines())


def documented_invocation_carries_the_variable(compose: str) -> bool:
    """Does every documented direct `--build` invocation carry the variable?

    ⭐ `compose.yaml`'s header offers the bare `docker compose … run --rm --build
    dev` as an equal way in, and that path does not go through the wrapper.
    ⛔ An invocation this repository documents that reintroduces the defect is worse
    than one it never mentions: a reader copies it and gets moving digests with no
    warning, from the file that owns the build.

    ⚠️ Collapsed first, because the documented form puts the variable on one line
    and the command on the next — so a raw split would see a command with no
    variable beside it and a variable with no command, and could be satisfied by
    either half alone.
    """
    invocations = [
        line
        for line in joined(compose).splitlines()
        if "docker compose" in line and "--build" in line
    ]
    return bool(invocations) and all(VARIABLE in line for line in invocations)


# --- the wrapper sets it, and sets it where it counts ------------------------


def test_the_wrapper_disables_default_build_attestations():
    # ⛔ The whole of the repair. Without this line `--build` re-exports a new
    # attestation manifest and a new manifest list on every invocation over
    # identical contents, and the id the tooling surfaces is the list.
    assert assigned_value(instructions("check")) == "1", (
        f"docker/dev/check does not set {VARIABLE}=1, so every invocation "
        f"re-exports build provenance and two offices holding one identical "
        f"environment read different shas for it"
    )


def test_the_assignment_check_can_say_no():
    # ⭐ THE CONTROL, and it is the reason the assertion above is worth having.
    # Same predicate, a copy with the line removed, and it must report nothing.
    doctored = "\n".join(
        line
        for line in joined(instructions("check")).splitlines()
        if not line.startswith(f"{VARIABLE}=")
    )
    assert assigned_value(doctored) is None, (
        "the predicate reports a value for a script that does not set one, so "
        "the check above would pass over a wrapper that had lost the line"
    )


def test_the_setting_reaches_the_docker_client():
    # ⛔ An assignment that is not exported is invisible to `docker compose`,
    # which is a different process. The failure mode is the expensive one: the
    # line is present, the file reads as fixed, and nothing changed.
    assert exports_the_variable(instructions("check")), (
        f"{VARIABLE} is assigned but not exported, so the docker client never "
        f"sees it and the build still stamps provenance"
    )


def test_the_export_check_can_say_no():
    doctored = "\n".join(
        line
        for line in joined(instructions("check")).splitlines()
        if not line.strip().startswith("export ")
    )
    assert not exports_the_variable(doctored), (
        "the predicate reports an export for a script that exports nothing"
    )


def test_the_setting_is_unconditional_and_not_a_caller_default():
    # ⛔ The only variable in `check` with no `${VAR:-…}` escape, deliberately.
    # ⚠️ The others carry a CALLER's answer across the boundary; this one is the
    # wrapper's own guarantee that its readings are comparable to another
    # checkout's, and a caller who unset it would silently restore the defect
    # while every check above stayed green.
    script = instructions("check")
    assert f"${{{VARIABLE}:-" not in script, (
        f"{VARIABLE} carries a caller override, so an environment that unsets "
        f"it gets moving digests back with nothing to show for it"
    )
    assert assigned_value(script) == "1"


def test_the_unconditional_check_can_say_no():
    # ⭐ The control for the clause above: the shape it forbids, fed to it.
    #
    # ⚠️ **This control is DERIVED from the real file, so it fails LOUDLY when
    # the assignment is gone rather than passing over an empty doctoring** — and
    # that is deliberate. MEASURED: with `docker/dev/check` planted back to its
    # state before the repair, this is the SIXTH red beside the five the plant was
    # predicted to produce. ⛔ A control that quietly passed there would be a
    # control whose subject had vanished: a vacuous pass.
    doctored = instructions("check").replace(f"{VARIABLE}=1", f"{VARIABLE}=${{{VARIABLE}:-1}}")
    assert f"${{{VARIABLE}:-" in doctored, (
        f"the doctored copy carries no `${{{VARIABLE}:-…}}`, which means the "
        f"real file had no `{VARIABLE}=1` to doctor — this control's subject is "
        f"absent, so it refuses to report a pass"
    )
    assert assigned_value(doctored) == f"${{{VARIABLE}:-1}}", (
        "the predicate reads an overridable assignment as the literal value, so "
        "the check above could not tell the two apart"
    )


def test_the_setting_precedes_the_compose_invocation():
    # ⚠️ `exec` replaces the shell: anything after that line never runs at all.
    assert set_before_the_build(instructions("check")), (
        f"{VARIABLE} is set after the Compose invocation that consumes it, so "
        f"it is set in a shell that no longer exists"
    )


def test_the_ordering_check_can_say_no():
    script = instructions("check")
    kept = [line for line in joined(script).splitlines() if not line.startswith(f"{VARIABLE}=")]
    doctored = "\n".join([*kept, f"{VARIABLE}=1"])
    assert not set_before_the_build(doctored), (
        "the predicate accepts an assignment made after the exec'd command, "
        "where it can have no effect"
    )


def test_it_does_not_cross_into_the_container():
    # ⭐ It is the docker CLIENT's variable. ⛔ Adding it to the pass-through
    # block would put a build-time setting inside a container that never builds
    # anything, and `compose.yaml` carries three crossing variables, not four
    # (`W36`, and the run's outer bound draws the same distinction).
    entries = [line.strip() for line in instructions("compose.yaml").splitlines()]
    assert f"- {VARIABLE}" not in entries, (
        f"{VARIABLE} crosses into the container, where nothing builds; it "
        f"belongs to the docker client on the host"
    )


# --- the declarative form is inert, and is not shipped as if it worked -------


def test_the_inert_provenance_key_is_not_shipped():
    # ⛔ MEASURED: `build: provenance: false` in `compose.yaml` changes nothing
    # at Compose v5.2.0 / buildx v0.35.0 — the attestation manifest was still
    # exported and still moved through `run --build`, through plain `build`, and
    # through `COMPOSE_BAKE=true`; a `.env` beside the file does not carry the
    # variable either. ⚠️ Compose accepts the key silently, so a future reader
    # who "tidies" the wrapper's line into the YAML would leave the tree looking
    # fixed and measuring identically to the defect.
    assert not declares_the_inert_key(read("compose.yaml")), (
        "compose.yaml declares a provenance build key, which is inert on this "
        "Docker: the fix is the variable docker/dev/check exports, and a key "
        "that reads like the fix and does nothing is worse than no key"
    )


def test_the_inert_key_check_can_say_yes():
    # ⭐ The control: the predicate must actually see the key it forbids. A
    # detector that can only say no is the same as no detector.
    doctored = read("compose.yaml").replace(
        "      dockerfile: Dockerfile",
        "      dockerfile: Dockerfile\n      provenance: false",
    )
    assert declares_the_inert_key(doctored), (
        "the predicate does not see a provenance key that is present, so the "
        "check above would pass over a file that had grown one"
    )


def test_the_documented_direct_invocation_carries_the_variable():
    # ⛔ `compose.yaml`'s header documents a way in that does not go through
    # `check`. Documenting an invocation that reintroduces the defect is worse
    # than not mentioning it: a reader who copies it gets moving digests and no
    # warning, from the file that owns the build.
    assert documented_invocation_carries_the_variable(read("compose.yaml")), (
        f"compose.yaml documents a `--build` invocation without {VARIABLE}, so "
        f"the documented path still re-exports provenance on every run"
    )


def test_the_documented_invocation_check_can_say_no():
    doctored = read("compose.yaml").replace(f"{VARIABLE}=1 \\", "")
    assert not documented_invocation_carries_the_variable(doctored), (
        "the predicate accepts a documented --build invocation with no variable anywhere near it"
    )


# --- the acceptance: two builds, one identifier ------------------------------


def exported_digests(output: str) -> dict[str, list[str]]:
    """Every `exporting <kind> sha256:…` line in a build log, grouped by kind."""
    digests: dict[str, list[str]] = {kind: [] for kind in EXPORT_KINDS}
    for kind, digest in _EXPORTING.findall(output):
        digests[kind].append(digest)
    return digests


def test_two_invocations_of_the_wrapper_export_one_identifier():
    # ⭐ **THE ACCEPTANCE, and the static half above is dark without it.** Every
    # check so far reads text; this one builds twice and reads what came out.
    # ⛔ Both directions in one reading: the stable pair must be PRESENT and
    # EQUAL — an absent line would satisfy "no two values differ" vacuously —
    # and the provenance-bearing pair must not appear at all.
    #
    # ⚠️ Only the parsed digests reach a failure message. A build log carries
    # the context path, and a path from this machine is personal data (R7).
    require_docker_run()
    readings = [
        exported_digests(result.stdout + result.stderr)
        for result in (
            run([f"./{DEV}/check", "python3", "-c", "pass"], cwd=repository_root())
            for _ in range(2)
        )
    ]
    for kind in STABLE:
        values = {digest for reading in readings for digest in reading[kind]}
        assert len(values) == 1, (
            f"two byte-identical builds exported {len(values)} distinct "
            f"{kind} digests: {sorted(values)}"
        )
    for kind in PROVENANCE_BEARING:
        found = [digest for reading in readings for digest in reading[kind]]
        assert not found, (
            f"the build still exports a {kind}, which carries build-time "
            f"provenance and moves across identical builds: {found}"
        )
