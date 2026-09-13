r"""Ruling 285(b) at authoring time: a NEW handoff cites a tracked document as a POINTER (`W135`).

**What it does.** Finds every citation of a tracked markdown document written as
a BARE FILENAME in a task or office handoff that is NEW — absent from the tree at
`CITATION_PIN`. ⛔ `check_pointers` resolves links and cannot see such a
citation at all, so it can neither resolve it nor report it missing.

**How you use it.** `check_handoffs` calls `citation_findings(root, bound,
frozen_documents(root))` as one more arm, and the package's `handoff_citations`
prints `citation_lines` through `NOTICES`. `bare_citations` is the reader both
use.

**Depends on.** `config` for the markdown population, `markdown` for the line
parser, `report.Finding`, and one `git ls-tree`. ⛔ Never its own package: the
package imports this, so this imports nothing back.

## ⛔ "NEW" IS A REF, and the frozen records are excluded BY CONSTRUCTION

⚠️ **Measured at `b182a88`, HOST, `wt/dev3`: 226 of the 306 documents under
`docs/tasks/handoffs/` carry no markdown pointer, and all 226 are in the tree at
that ref**, so every one is a record Ruling 106 freezes. ⛔ A bare-citation
rule over them fires in 131 of the 159 task and office handoffs, which no office
may repair.

- ⚠️ **A DIRECTORY cannot separate them.** `check_rulings_reach` names a subject
  directory, but a new handoff lands BESIDE the frozen ones, at the path
  `agent-protocol.md` prescribes, so naming that directory excludes nothing.
- ⚠️ **A WAVE MARKER does not exist** on any handoff, and a declared field is
  escaped by leaving it out.
- ⭐ **A REF does.** The tree at `CITATION_PIN` is immutable: a handoff absent
  from it cannot have been frozen when this rule landed, and one present in it
  cannot leave. ⛔ Nothing here names a document, so the next handoff needs no
  entry and there is no list to go stale.

⛔ **A PIN, NOT A KNOB** — the same construction as `existence.HANDOFF_OWED_FROM`.
Moving it forward to quiet a red handoff exempts that handoff, which is the one
use it must never have; the repair is the link.

⭐ **A commit object is not a branch position**, so `existence.py`'s *no git*
objection (Ruling 80) does not reach it: the answer is the same in every
checkout that holds the object. Measured readable inside the pinned image from a
linked worktree. ⛔ **Where git cannot answer (Ruling 216's third answer), every
bound handoff is read as NEW** — the arm fails closed and the notice says so.

## ⛔ What a citation IS, and what it never is

Outside fences, with every inline link blanked, a token `<path>.md` (an optional
`#anchor` after it) is a citation when it resolves to a markdown document git
tracks: beside the citing handoff, from the root, or as the tail of one tracked
path. ⭐ **A code span holding whitespace is a COMMAND and is not read.** ⛔ **A
name that resolves to nothing is not a finding** — Ruling 308: the backticked
name is right where the target is absent on this ref. ⭐ A test name, a symbol
and a sha are not `.md` tokens, so they are never read.

## ⚠️ Declared gaps (Ruling 258)

1. **Whether a pointer owes an ANCHOR** — whether the citation is to a section —
   is prose and is not judged; `check_pointers` resolves an anchor once written.
2. **`ruling record`, `session log` and `survey` are not bound.** This arm rides
   the six-section contract, which binds two kinds; widening it to records is a
   decision this row does not make.
3. **A blockquote is read as prose**, so a quoted bare name in a new handoff is
   a finding.
"""

from __future__ import annotations

import posixpath
import re
import shutil
import subprocess
from pathlib import Path

from tools.quality import config
from tools.quality.markdown import code_spans, prose_lines, strip_links
from tools.quality.report import Finding

RULE_BARE = "handoff-bare-citation"

#: ⛔ The ref whose tree IS the frozen population: the release tip this rule was
#: cut from. A PIN, NOT A KNOB — see the module docstring.
CITATION_PIN = "b182a8822af05998c31bbf08bec4c92ee67fe52b"

#: A markdown filename as it is written, with any directories and an optional
#: anchor. ⛔ Bounded on both sides so `x.md.bak` and `a/b.mdx` are not read.
_TOKEN = re.compile(r"(?<![\w./-])(?P<path>(?:[\w.-]+/)*[\w-]+\.md)(?:#[\w-]*)?(?![\w/-])")


