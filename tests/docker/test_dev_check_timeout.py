"""The outer bound on a run, and the statuses it must not touch.

⛔ **A third module under `tests/docker/` and not a section of either existing
one, and R11 is the reason.** `test_dev_image.py` is 583 lines against a
600-line ceiling for tests and `test_dev_image_browser.py` carries the browser
and the font. ⭐ These checks also have one subject — *what happens to a run that
never finishes* — which is the seam a module is supposed to be cut along.

## ⛔ What is being bounded, and whose defect it is

⚠️ `tests/visual/browser.py` sets `deadline = time.monotonic() + CALL_TIMEOUT`
and loops `while time.monotonic() < deadline`, but the loop body blocks in
`os.read` on a live pipe with no deadline. ⛔ **So its own `"no answer in 30s"`
is unreachable for a browser that is up and silent; it fires only if the pipe
closes.** A full-page capture at Docker's 64 MB `/dev/shm` default once wedged
the suite exactly that way: 5 of 7 capture checks passed and the 6th never
returned.

⛔ **This module tests the OUTER bound and not the deadlined read.** Deadlining
the read means `select`-ing on the fd, a different I/O path, which would change
what every reading in `tests/visual/` is taken against; that belongs to the
harness's own row. ⭐ A bound in `docker/dev/check` changes nothing any reading
is taken against, which is the whole of why the two are separable.

## ⛔ Why the plant is the point and the `timeout` is not

⚠️ **An instrument that converts a hang into a non-zero exit is DARK until
somebody hangs the thing on purpose**. A bound that nothing
ever trips is a check that cannot fail by construction, and it would pass every
static assertion in the first half of this file while doing nothing at all.

⭐ So the second half **wedges a run deliberately and reads it both ways**: a
command that overruns, a command that overruns *and ignores SIGTERM*, and — the
one that matters most — **a command that fails on its own, whose status must
come back unchanged**. ⛔ A wrapper that collapsed an overrun and a red into `1`
would make a wedged run indistinguishable from a failing assertion, which is
strictly worse than the hang it replaces.

⛔ **The statuses are read, not assumed** — through the real `docker/dev/check`
in the pinned image:

```text
command                            bound   status   wall
sh -c 'sleep 300'                    3s      124    3.66s
sh -c 'trap "" TERM; sleep 300'      3s      137    33.45s   killed after grace
sh -c 'exit 7'                      60s        7    -        its OWN code
python3 -c 'raise SystemExit(1)'   120s        1    -        pytest's range
sh -c 'exit 0'                      60s        0    -
(no arguments — the whole suite)  1800s        0    57.78s
```

⭐ **`124` and `137` are both outside pytest's exit range (0-5)**, so an overrun
can never be read as a failing assertion.

## ⚠️ Why the second half is opt-in

⛔ Gated on `STUDYFORGE_DOCKER_TESTS=1` and on not already being inside the
image, for the reasons `test_dev_image.py`'s docstring gives: the build needs the
network, and without the recursion guard the suite would build a container, run
the suite, which would build a container, forever. ⭐ The static half above needs
no daemon and always runs.
"""

from __future__ import annotations

import json
import re

from tests.docker.devfiles import DEV, instructions, read
from tests.docker.devgate import require_docker_run
from tests.support import repository_root, run

#: The variable that overrides the bound. ⛔ Read on the host and deliberately
#: NOT passed into the container: it shapes the command this wrapper builds
#: rather than anything inside, which is why `compose.yaml` still carries three
#: pass-through variables and not four.
OVERRIDE = "STUDYFORGE_CHECK_TIMEOUT"

#: ⛔ What `timeout` reports, and the whole of why this bound is safe.
#: `124` is an overrun it terminated, `137` is one it had to kill (128+9).
#: ⚠️ Neither can collide with pytest, whose codes are 0-5.
OVERRUN = (124, 137)

#: A bound short enough that the plant below costs seconds rather than minutes.
#: ⚠️ Not zero and not one: the container has to start before the command can
#: overrun, and a bound under the startup cost would measure Docker rather than
#: the wrapper.
PLANT_BOUND = "3"


