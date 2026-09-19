"""`W366`: what a guarded merge READ, and the lines it prints — split from `tools/mergegate.py`.

**What it does.** Holds the three exit codes, one gate's `Reading`, a run's `Outcome` and
`render`, which turns an outcome into the printed lines. ⭐ `W366` adds three things a reading
must SAY: the scope each suite gate took (`SELECTED n of m` is never printed as a full run),
why that scope was chosen, and — when a FULL run audits the selection — every failure the
selection would have MISSED, RED by name.

**How you use it.** Through `tools.mergegate`, which re-exports every name here:

    for line in render(stage_and_read(root, branch)):
        print(line)

**Depends on.** `dataclasses` — the standard library — `tools.authorship` for who wrote the
commits, `tools.gates` for the `Gate` a reading came from, and `tools.selection` for the
audit's arithmetic. ⛔ Nothing from `studyforge` or `tools.quality` (`W310`).

## ⛔ WHY THIS IS ITS OWN MODULE (Ruling 261: a SPLIT, never a trim)

⚠️ `tools/mergegate.py` stood at 397 of R11's 400 lines when `W366` needed the scope, the audit
and a tee. ⭐ The seam is the question each file answers: `mergegate` says *how a merge is
staged, gated and restored*; THIS file says *what a reading is and how it is printed*.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.authorship import Authorship, render_authorship
from tools.gates import Gate
from tools.selection import missed as outside_selection

#: Exit codes. ⛔ `UNREAD` is a third state and is never a pass (Ruling 191): a run that
#: staged nothing, read no gate, or could not verify its own restore lands here.
MERGED, REFUSED, UNREAD = 0, 1, 2


@dataclass(frozen=True)
class Reading:
    """One gate's exit code, with the gate it came from."""

    gate: Gate
    exit_code: int
    #: ⭐ `W366`: the test ids the gate's own summary named as FAILED or ERROR.
    failed: tuple[str, ...] = ()

    @property
    def green(self) -> bool:
        """Report whether this gate passed."""
        return self.exit_code == 0

    @property
    def missed(self) -> tuple[str, ...]:
        """Return every failure the audited selection would NOT have taken (`W366`)."""
        return () if self.gate.audit is None else outside_selection(self.gate.audit, self.failed)


@dataclass(frozen=True)
class Outcome:
    """What a run did: what it read, and whether the tree is where it started."""

    readings: tuple[Reading, ...] = ()
    not_taken: tuple[str, ...] = ()
    unread: str = ""
    tip_before: str = ""
    tip_after: str = ""
    restored: bool | None = None
    #: ⭐ `W308`: who wrote the commits this merge introduces, read BEFORE anything is staged.
    authorship: Authorship = Authorship()
    #: ⭐ `W366`: what the suite gates took and why, printed before any gate's reading.
    scope: tuple[str, ...] = ()

    @property
    def red(self) -> tuple[Reading, ...]:
        """Return every gate that refused, in the order they were taken."""
        return tuple(reading for reading in self.readings if not reading.green)

    @property
    def verdict(self) -> int:
        """Return the exit code: merged, refused, or unread when nothing was read."""
        # ⛔ `W308` FIRST, and it needs no `restored`: the authorship gate runs before the
        #    merge is staged, so a refusal here leaves a tree nothing ever touched.
        if self.authorship.crossed:
            return REFUSED
        if self.unread or not self.readings:
            return UNREAD
        if self.red:
            # ⛔ A refusal whose restore could not be VERIFIED is not a clean refusal:
            #    the office is left at a tree nobody has described (Ruling 287).
            return REFUSED if self.restored else UNREAD
        return MERGED


def render(outcome: Outcome) -> list[str]:
    """Return the lines the command prints: what was read, in which environment, then why."""
    if outcome.unread:
        return [f"⛔ UNREAD: {outcome.unread}, so no merge was gated (exit 2)"]
    # ⭐ `W308`: WHO WROTE IT, with its population, BEFORE any gate's reading (Ruling 191(a)).
    lines = render_authorship(outcome.authorship)
    if outcome.authorship.crossed:
        return lines
    lines.append(
        f"merge gate: {len(outcome.readings)} gate(s) read on the MERGED tree, never on HEAD"
    )
    lines.extend(outcome.scope)
    for reading in outcome.readings:
        state = "GREEN" if reading.green else "⛔ RED  "
        said = ", ".join(part for part in (reading.gate.form, reading.gate.scope) if part)
        form = f" ({said})" if said else ""
        lines.append(
            f"  {state}  exit {reading.exit_code}  {reading.gate.name} "
            f"[{reading.gate.environment}]{form} — {reading.gate.answers}"
        )
        lines.extend(_audit(reading))
    if not outcome.red:
        targeted = [r for r in outcome.readings if r.gate.scope.startswith("SELECTED")]
        lines.append(
            "⭐ PASSED: every declared gate is green on the merged tree"
            + (" — ⚠️ the suite read a SELECTION, not the full suite" if targeted else "")
        )
        return lines
    refused = ", ".join(f"{r.gate.name} [{r.gate.environment}]" for r in outcome.red)
    lines.append(f"⛔ REFUSED: {refused} — nothing was committed, and the merge was aborted")
    if outcome.not_taken:
        lines.append(
            f"⚠️ NOT TAKEN, because the merge was already refused: {', '.join(outcome.not_taken)}"
        )
    if outcome.restored:
        lines.append(f"⭐ RESTORED: HEAD is back at {outcome.tip_before[:12]} and clean")
    else:
        reads = outcome.tip_after[:12] or "nothing"
        lines.append(
            f"⛔ THE RESTORE COULD NOT BE VERIFIED: HEAD reads {reads} against "
            f"{outcome.tip_before[:12]}. Read the tree before anything else (exit 2)"
        )
    return lines


def _audit(reading: Reading) -> list[str]:
    """Return what a FULL run's audit of the selection found (`W366` clause 4)."""
    if reading.gate.audit is None:
        return []
    where = f"[{reading.gate.environment}]"
    if reading.missed:
        return [
            f"    ⛔ AUDIT RED {where}: the selection would have MISSED {test}"
            for test in reading.missed
        ]
    if reading.failed:
        return [f"    AUDIT {where}: every failure lies inside the selection, which caught it"]
    if not reading.green:
        return [f"    ⛔ AUDIT UNREAD {where}: the suite failed and named no failing test"]
    return [f"    ⭐ AUDIT GREEN {where}: nothing failed, so the selection missed nothing"]
