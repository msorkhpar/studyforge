"""The one exception this package raises, and the one thing its messages never say.

**What it does.** Names a refusal from any pass in this package, so a caller
catches one type rather than one per module.

**How you use it.** Catch `ReconnaissanceRefused`. `inside_root(path, root)` is
the one check a pass runs before it reads one path against another.
`describe(value)` is how a message says what arrived without reproducing it; it
is re-exported here because that is where this package's refusals already reach
for it.

**Depends on.** `studyforge.describe` and `pathlib`, and nothing else. ⛔
Deliberately: the passes import this module, so a dependency in any other
direction is a cycle waiting for the second caller.

## ⛔ Why a package that only measures needs an exception at all

⚠️ Every other refusal here is an `Uncertainty`: the material did not settle
something, and the report says so with what would settle it. ⭐ That is the
right shape for **material** and the wrong shape for a **caller mistake** — a
pass handed a document and a root that have nothing to do with each other has
not measured an uncertain corpus, it has been called wrongly, and filing that
as a question would be a guess with extra steps (R6: loud, named).

## ⛔ The message is where R7 bites, and it has bitten here once

⚠️ **Measured:** a refusal that is simply *let* to happen — handing
two unrelated paths to `Path.relative_to` — carries **both** absolute paths in
its message, one of them under a home directory. ⭐ So a refusal in this
package **tests the relationship between its arguments itself** and raises its
own sentence. ⛔ It never catches the standard library's error and re-raises
from it: `__cause__` would carry that message into every traceback the new one
appears in, which is the same leak with one more frame in front of it.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.describe import describe

__all__ = ["ReconnaissanceRefused", "describe", "inside_root"]


class ReconnaissanceRefused(ValueError):
    """An argument no pass in this package can measure anything from.

    ⛔ **The message names the argument, and what was wrong with its
    *relationship* to the others — never the value** (R7).
    `studyforge.describe` names a type; a path is not quoted, not in part, not
    normalised, and not with the home directory taken off the front.

    ⭐ **And it says that it is being silent, and why.** The one recorded way
    this discipline gets undone is the next author reading a refusal that looks
    unhelpfully vague and putting the value back, correctly by the rules as
    they found them.

    ⚠️ **`ValueError`, following the address package's split** and `corpus.manifest`'s
    reading of it: this is a value a caller passed, not a document that could
    not be read, so the base that already-written code handles is the one.
    """


def inside_root(path: Path, root: Path) -> None:
    """Refuse `path` unless it sits inside `root`, naming neither of them.

    ⭐ **Called instead of letting `Path.relative_to` raise.** The two are the
    same test; only one of them keeps the answer out of the message.

    ⚠️ **The test is on `path.parent`, and it is the strict one.** A parent
    inside the root puts the file inside it too, so one call covers every
    expression a pass then writes against that root — and it also catches the
    root handed in as its own document, where `path.relative_to(root)` answers
    `.` while `path.parent.relative_to(root)` is the call that raises.
    """
    if path.parent.is_relative_to(root):
        return
    raise ReconnaissanceRefused(
        "a document is read against the root it was found under, and this one is not "
        f"inside it: this pass was given {describe(path)} as the document and "
        f"{describe(root)} as the root, and the document's parent directory is not "
        "inside that root. Neither is reproduced here, because an absolute path in a "
        "refusal is personal data (R7) — that silence is the rule, not vagueness to be "
        "helpfully filled in. Pass the root that was walked, which is `inventory.root` "
        "where a survey passes it, or a document under that root."
    )
