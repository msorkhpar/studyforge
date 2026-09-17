"""`W191`: a row's self-certification is ONE command with ONE exit code.

**What it does.** Runs every gate `tools.mergegate.GATES` declares — the gates the
merge will re-run on the merged tree — reads each one's exit code, and prints one
certification block. It exits `0` only when every declared gate is green, `1` when
any is red, and `2` when nothing was read. With `--check` it does the other half: it
reads a block somebody PASTED and refuses a claim that is not whole.

**How you use it.** On the host, at the ref that will merge, in your own checkout:

    python3 -m tools.quality.certify > "$CAP/certification.txt" 2>&1
    CERTIFY_EXIT=$?
    python3 -m tools.quality.certify --check "$CAP/certification.txt"

`certify(root, runner=None, gates=GATES)` returns the `Certification` the command
prints, `render(certification)` gives its lines, and `read_claim(text)` returns what
a pasted block CLAIMS.

**Depends on.** `argparse`, `dataclasses`, `pathlib`, `re`, `subprocess` and `sys` —
the standard library — `git` on the path, and `tools.mergegate` for the gate
declaration and the runner. ⛔ It is in neither `CHECKS` nor `NOTICES`: it is a
COMMAND, like `mergegate.py`, `trial.py` and `gated.py`, and the mirror asserts that.

## ⛔ THE DEFECT: TWO GATES, ONE PHRASE, AND AN OFFICE THAT CAN SATISFY IT BY HALVES

⚠️ **`python3 -m tools.quality` can exit `0` while `python3 -m pytest` exits non-zero
at the same ref**, because format and lint enforcement live in the suite and not in
the floor (Ruling 78). ⭐ **The floor's `0` is a true statement about the floor's own
population and says nothing whatever about the suite's** — `tools/quality/__main__.py`
prints exactly that sentence, last, on every run.

⛔ **Since the reviewing office was removed, the phrase *"floor + suite green"* is not
a description of a habit — it IS the merge condition**, and an office that ran the
floor, read `0` and inferred the rest satisfies the WORDS. ⭐ **So the office-facing
artefact is one command and one exit code: there is no half of this to read, and
nothing to remember to `&&`.**

## ⛔ WHY THIS IS NOT A THIRD INSTRUMENT — IT DECLARES NO GATE

⭐ **Two gates that disagree are not fixed by adding a third that agrees with
neither.** ⛔ **This module declares NO gate, NO check and NO population.** It reads
`tools.mergegate.GATES` — the declaration the merge gate itself runs — so the office's
certification and the coordinator's re-reading on the merged tree cannot name
different populations, and a gate added there is one the office is already running.

⚠️ **And the gate COMMANDS are no longer typed into a document.** `W301`'s defect was
that they were: the obliged block redirected a BARE `docker/dev/check` into
`floor.txt`, and the wrapper's no-argument case is the image's own `CMD` — the suite —
so a pasted reading wore the other gate's name and still exited `0`. ⭐ **A command
read from `GATES` cannot be misspelled by a document.**

## ⛔ THE ONE BEHAVIOURAL DIFFERENCE FROM THE MERGE GATE, AND IT IS DELIBERATE

⭐ **`mergegate` STOPS AT THE FIRST RED; this does not.** ⛔ There the merge is already
refused and a later gate cannot change the outcome. ⚠️ **Here a partial reading is the
defect itself** — an office that stopped at the first red would hold exactly the half
reading this row is about, and would fix one gate only to meet the other on the next
round. ⭐ Every declared gate is read, every reading is printed, and the block names
each gate WITH its environment, because two gates share the name `suite` (Ruling 326).

## ⛔ WHAT `--check` CAN AND CANNOT DO, STATED RATHER THAN IMPLIED

⛔ **NO INSTRUMENT CAN READ A CLAIM ABOUT A COMMAND SOMEBODY RAN.** ⭐ What `--check`
reads is whether the claim is WHOLE: every declared gate present, each green, with the
ref and the role. ⚠️ **So a handoff that ran one gate and claimed both is caught — the
block it cannot produce is the one it has to paste — and a handoff that FABRICATES the
missing line is not.** ⛔ **The instrument that catches THAT is `tools.mergegate`**,
which re-runs this same `GATES` on the merged tree and refuses the merge; the cost is
that the catch lands at merge time, on the coordinator's clock, rather than at the
claim. ⭐ That cost is the reason this prints the block rather than asking an office to
type one.

## ⛔ R7: THE ROLE IS A KIND OF CHECKOUT, NEVER A PATH

⚠️ **`git rev-parse --git-common-dir` answers *which checkout* with an ABSOLUTE PATH**,
which carries a home directory and may not be written into any record (R7). ⭐ So the
role printed here is `main checkout` or `linked worktree`, read off whether `.git` is a
file, and the office names itself in its own hand-back. ⛔ Nothing this command prints
carries a path.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.mergegate import GATES, Gate, Reading, Runner, run_gate

#: Exit codes. ⛔ `UNREAD` is a third state and is never a pass (Ruling 191): a run that
#: read no gate, or could not name the ref its readings were taken at, lands here.
CERTIFIED, NOT_CERTIFIED, UNREAD = 0, 1, 2

#: The two kinds of checkout, and the whole vocabulary — no path is ever printed (R7).
MAIN, LINKED = "main checkout", "linked worktree"

#: ⛔ The block's grammar, written by `render` and read by `read_claim`. ⭐ ONE spelling,
#: used in both directions, so a block this command cannot produce is one it refuses.
HEADER = re.compile(r"^certification: ref (?P<ref>[0-9a-f]{7,40}) · role (?P<role>[a-z ]+)$")
GATE_LINE = re.compile(
    r"^(?P<name>\S+) \[(?P<environment>[^\]]+)\]: (?P<verdict>GREEN|RED) exit (?P<code>\d+)$"
)


@dataclass(frozen=True)
class Certification:
    """What one run read: the ref it was taken at, and every gate's exit code."""

    ref: str = ""
    role: str = ""
    readings: tuple[Reading, ...] = ()
    unread: str = ""

    @property
    def red(self) -> tuple[Reading, ...]:
        """Return every gate that refused, in the order they were taken."""
        return tuple(reading for reading in self.readings if not reading.green)

    @property
    def verdict(self) -> int:
        """Return the exit code: certified, not certified, or unread."""
        if self.unread or not self.readings:
            return UNREAD
        return NOT_CERTIFIED if self.red else CERTIFIED