def joined() -> str:
    """`check` with comments stripped and line continuations collapsed.

    ⛔ **Collapsing them is load-bearing and it cost a red to learn.** The first
    version of `test_the_bound_runs_inside_the_container_and_not_on_the_host`
    matched `^\\s*timeout` against the raw text and fired on the CONTINUATION of
    the Compose command — a correct implementation reported as a host-side
    invocation. ⚠️ A check that fires on the right answer is a check somebody
    deletes, so the shape a reader sees and the shape this asserts over are the
    same shape: one logical line per command.
    """
    return instructions("check").replace("\\\n", " ")


def check_line() -> str:
    """The single logical line that invokes Compose.

    ⛔ The assertions below are about the ORDER of words in one command, and a
    backslash-wrapped source line would let `timeout` and `dev` land on
    different lines and defeat them.
    """
    lines = [line for line in joined().splitlines() if "docker compose" in line]
    assert len(lines) == 1, f"expected one Compose invocation, found {lines}"
    return " ".join(lines[0].split())


# --- the bound exists, and is where it has to be ----------------------------


def test_the_run_is_bounded_at_all():
    # ⛔ The whole of the bound: an unbounded hang has no verdict, and R15 makes
    # this container the only authority for a reading — so a run that
    # never returns withholds the only reading that counts.
    assert "timeout" in check_line(), (
        "docker/dev/check runs the suite unbounded; a wedged browser read then "
        "hangs with no verdict instead of failing"
    )


def test_the_bound_runs_inside_the_container_and_not_on_the_host():
    # ⛔ **Three reasons, and all three are in `check`'s own comment block.**
    # (1) The host's `timeout` is a different program — `uutils coreutils` on
    # one machine, GNU coreutils in the image, absent on macOS — so a host-side
    # bound is an UNPINNED bound. (2) `check` claims two screens up that it uses
    # only `docker`, `id` and shell builtins; a host-side `timeout` falsifies
    # that claim in the file that makes it. (3) Inside, it bounds the COMMAND
    # and not the image BUILD, which is the right subject: a cold build is slow
    # for network reasons and the thing that hangs is a read in the suite.
    line = check_line()
    service = line.index(" dev ")
    assert line.index("timeout") > service, (
        f"timeout runs before the service name, so it is bounding the host's "
        f"docker client rather than the command in the container: {line!r}"
    )
    assert not re.search(r"^\s*(exec\s+)?timeout\b", joined(), re.MULTILINE), (
        "check invokes timeout on the host, which needs a tool beyond docker "
        "and id and is a different implementation on every machine"
    )


def test_the_bound_is_overridable_and_carries_a_default():
    # ⭐ Overridable because the plant below needs a short bound, and because a
    # contributor on slow hardware must be able to raise it rather than delete
    # it. ⛔ Defaulted because a bound nobody sets is no bound.
    script = instructions("check")
    assert f"{OVERRIDE}=${{{OVERRIDE}:-" in script, (
        f"{OVERRIDE} has no default, so an unset variable leaves the run unbounded"
    )
    default = script.split(f"{OVERRIDE}:-")[1].split("}")[0]
    assert default.isdigit() and int(default) > 0, (
        f"the default bound is not a duration: {default!r}"
    )


def test_the_default_bound_is_loose_against_a_measured_run_and_says_so():
    # ⛔ **A loose threshold says so.** A threshold chosen to be LOOSE must SAY so
    # in its own body, or the next reader cannot tell a measured bound from a
    # guessed one — and tightens it.
    script = read("check")
    default = int(instructions("check").split(f"{OVERRIDE}:-")[1].split("}")[0])
    assert default >= 600, (
        f"a {default}s bound is tight enough to fire on a healthy run on slower "
        f"hardware, and a bound that fires on a healthy run is one somebody deletes"
    )
    assert "LOOSE" in script and "57.66" in script, (
        "the bound does not state that it is loose, or against what it was "
        "measured; a loose threshold says both in its own body"
    )


