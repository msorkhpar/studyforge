"""The rubric's obliged self-certification block, read against `check`'s own contract.

⛔ **A fourth module under `tests/docker/` and not a section of an existing one, for
R11's reason and for a subject reason.** `test_dev_check_timeout.py` owns *what
happens to a run that never finishes*; this owns *which command each gate names*.
⭐ They share `devfiles` and nothing else.

## ⛔ The defect this exists to stop coming back

⚠️ `docker/dev/check`'s no-argument case sets `python3 -m pytest` — the image's own
`CMD`, which `test_dev_check_timeout.py` pins as a CHECKED COPY. ⛔ So a **bare**
`docker/dev/check` runs THE SUITE. The rubric's obliged block once redirected
a bare invocation into `floor.txt` and read its status as `FLOOR_EXIT`, so an office
that pasted the block ran the suite twice and filed one run under the floor's name.

⭐ **It is the worst class a gate can have: it does not FAIL, it PASSES THE WRONG
THING** — a reading with nothing under it. Both statuses are `0` whenever the suite is green, so
no instrument downstream could tell — which is why the check has to be on the TEXT
the office pastes, and not on an exit code.

## ⭐ Why here and not beside the rubric

⛔ **The contract being broken is `docker/dev/check`'s**, stated in that file's own
header: the bare form is documented as *the whole suite* and the floor has a named
form of its own. ⚠️ A check that read only the rubric would assert the rubric agrees
with itself; this reads BOTH and fails if they ever disagree, which is the idiom
`test_the_no_argument_case_names_the_image_s_own_command` already uses for `CMD`.

## ⛔ THE COMMANDS MOVED OUT OF THE DOCUMENT, SO THE QUESTION MOVED WITH THEM

⭐ **The obliged block is now ONE command with ONE exit code** — a two-item list of
readings is satisfiable by halves — ⛔ **so the gate argv an
office runs is `tools.mergegate.GATES` and is no longer TYPED into the rubric at all.**

⚠️ **Nothing the first version pinned is dropped; each assertion is re-pointed at the
population that now carries the answer** — a control is inverted, never deleted. ⭐ **The ONE
control that inverts says so in its own body:** the block used to owe the wrapper two
invocations and now owes it NONE, because an office invoking the wrapper by hand is
back to running two things and remembering to `&&` them.
"""

from __future__ import annotations

import re

from tests.docker.devfiles import instructions, read
from tests.support import repository_root
from tools.mergegate import GATES

#: The document carrying the obliged block. ⚠️ Named as a path rather than linked:
#: this is a test, and the link rule binds a handoff's citations, not a constant.
RUBRIC = "docs/conventions/review-rubric.md"

#: The block is identified by what it WRITES, never by a line number or a heading —
#: both of which move every time the rubric is re-wrapped.
MARKER = "$CAP/certification.txt"

#: The one command the block obliges, whose exit code IS the certification.
CERTIFY = "python3 -m tools.quality.certify"

#: The floor's own command, as `check`'s header documents it.
FLOOR = ["python3", "-m", "tools.quality"]

#: The suite's, whose trailing flags are the office's business and not this check's.
SUITE = ["python3", "-m", "pytest"]

#: Every `docker/dev/check` invocation, with whatever it names up to a redirect,
#: a pipe or the end of the command.
INVOCATION = re.compile(r"(?:\./)?docker/dev/check\b(?P<rest>[^>|;}\n]*)")


def rubric() -> str:
    return (repository_root() / RUBRIC).read_text(encoding="utf-8")


def obliged_block() -> list[str]:
    """The fenced block the rubric tells a handoff to paste.

    ⛔ Located by `MARKER` rather than by position, and asserted UNIQUE: two blocks
    writing the same capture file would mean the rubric had grown a second copy of
    its own gate form, which is the defect one level up from this one.
    """
    blocks: list[list[str]] = []
    current: list[str] = []
    inside = False
    for line in rubric().splitlines():
        if line.startswith("```"):
            if inside:
                blocks.append(current)
                current = []
            inside = not inside
            continue
        if inside:
            current.append(line)
    found = [block for block in blocks if any(MARKER in line for line in block)]
    assert len(found) == 1, f"expected one block writing {MARKER}, found {len(found)}"
    return found[0]


def block_invocations() -> list[list[str]]:
    """What each `docker/dev/check` IN THE BLOCK names — which must now be none at all."""
    commands = []
    for line in obliged_block():
        if line.lstrip().startswith("#"):
            continue
        commands.extend(match.group("rest").split() for match in INVOCATION.finditer(line))
    return commands


def invocations() -> list[list[str]]:
    """What each declared gate names as its command, for every gate run through the wrapper.

    ⛔ **Read from `tools.mergegate.GATES` and no longer from the document**.
    ⭐ Every question below is the one the first version asked; only the population moved, from text
    an office retypes to the declaration the office and the merge gate both run.
    """
    return [
        list(gate.argv[1:])
        for gate in GATES
        if gate.argv and gate.argv[0].removeprefix("./") == "docker/dev/check"
    ]