@dataclass(frozen=True)
class Claim:
    """What a PASTED block claims, and what it left out."""

    ref: str = ""
    role: str = ""
    green: tuple[str, ...] = ()
    red: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    unread: str = ""

    @property
    def verdict(self) -> int:
        """Return the exit code: a whole green claim, an incomplete one, or nothing read."""
        if self.unread or not (self.green or self.red):
            return UNREAD
        return NOT_CERTIFIED if (self.red or self.missing or not self.ref) else CERTIFIED


def _git(root: Path, *arguments: str) -> tuple[int, str]:
    """Run git in `root` and return its exit code with its stripped stdout."""
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(root), *arguments],  # noqa: S607 - git from the path, by design
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return 1, ""
    return result.returncode, result.stdout.strip()


def role_of(root: Path) -> str:
    """Name the KIND of checkout `root` is. ⛔ A kind, never a path (R7)."""
    return LINKED if (root / ".git").is_file() else MAIN


def named(gate: Gate) -> str:
    """Name one gate the way every line here names it: with its environment."""
    return f"{gate.name} [{gate.environment}]"


def certify(
    root: Path,
    runner: Runner | None = None,
    gates: Sequence[Gate] = GATES,
) -> Certification:
    """Read EVERY declared gate at `root`'s tip and return the certification.

    ⛔ **Nothing stops at the first red.** A partial reading is this row's defect, so a
    red gate is recorded and the run continues to the next one.
    """
    # ⛔ Resolved HERE and not as a default argument, for `mergegate.stage_and_read`'s
    #    reason: a default binds at definition, and no mirror could then substitute a
    #    runner without a docker daemon.
    take = run_gate if runner is None else runner
    if not gates:
        return Certification(unread="no gate is declared, so nothing was read")
    code, ref = _git(root, "rev-parse", "HEAD")
    if code != 0 or not ref:
        return Certification(unread="git cannot read a HEAD here, so no reading has a ref")
    code, dirty = _git(root, "status", "--porcelain", "--untracked-files=no")
    if code != 0:
        return Certification(unread="git cannot read this tree's status", ref=ref)
    if dirty:
        return Certification(
            unread=(
                "the tracked tree is not clean, so these readings would be taken at no ref "
                "that can merge — commit first, then certify"
            ),
            ref=ref,
        )
    readings = tuple(Reading(gate, take(gate, root)) for gate in gates)
    return Certification(ref=ref, role=role_of(root), readings=readings)


