"""What a finished build says it did, and what it says it would not touch.

**What it does.** Turns the `Written` record `generate.write_site` returns into
the greppable lines `studyforge build` prints, and into the exit code a script
reads.

**How you use it.** `lines(written, root, into)` renders the report, ⭐ with a
`stale` line per clip that plays moved words and an `unlinked` line per clip an
earlier narrated build left under `--out`, neither changing the exit;
`exit_code(written)` is `0` when nothing was refused and `1` when anything was.
⚠️ **A replaced path is not a refusal**: a rebuild that overwrote only its own
previous output exits `0`, which is what makes *build, edit a lesson, build
again* usable from a script.

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

#: What replacing this build's own prior output says. ⛔ **A separate verb
#: rather than a second `wrote` line**, because *"which of my files did this
#: run overwrite"* is the question the rebuild policy owes an auditable answer
#: to, and a report that spelled a replacement and a creation the same way
#: would not be one. ⚠️ The sentence names the reason it was allowed, not just
#: the fact: a reader who sees it should be able to tell at once whether the
#: build has just eaten something of theirs.
REBUILT = "the plan declares this path as the build's own; its previous output was replaced"

#: What a clip playing words its paragraph no longer says gets.
#: ⭐ It names the command that lists each and says how to re-voice it.
STALE = (
    "this clip plays words its paragraph no longer says; studyforge validate names "
    "each such clip and the narrate command that re-voices it"
)

#: What a clip an earlier narrated build left in `--out` gets.
#: ⛔ A build deletes nothing (R3, and narration's own rule), so it says how to.
UNLINKED = (
    "an earlier build with narration copied this clip here and no page links it; "
    "nothing was deleted. Delete it, or build into an empty --out, to be rid of it"
)


def exit_code(written: Written) -> int:
    """`0` when the whole site was written, `1` when any path was refused."""
    return INVALID if written.refused else OK


def lines(written: Written, root: str, into: str) -> list[str]:
    """Return the whole report, one fact per line, paths sorted (R10).

    ⛔ **Every written path gets exactly one line.** `Written.replaced` is a
    cross-cutting record over `paths` rather than a fourth category, so a
    replaced path is subtracted from the `wrote` lines here — a reader counting
    `wrote` lines against `studyforge plan` must not see one path twice.
    """
    replaced = {str(path) for path in written.replaced}
    out = [f"build {root}  into {into}"]
    out += [
        f"wrote {path}"
        for path in sorted(str(path) for path in written.paths)
        if path not in replaced
    ]
    out += [f"replace {path}  {REBUILT}" for path in sorted(replaced)]
    out += [
        f"refuse {path}  {ALREADY_THERE}" for path in sorted(str(path) for path in written.refused)
    ]
    out += [f"stale {path}  {STALE}" for path in sorted(str(path) for path in written.stale)]
    out += [f"unlinked {path}  {UNLINKED}" for path in sorted(str(p) for p in written.unlinked)]
    return out