def frozen_documents(root: Path, pin: str = CITATION_PIN) -> frozenset[str] | None:
    """Every path in the tree at `pin`, or `None` when git cannot say (Ruling 216)."""
    git = shutil.which("git")
    if git is None:
        return None
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [git, "ls-tree", "-r", "-z", "--name-only", pin],
            capture_output=True,
            text=True,
            cwd=root,
            check=False,
            timeout=30,
        )
    except OSError, subprocess.SubprocessError:
        return None
    if result.returncode != 0:  # 128: not a repository, or the pin is not in it
        return None
    return frozenset(name for name in result.stdout.split("\0") if name)


def tracked_documents(root: Path) -> frozenset[str]:
    """Every markdown document in the floor's own population, repo-relative."""
    return frozenset(config.relative(path, root) for path in config.markdown_population(root).paths)


def _resolve(relative: str, token: str, documents: frozenset[str]) -> str | None:
    """Return the tracked document `token` names from `relative`, or `None`."""
    beside = posixpath.normpath(posixpath.join(posixpath.dirname(relative), token))
    for candidate in (beside, posixpath.normpath(token)):
        if candidate in documents:
            return candidate
    tail = "/" + "/".join(part for part in token.split("/") if part not in (".", ".."))
    return next((document for document in sorted(documents) if document.endswith(tail)), None)


def bare_citations(
    relative: str, text: str, documents: frozenset[str]
) -> list[tuple[int, str, str]]:
    """`(line, token as written, document it names)` for every bare citation."""
    found: list[tuple[int, str, str]] = []
    for number, line in prose_lines(text):
        read = strip_links(line)
        for start, end, body in code_spans(read):
            if any(character.isspace() for character in body.strip()):
                read = read[:start] + " " * (end - start) + read[end:]
        for match in _TOKEN.finditer(read):
            target = _resolve(relative, match.group("path"), documents)
            if target is not None:
                found.append((number, match.group("path"), target))
    return found


def new_handoffs(
    bound: list[tuple[str, str]], frozen: frozenset[str] | None
) -> list[tuple[str, str]]:
    """Return the bound handoffs absent from the pinned tree — all of them if it is unread."""
    return [
        (relative, text) for relative, text in bound if frozen is None or relative not in frozen
    ]


def citation_findings(
    root: Path, bound: list[tuple[str, str]], frozen: frozenset[str] | None
) -> list[Finding]:
    """Every bare citation of a tracked document in a NEW handoff."""
    new = new_handoffs(bound, frozen)
    if not new:
        return []
    documents = tracked_documents(root)
    findings: list[Finding] = []
    for relative, text in new:
        for number, token, target in bare_citations(relative, text, documents):
            pointer = posixpath.relpath(target, posixpath.dirname(relative))
            findings.append(
                Finding(
                    relative,
                    number,
                    RULE_BARE,
                    f"cites `{token}`, a tracked document, by BARE FILENAME, which "
                    f"`check_pointers` cannot see (Ruling 285(b)). Write the pointer — "
                    f"[`{token}`]({pointer}) — anchored where it cites a section. A test "
                    f"name, a symbol, a sha or a command is not a citation and is not read.",
                )
            )
    return findings


def citation_lines(
    root: Path, bound: list[tuple[str, str]], frozen: frozenset[str] | None
) -> list[str]:
    """Print the arm's figure WITH its denominator, whether or not it fired (Ruling 48)."""
    new = new_handoffs(bound, frozen)
    documents = tracked_documents(root) if new else frozenset()
    citing = [relative for relative, text in new if bare_citations(relative, text, documents)]
    empty = " — the population is EMPTY, so this is 0 = 0 and not a clean bill" if not new else ""
    if frozen is None:
        basis = (
            f"the pin {CITATION_PIN[:7]} could NOT be read here, so all {len(bound)} task "
            f"and office handoffs are read as new (fails closed)"
        )
    else:
        basis = (
            f"{len(bound) - len(new)} of {len(bound)} task and office handoffs are in the "
            f"tree at the pin {CITATION_PIN[:7]}, frozen records that are not read (Ruling 106)"
        )
    return [
        f"handoff citations: {len(citing)} of {len(new)} new handoffs cite a tracked "
        f"document without a pointer{empty}. {basis}."
    ]