def render(certification: Certification) -> list[str]:
    """Return the block the command prints — the one an office pastes, unedited."""
    if certification.unread:
        return [f"⛔ UNREAD: {certification.unread}, so nothing is certified (exit {UNREAD})"]
    lines = [f"certification: ref {certification.ref} · role {certification.role}"]
    for reading in certification.readings:
        verdict = "GREEN" if reading.green else "RED"
        lines.append(f"{named(reading.gate)}: {verdict} exit {reading.exit_code}")
    if certification.red:
        refused = ", ".join(named(reading.gate) for reading in certification.red)
        lines.append(
            f"⛔ NOT CERTIFIED: {refused} refused at this ref, so this row does not merge "
            f"(exit {NOT_CERTIFIED})"
        )
        return lines
    lines.append(
        f"⭐ CERTIFIED: every declared gate is GREEN at this ref, in the environment each "
        f"line names (exit {CERTIFIED})"
    )
    return lines


def read_claim(text: str, gates: Sequence[Gate] = GATES) -> Claim:
    """Read a PASTED block and report what it claims — and what it left out.

    ⛔ **This reads a CLAIM, never a run.** It cannot know that any command was taken;
    what it refuses is a claim that is not whole — see the module contract.
    """
    header = next((match for match in map(HEADER.match, text.splitlines()) if match), None)
    green: list[str] = []
    red: list[str] = []
    for line in text.splitlines():
        match = GATE_LINE.match(line)
        if match is None:
            continue
        label = f"{match.group('name')} [{match.group('environment')}]"
        claimed_green = match.group("verdict") == "GREEN" and match.group("code") == "0"
        (green if claimed_green else red).append(label)
    if not green and not red:
        return Claim(unread="no certification block is here: not one gate line was read")
    claimed = set(green) | set(red)
    return Claim(
        ref=header.group("ref") if header else "",
        role=header.group("role") if header else "",
        green=tuple(green),
        red=tuple(red),
        missing=tuple(named(gate) for gate in gates if named(gate) not in claimed),
    )


def render_claim(claim: Claim) -> list[str]:
    """Return the lines `--check` prints about a pasted block."""
    if claim.unread:
        return [f"⛔ UNREAD: {claim.unread} (exit {UNREAD})"]
    # ⛔ The gates the block names, NAMED — never counted. A count would be the figure
    #    this project's own record rule cuts, and the names are what a reader acts on.
    lines = [f"claimed: {', '.join((*claim.green, *claim.red))}"]
    if not claim.ref:
        lines.append("⛔ the block names no ref, so its readings were taken at nothing")
    if claim.missing:
        lines.append(
            f"⛔ the claim is NOT WHOLE — declared and not carried here: "
            f"{', '.join(claim.missing)}. One gate's reading is not both"
        )
    if claim.red:
        lines.append(f"⛔ the block itself reports RED: {', '.join(claim.red)}")
    if claim.verdict == CERTIFIED:
        lines.append(
            f"⭐ WHOLE: every declared gate is claimed GREEN, with a ref (exit {CERTIFIED}). "
            f"⚠️ A claim is not a run — that these commands were TAKEN is readable from no "
            f"text, and `tools.mergegate` is what reads it, on the merged tree"
        )
    return lines


def main(argv: list[str] | None = None) -> int:
    """Certify the tree at `--root`, or read a claim with `--check`, and return the exit."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.quality.certify",
        description="Run every gate a merge will re-run and certify the ref, with ONE "
        "exit code; or read a pasted certification block and refuse a claim that is "
        "not whole.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="the checkout to certify (default: the current directory)",
    )
    parser.add_argument(
        "--check",
        type=Path,
        default=None,
        metavar="FILE",
        help="read a pasted certification block instead of running any gate",
    )
    arguments = parser.parse_args(argv)
    if arguments.check is not None:
        try:
            text = arguments.check.read_text(encoding="utf-8")
        except OSError:
            print(f"⛔ UNREAD: that block cannot be read (exit {UNREAD})")
            return UNREAD
        claim = read_claim(text)
        for line in render_claim(claim):
            print(line)
        return claim.verdict
    certification = certify(arguments.root)
    for line in render(certification):
        print(line)
    return certification.verdict


if __name__ == "__main__":
    sys.exit(main())
