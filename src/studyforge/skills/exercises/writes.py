r"""The additive commit: every file checked against the tree before any is written (R3).

**What it does.** Writes the files one authoring pass produced into the corpus
root, creating what is not there, keeping what is there with the same bytes,
and refusing the WHOLE pass — before a byte is written — when any would
overwrite a file with other bytes.

**How you use it.**

    written, kept = commit(root, files, "the authoring pass", replaces=(LEDGER_PATH,))

**Depends on.** `drafts` for the refusal and `studyforge.exercise` for the
rule a corpus-root path obeys. Standard library only.

## ⛔ ONE NAMED EXCEPTION, AND IT IS THE LEDGER'S (`W456`)

⭐ **`replaces` names the files a pass may rewrite, and the corpus pass names
exactly one: `exercises/ledger.json`.** It is one file for the whole corpus, so
a pass over part of it must rewrite it to add its own rows — and `merge` is
what makes that rewrite additive, keeping every row the pass did not re-read.
⚠️ Before `W456` the ledger was not exempt, so a second pass over another
container was refused here, and the one way past the refusal — removing the
ledger — lost every earlier container's rows. ⛔ A replaceable path holding a
directory is still refused: a rewrite replaces a file and nothing else.

⚠️ **Split out of `corpus` at `W456`**, when the merge brought that module to
R11's ceiling. The seam is the write: `corpus` decides what the pass produced,
and this module decides whether the tree may take it.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from studyforge.exercise import require_path
from studyforge.skills.exercises.drafts import AuthoringError


def commit(
    root: Path, files: Sequence[tuple[str, bytes]], where: str, replaces: Sequence[str] = ()
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Create every file not already there, refusing ALL of them if any would be rewritten.

    ⛔ **R3, checked whole before a byte is written.** A file present with the
    same bytes is kept, which is what makes a re-run write nothing (R10); a
    file present with different bytes — or two of this pass's own files at one
    path — refuses the pass and names the path. ⚠️ `replaces` is the one
    exception, and only the ledger is ever named in it: `merge` keeps every row
    the pass did not re-read, so its rewrite adds and never loses (`W456`).
    """
    wanted: dict[str, bytes] = {}
    for path, data in files:
        inside = require_path(path, "a path the authoring pass writes", where)
        if wanted.setdefault(inside, data) != data:
            raise AuthoringError(
                f"{where}: two of this pass's own files land on '{inside}' with "
                f"different bytes, so one of them would be lost."
            )
    rewritten = [
        path
        for path, data in wanted.items()
        if (root / path).exists()
        and not _same(root / path, data)
        and (path not in replaces or not (root / path).is_file())
    ]
    if rewritten:
        raise AuthoringError(
            f"{where}: {len(rewritten)} file(s) this pass would write are already in the "
            f"corpus with different contents, the first at '{rewritten[0]}'. Generation "
            f"is non-destructive (R3): nothing was written, and no existing file is "
            f"rewritten to make room."
        )
    written, kept = [], []
    for path, data in wanted.items():
        target = root / path
        if _same(target, data) or (path not in replaces and target.exists()):
            kept.append(path)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        written.append(path)
    return tuple(written), tuple(kept)


def _same(path: Path, data: bytes) -> bool:
    """Is the file at `path` exactly these bytes? ⛔ A directory is never the same."""
    return path.is_file() and path.read_bytes() == data
