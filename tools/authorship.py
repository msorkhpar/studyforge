"""`W308`: WHO WROTE the commits a merge would introduce — read as a VERDICT, never echoed.

**What it does.** Reads the author line of every commit that merging `<branch>` would
introduce, and reports WHICH of them are not placeholders. ⛔ It answers a BOOLEAN and a
list of SHORT SHAS; no author line it reads is ever returned, printed, logged or stored,
so a refusal cannot relocate somebody's identity into a build log (R7, Ruling 345's
clause 5 — prove absence with a null check, never by printing the value).

**How you use it.** `read_authorship(root, branch)` returns an `Authorship`;
`render_authorship(authorship)` is the lines the merge gate prints; and
`author_is_placeholder(line)` is the predicate — the ONE function here that ever sees a
value. `tools.mergegate` is the caller, and the merge path is the only caller there is.

**Depends on.** `dataclasses`, `pathlib` and `subprocess` — the standard library — and
`git` on the path. ⛔ It imports neither `studyforge` nor `tools.quality`, for the reason
`tools/mergegate.py` gives: a tree too broken to import must still be one whose merge is
REFUSED rather than one that crashes the gate. ⚠️ `tools.quality.personal_data.shapes`
holds this repository's other reserved-address pattern and is deliberately NOT imported —
that is a FLOOR package, and importing it would put the floor on the merge path's import
graph. ⭐ The duplication is named in `docs/tasks/handoffs/W308.md` rather than hidden.

## ⛔ WHY THE POPULATION IS `HEAD..<branch>`, AND NEVER HISTORY

⭐ **The commits a merge INTRODUCES are the proposal; everything reachable from `HEAD` has
already LANDED.** ⛔ A gate over landed tips is a backlog no office may clear, so nothing
on the release line is ever judged — ⭐ **and that is also why the user's own identity
passes.** The standing ruling is that a REAL git identity in a LOCAL commit is fine here,
because nothing is ever pushed; that identity sits on the release line's own commits, and
this gate never reads them.

⚠️ **Asserted by a PLANT rather than by this paragraph** (Ruling 123): the mirror lands a
foreign author line on the release side and reads the merge GREEN.

⭐ **The caller runs this BEFORE it stages the merge**, so a refusal here costs nothing: there
is no commit to undo and no tree to restore, and `tools.mergegate.Outcome.verdict` therefore
answers authorship first and never consults `restored`. ⛔ That ordering is the reason this
gate can be strict without ever being the reason an office loses work.

## ⛔ WHY A PLACEHOLDER IS THE RULE, AND WHY IT IS NOT A ROSTER OF OFFICES

⭐ Ruling 345 makes an office's author line PER INVOCATION — `git -c user.name=<office>
-c user.email=<office>@example.invalid` — precisely so that no identity can enter the
SHARED config that every other office's commit would then be authored with. ⛔ **This gate
enforces that MECHANISM, not a list of names**: `W305` refused *"add `dev1` to the
allow-list"* because it fails the next office called anything else. ⭐ The predicate asks
only whether the address is unreachable BY CONSTRUCTION, so it holds for every office name
that will ever exist, and it needs no maintenance when one is added.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

#: Addresses that are unreachable BY CONSTRUCTION and therefore identify nobody: RFC 6761's
#: reserved TLDs and RFC 2606's documentation domains. ⛔ A property of the ADDRESS, never a
#: roster of offices — the contract above says why that distinction is the whole design.
PLACEHOLDER_TLDS = ("invalid", "test", "example", "localhost")
PLACEHOLDER_DOMAINS = ("example.com", "example.net", "example.org")


def author_is_placeholder(line: str) -> bool:
    """Report whether `line`'s address is unreachable by construction.

    ⛔ **COMPARE, NEVER ECHO.** This is the only function on the merge path that sees an
    author line, and it returns a BOOLEAN: nothing it reads reaches a caller, a message or
    a log. ⚠️ A line with no bracketed address is NOT a placeholder — an unreadable author
    line is refused rather than admitted, because the permissive reading of a malformed
    input is how a gate becomes decorative.
    """
    _, _, rest = line.partition("<")
    address, closed, _ = rest.partition(">")
    if not closed:
        return False
    domain = address.rpartition("@")[2].strip().lower()
    if not domain:
        return False
    if domain in PLACEHOLDER_DOMAINS or domain in PLACEHOLDER_TLDS:
        return True
    return any(
        domain.endswith(f".{reserved}") for reserved in (*PLACEHOLDER_TLDS, *PLACEHOLDER_DOMAINS)
    )


@dataclass(frozen=True)
class Authorship:
    """One read: how many commits were judged, which were foreign, or why none were read."""

    population: int = 0
    foreign: tuple[str, ...] = ()
    unread: str = ""


def _git(root: Path, *arguments: str) -> tuple[int, str]:
    """Run git in `root` and return its exit code with its stripped stdout.

    ⚠️ A deliberate twin of `tools.mergegate._git` rather than an import of it: that module
    imports THIS one, so reaching back would be a cycle. ⭐ Both are four lines over
    `subprocess.run`, and the alternative is a third module for one call.
    """
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


def read_authorship(root: Path, branch: str) -> Authorship:
    """Read the author line of every commit that merging `branch` would introduce.

    ⛔ **Ruling 191: an EMPTY population is never the pass reading.** A branch that
    introduces no commit returns `unread` and not a clean `Authorship`, so no caller can
    read a green out of a population of `0`.
    """
    code, out = _git(root, "rev-list", f"HEAD..{branch}")
    if code != 0:
        return Authorship(unread=f"git cannot list the commits {branch} would introduce")
    commits = tuple(sha for sha in out.splitlines() if sha)
    if not commits:
        return Authorship(
            unread=f"{branch} introduces no commit, so NO author line was read (Ruling 191)"
        )
    foreign: list[str] = []
    for sha in commits:
        code, line = _git(root, "show", "--no-patch", "--format=%an <%ae>", sha)
        if code != 0:
            return Authorship(
                population=len(commits),
                unread=f"git cannot read the author line of {sha[:12]}",
            )
        if not author_is_placeholder(line):
            foreign.append(sha[:12])
    return Authorship(population=len(commits), foreign=tuple(foreign))


def render_authorship(authorship: Authorship) -> list[str]:
    """Return the lines the merge gate prints: the POPULATION first, then the verdict.

    ⛔ Ruling 191(a): a control prints the SIZE of the population it was drawn from BEFORE
    its verdict, so a reader can tell a green from a green over nothing.
    """
    lines = [
        f"authorship: {authorship.population} commit(s) introduced by this merge were read "
        f"for their author line — on the branch, never on the release line"
    ]
    if not authorship.foreign:
        lines.append("⭐ PLACEHOLDER: every introduced commit's author line identifies nobody")
        return lines
    lines.extend(
        f"  ⛔ RED    {sha} — its author line is not a placeholder" for sha in authorship.foreign
    )
    lines.append(
        "⛔ REFUSED: an office's commit carries a PLACEHOLDER author line, so that one "
        "office's work cannot land under another's name — nothing was staged, and the "
        "tree was never touched"
    )
    lines.append(
        "⭐ THE REMEDY IS PER INVOCATION (Ruling 345) and never `git config`: re-author the "
        "commits named above with "
        "`git -c user.name=<office> -c user.email=<office>@example.invalid`"
    )
    return lines
