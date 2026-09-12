"""What a finished build says it did, and what it says it would not touch.

**What it does.** Turns the `Written` record `generate.write_site` returns into
the greppable lines `studyforge build` prints, and into the exit code a script
reads.

**How you use it.** `lines(written, root, into)` renders the report;
`exit_code(written)` is `0` when nothing was refused and `1` when anything was.

**Depends on.** `generate.Written` for the record's shape and
`validate.report` for the two exit codes, imported rather than respelled.
⛔ No filesystem: this module knows what a build said, never how it found out.

## The line format

⭐ **The same shape as a plan's** — `<verb> <subject>  <detail>`, one fact per
line — because the acceptance that matters most for this command is a path-for-
path diff against `studyforge plan`, and two reports a reader has to normalise
before diffing are two reports nobody diffs.

⛔ **Every path printed here is relative to the output root**, exactly as
placement named it, so the report carries no directory belonging to whoever ran
it (R7).
"""

from __future__ import annotations

from studyforge.generate import Written
from studyforge.validate.report import INVALID, OK

#: What a refusal says. ⛔ R3 is enforced by refusing rather than by
#: remembering, so the line names the rule: a reader who sees it has not lost
#: anything, and the message has to make that obvious or they will assume they
#: have.
ALREADY_THERE = "a file is already there; nothing was overwritten"


def exit_code(written: Written) -> int:
    """`0` when the whole site was written, `1` when any path was refused."""
    return INVALID if written.refused else OK


def lines(written: Written, root: str, into: str) -> list[str]:
    """Return the whole report, one fact per line, paths sorted (R10)."""
    out = [f"build {root}  into {into}"]
    out += [f"wrote {path}" for path in sorted(str(path) for path in written.paths)]
    out += [
        f"refuse {path}  {ALREADY_THERE}" for path in sorted(str(path) for path in written.refused)
    ]
    return out
