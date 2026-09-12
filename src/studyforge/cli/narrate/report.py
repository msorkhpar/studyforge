"""What a finished narration run says it did, and the exit code a script reads.

**What it does.** Turns a `stage.Narrated` into the greppable lines
`studyforge narrate` prints, and into its exit code.

**How you use it.** `lines(narrated, root)` renders the report;
`exit_code(narrated)` is `0` narrated, `1` something the corpus declared could
not be produced, `2` the tool could not run at all — `cli/site/`'s three.

**Depends on.** `stage.Narrated` for the record's shape, and `validate` for the
three exit codes, imported rather than respelled. ⛔ No filesystem and no
network: this module knows what a run said, never how it found out.

## The line format

⭐ `<verb> <subject>  <detail>`, one fact per line — `studyforge build`'s and
`studyforge plan`'s shape. ⛔ **Every clip path is relative to the corpus
root**, so the report carries no directory belonging to whoever ran it (R7).

⛔ **An absent service is a NAMED refusal and exits `2`.** Nothing about the
corpus is wrong, so it is not `1`; the stage could not run, and the line says
the corpus still reads without narration (R6, R8).
"""

from __future__ import annotations

from pathlib import Path

from studyforge.cli.narrate.stage import Narrated
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK

#: What a run with no service says. ⛔ It names the remedy and the floor: the
#: corpus still builds and reads, silently, and nothing was requested or written.
NO_SERVICE = (
    "no narration service answered, so nothing was requested and nothing was written; "
    "the corpus still builds and reads without narration. Start the service and run again"
)

#: What a unit a job stopped early on says.
RETRY = "the job stopped early; running this command again asks only for what is left"

#: What a clip placed under another format says.
UNSETTLED = "the service answered in another format; this unit will be asked for again"


def exit_code(narrated: Narrated) -> int:
    """`2` no service, `1` anything declared was not produced, `0` otherwise."""
    if not narrated.health.reachable:
        return UNUSABLE
    if narrated.stopped or narrated.failed or narrated.retryable or narrated.unsettled:
        return INVALID
    return OK


def lines(narrated: Narrated, root: str) -> list[str]:
    """Return the whole report, one fact per line, clip paths sorted (R10)."""
    out = [f"narrate {root}"]
    if not narrated.health.reachable:
        out.append(f"refuse service  {NO_SERVICE}")
        out.append(f"detail service  {narrated.health.detail}")
        return out
    out.append(f"probe service  {narrated.health.detail}")
    base = Path(root)
    out += [f"wrote {path}" for path in sorted(_relative(item, base) for item in narrated.written)]
    out += [f"fail {speech_id}  {reason}" for speech_id, reason in narrated.failed]
    out += [f"retry {speech_id}  {RETRY}" for speech_id in narrated.retryable]
    out += [f"unsettled {speech_id}  {UNSETTLED}" for speech_id in narrated.unsettled]
    if narrated.stopped:
        out.append(f"stopped service  {narrated.stopped}")
    out.append(
        f"narrated {root}  {len(narrated.written)} clip(s) written, "
        f"{narrated.fresh} already synthesised under these conditions"
    )
    return out


def _relative(path: Path, base: Path) -> str:
    """`path` relative to the corpus root, in POSIX spelling; ⛔ never absolute (R7)."""
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.name
