"""What a finished narration run says it did, and the exit code a script reads.

**What it does.** Turns a `stage.Narrated` into the greppable lines
`studyforge narrate` prints, and into its exit code.

**How you use it.** `lines(narrated, root)` renders the report;
`prune_lines(pruned, root)` and `prune_exit_code(pruned)` render `--prune`'s;
`exit_code(narrated)` is `0` narrated, `1` something the corpus declared could
not be produced, `2` the tool could not run at all — `cli/site/`'s three.

**Depends on.** `stage.Narrated` and `prune.Pruned` for the two shapes, and `validate` for the
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

from studyforge.cli.narrate.prune import Pruned
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

#: ⭐ The dead-entry disclosure — printed on EVERY run, zero included, so an absent
#: line is a disclosure that did not run rather than a corpus with none.
DEAD = "record entries name a speech id this corpus did not produce; --prune deletes their clips"

#: ⭐ Printed on every run, zero included, beside the dead count.
SUPERSEDED = (
    "clips an earlier wording or directory wrote are still named by the record; "
    "--prune deletes them"
)

#: What a walk that missed declared units says, on either request.
PARTIAL = (
    "declared units have no material, so this walk is partial and a prune refuses "
    "until every declared unit is read"
)

#: ⛔ A partial walk refuses BY NAME, and before a file is touched.
REFUSED = "nothing was deleted: these declared units have no material, so the walk is partial"


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
        return out + _disclosure(narrated)
    out.append(f"probe service  {narrated.health.detail}")
    base = Path(root)
    out += [f"wrote {path}" for path in sorted(_relative(item, base) for item in narrated.written)]
    out += [f"fail {speech_id}  {reason}" for speech_id, reason in narrated.failed]
    out += [f"retry {speech_id}  {RETRY}" for speech_id in narrated.retryable]
    out += [f"unsettled {speech_id}  {UNSETTLED}" for speech_id in narrated.unsettled]
    if narrated.stopped:
        out.append(f"stopped service  {narrated.stopped}")
    out += _disclosure(narrated)
    out.append(
        f"narrated {root}  {len(narrated.written)} clip(s) written, "
        f"{narrated.fresh} already synthesised under these conditions"
    )
    return out


def _disclosure(narrated: Narrated) -> list[str]:
    """Return the dead-entry count and the units a partial walk missed — named, never paths."""
    out = [f"dead record  {len(narrated.dead)} {DEAD}"]
    out.append(f"superseded clips  {len(narrated.superseded)} {SUPERSEDED}")
    if narrated.unwalked:
        out.append(f"partial walk  {PARTIAL}: {', '.join(narrated.unwalked)}")
    return out


def prune_exit_code(pruned: Pruned) -> int:
    """`1` refused or anything held, `0` otherwise — ⛔ a refusal is never `0`."""
    return INVALID if pruned.refused or pruned.held else OK


def prune_lines(pruned: Pruned, root: str) -> list[str]:
    """Return `--prune`'s whole report, one fact per line, paths relative (R7, R10)."""
    out = [f"prune {root}"]
    if pruned.refused:
        out.append(f"refuse walk  {REFUSED}: {', '.join(pruned.unwalked)}")
        return out
    base = Path(root)
    out += [f"delete {path}" for path in sorted(_relative(item, base) for item in pruned.deleted)]
    out += [f"forget {speech_id}" for speech_id in pruned.forgotten]
    out += [f"forget {speech_id}  superseded {item.filename}" for speech_id, item in pruned.cleared]
    out += [f"held {speech_id}  {why}" for speech_id, why in pruned.held]
    out.append(
        f"pruned {root}  {len(pruned.deleted)} clip(s) deleted, "
        f"{len(pruned.forgotten)} record entries removed, {len(pruned.held)} held"
    )
    return out


def _relative(path: Path, base: Path) -> str:
    """`path` relative to the corpus root, in POSIX spelling; ⛔ never absolute (R7)."""
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.name