def test_the_no_argument_case_names_the_image_s_own_command():
    # ⛔ `timeout` needs a command, so the no-argument case has to name one —
    # and a second copy of the image's `CMD` is exactly the divergence this
    # wrapper exists to prevent. ⭐ So it is a CHECKED copy, in the idiom
    # `test_dev_image_browser.py` states for the browser candidate names: this
    # asserts the two agree, and a check that read only one could not notice
    # them disagreeing.
    cmd = [line for line in instructions("Dockerfile").splitlines() if line.startswith("CMD ")]
    assert len(cmd) == 1, f"expected one CMD, found {cmd}"
    declared = json.loads(cmd[0][len("CMD ") :])
    fallback = [
        line for line in instructions("check").splitlines() if line.strip().startswith("set --")
    ]
    assert len(fallback) == 1, f"expected one default-command line in check, found {fallback}"
    assert fallback[0].split("set --", 1)[1].split() == declared, (
        f"check defaults to {fallback[0]!r} and the image's CMD is {declared}; "
        f"the two must be the same command or the wrapper and the host diverge"
    )


def test_nothing_between_timeout_and_the_caller_can_rewrite_the_status():
    # ⛔ **The trap this check exists not to fall into.** A wrapper that collapsed
    # an overrun and a red into `1` would make a wedged run indistinguishable
    # from a failing assertion — strictly worse than the hang it replaces.
    # ⭐ `exec` is the shape that cannot: the shell is replaced, so there is no
    # frame left to inspect or rewrite what came back.
    line = check_line()
    assert line.startswith("exec "), f"the Compose invocation is not exec'd: {line!r}"
    for rewriting in ("|| exit", "&& exit", "; exit", "|| true", "2>/dev/null"):
        assert rewriting not in line, f"the status is rewritten by {rewriting!r}: {line!r}"


# --- the plant: a run wedged on purpose, read both ways ---------------------


def bounded(command: list[str], bound: str = PLANT_BOUND):
    """Run `docker/dev/check` with a short bound and return the result."""
    return run(
        ["env", f"{OVERRIDE}={bound}", f"./{DEV}/check", *command],
        cwd=repository_root(),
    )


def test_a_run_that_never_finishes_comes_back_with_an_overrun_status():
    # ⭐ **THE PLANT, and without it every assertion above is dark.** A bound
    # that nothing ever trips is a check that cannot fail by construction
    # until something trips it, so this wedges a run on purpose and reads what comes out.
    require_docker_run()
    result = bounded(["sh", "-c", "sleep 300"])
    assert result.returncode in OVERRUN, (
        f"a command that ran far past the bound returned {result.returncode}; "
        f"the bound did not fire, so a wedged suite still hangs forever"
        + result.stdout
        + result.stderr
    )


def test_a_run_that_ignores_sigterm_is_killed_and_still_reports_an_overrun():
    # ⛔ The half a bare `timeout` would miss: a command that traps SIGTERM
    # turns the bound straight back into the hang it replaces. `--kill-after`
    # closes it, and the status becomes `137` rather than `124` — still an
    # overrun, still outside pytest's range.
    require_docker_run()
    result = bounded(["sh", "-c", 'trap "" TERM; sleep 300'])
    assert result.returncode in OVERRUN, (
        f"a command that ignores SIGTERM returned {result.returncode}; without "
        f"a kill after the grace period the bound is advisory only" + result.stdout + result.stderr
    )


def test_a_real_failure_passes_its_own_status_through_unchanged():
    # ⛔ **THE OTHER WAY, AND IT IS THE ONE THAT MATTERS MOST.** `7` is chosen
    # because it is neither an overrun nor anything pytest emits: a wrapper that
    # normalised statuses would return `1` here and look perfectly healthy while
    # having destroyed the difference between a red and a hang.
    require_docker_run()
    result = bounded(["sh", "-c", "exit 7"], bound="60")
    assert result.returncode == 7, (
        f"a command that failed with 7 came back as {result.returncode}; the "
        f"wrapper is rewriting statuses, so a wedged run and a red are no "
        f"longer distinguishable" + result.stdout + result.stderr
    )
    assert result.returncode not in OVERRUN, "a real failure was reported as an overrun"


def test_a_run_inside_the_bound_is_still_clean():
    # ⭐ The control's control: the bound must be invisible to a healthy run.
    # ⚠️ Without this the three checks above are all satisfied by a wrapper that
    # simply returns non-zero always.
    require_docker_run()
    result = bounded(["sh", "-c", "exit 0"], bound="60")
    assert result.returncode == 0, (
        f"a command that succeeded came back as {result.returncode}; the bound "
        f"is firing on a run that finished" + result.stdout + result.stderr
    )