def default_command() -> list[str]:
    """`check`'s no-argument case — what a BARE invocation actually runs."""
    fallback = [
        line for line in instructions("check").splitlines() if line.strip().startswith("set --")
    ]
    assert len(fallback) == 1, f"expected one default-command line in check, found {fallback}"
    return fallback[0].split("set --", 1)[1].split()


# --- the block names a command for every gate --------------------------------


def test_the_obliged_block_names_the_one_certifying_command():
    # ⭐ The control, and it is the same control: without it every assertion below is
    # vacuously true of a block that stopped obliging anything, and the rubric's own
    # instruction would have quietly become prose.
    assert any(CERTIFY in line for line in obliged_block()), (
        f"the obliged block no longer names {CERTIFY}, so the certification it obliges "
        f"is a sentence again"
    )


def test_the_obliged_block_RUNS_NO_GATE_BY_HAND():
    # ⛔ **THE INVERTED CONTROL** — inverted, never deleted. This module used to require
    # the block to invoke the wrapper TWICE, once per gate. It now requires NONE: an
    # office invoking the wrapper by hand is back to running two things and remembering
    # to `&&` them, which is the office this row is about. ⭐ The commands still exist —
    # in `GATES`, asserted below — and the block reads them rather than retyping them.
    assert block_invocations() == [], (
        f"the obliged block invokes the wrapper by hand: {block_invocations()}; the "
        f"gate commands live in tools.mergegate.GATES and the block runs ONE command"
    )


def test_the_declared_gates_are_inhabited_and_reach_the_wrapper():
    # ⭐ The second half of the control, on the population that moved: an empty GATES,
    # or one that stopped naming the wrapper, would make every assertion below vacuous
    # (an empty population is never the pass reading).
    assert len(invocations()) >= 2, (
        f"the declared gates make {len(invocations())} wrapper invocations; they owe "
        f"one for the floor and one for the suite"
    )


def test_no_declared_gate_is_a_bare_invocation():
    # ⛔ **THE WHOLE OF THE DEFECT**, asked of `GATES`. A bare `docker/dev/check`
    # runs the image's `CMD`, so a bare call filed under the FLOOR's name is a SUITE
    # run — and exits 0, so nothing downstream can tell.
    for command in invocations():
        assert command, (
            "a declared gate invokes docker/dev/check with no command, which runs "
            "the image's CMD (the suite); a reading filed from it wears whichever "
            "gate's name the redirect gave it"
        )


def test_each_gate_names_the_command_its_own_reading_comes_from():
    # ⭐ Explicitly, and in the forms `check`'s header documents — so neither
    # reading can be produced by the wrapper's default and the two can never be
    # the same run.
    commands = invocations()
    assert FLOOR in commands, f"no invocation names the floor as {' '.join(FLOOR)}: {commands}"
    assert any(command[: len(SUITE)] == SUITE for command in commands), (
        f"no invocation names the suite as {' '.join(SUITE)}: {commands}"
    )


def test_the_floor_reading_cannot_be_produced_by_the_wrappers_default():
    # ⛔ The property that actually settles the row, asserted against the wrapper
    # rather than against a literal: if `check`'s default ever BECAME the floor,
    # this would still be the right question and would still answer it.
    assert FLOOR != default_command(), (
        f"check's no-argument case is {default_command()}, which is the floor's own "
        f"command; a bare invocation and a floor invocation would be the same run"
    )
    for command in invocations():
        if command[: len(SUITE)] == SUITE:
            continue
        assert command != default_command(), (
            f"a non-suite gate names {command}, which is exactly what a bare "
            f"invocation runs; the two readings would be one run filed twice"
        )


# --- and they agree with the contract in `check`'s own header ----------------


def test_the_named_forms_are_the_ones_the_wrapper_documents():
    # ⛔ **Asserted where the contract LIVES.** `check`'s header is the authority
    # for how it is invoked, and `instructions()` would strip it — so this reads
    # the raw text on purpose, which is the one place in this directory that is
    # correct rather than lazy.
    header = read("check")
    assert f"docker/dev/check {' '.join(FLOOR)}" in header, (
        "check's header no longer documents the floor's own invocation, so the "
        "rubric is now naming a form its wrapper does not claim to support"
    )
    assert " ".join(SUITE) in header, "check's header no longer documents the suite's command"


def test_the_wrapper_still_documents_the_bare_form_as_the_whole_suite():
    # ⚠️ **The premise, asserted rather than assumed.** Every check above is
    # reasoning from "bare means the suite". If `check` ever documented the bare
    # form as something else, these would be guarding a rule that had moved.
    header = read("check")
    bare = [
        line
        for line in header.splitlines()
        if line.lstrip("# ").startswith("docker/dev/check ") and "the whole suite" in line
    ]
    assert len(bare) == 1, (
        f"check's header no longer documents a bare invocation as the whole suite, "
        f"found {bare}; W301's premise has moved and its checks need re-reading"
    )
